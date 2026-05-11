from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TemporalOperatorReviewInputRef:
    source_type: str
    source_id: str
    source_hash: str


@dataclass(frozen=True)
class TemporalOperatorReviewQueueItem:
    item_id: str
    item_type: str
    item_title: str
    item_summary: str
    item_posture: str
    display_priority: int
    source_ref_ids: tuple[str, ...]
    projection_only: bool
    action_authorization_allowed: bool


@dataclass(frozen=True)
class TemporalOperatorReviewPriorityBand:
    band_id: str
    band_type: str
    item_count: int
    operator_review_required: bool
    projection_only: bool


@dataclass(frozen=True)
class TemporalOperatorReviewRiskSurface:
    surface_id: str
    surface_type: str
    severity: str
    source_ref_ids: tuple[str, ...]
    projection_only: bool
    action_authorization_allowed: bool


@dataclass(frozen=True)
class TemporalOperatorReviewRecommendation:
    recommendation_id: str
    recommendation_type: str
    operator_review_required: bool
    action_authorization_allowed: bool
    execution_allowed: bool
    routing_change_allowed: bool


@dataclass(frozen=True)
class TemporalClimateOperatorReviewProjectionQueue:
    schema_version: str
    queue_id: str
    input_refs: tuple[TemporalOperatorReviewInputRef, ...]
    queue_items: tuple[TemporalOperatorReviewQueueItem, ...]
    priority_bands: tuple[TemporalOperatorReviewPriorityBand, ...]
    risk_surfaces: tuple[TemporalOperatorReviewRiskSurface, ...]
    recommendations: tuple[TemporalOperatorReviewRecommendation, ...]
    queue_status: str
    queue_posture: str
    queue_policy: str
    created_by_lane: str
    authority_ref: dict | None
    projection_only: bool
    queue_authoritative: bool
    action_authorization_allowed: bool
    execution_allowed: bool
    mutation_allowed: bool
    rollback_allowed: bool
    promotion_allowed: bool
    timeline_collapse_allowed: bool
    canonical_selection_allowed: bool
    routing_change_allowed: bool
    auto_transition_allowed: bool
    queue_hash: str


@dataclass(frozen=True)
class TemporalOperatorReviewValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class TemporalOperatorReviewValidationReport:
    status: str
    findings: tuple[TemporalOperatorReviewValidationFinding, ...]
    receipt_hash: str
