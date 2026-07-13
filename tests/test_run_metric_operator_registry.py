"""Tests for metric operator registry (candidate ff6a1fbebeb01424)"""

from core.metric_operator_registry_stabilization import (
    SCHEMA_VERSION,
    LOCKED_FALSE_FLAGS,
    ALLOWED_VECTOR_TYPES,
)

def test_schema():
    assert SCHEMA_VERSION == "MetricOperatorRegistryStabilization.v1"

def test_locked_flags():
    assert "production_activation" in LOCKED_FALSE_FLAGS
    assert "canon_promotion" in LOCKED_FALSE_FLAGS
    assert len(LOCKED_FALSE_FLAGS) > 5

def test_allowed_vector_types():
    assert "VALID_METADATA_VECTOR" in ALLOWED_VECTOR_TYPES
    assert len(ALLOWED_VECTOR_TYPES) > 0
