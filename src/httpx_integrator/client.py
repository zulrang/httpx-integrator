"""Client implementation for httpx-integrator."""

from typing import Any

import httpx

from httpx_integrator.config import ClientConfig, TimeoutConfig


def _convert_timeout_config(timeout_config: TimeoutConfig) -> httpx.Timeout:
    """Convert TimeoutConfig to httpx.Timeout.

    Args:
        timeout_config: TimeoutConfig instance to convert.

    Returns:
        httpx.Timeout instance with the configured values.
    """
    return httpx.Timeout(
        connect=timeout_config.connect,
        read=timeout_config.read,
        write=timeout_config.write,
        pool=timeout_config.pool,
    )


class Client:
    """Synchronous HTTP client wrapper around httpx.Client.

    This client provides a resilient interface for making HTTP requests with
    configurable timeouts, retries, and other resilience features.

    Args:
        config: Optional ClientConfig for configuring resilience features.
        **kwargs: All httpx.Client parameters are supported and passed through.

    Example:
        ```python
        from httpx_integrator import Client, ClientConfig, TimeoutConfig

        config = ClientConfig(timeouts=TimeoutConfig(connect=5.0, read=30.0))
        client = Client(config=config, base_url="https://api.example.com")
        response = client.get("/users")
        ```
    """

    def __init__(
        self,
        config: ClientConfig | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the Client.

        Args:
            config: Optional ClientConfig for configuring resilience features.
            **kwargs: All httpx.Client parameters are supported.
        """
        self._config = config

        # Apply timeout from config if provided and not overridden in kwargs
        if config and config.timeouts and "timeout" not in kwargs:
            kwargs["timeout"] = _convert_timeout_config(config.timeouts)

        self._client = httpx.Client(**kwargs)

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        """Send a GET request."""
        return self._client.get(url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> httpx.Response:
        """Send a POST request."""
        return self._client.post(url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> httpx.Response:
        """Send a PUT request."""
        return self._client.put(url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> httpx.Response:
        """Send a PATCH request."""
        return self._client.patch(url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        """Send a DELETE request."""
        return self._client.delete(url, **kwargs)

    def head(self, url: str, **kwargs: Any) -> httpx.Response:
        """Send a HEAD request."""
        return self._client.head(url, **kwargs)

    def options(self, url: str, **kwargs: Any) -> httpx.Response:
        """Send an OPTIONS request."""
        return self._client.options(url, **kwargs)

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """Send a request with the given method."""
        return self._client.request(method, url, **kwargs)
