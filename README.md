# httpx-integrator

A resilient HTTP client wrapper around `httpx` that implements industry best practices for third-party API integration, including circuit breakers, retries, rate limiting, validation, and observability features.

## Features

- **Resilient HTTP Client**: Wraps `httpx` with production-ready resilience patterns
- **Configurable Timeouts**: Separate connect and read timeouts with sensible defaults
- **Type-Safe Configuration**: Pydantic-based configuration with full IDE support
- **Pass-Through Compatibility**: All `httpx` parameters are supported
- **Extensible**: Plugin system for custom retry strategies and storage backends

## Installation

```bash
# Using uv (recommended)
uv add httpx-integrator

# Using pip
pip install httpx-integrator
```

## Quick Start

```python
from httpx_integrator import Client, ClientConfig, TimeoutConfig

# Create a client with timeout configuration
config = ClientConfig(
    timeouts=TimeoutConfig(connect=5.0, read=30.0)
)

client = Client(
    config=config,
    base_url="https://api.example.com"
)

# Make requests
response = client.get("/users")
print(response.json())
```

## Documentation

- [Getting Started Guide](docs/getting_started.md) - Installation and basic usage
- [Project Design Document](docs/project_design_document.md) - Architecture and design decisions
- [Best Practices](docs/BEST_PRACTICES.md) - Third-party integration best practices

## Development

```bash
# Install dependencies
uv sync --all-groups

# Run tests
uv run pytest

# Run linting and type checking
uv run ruff check .
uv run mypy src/
```

## License

MIT
