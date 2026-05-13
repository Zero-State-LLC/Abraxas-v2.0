from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class TemporalReleaseIndexInputRef:
    input_ref_id:str; input_ref_type:str; input_ref_path:str; input_ref_hash:str

@dataclass(frozen=True)
class TemporalReleaseIndexEntry:
    entry_id:str; release_bundle_id:str; release_version:str; release_hash:str; release_status:str; release_posture:str; commit_hashes:tuple[str,...]; artifact_hashes:tuple[str,...]; test_statuses:tuple[str,...]; schema_hashes:tuple[str,...]; operator_review_required:bool; included_in_index:bool; activation_allowed:bool; promotion_allowed:bool; rollback_allowed:bool

@dataclass(frozen=True)
class TemporalReleaseLineageRef:
    lineage_id:str; from_release_bundle_id:str; to_release_bundle_id:str; lineage_type:str; lineage_hash:str; lineage_preserved:bool; canonical_selection_allowed:bool; timeline_collapse_allowed:bool

@dataclass(frozen=True)
class TemporalReleaseIndexSummary:
    summary_id:str; release_count:int; pass_count:int; warn_count:int; blocked_count:int; no_diff_count:int; not_computable_count:int; operator_review_required_count:int; latest_release_bundle_id:str; latest_release_hash:str; summary_posture:str

@dataclass(frozen=True)
class TemporalReleaseIndexFinding:
    finding_id:str; finding_type:str; severity:str; affected_release_bundle_ids:tuple[str,...]; finding_summary:str; execution_allowed:bool

@dataclass(frozen=True)
class TemporalReleaseIndexRecommendation:
    recommendation_id:str; recommendation_type:str; description:str; operator_review_required:bool; action_authorization_allowed:bool; execution_allowed:bool; mutation_allowed:bool; rollback_allowed:bool; promotion_allowed:bool; routing_change_allowed:bool; timeline_collapse_allowed:bool; canonical_selection_allowed:bool; replay_normalization_allowed:bool

@dataclass(frozen=True)
class TemporalGovernanceReleaseIndexRegistry:
    schema_version:str; registry_id:str; input_refs:tuple[TemporalReleaseIndexInputRef,...]; release_entries:tuple[TemporalReleaseIndexEntry,...]; lineage_refs:tuple[TemporalReleaseLineageRef,...]; summary:TemporalReleaseIndexSummary; findings:tuple[TemporalReleaseIndexFinding,...]; recommendations:tuple[TemporalReleaseIndexRecommendation,...]; registry_status:str; registry_posture:str; registry_policy:str; created_by_lane:str; authority_ref:dict|None; audit_only:bool; projection_only:bool; registry_authoritative:bool; release_activation_allowed:bool; execution_allowed:bool; mutation_allowed:bool; rollback_allowed:bool; promotion_allowed:bool; routing_change_allowed:bool; timeline_collapse_allowed:bool; canonical_selection_allowed:bool; replay_normalization_allowed:bool; adapter_activation_allowed:bool; auto_transition_allowed:bool; global_runtime_activation_allowed:bool; registry_hash:str

@dataclass(frozen=True)
class TemporalReleaseIndexValidationFinding:
    code:str; severity:str; message:str

@dataclass(frozen=True)
class TemporalReleaseIndexValidationReport:
    status:str; findings:tuple[TemporalReleaseIndexValidationFinding,...]; receipt_hash:str
