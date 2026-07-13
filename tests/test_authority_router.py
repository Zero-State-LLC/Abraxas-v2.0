"""Tests for core/runtime_spine/authority_router.py (HARDENING candidate 929fd38c389d4216)"""

from core.runtime_spine.authority_router import authority_gate
from core.runtime_spine.models import RuntimeInvocation, RuntimeRoute

def _make_invocation(lane="SHADOW", scope="OBSERVATION", promo="SHADOW_ONLY", subsystem_id="test", outcome_binding=None, canon_attestation=None):
    route = RuntimeRoute(
        subsystem_id=subsystem_id,
        lane=lane,
        promotion_state=promo,
        authority_scope=scope,
    )
    return RuntimeInvocation(route=route, payload={}, outcome_binding=outcome_binding, canon_attestation=canon_attestation)

def test_valid_shadow_observation():
    inv = _make_invocation(lane="SHADOW", scope="OBSERVATION", promo="SHADOW_ONLY")
    posture, reason = authority_gate(inv)
    assert posture.value == "PASS"
    assert "passed" in reason.lower()

def test_blocked_unknown_authority_route():
    inv = _make_invocation(lane="SHADOW", scope="FORECAST", promo="SHADOW_ONLY")  # FORECAST not allowed for SHADOW
    posture, reason = authority_gate(inv)
    assert posture.value == "BLOCKED"
    assert "unknown" in reason.lower() or "blocked" in reason.lower()

def test_forecast_requires_outcome_binding():
    inv = _make_invocation(lane="FORECAST", scope="FORECAST", promo="CANARY", outcome_binding=None)
    posture, reason = authority_gate(inv)
    assert posture.value == "BLOCKED"
    assert "outcome binding" in reason.lower()
