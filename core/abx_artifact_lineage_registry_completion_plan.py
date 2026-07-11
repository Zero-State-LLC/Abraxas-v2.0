from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxArtifactLineageRegistryCompletionPlan.v1"
PLAN_ID = "ABX_ARTIFACT_LINEAGE_REGISTRY_COMPLETION_PLAN_001"
DETERMINISTIC_GENERATED_AT = "2026-06-05T00:00:00Z"
SOURCE_BACKLOG = "ABX_NOT_COMPUTABLE_COMPLETION_BACKLOG_001"
SOURCE_RESEARCH_APPLICATION = "ABX_RESEARCH_COMPLETION_APPLICATION_001"
RECOMMENDED_NEXT_PLAN = "ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_001"
DOWNSTREAM = "NOT_COMPUTABLE"
OUT_JSON = "out/sync/abx_artifact_lineage_registry_completion_plan/latest.json"
OUT_MD = "out/sync/abx_artifact_lineage_registry_completion_plan/latest.md"

FORBIDDEN_ACTIONS = [
    "implement_runtime_execution",
    "promote_research_to_canon",
    "create_downstream_lanes",
    "mutate_governance",
    "authorize_operator_decisions",
    "infer_missing_artifacts_as_present",
    "treat_lineage_as_correctness_proof",
    "treat_calibrated_confidence_as_authorization",
    "delete_or_rewrite_existing_artifacts",
    "rename_runner_paths_without_operator_review",
]

REQUIRED_REPO_SCANS = [
    "core/generated_artifact_registry.py",
    "scripts/run_*.py",
    "scripts/run_*.py",
    "contracts/**/*.schema.json",
    "out/**/*.json",
    "out/**/*.md",
    "docs/**/*.md",
    "tests/test_*.py",
    "README.md",
    "AGENTS.md",
    "PLANS.md",
]

REQUIRED_REGISTRY_CHECKS = [
    "detect_artifacts_with_outputs_but_no_registry_entry",
    "detect_registry_entries_with_no_runner",
    "artifact_registry_runner_discovery_gap",
    "preserve_unresolved_cases_as_NOT_COMPUTABLE",
]

REQUIRED_RUNNER_CHECKS = [
    "detect_uppercase_Scripts_runner_discovery_gaps",
    "detect_registry_entries_with_no_runner",
    "detect_runner_paths_with_no_schema",
    "uppercase_scripts_runner_visibility",
]

REQUIRED_SCHEMA_CHECKS = [
    "detect_runner_paths_with_no_schema",
    "detect_schemas_with_no_tests",
    "detect_json_outputs_without_schema",
    "preserve_unresolved_cases_as_NOT_COMPUTABLE",
]

REQUIRED_OUTPUT_CHECKS = [
    "detect_markdown_outputs_without_json_pair",
    "detect_json_outputs_without_schema",
    "detect_generated_outputs_with_no_notion_surface",
    "dashboard_projection_traceability",
]

REQUIRED_TEST_CHECKS = [
    "detect_schemas_with_no_tests",
    "systemwide_integration_matrix_gaps",
    "missing_replay_repair_batch",
    "missing_artifact_repair_batch",
]

REQUIRED_DOCS_CHECKS = [
    "detect_docs_references_to_missing_artifacts",
    "orphaned_subsystem_status",
    "dashboard_projection_traceability",
    "preserve_unresolved_cases_as_NOT_COMPUTABLE",
]

REQUIRED_NOTION_MAPPING_CHECKS = [
    "detect_generated_outputs_with_no_notion_surface",
    "artifact_registry_runner_discovery_gap",
    "dashboard_projection_traceability",
    "preserve_unresolved_cases_as_NOT_COMPUTABLE",
]


def _research_sources() -> list[dict[str, Any]]:
    return [
        {
            "title": "Atlas: A Framework for ML Lifecycle Provenance & Transparency",
            "authors_if_known": "UNKNOWN",
            "source_type": "research_paper",
            "relevance": "artifact lineage, integrity metadata, transparency logs, provenance chains",
            "allowed_use": "research_basis_for_schema_and_plan_design",
            "forbidden_use": "proof_of_repo_completeness",
        },
        {
            "title": "PROV-ML / ML lifecycle provenance research",
            "authors_if_known": "UNKNOWN",
            "source_type": "research_family",
            "relevance": "lifecycle-aware provenance representation",
            "allowed_use": "research_basis_for_schema_and_plan_design",
            "forbidden_use": "proof_of_repo_completeness",
        },
        {
            "title": "Reproducible ML artifact lifecycle research",
            "authors_if_known": "UNKNOWN",
            "source_type": "research_family",
            "relevance": "dataset/feature/workflow/execution/asset traceability",
            "allowed_use": "research_basis_for_schema_and_plan_design",
            "forbidden_use": "proof_of_repo_completeness",
        },
    ]


