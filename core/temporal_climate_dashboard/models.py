from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TemporalClimateInputRef:
    source_type: str
    source_id: str
    source_hash: str


@dataclass(frozen=True)
class TemporalClimateSummary:
    summary_id: str
    regime_state: str
    pressure_state: str
    topology_state: str
    continuity_state: str
    dominant_risk: str
    summary_confidence: float
    operator_review_required: bool
    projection_only: bool


@dataclass(frozen=True)
class TemporalClimateStatusTile:
    tile_id: str
    tile_type: str
    tile_label: str
    tile_value: str
    tile_posture: str
    source_ref_ids: tuple[str, ...]
    projection_only: bool


@dataclass(frozen=True)
class TemporalClimateAlert:
    alert_id: str
    alert_type: str
    severity: str
    alert_summary: str
    affected_ref_ids: tuple[str, ...]
    operator_review_required: bool
    action_authorization_allowed: bool


@dataclass(frozen=True)
class TemporalClimateTrendIndicator:
    trend_id: str
    trend_type: str
    trend_direction: str
    trend_strength: float
    trend_confidence: float
    source_ref_ids: tuple[str, ...]
    projection_only: bool


@dataclass(frozen=True)
class TemporalClimateOperatorAction:
    action_id: str
    action_type: str
    description: str
    operator_review_required: bool
    action_authorization_allowed: bool
    history_rewrite_allowed: bool
    ledger_mutation_allowed: bool
    timeline_collapse_allowed: bool
    canonical_selection_allowed: bool
    routing_change_allowed: bool
    live_execution_allowed: bool


@dataclass(frozen=True)
class TemporalClimateDashboardPacket:
    schema_version: str
    packet_id: str
    input_refs: tuple[TemporalClimateInputRef, ...]
    climate_summary: TemporalClimateSummary
    status_tiles: tuple[TemporalClimateStatusTile, ...]
    alerts: tuple[TemporalClimateAlert, ...]
    trend_indicators: tuple[TemporalClimateTrendIndicator, ...]
    operator_actions: tuple[TemporalClimateOperatorAction, ...]
    packet_status: str
    packet_posture: str
    packet_policy: str
    created_by_lane: str
    authority_ref: dict | None
    projection_only: bool
    packet_authoritative: bool
    action_authorization_allowed: bool
    auto_transition_allowed: bool
    history_rewrite_allowed: bool
    ledger_mutation_allowed: bool
    timeline_collapse_allowed: bool
    canonical_selection_allowed: bool
    live_execution_allowed: bool
    routing_change_allowed: bool
    packet_hash: str


@dataclass(frozen=True)
class TemporalClimateValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class TemporalClimateValidationReport:
    status: str
    findings: tuple[TemporalClimateValidationFinding, ...]
    receipt_hash: str
