from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.global_ingest_operator_decision_evidence_collection_dry_run import (
    write_global_ingest_operator_decision_evidence_collection_dry_run,
)
from core.global_ingest_operator_decision_evidence_collection_plan import (
    write_global_ingest_operator_decision_evidence_collection_plan,
)
from core.global_ingest_operator_decision_evidence_collection_validation_plan import (
    build_global_ingest_operator_decision_evidence_collection_validation_plan,
    render_global_ingest_operator_decision_evidence_collection_validation_plan_markdown,
    write_global_ingest_operator_decision_evidence_collection_validation_plan,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_global_ingest_operator_decision_evidence_collection_validation_plan.py",
    "local_global_ingest_operator_decision_evidence_collection_validation_plan_runner",
)


def test_missing_source_fails_closed(tmp_path: Path) -> None:
    packet = build_global_ingest_operator_decision_evidence_collection_validation_plan(
        source_root=tmp_path
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["source_dry_run_observed"] is False
    assert "source_dry_run_missing_or_unreadable" in packet["blockers"]


def test_ready_source_produces_validation_plan_ready() -> None:
    packet = build_global_ingest_operator_decision_evidence_collection_validation_plan()
    assert (
        packet["status"]
        == "GLOBAL_INGEST_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_PLAN_READY"
    )
    assert packet["target_pipeline_id"] == "oracle_signal"
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_not_ready_source_blocks(tmp_path: Path) -> None:
    write_global_ingest_operator_decision_evidence_collection_plan(".", out_root=tmp_path)
    dry_run_path = (
        tmp_path
        / "out/operator_review/global_ingest_operator_decision_evidence_collection_dry_run_001.latest.json"
    )
    dry_run_path.parent.mkdir(parents=True, exist_ok=True)
    dry_run_path.write_text(
        json.dumps(
            {
                "status": "NOT_COMPUTABLE",
                "target_pipeline_id": "oracle_signal",
                "decision_scope": "IMPLEMENTATION_SPEC_DECISION_REQUIRED",
                "simulated_evidence_bundle": [],
                "readiness_summary": {"simulated_only": False, "evaluation_blockers": ["missing"]},
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )
    packet = build_global_ingest_operator_decision_evidence_collection_validation_plan(
        source_root=tmp_path
    )
    assert (
        packet["status"]
        == "BLOCKED_BY_GLOBAL_INGEST_OPERATOR_DECISION_EVIDENCE_COLLECTION_DRY_RUN"
    )


def test_invariant_failure_blocks_plan(tmp_path: Path) -> None:
    write_global_ingest_operator_decision_evidence_collection_plan(".", out_root=tmp_path)
    write_global_ingest_operator_decision_evidence_collection_dry_run(".", out_root=tmp_path)
    dry_run_path = (
        tmp_path
        / "out/operator_review/global_ingest_operator_decision_evidence_collection_dry_run_001.latest.json"
    )
    payload = json.loads(dry_run_path.read_text(encoding="utf-8"))
    payload["readiness_summary"]["groups_ready"] = 1
    dry_run_path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    packet = build_global_ingest_operator_decision_evidence_collection_validation_plan(
        source_root=tmp_path
    )
    assert (
        packet["status"]
        == "GLOBAL_INGEST_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_PLAN_BLOCKED_BY_DRY_RUN"
    )
    assert "summary_groups_ready" in packet["validation_blockers"]


def test_writer_and_runner_emit_json_and_markdown(tmp_path: Path) -> None:
    write_global_ingest_operator_decision_evidence_collection_plan(".", out_root=tmp_path)
    write_global_ingest_operator_decision_evidence_collection_dry_run(".", out_root=tmp_path)
    packet = write_global_ingest_operator_decision_evidence_collection_validation_plan(
        ".", out_root=tmp_path
    )
    json_path = (
        tmp_path
        / "out/operator_review/global_ingest_operator_decision_evidence_collection_validation_plan_001.latest.json"
    )
    md_path = (
        tmp_path
        / "out/operator_review/global_ingest_operator_decision_evidence_collection_validation_plan_001.latest.md"
    )
    assert json_path.exists()
    assert md_path.exists()
    assert (
        packet["validation_plan_id"]
        == "global_ingest_operator_decision_evidence_collection_validation_plan_001"
    )
    runner_packet = RUNNER.run(repo_root=".", out_root=tmp_path)
    assert runner_packet["validation_plan_hash"] == packet["validation_plan_hash"]


def test_schema_and_markdown_render() -> None:
    packet = build_global_ingest_operator_decision_evidence_collection_validation_plan()
    schema = json.loads(
        Path(
            "contracts/operator_review/global_ingest_operator_decision_evidence_collection_validation_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_global_ingest_operator_decision_evidence_collection_validation_plan_markdown(
        packet
    )
    assert markdown[0] == "# Global Ingest Operator Decision Evidence Collection Validation Plan"
    assert any("hold" in line for line in markdown)


def test_hash_stable() -> None:
    first = build_global_ingest_operator_decision_evidence_collection_validation_plan()
    second = build_global_ingest_operator_decision_evidence_collection_validation_plan()
    assert first["validation_plan_hash"] == second["validation_plan_hash"]


def test_registry_includes_validation_plan_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/global_ingest_operator_decision_evidence_collection_validation_plan_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/operator_review/global_ingest_operator_decision_evidence_collection_validation_plan_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
