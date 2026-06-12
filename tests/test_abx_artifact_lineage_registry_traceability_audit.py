from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_registry_traceability_audit import (
    build_abx_artifact_lineage_registry_traceability_audit,
    render_markdown,
    write_abx_artifact_lineage_registry_traceability_audit,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_artifact_lineage_registry_traceability_audit.py",
    "local_abx_artifact_lineage_registry_traceability_audit_runner",
)


def test_audit_id_and_source_plan_are_exact() -> None:
    packet = build_abx_artifact_lineage_registry_traceability_audit()
    assert packet["audit_id"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_001"
    assert packet["source_completion_plan"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_COMPLETION_PLAN_001"
    assert packet["source_completion_plan_observed"] is True


def test_governance_locks_are_preserved() -> None:
    packet = build_abx_artifact_lineage_registry_traceability_audit()
    locks = packet["governance_locks"]
    assert locks["governance_status"] == "FROZEN"
    assert locks["canon_status"] == "ADVISORY_ONLY"
    assert locks["execution_authority"] is False
    assert locks["canon_mutation_allowed"] is False
    assert locks["runtime_mutation_allowed"] is False
    assert locks["research_candidates_canonized"] is False
    assert packet["downstream"] == "NOT_COMPUTABLE"


def test_required_findings_are_present() -> None:
    packet = build_abx_artifact_lineage_registry_traceability_audit()
    finding_ids = {
        finding["finding_id"]
        for section in (
            "registry_findings",
            "runner_findings",
            "schema_findings",
            "output_findings",
            "docs_findings",
            "notion_mapping_findings",
        )
        for finding in packet[section]
    }
    assert {
        "detect_uppercase_Scripts_runner_discovery_gaps",
        "detect_artifacts_with_outputs_but_no_registry_entry",
        "detect_registry_entries_with_no_runner",
        "detect_runner_paths_with_no_schema",
        "detect_schemas_with_no_tests",
        "detect_generated_outputs_with_no_notion_surface",
        "detect_markdown_outputs_without_json_pair",
        "detect_json_outputs_without_schema",
        "detect_docs_references_to_missing_artifacts",
    }.issubset(finding_ids)


def test_uppercase_runner_gap_and_notion_mapping_are_resolved_by_records() -> None:
    packet = build_abx_artifact_lineage_registry_traceability_audit()
    runner_statuses = {finding["finding_id"]: finding["status"] for finding in packet["runner_findings"]}
    notion_statuses = {finding["finding_id"]: finding["status"] for finding in packet["notion_mapping_findings"]}
    assert runner_statuses["detect_uppercase_Scripts_runner_discovery_gaps"] == "PASS"
    assert notion_statuses["detect_generated_outputs_with_no_notion_surface"] == "PASS"
    assert packet["runner_casing_policy_decision"]["record_observed"] is True
    assert packet["notion_mapping_scope_resolution"]["record_observed"] is True
    assert packet["runner_casing_policy_decision"]["runner_path_normalization_allowed"] is False
    assert packet["notion_mapping_scope_resolution"]["notion_completeness_claim_allowed"] is False


def test_target_cluster_results_cover_all_completion_plan_clusters() -> None:
    packet = build_abx_artifact_lineage_registry_traceability_audit()
    cluster_ids = {item["cluster_id"] for item in packet["target_cluster_results"]}
    assert cluster_ids == {
        "runtime_spine_audit_aggregator",
        "missing_replay_repair_batch",
        "missing_artifact_repair_batch",
        "uppercase_scripts_runner_visibility",
        "systemwide_integration_matrix_gaps",
        "orphaned_subsystem_status",
        "dashboard_projection_traceability",
        "artifact_registry_runner_discovery_gap",
    }


def test_resolved_artifact_lineage_clusters_follow_supporting_findings() -> None:
    packet = build_abx_artifact_lineage_registry_traceability_audit()
    clusters = {item["cluster_id"]: item for item in packet["target_cluster_results"]}

    assert clusters["runtime_spine_audit_aggregator"]["cluster_status"] == "PASS"
    assert clusters["missing_artifact_repair_batch"]["cluster_status"] == "PASS"
    assert clusters["missing_replay_repair_batch"]["cluster_status"] == "NOT_COMPUTABLE"
    assert packet["downstream"] == "NOT_COMPUTABLE"


def test_markdown_and_schema_validation_pass() -> None:
    packet = build_abx_artifact_lineage_registry_traceability_audit()
    schema = json.loads(
        Path(
            "contracts/canon/abx_artifact_lineage_registry_traceability_audit.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_markdown(packet)
    assert "ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_001" in markdown
    assert "NOT_COMPUTABLE" in markdown
    assert "ABX_ARTIFACT_LINEAGE_REGISTRY_REPAIR_PLAN_001" in markdown


def test_output_is_deterministic() -> None:
    first = build_abx_artifact_lineage_registry_traceability_audit()
    second = build_abx_artifact_lineage_registry_traceability_audit()
    assert first == second


def test_writer_and_runner_emit_outputs(tmp_path: Path) -> None:
    json_path = tmp_path / "out/sync/abx_artifact_lineage_registry_traceability_audit/latest.json"
    md_path = tmp_path / "out/sync/abx_artifact_lineage_registry_traceability_audit/latest.md"
    packet = write_abx_artifact_lineage_registry_traceability_audit(json_path, md_path)
    assert json_path.exists()
    assert md_path.exists()
    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_json=json_path, out_md=md_path)
    assert runner_packet["packet_hash"] == packet["packet_hash"]
