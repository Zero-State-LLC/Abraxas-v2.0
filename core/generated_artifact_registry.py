from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Literal, cast

from pydantic import BaseModel, Field

from core.canonical.json import canonical_dumps, write_canonical_json
from core.config import RuntimePaths

GENERATED_ARTIFACT_POLICY_V1: dict[str, Any] = {
    "policy_id": "GENERATED_ARTIFACT_POLICY_V1",
    "canonical_truth": [
        "generators",
        "schemas",
        "deterministic_inputs",
    ],
    "rules": [
        "generated artifacts are derived surfaces",
        "ci regenerates required artifacts before tests",
        "prohibit unrelated artifact churn",
        "prohibit mixed feature+artifact PRs",
        "prohibit giant regeneration-only PRs",
        "fail closed on missing generators or schemas",
        "never fabricate artifacts",
    ],
    "advisory_only": True,
    "mutation_allowed": False,
    "authority_granted": False,
    "auto_execute": False,
    "auto_approve": False,
}

_SCOPE_PREFIXES = (
    "out/contracts/",
    "out/sync/",
    "out/projections/",
    "out/audit/",
    "out/validation/",
    "out/canon_resume_state/",
    "out/reports/",
    "out/exports/",
    "out/previews/",
    "out/ingest/",
    "out/operator_review/",
    "out/archive/",
    "out/package/",
    "out/oracle/",
    "out/yggdrasil/",
    "out/temporal_continuity_spine_precheck/",
    "out/temporal_continuity_spine_binder_contract/",
    "out/temporal_continuity_binder_readiness_audit/",
    "out/temporal_continuity_evidence_index/",
    "out/temporal_continuity_missing_evidence_restoration_plan/",
     "out/temporal_continuity_generator_discovery_plan/",
     "out/temporal_continuity_upstream_input_restoration_plan/",
     "out/temporal_continuity_upstream_input_regeneration_dry_run_plan/",
     "out/temporal_continuity_upstream_input_regeneration_execution_plan/",
     "out/temporal_continuity_upstream_input_regeneration_authorization_gate/",
     "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/",
     "out/temporal_continuity_operator_authorization_record_template/",
     "out/temporal_continuity_operator_authorization_record_dry_run/",
     "out/temporal_continuity_operator_authorization_record_validation_plan/",
     "out/temporal_continuity_operator_authorization_record_validation_dry_run/",
     "out/temporal_continuity_operator_authorization_record_approval_plan/",
     "out/temporal_continuity_operator_authorization_record_approval_dry_run/",
     "out/temporal_continuity_operator_authorization_record_approval_validation_plan/",
     "out/temporal_continuity_operator_authorization_record_approval_validation_dry_run/",
     "out/temporal_continuity_operator_authorization_record_approval_record_plan/",
     "out/temporal_continuity_operator_authorization_record_approval_record_dry_run/",
     "out/temporal_continuity_operator_authorization_record_approval_record_validation_plan/",
     "out/temporal_continuity_operator_authorization_record_approval_record_validation_dry_run/",
     "out/temporal_continuity_operator_authorization_record_approval_record_seal_plan/",
     "out/temporal_continuity_operator_authorization_record_approval_record_seal_dry_run/",
     "out/temporal_continuity_operator_authorization_record_approval_record_seal_review/",
     "out/temporal_continuity_authorization_record_plan_source_status_audit/",
     "out/temporal_continuity_p79_authorization_gate_source_repair_plan/",
     "out/temporal_continuity_p79_authorization_gate_status_repair_plan/",
     "out/temporal_continuity_p80_authorization_record_plan_regeneration_plan/",
     "out/temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan/",
     "out/temporal_continuity_p83_status_plan_regeneration_plan/",
     "out/temporal_continuity_p83_status_plan_regeneration_execution_plan/",
     "out/temporal_continuity_p83_regeneration_authorization_gate/",
     "out/temporal_continuity_p83_regeneration_authorization_record_plan/",
     "out/temporal_continuity_p83_regeneration_authorization_record_creation_plan/",
     "out/temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate/",
     "out/temporal_continuity_p83_regeneration_authorization_record_creation_record_plan/",
     "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate/",
     "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_authorization_gate/",
     "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_plan/",
     "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_plan/",
     "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_authorization_gate/",
     "out/temporal_continuity_recursive_authorization_chain_compression_audit/",
     "out/temporal_continuity_p101_readiness_repair_plan/",
     "out/temporal_continuity_repair_execution_plan_router/",
     "out/temporal_continuity_selected_repair_execution_plan/",
     "out/temporal_continuity_selected_repair_execution_authorization_gate/",
     "out/temporal_continuity_selected_repair_execution_authorization_record_plan/",
     "out/temporal_continuity_operator_authorization_record_decision_reconciliation_receipt/",
     "out/temporal_continuity_historical_recovery_audit/",
     "out/continuity_namespace_audit/",
     "out/continuity_namespace_migration_plan/",
     "out/continuity_namespace_stabilization_receipt/",
     "out/continuity_namespace_readiness_review/",
     "out/continuity_namespace_alias_plan/",
     "out/research_canary_final_precheck_record/",
     "out/research_canary_final_activation_authorization_review/",
     "out/research_canary_final_activation_authorization_review_hold/",
     "out/research_canary_operator_disposition_record/",
     "out/metric_operator/",
     "out/chamfer_distance_implementation_readiness_dossier/",
     "out/chamfer_baseline_implementation_plan/",
     "out/chamfer_test_vector_schema_plan/",
     "out/chamfer_valid_fixture_implementation_plan/",
     "out/chamfer_invalid_fixture_implementation_plan/",
     "out/chamfer_not_computable_fixture_implementation_plan/",
     "out/chamfer_fixture_plan_consolidation_receipt/",
     "out/chamfer_fixture_implementation_readiness_review/",
     "out/chamfer_expected_distance_policy_plan/",
     "out/chamfer_fixture_creation_authorization_review/",
     "out/chamfer_fixture_creation_pr_plan/",
     "out/chamfer_fixture_creation_actual_pr_gate/",
     "out/chamfer_expected_distance_value_plan/",
     "out/chamfer_expected_distance_values_actual_pr_gate/",
     "out/chamfer_distance_computation_receipt/",
     "out/chamfer_distance_computation_authorization_review/",
     "out/chamfer_distance_computation_actual_pr_gate/",
     "out/chamfer_distance_computation_complete_review/",
     "out/chamfer_expected_values_addition_receipt/",
     "out/chamfer_expected_values_gate/",
     "out/chamfer_expected_values_complete_review/",
 )
