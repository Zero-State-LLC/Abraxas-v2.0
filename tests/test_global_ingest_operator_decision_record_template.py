from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.global_ingest_operator_decision_record_template import (
    build_global_ingest_operator_decision_record_template,
    render_global_ingest_operator_decision_record_template_markdown,
    write_global_ingest_operator_decision_record_template,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_global_ingest_operator_decision_record_template.py",
    "local_global_ingest_operator_decision_record_template_runner",
)


def test_template_is_deterministic_and_fail_closed() -> None:
    first = build_global_ingest_operator_decision_record_template()
    second = build_global_ingest_operator_decision_record_template()

    assert first["template_hash"] == second["template_hash"]
    assert first["status"] == "GLOBAL_INGEST_OPERATOR_DECISION_RECORD_TEMPLATE_READY"
    assert first["advisory_only"] is True
    assert first["projection_only"] is True
    assert first["non_authoritative"] is True
    assert first["execution_authority"] is False
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_template_targets_oracle_signal_decision_hold() -> None:
    packet = build_global_ingest_operator_decision_record_template()

    assert packet["target_pipeline_id"] == "oracle_signal"
    assert packet["recommended_default_decision"] == "HOLD"
    assert "selected_decision" in packet["required_decision_fields"]
    assert "execution_authority_denied_acknowledged" in packet["required_acknowledgement_fields"]
    assert "out/sync/oracle_signal_research_intake_receipt/latest.json" in packet["required_review_artifacts"]
    assert "out/sync/oracle_confidence_calibration_plan/latest.json" in packet["required_review_artifacts"]
    assert "out/sync/oracle_confidence_calibration_contract_plan/latest.json" in packet["required_review_artifacts"]


def test_writer_and_runner_emit_json_and_markdown(tmp_path: Path) -> None:
    packet = write_global_ingest_operator_decision_record_template(".", out_root=tmp_path)

    json_path = tmp_path / "out/operator_review/global_ingest_operator_decision_record_template_001.latest.json"
    md_path = tmp_path / "out/operator_review/global_ingest_operator_decision_record_template_001.latest.md"
    assert json_path.exists()
    assert md_path.exists()
    assert packet["template_id"] == "global_ingest_operator_decision_record_template_001"

    runner_packet = RUNNER.run(repo_root=".", out_root=tmp_path)
    assert runner_packet["template_hash"] == packet["template_hash"]


def test_schema_and_markdown_render() -> None:
    packet = build_global_ingest_operator_decision_record_template()
    schema = json.loads(
        Path(
            "contracts/operator_review/global_ingest_operator_decision_record_template.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_global_ingest_operator_decision_record_template_markdown(packet)
    assert markdown[0] == "# Global Ingest Operator Decision Record Template"
    assert any("oracle_signal" in line for line in markdown)


def test_registry_includes_template_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/operator_review/global_ingest_operator_decision_record_template_001.latest.json" in _DERIVED_OPTIONAL_ARTIFACTS
    assert "out/operator_review/global_ingest_operator_decision_record_template_001.latest.md" in _DERIVED_OPTIONAL_ARTIFACTS
