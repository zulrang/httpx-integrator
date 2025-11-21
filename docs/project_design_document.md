# Project Design Document: httpx-integrator

## Executive Summary

### Project Goals

`httpx-integrator` is a Python library that wraps `httpx` to provide a resilient, production-ready HTTP client for integrating with third-party APIs. The library implements industry best practices for third-party integration, including circuit breakers, retries, rate limiting, validation, and observability features.

### Scope

This library provides:
- A new interface that wraps `httpx` (not a drop-in replacement)
- Support for both synchronous and asynchronous operations
- Configurable resilience patterns (retries, circuit breakers, timeouts)
- Request/response validation
- Rate limiting and idempotency support
- Distributed tracing and observability
- Testing utilities for integration testing

### Target Users

- Developers building integrations with third-party APIs
- Teams requiring resilient HTTP clients for production systems
- Applications that need to handle external API failures gracefully
- Systems that require strict validation of external API responses

### Key Design Principles

1. **Simplicity**: Easy-to-use API with sensible defaults
2. **Configurability**: Flexible configuration via Pydantic models
3. **Composability**: Features can be enabled/disabled independently
4. **Pass-through**: Full access to underlying `httpx` functionality
5. **Type Safety**: Comprehensive type hints and Pydantic validation
6. **Observability**: Built-in tracing and logging support

## Architecture Design

### Wrapper Pattern

