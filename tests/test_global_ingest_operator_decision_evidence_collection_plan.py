from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.global_ingest_operator_decision_evidence_collection_plan import (
    build_global_ingest_operator_decision_evidence_collection_plan,
    render_global_ingest_operator_decision_evidence_collection_plan_markdown,
    write_global_ingest_operator_decision_evidence_collection_plan,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_global_ingest_operator_decision_evidence_collection_plan.py",
    "local_global_ingest_operator_decision_evidence_collection_plan_runner",
)


def test_plan_is_deterministic_and_fail_closed() -> None:
    first = build_global_ingest_operator_decision_evidence_collection_plan()
    second = build_global_ingest_operator_decision_evidence_collection_plan()

    assert first["plan_hash"] == second["plan_hash"]
    assert first["status"] == "GLOBAL_INGEST_OPERATOR_DECISION_EVIDENCE_COLLECTION_PLAN_READY"
    assert first["advisory_only"] is True
    assert first["projection_only"] is True
    assert first["non_authoritative"] is True
    assert first["implementation_authorized"] is False
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_plan_targets_oracle_signal_hold_with_required_groups() -> None:
    packet = build_global_ingest_operator_decision_evidence_collection_plan()

    assert packet["target_pipeline_id"] == "oracle_signal"
    assert packet["recommended_default_decision"] == "HOLD"
    assert any(
        group["group_id"] == "provenance_evidence" for group in packet["evidence_bundle_groups"]
    )
    assert any(
        "out/sync/oracle_signal_intake_boundary_implementation_plan/latest.json" == path
        for path in packet["required_review_artifacts"]
    )
    assert any(
        "out/sync/oracle_confidence_calibration_plan/latest.json" == path
        for path in packet["required_review_artifacts"]
    )
    assert any(
        "out/sync/oracle_confidence_calibration_contract_plan/latest.json" == path
        for path in packet["required_review_artifacts"]
    )
    assert any(
        "out/sync/oracle_signal_research_intake_receipt/latest.json" == path
        for path in packet["required_review_artifacts"]
    )


def test_writer_and_runner_emit_json_and_markdown(tmp_path: Path) -> None:
    packet = write_global_ingest_operator_decision_evidence_collection_plan(".", out_root=tmp_path)

    json_path = (
        tmp_path
        / "out/operator_review/global_ingest_operator_decision_evidence_collection_plan_001.latest.json"
    )
    md_path = (
        tmp_path
        / "out/operator_review/global_ingest_operator_decision_evidence_collection_plan_001.latest.md"
    )
    assert json_path.exists()
    assert md_path.exists()
    assert packet["plan_id"] == "global_ingest_operator_decision_evidence_collection_plan_001"

    runner_packet = RUNNER.run(repo_root=".", out_root=tmp_path)
    assert runner_packet["plan_hash"] == packet["plan_hash"]


def test_schema_and_markdown_render() -> None:
    packet = build_global_ingest_operator_decision_evidence_collection_plan()
    schema = json.loads(
        Path(
            "contracts/operator_review/global_ingest_operator_decision_evidence_collection_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_global_ingest_operator_decision_evidence_collection_plan_markdown(packet)
    assert markdown[0] == "# Global Ingest Operator Decision Evidence Collection Plan"
    assert any("oracle_signal" in line for line in markdown)


def test_registry_includes_plan_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/global_ingest_operator_decision_evidence_collection_plan_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/operator_review/global_ingest_operator_decision_evidence_collection_plan_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