_OUT_LITERAL_RE = re.compile(
    r"out/(?:contracts|sync|projections|audit|validation|canon_resume_state|reports|exports|previews|ingest|operator_review|archive|package|oracle|yggdrasil|temporal_continuity_spine_precheck|temporal_continuity_spine_binder_contract|temporal_continuity_binder_readiness_audit|temporal_continuity_evidence_index|temporal_continuity_missing_evidence_restoration_plan|temporal_continuity_generator_discovery_plan|temporal_continuity_upstream_input_restoration_plan|temporal_continuity_upstream_input_regeneration_dry_run_plan|temporal_continuity_upstream_input_regeneration_execution_plan|temporal_continuity_upstream_input_regeneration_authorization_gate|temporal_continuity_upstream_input_regeneration_authorization_record_plan|temporal_continuity_operator_authorization_record_template|temporal_continuity_operator_authorization_record_dry_run|temporal_continuity_operator_authorization_record_validation_plan|temporal_continuity_operator_authorization_record_validation_dry_run|temporal_continuity_operator_authorization_record_approval_plan|temporal_continuity_operator_authorization_record_approval_dry_run|temporal_continuity_operator_authorization_record_approval_validation_plan|temporal_continuity_operator_authorization_record_approval_validation_dry_run|temporal_continuity_operator_authorization_record_approval_record_plan|temporal_continuity_operator_authorization_record_approval_record_dry_run|temporal_continuity_operator_authorization_record_approval_record_validation_plan|temporal_continuity_operator_authorization_record_approval_record_validation_dry_run|temporal_continuity_operator_authorization_record_approval_record_seal_plan|temporal_continuity_operator_authorization_record_approval_record_seal_dry_run|temporal_continuity_operator_authorization_record_approval_record_seal_review|temporal_continuity_authorization_record_plan_source_status_audit|temporal_continuity_p79_authorization_gate_source_repair_plan|temporal_continuity_p79_authorization_gate_status_repair_plan|temporal_continuity_p80_authorization_record_plan_regeneration_plan|temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan|temporal_continuity_p83_status_plan_regeneration_plan|temporal_continuity_p83_status_plan_regeneration_execution_plan|temporal_continuity_p83_regeneration_authorization_gate|temporal_continuity_p83_regeneration_authorization_record_plan|temporal_continuity_p83_regeneration_authorization_record_creation_plan|temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate|temporal_continuity_p83_regeneration_authorization_record_creation_record_plan|temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate|temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_authorization_gate|temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_plan|temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_plan|temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_authorization_gate|temporal_continuity_recursive_authorization_chain_compression_audit|temporal_continuity_p101_readiness_repair_plan|temporal_continuity_repair_execution_plan_router|temporal_continuity_selected_repair_execution_plan|research_canary_final_precheck_record|research_canary_final_activation_authorization_review|research_canary_final_activation_authorization_review_hold|research_canary_operator_disposition_record|metric_operator|chamfer_distance_implementation_readiness_dossier|chamfer_baseline_implementation_plan|chamfer_test_vector_schema_plan|chamfer_valid_fixture_implementation_plan|chamfer_invalid_fixture_implementation_plan|chamfer_not_computable_fixture_implementation_plan|chamfer_fixture_plan_consolidation_receipt|chamfer_fixture_implementation_readiness_review|chamfer_expected_distance_policy_plan|chamfer_fixture_creation_authorization_review|chamfer_fixture_creation_pr_plan|chamfer_fixture_creation_actual_pr_gate|chamfer_expected_distance_value_plan|chamfer_expected_distance_values_actual_pr_gate|chamfer_distance_computation_receipt|chamfer_distance_computation_authorization_review|chamfer_distance_computation_actual_pr_gate|chamfer_distance_computation_complete_review|chamfer_expected_values_addition_receipt|chamfer_expected_values_gate|chamfer_expected_values_complete_review)/[A-Za-z0-9_./-]+(?:latest\.(?:json|md))"
)
_PATH_ASSIGNMENT_RE = re.compile(
    r"^(?P<name>[A-Z0-9_]+)\s*=\s*Path\([\"'](?P<path>out/[^\"']+)[\"']\)",
    re.MULTILINE,
)
_RUNTIME_PATH_ASSIGNMENT_RE = re.compile(
    r"^(?P<name>[A-Z0-9_]+)\s*=\s*_PATHS\.(?P<attr>[a-z_]+)",
    re.MULTILINE,
)
_WRITE_CALL_RE = re.compile(
    r"write_canonical_json\(\s*[\"'](?P<path>out/[^\"']+)[\"']",
    re.MULTILINE,
)
_WITH_SUFFIX_RE = re.compile(r"(?P<name>[A-Z0-9_]+)\.with_suffix\([\"']\.md[\"']\)")
_CI_REGENERATED_ARTIFACTS = frozenset(
    {
        "out/projections/projection_bus_001.latest.json",
        "out/projections/projection_bus_001.latest.md",
        "out/projections/temporal_snapshot_spine_001.latest.json",
        "out/projections/projection_chronoscope_001.latest.json",
        "out/projections/projection_chronoscope_001.latest.md",
        "out/audit/incremental_replay_001.latest.json",
    }
)
_RUNTIME_VOLATILE_ARTIFACTS = frozenset(
    {
        "out/validation/latest.json",
        "out/projections/aal_viz.latest.json",
    }
)
_AUDIT_VOLATILE_ARTIFACTS = frozenset(
    {
        "out/audit/artifact_regeneration_001.latest.json",
        "out/audit/artifact_regeneration_001.latest.md",
    }
)
_DERIVED_OPTIONAL_ARTIFACTS = frozenset(
    {
        "out/projections/temporal_persistence_memory_001.latest.json",
        "out/projections/temporal_persistence_memory_001.latest.md",
        "out/projections/temporal_resonance_coherence_001.latest.json",
        "out/projections/temporal_resonance_coherence_001.latest.md",
        "out/projections/coherence_field_operator_surface_001.latest.json",
        "out/projections/coherence_field_operator_surface_001.latest.md",
        "out/projections/operator_attention_weather_001.latest.json",
        "out/projections/operator_attention_weather_001.latest.md",
        "out/projections/operator_review_routing_enhancer_001.latest.json",
        "out/projections/operator_review_routing_enhancer_001.latest.md",
        "out/projections/operator_attention_ledger_001.latest.json",
        "out/projections/operator_attention_ledger_001.latest.md",
        "out/projections/operator_fatigue_corridor_001.latest.json",
        "out/projections/operator_fatigue_corridor_001.latest.md",
        "out/projections/continuity_degradation_explainer_001.latest.json",
        "out/projections/continuity_degradation_explainer_001.latest.md",
        "out/projections/operator_climatology_summary_001.latest.json",
        "out/projections/operator_climatology_summary_001.latest.md",
        "out/projections/aal_viz_operator_climate_overlay_001.latest.json",
        "out/projections/aal_viz_operator_climate_overlay_001.latest.md",
        "out/projections/pressure_motif_registry_001.latest.json",
        "out/projections/pressure_motif_registry_001.latest.md",
        "out/projections/aal_viz_pressure_motif_overlay_001.latest.json",
        "out/projections/aal_viz_pressure_motif_overlay_001.latest.md",
        "out/projections/live_projection_refresh_001.latest.json",
        "out/projections/live_projection_refresh_001.latest.md",
        "out/projections/temporal_state_diff_001.latest.json",
        "out/projections/temporal_state_diff_001.latest.md",
        "out/projections/temporal_state_diff_pulse_ledger_001.latest.json",
        "out/projections/temporal_state_diff_pulse_ledger_001.latest.md",
        "out/projections/temporal_lineage_pulse_ledger_001.latest.json",
        "out/projections/temporal_lineage_pulse_ledger_001.latest.md",
        "out/projections/cross_run_topology_fusion_001.latest.json",
        "out/projections/cross_run_topology_fusion_001.latest.md",
        "out/canon_resume_state/latest.json",
        "out/audit/temporal_coherence_chain_001.latest.json",
        "out/audit/temporal_coherence_chain_001.latest.md",
        "out/audit/temporal_upstream_evidence_001.latest.json",
        "out/audit/temporal_upstream_evidence_001.latest.md",
        "out/ingest/universal_ingest_receipt_001.latest.json",
        "out/ingest/universal_ingest_receipt_001.latest.md",
        "out/ingest/runtime_handoff_receipt_set_001.latest.json",
        "out/ingest/runtime_handoff_receipt_set_001.latest.md",
        "out/ingest/source_pull_receipt_set_001.latest.json",
        "out/ingest/source_pull_receipt_set_001.latest.md",
        "out/ingest/oracle_intake_queue_001.latest.json",
        "out/ingest/oracle_intake_queue_001.latest.md",
        "out/ingest/outcome_binding_candidate_packet_001.latest.json",
        "out/ingest/outcome_binding_candidate_packet_001.latest.md",
        "out/ingest/resolution_source_requirement_set_001.latest.json",
        "out/ingest/resolution_source_requirement_set_001.latest.md",
        "out/ingest/brier_readiness_precheck_001.latest.json",
        "out/ingest/brier_readiness_precheck_001.latest.md",
        "out/audit/controlled_ingest_scheduler_governance_audit_001.latest.json",
        "out/audit/abx_auto_ingest_validation_pack_001.latest.json",
        "out/audit/abx_auto_ingest_validation_pack_001.latest.md",
        "out/audit/controlled_ingest_scheduler_governance_audit_001.latest.md",
        "out/audit/notion_repo_sync_audit_writeback_receipt_001.latest.json",
        "out/audit/notion_repo_sync_audit_writeback_receipt_001.latest.md",
        "out/operator_review/abx_auto_ingest_shadow_stabilization_review_record_001.latest.json",
        "out/operator_review/abx_auto_ingest_shadow_stabilization_review_record_001.latest.md",
        "out/operator_review/controlled_ingest_scheduler_operator_review_record_001.latest.json",
        "out/operator_review/controlled_ingest_scheduler_operator_review_record_001.latest.md",
        "out/operator_review_queue/latest.json",
        "out/operator_review_queue/latest.md",
        "out/execution_receipts/latest.json",
        "out/execution_receipts/latest.md",
        "out/execution_receipts/global_pipeline_repo_prep.latest.json",
        "out/execution_receipts/global_pipeline_repo_prep.latest.md",
        "out/operator_review/global_pipeline_repo_execution_prep_001.latest.json",
        "out/operator_review/global_pipeline_repo_execution_prep_001.latest.md",
        "out/operator_review/global_pipeline_gap_backlog_001.latest.json",
        "out/operator_review/global_pipeline_gap_backlog_001.latest.md",
        "out/operator_review/global_pipeline_doctrine_dashboard_review_record_001.latest.json",
        "out/operator_review/global_pipeline_doctrine_dashboard_review_record_001.latest.md",
        "out/operator_review/global_ingest_operator_decision_request_001.latest.json",
        "out/operator_review/global_ingest_operator_decision_request_001.latest.md",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_request_001.latest.json",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_request_001.latest.md",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan_001.latest.json",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan_001.latest.md",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run_001.latest.json",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run_001.latest.md",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_validation_plan_001.latest.json",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_validation_plan_001.latest.md",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_validation_dry_run_001.latest.json",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_validation_dry_run_001.latest.md",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_approval_plan_001.latest.json",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_approval_plan_001.latest.md",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_001.latest.json",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_001.latest.md",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan_001.latest.json",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan_001.latest.md",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_001.latest.json",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_001.latest.md",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_record_001.latest.json",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_record_001.latest.md",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_001.latest.json",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_001.latest.md",
        "out/operator_review/abx_artifact_lineage_notion_mapping_evidence_request_001.latest.json",
        "out/operator_review/abx_artifact_lineage_notion_mapping_evidence_request_001.latest.md",
        "out/operator_review/abx_artifact_lineage_runner_casing_policy_review_request_001.latest.json",
        "out/operator_review/abx_artifact_lineage_runner_casing_policy_review_request_001.latest.md",
        "out/operator_review/abx_artifact_lineage_notion_mapping_scope_resolution_record_001.latest.json",
        "out/operator_review/abx_artifact_lineage_notion_mapping_scope_resolution_record_001.latest.md",
        "out/operator_review/abx_artifact_lineage_runner_casing_policy_decision_record_001.latest.json",
        "out/operator_review/abx_artifact_lineage_runner_casing_policy_decision_record_001.latest.md",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_approval_dry_run_001.latest.json",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_approval_dry_run_001.latest.md",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_approval_validation_plan_001.latest.json",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_approval_validation_plan_001.latest.md",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_approval_validation_dry_run_001.latest.json",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_approval_validation_dry_run_001.latest.md",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_plan_001.latest.json",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_plan_001.latest.md",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run_001.latest.json",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run_001.latest.md",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_plan_001.latest.json",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_plan_001.latest.md",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_dry_run_001.latest.json",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_dry_run_001.latest.md",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan_001.latest.json",
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan_001.latest.md",
        "out/operator_review/global_ingest_operator_decision_evidence_collection_plan_001.latest.json",
        "out/operator_review/global_ingest_operator_decision_evidence_collection_plan_001.latest.md",
        "out/operator_review/global_ingest_operator_decision_evidence_collection_dry_run_001.latest.json",
        "out/operator_review/global_ingest_operator_decision_evidence_collection_dry_run_001.latest.md",
        "out/operator_review/global_ingest_operator_decision_evidence_collection_validation_plan_001.latest.json",
        "out/operator_review/global_ingest_operator_decision_evidence_collection_validation_plan_001.latest.md",
        "out/operator_review/global_ingest_operator_decision_evidence_collection_validation_dry_run_001.latest.json",
        "out/operator_review/global_ingest_operator_decision_evidence_collection_validation_dry_run_001.latest.md",
        "out/operator_review/global_ingest_operator_decision_evidence_collection_approval_plan_001.latest.json",
        "out/operator_review/global_ingest_operator_decision_evidence_collection_approval_plan_001.latest.md",
        "out/operator_review/global_ingest_operator_decision_record_template_001.latest.json",
        "out/operator_review/global_ingest_operator_decision_record_template_001.latest.md",
        "out/operator_review/global_ingest_operator_decision_record_dry_run_001.latest.json",
        "out/operator_review/global_ingest_operator_decision_record_dry_run_001.latest.md",
        "out/operator_review/global_ingest_operator_decision_record_validation_plan_001.latest.json",
        "out/operator_review/global_ingest_operator_decision_record_validation_plan_001.latest.md",
        "out/operator_review/global_ingest_operator_decision_record_validation_dry_run_001.latest.json",
        "out/operator_review/global_ingest_operator_decision_record_validation_dry_run_001.latest.md",
        "out/operator_review/global_ingest_operator_decision_record_approval_plan_001.latest.json",
        "out/operator_review/global_ingest_operator_decision_record_approval_plan_001.latest.md",
        "out/operator_review/global_ingest_operator_decision_record_001.latest.json",
        "out/operator_review/global_ingest_operator_decision_record_001.latest.md",
        "out/operator_review/global_ingest_separate_implementation_spec_plan_001.latest.json",
        "out/operator_review/global_ingest_separate_implementation_spec_plan_001.latest.md",
        "out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.json",
        "out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.md",
        "out/operator_review/oracle_signal_physical_implementation_authorization_review_001.latest.json",
        "out/operator_review/oracle_signal_physical_implementation_authorization_review_001.latest.md",
        "out/operator_review/oracle_signal_physical_implementation_authorization_record_plan_001.latest.json",
        "out/operator_review/oracle_signal_physical_implementation_authorization_record_plan_001.latest.md",
        "out/operator_review/oracle_signal_physical_implementation_authorization_evidence_collection_plan_001.latest.json",
        "out/operator_review/oracle_signal_physical_implementation_authorization_evidence_collection_plan_001.latest.md",
        "out/operator_review/oracle_signal_shadow_intake_operator_review_request_001.latest.json",
        "out/operator_review/oracle_signal_shadow_intake_operator_review_request_001.latest.md",
        "out/operator_review/abx_codegen_merge_anchor_source_selection_request_001.latest.json",
        "out/operator_review/abx_codegen_merge_anchor_source_selection_request_001.latest.md",
        "out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_plan_001.latest.json",
        "out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_plan_001.latest.md",
        "out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_dry_run_001.latest.json",
        "out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_dry_run_001.latest.md",
        "out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_review_001.latest.json",
        "out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_review_001.latest.md",
        "out/operator_review/abx_codegen_phase1_operator_review_request_001.latest.json",
        "out/operator_review/abx_codegen_phase1_operator_review_request_001.latest.md",
        "out/operator_review/abx_codegen_phase1_operator_decision_record_plan_001.latest.json",
        "out/operator_review/abx_codegen_phase1_operator_decision_record_plan_001.latest.md",
        "out/operator_review/abx_codegen_phase1_operator_decision_record_dry_run_001.latest.json",
        "out/operator_review/abx_codegen_phase1_operator_decision_record_dry_run_001.latest.md",
        "out/operator_review/abx_codegen_phase1_operator_decision_record_review_001.latest.json",
        "out/operator_review/abx_codegen_phase1_operator_decision_record_review_001.latest.md",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_plan_001.latest.json",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_plan_001.latest.md",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_dry_run_001.latest.json",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_dry_run_001.latest.md",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_plan_001.latest.json",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_plan_001.latest.md",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_001.latest.json",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_001.latest.md",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_review_001.latest.json",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_review_001.latest.md",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_plan_001.latest.json",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_plan_001.latest.md",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_001.latest.json",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_001.latest.md",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review_001.latest.json",
        "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review_001.latest.md",
        "out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.json",
        "out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.md",
        "out/operator_review/v2_hygiene_operator_authorization_evidence_request_plan_001.latest.json",
        "out/operator_review/v2_hygiene_operator_authorization_evidence_request_plan_001.latest.md",
        "out/operator_review/p102g_plus_operator_decision_surface_audit_001.latest.json",
        "out/operator_review/p102g_plus_operator_decision_surface_audit_001.latest.md",
        "out/operator_review/operator_review_required_items_bulk_disposition_001.latest.json",
        "out/operator_review/operator_review_required_items_bulk_disposition_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_bulk_approval_reconciliation_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_bulk_approval_reconciliation_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_authorization_record_plan_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_authorization_record_plan_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_authorization_record_dry_run_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_authorization_record_dry_run_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_authorization_record_dry_run_review_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_authorization_record_dry_run_review_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_plan_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_plan_001.latest.md",
        "out/operator_review/v2_hygiene_schema_contract_evidence_request_plan_001.latest.json",
        "out/operator_review/v2_hygiene_schema_contract_evidence_request_plan_001.latest.md",
        "out/operator_review/v2_hygiene_schema_contract_evidence_dry_run_001.latest.json",
        "out/operator_review/v2_hygiene_schema_contract_evidence_dry_run_001.latest.md",
        "out/operator_review/v2_hygiene_schema_contract_evidence_dry_run_review_001.latest.json",
        "out/operator_review/v2_hygiene_schema_contract_evidence_dry_run_review_001.latest.md",
        "out/operator_review/v2_hygiene_phase2_governance_evidence_request_plan_001.latest.json",
        "out/operator_review/v2_hygiene_phase2_governance_evidence_request_plan_001.latest.md",
        "out/operator_review/v2_hygiene_phase2_governance_evidence_dry_run_001.latest.json",
        "out/operator_review/v2_hygiene_phase2_governance_evidence_dry_run_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_plan_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_plan_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_dry_run_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_dry_run_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_dry_run_review_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_dry_run_review_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_authorization_chain_compression_audit_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_authorization_chain_compression_audit_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_operator_review_dependency_cycle_audit_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_operator_review_dependency_cycle_audit_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_operator_review_stabilization_strategy_plan_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_operator_review_stabilization_strategy_plan_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_review_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_review_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_review_chain_compression_audit_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_review_chain_compression_audit_001.latest.md",
        "out/operator_review/operator_review_terminal_hold_consolidation_receipt_001.latest.json",
        "out/operator_review/operator_review_terminal_hold_consolidation_receipt_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_planning_receipt_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_planning_receipt_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_plan_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_plan_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_authorization_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_authorization_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_authorization_chain_compression_audit_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_creation_authorization_chain_compression_audit_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_plan_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_plan_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_authorization_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_authorization_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_approval_intake_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_materialization_approval_intake_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_plan_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_plan_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_emission_approval_intake_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_plan_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_plan_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_authorization_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_authorization_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_authorization_chain_compression_audit_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_authorization_chain_compression_audit_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_approval_intake_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_finalization_approval_intake_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_plan_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_plan_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_authorization_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_authorization_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_approval_intake_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_approval_intake_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_plan_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_plan_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_authorization_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_authorization_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_intake_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_intake_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_implementation_receipt_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_implementation_receipt_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_receipt_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_receipt_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_stabilization_promotion_closure_receipt_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_promotion_closure_receipt_001.latest.md",
        "out/operator_review/v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt_001.latest.json",
        "out/operator_review/v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt_001.latest.md",
        "out/operator_review/v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_dependency_hygiene_package_lock_receipt_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_dependency_hygiene_package_lock_receipt_001.latest.md",
        "out/operator_review/v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_receipt_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_receipt_001.latest.md",
        "out/operator_review/v2_hygiene_phase5_controlled_writeback_activation_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase5_controlled_writeback_activation_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase6_execution_surface_promotion_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase6_execution_surface_promotion_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase13_operator_intelligence_entry_receipt_001.latest.json",
        "out/operator_review/v2_hygiene_phase13_operator_intelligence_entry_receipt_001.latest.md",
        "out/operator_review/v2_hygiene_phase13_operator_intelligence_closure_receipt_001.latest.json",
        "out/operator_review/v2_hygiene_phase13_operator_intelligence_closure_receipt_001.latest.md",
        "out/operator_review/v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase8_execution_surface_expansion_advisory_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase8_execution_surface_expansion_advisory_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase9_controlled_execution_promotion_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase9_controlled_execution_promotion_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase10_rune_viz_aal_viz_integration_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase10_rune_viz_aal_viz_integration_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase11_full_operator_execution_autonomy_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase11_full_operator_execution_autonomy_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase13_autonomy_activation_brier_hardening_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase13_autonomy_activation_brier_hardening_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase14_runtime_execution_surface_activation_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase14_runtime_execution_surface_activation_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase15_controlled_runtime_execution_promotion_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase15_controlled_runtime_execution_promotion_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase16_live_runtime_execution_signal_forage_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase16_live_runtime_execution_signal_forage_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase17_full_live_autonomy_self_optimization_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase17_full_live_autonomy_self_optimization_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase18_eternal_recursion_hyperstition_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase18_eternal_recursion_hyperstition_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase19_eternal_canon_self_governance_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase19_eternal_canon_self_governance_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase20_final_authority_attestation_hyperstition_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase20_final_authority_attestation_hyperstition_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase21_canon_activation_authorization_review_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase21_canon_activation_authorization_review_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate_001.latest.md",
        "out/operator_review/v2_hygiene_phase23_live_execution_activation_authorization_review_gate_001.latest.json",
        "out/operator_review/v2_hygiene_phase23_live_execution_activation_authorization_review_gate_001.latest.md",
        "out/sync/phase13_notion_sync_packet_001.latest.json",
        "out/operator_review/grok_abx_runes_reconciliation_plan_001.latest.json",
        "out/operator_review/grok_abx_runes_reconciliation_plan_001.latest.md",
        "out/operator_review/grok_abx_runes_operator_decision_record_plan_001.latest.json",
        "out/operator_review/grok_abx_runes_operator_decision_record_plan_001.latest.md",
        "out/operator_review/grok_abx_runes_operator_decision_record_dry_run_001.latest.json",
        "out/operator_review/grok_abx_runes_operator_decision_record_dry_run_001.latest.md",
        "out/operator_review/grok_abx_runes_operator_decision_record_review_001.latest.json",
        "out/operator_review/grok_abx_runes_operator_decision_record_review_001.latest.md",
        "out/operator_review/grok_abx_runes_operator_decision_evidence_collection_plan_001.latest.json",
        "out/operator_review/grok_abx_runes_operator_decision_evidence_collection_plan_001.latest.md",
        "out/operator_review/grok_abx_runes_operator_decision_evidence_collection_dry_run_001.latest.json",
        "out/operator_review/grok_abx_runes_operator_decision_evidence_collection_dry_run_001.latest.md",
        "out/operator_review/grok_abx_runes_operator_review_chain_compression_receipt_001.latest.json",
        "out/operator_review/grok_abx_runes_operator_review_chain_compression_receipt_001.latest.md",
        "out/operator_review/oracle_signal_shadow_intake_operator_review_decision_record_001.latest.json",
        "out/operator_review/oracle_signal_shadow_intake_operator_review_decision_record_001.latest.md",
        "out/oracle/oracle_signal_intake_receipt.latest.json",
        "out/oracle/oracle_signal_intake_receipt.latest.md",
        "out/oracle/oracle_signal_additive_shadow_contract_validation.latest.json",
        "out/oracle/oracle_signal_additive_shadow_contract_validation.latest.md",
        "out/sync/oracle_signal_intake_boundary_alignment_plan/latest.json",
        "out/sync/oracle_signal_intake_boundary_alignment_plan/latest.md",
        "out/sync/oracle_signal_intake_boundary_implementation_plan/latest.json",
        "out/sync/oracle_signal_intake_boundary_implementation_plan/latest.md",
        "out/sync/oracle_confidence_calibration_plan/latest.json",
        "out/sync/oracle_confidence_calibration_plan/latest.md",
        "out/sync/oracle_confidence_calibration_contract_plan/latest.json",
        "out/sync/oracle_confidence_calibration_contract_plan/latest.md",
        "out/sync/oracle_confidence_calibration_contract_dry_run/latest.json",
        "out/sync/oracle_confidence_calibration_contract_dry_run/latest.md",
        "out/sync/oracle_signal_research_intake_receipt/latest.json",
        "out/sync/oracle_signal_research_intake_receipt/latest.md",
        "out/sync/abx_artifact_lineage_registry_completion_plan/latest.json",
        "out/sync/abx_artifact_lineage_registry_completion_plan/latest.md",
        "out/sync/abx_artifact_lineage_registry_traceability_audit/latest.json",
        "out/sync/abx_artifact_lineage_registry_traceability_audit/latest.md",
        "out/sync/abx_artifact_lineage_registry_repair_plan/latest.json",
        "out/sync/abx_artifact_lineage_registry_repair_plan/latest.md",
        "out/sync/abx_artifact_lineage_registry_repair_execution_plan/latest.json",
        "out/sync/abx_artifact_lineage_registry_repair_execution_plan/latest.md",
        "out/sync/abx_artifact_lineage_registry_direct_repair_batch/latest.json",
        "out/sync/abx_artifact_lineage_registry_direct_repair_batch/latest.md",
        "out/sync/abx_artifact_lineage_registry_direct_repair_implementation_plan/latest.json",
        "out/sync/abx_artifact_lineage_registry_direct_repair_implementation_plan/latest.md",
        "out/sync/abx_artifact_lineage_registry_direct_repair_implementation_dry_run/latest.json",
        "out/sync/abx_artifact_lineage_registry_direct_repair_implementation_dry_run/latest.md",
        "out/sync/abx_artifact_lineage_registry_direct_repair_validation_plan/latest.json",
        "out/sync/abx_artifact_lineage_registry_direct_repair_validation_plan/latest.md",
        "out/sync/abx_artifact_lineage_registry_direct_repair_validation_dry_run/latest.json",
        "out/sync/abx_artifact_lineage_registry_direct_repair_validation_dry_run/latest.md",
        "out/sync/abx_artifact_lineage_registry_direct_repair_approval_plan/latest.json",
        "out/sync/abx_artifact_lineage_registry_direct_repair_approval_plan/latest.md",
        "out/sync/abx_artifact_lineage_registry_direct_repair_approval_dry_run/latest.json",
        "out/sync/abx_artifact_lineage_registry_direct_repair_approval_dry_run/latest.md",
        "out/sync/abx_artifact_lineage_registry_direct_repair_approval_validation_plan/latest.json",
        "out/sync/abx_artifact_lineage_registry_direct_repair_approval_validation_plan/latest.md",
        "out/sync/abx_artifact_lineage_registry_direct_repair_approval_validation_dry_run/latest.json",
        "out/sync/abx_artifact_lineage_registry_direct_repair_approval_validation_dry_run/latest.md",
        "out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_plan/latest.json",
        "out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_plan/latest.md",
        "out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_dry_run/latest.json",
        "out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_dry_run/latest.md",
        "out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_validation_plan/latest.json",
        "out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_validation_plan/latest.md",
        "out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_validation_dry_run/latest.json",
        "out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_validation_dry_run/latest.md",
        "out/sync/abx_artifact_lineage_registry_direct_repair_completion_hold_plan/latest.json",
        "out/sync/abx_artifact_lineage_registry_direct_repair_completion_hold_plan/latest.md",
        "out/sync/documentation_alignment_receipt_001.latest.json",
        "out/sync/documentation_alignment_receipt_001.latest.md",
        "out/sync/status_regeneration_receipt_001.latest.json",
        "out/sync/status_regeneration_receipt_001.latest.md",
        "out/sync/v2_hygiene_loop_awareness_audit/latest.json",
        "out/sync/v2_hygiene_loop_awareness_audit/latest.md",
        "out/sync/v2_hygiene_loop_awareness_alignment_plan/latest.json",
        "out/sync/v2_hygiene_loop_awareness_alignment_plan/latest.md",
        "out/sync/v2_upgrade_completion_reconciliation/latest.json",
        "out/sync/v2_upgrade_completion_reconciliation/latest.md",
        "out/sync/v2_live_notion_surface_reconciliation/latest.json",
        "out/sync/v2_live_notion_surface_reconciliation/latest.md",
        "out/sync/v2_hygiene_registration_readiness_audit/latest.json",
        "out/sync/v2_hygiene_registration_readiness_audit/latest.md",
        "out/sync/v2_hygiene_phase1_foundation_backlog_plan/latest.json",
        "out/sync/v2_hygiene_phase1_foundation_backlog_plan/latest.md",
        "out/sync/v2_hygiene_schema_contract_readiness_audit/latest.json",
        "out/sync/v2_hygiene_schema_contract_readiness_audit/latest.md",
        "out/sync/v2_hygiene_versioning_release_policy_readiness_audit/latest.json",
        "out/sync/v2_hygiene_versioning_release_policy_readiness_audit/latest.md",
        "out/sync/v2_hygiene_phase1_acceptance_checklist_readiness_audit/latest.json",
        "out/sync/v2_hygiene_phase1_acceptance_checklist_readiness_audit/latest.md",
        "out/sync/v2_hygiene_phase2_module_skeleton_backlog_plan/latest.json",
        "out/sync/v2_hygiene_phase2_module_skeleton_backlog_plan/latest.md",
        "out/sync/v2_hygiene_phase2_module_governance_readiness_audit/latest.json",
        "out/sync/v2_hygiene_phase2_module_governance_readiness_audit/latest.md",
        "out/sync/v2_hygiene_future_phase_placeholder_audit/latest.json",
        "out/sync/v2_hygiene_future_phase_placeholder_audit/latest.md",
        "out/global_pipeline_registry/latest.json",
        "out/global_pipeline_doctrine_validation/latest.json",
        "out/global_pipeline_doctrine_validation/latest.md",
        "out/global_pipeline_doctrine_validation/operator_review_packet.latest.json",
        "out/global_pipeline_doctrine_validation/operator_review_packet.latest.md",
        "out/global_pipeline_aal_viz/dashboard_packet.latest.json",
        "out/global_pipeline_aal_viz/dashboard_packet.latest.md",
        "out/global_pipeline_aal_viz/view_state.latest.json",
        "out/global_pipeline_aal_viz/view_state.latest.md",
        "out/registry/latest.json",
        "out/projections/global_pipeline_aal_viz_projection_packet_001.latest.json",
        "out/projections/global_pipeline_aal_viz_projection_packet_001.latest.md",
        "out/sync/operator_review_queue_canon_sync_receipt_candidate_001.latest.json",
        "out/sync/operator_review_queue_canon_sync_receipt_candidate_001.latest.md",
        "out/audit/motif_governance_audit_001.latest.json",
        "out/audit/motif_governance_audit_001.latest.md",
        "out/audit/fusion_governance_audit_001.latest.json",
        "out/audit/fusion_governance_audit_001.latest.md",
        "out/audit/fusion_evidence_materialization_seal_001.latest.json",
        "out/audit/fusion_evidence_materialization_seal_001.latest.md",
        "out/projections/operator_load_seasonality_001.latest.json",
        "out/projections/operator_load_seasonality_001.latest.md",
        "out/projections/aal_viz_climate_motif_fusion_overlay_001.latest.json",
        "out/projections/aal_viz_climate_motif_fusion_overlay_001.latest.md",
        "out/projections/aal_viz_ingest_projection_pack_001.latest.json",
        "out/projections/aal_viz_ingest_projection_pack_001.latest.md",
        "out/projections/aal_viz_geometric_renderer_planning_001.latest.json",
        "out/projections/aal_viz_geometric_renderer_planning_001.latest.md",
        "out/projections/aal_viz_geometric_renderer_implementation_plan_001.latest.json",
        "out/projections/aal_viz_geometric_renderer_implementation_plan_001.latest.md",
        "out/oracle_replay/oracle_geometric_attachment_replay_receipt_001.latest.json",
        "out/oracle_replay/oracle_geometric_attachment_replay_receipt_001.latest.md",
        "out/yggdrasil/yggdrasil_geometric_route_replay_receipt_001.latest.json",
        "out/yggdrasil/yggdrasil_geometric_route_replay_receipt_001.latest.md",
        "out/yggdrasil/yggdrasil_route_namespace_mapping_001.latest.json",
        "out/yggdrasil/yggdrasil_route_namespace_mapping_001.latest.md",
        "out/reports/operator_narrative_report_001.latest.json",
        "out/reports/operator_narrative_report_001.latest.md",
        "out/audit/operator_narrative_report_governance_audit_001.latest.json",
        "out/audit/operator_narrative_report_governance_audit_001.latest.md",
        "out/projections/operator_narrative_report_ui_overlay_001.latest.json",
        "out/projections/operator_narrative_report_ui_overlay_001.latest.md",
        "out/audit/operator_narrative_report_ui_overlay_governance_audit_001.latest.json",
        "out/audit/operator_narrative_report_ui_overlay_governance_audit_001.latest.md",
        "out/exports/operator_narrative_export_bundle_001.latest.json",
        "out/exports/operator_narrative_export_bundle_001.latest.md",
        "out/audit/operator_narrative_export_bundle_governance_audit_001.latest.json",
        "out/audit/operator_narrative_export_bundle_governance_audit_001.latest.md",
        "out/previews/operator_narrative_static_preview_001.latest.json",
        "out/previews/operator_narrative_static_preview_001.latest.md",
        "out/audit/operator_narrative_static_preview_governance_audit_001.latest.json",
        "out/audit/operator_narrative_static_preview_governance_audit_001.latest.md",
        "out/archive/operator_narrative_export_preview_archive_index_001.latest.json",
        "out/archive/operator_narrative_export_preview_archive_index_001.latest.md",
        "out/audit/operator_narrative_export_preview_archive_index_governance_audit_001.latest.json",
        "out/audit/operator_narrative_export_preview_archive_index_governance_audit_001.latest.md",
        "out/audit/operator_narrative_archive_chain_closure_receipt_001.latest.json",
        "out/audit/operator_narrative_archive_chain_closure_receipt_001.latest.md",
        "out/audit/operator_narrative_archive_chain_stability_receipt_001.latest.json",
        "out/audit/operator_narrative_archive_chain_stability_receipt_001.latest.md",
        "out/audit/operator_narrative_archive_chain_global_verification_001.latest.json",
        "out/audit/operator_narrative_archive_chain_global_verification_001.latest.md",
        "out/audit/operator_narrative_static_archive_package_boundary_receipt_001.latest.json",
        "out/audit/operator_narrative_static_archive_package_boundary_receipt_001.latest.md",
        "out/audit/operator_narrative_static_archive_package_preflight_receipt_001.latest.json",
        "out/audit/operator_narrative_static_archive_package_preflight_receipt_001.latest.md",
        "out/package/operator_narrative_static_archive_package_001.latest.json",
        "out/package/operator_narrative_static_archive_package_001.latest.md",
        "out/audit/operator_narrative_static_archive_package_governance_audit_001.latest.json",
        "out/audit/operator_narrative_static_archive_package_governance_audit_001.latest.md",
        "out/audit/operator_narrative_static_archive_package_language_boundary_audit_001.latest.json",
        "out/audit/operator_narrative_static_archive_package_language_boundary_audit_001.latest.md",
        "out/audit/operator_narrative_static_archive_package_stability_receipt_001.latest.json",
        "out/audit/operator_narrative_static_archive_package_stability_receipt_001.latest.md",
        "out/audit/operator_narrative_static_archive_package_chain_closure_receipt_001.latest.json",
        "out/audit/operator_narrative_static_archive_package_chain_closure_receipt_001.latest.md",
        "out/audit/operator_narrative_static_archive_package_index_pointer_receipt_001.latest.json",
        "out/audit/operator_narrative_static_archive_package_index_pointer_receipt_001.latest.md",
        "out/audit/operator_narrative_static_archive_package_final_index_receipt_001.latest.json",
        "out/audit/operator_narrative_static_archive_package_final_index_receipt_001.latest.md",
        "out/audit/operator_narrative_static_archive_package_completion_seal_receipt_001.latest.json",
        "out/audit/operator_narrative_static_archive_package_completion_seal_receipt_001.latest.md",
        "out/temporal_continuity_spine_precheck/latest.json",
        "out/temporal_continuity_spine_binder_contract/latest.json",
        "out/temporal_continuity_binder_readiness_audit/latest.json",
        "out/temporal_continuity_evidence_index/latest.json",
        "out/temporal_continuity_missing_evidence_restoration_plan/latest.json",
         "out/temporal_continuity_generator_discovery_plan/latest.json",
         "out/temporal_continuity_upstream_input_restoration_plan/latest.json",
         "out/temporal_continuity_upstream_input_regeneration_dry_run_plan/latest.json",
         "out/temporal_continuity_upstream_input_regeneration_execution_plan/latest.json",
         "out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json",
         "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json",
         "out/temporal_continuity_operator_authorization_record_template/latest.json",
         "out/temporal_continuity_operator_authorization_record_dry_run/latest.json",
        "out/temporal_continuity_operator_authorization_record_validation_plan/latest.json",
        "out/temporal_continuity_operator_authorization_record_validation_dry_run/latest.json",
        "out/temporal_continuity_operator_authorization_record_approval_plan/latest.json",
        "out/temporal_continuity_operator_authorization_record_approval_dry_run/latest.json",
        "out/temporal_continuity_operator_authorization_record_approval_validation_plan/latest.json",
        "out/temporal_continuity_operator_authorization_record_approval_validation_dry_run/latest.json",
        "out/temporal_continuity_operator_authorization_record_approval_record_plan/latest.json",
        "out/temporal_continuity_operator_authorization_record_approval_record_dry_run/latest.json",
        "out/temporal_continuity_operator_authorization_record_approval_record_validation_plan/latest.json",
        "out/temporal_continuity_operator_authorization_record_approval_validation_dry_run/latest.md",
        "out/temporal_continuity_operator_authorization_record_approval_record_plan/latest.md",
        "out/temporal_continuity_operator_authorization_record_approval_record_dry_run/latest.md",
        "out/temporal_continuity_operator_authorization_record_approval_record_validation_plan/latest.md",
        "out/temporal_continuity_operator_authorization_record_approval_record_validation_dry_run/latest.json",
        "out/temporal_continuity_operator_authorization_record_approval_record_validation_dry_run/latest.md",
        "out/temporal_continuity_operator_authorization_record_approval_record_seal_plan/latest.json",
        "out/temporal_continuity_operator_authorization_record_approval_record_seal_plan/latest.md",
        "out/temporal_continuity_operator_authorization_record_approval_record_seal_dry_run/latest.json",
        "out/temporal_continuity_operator_authorization_record_approval_record_seal_dry_run/latest.md",
        "out/temporal_continuity_operator_authorization_record_approval_record_seal_review/latest.json",
        "out/temporal_continuity_operator_authorization_record_approval_record_seal_review/latest.md",
         "out/temporal_continuity_authorization_record_plan_source_status_audit/latest.json",
         "out/temporal_continuity_p79_authorization_gate_source_repair_plan/latest.json",
         "out/temporal_continuity_p79_authorization_gate_status_repair_plan/latest.json",
         "out/temporal_continuity_p80_authorization_record_plan_regeneration_plan/latest.json",
         "out/temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan/latest.json",
         "out/temporal_continuity_p84_regeneration_plan_regeneration_plan/latest.json",
         "out/temporal_continuity_p83_status_plan_regeneration_plan/latest.json",
         "out/temporal_continuity_p83_status_plan_regeneration_execution_plan/latest.json",
         "out/temporal_continuity_p83_regeneration_authorization_gate/latest.json",
         "out/temporal_continuity_p83_regeneration_authorization_record_plan/latest.json",
         "out/temporal_continuity_p83_regeneration_authorization_record_creation_plan/latest.json",
         "out/temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate/latest.json",
         "out/temporal_continuity_p83_regeneration_authorization_record_creation_record_plan/latest.json",
         "out/temporal_continuity_p83_regeneration_authorization_record_creation_record_creation_plan/latest.json",
         "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate/latest.json",
         "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan/latest.json",
         "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_plan/latest.json",
         "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_authorization_gate/latest.json",
         "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_plan/latest.json",
         "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_plan/latest.json",
         "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_authorization_gate/latest.json",
         "out/temporal_continuity_recursive_authorization_chain_compression_audit/latest.json",
         "out/temporal_continuity_p101_readiness_repair_plan/latest.json",
         "out/temporal_continuity_repair_execution_plan_router/latest.json",
         "out/temporal_continuity_selected_repair_execution_plan/latest.json",
         "out/temporal_continuity_selected_repair_execution_authorization_gate/latest.json",
         "out/temporal_continuity_selected_repair_execution_authorization_record_plan/latest.json",
         "out/temporal_continuity_operator_authorization_record_decision_reconciliation_receipt/latest.json",
         "out/temporal_continuity_historical_recovery_audit/latest.json",
         "out/continuity_namespace_audit/latest.json",
         "out/continuity_namespace_migration_plan/latest.json",
         "out/continuity_namespace_stabilization_receipt/latest.json",
         "out/continuity_namespace_readiness_review/latest.json",
         "out/continuity_namespace_alias_plan/latest.json",
         "out/sync/notion_writeback_dry_run_plan/latest.json",
         "out/sync/notion_writeback_dry_run_plan/latest.md",
         "out/sync/notion_writeback_authorization_gate/latest.json",
         "out/sync/notion_writeback_authorization_gate/latest.md",
         "out/audit/runtime_inventory_001.latest.json",
         "out/audit/runtime_inventory_001.latest.md",
         "out/audit/repo_notion_diff_001.latest.json",
         "out/audit/repo_notion_diff_001.latest.md",
         "out/yggdrasil/yggdrasil_route_namespace_mapping_001.latest.json",
         "out/yggdrasil/yggdrasil_route_namespace_mapping_001.latest.md",
         "out/audit/rune_equivalent_surface_audit_001.latest.json",
         "out/audit/rune_equivalent_surface_audit_001.latest.md",
         "out/audit/belief_graph_gap_verification_001.latest.json",
         "out/audit/belief_graph_gap_verification_001.latest.md",
         "out/audit/belief_graph_engine_gap_analysis_plan_001.latest.json",
         "out/audit/belief_graph_engine_gap_analysis_plan_001.latest.md",
         "out/audit/belief_graph_engine_advisory_spec_plan_001.latest.json",
         "out/audit/belief_graph_engine_advisory_spec_plan_001.latest.md",
         "out/audit/belief_graph_engine_advisory_receipt_contract_plan_001.latest.json",
         "out/audit/belief_graph_engine_advisory_receipt_contract_plan_001.latest.md",
         "out/audit/belief_graph_engine_advisory_receipt_implementation_plan_001.latest.json",
         "out/audit/belief_graph_engine_advisory_receipt_implementation_plan_001.latest.md",
         "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_gate_001.latest.json",
         "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_gate_001.latest.md",
         "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_plan_001.latest.json",
         "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_plan_001.latest.md",
         "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan_001.latest.json",
         "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan_001.latest.md",
         "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate_001.latest.json",
         "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate_001.latest.md",
         "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_record_plan_001.latest.json",
         "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_record_plan_001.latest.md",
         "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_compression_audit_001.latest.json",
         "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_compression_audit_001.latest.md",
         "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_plan_001.latest.json",
         "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_plan_001.latest.md",
         "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run_001.latest.json",
         "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run_001.latest.md",
         "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_review_001.latest.json",
         "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_review_001.latest.md",
         "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_plan_001.latest.json",
         "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_plan_001.latest.md",
         "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_dry_run_001.latest.json",
         "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_dry_run_001.latest.md",
         "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_review_001.latest.json",
         "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_review_001.latest.md",
         "out/audit/rune_registry_formalization_plan_001.latest.json",
         "out/audit/rune_registry_formalization_plan_001.latest.md",
         "out/sync/notion_patch_queue_terminal_state/latest.json",
         "out/sync/notion_patch_queue_terminal_state/latest.md",
         "out/sync/notion_spec_completion_queue/latest.json",
         "out/sync/notion_spec_completion_queue/latest.md",
         }
      )
