"""Tests for timeout functionality."""

import socket
import time
from unittest.mock import Mock, patch

import httpx
import pytest
from pytest_httpserver import HTTPServer

from httpx_integrator import Client, ClientConfig, TimeoutConfig


def test_connect_timeout_is_applied():
    """Test connect timeout is applied from config."""
    config = ClientConfig(timeouts=TimeoutConfig(connect=1.0, read=30.0))
    with patch("httpx_integrator.client.httpx.Client") as mock_client_class:
        mock_client_instance = Mock()
        mock_client_class.return_value = mock_client_instance

        Client(config=config)

        # Verify httpx.Client was called with timeout
        call_kwargs = mock_client_class.call_args[1]
        assert "timeout" in call_kwargs
        timeout = call_kwargs["timeout"]
        assert isinstance(timeout, httpx.Timeout)
        assert timeout.connect == 1.0
        assert timeout.read == 30.0


def test_read_timeout_is_applied():
    """Test read timeout is applied from config."""
    config = ClientConfig(timeouts=TimeoutConfig(connect=5.0, read=60.0))
    with patch("httpx_integrator.client.httpx.Client") as mock_client_class:
        mock_client_instance = Mock()
        mock_client_class.return_value = mock_client_instance

        Client(config=config)

        call_kwargs = mock_client_class.call_args[1]
        timeout = call_kwargs["timeout"]
        assert timeout.read == 60.0


def test_timeout_from_client_config_is_used():
    """Test timeout from ClientConfig is used."""
    timeout_config = TimeoutConfig(connect=10.0, read=120.0)
    config = ClientConfig(timeouts=timeout_config)
    with patch("httpx_integrator.client.httpx.Client") as mock_client_class:
        mock_client_instance = Mock()
        mock_client_class.return_value = mock_client_instance

        Client(config=config)

        call_kwargs = mock_client_class.call_args[1]
        timeout = call_kwargs["timeout"]
        assert timeout.connect == 10.0
        assert timeout.read == 120.0


def test_per_request_timeout_override():
    """Test per-request timeout override."""
    config = ClientConfig(timeouts=TimeoutConfig(connect=5.0, read=30.0))
    client = Client(config=config)

    # Mock the underlying httpx client
    mock_response = Mock()
    mock_response.status_code = 200
    client._client = Mock()
    client._client.get.return_value = mock_response

    # Override timeout for this request (httpx.Timeout requires all params or a default)
    request_timeout = httpx.Timeout(5.0, connect=2.0, read=10.0)
    client.get("https://api.example.com/users", timeout=request_timeout)

    # Verify the request was made with the overridden timeout
    client._client.get.assert_called_once()
    call_kwargs = client._client.get.call_args[1]
    assert call_kwargs["timeout"] == request_timeout


def test_timeout_with_httpx_timeout_object():
    """Test timeout can be passed as httpx.Timeout object."""
    # httpx.Timeout requires a default or all four parameters
    httpx_timeout = httpx.Timeout(5.0, connect=3.0, read=15.0)
    with patch("httpx_integrator.client.httpx.Client") as mock_client_class:
        mock_client_instance = Mock()
        mock_client_class.return_value = mock_client_instance

        Client(timeout=httpx_timeout)

        call_kwargs = mock_client_class.call_args[1]
        assert call_kwargs["timeout"] == httpx_timeout


def test_timeout_defaults_when_no_config():
    """Test default timeout behavior when no config is provided."""
    with patch("httpx_integrator.client.httpx.Client") as mock_client_class:
        mock_client_instance = Mock()
        mock_client_class.return_value = mock_client_instance

        Client()

        # When no timeout config, httpx should use its defaults
        # timeout may or may not be in kwargs depending on httpx defaults
        # This test just ensures Client doesn't crash
        assert mock_client_class.called


def test_timeout_with_optional_fields():
    """Test timeout with optional write and pool fields."""
    config = ClientConfig(timeouts=TimeoutConfig(connect=5.0, read=30.0, write=10.0, pool=20.0))
    with patch("httpx_integrator.client.httpx.Client") as mock_client_class:
        mock_client_instance = Mock()
        mock_client_class.return_value = mock_client_instance

        Client(config=config)

        call_kwargs = mock_client_class.call_args[1]
        timeout = call_kwargs["timeout"]
        assert timeout.connect == 5.0
        assert timeout.read == 30.0
        assert timeout.write == 10.0
        assert timeout.pool == 20.0


# Integration tests using httpx test server
def test_connect_timeout_with_unreachable_host():
    """Test connect timeout with unreachable host."""
    # Use a port that's likely not in use
    unreachable_port = 65535
    unreachable_url = f"http://127.0.0.1:{unreachable_port}"

    config = ClientConfig(timeouts=TimeoutConfig(connect=0.1, read=30.0))
    client = Client(config=config)

    # This should raise a ConnectTimeout or similar error
    with pytest.raises((httpx.ConnectTimeout, httpx.ConnectError, socket.gaierror)):
        client.get(unreachable_url, timeout=0.5)


def test_read_timeout_with_slow_server(httpserver: HTTPServer):
    """Test read timeout with slow server."""

    def slow_handler(request):
        time.sleep(2)  # Sleep longer than read timeout
        return {"message": "too slow"}

    httpserver.expect_request("/slow").respond_with_handler(slow_handler)

    config = ClientConfig(timeouts=TimeoutConfig(connect=5.0, read=0.5))
    client = Client(config=config)

    # This should raise a ReadTimeout
    with pytest.raises(httpx.ReadTimeout):
        client.get(httpserver.url_for("/slow"))


def test_timeout_exceptions_are_raised_correctly(httpserver: HTTPServer):
    """Test timeout exceptions are raised correctly."""

    def slow_handler(request):
        time.sleep(1)
        return {"message": "response"}

    httpserver.expect_request("/delayed").respond_with_handler(slow_handler)

    # Very short read timeout
    config = ClientConfig(timeouts=TimeoutConfig(connect=5.0, read=0.1))
    client = Client(config=config)

    with pytest.raises(httpx.ReadTimeout):
        client.get(httpserver.url_for("/delayed"))
