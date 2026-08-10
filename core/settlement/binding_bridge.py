"""Resolution-output → SettlementVerdict.v1 mapping (advisory, non-activating).

Convergence layer named by this package's README: map resolution outputs
(currently ForecastOutcomeBindingPacket.v1) into SettlementVerdict.v1 so that
score computation can be gated on a score-ready settlement verdict instead of
reading binding status directly.

This module is pure and fail-closed:
- it does not write to disk, resolve outcomes, or escalate authority;
- without an explicit ``authority_ref`` it never emits ``SETTLED``;
- Brier scoring remains telemetry-only; this mapping does not activate it.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash

from .models import (
    AuthorityRef,
    SettlementConflictSummary,
    SettlementDecision,
    SettlementReason,
    SettlementStatus,
    SettlementVerdict,
)
from .verdict import build_settlement_verdict

BINDING_BRIDGE_POLICY = "POLICY_BINARY_OUTCOME_BINDING_V1"

# Binary Brier scoring accepts only TRUE/FALSE. PARTIAL is settle-able but not
# binary-score-ready; VOID and NOT_COMPUTABLE are never score-ready.
SCORE_READY_DECISIONS = frozenset({SettlementDecision.TRUE, SettlementDecision.FALSE})

_DECISION_BY_BINDING_STATUS = {
    "matched": SettlementDecision.TRUE,
    "mismatched": SettlementDecision.FALSE,
    "expired": SettlementDecision.VOID,
    "unresolved": SettlementDecision.NOT_COMPUTABLE,
}


def _binding_payload(binding: Any) -> dict[str, Any]:
    if isinstance(binding, Mapping):
        return dict(binding)
    model_dump = getattr(binding, "model_dump", None)
    if callable(model_dump):
        return model_dump(mode="json")
    raise TypeError("binding must be a Mapping or a pydantic model with model_dump()")


def settlement_verdict_from_outcome_binding(
    binding: Any,
    *,
    settlement_id: str,
    forecast_id: str,
    evidence_packet_id: str,
    evidence_hash: str,
    created_by_lane: str,
    authority_ref: AuthorityRef | None = None,
    binding_hash: str | None = None,
) -> SettlementVerdict:
    """Map a ForecastOutcomeBindingPacket into a SettlementVerdict.v1 (pure).

    Fail-closed status derivation:
    - ``unresolved``  → DRAFT with decision NOT_COMPUTABLE
    - ``expired``     → VOID with decision VOID
    - ``matched`` / ``mismatched`` → SETTLED only when ``authority_ref`` is
      provided; DRAFT otherwise. The mapping never invents authority.
    """
    payload = _binding_payload(binding)
    binding_id = payload["binding_id"]
    forecast_hash = payload["forecast_hash"]
    binding_status = payload["binding_status"]

    decision = _DECISION_BY_BINDING_STATUS.get(binding_status)
    if decision is None:
        raise ValueError(f"unknown binding_status: {binding_status!r}")

    if binding_status == "unresolved":
        settlement_status = SettlementStatus.DRAFT
    elif binding_status == "expired":
        settlement_status = SettlementStatus.VOID
    elif authority_ref is not None:
        settlement_status = SettlementStatus.SETTLED
    else:
        settlement_status = SettlementStatus.DRAFT

    resolved_binding_hash = binding_hash if binding_hash is not None else canonical_hash(payload)

    reason = SettlementReason(
        reason_id=f"binding:{binding_id}",
        reason_type="OUTCOME_BINDING",
        description=f"Outcome binding {binding_id} reported binding_status={binding_status}.",
        source_ref_ids=(binding_id,),
        policy=BINDING_BRIDGE_POLICY,
    )

    return build_settlement_verdict(
        settlement_id=settlement_id,
        forecast_id=forecast_id,
        forecast_hash=forecast_hash,
        binding_id=binding_id,
        binding_hash=resolved_binding_hash,
        evidence_packet_id=evidence_packet_id,
        evidence_hash=evidence_hash,
        decision=decision,
        reasons=(reason,),
        conflict_summary=SettlementConflictSummary(
            has_conflicts=False,
            conflict_ids=(),
            conflict_policy="NO_CONFLICT_POLICY",
            resolution_posture="CLEAR",
        ),
        settlement_status=settlement_status,
        created_by_lane=created_by_lane,
        authority_ref=authority_ref,
    )


def is_score_ready(verdict: SettlementVerdict | Mapping[str, Any]) -> bool:
    """True when the verdict may feed binary score computation.

    Requires validation status PASS, settlement_status SETTLED, and a binary
    decision (TRUE/FALSE). Everything else — DRAFT, VOID, CONFLICTING,
    NOT_COMPUTABLE, PARTIAL, or any validator finding above PASS — is not
    score-ready.
    """
    from .validator import validate_settlement_verdict

    report = validate_settlement_verdict(verdict)
    if report.status != "PASS":
        return False
    if isinstance(verdict, SettlementVerdict):
        status = verdict.settlement_status
        decision = verdict.decision
    else:
        status = SettlementStatus(verdict["settlement_status"])
        decision = SettlementDecision(verdict["decision"])
    return status == SettlementStatus.SETTLED and decision in SCORE_READY_DECISIONS


def observed_outcome_from_verdict(verdict: SettlementVerdict | Mapping[str, Any]) -> int:
    """Binary outcome for score computation: TRUE → 1, FALSE → 0.

    Raises ``ValueError`` when the verdict is not score-ready; scoring paths
    must not fall back to raw binding status when a verdict is supplied.
    """
    if not is_score_ready(verdict):
        raise ValueError("settlement verdict is not score-ready (requires PASS + SETTLED + TRUE/FALSE)")
    decision = verdict.decision if isinstance(verdict, SettlementVerdict) else SettlementDecision(verdict["decision"])
    return 1 if decision == SettlementDecision.TRUE else 0
