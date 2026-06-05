from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.global_ingest_operator_decision_evidence_collection_approval_plan import (
    build_global_ingest_operator_decision_evidence_collection_approval_plan,
    render_global_ingest_operator_decision_evidence_collection_approval_plan_markdown,
    write_global_ingest_operator_decision_evidence_collection_approval_plan,
)
from core.global_ingest_operator_decision_evidence_collection_dry_run import (
    write_global_ingest_operator_decision_evidence_collection_dry_run,
)
from core.global_ingest_operator_decision_evidence_collection_plan import (
    write_global_ingest_operator_decision_evidence_collection_plan,
)
from core.global_ingest_operator_decision_evidence_collection_validation_dry_run import (
    write_global_ingest_operator_decision_evidence_collection_validation_dry_run,
)
from core.global_ingest_operator_decision_evidence_collection_validation_plan import (
    write_global_ingest_operator_decision_evidence_collection_validation_plan,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_global_ingest_operator_decision_evidence_collection_approval_plan.py",
    "local_global_ingest_operator_decision_evidence_collection_approval_plan_runner",
)


def _seed_ready_validation_dry_run(tmp_path: Path) -> None:
    write_global_ingest_operator_decision_evidence_collection_plan(".", out_root=tmp_path)
    write_global_ingest_operator_decision_evidence_collection_dry_run(".", out_root=tmp_path)
    write_global_ingest_operator_decision_evidence_collection_validation_plan(".", out_root=tmp_path)
    write_global_ingest_operator_decision_evidence_collection_validation_dry_run(".", out_root=tmp_path)


def test_missing_source_fails_closed(tmp_path: Path) -> None:
    packet = build_global_ingest_operator_decision_evidence_collection_approval_plan(
        source_root=tmp_path
    )
    assert packet["status"] == "NOT_COMPUTABLE"


def test_ready_source_produces_ready(tmp_path: Path) -> None:
    _seed_ready_validation_dry_run(tmp_path)
    packet = build_global_ingest_operator_decision_evidence_collection_approval_plan(
        source_root=tmp_path
    )
    assert (
        packet["status"]
        == "GLOBAL_INGEST_OPERATOR_DECISION_EVIDENCE_COLLECTION_APPROVAL_PLAN_READY"
    )
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["target_pipeline_id"] == "oracle_signal"
    assert "out/sync/oracle_signal_research_intake_receipt/latest.json" in packet["source_review_artifacts"]
    assert "out/sync/oracle_confidence_calibration_plan/latest.json" in packet["source_review_artifacts"]
    assert "out/sync/oracle_confidence_calibration_contract_plan/latest.json" in packet["source_review_artifacts"]


def test_not_ready_source_blocks(tmp_path: Path) -> None:
    _seed_ready_validation_dry_run(tmp_path)
    source_path = (
        tmp_path
        / "out/operator_review/global_ingest_operator_decision_evidence_collection_validation_dry_run_001.latest.json"
    )
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    payload["status"] = "NOT_COMPUTABLE"
    source_path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    packet = build_global_ingest_operator_decision_evidence_collection_approval_plan(
        source_root=tmp_path
    )
    assert (
        packet["status"]
        == "BLOCKED_BY_GLOBAL_INGEST_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_DRY_RUN"
    )


def test_failed_validation_blocks(tmp_path: Path) -> None:
    _seed_ready_validation_dry_run(tmp_path)
    source_path = (
        tmp_path
        / "out/operator_review/global_ingest_operator_decision_evidence_collection_validation_dry_run_001.latest.json"
    )
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    payload["validation_passed"] = False
    source_path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    packet = build_global_ingest_operator_decision_evidence_collection_approval_plan(
        source_root=tmp_path
    )
    assert (
        packet["status"]
        == "BLOCKED_BY_FAILED_GLOBAL_INGEST_EVIDENCE_COLLECTION_VALIDATION_DRY_RUN"
    )


def test_requirements_and_invariants_present(tmp_path: Path) -> None:
    _seed_ready_validation_dry_run(tmp_path)
    packet = build_global_ingest_operator_decision_evidence_collection_approval_plan(
        source_root=tmp_path
    )
    assert packet["required_operator_acknowledgements"]
    assert packet["required_operator_approval_fields"]
    assert packet["approval_constraints"]
    assert packet["approval_provenance_requirements"]
    assert packet["approval_hash_requirements"]
    assert packet["approval_granted"] is False
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False


def test_writer_and_runner_emit_json_and_markdown(tmp_path: Path) -> None:
    _seed_ready_validation_dry_run(tmp_path)
    packet = write_global_ingest_operator_decision_evidence_collection_approval_plan(
        tmp_path
    )
    json_path = (
        tmp_path
        / "out/operator_review/global_ingest_operator_decision_evidence_collection_approval_plan_001.latest.json"
    )
    md_path = (
        tmp_path
        / "out/operator_review/global_ingest_operator_decision_evidence_collection_approval_plan_001.latest.md"
    )
    assert json_path.exists()
    assert md_path.exists()
    assert (
        packet["approval_plan_id"]
        == "global_ingest_operator_decision_evidence_collection_approval_plan_001"
    )

    runner_packet = RUNNER.run(repo_root=tmp_path)
    assert runner_packet["approval_plan_hash"] == packet["approval_plan_hash"]


def test_schema_and_markdown_render(tmp_path: Path) -> None:
    _seed_ready_validation_dry_run(tmp_path)
    packet = build_global_ingest_operator_decision_evidence_collection_approval_plan(
        source_root=tmp_path
    )
    schema = json.loads(
        Path(
            "contracts/operator_review/global_ingest_operator_decision_evidence_collection_approval_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_global_ingest_operator_decision_evidence_collection_approval_plan_markdown(
        packet
    )
    assert markdown[0] == "# Global Ingest Operator Decision Evidence Collection Approval Plan"
    assert any("hold" in line for line in markdown)


def test_hash_stable(tmp_path: Path) -> None:
    _seed_ready_validation_dry_run(tmp_path)
    first = build_global_ingest_operator_decision_evidence_collection_approval_plan(
        source_root=tmp_path
    )
    second = build_global_ingest_operator_decision_evidence_collection_approval_plan(
        source_root=tmp_path
    )
    assert first["approval_plan_hash"] == second["approval_plan_hash"]


def test_registry_includes_approval_plan_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/global_ingest_operator_decision_evidence_collection_approval_plan_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/operator_review/global_ingest_operator_decision_evidence_collection_approval_plan_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
