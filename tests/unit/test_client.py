"""Tests for Client class."""

from unittest.mock import Mock, patch

from httpx_integrator import Client, ClientConfig, TimeoutConfig


def test_client_can_be_instantiated_with_no_config():
    """Test Client can be instantiated with no config."""
    client = Client()
    assert client is not None
    assert hasattr(client, "_client")


def test_client_can_be_instantiated_with_client_config():
    """Test Client can be instantiated with ClientConfig."""
    config = ClientConfig(timeouts=TimeoutConfig(connect=10.0, read=60.0))
    client = Client(config=config)
    assert client is not None
    assert client._config == config


def test_client_accepts_httpx_client_parameters():
    """Test Client accepts httpx.Client parameters."""
    client = Client(
        base_url="https://api.example.com",
        headers={"Authorization": "Bearer token"},
        cookies={"session": "abc123"},
    )
    assert client is not None
    # Verify httpx.Client was created with these parameters
    assert client._client.base_url == "https://api.example.com"
    assert "Authorization" in client._client.headers
    assert client._client.headers["Authorization"] == "Bearer token"


def test_client_wraps_httpx_client():
    """Test Client wraps httpx.Client correctly."""
    client = Client()
    # Verify internal client is an httpx.Client instance
    from httpx import Client as HTTPXClient

    assert isinstance(client._client, HTTPXClient)


def test_client_with_config_and_httpx_params():
    """Test Client accepts both config and httpx parameters."""
    config = ClientConfig(timeouts=TimeoutConfig(connect=5.0, read=30.0))
    client = Client(
        config=config,
        base_url="https://api.example.com",
        headers={"X-Custom": "value"},
    )
    assert client._config == config
    assert client._client.base_url == "https://api.example.com"
    assert client._client.headers["X-Custom"] == "value"


def test_client_get_returns_httpx_response():
    """Test client.get() returns httpx.Response."""
    with patch("httpx_integrator.client.httpx.Client") as mock_client_class:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_class.return_value = mock_client_instance

        client = Client()
        response = client.get("https://api.example.com/users")

        assert response == mock_response
        mock_client_instance.get.assert_called_once_with("https://api.example.com/users")


def test_client_post_works():
    """Test client.post() works."""
    with patch("httpx_integrator.client.httpx.Client") as mock_client_class:
        mock_response = Mock()
        mock_response.status_code = 201
        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_client_instance

        client = Client()
        response = client.post("https://api.example.com/users", json={"name": "John"})

        assert response == mock_response
        mock_client_instance.post.assert_called_once_with("https://api.example.com/users", json={"name": "John"})


def test_client_methods_pass_through_to_httpx():
    """Test all HTTP methods pass through to httpx correctly."""
    with patch("httpx_integrator.client.httpx.Client") as mock_client_class:
        mock_response = Mock()
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.put.return_value = mock_response
        mock_client_instance.patch.return_value = mock_response
        mock_client_instance.delete.return_value = mock_response
        mock_client_instance.head.return_value = mock_response
        mock_client_instance.options.return_value = mock_response
        mock_client_instance.request.return_value = mock_response
        mock_client_class.return_value = mock_client_instance

        client = Client()
        url = "https://api.example.com/resource"

        # Test all methods
        client.get(url)
        client.post(url)
        client.put(url)
        client.patch(url)
        client.delete(url)
        client.head(url)
        client.options(url)
        client.request("GET", url)

        # Verify all methods were called
        assert mock_client_instance.get.called
        assert mock_client_instance.post.called
        assert mock_client_instance.put.called
        assert mock_client_instance.patch.called
        assert mock_client_instance.delete.called
        assert mock_client_instance.head.called
        assert mock_client_instance.options.called
        assert mock_client_instance.request.called
