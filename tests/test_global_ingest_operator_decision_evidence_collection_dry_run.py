from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.global_ingest_operator_decision_evidence_collection_dry_run import (
    build_global_ingest_operator_decision_evidence_collection_dry_run,
    render_global_ingest_operator_decision_evidence_collection_dry_run_markdown,
    write_global_ingest_operator_decision_evidence_collection_dry_run,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_global_ingest_operator_decision_evidence_collection_dry_run.py",
    "local_global_ingest_operator_decision_evidence_collection_dry_run_runner",
)


def test_dry_run_is_deterministic_and_fail_closed() -> None:
    first = build_global_ingest_operator_decision_evidence_collection_dry_run()
    second = build_global_ingest_operator_decision_evidence_collection_dry_run()

    assert first["dry_run_hash"] == second["dry_run_hash"]
    assert (
        first["status"]
        == "GLOBAL_INGEST_OPERATOR_DECISION_EVIDENCE_COLLECTION_DRY_RUN_READY"
    )
    assert first["simulated_only"] is True
    assert first["valid_for_decision_record"] is False
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_dry_run_targets_oracle_signal_and_shows_missing_bundle() -> None:
    packet = build_global_ingest_operator_decision_evidence_collection_dry_run()

    assert packet["target_pipeline_id"] == "oracle_signal"
    assert packet["readiness_summary"]["groups_ready"] == 0
    assert packet["readiness_summary"]["evidence_bundle_complete"] is False
    assert "out/sync/oracle_signal_research_intake_receipt/latest.json" in packet["source_review_artifacts"]
    assert "out/sync/oracle_confidence_calibration_plan/latest.json" in packet["source_review_artifacts"]
    assert any(item["group_id"] == "decision" for item in packet["simulated_evidence_bundle"])


def test_writer_and_runner_emit_json_and_markdown(tmp_path: Path) -> None:
    packet = write_global_ingest_operator_decision_evidence_collection_dry_run(
        ".", out_root=tmp_path
    )

    json_path = (
        tmp_path
        / "out/operator_review/global_ingest_operator_decision_evidence_collection_dry_run_001.latest.json"
    )
    md_path = (
        tmp_path
        / "out/operator_review/global_ingest_operator_decision_evidence_collection_dry_run_001.latest.md"
    )
    assert json_path.exists()
    assert md_path.exists()
    assert packet["dry_run_id"] == "global_ingest_operator_decision_evidence_collection_dry_run_001"

    runner_packet = RUNNER.run(repo_root=".", out_root=tmp_path)
    assert runner_packet["dry_run_hash"] == packet["dry_run_hash"]


def test_schema_and_markdown_render() -> None:
    packet = build_global_ingest_operator_decision_evidence_collection_dry_run()
    schema = json.loads(
        Path(
            "contracts/operator_review/global_ingest_operator_decision_evidence_collection_dry_run.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_global_ingest_operator_decision_evidence_collection_dry_run_markdown(
        packet
    )
    assert markdown[0] == "# Global Ingest Operator Decision Evidence Collection Dry Run"
    assert any("oracle_signal" in line for line in markdown)


def test_registry_includes_dry_run_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/global_ingest_operator_decision_evidence_collection_dry_run_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/operator_review/global_ingest_operator_decision_evidence_collection_dry_run_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
