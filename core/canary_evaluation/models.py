from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class CanaryEvaluationInputRef:
    ref_type: str
    ref_id: str
    ref_hash: str


@dataclass(frozen=True)
class CanaryEvaluationMetric:
    metric_id: str
    metric_type: str
    metric_value: float
    threshold_policy: Mapping[str, Any]
    pass_policy: str
    metric_posture: str


@dataclass(frozen=True)
class CanaryEvaluationDecision:
    decision: str
    reason: str


@dataclass(frozen=True)
class CanaryEvaluationRecommendation:
    recommendation_type: str
    summary: str


@dataclass(frozen=True)
class CanaryEvaluationReviewSummary:
    summary_id: str
    operator_review_required: bool
    promotion_proposal_allowed: bool
    rollback_proposal_allowed: bool
    execution_allowed: bool
    summary_text: str


@dataclass(frozen=True)
class AuthorityRef:
    authority_type: str
    authority_id: str
    label: str


@dataclass(frozen=True)
class CanaryEvaluation:
    schema_version: str
    evaluation_id: str
    activation_id: str
    activation_hash: str
    accumulation_id: str
    accumulation_hash: str
    input_refs: tuple[CanaryEvaluationInputRef, ...]
    metrics: tuple[CanaryEvaluationMetric, ...]
    decision: CanaryEvaluationDecision
    recommendations: tuple[CanaryEvaluationRecommendation, ...]
    review_summary: CanaryEvaluationReviewSummary
    evaluation_status: str
    created_by_lane: str
    authority_ref: AuthorityRef | None
    promotion_allowed: bool
    rollback_allowed: bool
    mutation_allowed: bool
    evaluation_hash: str


@dataclass(frozen=True)
class CanaryEvaluationValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class CanaryEvaluationValidationReport:
    status: str
    findings: tuple[CanaryEvaluationValidationFinding, ...]
    receipt_hash: str
