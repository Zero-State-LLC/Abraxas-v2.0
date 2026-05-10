from __future__ import annotations

from core.runtime_spine.models import RuntimeInvocation, RuntimePosture


def authority_gate(invocation: RuntimeInvocation) -> tuple[RuntimePosture, str]:
    lane = invocation.route.lane
    scope = invocation.route.authority_scope
    promo = invocation.route.promotion_state

    if lane == "PROJECTION" and scope == "INFERENCE":
        return RuntimePosture.BLOCKED, "Projection lane cannot claim inference authority."
    if lane == "SHADOW" and scope == "FORECAST":
        return RuntimePosture.BLOCKED, "Shadow lane cannot emit forecast authority."
    if lane == "FORECAST" and not invocation.outcome_binding:
        return RuntimePosture.BLOCKED, "Forecast requires outcome binding."
    if promo == "CANON_ACTIVE" and invocation.route.subsystem_id.startswith("repo-only"):
        return RuntimePosture.BLOCKED, "Repo-only authority cannot claim canon-active status."
    if promo == "CANON_ACTIVE" and not invocation.canon_attestation:
        return RuntimePosture.NOT_COMPUTABLE, "Canon attestation is missing for canon-active route."
    return RuntimePosture.PASS, "Authority checks passed."
