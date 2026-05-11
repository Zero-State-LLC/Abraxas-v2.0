from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class TemporalReleaseInputRef:
    input_ref_id:str; input_ref_type:str; input_ref_path:str; input_ref_hash:str
@dataclass(frozen=True)
class TemporalReleaseArtifactRef:
    artifact_id:str; artifact_type:str; path:str; sha256:str; exists:bool; required:bool; artifact_posture:str; mutation_allowed:bool
@dataclass(frozen=True)
class TemporalReleaseCommitRef:
    commit_id:str; commit_hash:str; commit_message:str; included_in_release:bool; promotion_allowed:bool; rollback_allowed:bool
@dataclass(frozen=True)
class TemporalReleaseTestRef:
    test_id:str; test_command:str; test_status:str; test_summary:str; required:bool
@dataclass(frozen=True)
class TemporalReleaseSchemaRef:
    schema_id:str; schema_path:str; schema_version:str; schema_hash:str; schema_status:str; canonical_selection_allowed:bool
@dataclass(frozen=True)
class TemporalReleaseSummary:
    summary_id:str; input_count:int; artifact_count:int; commit_count:int; test_count:int; schema_count:int; pass_count:int; warn_count:int; blocked_count:int; not_computable_count:int; release_ready:bool; operator_review_required:bool; summary_posture:str
@dataclass(frozen=True)
class TemporalReleaseConstraintBadge:
    badge_id:str; badge_type:str; badge_label:str; required:bool; badge_posture:str
@dataclass(frozen=True)
class TemporalReleaseRecommendation:
    recommendation_id:str; recommendation_type:str; description:str; operator_review_required:bool; action_authorization_allowed:bool; execution_allowed:bool; mutation_allowed:bool; rollback_allowed:bool; promotion_allowed:bool; routing_change_allowed:bool; timeline_collapse_allowed:bool; canonical_selection_allowed:bool; replay_normalization_allowed:bool
@dataclass(frozen=True)
class TemporalGovernanceReleaseBundle:
    schema_version:str; bundle_id:str; input_refs:tuple[TemporalReleaseInputRef,...]; artifact_refs:tuple[TemporalReleaseArtifactRef,...]; commit_refs:tuple[TemporalReleaseCommitRef,...]; test_refs:tuple[TemporalReleaseTestRef,...]; schema_refs:tuple[TemporalReleaseSchemaRef,...]; release_summary:TemporalReleaseSummary; constraint_badges:tuple[TemporalReleaseConstraintBadge,...]; recommendations:tuple[TemporalReleaseRecommendation,...]; bundle_status:str; bundle_posture:str; bundle_policy:str; created_by_lane:str; authority_ref:dict|None; audit_only:bool; projection_only:bool; bundle_authoritative:bool; inference_authority_allowed:bool; action_authorization_allowed:bool; execution_allowed:bool; mutation_allowed:bool; rollback_allowed:bool; promotion_allowed:bool; routing_change_allowed:bool; timeline_collapse_allowed:bool; canonical_selection_allowed:bool; replay_normalization_allowed:bool; adapter_activation_allowed:bool; auto_transition_allowed:bool; global_runtime_activation_allowed:bool; bundle_hash:str
@dataclass(frozen=True)
class TemporalReleaseValidationFinding:
    code:str; severity:str; message:str
@dataclass(frozen=True)
class TemporalReleaseValidationReport:
    status:str; findings:tuple[TemporalReleaseValidationFinding,...]; receipt_hash:str
