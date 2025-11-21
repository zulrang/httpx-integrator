# Getting Started with httpx-integrator

This guide will help you get started with `httpx-integrator`, a resilient HTTP client wrapper around `httpx`.

## Installation

### Using uv (Recommended)

```bash
uv add httpx-integrator
```

### Using pip

```bash
pip install httpx-integrator
```

## Basic Usage

### Creating a Client

The simplest way to create a client is without any configuration:

```python
from httpx_integrator import Client

client = Client()
response = client.get("https://api.example.com/users")
```

### Configuring Timeouts

Configure timeouts using `TimeoutConfig`:

```python
from httpx_integrator import Client, ClientConfig, TimeoutConfig

config = ClientConfig(
    timeouts=TimeoutConfig(
        connect=5.0,  # Connection timeout in seconds
        read=30.0,    # Read timeout in seconds
    )
)

client = Client(config=config)
response = client.get("https://api.example.com/users")
```

### Using httpx Parameters

All `httpx.Client` parameters are supported and passed through:

```python
from httpx_integrator import Client, ClientConfig, TimeoutConfig

config = ClientConfig(
    timeouts=TimeoutConfig(connect=5.0, read=30.0)
)

client = Client(
    config=config,
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer token"},
    cookies={"session": "abc123"},
    follow_redirects=True,
)

# Use relative URLs with base_url
response = client.get("/users")
```

### Per-Request Timeout Override

You can override timeouts for individual requests:

```python
import httpx
from httpx_integrator import Client, ClientConfig, TimeoutConfig

config = ClientConfig(
    timeouts=TimeoutConfig(connect=5.0, read=30.0)
)
client = Client(config=config)

# Override timeout for this specific request
request_timeout = httpx.Timeout(5.0, connect=2.0, read=10.0)
response = client.get(
    "https://api.example.com/users",
    timeout=request_timeout
)
```

## Configuration Options

### TimeoutConfig

The `TimeoutConfig` class allows you to configure various timeout values:

```python
from httpx_integrator import TimeoutConfig

# Default values
timeout = TimeoutConfig()  # connect=5.0, read=30.0

# Custom values
timeout = TimeoutConfig(
    connect=10.0,  # Connection timeout
    read=60.0,     # Read timeout
    write=5.0,      # Write timeout (optional)
    pool=10.0,      # Pool timeout (optional)
)
```

### ClientConfig

The `ClientConfig` class is the main configuration container:

```python
from httpx_integrator import ClientConfig, TimeoutConfig

config = ClientConfig(
    timeouts=TimeoutConfig(connect=5.0, read=30.0),
    # Other configuration options will be available in future releases:
    # retries=RetryConfig(...),           # Phase 1
    # circuit_breaker=CircuitBreakerConfig(...),  # Phase 2
    # rate_limit=RateLimitConfig(...),    # Phase 2
    # validation=ValidationConfig(...),   # Phase 1
    # tracing=TracingConfig(...),         # Phase 3
)
```

## HTTP Methods

The client supports all standard HTTP methods:

```python
from httpx_integrator import Client

client = Client()

# GET request
response = client.get("https://api.example.com/users")

# POST request
response = client.post(
    "https://api.example.com/users",
    json={"name": "John Doe", "email": "john@example.com"}
)

# PUT request
response = client.put(
    "https://api.example.com/users/123",
    json={"name": "Jane Doe"}
)

# PATCH request
response = client.patch(
    "https://api.example.com/users/123",
    json={"email": "jane@example.com"}
)

# DELETE request
response = client.delete("https://api.example.com/users/123")

# HEAD request
response = client.head("https://api.example.com/resource")

# OPTIONS request
response = client.options("https://api.example.com/resource")

# Generic request method
response = client.request("GET", "https://api.example.com/users")
```

## Response Handling

The client returns standard `httpx.Response` objects, so you can use all `httpx` response methods:

```python
from httpx_integrator import Client

client = Client()
response = client.get("https://api.example.com/users")

# Access response properties
print(response.status_code)
print(response.headers)
print(response.text)
print(response.json())

# Check status
if response.is_success:
    data = response.json()
```

## Error Handling

The client raises standard `httpx` exceptions:

```python
from httpx_integrator import Client
import httpx

client = Client()

try:
    response = client.get("https://api.example.com/users")
except httpx.HTTPStatusError as e:
    print(f"HTTP error occurred: {e.response.status_code}")
except httpx.ConnectTimeout:
    print("Connection timeout")
except httpx.ReadTimeout:
    print("Read timeout")
except httpx.RequestError as e:
    print(f"Request error: {e}")
```

## Examples

### Example: API Client with Timeouts

```python
from httpx_integrator import Client, ClientConfig, TimeoutConfig

# Configure timeouts
config = ClientConfig(
    timeouts=TimeoutConfig(connect=5.0, read=30.0)
)

# Create client with base URL and headers
client = Client(
    config=config,
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer your-token-here"},
)

# Make requests
try:
    response = client.get("/users")
    users = response.json()
    print(f"Found {len(users)} users")
except Exception as e:
    print(f"Error: {e}")
```

### Example: Per-Request Configuration

```python
from httpx_integrator import Client, ClientConfig, TimeoutConfig
import httpx

# Default configuration
config = ClientConfig(
    timeouts=TimeoutConfig(connect=5.0, read=30.0)
)
client = Client(config=config)

# Most requests use default timeout
response1 = client.get("https://api.example.com/users")

# Some requests need longer timeout
long_timeout = httpx.Timeout(5.0, connect=5.0, read=120.0)
response2 = client.get(
    "https://api.example.com/slow-endpoint",
    timeout=long_timeout
)
```

## Next Steps

- Read the [Project Design Document](project_design_document.md) for architecture details
- Check out [Best Practices](BEST_PRACTICES.md) for third-party integration guidelines
- Stay tuned for upcoming features:
  - Retries with exponential backoff (Phase 1)
  - Circuit breakers (Phase 2)
  - Rate limiting (Phase 2)
  - Response validation (Phase 1)
  - Distributed tracing (Phase 3)
