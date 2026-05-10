from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReplayConsensusInputRef:
    source_type: str
    source_id: str
    source_hash: str


@dataclass(frozen=True)
class ReplayConsensusCluster:
    cluster_id: str
    candidate_ids: tuple[str, ...]
    lineage_ids: tuple[str, ...]
    arbitration_ids: tuple[str, ...]
    cluster_posture: str
    cluster_support_count: int
    cluster_conflict_count: int
    lineages_preserved: bool
    normalization_allowed: bool


@dataclass(frozen=True)
class ReplayConsensusFinding:
    finding_id: str
    finding_type: str
    severity: str
    affected_cluster_ids: tuple[str, ...]
    affected_lineage_ids: tuple[str, ...]
    finding_summary: str
    normalization_allowed: bool


@dataclass(frozen=True)
class ReplayConsensusPosture:
    posture_id: str
    consensus_ratio: float
    conflict_ratio: float
    arbitration_count: int
    lineage_count: int
    consensus_state: str
    canonical_selection_allowed: bool
    auto_promotion_allowed: bool


@dataclass(frozen=True)
class ReplayConsensusRecommendation:
    recommendation_id: str
    recommendation_type: str
    description: str
    operator_review_required: bool
    history_rewrite_allowed: bool
    ledger_mutation_allowed: bool
    timeline_collapse_allowed: bool


@dataclass(frozen=True)
class ReplayConsensusReview:
    schema_version: str
    review_id: str
    input_refs: tuple[ReplayConsensusInputRef, ...]
    consensus_clusters: tuple[ReplayConsensusCluster, ...]
    consensus_findings: tuple[ReplayConsensusFinding, ...]
    consensus_posture: ReplayConsensusPosture
    recommendations: tuple[ReplayConsensusRecommendation, ...]
    review_status: str
    review_policy: str
    created_by_lane: str
    authority_ref: dict | None
    history_rewrite_allowed: bool
    ledger_mutation_allowed: bool
    timeline_collapse_allowed: bool
    live_execution_allowed: bool
    routing_change_allowed: bool
    review_hash: str


@dataclass(frozen=True)
class ReplayConsensusValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class ReplayConsensusValidationReport:
    status: str
    findings: tuple[ReplayConsensusValidationFinding, ...]
    receipt_hash: str
