from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OperatorReviewSourceRef:
    source_type: str
    source_id: str
    source_hash: str


@dataclass(frozen=True)
class OperatorDecisionReceipt:
    receipt_id: str
    decision_status: str
    operator_id_policy: str
    decision_reason: str
    decision_scope: str
    mutation_authorized: bool
    receipt_hash: str


@dataclass(frozen=True)
class OperatorReviewItem:
    item_id: str
    source_ref: OperatorReviewSourceRef
    review_type: str
    priority: str
    summary: str
    recommended_action: str
    mutation_allowed: bool
    decision_status: str
    decision_receipt: OperatorDecisionReceipt | None


@dataclass(frozen=True)
class OperatorDecisionPolicy:
    policy_id: str
    allow_autonomous_approval: bool
    allow_mutation: bool
    require_receipt_for_final_decision: bool
    routing_policy: str


@dataclass(frozen=True)
class AuthorityRef:
    authority_type: str
    authority_id: str
    label: str


@dataclass(frozen=True)
class OperatorReviewQueue:
    schema_version: str
    queue_id: str
    items: tuple[OperatorReviewItem, ...]
    queue_status: str
    decision_policy: OperatorDecisionPolicy
    created_by_lane: str
    authority_ref: AuthorityRef | None
    mutation_allowed: bool
    queue_hash: str


@dataclass(frozen=True)
class OperatorReviewValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class OperatorReviewValidationReport:
    status: str
    findings: tuple[OperatorReviewValidationFinding, ...]
    receipt_hash: str