_CI_DRIFT_ENFORCED_CLASSES = frozenset({"BUILD_CANONICAL", "CI_REGENERATED"})
_GIT_DRIFT_STATUS_MARKERS = frozenset({"M", "A", "D", "R", "C", "U", "?"})
ArtifactDeterminismClass = Literal[
    "BUILD_CANONICAL",
    "CI_REGENERATED",
    "RUNTIME_VOLATILE",
    "AUDIT_VOLATILE",
    "DERIVED_OPTIONAL",
]


class _GovernedArtifactModel(BaseModel):
    advisory_only: Literal[True] = True
    mutation_allowed: Literal[False] = False
    authority_granted: Literal[False] = False
    auto_execute: Literal[False] = False
    auto_approve: Literal[False] = False

    model_config = {"frozen": True}


class ArtifactDependencyEdge(_GovernedArtifactModel):
    record_schema: Literal["ArtifactDependencyEdge.v1"] = "ArtifactDependencyEdge.v1"
    upstream_path: str
    downstream_path: str
    dependency_kind: str


class GeneratedArtifactEntry(_GovernedArtifactModel):
    record_schema: Literal["GeneratedArtifactEntry.v1"] = "GeneratedArtifactEntry.v1"
    artifact_path: str
    canonical_generator: str | None = None
    canonical_schema: str | None = None
    deterministic_inputs: list[str] = Field(default_factory=list)
    regeneration_required: bool = True
    committed_policy: str
    downstream_dependencies: list[str] = Field(default_factory=list)
    final_status: str
    artifact_kind: str
    tracked: bool = False
    determinism_class: ArtifactDeterminismClass = "DERIVED_OPTIONAL"