The library implements a wrapper pattern around `httpx`, providing a new interface that:
- Encapsulates `httpx.Client` and `httpx.AsyncClient`
- Adds resilience and validation layers
- Maintains compatibility with `httpx` configuration options
- Allows pass-through of all `httpx` parameters

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                    Application Code                      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              httpx-integrator Client                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Configuration Layer (Pydantic)           │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Resilience Layer                          │   │
│  │  - Retries (exponential backoff + jitter)         │   │
│  │  - Circuit Breakers                               │   │
│  │  - Rate Limiting                                  │   │
│  │  - Timeouts                                       │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Validation Layer                          │   │
│  │  - Request validation                             │   │
│  │  - Response validation                            │   │
│  │  - Schema validation                              │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Observability Layer                       │   │
│  │  - Distributed tracing                            │   │
│  │  - Correlation IDs                                │   │
│  │  - Metrics                                        │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                    httpx Client                          │
└─────────────────────────────────────────────────────────┘
```

### Adapter/Facade Pattern

The library acts as a facade, simplifying complex resilience patterns into a single, easy-to-use interface. It also provides adapter interfaces (protocols) for:
- Custom retry strategies (`RetryStrategy` protocol)
- Custom circuit breaker storage backends (`CircuitBreakerStorage` protocol)
- Custom validators
- Custom rate limiters

### Plugin Architecture

The library supports a plugin system for extensibility:

1. **Retry Strategy Plugins**: Implement `RetryStrategy` protocol to define custom retry logic
2. **Circuit Breaker Storage Plugins**: Implement `CircuitBreakerStorage` protocol for custom storage backends
3. **Validator Plugins**: Custom validation functions for request/response validation
4. **Rate Limiter Plugins**: Custom rate limiting algorithms

Plugins are injected via configuration, allowing users to extend functionality without modifying the core library.

### Anti-Corruption Layer

The validation layer serves as an anti-corruption layer, ensuring external API models don't leak into the application's domain. Response validation transforms external data structures into validated, type-safe models before they reach application code.

### Sync and Async Support

Two client variants:
- `Client`: Synchronous wrapper around `httpx.Client`
- `AsyncClient`: Asynchronous wrapper around `httpx.AsyncClient`

Both share the same configuration interface and feature set.

## Feature Prioritization (Phased Approach)

### Phase 1: MVP - Core Resilience (Foundation)

**Goal**: Provide essential resilience features for production use.

**Features**:
1. **Timeouts**
   - Separate connect and read timeouts
   - Configurable per-request and per-client
   - Defaults: connect=5s, read=30s

2. **Retries with Exponential Backoff & Jitter**
   - Configurable retry count
   - Exponential backoff with jitter
   - Retry on specific HTTP status codes
   - Retry on network errors
   - Configurable backoff strategy
   - Plugin system for custom retry strategies

3. **Basic Request/Response Validation**
   - Type validation for request/response bodies
   - HTTP status code validation
   - Basic schema validation via Pydantic
   - Custom exception classes for validation errors (similar to Starlette/FastAPI pattern)

**Acceptance Criteria**:
- Client can be instantiated with timeout configuration
- Failed requests retry with exponential backoff
- Invalid responses are caught and raised before reaching application code
- All features work in both sync and async modes
- Full test coverage (>90%)

**Dependencies**: None (foundation phase)

---

### Phase 2: Advanced Resilience

**Goal**: Add production-grade resilience patterns.

**Features**:
1. **Circuit Breakers**
   - Configurable failure threshold
   - Configurable time window
   - Half-open state support
   - Per-endpoint or per-domain circuit breakers
   - Configurable failure criteria (status codes, exceptions)
   - Shared state across all client instances via external cache (Redis/Memcached)
   - Distributed circuit breaker state management

2. **Rate Limiting (Client-Side)**
   - Token bucket or sliding window algorithm
   - Per-client and per-endpoint rate limits
   - Configurable rate limit headers parsing
   - Automatic backoff when rate limited

3. **Idempotency Key Support**
   - Automatic idempotency key generation
   - Configurable key format
   - Header injection (e.g., `Idempotency-Key`)
   - Per-request or per-client configuration

**Acceptance Criteria**:
- Circuit breaker trips after threshold failures
- Circuit breaker state is shared across client instances via Redis/Memcached
- Rate limiter prevents exceeding configured limits
- Idempotency keys are automatically added to requests
- All features are configurable via Pydantic models
- Integration tests with real HTTP servers

**Dependencies**: Phase 1 must be complete

---

### Phase 3: Observability & Isolation

**Goal**: Enable monitoring, debugging, and resource isolation.

**Features**:
1. **Distributed Tracing**
   - Automatic correlation ID generation
   - OpenTelemetry integration (optional)
   - Request/response logging
   - Trace context propagation
   - Configurable trace sampling

2. **Bulkheads (Resource Isolation)**
   - Separate connection pools per client
   - Configurable pool size limits
   - Isolation of slow/failing endpoints

3. **Advanced Validation**
   - Pydantic model validation for responses
   - Custom validator functions
   - Response transformation
   - Schema versioning support

**Acceptance Criteria**:
- Correlation IDs are generated and logged
- OpenTelemetry spans are created (when enabled)
- Connection pools are isolated per client instance
- Response validation supports complex Pydantic models
- Tracing works across async boundaries

**Dependencies**: Phase 1 must be complete (Phase 2 recommended)

---

### Phase 4: Testing & Operational Tools

**Goal**: Provide tools for testing and operational excellence.

**Features**:
1. **VCR-Style Request Recording/Replay**
   - Record HTTP interactions
   - Replay recorded interactions in tests
   - Configurable matching (URL, headers, body)
   - Cassette management

2. **Consumer-Driven Contract Testing Utilities**
   - Contract definition helpers
   - Mock server integration
   - Contract validation utilities

3. **Enhanced Secrets Management**
   - Integration with secrets managers
   - Environment variable helpers
   - Secure credential injection

**Acceptance Criteria**:
- HTTP interactions can be recorded and replayed
- Contract testing utilities are functional
- Secrets can be loaded from external sources
- All features have comprehensive documentation

**Dependencies**: Phase 1 must be complete

## API Design

### Client Interface

#### Synchronous Client

```python
from httpx_integrator import Client, ClientConfig

# Basic usage
client = Client(
    config=ClientConfig(
        timeouts=TimeoutConfig(connect=5.0, read=30.0),
        retries=RetryConfig(max_attempts=3, backoff_factor=1.0),
    )
)

response = client.get("https://api.example.com/users")
```

#### Asynchronous Client

```python
from httpx_integrator import AsyncClient, ClientConfig

async def main():
    client = AsyncClient(
        config=ClientConfig(
            timeouts=TimeoutConfig(connect=5.0, read=30.0),
            retries=RetryConfig(max_attempts=3),
        )
    )

    response = await client.get("https://api.example.com/users")
```

or

```python
from httpx_integrator import AsyncClient, ClientConfig

async def main():
    with AsyncClient(
        config=ClientConfig(
            timeouts=TimeoutConfig(connect=5.0, read=30.0),
            retries=RetryConfig(max_attempts=3),
        )
    ):
        response = await client.get("https://api.example.com/users")
