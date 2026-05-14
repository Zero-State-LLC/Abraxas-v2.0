from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class TemporalOperatorBriefInputRef:
    input_ref_id:str
    input_ref_type:str
    input_ref_path:str
    input_ref_hash:str
@dataclass(frozen=True)
class TemporalOperatorBriefHeader:
    header_id:str
    title:str
    dominant_status:str
    dominant_risk:str
    summary_text:str
    operator_review_required:bool
    projection_only:bool
@dataclass(frozen=True)
class TemporalOperatorBriefSection:
    section_id:str
    section_type:str
    section_title:str
    section_body:str
    section_posture:str
    source_ref_ids:tuple[str,...]
    projection_only:bool
    inference_authority_allowed:bool
@dataclass(frozen=True)
class TemporalOperatorBriefActionCard:
    card_id:str
    card_type:str
    card_title:str
    card_body:str
    card_posture:str
    operator_review_required:bool
    action_authorization_allowed:bool
    execution_allowed:bool
    mutation_allowed:bool
    routing_change_allowed:bool
@dataclass(frozen=True)
class TemporalOperatorBriefProvenanceRef:
    provenance_id:str
    source_ref_id:str
    source_type:str
    source_hash:str
    included_in_brief:bool
    provenance_required:bool
    canonical_selection_allowed:bool
@dataclass(frozen=True)
class TemporalOperatorBriefConstraintBadge:
    badge_id:str
    badge_type:str
    badge_label:str
    required:bool
    badge_posture:str
@dataclass(frozen=True)
class TemporalGovernanceOperatorBriefBundle:
    schema_version:str
    brief_id:str
    input_refs:tuple[TemporalOperatorBriefInputRef,...]
    brief_header:TemporalOperatorBriefHeader
    sections:tuple[TemporalOperatorBriefSection,...]
    action_cards:tuple[TemporalOperatorBriefActionCard,...]
    provenance_refs:tuple[TemporalOperatorBriefProvenanceRef,...]
    constraint_badges:tuple[TemporalOperatorBriefConstraintBadge,...]
    brief_status:str
    brief_posture:str
    brief_policy:str
    created_by_lane:str
    authority_ref:dict|None
    projection_only:bool
    brief_authoritative:bool
    inference_authority_allowed:bool
    action_authorization_allowed:bool
    execution_allowed:bool
    mutation_allowed:bool
    rollback_allowed:bool
    promotion_allowed:bool
    routing_change_allowed:bool
    timeline_collapse_allowed:bool
    canonical_selection_allowed:bool
    replay_normalization_allowed:bool
    adapter_activation_allowed:bool
    auto_transition_allowed:bool
    brief_hash:str
@dataclass(frozen=True)
class TemporalOperatorBriefValidationFinding:
    code:str
    severity:str
    message:str
@dataclass(frozen=True)
class TemporalOperatorBriefValidationReport:
    status:str
    findings:tuple[TemporalOperatorBriefValidationFinding,...]
    receipt_hash:str
