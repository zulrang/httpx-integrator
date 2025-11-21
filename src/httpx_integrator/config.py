"""Configuration models for httpx-integrator."""

from pydantic import BaseModel, ConfigDict, Field


class TimeoutConfig(BaseModel):
    """Timeout configuration for HTTP requests.

    Attributes:
        connect: Connection timeout in seconds. Defaults to 5.0.
        read: Read timeout in seconds. Defaults to 30.0.
        write: Write timeout in seconds. Optional.
        pool: Pool timeout in seconds. Optional.
    """

    connect: float = Field(default=5.0, ge=0.0, description="Connection timeout in seconds")
    read: float = Field(default=30.0, ge=0.0, description="Read timeout in seconds")
    write: float | None = Field(default=None, ge=0.0, description="Write timeout in seconds")
    pool: float | None = Field(default=None, ge=0.0, description="Pool timeout in seconds")


class ClientConfig(BaseModel):
    """Main client configuration.

    Attributes:
        timeouts: Timeout configuration. Optional.
        retries: Retry configuration. Optional (Phase 1).
        circuit_breaker: Circuit breaker configuration. Optional (Phase 2).
        rate_limit: Rate limiting configuration. Optional (Phase 2).
        idempotency: Idempotency configuration. Optional (Phase 2).
        validation: Validation configuration. Optional (Phase 1).
        tracing: Tracing configuration. Optional (Phase 3).
    """

    model_config = ConfigDict(extra="forbid")

    timeouts: TimeoutConfig | None = None
    retries: None = None  # Will be implemented in Phase 1
    circuit_breaker: None = None  # Will be implemented in Phase 2
    rate_limit: None = None  # Will be implemented in Phase 2
    idempotency: None = None  # Will be implemented in Phase 2
    validation: None = None  # Will be implemented in Phase 1
    tracing: None = None  # Will be implemented in Phase 3