```


### Method Signatures

The client provides methods mirroring `httpx`:

**Synchronous**:
- `get(url, **kwargs) -> Response`
- `post(url, **kwargs) -> Response`
- `put(url, **kwargs) -> Response`
- `patch(url, **kwargs) -> Response`
- `delete(url, **kwargs) -> Response`
- `head(url, **kwargs) -> Response`
- `options(url, **kwargs) -> Response`
- `request(method, url, **kwargs) -> Response`

**Asynchronous**:
- `get(url, **kwargs) -> Awaitable[Response]`
- `post(url, **kwargs) -> Awaitable[Response]`
- `put(url, **kwargs) -> Awaitable[Response]`
- `patch(url, **kwargs) -> Awaitable[Response]`
- `delete(url, **kwargs) -> Awaitable[Response]`
- `head(url, **kwargs) -> Awaitable[Response]`
- `options(url, **kwargs) -> Awaitable[Response]`
- `request(method, url, **kwargs) -> Awaitable[Response]`

### Pass-Through Configuration

All `httpx` parameters are passed through:

```python
client = Client(
    config=ClientConfig(...),
    # All httpx.Client parameters are supported
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer token"},
    cookies={"session": "abc123"},
    auth=("user", "pass"),
    follow_redirects=True,
    # ... all other httpx parameters
)
```

### Per-Request Configuration

Configuration can be overridden per-request:

```python
# Override retries for a specific request
response = client.get(
    "https://api.example.com/users",
    retries=RetryConfig(max_attempts=5),
    timeout=TimeoutConfig(connect=10.0, read=60.0),
)
```

### Response Objects

The library returns `httpx.Response` objects, ensuring compatibility with existing code that uses `httpx` directly.

### Custom Exceptions

The library provides custom exception classes for better error handling:

```python
from httpx_integrator.exceptions import (
    ValidationError,           # Base exception for all validation errors
    RequestValidationError,    # Request validation failed
    ResponseValidationError,   # Response validation failed
    CircuitBreakerOpenError,   # Circuit breaker is open
    RateLimitExceededError,    # Rate limit exceeded
)

# ValidationError provides:
# - errors: List of Pydantic validation errors
# - context: Additional context (URL, method, headers, etc.)
# - original_exception: The underlying Pydantic ValidationError

# ResponseValidationError additionally provides:
# - status_code: HTTP status code
# - response_body: Response body (if available)
```

## Configuration Schema

### Pydantic Models

All configuration is done via Pydantic models for validation and IDE support.

#### Core Configuration

```python
from pydantic import BaseModel
from typing import Optional, List, Callable, Protocol
from httpx import Timeout as HTTPXTimeout, Response

class TimeoutConfig(BaseModel):
    """Timeout configuration."""
    connect: float = 5.0  # Connection timeout in seconds
    read: float = 30.0    # Read timeout in seconds
    write: Optional[float] = None  # Write timeout (optional)
    pool: Optional[float] = None   # Pool timeout (optional)

class RetryStrategy(Protocol):
    """Protocol for custom retry strategies."""
    def should_retry(self, attempt: int, exception: Optional[Exception], response: Optional[Response]) -> bool:
        """Determine if a retry should be attempted."""
        ...

class RetryConfig(BaseModel):
    """Retry configuration."""
    max_attempts: int = 3
    backoff_factor: float = 1.0
    backoff_max: float = 60.0
    jitter: bool = True
    retry_on_status: List[int] = [500, 502, 503, 504]
    retry_on_exceptions: List[type[Exception]] = [ConnectionError, TimeoutError]
    strategy: Optional[RetryStrategy] = None  # Custom retry strategy plugin

class CircuitBreakerStorage(Protocol):
    """Protocol for circuit breaker storage backends."""
    def get_state(self, key: str) -> Optional[str]:
        """Get circuit breaker state."""
        ...
    def set_state(self, key: str, state: str, ttl: Optional[float] = None) -> None:
        """Set circuit breaker state."""
        ...
    def increment_failure(self, key: str) -> int:
        """Increment failure count, return new count."""
        ...
    def reset_failures(self, key: str) -> None:
        """Reset failure count."""
        ...

