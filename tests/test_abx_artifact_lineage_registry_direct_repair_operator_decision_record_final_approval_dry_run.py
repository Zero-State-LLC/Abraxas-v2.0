from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run import (
    build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run,
    render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run_markdown,
    write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run,
)
from core.abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_plan import (
    write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_plan,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "scripts/run_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run.py",
    "local_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run_runner",
)


def test_dry_run_id_and_source_are_exact() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run()
    assert (
        packet["dry_run_id"]
        == "abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run_001"
    )
    assert packet["source_final_approval_plan_observed"] is True
    assert packet["source_final_approval_plan_path"] == (
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_plan_001.latest.json"
    )


def test_final_approval_dry_run_is_ready_and_fail_closed() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run()
    assert (
        packet["status"]
        == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_FINAL_APPROVAL_DRY_RUN_READY"
    )
    assert packet["final_approval_ready"] is True
    assert packet["approval_granted"] is False
    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False


def test_simulated_final_approval_execution_stays_non_authoritative() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run()
    execution = packet["simulated_final_approval_execution"]
    assert execution["simulated_only"] is True
    assert execution["operator_input_required"] is True
    assert execution["final_approval_ready"] is True
    assert execution["approval_granted"] is False
    assert execution["implementation_authorized"] is False
    assert execution["execution_authority"] is False
    assert execution["final_approval_blockers"] == []


def test_schema_and_markdown_validation_pass() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run()
    schema = json.loads(
        Path(
            "contracts/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run_markdown(
        packet
    )
    assert "ABX Artifact Lineage Registry Direct Repair Operator Decision Record Final Approval Dry Run" in markdown[0]
    assert any("hold" in line for line in markdown)


def test_output_is_deterministic() -> None:
    first = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run()
    second = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run()
    assert first == second


def test_writer_and_runner_emit_outputs(tmp_path: Path) -> None:
    write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_plan(
        ".", out_root=tmp_path
    )
    packet = write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run(
        ".", out_root=tmp_path
    )
    json_path = (
        tmp_path
        / "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run_001.latest.json"
    )
    md_path = (
        tmp_path
        / "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run_001.latest.md"
    )
    assert json_path.exists()
    assert md_path.exists()
    runner_packet = RUNNER.run(repo_root=".", out_root=tmp_path)
    assert runner_packet["dry_run_hash"] == packet["dry_run_hash"]


def test_registry_includes_final_approval_dry_run_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
