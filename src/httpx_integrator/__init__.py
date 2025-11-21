"""httpx-integrator: A resilient HTTP client wrapper around httpx."""

from httpx_integrator.client import Client
from httpx_integrator.config import ClientConfig, TimeoutConfig

__version__ = "0.1.0"
__all__ = ["Client", "ClientConfig", "TimeoutConfig"]
