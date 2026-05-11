from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TemporalDigestInputRef:
    source_type: str
    source_id: str
    source_hash: str


@dataclass(frozen=True)
class TemporalDigestSection:
    section_id: str
    section_type: str
    section_title: str
    section_body: str
    section_posture: str
    source_ref_ids: tuple[str, ...]
    projection_only: bool
    inference_authority_allowed: bool


@dataclass(frozen=True)
class TemporalDigestSignalCard:
    card_id: str
    card_type: str
    card_label: str
    card_summary: str
    card_weight: float
    card_posture: str
    source_ref_ids: tuple[str, ...]
    lineage_preserved: bool
    replay_normalization_allowed: bool
    canonical_selection_allowed: bool


@dataclass(frozen=True)
class TemporalDigestProvenanceRef:
    provenance_id: str
    source_ref_id: str
    source_type: str
    source_hash: str
    compression_trace_id: str
    included_in_digest: bool
    provenance_required: bool


@dataclass(frozen=True)
class TemporalDigestWarning:
    warning_id: str
    warning_type: str
    warning_posture: str
    warning_summary: str


@dataclass(frozen=True)
class TemporalDigestRecommendation:
    recommendation_id: str
    recommendation_type: str
    execution_allowed: bool
    mutation_allowed: bool
    routing_change_allowed: bool
    replay_normalization_allowed: bool
    canonical_selection_allowed: bool


@dataclass(frozen=True)
class TemporalClimateCompressionDigestProjection:
    schema_version: str
    digest_id: str
    input_refs: tuple[TemporalDigestInputRef, ...]
    sections: tuple[TemporalDigestSection, ...]
    signal_cards: tuple[TemporalDigestSignalCard, ...]
    provenance_refs: tuple[TemporalDigestProvenanceRef, ...]
    warnings: tuple[TemporalDigestWarning, ...]
    recommendations: tuple[TemporalDigestRecommendation, ...]
    digest_status: str
    digest_posture: str
    digest_policy: str
    created_by_lane: str
    authority_ref: dict | None
    projection_only: bool
    digest_authoritative: bool
    inference_authority_allowed: bool
    action_authorization_allowed: bool
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
    digest_hash: str


@dataclass(frozen=True)
class TemporalDigestValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class TemporalDigestValidationReport:
    status: str
    findings: tuple[TemporalDigestValidationFinding, ...]
    receipt_hash: str
