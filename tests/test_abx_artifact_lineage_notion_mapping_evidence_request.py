from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_notion_mapping_evidence_request import (
    build_abx_artifact_lineage_notion_mapping_evidence_request,
    render_abx_artifact_lineage_notion_mapping_evidence_request_markdown,
    write_abx_artifact_lineage_notion_mapping_evidence_request,
)


def test_request_is_deterministic_and_fail_closed() -> None:
    first = build_abx_artifact_lineage_notion_mapping_evidence_request()
    second = build_abx_artifact_lineage_notion_mapping_evidence_request()

    assert first["request_hash"] == second["request_hash"]
    assert first["schema_version"] == "AbxArtifactLineageNotionMappingEvidenceRequest.v1"
    assert first["status"] == "ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_EVIDENCE_REQUEST_HELD"
    assert first["advisory_only"] is True
    assert first["projection_only"] is True
    assert first["non_authoritative"] is True
    assert first["notion_writeback_allowed"] is False
    assert first["notion_completeness_claim_allowed"] is False
    assert first["execution_authority"] is False
    assert first["safe_to_auto_continue"] is False


def test_request_targets_current_notion_mapping_gap() -> None:
    packet = build_abx_artifact_lineage_notion_mapping_evidence_request()

    assert packet["request_scope"] == "NOTION_MAPPING_EVIDENCE_COLLECTION_ONLY"
    assert packet["target_finding_id"] == "detect_generated_outputs_with_no_notion_surface"
    assert packet["target_status"] == "NOT_COMPUTABLE"
    assert packet["impacted_output_count"] == 30
    assert "out/sync/abx_artifact_lineage_registry_traceability_audit" in packet["impacted_outputs"]
    assert packet["source_traceability_audit"]["source_audit_ready"] is True


def test_request_preserves_evidence_and_writeback_boundaries() -> None:
    packet = build_abx_artifact_lineage_notion_mapping_evidence_request()

    assert "DETERMINISTIC_REPO_VISIBLE_NOTION_MAPPING_INDEX" in packet["accepted_evidence_routes"]
    assert "GOVERNED_EXTERNAL_EVIDENCE_IMPORT_RECEIPT" in packet["accepted_evidence_routes"]
    assert "AUTOMATED_WRITEBACK_WITHOUT_OPERATOR_AUTHORIZATION" in packet["rejected_evidence_routes"]
    assert "NOTION_WRITEBACK" in packet["blocked_actions"]
    assert "NOTION_MAPPING_COMPLETENESS_ASSERTION" in packet["blocked_actions"]
    assert packet["recommended_next_lane"] == "ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_EVIDENCE_COLLECTION_PLAN"
    assert packet["downstream_status"] == "HELD_FOR_EVIDENCE"


def test_writer_emits_json_and_markdown() -> None:
    packet = write_abx_artifact_lineage_notion_mapping_evidence_request()

    json_path = Path("out/operator_review/abx_artifact_lineage_notion_mapping_evidence_request_001.latest.json")
    md_path = Path("out/operator_review/abx_artifact_lineage_notion_mapping_evidence_request_001.latest.md")
    assert json_path.exists()
    assert md_path.exists()
    assert packet["impacted_output_count"] == 30


def test_schema_and_markdown_render() -> None:
    packet = build_abx_artifact_lineage_notion_mapping_evidence_request()
    schema = json.loads(
        Path("contracts/operator_review/abx_artifact_lineage_notion_mapping_evidence_request.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    validate(packet, schema)
    markdown = render_abx_artifact_lineage_notion_mapping_evidence_request_markdown(packet)
    assert markdown[0] == "# ABX Artifact Lineage Notion Mapping Evidence Request"
    assert any("NOTION_WRITEBACK" in line for line in markdown)
