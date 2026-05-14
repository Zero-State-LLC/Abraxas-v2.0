from __future__ import annotations

from core.runtime_spine.models import (
    RuntimeInvocation,
    RuntimePosture,
    _VALID_LANES,
    _VALID_SCOPES,
    _VALID_STATES,
)

# Explicit allowlist: maps each valid lane to the set of scopes it may claim.
# Any scope not listed for a given lane is rejected as unknown_authority_route.
_LANE_SCOPE_MATRIX: dict[str, frozenset[str]] = {
    "SHADOW": frozenset({"OBSERVATION", "DIAGNOSE", "ANNOTATE"}),
    "FORECAST": frozenset({"FORECAST"}),
    "PROJECTION": frozenset({"RENDER"}),
    "CANON": frozenset({"DOCTRINE", "REGISTRY", "CANON"}),
    "OPERATOR": frozenset({"APPROVE", "DENY", "MANUAL_OVERRIDE", "OPERATOR"}),
    "GOVERNANCE": frozenset({"GOVERNANCE", "DOCTRINE", "REGISTRY"}),
}


def authority_gate(invocation: RuntimeInvocation) -> tuple[RuntimePosture, str]:
    lane = invocation.route.lane
    scope = invocation.route.authority_scope
    promo = invocation.route.promotion_state

    # --- Fail-closed: reject unrecognised values defensively (RuntimeRoute
    #     __post_init__ already enforces this at construction, but authority_gate
    #     must be independently safe against bypass). ---
    if lane not in _VALID_LANES:
        return RuntimePosture.BLOCKED, "invalid_lane"
    if scope not in _VALID_SCOPES:
        return RuntimePosture.BLOCKED, "invalid_scope"
    if promo not in _VALID_STATES:
        return RuntimePosture.BLOCKED, "invalid_state"

    # --- Specific invariant violations ---
    if lane == "PROJECTION" and scope == "INFERENCE":
        return RuntimePosture.BLOCKED, "projection_inference_blocked"
    if lane == "SHADOW" and scope == "FORECAST":
        return RuntimePosture.BLOCKED, "shadow_forecast_blocked"
    if lane == "FORECAST" and not invocation.outcome_binding:
        return RuntimePosture.BLOCKED, "Forecast requires outcome binding."
    if promo == "CANON_ACTIVE" and invocation.route.subsystem_id.startswith("repo-only"):
        return RuntimePosture.BLOCKED, "Repo-only authority cannot claim canon-active status."
    if promo == "CANON_ACTIVE" and not invocation.canon_attestation:
        return RuntimePosture.NOT_COMPUTABLE, "Canon attestation is missing for canon-active route."

    # --- Fail-closed: unknown route combination must not default to PASS.
    #     Only scope values explicitly listed in the lane's allowlist may proceed. ---
    allowed_scopes = _LANE_SCOPE_MATRIX.get(lane, frozenset())
    if scope not in allowed_scopes:
        return RuntimePosture.BLOCKED, "unknown_authority_route"

    return RuntimePosture.PASS, "Authority checks passed."
