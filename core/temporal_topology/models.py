from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TemporalTopologyInputRef:
    source_type: str
    source_id: str
    source_hash: str


@dataclass(frozen=True)
class TemporalTopologyNode:
    node_id: str
    node_type: str
    ref_id: str
    continuity_posture: str
    pressure_score: float
    blocked_pressure: float
    nondeterminism_pressure: float
    fracture_pressure: float
    node_posture: str
    mutation_allowed: bool


@dataclass(frozen=True)
class TemporalTopologyEdge:
    edge_id: str
    source_node_id: str
    target_node_id: str
    edge_type: str
    coupling_strength: float
    pressure_transfer_score: float
    edge_posture: str
    routing_change_allowed: bool


@dataclass(frozen=True)
class TemporalPressureHotspot:
    hotspot_id: str
    node_ids: tuple[str, ...]
    hotspot_type: str
    pressure_score: float
    severity: str
    operator_review_required: bool


@dataclass(frozen=True)
class TemporalFractureZone:
    fracture_zone_id: str
    node_ids: tuple[str, ...]
    edge_ids: tuple[str, ...]
    fracture_type: str
    fracture_score: float
    lineages_preserved: bool
    normalization_allowed: bool


@dataclass(frozen=True)
class TemporalTopologyMetric:
    metric_id: str
    metric_type: str
    metric_value: float
    metric_policy: str
    metric_posture: str


@dataclass(frozen=True)
class TemporalTopologyRecommendation:
    recommendation_id: str
    recommendation_type: str
    description: str
    operator_review_required: bool
    history_rewrite_allowed: bool
    ledger_mutation_allowed: bool
    timeline_collapse_allowed: bool
    canonical_selection_allowed: bool
    routing_change_allowed: bool


@dataclass(frozen=True)
class TemporalGovernanceTopologyIndex:
    schema_version: str
    topology_id: str
    input_refs: tuple[TemporalTopologyInputRef, ...]
    nodes: tuple[TemporalTopologyNode, ...]
    edges: tuple[TemporalTopologyEdge, ...]
    pressure_hotspots: tuple[TemporalPressureHotspot, ...]
    fracture_zones: tuple[TemporalFractureZone, ...]
    metrics: tuple[TemporalTopologyMetric, ...]
    recommendations: tuple[TemporalTopologyRecommendation, ...]
    topology_status: str
    topology_posture: str
    topology_policy: str
    created_by_lane: str
    authority_ref: dict | None
    history_rewrite_allowed: bool
    ledger_mutation_allowed: bool
    timeline_collapse_allowed: bool
    canonical_selection_allowed: bool
    live_execution_allowed: bool
    routing_change_allowed: bool
    topology_hash: str


@dataclass(frozen=True)
class TemporalTopologyValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class TemporalTopologyValidationReport:
    status: str
    findings: tuple[TemporalTopologyValidationFinding, ...]
    receipt_hash: str
