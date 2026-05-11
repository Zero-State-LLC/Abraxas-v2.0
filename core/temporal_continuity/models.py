from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TemporalContinuityInputRef:
    source_type: str
    source_id: str
    source_hash: str


@dataclass(frozen=True)
class TemporalContinuityComponentScore:
    component_id: str
    component_type: str
    raw_value: float
    normalized_score: float
    weight: float
    component_posture: str
    mutation_allowed: bool


@dataclass(frozen=True)
class TemporalContinuityMetric:
    metric_id: str
    metric_type: str
    metric_value: float
    metric_policy: str
    metric_posture: str


@dataclass(frozen=True)
class TemporalContinuityFinding:
    finding_id: str
    finding_type: str
    severity: str
    affected_ref_ids: tuple[str, ...]
    finding_summary: str
    normalization_allowed: bool


@dataclass(frozen=True)
class TemporalContinuityRecommendation:
    recommendation_id: str
    recommendation_type: str
    description: str
    operator_review_required: bool
    history_rewrite_allowed: bool
    ledger_mutation_allowed: bool
    timeline_collapse_allowed: bool
    canonical_selection_allowed: bool


@dataclass(frozen=True)
class TemporalContinuityIndex:
    schema_version: str
    index_id: str
    input_refs: tuple[TemporalContinuityInputRef, ...]
    component_scores: tuple[TemporalContinuityComponentScore, ...]
    metrics: tuple[TemporalContinuityMetric, ...]
    findings: tuple[TemporalContinuityFinding, ...]
    recommendations: tuple[TemporalContinuityRecommendation, ...]
    continuity_score: float
    continuity_posture: str
    index_status: str
    index_policy: str
    created_by_lane: str
    authority_ref: dict | None
    history_rewrite_allowed: bool
    ledger_mutation_allowed: bool
    timeline_collapse_allowed: bool
    canonical_selection_allowed: bool
    live_execution_allowed: bool
    routing_change_allowed: bool
    index_hash: str


@dataclass(frozen=True)
class TemporalContinuityValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class TemporalContinuityValidationReport:
    status: str
    findings: tuple[TemporalContinuityValidationFinding, ...]
    receipt_hash: str
