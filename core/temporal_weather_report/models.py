from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class TemporalWeatherInputRef:
    input_ref_id:str
    input_ref_type:str
    input_ref_path:str
    input_ref_hash:str
@dataclass(frozen=True)
class TemporalWeatherSummary:
    summary_id:str
    dominant_weather:str
    dominant_risk:str
    summary_text:str
    confidence:float
    operator_review_required:bool
    projection_only:bool
@dataclass(frozen=True)
class TemporalWeatherSection:
    section_id:str
    section_type:str
    section_title:str
    section_body:str
    section_posture:str
    source_ref_ids:tuple[str,...]
    projection_only:bool
    inference_authority_allowed:bool
@dataclass(frozen=True)
class TemporalWeatherAlert:
    alert_id:str
    alert_type:str
    severity:str
    alert_summary:str
    source_ref_ids:tuple[str,...]
    operator_review_required:bool
    action_authorization_allowed:bool
@dataclass(frozen=True)
class TemporalWeatherPressureFront:
    front_id:str
    front_type:str
    front_strength:float
    front_direction:str
    affected_refs:tuple[str,...]
    lineage_preserved:bool
    replay_normalization_allowed:bool
    routing_change_allowed:bool
@dataclass(frozen=True)
class TemporalWeatherReviewPrompt:
    prompt_id:str
    prompt_type:str
    prompt_text:str
    operator_review_required:bool
    action_authorization_allowed:bool
    execution_allowed:bool
    mutation_allowed:bool
    routing_change_allowed:bool
@dataclass(frozen=True)
class TemporalGovernanceWeatherReportPacket:
    schema_version:str
    report_id:str
    input_refs:tuple[TemporalWeatherInputRef,...]
    weather_summary:TemporalWeatherSummary
    sections:tuple[TemporalWeatherSection,...]
    alerts:tuple[TemporalWeatherAlert,...]
    pressure_fronts:tuple[TemporalWeatherPressureFront,...]
    review_prompts:tuple[TemporalWeatherReviewPrompt,...]
    report_status:str
    report_posture:str
    report_policy:str
    created_by_lane:str
    authority_ref:dict|None
    projection_only:bool
    report_authoritative:bool
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
    report_hash:str
@dataclass(frozen=True)
class TemporalWeatherValidationFinding:
    code:str
    severity:str
    message:str
@dataclass(frozen=True)
class TemporalWeatherValidationReport:
    status:str
    findings:tuple[TemporalWeatherValidationFinding,...]
    receipt_hash:str