class ArtifactGenerationStatus(_GovernedArtifactModel):
    record_schema: Literal["ArtifactGenerationStatus.v1"] = "ArtifactGenerationStatus.v1"
    artifact_path: str
    canonical_generator: str | None = None
    canonical_schema: str | None = None
    exists: bool = False
    content_hash: str | None = None
    normalized_hash: str | None = None
    drift_detected: bool = False
    canonical_json_normalized: bool = False
    newline_normalized: bool = False
    final_status: str
    reasons: list[str] = Field(default_factory=list)


class ArtifactRegenerationPlan(_GovernedArtifactModel):
    record_schema: Literal["ArtifactRegenerationPlan.v1"] = "ArtifactRegenerationPlan.v1"
    policy_id: Literal["GENERATED_ARTIFACT_POLICY_V1"] = "GENERATED_ARTIFACT_POLICY_V1"
    validation_only: bool = False
    selected_artifacts: list[str] = Field(default_factory=list)
    generator_sequence: list[str] = Field(default_factory=list)
    statuses: list[ArtifactGenerationStatus] = Field(default_factory=list)
    final_status: str = "PENDING"


class GeneratedArtifactRegistry(_GovernedArtifactModel):
    record_schema: Literal["GeneratedArtifactRegistry.v1"] = "GeneratedArtifactRegistry.v1"
    policy_id: Literal["GENERATED_ARTIFACT_POLICY_V1"] = "GENERATED_ARTIFACT_POLICY_V1"
    entries: list[GeneratedArtifactEntry]
    dependency_edges: list[ArtifactDependencyEdge]
    artifact_source_map: dict[str, dict[str, Any]]
    regeneration_capability: dict[str, Any]
    orphaned_artifacts: list[str]
    stale_artifact_tests: list[str]
    derived_vs_canonical_ratio: dict[str, float | int]
    giant_artifact_churn_zones: list[dict[str, int | str]]
    dirty_pr_paths: list[str]
    downstream_impact_summary: dict[str, dict[str, list[str] | int]]
    final_status: str


