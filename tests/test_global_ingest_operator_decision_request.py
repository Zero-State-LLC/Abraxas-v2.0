from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.global_pipeline_doctrine_validation import (
    write_global_pipeline_doctrine_validation_artifacts,
)
from core.global_pipeline_gap_backlog import write_global_pipeline_gap_backlog
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
    assert packet["implementation_plan_ready"] is True
    assert packet["calibration_plan_ready"] is True
    assert packet["calibration_contract_plan_ready"] is True
    assert "core/oracle_signal.py" in packet["observed_paths"]
    assert "scripts/run_ingest_once.py" in packet["observed_paths"]
    assert "scripts/run_oracle_intake.py" in packet["observed_paths"]


def test_request_carries_hold_boundaries() -> None:
    packet = build_global_ingest_operator_decision_request()

    assert "CORE_ORACLE_SIGNAL_IMPLEMENTATION" in packet["blocked_actions"]
    assert "EXECUTION_AUTHORITY_GRANT" in packet["blocked_actions"]
    assert "HOLD" in packet["decision_options"]
    assert "APPROVE_SEPARATE_IMPLEMENTATION_SPEC" in packet["decision_options"]
    assert "review_oracle_signal_research_intake_receipt" in packet["required_operator_actions"]
    assert "review_oracle_signal_intake_boundary_implementation_plan" in packet["required_operator_actions"]
    assert "review_oracle_confidence_calibration_plan" in packet["required_operator_actions"]
    assert "review_oracle_confidence_calibration_contract_plan" in packet["required_operator_actions"]
    assert "review_global_ingest_operator_decision_evidence_collection_plan" in packet["required_operator_actions"]
    assert "review_global_ingest_operator_decision_evidence_collection_dry_run" in packet["required_operator_actions"]
    assert "review_global_ingest_operator_decision_evidence_collection_validation_plan" in packet["required_operator_actions"]
    assert "review_global_ingest_operator_decision_record_dry_run" in packet["required_operator_actions"]
    assert "review_global_ingest_operator_decision_record_validation_plan" in packet["required_operator_actions"]
    assert "review_global_ingest_operator_decision_record_validation_dry_run" in packet["required_operator_actions"]
    assert "review_global_ingest_operator_decision_record_approval_plan" in packet["required_operator_actions"]
    assert "review_global_ingest_operator_decision_evidence_collection_approval_plan" in packet["required_operator_actions"]
    assert "prepare_global_ingest_operator_decision_record_template" in packet["required_operator_actions"]
    assert any("global_ingest_operator_decision_record_template_001.latest.json" in path for path in packet["decision_record_template_candidates"])
    assert any("global_ingest_operator_decision_record_dry_run_001.latest.json" in path for path in packet["decision_record_dry_run_candidates"])
    assert any("global_ingest_operator_decision_record_validation_plan_001.latest.json" in path for path in packet["decision_record_validation_plan_candidates"])
    assert any("global_ingest_operator_decision_record_validation_dry_run_001.latest.json" in path for path in packet["decision_record_validation_dry_run_candidates"])
    assert any("global_ingest_operator_decision_record_approval_plan_001.latest.json" in path for path in packet["decision_record_approval_plan_candidates"])
    assert any("global_ingest_operator_decision_evidence_collection_plan_001.latest.json" in path for path in packet["decision_evidence_collection_plan_candidates"])
    assert any("global_ingest_operator_decision_evidence_collection_dry_run_001.latest.json" in path for path in packet["decision_evidence_collection_dry_run_candidates"])
    assert any("global_ingest_operator_decision_evidence_collection_validation_plan_001.latest.json" in path for path in packet["decision_evidence_collection_validation_plan_candidates"])
    assert any("global_ingest_operator_decision_evidence_collection_approval_plan_001.latest.json" in path for path in packet["decision_evidence_collection_approval_plan_candidates"])
    assert any("oracle_signal_intake_boundary_implementation_plan/latest.json" in path for path in packet["implementation_plan_candidates"])
    assert any("oracle_confidence_calibration_plan/latest.json" in path for path in packet["implementation_plan_candidates"])
    assert any("oracle_confidence_calibration_contract_plan/latest.json" in path for path in packet["implementation_plan_candidates"])


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


def test_request_id_remains_stable_across_doctrine_and_backlog_replay() -> None:
    initial = write_global_ingest_operator_decision_request()

    write_global_pipeline_doctrine_validation_artifacts()
    write_global_pipeline_gap_backlog()
    replayed = build_global_ingest_operator_decision_request()

    assert replayed["request_id"] == initial["request_id"]
