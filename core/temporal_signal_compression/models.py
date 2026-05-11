from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TemporalCompressionInputRef:
    source_type: str
    source_id: str
    source_hash: str


@dataclass(frozen=True)
class TemporalCompressionCluster:
    cluster_id: str
    cluster_type: str
    cluster_posture: str
    signal_count: int
    source_ref_ids: tuple[str, ...]
    lineage_preserved: bool
    replay_normalization_allowed: bool
    canonical_selection_allowed: bool


@dataclass(frozen=True)
class TemporalCompressionMotif:
    motif_id: str
    motif_type: str
    motif_weight: float
    motif_visibility: str
    lineage_preserved: bool
    replay_normalization_allowed: bool


@dataclass(frozen=True)
class TemporalCompressionPressureBand:
    band_id: str
    pressure_level: str
    cluster_count: int
    overloaded: bool
    projection_only: bool


@dataclass(frozen=True)
class TemporalCompressionObservation:
    observation_id: str
    observation_type: str
    observation_posture: str
    projection_only: bool
    action_authorization_allowed: bool


@dataclass(frozen=True)
class TemporalCompressionRecommendation:
    recommendation_id: str
    recommendation_type: str
    execution_allowed: bool
    mutation_allowed: bool
    routing_change_allowed: bool
    replay_normalization_allowed: bool
    canonical_selection_allowed: bool


@dataclass(frozen=True)
class TemporalClimateSignalCompressionLedger:
    schema_version: str
    ledger_id: str
    input_refs: tuple[TemporalCompressionInputRef, ...]
    compression_clusters: tuple[TemporalCompressionCluster, ...]
    compression_motifs: tuple[TemporalCompressionMotif, ...]
    pressure_bands: tuple[TemporalCompressionPressureBand, ...]
    observations: tuple[TemporalCompressionObservation, ...]
    recommendations: tuple[TemporalCompressionRecommendation, ...]
    ledger_status: str
    ledger_posture: str
    compression_policy: str
    created_by_lane: str
    authority_ref: dict | None
    projection_only: bool
    ledger_authoritative: bool
    execution_allowed: bool
    mutation_allowed: bool
    rollback_allowed: bool
    promotion_allowed: bool
    routing_change_allowed: bool
    timeline_collapse_allowed: bool
    canonical_selection_allowed: bool
    replay_normalization_allowed: bool
    adapter_activation_allowed: bool
    auto_transition_allowed: bool
    ledger_hash: str


@dataclass(frozen=True)
class TemporalCompressionValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class TemporalCompressionValidationReport:
    status: str
    findings: tuple[TemporalCompressionValidationFinding, ...]
    receipt_hash: str