def _target_not_computable_clusters() -> list[dict[str, Any]]:
    return [
        {
            "cluster_id": "runtime_spine_audit_aggregator",
            "cluster_status": "NOT_COMPUTABLE",
            "reason_for_not_computable": "artifact lineage between runtime spine surfaces and their producers is not yet enumerated in a single deterministic registry completion plan",
            "evidence_required_to_reduce": "explicit producer, schema, runner, output, and registry bindings for the runtime spine audit family",
            "proposed_completion_check": "detect_artifacts_with_outputs_but_no_registry_entry",
        },
        {
            "cluster_id": "missing_replay_repair_batch",
            "cluster_status": "NOT_COMPUTABLE",
            "reason_for_not_computable": "replay repair artifacts are not yet enumerated with explicit lineage and completion expectations",
            "evidence_required_to_reduce": "artifact lineage records linking replay repair artifacts to schemas, tests, and runners",
            "proposed_completion_check": "preserve_unresolved_cases_as_NOT_COMPUTABLE",
        },
        {
            "cluster_id": "missing_artifact_repair_batch",
            "cluster_status": "NOT_COMPUTABLE",
            "reason_for_not_computable": "repair batches exist as unresolved families without a deterministic registry completion map",
            "evidence_required_to_reduce": "registry-to-runner and output-to-schema traceability for artifact repair surfaces",
            "proposed_completion_check": "detect_registry_entries_with_no_runner",
        },
        {
            "cluster_id": "uppercase_scripts_runner_visibility",
            "cluster_status": "NOT_COMPUTABLE",
            "reason_for_not_computable": "case-sensitive runner visibility differs across local and GitHub environments",
            "evidence_required_to_reduce": "deterministic enumeration of scripts/run_*.py and scripts/run_*.py bindings",
            "proposed_completion_check": "detect_uppercase_Scripts_runner_discovery_gaps",
        },
        {
            "cluster_id": "systemwide_integration_matrix_gaps",
            "cluster_status": "NOT_COMPUTABLE",
            "reason_for_not_computable": "integration expectations are scattered and not yet attached to artifact families in one completion plan",
            "evidence_required_to_reduce": "family-level lineage records including tests and downstream consumers",
            "proposed_completion_check": "detect_schemas_with_no_tests",
        },
        {
            "cluster_id": "orphaned_subsystem_status",
            "cluster_status": "NOT_COMPUTABLE",
            "reason_for_not_computable": "some subsystem status surfaces may be referenced in docs without complete traceability to generated artifacts",
            "evidence_required_to_reduce": "docs-to-artifact lineage plus explicit notion surface mapping",
            "proposed_completion_check": "detect_docs_references_to_missing_artifacts",
        },
        {
            "cluster_id": "dashboard_projection_traceability",
            "cluster_status": "NOT_COMPUTABLE",
            "reason_for_not_computable": "projection and dashboard surfaces require a clearer producer/consumer lineage map before unresolved cases can be reduced safely",
            "evidence_required_to_reduce": "explicit projection packet lineage linking registry entries, runners, schemas, and notion surfaces",
            "proposed_completion_check": "detect_generated_outputs_with_no_notion_surface",
        },
        {
            "cluster_id": "artifact_registry_runner_discovery_gap",
            "cluster_status": "NOT_COMPUTABLE",
            "reason_for_not_computable": "registry entries and runner discovery rules are not yet reconciled for all advisory surfaces",
            "evidence_required_to_reduce": "deterministic artifact lineage records with registry presence and runner binding status",
            "proposed_completion_check": "detect_registry_entries_with_no_runner",
        },
    ]


def _artifact_lineage_record_shape() -> dict[str, Any]:
    return {
        "artifact_id": "string",
        "artifact_family": "string",
        "producer_module": "string",
        "runner_path": "string",
        "schema_path": "string",
        "output_json_path": "string",
        "output_md_path": "string",
        "registry_entry": ["PRESENT", "MISSING", "PARTIAL", "NOT_COMPUTABLE"],
        "parent_artifacts": ["string"],
        "child_artifacts": ["string"],
        "provenance_hash": "string",
        "drift_status": ["PASS", "DRIFT", "NOT_CHECKED", "NOT_COMPUTABLE"],
        "replay_status": ["REPLAYABLE", "NOT_REPLAYABLE", "NOT_CHECKED", "NOT_COMPUTABLE"],
        "notion_surface": ["PRESENT", "MISSING", "PARTIAL", "NOT_COMPUTABLE"],
        "not_computable_reason": "string",
    }