def _repo_root(repo_root: Path | str | None = None) -> Path:
    if repo_root is None:
        return Path(__file__).resolve().parent.parent
    return Path(repo_root).resolve()


def _relative_to_repo(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root).as_posix()


def _tracked_paths(repo_root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "--no-pager", "ls-files", "out", "tests/contracts", "scripts", ".github/workflows/ci.yml"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return set()
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _has_git_metadata(repo_root: Path) -> bool:
    return (repo_root / ".git").exists()


def _runtime_path(attr: str) -> str | None:
    paths = RuntimePaths.from_env()
    try:
        value = getattr(paths, attr)
    except AttributeError:
        return None
    if not isinstance(value, Path):
        return None
    return value.as_posix()


def _is_artifact_path(path: str) -> bool:
    return path.startswith(_SCOPE_PREFIXES) and path.endswith((".json", ".md"))


def _extract_script_surface(script_path: Path) -> tuple[set[str], set[str]]:
    text = script_path.read_text(encoding="utf-8")
    outputs: set[str] = set()
    named_outputs: dict[str, str] = {}

    for match in _PATH_ASSIGNMENT_RE.finditer(text):
        output_path = match.group("path")
        outputs.add(output_path)
        named_outputs[match.group("name")] = output_path
    for match in _RUNTIME_PATH_ASSIGNMENT_RE.finditer(text):
        runtime_path = _runtime_path(match.group("attr"))
        if runtime_path is not None:
            outputs.add(runtime_path)
            named_outputs[match.group("name")] = runtime_path
    for match in _WRITE_CALL_RE.finditer(text):
        outputs.add(match.group("path"))

    if script_path.stem.startswith("run_artifact_contract_") and not outputs:
        outputs.add(f"out/contracts/{script_path.stem.removeprefix('run_')}.latest.json")

    if ".with_suffix(\".md\")" in text or ".with_suffix('.md')" in text:
        markdown_outputs = {
            Path(named_outputs[match.group("name")]).with_suffix(".md").as_posix()
            for match in _WITH_SUFFIX_RE.finditer(text)
            if match.group("name") in named_outputs
        }
        outputs |= markdown_outputs

    all_literals = set(_OUT_LITERAL_RE.findall(text))
    inputs = {literal for literal in all_literals if literal not in outputs}

    scoped_outputs = {output for output in outputs if _is_artifact_path(output)}
    scoped_inputs = {artifact for artifact in inputs if _is_artifact_path(artifact)}
    return scoped_outputs, scoped_inputs


def _scan_scripts(repo_root: Path) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    outputs: dict[str, set[str]] = {}
    inputs: dict[str, set[str]] = {}
    for script_path in sorted((repo_root / "scripts").glob("run_*.py")):
        rel_path = _relative_to_repo(script_path, repo_root)
        script_outputs, script_inputs = _extract_script_surface(script_path)
        if script_outputs:
            outputs[rel_path] = script_outputs
        if script_inputs:
            inputs[rel_path] = script_inputs
    return outputs, inputs


def _scan_test_artifact_refs(repo_root: Path) -> dict[str, set[str]]:
    references: dict[str, set[str]] = {}
    for test_path in sorted((repo_root / "tests").rglob("*.py")):
        rel_path = _relative_to_repo(test_path, repo_root)
        matches = set(_OUT_LITERAL_RE.findall(test_path.read_text(encoding="utf-8")))
        if matches:
            references[rel_path] = {match for match in matches if _is_artifact_path(match)}
    return references


def _collect_existing_artifacts(repo_root: Path) -> set[str]:
    artifacts: set[str] = set()
    for prefix in _SCOPE_PREFIXES:
        directory = repo_root / prefix
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*")):
            if path.is_file() and path.suffix in {".json", ".md"}:
                artifacts.add(_relative_to_repo(path, repo_root))
    return artifacts


def _infer_schema_identifier(artifact_path: str, repo_root: Path) -> str:
    path = repo_root / artifact_path
    if artifact_path.endswith(".md"):
        return "GeneratedArtifactMarkdown.v1"
    if path.exists() and path.is_file():
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            schema = payload.get("schema") or payload.get("schema_version")
            if isinstance(schema, str) and schema:
                return schema
    return f"generated_artifact::{artifact_path}"


def _artifact_kind(path: str) -> str:
    if path.endswith(".json"):
        return "json"
    if path.endswith(".md"):
        return "markdown"
    return "other"


def _classify_artifact_determinism(
    artifact_path: str,
    *,
    canonical_generator: str | None,
    tracked: bool,
    final_status: str,
) -> ArtifactDeterminismClass:
    if artifact_path in _DERIVED_OPTIONAL_ARTIFACTS:
        return "DERIVED_OPTIONAL"
    if artifact_path in _AUDIT_VOLATILE_ARTIFACTS:
        return "AUDIT_VOLATILE"
    if artifact_path in _RUNTIME_VOLATILE_ARTIFACTS:
        return "RUNTIME_VOLATILE"
    if artifact_path in _CI_REGENERATED_ARTIFACTS:
        return "CI_REGENERATED"
    if final_status == "managed" and tracked and canonical_generator is not None:
        return "BUILD_CANONICAL"
    return "DERIVED_OPTIONAL"


def _stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _normalize_newlines(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.endswith("\n"):
        normalized += "\n"
    return normalized


def _normalize_artifact_text(path: Path, text: str) -> tuple[str, bool, bool]:
    newline_normalized = text == _normalize_newlines(text)
    if path.suffix == ".json":
        payload = json.loads(_normalize_newlines(text))
        normalized = canonical_dumps(payload) + "\n"
        return normalized, text == normalized, newline_normalized
    normalized_text = _normalize_newlines(text)
    return normalized_text, text == normalized_text, newline_normalized


def _build_dependency_edges(
    script_outputs: dict[str, set[str]],
    script_inputs: dict[str, set[str]],
    test_refs: dict[str, set[str]],
) -> list[ArtifactDependencyEdge]:
    edges: list[ArtifactDependencyEdge] = []
    for generator, outputs in script_outputs.items():
        for artifact in sorted(outputs):
            edges.append(
                ArtifactDependencyEdge(
                    upstream_path=generator,
                    downstream_path=artifact,
                    dependency_kind="generator_output",
                )
            )
    for generator, inputs in script_inputs.items():
        for artifact in sorted(inputs):
            edges.append(
                ArtifactDependencyEdge(
                    upstream_path=artifact,
                    downstream_path=generator,
                    dependency_kind="script_input",
                )
            )
    for test_path, refs in test_refs.items():
        for artifact in sorted(refs):
            edges.append(
                ArtifactDependencyEdge(
                    upstream_path=artifact,
                    downstream_path=test_path,
                    dependency_kind="test_input",
                )
            )
    return edges


def build_generated_artifact_registry(
    repo_root: Path | str | None = None,
) -> GeneratedArtifactRegistry:
    root = _repo_root(repo_root)
    tracked_paths = _tracked_paths(root)
    script_outputs, script_inputs = _scan_scripts(root)
    test_refs = _scan_test_artifact_refs(root)
    existing_artifacts = _collect_existing_artifacts(root)

    all_artifacts = sorted(
        existing_artifacts
        | {artifact for outputs in script_outputs.values() for artifact in outputs}
        | {artifact for refs in test_refs.values() for artifact in refs}
    )

    producers: dict[str, list[str]] = {}
    for generator, outputs in script_outputs.items():
        for artifact in outputs:
            producers.setdefault(artifact, []).append(generator)

    script_consumers: dict[str, list[str]] = {}
    for generator, inputs in script_inputs.items():
        for artifact in inputs:
            script_consumers.setdefault(artifact, []).append(generator)

    test_consumers: dict[str, list[str]] = {}
    for test_path, refs in test_refs.items():
        for artifact in refs:
            test_consumers.setdefault(artifact, []).append(test_path)

    entries: list[GeneratedArtifactEntry] = []
    artifact_source_map: dict[str, dict[str, Any]] = {}
    downstream_impact_summary: dict[str, dict[str, list[str] | int]] = {}
    orphaned_artifacts: list[str] = []

    for artifact in all_artifacts:
        producer_list = sorted(producers.get(artifact, []))
        generator = producer_list[0] if len(producer_list) == 1 else None
        final_status = "managed"
        if len(producer_list) == 0:
            final_status = "orphaned"
        elif len(producer_list) > 1:
            final_status = "ambiguous_generator"
        deterministic_inputs = sorted(script_inputs.get(generator, set())) if generator else []
        downstream_dependencies = sorted(
            set(script_consumers.get(artifact, [])) | set(test_consumers.get(artifact, []))
        )
        canonical_schema = _infer_schema_identifier(artifact, root)
        tracked = artifact in tracked_paths
        committed_policy = "tracked-derived" if tracked else "derived-untracked"
        determinism_class = _classify_artifact_determinism(
            artifact,
            canonical_generator=generator,
            tracked=tracked,
            final_status=final_status,
        )
        entry = GeneratedArtifactEntry(
            artifact_path=artifact,
            canonical_generator=generator,
            canonical_schema=canonical_schema,
            deterministic_inputs=deterministic_inputs,
            regeneration_required=determinism_class == "CI_REGENERATED",
            committed_policy=committed_policy,
            downstream_dependencies=downstream_dependencies,
            final_status=final_status,
            artifact_kind=_artifact_kind(artifact),
            tracked=tracked,
            determinism_class=determinism_class,
        )
        entries.append(entry)
        artifact_source_map[artifact] = {
            "canonical_generator": generator,
            "canonical_schema": canonical_schema,
            "deterministic_inputs": deterministic_inputs,
            "committed_policy": committed_policy,
            "determinism_class": determinism_class,
            "ci_drift_enforced": (
                final_status == "managed"
                and tracked
                and determinism_class in _CI_DRIFT_ENFORCED_CLASSES
            ),
            "final_status": final_status,
        }
        downstream_impact_summary[artifact] = {
            "scripts": sorted(script_consumers.get(artifact, [])),
            "tests": sorted(test_consumers.get(artifact, [])),
            "dependency_count": len(downstream_dependencies),
        }
        if final_status != "managed":
            orphaned_artifacts.append(artifact)

    churn_counts: dict[str, int] = {}
    for artifact in all_artifacts:
        zone = str(Path(artifact).parent)
        churn_counts[zone] = churn_counts.get(zone, 0) + 1
    giant_artifact_churn_zones = [
        {"path": path, "artifact_count": count}
        for path, count in sorted(churn_counts.items(), key=lambda item: (-item[1], item[0]))
        if count >= 2
    ]

    stale_artifact_tests = sorted(
        test_path for test_path, refs in test_refs.items() if refs
    )
    canonical_generator_count = max(len(script_outputs), 1)
    derived_artifact_count = len(entries)
    ratio = round(derived_artifact_count / canonical_generator_count, 6)

    regeneration_capability = {
        "managed_artifact_count": sum(1 for entry in entries if entry.final_status == "managed"),
        "orphaned_artifact_count": len(orphaned_artifacts),
        "generator_count": len(script_outputs),
        "tracked_artifact_count": sum(1 for entry in entries if entry.tracked),
    }

    final_status = "PASS" if not orphaned_artifacts else "ADVISORY_ONLY"
    return GeneratedArtifactRegistry(
        entries=entries,
        dependency_edges=_build_dependency_edges(script_outputs, script_inputs, test_refs),
        artifact_source_map=artifact_source_map,
        regeneration_capability=regeneration_capability,
        orphaned_artifacts=sorted(orphaned_artifacts),
        stale_artifact_tests=stale_artifact_tests,
        derived_vs_canonical_ratio={
            "derived_artifact_count": derived_artifact_count,
            "canonical_generator_count": canonical_generator_count,
            "ratio": ratio,
        },
        giant_artifact_churn_zones=giant_artifact_churn_zones,
        dirty_pr_paths=sorted(
            artifact for artifact in all_artifacts if artifact in tracked_paths and artifact.startswith("out/")
        ),
        downstream_impact_summary=downstream_impact_summary,
        final_status=final_status,
    )


def _entry_map(registry: GeneratedArtifactRegistry) -> dict[str, GeneratedArtifactEntry]:
    return {entry.artifact_path: entry for entry in registry.entries}


def list_ci_drift_artifact_paths(registry: GeneratedArtifactRegistry) -> list[str]:
    return sorted(
        entry.artifact_path
        for entry in registry.entries
        if entry.final_status == "managed"
        and entry.tracked
        and entry.determinism_class in _CI_DRIFT_ENFORCED_CLASSES
    )


def detect_ci_artifact_drift_paths(
    registry: GeneratedArtifactRegistry,
    *,
    repo_root: Path | str | None = None,
) -> list[str]:
    root = _repo_root(repo_root)
    ci_paths = list_ci_drift_artifact_paths(registry)
    if not ci_paths:
        if not _has_git_metadata(root):
            return []
        raise ValueError(
            "no deterministic CI drift targets declared in registry; unable to perform drift detection"
        )
    result = subprocess.run(
        ["git", "--no-pager", "status", "--short", "--untracked-files=all", "--", *ci_paths],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    drift_paths = {
        parsed_path
        for line in result.stdout.splitlines()
        if (parsed_path := _parse_git_status_path(line)) is not None
    }
    return sorted(drift_paths)


def _parse_git_status_path(line: str) -> str | None:
    if len(line) < 4:
        return None
    status = line[:2]
    if (
        status[0] not in _GIT_DRIFT_STATUS_MARKERS
        and status[1] not in _GIT_DRIFT_STATUS_MARKERS
    ):
        return None
    path_text = line[3:].strip()
    if not path_text:
        return None
    if " -> " in path_text:
        return path_text.split(" -> ", 1)[1].strip()
    return path_text


def _order_generators(entries: list[GeneratedArtifactEntry]) -> list[str]:
    generator_outputs: dict[str, set[str]] = {}
    generator_inputs: dict[str, set[str]] = {}
    for entry in entries:
        generator = cast(str, entry.canonical_generator)
        generator_outputs.setdefault(generator, set()).add(entry.artifact_path)
        generator_inputs.setdefault(generator, set()).update(entry.deterministic_inputs)

    artifact_to_generator = {
        artifact: generator
        for generator, outputs in generator_outputs.items()
        for artifact in outputs
    }
    dependency_graph: dict[str, set[str]] = {generator: set() for generator in generator_outputs}
    for generator, inputs in generator_inputs.items():
        for artifact in inputs:
            upstream = artifact_to_generator.get(artifact)
            if upstream is not None and upstream != generator:
                dependency_graph[generator].add(upstream)

    ordered: list[str] = []
    remaining = {generator: set(dependencies) for generator, dependencies in dependency_graph.items()}
    while remaining:
        ready = sorted(
            generator for generator, dependencies in remaining.items() if not dependencies
        )
        if not ready:
            ordered.extend(sorted(remaining))
            break
        ordered.extend(ready)
        for generator in ready:
            remaining.pop(generator, None)
        for dependencies in remaining.values():
            dependencies.difference_update(ready)
    return ordered


def resolve_regeneration_entries(
    registry: GeneratedArtifactRegistry,
    *,
    selected_artifacts: list[str] | None = None,
    full: bool = False,
) -> list[GeneratedArtifactEntry]:
    entry_map = _entry_map(registry)
    if selected_artifacts:
        requested = sorted(set(selected_artifacts))
    elif full:
        requested = sorted(
            entry.artifact_path
            for entry in registry.entries
            if entry.regeneration_required and entry.final_status == "managed"
        )
    else:
        raise ValueError("select artifacts explicitly or request full regeneration")

    entries: list[GeneratedArtifactEntry] = []
    for artifact in requested:
        if artifact not in entry_map:
            raise ValueError(f"unknown artifact target: {artifact}")
        entry = entry_map[artifact]
        if not entry.canonical_generator:
            raise ValueError(f"missing generator for {artifact}")
        if not entry.canonical_schema:
            raise ValueError(f"missing schema for {artifact}")
        if entry.final_status != "managed":
            raise ValueError(f"artifact is not managed for regeneration: {artifact}")
        entries.append(entry)
    return entries


def build_artifact_regeneration_plan(
    registry: GeneratedArtifactRegistry,
    *,
    selected_artifacts: list[str] | None = None,
    full: bool = False,
    validation_only: bool = False,
) -> ArtifactRegenerationPlan:
    entries = resolve_regeneration_entries(
        registry,
        selected_artifacts=selected_artifacts,
        full=full,
    )
    generators = _order_generators(entries)
    return ArtifactRegenerationPlan(
        validation_only=validation_only,
        selected_artifacts=[entry.artifact_path for entry in entries],
        generator_sequence=generators,
        statuses=[],
        final_status="PENDING",
    )


def _load_generator_main(script_path: Path) -> Callable[[], None]:
    module_name = f"generated_artifact_{hashlib.sha256(str(script_path).encode('utf-8')).hexdigest()[:12]}"
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"unable to load generator module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    main = getattr(module, "main", None)
    if not callable(main):
        raise ValueError(f"generator has no callable main(): {script_path}")
    signature = inspect.signature(main)
    if len(signature.parameters) == 0:
        return cast(Callable[[], None], main)
    return cast(Callable[[], None], lambda: cast(Callable[[list[str]], None], main)([]))


def _inspect_artifact(
    entry: GeneratedArtifactEntry,
    *,
    repo_root: Path,
    apply_normalization: bool,
) -> ArtifactGenerationStatus:
    artifact_path = repo_root / entry.artifact_path
    if not artifact_path.exists():
        return ArtifactGenerationStatus(
            artifact_path=entry.artifact_path,
            canonical_generator=entry.canonical_generator,
            canonical_schema=entry.canonical_schema,
            exists=False,
            final_status="MISSING_ARTIFACT",
            reasons=["artifact_missing_after_generation"],
        )

    original_text = artifact_path.read_text(encoding="utf-8")
    normalized_text, canonical_json_normalized, newline_normalized = _normalize_artifact_text(
        artifact_path,
        original_text,
    )
    drift_detected = normalized_text != original_text
    if apply_normalization and drift_detected:
        artifact_path.write_text(normalized_text, encoding="utf-8")

    reasons: list[str] = []
    if drift_detected:
        reasons.append("artifact_drift_detected")
    if not newline_normalized:
        reasons.append("newline_normalization_required")
    if artifact_path.suffix == ".json" and not canonical_json_normalized:
        reasons.append("canonical_json_normalization_required")

    final_status = "VALIDATED"
    if drift_detected and apply_normalization:
        final_status = "NORMALIZED"
    elif drift_detected:
        final_status = "DRIFT_DETECTED"

    return ArtifactGenerationStatus(
        artifact_path=entry.artifact_path,
        canonical_generator=entry.canonical_generator,
        canonical_schema=entry.canonical_schema,
        exists=True,
        content_hash=_stable_hash(original_text),
        normalized_hash=_stable_hash(normalized_text),
        drift_detected=drift_detected,
        canonical_json_normalized=canonical_json_normalized,
        newline_normalized=newline_normalized,
        final_status=final_status,
        reasons=reasons,
    )


def execute_artifact_regeneration(
    registry: GeneratedArtifactRegistry,
    *,
    repo_root: Path | str | None = None,
    selected_artifacts: list[str] | None = None,
    full: bool = False,
    validation_only: bool = False,
) -> ArtifactRegenerationPlan:
    root = _repo_root(repo_root)
    entries = resolve_regeneration_entries(
        registry,
        selected_artifacts=selected_artifacts,
        full=full,
    )
    plan = build_artifact_regeneration_plan(
        registry,
        selected_artifacts=selected_artifacts,
        full=full,
        validation_only=validation_only,
    )

    if not validation_only:
        previous_cwd = Path.cwd()
        os.chdir(root)
        try:
            for generator in plan.generator_sequence:
                generator_path = root / generator
                if not generator_path.exists():
                    raise FileNotFoundError(f"missing generator: {generator}")
                _load_generator_main(generator_path)()
        finally:
            os.chdir(previous_cwd)

    statuses = [
        _inspect_artifact(
            entry,
            repo_root=root,
            apply_normalization=not validation_only,
        )
        for entry in entries
    ]
    failures = [
        status
        for status in statuses
        if status.final_status in {"MISSING_ARTIFACT", "DRIFT_DETECTED"}
    ]
    return ArtifactRegenerationPlan(
        validation_only=validation_only,
        selected_artifacts=plan.selected_artifacts,
        generator_sequence=plan.generator_sequence,
        statuses=statuses,
        final_status="FAILED" if failures else "PASS",
    )


def build_artifact_regeneration_payload(
    registry: GeneratedArtifactRegistry,
    plan: ArtifactRegenerationPlan,
) -> dict[str, Any]:
    return {
        "schema": "ArtifactRegenerationReport.v1",
        "policy": GENERATED_ARTIFACT_POLICY_V1,
        "registry": registry.model_dump(),
        "plan": plan.model_dump(),
        "artifact_source_map": registry.artifact_source_map,
        "regeneration_capability": registry.regeneration_capability,
        "orphaned_artifacts": registry.orphaned_artifacts,
        "stale_artifact_tests": registry.stale_artifact_tests,
        "derived_vs_canonical_ratio": registry.derived_vs_canonical_ratio,
        "artifact_dependency_graph": [edge.model_dump() for edge in registry.dependency_edges],
        "downstream_impact_summary": registry.downstream_impact_summary,
        "final_status": "PASS" if plan.final_status == "PASS" else "FAILED",
        "advisory_only": True,
        "mutation_allowed": False,
        "authority_granted": False,
        "auto_execute": False,
        "auto_approve": False,
    }


def build_artifact_regeneration_markdown(
    registry: GeneratedArtifactRegistry,
    plan: ArtifactRegenerationPlan,
) -> str:
    lines = [
        "# Artifact Regeneration 001",
        "",
        f"- Final Status: `{plan.final_status}`",
        f"- Validation Only: `{plan.validation_only}`",
        f"- Managed Artifacts: `{registry.regeneration_capability['managed_artifact_count']}`",
        f"- Orphaned Artifacts: `{len(registry.orphaned_artifacts)}`",
        f"- Selected Artifacts: `{len(plan.selected_artifacts)}`",
        "",
        "## Generator Sequence",
    ]
    if plan.generator_sequence:
        lines.extend(f"- `{generator}`" for generator in plan.generator_sequence)
    else:
        lines.append("- None")
    lines.extend(["", "## Drift Summary"])
    drifted = [status for status in plan.statuses if status.drift_detected]
    if drifted:
        lines.extend(f"- `{status.artifact_path}`" for status in drifted)
    else:
        lines.append("- None")
    lines.extend(["", "## Stale Artifact Tests"])
    if registry.stale_artifact_tests:
        lines.extend(f"- `{test_path}`" for test_path in registry.stale_artifact_tests)
    else:
        lines.append("- None")
    return "\n".join(lines) + "\n"


def write_artifact_regeneration_outputs(
    registry: GeneratedArtifactRegistry,
    plan: ArtifactRegenerationPlan,
    *,
    repo_root: Path | str | None = None,
) -> tuple[Path, Path]:
    root = _repo_root(repo_root)
    json_path = root / "out/audit/artifact_regeneration_001.latest.json"
    markdown_path = root / "out/audit/artifact_regeneration_001.latest.md"
    write_canonical_json(json_path, build_artifact_regeneration_payload(registry, plan))
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(
        build_artifact_regeneration_markdown(registry, plan),
        encoding="utf-8",
    )
    return json_path, markdown_path
