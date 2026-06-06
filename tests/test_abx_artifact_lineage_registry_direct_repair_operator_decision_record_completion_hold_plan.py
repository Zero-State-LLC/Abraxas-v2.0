from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan import (
    build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan,
    render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan_markdown,
    write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan,
)
from core.abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_dry_run import (
    write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_dry_run,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan.py",
    "local_abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan_runner",
)


def test_missing_source_fails_closed(tmp_path: Path) -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan(
        source_root=tmp_path
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["source_final_approval_validation_dry_run_observed"] is False
    assert "source_final_approval_validation_dry_run_missing_or_unreadable" in packet["blockers"]
    assert packet["valid_for_execution"] is False


def test_completion_hold_plan_is_ready_and_fail_closed() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan()
    assert (
        packet["status"]
        == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_COMPLETION_HOLD_PLAN_EMITTED"
    )
    assert packet["completion_hold_active"] is True
    assert packet["repair_completion_recognized"] is False
    assert packet["operator_decision_required"] is True
    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_repair"] is False


def test_hold_reasons_are_present() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan()
    assert "FINAL_OPERATOR_DECISION_RECORD_MISSING" in packet["unresolved_hold_reasons"]
    assert "DIRECT_REPAIR_EXECUTION_AUTHORITY_REMAINS_DENIED" in packet["unresolved_hold_reasons"]


def test_schema_and_markdown_render() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan()
    schema = json.loads(
        Path(
            "contracts/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan_markdown(
        packet
    )
    assert markdown[0] == "# ABX Artifact Lineage Registry Direct Repair Operator Decision Record Completion Hold Plan"
    assert any("FINAL_OPERATOR_DECISION_RECORD_MISSING" in line for line in markdown)


def test_writer_and_runner_emit_outputs(tmp_path: Path) -> None:
    write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_dry_run(
        ".", out_root=tmp_path
    )
    packet = write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan(
        ".", out_root=tmp_path
    )
    json_path = (
        tmp_path
        / "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan_001.latest.json"
    )
    md_path = (
        tmp_path
        / "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan_001.latest.md"
    )
    assert json_path.exists()
    assert md_path.exists()
    runner_packet = RUNNER.run(repo_root=".", out_root=tmp_path)
    assert runner_packet["completion_hold_plan_hash"] == packet["completion_hold_plan_hash"]


def test_registry_includes_completion_hold_plan_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
