from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run import (
    build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run,
    render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run_markdown,
    write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run,
)
from core.abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan import (
    write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run.py",
    "local_abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run_runner",
)


def test_missing_source_fails_closed(tmp_path: Path) -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run(source_root=tmp_path)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["source_plan_observed"] is False
    assert "source_plan_missing_or_unreadable" in packet["validation_blockers"]
    assert packet["valid_for_execution"] is False


def test_dry_run_is_deterministic_and_fail_closed() -> None:
    first = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run()
    second = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run()
    assert first["dry_run_hash"] == second["dry_run_hash"]
    assert first["status"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_DRY_RUN_READY"
    assert first["advisory_only"] is True
    assert first["projection_only"] is True
    assert first["simulated_only"] is True
    assert first["execution_authority"] is False
    assert first["valid_for_execution"] is False


def test_dry_run_targets_record_plan_and_hold_boundary() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run()
    sim = packet["simulated_decision_record"]
    assert packet["target_surface"] == "ABX Artifact Lineage Registry Direct Repair"
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert sim["selected_decision"] == "HOLD"
    assert sim["execution_authority"] is False
    assert "out/sync/abx_artifact_lineage_registry_direct_repair_completion_hold_plan/latest.json" in packet["source_review_artifacts"]
    assert "operator_decision_not_attested" in packet["validation_blockers"]


def test_writer_and_runner_emit_json_and_markdown(tmp_path: Path) -> None:
    write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan(".", out_root=tmp_path)
    packet = write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run(".", out_root=tmp_path)
    json_path = tmp_path / "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run_001.latest.json"
    md_path = tmp_path / "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run_001.latest.md"
    assert json_path.exists()
    assert md_path.exists()
    assert packet["dry_run_id"] == "abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run_001"
    runner_packet = RUNNER.run(repo_root=".", out_root=tmp_path)
    assert runner_packet["dry_run_hash"] == packet["dry_run_hash"]


def test_schema_and_markdown_render() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run()
    schema = json.loads(
        Path(
            "contracts/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run_markdown(packet)
    assert markdown[0] == "# ABX Artifact Lineage Registry Direct Repair Operator Decision Record Dry Run"
    assert any("operator_decision_not_attested" in line for line in markdown)


def test_registry_includes_dry_run_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run_001.latest.json" in _DERIVED_OPTIONAL_ARTIFACTS
    assert "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run_001.latest.md" in _DERIVED_OPTIONAL_ARTIFACTS
