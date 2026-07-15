"""Independent fail-closed stabilization-entry gate."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.campaign_director.stabilization_campaign import StabilizationEntryDecision

from .models import StabilizationGateDecision

READINESS_KEYS = (
    "python_ready",
    "typescript_ready",
    "contract_inventory_complete",
    "conformance_corpus_ready",
    "reproducibility_ready",
    "canonical_artifact_safety_ready",
)

AUTHORITY_CONTAINER_KEYS = ("authority", "authority_boundary")


def evaluate_stabilization_entry(
    evidence: Mapping[str, Any] | None,
) -> StabilizationGateDecision:
    supplied = evidence or {}
    flags = {key: supplied.get(key) is True for key in READINESS_KEYS}
    missing = sorted(key for key in READINESS_KEYS if key not in supplied)
    blocking = {str(item) for item in supplied.get("blocking_findings", [])}
    blocking.update(f"MISSING_EVIDENCE:{key}" for key in missing)
    for container_key in AUTHORITY_CONTAINER_KEYS:
        authority = supplied.get(container_key)
        if authority is None:
            continue
        if not isinstance(authority, Mapping):
            blocking.add(f"INVALID_EVIDENCE:{container_key}")
            continue
        for key, value in authority.items():
            is_unlocked = value is not True if key == "advisory_only" else value is True
            if is_unlocked:
                blocking.add(f"AUTHORITY_NOT_LOCKED:{key}")
    bounded = tuple(sorted(str(item) for item in supplied.get("bounded_exceptions", [])))
    confidence = str(supplied.get("full_suite_confidence", "NOT_COMPUTABLE"))
    ready = all(flags.values()) and confidence != "NOT_COMPUTABLE" and not blocking
    if not ready:
        decision = StabilizationEntryDecision.HELD.value
    elif bounded:
        decision = StabilizationEntryDecision.READY_WITH_BOUNDED_EXCEPTIONS.value
    else:
        decision = StabilizationEntryDecision.READY.value
    return StabilizationGateDecision(
        decision=decision,
        **flags,
        full_suite_confidence=confidence,
        blocking_findings=tuple(sorted(blocking)),
        bounded_exceptions=bounded,
        evidence_refs=tuple(
            sorted(str(item) for item in supplied.get("evidence_refs", []))
        ),
        operator_action_required=True,
    )
