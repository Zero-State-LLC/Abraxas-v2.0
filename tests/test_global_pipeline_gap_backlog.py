from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.global_pipeline_gap_backlog import (
    build_global_pipeline_gap_backlog,
    render_global_pipeline_gap_backlog_markdown,
    write_global_pipeline_gap_backlog,
)


def test_backlog_is_deterministic_and_fail_closed() -> None:
    first = build_global_pipeline_gap_backlog()
    second = build_global_pipeline_gap_backlog()

    assert first["backlog_id"] == second["backlog_id"]
    assert first["schema_version"] == "GlobalPipelineGapBacklog.v1"
    assert first["status"] == "GLOBAL_PIPELINE_GAP_BACKLOG_EMITTED"
    assert first["advisory_only"] is True
    assert first["projection_only"] is True
    assert first["non_authoritative"] is True
    assert first["execution_authority"] is False
    assert first["recommended_next_state"] == "hold"
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert first["gap_count"] == 9


def test_oracle_signal_is_ranked_first_and_blocked() -> None:
    packet = build_global_pipeline_gap_backlog()
    first = packet["backlog_items"][0]

    assert first["pipeline_id"] == "oracle_signal"
    assert first["priority"] == "P0"
    assert first["queue_action"] == "SPEC_AUTHORING_APPROVED_IMPLEMENTATION_HELD"
    assert first["missing_contract"] is False
    assert first["missing_validation"] is False
    assert "contracts/oracle/oracle_signal_intake_receipt.v1.schema.json" in first["observed_paths"]
    assert "scripts/run_oracle_signal_intake_boundary.py" in first["observed_paths"]
    assert "core/oracle_signal.py" in first["missing_paths"]
    assert "IMPLEMENTATION_AUTHORITY_DENIED" in first["blocked_reasons"]
    assert "global_ingest_operator_decision_record_001" in first["required_inputs"]


def test_unobserved_subsystems_are_deferred_not_fabricated() -> None:
    packet = build_global_pipeline_gap_backlog()
    deferred = {item["pipeline_id"]: item for item in packet["backlog_items"] if item["completion_status"] == "DEFERRED"}

    assert "beatoven_psyfi_integration" in deferred
    assert deferred["beatoven_psyfi_integration"]["source_observed"] is False
    assert deferred["beatoven_psyfi_integration"]["queue_action"] == "DEFER_UNOBSERVED_SUBSYSTEM"


def test_writer_emits_json_and_markdown() -> None:
    packet = write_global_pipeline_gap_backlog()

    json_path = Path("out/operator_review/global_pipeline_gap_backlog_001.latest.json")
    md_path = Path("out/operator_review/global_pipeline_gap_backlog_001.latest.md")
    assert json_path.exists()
    assert md_path.exists()
    assert packet["gap_count"] == 9


def test_schema_and_markdown_render() -> None:
    packet = build_global_pipeline_gap_backlog()
    schema = json.loads(
        Path("contracts/operator_review/global_pipeline_gap_backlog.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    validate(packet, schema)
    markdown = render_global_pipeline_gap_backlog_markdown(packet)
    assert markdown[0] == "# Global Pipeline Gap Backlog"
    assert any("oracle_signal" in line for line in markdown)


def test_backlog_hashes_do_not_depend_on_downstream_doctrine_review() -> None:
    packet = build_global_pipeline_gap_backlog()

    assert "doctrine_proof" in packet["source_hashes"]
    assert "doctrine_review" not in packet["source_hashes"]
