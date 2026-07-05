from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import validate

from core.abx_artifact_lineage_registry_direct_repair_operator_decision_request import (
    build_abx_artifact_lineage_registry_direct_repair_operator_decision_request,
    render_abx_artifact_lineage_registry_direct_repair_operator_decision_request_markdown,
    write_abx_artifact_lineage_registry_direct_repair_operator_decision_request,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_request_is_deterministic_and_fail_closed() -> None:
    first = build_abx_artifact_lineage_registry_direct_repair_operator_decision_request()
    second = build_abx_artifact_lineage_registry_direct_repair_operator_decision_request()

    assert first["request_id"] == second["request_id"]
    assert first["schema_version"] == "AbxArtifactLineageRegistryDirectRepairOperatorDecisionRequest.v1"
    assert first["status"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_REQUEST_EMITTED"
    assert first["advisory_only"] is True
    assert first["projection_only"] is True
    assert first["non_authoritative"] is True
    assert first["execution_authority"] is False
    assert first["implementation_authorized"] is False
    assert first["recommended_decision"] == "HOLD"


def test_request_targets_direct_repair_hold() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_request()

    assert packet["target_surface"] == "ABX Artifact Lineage Registry Direct Repair"
    assert packet["decision_scope"] == "DIRECT_REPAIR_EXECUTION_DECISION_REQUIRED"
    assert packet["target_plan_id"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_COMPLETION_HOLD_PLAN_001"
    assert packet["completion_hold_ready"] is True
    assert packet["validation_passed"] is True


def test_request_carries_hold_boundaries() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_request()

    assert "DIRECT_REGISTRY_COVERAGE_REPAIR_EXECUTION" in packet["blocked_actions"]
    assert "RUNNER_CASING_POLICY_OVERRIDE" in packet["blocked_actions"]
    assert "NOTION_MAPPING_COMPLETENESS_ASSERTION" in packet["blocked_actions"]
    assert "HOLD" in packet["decision_options"]
    assert "AUTHORIZE_SEPARATE_DIRECT_REPAIR_EXECUTION_SPEC" in packet["decision_options"]
    assert "FINAL_OPERATOR_DECISION_RECORD_MISSING" in packet["blocked_reasons"]
    assert "review_direct_repair_completion_hold_plan" in packet["required_operator_actions"]


def test_writer_emits_json_and_markdown(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    packet = write_abx_artifact_lineage_registry_direct_repair_operator_decision_request(
        source_root=REPO_ROOT
    )

    json_path = (
        tmp_path
        / "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_request_001.latest.json"
    )
    md_path = (
        tmp_path
        / "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_request_001.latest.md"
    )
    assert json_path.exists()
    assert md_path.exists()
    assert packet["target_plan_id"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_COMPLETION_HOLD_PLAN_001"


def test_schema_and_markdown_render() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_request()
    schema = json.loads(
        Path(
            "contracts/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_request.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_abx_artifact_lineage_registry_direct_repair_operator_decision_request_markdown(packet)
    assert markdown[0] == "# ABX Artifact Lineage Registry Direct Repair Operator Decision Request"
    assert any("FINAL_OPERATOR_DECISION_RECORD_MISSING" in line for line in markdown)


def test_request_id_remains_stable_across_replay() -> None:
    initial = build_abx_artifact_lineage_registry_direct_repair_operator_decision_request(
        source_root=REPO_ROOT
    )
    replayed = build_abx_artifact_lineage_registry_direct_repair_operator_decision_request()
    assert replayed["request_id"] == initial["request_id"]
