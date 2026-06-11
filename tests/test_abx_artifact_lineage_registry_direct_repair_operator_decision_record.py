from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_registry_direct_repair_operator_decision_record import (
    build_abx_artifact_lineage_registry_direct_repair_operator_decision_record,
    render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_markdown,
    write_abx_artifact_lineage_registry_direct_repair_operator_decision_record,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_artifact_lineage_registry_direct_repair_operator_decision_record.py",
    "local_abx_artifact_lineage_registry_direct_repair_operator_decision_record_runner",
)


def test_decision_record_is_deterministic_and_approves_spec_only() -> None:
    first = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record()
    second = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record()

    assert first["decision_record_hash"] == second["decision_record_hash"]
    assert (
        first["status"]
        == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_APPROVED_FOR_SEPARATE_EXECUTION_SPEC"
    )
    assert first["selected_decision"] == "AUTHORIZE_SEPARATE_DIRECT_REPAIR_EXECUTION_SPEC"
    assert first["approval_granted"] is True
    assert first["separate_execution_spec_authoring_approved"] is True
    assert first["completion_hold_active"] is False
    assert first["recommended_next_patch"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SEPARATE_EXECUTION_SPEC_PLAN"


def test_decision_record_keeps_repair_execution_denied() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record()

    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["runtime_mutation_allowed"] is False
    assert packet["canon_mutation_allowed"] is False
    assert packet["queue_mutation_allowed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_repair"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["safe_to_prepare_planning_pr"] is True
    assert "DIRECT_REGISTRY_COVERAGE_REPAIR_EXECUTION" in packet["blocked_actions"]
    assert "AUTHOR_SEPARATE_DIRECT_REPAIR_EXECUTION_SPEC" in packet["allowed_follow_on_actions"]
    assert "NOTION_MAPPING_EVIDENCE_REMAINS_NOT_COMPUTABLE" in packet["unresolved_hold_reasons"]


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    packet = write_abx_artifact_lineage_registry_direct_repair_operator_decision_record(".", out_root=tmp_path)
    json_path = tmp_path / "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_001.latest.json"
    md_path = tmp_path / "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_001.latest.md"

    assert json_path.exists()
    assert md_path.exists()
    runner_packet = RUNNER.run(repo_root=".", out_root=tmp_path)
    assert runner_packet["decision_record_hash"] == packet["decision_record_hash"]

    schema = json.loads(
        Path("contracts/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    validate(packet, schema)
    markdown = render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_markdown(packet)
    assert markdown[0] == "# ABX Artifact Lineage Registry Direct Repair Operator Decision Record"
    assert any("AUTHORIZE_SEPARATE_DIRECT_REPAIR_EXECUTION_SPEC" in line for line in markdown)


def test_registry_includes_decision_record_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
