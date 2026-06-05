from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.global_ingest_operator_decision_request import (
    build_global_ingest_operator_decision_request,
    render_global_ingest_operator_decision_request_markdown,
    write_global_ingest_operator_decision_request,
)


def test_request_is_deterministic_and_fail_closed() -> None:
    first = build_global_ingest_operator_decision_request()
    second = build_global_ingest_operator_decision_request()

    assert first["request_id"] == second["request_id"]
    assert first["schema_version"] == "GlobalIngestOperatorDecisionRequest.v1"
    assert first["status"] == "GLOBAL_INGEST_OPERATOR_DECISION_REQUEST_EMITTED"
    assert first["advisory_only"] is True
    assert first["projection_only"] is True
    assert first["non_authoritative"] is True
    assert first["execution_authority"] is False
    assert first["implementation_authorized"] is False
    assert first["recommended_decision"] == "HOLD"


def test_request_targets_oracle_signal_hold() -> None:
    packet = build_global_ingest_operator_decision_request()

    assert packet["target_pipeline_id"] == "oracle_signal"
    assert packet["decision_scope"] == "IMPLEMENTATION_SPEC_DECISION_REQUIRED"
    assert "core/oracle_signal.py" in packet["missing_paths"]
    assert "scripts/run_ingest_once.py" in packet["observed_paths"]
    assert "scripts/run_oracle_intake.py" in packet["observed_paths"]


def test_request_carries_hold_boundaries() -> None:
    packet = build_global_ingest_operator_decision_request()

    assert "CORE_ORACLE_SIGNAL_IMPLEMENTATION" in packet["blocked_actions"]
    assert "EXECUTION_AUTHORITY_GRANT" in packet["blocked_actions"]
    assert "HOLD" in packet["decision_options"]
    assert "APPROVE_SEPARATE_IMPLEMENTATION_SPEC" in packet["decision_options"]


def test_writer_emits_json_and_markdown() -> None:
    packet = write_global_ingest_operator_decision_request()

    json_path = Path("out/operator_review/global_ingest_operator_decision_request_001.latest.json")
    md_path = Path("out/operator_review/global_ingest_operator_decision_request_001.latest.md")
    assert json_path.exists()
    assert md_path.exists()
    assert packet["target_pipeline_id"] == "oracle_signal"


def test_schema_and_markdown_render() -> None:
    packet = build_global_ingest_operator_decision_request()
    schema = json.loads(
        Path("contracts/operator_review/global_ingest_operator_decision_request.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    validate(packet, schema)
    markdown = render_global_ingest_operator_decision_request_markdown(packet)
    assert markdown[0] == "# Global Ingest Operator Decision Request"
    assert any("oracle_signal" in line for line in markdown)