class CircuitBreakerConfig(BaseModel):
    """Circuit breaker configuration."""
    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2   # Successes before half-open -> closed
    timeout: float = 60.0        # Time before attempting half-open
    expected_exception: type[Exception] = Exception
    name: Optional[str] = None   # For observability
    storage: Optional[CircuitBreakerStorage] = None  # Shared storage (Redis/Memcached)
    storage_key_prefix: str = "httpx_integrator:circuit_breaker"  # Key prefix for storage

class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""
    max_requests: int = 100
    time_window: float = 60.0  # Time window in seconds
    algorithm: str = "token_bucket"  # "token_bucket" or "sliding_window"
    per_endpoint: bool = False  # Apply per endpoint vs per client

class IdempotencyConfig(BaseModel):
    """Idempotency key configuration."""
    enabled: bool = True
    header_name: str = "Idempotency-Key"
    key_generator: Optional[Callable] = None  # Custom key generator
    methods: List[str] = ["POST", "PUT", "PATCH"]  # Methods that need keys

class ValidationConfig(BaseModel):
    """Validation configuration."""
    validate_request: bool = False
    validate_response: bool = True
    response_model: Optional[type[BaseModel]] = None  # Pydantic model
    strict: bool = True  # Strict validation mode

class TracingConfig(BaseModel):
    """Distributed tracing configuration."""
    enabled: bool = True
    correlation_id_header: str = "X-Correlation-ID"
    generate_correlation_id: bool = True
    opentelemetry_enabled: bool = False
    trace_sampling_rate: float = 1.0  # 0.0 to 1.0

class ClientConfig(BaseModel):
    """Main client configuration."""
    timeouts: Optional[TimeoutConfig] = None
    retries: Optional[RetryConfig] = None
    circuit_breaker: Optional[CircuitBreakerConfig] = None
    rate_limit: Optional[RateLimitConfig] = None
    idempotency: Optional[IdempotencyConfig] = None
    validation: Optional[ValidationConfig] = None
    tracing: Optional[TracingConfig] = None

    class Config:
        extra = "forbid"  # Prevent typos
```

### TypedDict Alternative

For type-only usage (no runtime validation), TypedDict variants are provided:

```python
from typing import TypedDict

class TimeoutConfigDict(TypedDict, total=False):
    connect: float
    read: float
    write: float
    pool: float
```

### Hierarchical Configuration

Configuration can be set at three levels:

1. **Global defaults**: Set via environment variables or config files
2. **Per-client**: Set when creating the client
3. **Per-request**: Override for individual requests

```python
# Global defaults (via environment)
# HTTPX_INTEGRATOR_TIMEOUT_CONNECT=5.0
# HTTPX_INTEGRATOR_TIMEOUT_READ=30.0

# Per-client
client = Client(
    config=ClientConfig(
        timeouts=TimeoutConfig(connect=10.0, read=60.0),
    )
)

