from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TemporalPressureForecastInputRef:
    source_type: str
    source_id: str
    source_hash: str


@dataclass(frozen=True)
class TemporalPressureVector:
    vector_id: str
    source_node_id: str
    target_node_id: str
    vector_type: str
    magnitude: float
    confidence: float
    direction_policy: str
    forecast_horizon_policy: str
    vector_posture: str
    routing_change_allowed: bool


@dataclass(frozen=True)
class TemporalPressureWave:
    wave_id: str
    node_ids: tuple[str, ...]
    edge_ids: tuple[str, ...]
    wave_type: str
    wave_magnitude: float
    wave_confidence: float
    convergence_risk: float
    wave_posture: str
    mutation_allowed: bool


@dataclass(frozen=True)
class TemporalRegimeTransitionSignal:
    signal_id: str
    signal_type: str
    trigger_policy: str
    transition_probability: float
    confidence: float
    affected_node_ids: tuple[str, ...]
    affected_fracture_zone_ids: tuple[str, ...]
    signal_posture: str
    auto_transition_allowed: bool


@dataclass(frozen=True)
class TemporalPressureForecastMetric:
    metric_id: str
    metric_type: str
    metric_value: float
    metric_policy: str
    metric_posture: str


@dataclass(frozen=True)
class TemporalPressureForecastRecommendation:
    recommendation_id: str
    recommendation_type: str
    description: str
    operator_review_required: bool
    forecast_authoritative: bool
    history_rewrite_allowed: bool
    ledger_mutation_allowed: bool
    timeline_collapse_allowed: bool
    canonical_selection_allowed: bool
    routing_change_allowed: bool


@dataclass(frozen=True)
class TemporalPressureForecastSurface:
    schema_version: str
    surface_id: str
    input_refs: tuple[TemporalPressureForecastInputRef, ...]
    pressure_vectors: tuple[TemporalPressureVector, ...]
    pressure_waves: tuple[TemporalPressureWave, ...]
    regime_transition_signals: tuple[TemporalRegimeTransitionSignal, ...]
    metrics: tuple[TemporalPressureForecastMetric, ...]
    recommendations: tuple[TemporalPressureForecastRecommendation, ...]
    forecast_status: str
    forecast_posture: str
    forecast_policy: str
    created_by_lane: str
    authority_ref: dict | None
    forecast_authoritative: bool
    history_rewrite_allowed: bool
    ledger_mutation_allowed: bool
    timeline_collapse_allowed: bool
    canonical_selection_allowed: bool
    live_execution_allowed: bool
    routing_change_allowed: bool
    surface_hash: str


@dataclass(frozen=True)
class TemporalPressureForecastValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class TemporalPressureForecastValidationReport:
    status: str
    findings: tuple[TemporalPressureForecastValidationFinding, ...]
    receipt_hash: str
