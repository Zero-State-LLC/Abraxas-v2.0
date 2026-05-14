from core.runtime_spine.models import RuntimeInvocation, RuntimePosture, RuntimeRoute
from core.runtime_spine.router import build_runtime_spine_audit_payload, route_runtime_invocation

import pytest


def _invocation(**kwargs) -> RuntimeInvocation:
    route = RuntimeRoute(
        subsystem_id=kwargs.get("subsystem_id", "subsystem.alpha"),
        lane=kwargs.get("lane", "CANON"),
        promotion_state=kwargs.get("promotion_state", "CANON_ACTIVE"),
        authority_scope=kwargs.get("authority_scope", "CANON"),
    )
    return RuntimeInvocation(
        route=route,
        payload=kwargs.get("payload", {"k": 1}),
        canon_attestation=kwargs.get("canon_attestation", "attested"),
        outcome_binding=kwargs.get("outcome_binding", "bound"),
    )


def test_identical_invocation_identical_decision_hash() -> None:
    i1 = _invocation()
    i2 = _invocation()
    assert route_runtime_invocation(i1).decision_hash == route_runtime_invocation(i2).decision_hash


def test_projection_inference_blocked() -> None:
    decision = route_runtime_invocation(_invocation(lane="PROJECTION", authority_scope="INFERENCE"))
    assert decision.posture == RuntimePosture.BLOCKED


def test_shadow_forecast_emission_blocked() -> None:
    decision = route_runtime_invocation(_invocation(lane="SHADOW", authority_scope="FORECAST"))
    assert decision.posture == RuntimePosture.BLOCKED


def test_forecast_without_outcome_binding_blocked() -> None:
    decision = route_runtime_invocation(_invocation(lane="FORECAST", authority_scope="FORECAST", outcome_binding=None))
    assert decision.posture == RuntimePosture.BLOCKED


def test_canon_backed_route_passes_with_attestation() -> None:
    decision = route_runtime_invocation(_invocation(subsystem_id="canon.subsystem", promotion_state="CANON_ACTIVE", canon_attestation="valid-attest"))
    assert decision.posture == RuntimePosture.PASS


def test_missing_canon_attestation_not_computable() -> None:
    decision = route_runtime_invocation(_invocation(subsystem_id="canon.subsystem", promotion_state="CANON_ACTIVE", canon_attestation=None))
    assert decision.posture == RuntimePosture.NOT_COMPUTABLE


def test_runtime_spine_payload_includes_normalized_fields() -> None:
    payload = build_runtime_spine_audit_payload(_invocation())
    assert "status" in payload and "posture" in payload and "runtime_posture" in payload
    assert "audit_envelope" in payload


# --- New fail-closed tests (PATCH-P0-RUNTIME-AUTHORITY-FAIL-CLOSED-001) ---

def test_unknown_lane_fails_closed() -> None:
    """Construction of RuntimeRoute with an unknown lane must raise ValueError."""
    with pytest.raises(ValueError, match="invalid_lane"):
        _invocation(lane="UNKNOWN_LANE_XYZ")


def test_unknown_scope_fails_closed() -> None:
    """Construction of RuntimeRoute with an unknown scope must raise ValueError."""
    with pytest.raises(ValueError, match="invalid_scope"):
        _invocation(authority_scope="UNKNOWN_SCOPE_XYZ")


def test_unknown_state_fails_closed() -> None:
    """Construction of RuntimeRoute with an unknown promotion state must raise ValueError."""
    with pytest.raises(ValueError, match="invalid_state"):
        _invocation(promotion_state="UNKNOWN_STATE_XYZ")


def test_projection_cannot_route_as_inference_authority() -> None:
    """PROJECTION lane must be BLOCKED with reason 'projection_inference_blocked'."""
    decision = route_runtime_invocation(_invocation(lane="PROJECTION", authority_scope="INFERENCE"))
    assert decision.posture == RuntimePosture.BLOCKED
    assert decision.reason == "projection_inference_blocked"


def test_shadow_cannot_route_as_forecast_authority() -> None:
    """SHADOW lane must be BLOCKED with reason 'shadow_forecast_blocked'."""
    decision = route_runtime_invocation(_invocation(lane="SHADOW", authority_scope="FORECAST"))
    assert decision.posture == RuntimePosture.BLOCKED
    assert decision.reason == "shadow_forecast_blocked"


def test_known_safe_route_still_passes() -> None:
    """A fully valid CANON route with attestation must still receive PASS."""
    decision = route_runtime_invocation(
        _invocation(
            subsystem_id="canon.subsystem",
            lane="CANON",
            authority_scope="CANON",
            promotion_state="CANON_ACTIVE",
            canon_attestation="attested",
            outcome_binding="bound",
        )
    )
    assert decision.posture == RuntimePosture.PASS


def test_unknown_route_combination_does_not_default_pass() -> None:
    """SHADOW lane claiming CANON scope is a valid-value combination but an invalid
    route combination and must NOT be allowed to PASS."""
    decision = route_runtime_invocation(_invocation(lane="SHADOW", authority_scope="CANON"))
    assert decision.posture != RuntimePosture.PASS
    assert decision.posture == RuntimePosture.BLOCKED
    assert decision.reason == "unknown_authority_route"

