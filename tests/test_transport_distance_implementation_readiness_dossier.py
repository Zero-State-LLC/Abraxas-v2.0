"""Tests for core/transport_distance_implementation_readiness_dossier.py (HARDENING candidate ec3bb2934441f4b0)"""

from core.transport_distance_implementation_readiness_dossier import (
    REQUIRED_BLOCKED_SCOPES, LOCKED_TRUE_AUTHORITY_KEYS, LOCKED_FALSE_AUTHORITY_KEYS,
    LOCKED_FALSE_GOVERNANCE_FLAGS, FORBIDDEN, SCHEMA_VERSION, DOSSIER_TYPE
)

def test_constants():
    assert "transport_computation" in REQUIRED_BLOCKED_SCOPES
    assert "production_activation" in REQUIRED_BLOCKED_SCOPES
    assert "advisory_only" in LOCKED_TRUE_AUTHORITY_KEYS
    assert "transport_computation_authorized" in LOCKED_FALSE_AUTHORITY_KEYS
    assert "executable" in FORBIDDEN
    assert SCHEMA_VERSION.startswith("TransportDistanceImplementationReadinessDossier")
    assert DOSSIER_TYPE == "TRANSPORT_DISTANCE_IMPLEMENTATION_READINESS_DOSSIER"

def test_forbidden_and_locks():
    assert "production_activation" in LOCKED_FALSE_GOVERNANCE_FLAGS
    for item in ["numpy", "scipy", "gpu-kernel"]:
        assert item in FORBIDDEN

def test_blocked_scopes_integrity():
    assert len(REQUIRED_BLOCKED_SCOPES) >= 5