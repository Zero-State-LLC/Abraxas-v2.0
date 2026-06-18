from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_notion_mapping_scope_resolution_record import (
    build_abx_artifact_lineage_notion_mapping_scope_resolution_record,
    write_abx_artifact_lineage_notion_mapping_scope_resolution_record,
)
from core.abx_artifact_lineage_runner_casing_policy_decision_record import (
    build_abx_artifact_lineage_runner_casing_policy_decision_record,
    write_abx_artifact_lineage_runner_casing_policy_decision_record,
)


def test_notion_scope_resolution_record_is_deterministic_and_bounded() -> None:
    first = build_abx_artifact_lineage_notion_mapping_scope_resolution_record()
    second = build_abx_artifact_lineage_notion_mapping_scope_resolution_record()

    assert first["record_hash"] == second["record_hash"]
    assert first["status"] == "ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_SCOPE_RESOLUTION_RECORD_ACCEPTED"
    assert first["resolved_output_count"] == len(first["resolved_outputs"])
    assert "out/sync/v2_hygiene_loop_awareness_audit" in first["resolved_outputs"]
    assert "out/sync/v2_upgrade_completion_reconciliation" in first["resolved_outputs"]
    assert first["notion_writeback_allowed"] is False
    assert first["notion_completeness_claim_allowed"] is False
    assert first["external_notion_evidence_imported"] is False
    assert first["traceability_audit_consumption_allowed"] is True
    assert first["resolution_decision"] == "EXCLUDE_SYNC_OUTPUT_FAMILIES_FROM_MANDATORY_NOTION_SURFACE_MAPPING"


def test_runner_policy_decision_record_is_deterministic_and_bounded() -> None:
    first = build_abx_artifact_lineage_runner_casing_policy_decision_record()
    second = build_abx_artifact_lineage_runner_casing_policy_decision_record()

    assert first["record_hash"] == second["record_hash"]
    assert first["status"] == "ABX_ARTIFACT_LINEAGE_RUNNER_CASING_POLICY_DECISION_RECORD_ACCEPTED"
    assert first["resolved_runner_count"] == 478
    assert first["runner_path_normalization_allowed"] is False
    assert first["script_discovery_semantics_change_allowed"] is False
    assert first["traceability_audit_consumption_allowed"] is True
    assert first["policy_decision"] == "CASE_INSENSITIVE_BASENAME_EQUIVALENCE_FOR_AUDIT_DISCOVERY_ONLY"


def test_blocker_resolution_records_validate_against_schemas() -> None:
    notion = build_abx_artifact_lineage_notion_mapping_scope_resolution_record()
    runner = build_abx_artifact_lineage_runner_casing_policy_decision_record()
    notion_schema = json.loads(
        Path(
            "contracts/operator_review/abx_artifact_lineage_notion_mapping_scope_resolution_record.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    runner_schema = json.loads(
        Path("contracts/operator_review/abx_artifact_lineage_runner_casing_policy_decision_record.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )

    validate(notion, notion_schema)
    validate(runner, runner_schema)


def test_blocker_resolution_record_writers_emit_artifacts(tmp_path: Path) -> None:
    notion = write_abx_artifact_lineage_notion_mapping_scope_resolution_record(out_root=tmp_path)
    runner = write_abx_artifact_lineage_runner_casing_policy_decision_record(out_root=tmp_path)

    assert (
        tmp_path
        / "out/operator_review/abx_artifact_lineage_notion_mapping_scope_resolution_record_001.latest.json"
    ).exists()
    assert (
        tmp_path
        / "out/operator_review/abx_artifact_lineage_notion_mapping_scope_resolution_record_001.latest.md"
    ).exists()
    assert (
        tmp_path
        / "out/operator_review/abx_artifact_lineage_runner_casing_policy_decision_record_001.latest.json"
    ).exists()
    assert (
        tmp_path
        / "out/operator_review/abx_artifact_lineage_runner_casing_policy_decision_record_001.latest.md"
    ).exists()
    assert notion["downstream_status"] == "READY_FOR_TRACEABILITY_AUDIT_REPLAY"
    assert runner["downstream_status"] == "READY_FOR_TRACEABILITY_AUDIT_REPLAY"
