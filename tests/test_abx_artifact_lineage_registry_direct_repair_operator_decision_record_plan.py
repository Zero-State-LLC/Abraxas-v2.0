from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan import (
    build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan,
    render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan_markdown,
    write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan,
)


def test_plan_is_deterministic_and_fail_closed() -> None:
    first = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan()
    second = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan()

    assert first["decision_record_plan_hash"] == second["decision_record_plan_hash"]
    assert first["schema_version"] == "AbxArtifactLineageRegistryDirectRepairOperatorDecisionRecordPlan.v1"
    assert first["status"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_PLAN_READY"
    assert first["advisory_only"] is True
    assert first["projection_only"] is True
    assert first["non_authoritative"] is True
    assert first["execution_authority"] is False
    assert first["implementation_authorized"] is False
    assert first["recommended_default_decision"] == "HOLD"


def test_plan_targets_direct_repair_request() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan()
    assert packet["decision_scope"] == "DIRECT_REPAIR_EXECUTION_DECISION_REQUIRED"
    assert packet["target_surface"] == "ABX Artifact Lineage Registry Direct Repair"
    assert (
        packet["source_request_path"]
        == "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_operator_decision_request_001.latest.json"
    )


def test_plan_carries_required_fields() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan()
    assert "selected_decision" in packet["required_decision_fields"]
    assert "reviewed_request_id" in packet["required_evidence_fields"]
    assert any("operator_decision_record_001.latest.json" in item for item in packet["future_record_output_candidates"])
    assert (
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan_001.latest.json"
        in packet["required_review_artifacts"]
    )


def test_writer_emits_json_and_markdown() -> None:
    packet = write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan()
    json_path = Path("out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan_001.latest.json")
    md_path = Path("out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan_001.latest.md")
    assert json_path.exists()
    assert md_path.exists()
    assert packet["target_plan_id"] == "abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan_001"


def test_schema_and_markdown_render() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan()
    schema = json.loads(
        Path(
            "contracts/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan_markdown(packet)
    assert markdown[0] == "# ABX Artifact Lineage Registry Direct Repair Operator Decision Record Plan"
    assert any("selected_decision" in line for line in markdown)


def test_plan_hash_remains_stable_across_replay() -> None:
    initial = write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan()
    replayed = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan()
    assert replayed["decision_record_plan_hash"] == initial["decision_record_plan_hash"]
