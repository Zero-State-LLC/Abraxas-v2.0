from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromotionDecisionInputRef:
    source_type: str
    source_id: str
    source_hash: str


@dataclass(frozen=True)
class PromotionDecisionEvidenceLineage:
    lineage_id: str
    forecast_ref_ids: tuple[str, ...]
    brier_ref_ids: tuple[str, ...]
    calibration_ref_ids: tuple[str, ...]
    reliability_advisory_ref_ids: tuple[str, ...]
    canary_ref_ids: tuple[str, ...]
    operator_receipt_ref_ids: tuple[str, ...]
    lineage_complete: bool


@dataclass(frozen=True)
class PromotionDecisionPosture:
    posture: str
    rationale: str


@dataclass(frozen=True)
class PromotionDecisionOperatorRequirement:
    operator_review_required: bool
    operator_receipt_required: bool
    required_decision_statuses: tuple[str, ...]
    execution_requires_separate_packet: bool


@dataclass(frozen=True)
class PromotionDecisionRiskSummary:
    risk_id: str
    risk_posture: str
    rollback_available: bool
    guardrail_breach_present: bool
    uncertainty_policy: str


@dataclass(frozen=True)
class AuthorityRef:
    authority_type: str
    authority_id: str
    label: str


@dataclass(frozen=True)
class PromotionDecisionPacket:
    schema_version: str
    decision_packet_id: str
    proposal_id: str
    proposal_hash: str
    evaluation_id: str
    evaluation_hash: str
    input_refs: tuple[PromotionDecisionInputRef, ...]
    evidence_lineage: PromotionDecisionEvidenceLineage
    decision_posture: PromotionDecisionPosture
    operator_requirement: PromotionDecisionOperatorRequirement
    risk_summary: PromotionDecisionRiskSummary
    packet_status: str
    created_by_lane: str
    authority_ref: AuthorityRef | None
    promotion_execution_allowed: bool
    rollback_execution_allowed: bool
    mutation_allowed: bool
    packet_hash: str


@dataclass(frozen=True)
class PromotionDecisionValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class PromotionDecisionValidationReport:
    status: str
    findings: tuple[PromotionDecisionValidationFinding, ...]
    receipt_hash: str
