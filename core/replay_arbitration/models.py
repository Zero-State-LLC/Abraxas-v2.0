from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReplayArbitrationInputRef:
    source_type: str
    source_id: str
    source_hash: str


@dataclass(frozen=True)
class ReplayLineageCandidate:
    candidate_id: str
    lineage_id: str
    ledger_ref_id: str
    diff_ref_ids: tuple[str, ...]
    replay_ref_ids: tuple[str, ...]
    stability_posture: str
    divergence_count: int
    blocked_count: int
    nondeterminism_count: int
    lineage_preserved: bool


@dataclass(frozen=True)
class ReplayArbitrationFinding:
    finding_id: str
    finding_type: str
    severity: str
    affected_candidate_ids: tuple[str, ...]
    finding_summary: str
    normalization_allowed: bool


@dataclass(frozen=True)
class ReplayTemporalAuthorityScore:
    score_id: str
    candidate_id: str
    stability_component: float
    lineage_completeness_component: float
    rollback_integrity_component: float
    authority_lineage_component: float
    nondeterminism_penalty: float
    blocked_history_penalty: float
    authority_score: float
    authority_posture: str
    auto_select_allowed: bool


@dataclass(frozen=True)
class ReplayArbitrationRecommendation:
    recommendation_id: str
    recommendation_type: str
    description: str
    operator_review_required: bool
    history_rewrite_allowed: bool
    ledger_mutation_allowed: bool


@dataclass(frozen=True)
class ReplayTemporalArbitration:
    schema_version: str
    arbitration_id: str
    input_refs: tuple[ReplayArbitrationInputRef, ...]
    lineage_candidates: tuple[ReplayLineageCandidate, ...]
    arbitration_findings: tuple[ReplayArbitrationFinding, ...]
    authority_scores: tuple[ReplayTemporalAuthorityScore, ...]
    recommendations: tuple[ReplayArbitrationRecommendation, ...]
    arbitration_status: str
    arbitration_policy: str
    created_by_lane: str
    authority_ref: dict | None
    history_rewrite_allowed: bool
    ledger_mutation_allowed: bool
    live_execution_allowed: bool
    routing_change_allowed: bool
    arbitration_hash: str


@dataclass(frozen=True)
class ReplayArbitrationValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class ReplayArbitrationValidationReport:
    status: str
    findings: tuple[ReplayArbitrationValidationFinding, ...]
    receipt_hash: str
