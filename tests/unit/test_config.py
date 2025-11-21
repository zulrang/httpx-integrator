"""Tests for configuration models."""

import pytest
from pydantic import ValidationError

from httpx_integrator.config import ClientConfig, TimeoutConfig


def test_timeout_config_defaults():
    """Test TimeoutConfig has correct default values."""
    config = TimeoutConfig()
    assert config.connect == 5.0
    assert config.read == 30.0
    assert config.write is None
    assert config.pool is None


def test_timeout_config_custom_values():
    """Test TimeoutConfig accepts custom values."""
    config = TimeoutConfig(connect=10.0, read=60.0, write=5.0, pool=10.0)
    assert config.connect == 10.0
    assert config.read == 60.0
    assert config.write == 5.0
    assert config.pool == 10.0


def test_timeout_config_negative_values_raises_error():
    """Test TimeoutConfig rejects negative values."""
    with pytest.raises(ValidationError):
        TimeoutConfig(connect=-1.0)

    with pytest.raises(ValidationError):
        TimeoutConfig(read=-1.0)

    with pytest.raises(ValidationError):
        TimeoutConfig(connect=5.0, read=-1.0)


def test_timeout_config_zero_values():
    """Test TimeoutConfig accepts zero values."""
    config = TimeoutConfig(connect=0.0, read=0.0)
    assert config.connect == 0.0
    assert config.read == 0.0


def test_timeout_config_non_numeric_raises_error():
    """Test TimeoutConfig rejects non-numeric values."""
    with pytest.raises(ValidationError):
        TimeoutConfig(connect="invalid")

    with pytest.raises(ValidationError):
        TimeoutConfig(read="invalid")


def test_timeout_config_optional_fields():
    """Test TimeoutConfig optional fields can be None."""
    config = TimeoutConfig(connect=5.0, read=30.0)
    assert config.write is None
    assert config.pool is None

    config_with_optional = TimeoutConfig(connect=5.0, read=30.0, write=5.0, pool=10.0)
    assert config_with_optional.write == 5.0
    assert config_with_optional.pool == 10.0


def test_timeout_config_pydantic_model_behavior():
    """Test TimeoutConfig behaves like a Pydantic model."""
    config = TimeoutConfig(connect=10.0, read=60.0)

    # Test dict conversion
    config_dict = config.model_dump()
    assert config_dict["connect"] == 10.0
    assert config_dict["read"] == 60.0

    # Test JSON serialization
    config_json = config.model_dump_json()
    assert "connect" in config_json
    assert "10.0" in config_json


def test_client_config_no_configuration():
    """Test ClientConfig can be instantiated with no configuration."""
    config = ClientConfig()
    assert config.timeouts is None
    assert config.retries is None
    assert config.circuit_breaker is None
    assert config.rate_limit is None
    assert config.idempotency is None
    assert config.validation is None
    assert config.tracing is None


def test_client_config_with_timeout_configuration():
    """Test ClientConfig accepts timeout configuration."""
    timeout_config = TimeoutConfig(connect=10.0, read=60.0)
    config = ClientConfig(timeouts=timeout_config)
    assert config.timeouts is not None
    assert config.timeouts.connect == 10.0
    assert config.timeouts.read == 60.0


def test_client_config_with_multiple_configurations():
    """Test ClientConfig accepts multiple configurations."""
    timeout_config = TimeoutConfig(connect=5.0, read=30.0)
    config = ClientConfig(timeouts=timeout_config)
    assert config.timeouts is not None
    # Other configs are None for now (will be added in later phases)
    assert config.retries is None


def test_client_config_extra_forbid_rejects_unknown_fields():
    """Test ClientConfig rejects unknown fields (extra='forbid')."""
    with pytest.raises(ValidationError) as exc_info:
        ClientConfig(unknown_field="value")

    errors = exc_info.value.errors()
    assert any(error["type"] == "extra_forbidden" for error in errors)
