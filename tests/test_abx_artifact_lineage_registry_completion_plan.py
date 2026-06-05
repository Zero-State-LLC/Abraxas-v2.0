from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_registry_completion_plan import (
    build_abx_artifact_lineage_registry_completion_plan,
    render_markdown,
    write_abx_artifact_lineage_registry_completion_plan,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_artifact_lineage_registry_completion_plan.py",
    "local_abx_artifact_lineage_registry_completion_plan_runner",
)


def test_plan_id_is_exact() -> None:
    packet = build_abx_artifact_lineage_registry_completion_plan()
    assert packet["plan_id"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_COMPLETION_PLAN_001"


def test_governance_locks_are_preserved() -> None:
    packet = build_abx_artifact_lineage_registry_completion_plan()
    locks = packet["governance_locks"]

    assert locks["governance_status"] == "FROZEN"
    assert locks["canon_status"] == "ADVISORY_ONLY"
    assert locks["execution_authority"] is False
    assert locks["canon_mutation_allowed"] is False
    assert locks["runtime_mutation_allowed"] is False
    assert locks["research_candidates_canonized"] is False
    assert packet["downstream"] == "NOT_COMPUTABLE"


def test_all_target_not_computable_clusters_are_present() -> None:
    packet = build_abx_artifact_lineage_registry_completion_plan()
    cluster_ids = {item["cluster_id"] for item in packet["target_not_computable_clusters"]}

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


def test_artifact_lineage_record_shape_includes_required_fields() -> None:
    packet = build_abx_artifact_lineage_registry_completion_plan()
    shape = packet["artifact_lineage_record_shape"]
    assert set(shape) == {
        "artifact_id",
        "artifact_family",
        "producer_module",
        "runner_path",
        "schema_path",
        "output_json_path",
        "output_md_path",
        "registry_entry",
        "parent_artifacts",
        "child_artifacts",
        "provenance_hash",
        "drift_status",
        "replay_status",
        "notion_surface",
        "not_computable_reason",
    }


def test_required_repo_scans_include_both_script_variants() -> None:
    packet = build_abx_artifact_lineage_registry_completion_plan()
    assert "scripts/run_*.py" in packet["required_repo_scans"]
    assert "Scripts/run_*.py" in packet["required_repo_scans"]


def test_forbidden_actions_include_required_guards() -> None:
    packet = build_abx_artifact_lineage_registry_completion_plan()
    actions = set(packet["forbidden_actions"])
    assert "infer_missing_artifacts_as_present" in actions
    assert "treat_lineage_as_correctness_proof" in actions
    assert "rename_runner_paths_without_operator_review" in actions


def test_markdown_render_includes_required_strings() -> None:
    packet = build_abx_artifact_lineage_registry_completion_plan()
    markdown = render_markdown(packet)
    assert "ABX_ARTIFACT_LINEAGE_REGISTRY_COMPLETION_PLAN_001" in markdown
    assert "NOT_COMPUTABLE" in markdown
    assert "ADVISORY_ONLY" in markdown


def test_schema_validation_passes() -> None:
    packet = build_abx_artifact_lineage_registry_completion_plan()
    schema = json.loads(
        Path(
            "contracts/canon/abx_artifact_lineage_registry_completion_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)


def test_output_is_deterministic() -> None:
    first = build_abx_artifact_lineage_registry_completion_plan()
    second = build_abx_artifact_lineage_registry_completion_plan()
    assert first == second


def test_writer_and_runner_emit_outputs(tmp_path: Path) -> None:
    json_path = tmp_path / "out/sync/abx_artifact_lineage_registry_completion_plan/latest.json"
    md_path = tmp_path / "out/sync/abx_artifact_lineage_registry_completion_plan/latest.md"
    packet = write_abx_artifact_lineage_registry_completion_plan(json_path, md_path)

    assert json_path.exists()
    assert md_path.exists()
    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_json=json_path, out_md=md_path)
    assert runner_packet["packet_hash"] == packet["packet_hash"]
