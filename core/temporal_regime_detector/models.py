from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TemporalRegimeInputRef:
    source_type: str
    source_id: str
    source_hash: str


@dataclass(frozen=True)
class TemporalRegimeState:
    state_id: str
    state_type: str
    state_score: float
    confidence: float
    evidence_ref_ids: tuple[str, ...]
    state_posture: str
    authoritative: bool


@dataclass(frozen=True)
class TemporalRegimeTransitionEvent:
    transition_id: str
    from_state: str
    to_state: str
    transition_probability: float
    transition_confidence: float
    trigger_ids: tuple[str, ...]
    affected_node_ids: tuple[str, ...]
    affected_fracture_zone_ids: tuple[str, ...]
    event_posture: str
    auto_transition_allowed: bool


@dataclass(frozen=True)
class TemporalRegimeTrigger:
    trigger_id: str
    trigger_type: str
    trigger_value: float
    threshold_policy: str
    trigger_posture: str
    normalization_allowed: bool


@dataclass(frozen=True)
class TemporalRegimeInstabilityMetric:
    metric_id: str
    metric_type: str
    metric_value: float
    metric_policy: str
    metric_posture: str


@dataclass(frozen=True)
class TemporalRegimeRecommendation:
    recommendation_id: str
    recommendation_type: str
    description: str
    operator_review_required: bool
    detector_authoritative: bool
    auto_transition_allowed: bool
    history_rewrite_allowed: bool
    ledger_mutation_allowed: bool
    timeline_collapse_allowed: bool
    canonical_selection_allowed: bool
    routing_change_allowed: bool


@dataclass(frozen=True)
class TemporalRegimeTransitionDetector:
    schema_version: str
    detector_id: str
    input_refs: tuple[TemporalRegimeInputRef, ...]
    current_regime_state: TemporalRegimeState
    candidate_regime_states: tuple[TemporalRegimeState, ...]
    transition_events: tuple[TemporalRegimeTransitionEvent, ...]
    triggers: tuple[TemporalRegimeTrigger, ...]
    instability_metrics: tuple[TemporalRegimeInstabilityMetric, ...]
    recommendations: tuple[TemporalRegimeRecommendation, ...]
    detector_status: str
    detector_posture: str
    detector_policy: str
    created_by_lane: str
    authority_ref: dict | None
    detector_authoritative: bool
    auto_transition_allowed: bool
    history_rewrite_allowed: bool
    ledger_mutation_allowed: bool
    timeline_collapse_allowed: bool
    canonical_selection_allowed: bool
    live_execution_allowed: bool
    routing_change_allowed: bool
    detector_hash: str


@dataclass(frozen=True)
class TemporalRegimeValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class TemporalRegimeValidationReport:
    status: str
    findings: tuple[TemporalRegimeValidationFinding, ...]
    receipt_hash: str
