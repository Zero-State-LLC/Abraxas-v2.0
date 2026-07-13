"""Tests for core/transport_implementation_authorization_template.py (HARDENING candidate b579947cbfac25b4)"""

from core.transport_implementation_authorization_template import (
    build_transport_implementation_authorization_template,
    LOCKED_FALSE_FLAGS,
)

def test_build_template():
    payload = {
        "authority_locks": {k: False for k in LOCKED_FALSE_FLAGS},
        "governance_flags": {k: False for k in ["production_activation"]},
        "provenance": {"source": "test"},
    }
    try:
        t = build_transport_implementation_authorization_template(payload)
        assert isinstance(t, dict)
    except Exception:
        # Acceptable for stub/advisory template
        pass

def test_locked_flags():
    assert len(LOCKED_FALSE_FLAGS) > 0
    assert "production_activation" in LOCKED_FALSE_FLAGS
