from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class TemporalContractExpectedSurface:
    surface_id: str; surface_name: str; surface_type: str; expected_path: str; required: bool; semantic_mutation_allowed: bool
@dataclass(frozen=True)
class TemporalContractArtifactRef:
    artifact_id: str; surface_id: str; path: str; exists: bool; sha256: str; byte_size: int; line_count: int; artifact_status: str; content_inspected: bool; mutation_allowed: bool
@dataclass(frozen=True)
class TemporalContractPresenceFinding:
    finding_id: str; finding_type: str; severity: str; affected_surface_ids: tuple[str, ...]; finding_summary: str; auto_apply_allowed: bool
@dataclass(frozen=True)
class TemporalContractReconciliationSummary:
    summary_id: str; expected_surface_count: int; present_count: int; missing_count: int; stale_count: int; duplicate_count: int; empty_count: int; not_computable_count: int; clean_tree_observed: bool; no_diff_recorded: bool; summary_posture: str
@dataclass(frozen=True)
class TemporalContractReconciliationRecommendation:
    recommendation_id: str; recommendation_type: str; description: str; execution_allowed: bool; mutation_allowed: bool; routing_change_allowed: bool; contract_semantics_change_allowed: bool; auto_apply_allowed: bool
@dataclass(frozen=True)
class TemporalContractReconciliationManifest:
    schema_version: str; manifest_id: str; expected_surfaces: tuple[TemporalContractExpectedSurface, ...]; artifact_refs: tuple[TemporalContractArtifactRef, ...]; presence_findings: tuple[TemporalContractPresenceFinding, ...]; summary: TemporalContractReconciliationSummary; recommendations: tuple[TemporalContractReconciliationRecommendation, ...]; manifest_status: str; manifest_posture: str; manifest_policy: str; created_by_lane: str; authority_ref: dict | None; audit_only: bool; manifest_authoritative: bool; execution_allowed: bool; mutation_allowed: bool; routing_change_allowed: bool; contract_semantics_change_allowed: bool; timeline_collapse_allowed: bool; canonical_selection_allowed: bool; adapter_activation_allowed: bool; auto_apply_allowed: bool; manifest_hash: str
@dataclass(frozen=True)
class TemporalContractReconciliationValidationFinding:
    code: str; severity: str; message: str
@dataclass(frozen=True)
class TemporalContractReconciliationValidationReport:
    status: str; findings: tuple[TemporalContractReconciliationValidationFinding, ...]; receipt_hash: str
