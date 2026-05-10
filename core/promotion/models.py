from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromotionProposalScope:
    scope_type: str
    scope_id: str


@dataclass(frozen=True)
class PromotionEvidenceRef:
    source_type: str
    source_id: str
    source_hash: str
    evidence_note: str


@dataclass(frozen=True)
class PromotionChangeSet:
    change_set_id: str
    change_summary: str
    target_artifacts: tuple[str, ...]
    mutation_class: str
    expected_effect: str
    applies_automatically: bool


@dataclass(frozen=True)
class PromotionCanaryPolicy:
    canary_policy_id: str
    canary_required: bool
    canary_scope: str
    success_criteria: str
    failure_criteria: str
    auto_promote: bool


@dataclass(frozen=True)
class PromotionRollbackPlan:
    rollback_plan_id: str
    rollback_available: bool
    rollback_summary: str
    rollback_artifacts: tuple[str, ...]
    auto_rollback: bool


@dataclass(frozen=True)
class PromotionReviewRequirement:
    review_required: bool
    required_review_type: str
    required_operator_receipt: bool
    operator_receipt_ref: str


@dataclass(frozen=True)
class AuthorityRef:
    authority_type: str
    authority_id: str
    label: str


@dataclass(frozen=True)
class PromotionProposal:
    schema_version: str
    proposal_id: str
    proposal_type: str
    scope: PromotionProposalScope
    evidence_refs: tuple[PromotionEvidenceRef, ...]
    change_set: PromotionChangeSet
    canary_policy: PromotionCanaryPolicy
    rollback_plan: PromotionRollbackPlan
    review_requirement: PromotionReviewRequirement
    proposal_status: str
    created_by_lane: str
    authority_ref: AuthorityRef | None
    mutation_allowed: bool
    execution_allowed: bool
    proposal_hash: str


@dataclass(frozen=True)
class PromotionValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class PromotionValidationReport:
    status: str
    findings: tuple[PromotionValidationFinding, ...]
    receipt_hash: str
