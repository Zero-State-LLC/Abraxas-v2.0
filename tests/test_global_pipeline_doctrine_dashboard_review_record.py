from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.global_pipeline_doctrine_dashboard_review_record import (
    build_global_pipeline_doctrine_dashboard_review_record,
    render_global_pipeline_doctrine_dashboard_review_record_markdown,
    write_global_pipeline_doctrine_dashboard_review_record,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "scripts/run_global_pipeline_doctrine_dashboard_review_record.py",
    "local_global_pipeline_doctrine_dashboard_review_record_runner",
)


def test_review_record_is_deterministic_and_review_only() -> None:
    first = build_global_pipeline_doctrine_dashboard_review_record()
    second = build_global_pipeline_doctrine_dashboard_review_record()

    assert first["record_hash"] == second["record_hash"]
    assert first["status"] == "GLOBAL_PIPELINE_DOCTRINE_DASHBOARD_REVIEW_ACCEPTED"
    assert first["selected_decision"] == "ACCEPT_REVIEW_EVIDENCE_ONLY"
    assert first["dashboard_review_accepted_as_reviewed_evidence"] is True
    assert first["doctrine_review_accepted_as_reviewed_evidence"] is True
    assert first["gap_backlog_accepted_as_reviewed_evidence"] is True
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_review_record_preserves_authority_locks() -> None:
    packet = build_global_pipeline_doctrine_dashboard_review_record()

    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["runtime_mutation_allowed"] is False
    assert packet["scheduler_mutation_allowed"] is False
    assert packet["ingest_runner_mutation_allowed"] is False
    assert packet["pipeline_or_route_mutation_allowed"] is False
    assert packet["queue_mutation_allowed"] is False
    assert packet["canon_mutation_allowed"] is False
    assert packet["forecast_weight_allowed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["safe_to_auto_continue"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_review_record_records_current_gap_counts() -> None:
    packet = build_global_pipeline_doctrine_dashboard_review_record()

    assert packet["observed_counts"]["missing_contract_count"] == 8
    assert packet["observed_counts"]["additive_shadow_contract_coverage_count"] == 1
    assert packet["observed_counts"]["missing_validation_count"] == 8
    assert packet["observed_counts"]["additive_shadow_validation_coverage_count"] == 1
    assert packet["observed_counts"]["gap_count"] == 9
    assert packet["observed_counts"]["blocked_count"] == 0


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    packet = write_global_pipeline_doctrine_dashboard_review_record(out_root=tmp_path)
    json_path = tmp_path / "out/operator_review/global_pipeline_doctrine_dashboard_review_record_001.latest.json"
    md_path = tmp_path / "out/operator_review/global_pipeline_doctrine_dashboard_review_record_001.latest.md"

    assert json_path.exists()
    assert md_path.exists()
    runner_packet = RUNNER.run(repo_root=".", out_root=tmp_path)
    assert runner_packet["record_hash"] == packet["record_hash"]

    schema = json.loads(
        Path("contracts/operator_review/global_pipeline_doctrine_dashboard_review_record.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    validate(packet, schema)
    markdown = render_global_pipeline_doctrine_dashboard_review_record_markdown(packet)
    assert markdown[0] == "# Global Pipeline Doctrine Dashboard Review Record"
    assert any("REQUEST_GLOBAL_INGEST_OPERATOR_DECISION" in line for line in markdown)


def test_registry_includes_review_record_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/operator_review/global_pipeline_doctrine_dashboard_review_record_001.latest.json" in (
        _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert "out/operator_review/global_pipeline_doctrine_dashboard_review_record_001.latest.md" in (
        _DERIVED_OPTIONAL_ARTIFACTS
    )
