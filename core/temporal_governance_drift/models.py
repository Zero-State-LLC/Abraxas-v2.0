from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class TemporalDriftInputRef:
    input_ref_id:str
    input_ref_type:str
    input_ref_path:str
    input_ref_hash:str
@dataclass(frozen=True)
class TemporalDriftZone:
    zone_id:str
    zone_type:str
    zone_label:str
    zone_posture:str
    affected_refs:tuple[str,...]
    lineage_preserved:bool
    replay_normalization_allowed:bool
    canonical_selection_allowed:bool
@dataclass(frozen=True)
class TemporalDriftVector:
    vector_id:str
    vector_type:str
    vector_strength:float
    vector_direction:str
    source_ref_ids:tuple[str,...]
    routing_change_allowed:bool
@dataclass(frozen=True)
class TemporalDriftPressureBand:
    band_id:str
    pressure_type:str
    pressure_score:float
    pressure_summary:str
    blocked_visibility_preserved:bool
    nondeterminism_visibility_preserved:bool
@dataclass(frozen=True)
class TemporalDriftFinding:
    finding_id:str
    finding_type:str
    severity:str
    affected_refs:tuple[str,...]
    finding_summary:str
    execution_allowed:bool
@dataclass(frozen=True)
class TemporalDriftRecommendation:
    recommendation_id:str
    recommendation_type:str
    description:str
    execution_allowed:bool
    mutation_allowed:bool
    rollback_allowed:bool
    promotion_allowed:bool
    routing_change_allowed:bool
    timeline_collapse_allowed:bool
    canonical_selection_allowed:bool
    replay_normalization_allowed:bool
@dataclass(frozen=True)
class TemporalGovernanceDriftObservatory:
    schema_version:str
    observatory_id:str
    input_refs:tuple[TemporalDriftInputRef,...]
    drift_zones:tuple[TemporalDriftZone,...]
    drift_vectors:tuple[TemporalDriftVector,...]
    pressure_bands:tuple[TemporalDriftPressureBand,...]
    findings:tuple[TemporalDriftFinding,...]
    recommendations:tuple[TemporalDriftRecommendation,...]
    observatory_status:str
    observatory_posture:str
    observatory_policy:str
    created_by_lane:str
    authority_ref:dict|None
    projection_only:bool
    observatory_authoritative:bool
    inference_authority_allowed:bool
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
    observatory_hash:str
@dataclass(frozen=True)
class TemporalDriftValidationFinding:
    code:str
    severity:str
    message:str
@dataclass(frozen=True)
class TemporalDriftValidationReport:
    status:str
    findings:tuple[TemporalDriftValidationFinding,...]
    receipt_hash:str