# Per-request (overrides client config)
response = client.get(
    "https://api.example.com/users",
    timeout=TimeoutConfig(connect=2.0, read=10.0),
)
```

## Dependencies

### Core Dependencies

- **httpx** (>=0.27.0): Underlying HTTP client
- **pydantic** (>=2.0.0): Configuration validation and data models

### Resilience Dependencies

- **tenacity** (>=8.2.0): Retry logic with exponential backoff
- **circuitbreaker** (>=2.0.0): Circuit breaker implementation
  - Alternative: **pybreaker** (if circuitbreaker is not suitable)

### Circuit Breaker Storage (Optional)

- **redis** (>=5.0.0): Redis client for shared circuit breaker state
- **pymemcache** (>=4.0.0): Memcached client for shared circuit breaker state
  - Alternative: **python-memcached** (if pymemcache is not suitable)

### Rate Limiting

- **limits** (>=3.0.0): Rate limiting library with multiple algorithms
  - Alternative: Custom implementation using `asyncio` and `time`

### Optional Dependencies

- **opentelemetry-api** (>=1.20.0): Distributed tracing (Phase 3)
- **opentelemetry-sdk** (>=1.20.0): OpenTelemetry SDK (Phase 3)
- **vcrpy** (>=6.0.0): VCR-style request recording (Phase 4)

### Development Dependencies

- **pytest** (>=7.4.0): Testing framework
- **pytest-asyncio** (>=0.21.0): Async test support
- **pytest-xdist** (>=3.8.0): Test parallelization
- **pytest-cov** (>=4.1.0): Coverage reporting
- **httpx** (for test servers): Mock HTTP servers
- **mypy** (>=1.5.0): Type checking
- **ruff** (>=0.1.0): Linting and formatting

### Dependency Management

All dependencies are managed via `uv` and specified in `pyproject.toml`. Optional dependencies are grouped as extras:

```toml
[project.optional-dependencies]
tracing = ["opentelemetry-api>=1.20.0", "opentelemetry-sdk>=1.20.0"]
testing = ["vcrpy>=6.0.0"]
circuit-breaker-redis = ["redis>=5.0.0"]
circuit-breaker-memcached = ["pymemcache>=4.0.0"]
```

## Implementation Roadmap

### Phase 1: MVP (Weeks 1-3)

**Week 1: Foundation**
- [ ] Project structure setup
- [ ] Core client wrapper (sync)
- [ ] Basic configuration system (Pydantic)
- [ ] Timeout implementation
- [ ] Unit tests for timeouts

**Week 2: Retries**
- [ ] Retry mechanism with tenacity
- [ ] Exponential backoff with jitter
- [ ] Configurable retry conditions
- [ ] RetryStrategy protocol definition
- [ ] Plugin system for custom strategies
- [ ] Async client wrapper
- [ ] Integration tests

**Week 3: Validation**
- [ ] Request validation
- [ ] Response validation
- [ ] Pydantic model integration
- [ ] Custom exception classes (ValidationError, RequestValidationError, ResponseValidationError)
- [ ] Error handling and context
- [ ] Documentation

**Deliverables**:
- Working sync/async clients
- Timeout, retry, and validation features
- Comprehensive test suite (>90% coverage)
- Basic documentation

### Phase 2: Advanced Resilience (Weeks 4-6)

**Week 4: Circuit Breakers**
- [ ] Circuit breaker integration
- [ ] Per-endpoint circuit breakers
- [ ] In-memory state management
- [ ] Redis/Memcached storage backends
- [ ] Distributed state sharing
- [ ] Metrics and observability

**Week 5: Rate Limiting**
- [ ] Rate limiter implementation
- [ ] Token bucket algorithm
- [ ] Per-endpoint rate limits
- [ ] Rate limit header parsing

**Week 6: Idempotency**
- [ ] Idempotency key generation
- [ ] Header injection
- [ ] Configuration options
- [ ] Testing and documentation

**Deliverables**:
- Circuit breaker, rate limiting, and idempotency features
- Integration tests with real HTTP servers
- Updated documentation

### Phase 3: Observability & Isolation (Weeks 7-9)

**Week 7: Distributed Tracing**
- [ ] Correlation ID generation
- [ ] Logging integration
- [ ] Trace context propagation
- [ ] OpenTelemetry integration (optional)

**Week 8: Bulkheads**
- [ ] Connection pool isolation
- [ ] Resource limits
- [ ] Configuration

**Week 9: Advanced Validation**
- [ ] Complex Pydantic model validation
- [ ] Custom validators
- [ ] Response transformation
- [ ] Schema versioning

**Deliverables**:
- Tracing and observability features
- Resource isolation
- Advanced validation capabilities

### Phase 4: Testing & Operational Tools (Weeks 10-12)

**Week 10-11: VCR Integration**
- [ ] Request recording
- [ ] Cassette management
- [ ] Replay functionality
- [ ] Matching strategies

**Week 12: Contract Testing & Secrets**
- [ ] Contract testing utilities
- [ ] Secrets management integration
- [ ] Documentation
- [ ] Examples and tutorials

**Deliverables**:
- VCR-style testing tools
- Contract testing utilities
- Enhanced secrets management
- Complete documentation

### Testing Strategy

**Unit Tests**:
- Test each feature in isolation
- Mock external dependencies
- Test configuration validation
- Test error cases

**Integration Tests**:
- Test with real HTTP servers (httpx test server)
- Test retry behavior
- Test circuit breaker behavior
- Test rate limiting

**End-to-End Tests**:
- Test complete workflows
- Test with real third-party APIs (optional, rate-limited)
- Test async/sync compatibility

**Coverage Target**: >90% code coverage

### Documentation Requirements

1. **API Documentation**: Comprehensive docstrings with examples
2. **User Guide**: Getting started, configuration, examples
3. **Architecture Documentation**: Design decisions, patterns used
4. **Migration Guide**: How to migrate from httpx
5. **Best Practices**: When to use which features
6. **Examples**: Real-world use cases

## Non-Goals

The following are explicitly **not** goals for this project:

1. **Drop-in httpx Replacement**: This is a new interface, not a replacement
2. **Built-in Caching**: Caching should be handled at the application layer
3. **Authentication Mechanisms**: Authentication is passed through to httpx
4. **Request/Response Serialization**: Use httpx's built-in JSON handling
5. **WebSocket Support**: Focus on HTTP/HTTPS only
6. **HTTP/2 Specific Features**: Rely on httpx's HTTP/2 support
7. **Custom Transport Layers**: Use httpx's transport system
8. **Built-in OAuth/Token Refresh**: Handle at application layer

## Success Metrics

- **Usability**: Can a developer integrate with a third-party API in <10 minutes?
- **Resilience**: Does the library handle common failure scenarios gracefully?
- **Performance**: Minimal overhead compared to raw httpx (<5% latency increase)
- **Reliability**: Test coverage >90%, no critical bugs in production use
- **Adoption**: Clear documentation and examples enable self-service usage

## Design Decisions

### Custom Retry Strategies (Plugins)

**Decision**: Yes, we support custom retry strategies via a plugin system.

**Implementation**:
- Define a `RetryStrategy` protocol that plugins must implement
- Allow users to provide custom retry strategies via `RetryConfig.strategy`
- Built-in strategies (exponential backoff, linear, etc.) are provided as defaults
- Plugin system enables advanced use cases (e.g., retry based on response content, custom backoff algorithms)

**Example**:
```python
from httpx_integrator import RetryStrategy