def _governance_locks() -> dict[str, Any]:
    return {
        "governance_status": "FROZEN",
        "canon_status": "ADVISORY_ONLY",
        "execution_authority": False,
        "canon_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "research_candidates_canonized": False,
        "downstream": DOWNSTREAM,
        "operator_review_required": True,
    }


def _not_computable_items() -> list[dict[str, Any]]:
    return [
        {
            "item_id": "ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_001",
            "status": "NOT_COMPUTABLE",
            "reason": "completion plan only; traceability audit is intentionally deferred to the recommended next plan",
        },
        {
            "item_id": "FULL_ARTIFACT_LINEAGE_RECONCILIATION",
            "status": "NOT_COMPUTABLE",
            "reason": "this patch defines the deterministic plan shape and required future scans, not the full reconciliation results",
        },
        {
            "item_id": "NOTION_SURFACE_COMPLETENESS_PROOF",
            "status": "NOT_COMPUTABLE",
            "reason": "Notion mappings are listed as required future checks and are not inferred as complete by this plan artifact",
        },
    ]


def build_abx_artifact_lineage_registry_completion_plan() -> dict[str, Any]:
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "source_backlog": SOURCE_BACKLOG,
        "source_research_application": SOURCE_RESEARCH_APPLICATION,
        "research_sources": _research_sources(),
        "target_not_computable_clusters": _target_not_computable_clusters(),
        "artifact_lineage_record_shape": _artifact_lineage_record_shape(),
        "required_repo_scans": REQUIRED_REPO_SCANS,
        "required_registry_checks": REQUIRED_REGISTRY_CHECKS,
        "required_runner_checks": REQUIRED_RUNNER_CHECKS,
        "required_schema_checks": REQUIRED_SCHEMA_CHECKS,
        "required_output_checks": REQUIRED_OUTPUT_CHECKS,
        "required_test_checks": REQUIRED_TEST_CHECKS,
        "required_docs_checks": REQUIRED_DOCS_CHECKS,
        "required_notion_mapping_checks": REQUIRED_NOTION_MAPPING_CHECKS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "governance_locks": _governance_locks(),
        "not_computable_items": _not_computable_items(),
        "recommended_next_plan": RECOMMENDED_NEXT_PLAN,
        "downstream": DOWNSTREAM,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "valid_for_execution": False,
    }
    return {**base, "packet_hash": canonical_hash(base)}


def render_markdown(plan: Mapping[str, Any]) -> str:
    lines = [
        "# ABX Artifact Lineage Registry Completion Plan",
        "",
        f"- `plan_id`: `{plan['plan_id']}`",
        f"- `generated_at`: `{plan['generated_at']}`",
        f"- `source_backlog`: `{plan['source_backlog']}`",
        f"- `source_research_application`: `{plan['source_research_application']}`",
        f"- `recommended_next_plan`: `{plan['recommended_next_plan']}`",
        f"- `downstream`: `{plan['downstream']}`",
        f"- `canon_status`: `{plan['governance_locks']['canon_status']}`",
        "",
        "## Target NOT_COMPUTABLE Clusters",
    ]
    for cluster in plan["target_not_computable_clusters"]:
        lines.append(
            f"- `{cluster['cluster_id']}`: `{cluster['cluster_status']}` via `{cluster['proposed_completion_check']}`"
        )
    lines.extend(["", "## Required Repo Scans"])
    for scan in plan["required_repo_scans"]:
        lines.append(f"- `{scan}`")
    lines.extend(["", "## Forbidden Actions"])
    for action in plan["forbidden_actions"]:
        lines.append(f"- `{action}`")
    lines.extend(["", "## Governance Locks"])
    for key, value in plan["governance_locks"].items():
        lines.append(f"- `{key}`: `{value}`")
    return "\n".join(lines) + "\n"


def write_abx_artifact_lineage_registry_completion_plan(
    json_path: Path,
    md_path: Path,
) -> dict[str, Any]:
    plan = build_abx_artifact_lineage_registry_completion_plan()
    write_canonical_json(json_path, plan)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(plan), encoding="utf-8")
    return plan
