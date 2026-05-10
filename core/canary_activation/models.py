from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class CanaryScope:
    scope_type: str
    scope_id: str


@dataclass(frozen=True)
class CanaryDurationPolicy:
    duration_policy_id: str
    start_policy: str
    end_policy: str
    max_observation_windows: int
    expiry_policy: str


@dataclass(frozen=True)
class CanaryGuardrail:
    guardrail_id: str
    guardrail_type: str
    threshold_policy: Mapping[str, Any]
    breach_action: str
    operator_review_required: bool


@dataclass(frozen=True)
class CanaryEvidenceRequirement:
    require_brier_entries: bool
    require_calibration_ledger: bool
    require_reliability_advisory: bool
    require_runtime_audit: bool
    minimum_evidence_count: int
    satisfied_evidence_count: int


@dataclass(frozen=True)
class CanaryRollbackLink:
    rollback_plan_id: str
    rollback_available: bool
    rollback_artifacts: tuple[str, ...]
    rollback_policy: str


@dataclass(frozen=True)
class CanaryOperatorApprovalRef:
    operator_receipt_ref: str
    review_queue_ref: str
    approval_policy: str


@dataclass(frozen=True)
class AuthorityRef:
    authority_type: str
    authority_id: str
    label: str


@dataclass(frozen=True)
class CanaryActivation:
    schema_version: str
    activation_id: str
    proposal_id: str
    proposal_hash: str
    scope: CanaryScope
    duration_policy: CanaryDurationPolicy
    guardrails: tuple[CanaryGuardrail, ...]
    evidence_requirements: CanaryEvidenceRequirement
    rollback_link: CanaryRollbackLink
    operator_approval_ref: CanaryOperatorApprovalRef
    activation_status: str
    created_by_lane: str
    authority_ref: AuthorityRef | None
    global_activation_allowed: bool
    mutation_limited_to_scope: bool
    auto_promote: bool
    auto_rollback: bool
    activation_hash: str


@dataclass(frozen=True)
class CanaryValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class CanaryValidationReport:
    status: str
    findings: tuple[CanaryValidationFinding, ...]
    receipt_hash: str