class CustomRetryStrategy(RetryStrategy):
    def should_retry(self, attempt: int, exception: Optional[Exception], response: Optional[Response]) -> bool:
        # Custom logic here
        return attempt < 5 and response and response.status_code >= 500

config = RetryConfig(strategy=CustomRetryStrategy())
```

### Circuit Breaker State Sharing

**Decision**: Circuit breakers should be shared across all client instances using an external cache (Redis or Memcached).

**Rationale**:
- In distributed systems, circuit breaker state must be shared across all instances
- Prevents one instance from making requests while another has the circuit open
- Enables consistent failure handling across the entire application

**Implementation**:
- Circuit breaker state stored in Redis or Memcached
- Storage backend is pluggable via `CircuitBreakerStorage` protocol
- Default: in-memory storage (single instance only)
- Optional: Redis or Memcached for distributed deployments
- Storage keys are namespaced with configurable prefix

**Example**:
```python
from httpx_integrator import CircuitBreakerConfig
from httpx_integrator.storage import RedisCircuitBreakerStorage
import redis

redis_client = redis.Redis(host='localhost', port=6379)
storage = RedisCircuitBreakerStorage(redis_client)

config = CircuitBreakerConfig(
    failure_threshold=5,
    storage=storage,
    storage_key_prefix="myapp:circuit_breaker"
)
```

### Validation Error Handling

**Decision**: Validation errors should be custom exceptions or wrappers (similar to Starlette > FastAPI pattern).

**Rationale**:
- Provides better error messages and context
- Enables application-specific error handling
- Maintains compatibility with Pydantic validation while adding HTTP-specific context

**Implementation**:
- Custom exception hierarchy: `ValidationError` (base) > `RequestValidationError`, `ResponseValidationError`
- Exceptions wrap Pydantic validation errors with additional context (URL, method, headers)
- Exceptions are serializable and include detailed error information
- Compatible with FastAPI/Starlette error handling patterns

**Example**:
```python
from httpx_integrator import ResponseValidationError

try:
    response = client.get("/users/123")
except ResponseValidationError as e:
    print(f"Validation failed: {e.errors}")
    print(f"Response status: {e.status_code}")
    print(f"Response body: {e.response_body}")
