from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.global_ingest_operator_decision_record_dry_run import (
    build_global_ingest_operator_decision_record_dry_run,
    render_global_ingest_operator_decision_record_dry_run_markdown,
    write_global_ingest_operator_decision_record_dry_run,
)
from core.global_ingest_operator_decision_record_template import (
    write_global_ingest_operator_decision_record_template,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "scripts/run_global_ingest_operator_decision_record_dry_run.py",
    "local_global_ingest_operator_decision_record_dry_run_runner",
)


def test_missing_source_fails_closed(tmp_path: Path) -> None:
    packet = build_global_ingest_operator_decision_record_dry_run(source_root=tmp_path)

    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["source_template_observed"] is False
    assert "source_template_missing_or_unreadable" in packet["validation_blockers"]
    assert packet["valid_for_execution"] is False


def test_dry_run_is_deterministic_and_fail_closed() -> None:
    first = build_global_ingest_operator_decision_record_dry_run()
    second = build_global_ingest_operator_decision_record_dry_run()

    assert first["dry_run_hash"] == second["dry_run_hash"]
    assert first["status"] == "GLOBAL_INGEST_OPERATOR_DECISION_RECORD_DRY_RUN_READY"
    assert first["advisory_only"] is True
    assert first["projection_only"] is True
    assert first["simulated_only"] is True
    assert first["execution_authority"] is False
    assert first["valid_for_execution"] is False


def test_dry_run_targets_template_and_hold_boundary() -> None:
    packet = build_global_ingest_operator_decision_record_dry_run()
    sim = packet["simulated_decision_record"]

    assert packet["target_pipeline_id"] == "oracle_signal"
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert sim["selected_decision"] == "HOLD"
    assert sim["implementation_authorized"] is False
    assert "out/sync/oracle_signal_research_intake_receipt/latest.json" in packet["source_review_artifacts"]
    assert "out/sync/oracle_confidence_calibration_plan/latest.json" in packet["source_review_artifacts"]
    assert "out/sync/oracle_confidence_calibration_contract_plan/latest.json" in packet["source_review_artifacts"]
    assert "operator_decision_not_attested" in packet["validation_blockers"]


def test_writer_and_runner_emit_json_and_markdown(tmp_path: Path) -> None:
    write_global_ingest_operator_decision_record_template(".", out_root=tmp_path)
    packet = write_global_ingest_operator_decision_record_dry_run(".", out_root=tmp_path)
    json_path = tmp_path / "out/operator_review/global_ingest_operator_decision_record_dry_run_001.latest.json"
    md_path = tmp_path / "out/operator_review/global_ingest_operator_decision_record_dry_run_001.latest.md"
    assert json_path.exists()
    assert md_path.exists()
    assert packet["dry_run_id"] == "global_ingest_operator_decision_record_dry_run_001"

    runner_packet = RUNNER.run(repo_root=".", out_root=tmp_path)
    assert runner_packet["dry_run_hash"] == packet["dry_run_hash"]


def test_schema_and_markdown_render() -> None:
    packet = build_global_ingest_operator_decision_record_dry_run()
    schema = json.loads(
        Path(
            "contracts/operator_review/global_ingest_operator_decision_record_dry_run.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_global_ingest_operator_decision_record_dry_run_markdown(packet)
    assert markdown[0] == "# Global Ingest Operator Decision Record Dry Run"
    assert any("operator_decision_not_attested" in line for line in markdown)


def test_registry_includes_dry_run_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/operator_review/global_ingest_operator_decision_record_dry_run_001.latest.json" in _DERIVED_OPTIONAL_ARTIFACTS
    assert "out/operator_review/global_ingest_operator_decision_record_dry_run_001.latest.md" in _DERIVED_OPTIONAL_ARTIFACTS