```

### CLI Tool

**Decision**: CLI tool is a nice-to-have but not mandatory for v1.0.

**Status**: Deferred to future release (post-v1.0)

**Potential Features** (if implemented):
- Test HTTP endpoints with configured resilience features
- Validate configuration files
- Generate example configurations
- Debug circuit breaker states

### Open Questions

1. ~~Should we support custom retry strategies via plugins?~~ **RESOLVED**: Yes, via plugin system
2. ~~Should circuit breakers be shared across client instances?~~ **RESOLVED**: Yes, via Redis/Memcached
3. How should we handle rate limit headers from different APIs? (e.g., `X-RateLimit-Remaining`, `Retry-After`)
4. ~~Should validation errors be custom exceptions or use Pydantic's?~~ **RESOLVED**: Custom exceptions wrapping Pydantic errors
5. ~~Should we provide a CLI tool for testing configurations?~~ **RESOLVED**: Nice-to-have, deferred

## Appendix: Example Usage

### Basic Example

```python
from httpx_integrator import Client, ClientConfig, TimeoutConfig, RetryConfig

config = ClientConfig(
    timeouts=TimeoutConfig(connect=5.0, read=30.0),
    retries=RetryConfig(max_attempts=3, backoff_factor=1.0),
)

client = Client(config=config)
response = client.get("https://api.example.com/users")
```

### Advanced Example

```python
from httpx_integrator import (
    Client, ClientConfig, TimeoutConfig, RetryConfig,
    CircuitBreakerConfig, RateLimitConfig, ValidationConfig
)
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

config = ClientConfig(
    timeouts=TimeoutConfig(connect=5.0, read=30.0),
    retries=RetryConfig(max_attempts=5, retry_on_status=[500, 502, 503]),
    circuit_breaker=CircuitBreakerConfig(
        failure_threshold=5,
        timeout=60.0,
    ),
    rate_limit=RateLimitConfig(max_requests=100, time_window=60.0),
    validation=ValidationConfig(
        validate_response=True,
        response_model=UserResponse,
    ),
)

client = Client(
    config=config,
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer token"},
)

# Response is validated and typed
user = client.get("/users/123").json()  # Returns UserResponse
```

### Plugin Example: Custom Retry Strategy

```python
from httpx_integrator import Client, ClientConfig, RetryConfig, RetryStrategy
from httpx import Response
from typing import Optional

class SmartRetryStrategy(RetryStrategy):
    """Retry only on 5xx errors, not on 4xx."""
    def should_retry(self, attempt: int, exception: Optional[Exception], response: Optional[Response]) -> bool:
        if exception:
            return attempt < 3  # Retry on network errors
        if response:
            return response.status_code >= 500 and attempt < 5  # Retry on server errors
        return False

config = ClientConfig(
    retries=RetryConfig(
        max_attempts=5,
        strategy=SmartRetryStrategy(),
    )
)

client = Client(config=config)
```

### Circuit Breaker with Shared Storage Example

```python
from httpx_integrator import Client, ClientConfig, CircuitBreakerConfig
from httpx_integrator.storage import RedisCircuitBreakerStorage
import redis

# Create Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Create storage backend
storage = RedisCircuitBreakerStorage(redis_client)

config = ClientConfig(
    circuit_breaker=CircuitBreakerConfig(
        failure_threshold=5,
        timeout=60.0,
        storage=storage,  # Shared across all client instances
        storage_key_prefix="myapp:api:circuit_breaker",
    )
)

# Multiple clients share the same circuit breaker state
client1 = Client(config=config, base_url="https://api.example.com")
client2 = Client(config=config, base_url="https://api.example.com")

# If client1 opens the circuit, client2 will also see it as open
```

### Error Handling Example

```python
from httpx_integrator import Client, ClientConfig, ValidationConfig
from httpx_integrator.exceptions import ResponseValidationError, CircuitBreakerOpenError
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

config = ClientConfig(
    validation=ValidationConfig(
        validate_response=True,
        response_model=UserResponse,
    )
)

client = Client(config=config)

try:
    response = client.get("https://api.example.com/users/123")
    user = response.json()  # Already validated as UserResponse
except ResponseValidationError as e:
    print(f"Validation failed: {e.errors}")
    print(f"Status code: {e.status_code}")
    print(f"Response body: {e.response_body}")
    # Handle validation error
except CircuitBreakerOpenError:
    print("Circuit breaker is open, service unavailable")
    # Handle circuit breaker open
```
