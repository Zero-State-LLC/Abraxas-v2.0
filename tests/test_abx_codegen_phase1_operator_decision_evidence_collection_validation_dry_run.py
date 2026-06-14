from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_phase1_operator_decision_evidence_collection_dry_run import (
    write_abx_codegen_phase1_operator_decision_evidence_collection_dry_run,
)
from core.abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run import (
    build_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run,
    render_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_markdown,
    write_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run,
)
from core.abx_codegen_phase1_operator_decision_evidence_collection_validation_plan import (
    write_abx_codegen_phase1_operator_decision_evidence_collection_validation_plan,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run

REPO_ROOT = Path(__file__).resolve().parents[1]


def _seed_ready_validation_plan(tmp_path: Path) -> None:
    write_abx_codegen_phase1_operator_decision_evidence_collection_dry_run(
        REPO_ROOT,
        out_root=tmp_path,
    )
    write_abx_codegen_phase1_operator_decision_evidence_collection_validation_plan(
        tmp_path,
        out_root=tmp_path,
    )


def test_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_ready() -> None:
    first = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run(
        REPO_ROOT
    )
    second = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run(
        REPO_ROOT
    )

    assert first["validation_dry_run_hash"] == second["validation_dry_run_hash"]
    assert (
        first["status"]
        == "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_DRY_RUN_READY"
    )
    assert first["source_validation_plan_ready"] is True
    assert first["validation_passed"] is True
    assert first["validation_blockers"] == []
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert first["recommended_next_state"] == "hold"


def test_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_denies_authority() -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run(
        REPO_ROOT
    )

    assert packet["validation_dry_run_only"] is True
    assert packet["validation_only"] is True
    assert packet["operator_attestations_present"] is False
    assert packet["evidence_bundle_created"] is False
    assert packet["decision_record_created"] is False
    assert packet["authorization_record_created"] is False
    assert packet["authorization_record_lane_authorized"] is False
    assert packet["implementation_authorized"] is False
    assert packet["implementation_unblocked"] is False
    assert packet["shadow_replay_execution_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["valid_for_decision_record"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_replays_checks() -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run(
        REPO_ROOT
    )
    summary = packet["validation_result_summary"]

    assert packet["replayed_bundle_group_results"]
    assert packet["replayed_invariant_results"]
    assert packet["replayed_authority_lock_results"]
    assert packet["executed_validation_checks"]
    assert all(check["passed"] is True for check in packet["replayed_bundle_group_results"])
    assert all(check["passed"] is True for check in packet["replayed_invariant_results"])
    assert all(check["passed"] is True for check in packet["replayed_authority_lock_results"])
    assert all(check["passed"] is True for check in packet["executed_validation_checks"])
    assert summary["validation_passed"] is True
    assert summary["checks_failed"] == 0
    assert summary["checks_passed"] == summary["checks_total"]
    assert summary["valid_for_decision_record"] is False


def test_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run(
        tmp_path
    )

    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["source_validation_plan_observed"] is False
    assert packet["source_validation_plan_ready"] is False
    assert "source_validation_plan_missing_or_unreadable" in packet["blockers"]
    assert "source_validation_plan_missing_or_not_ready" in packet["validation_blockers"]
    assert packet["valid_for_decision_record"] is False


def test_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_blocks_not_ready_source(
    tmp_path: Path,
) -> None:
    _seed_ready_validation_plan(tmp_path)
    plan_path = (
        tmp_path
        / "out/operator_review/"
        "abx_codegen_phase1_operator_decision_evidence_collection_validation_plan_001.latest.json"
    )
    payload = json.loads(plan_path.read_text(encoding="utf-8"))
    payload["status"] = "NOT_COMPUTABLE"
    plan_path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run(
        tmp_path
    )

    assert (
        packet["status"]
        == "BLOCKED_BY_ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_PLAN"
    )


def test_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_blocks_mutated_source(
    tmp_path: Path,
) -> None:
    _seed_ready_validation_plan(tmp_path)
    plan_path = (
        tmp_path
        / "out/operator_review/"
        "abx_codegen_phase1_operator_decision_evidence_collection_validation_plan_001.latest.json"
    )
    payload = json.loads(plan_path.read_text(encoding="utf-8"))
    payload["valid_for_decision_record"] = True
    plan_path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run(
        tmp_path
    )

    assert (
        packet["status"]
        == "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_DRY_RUN_FAILED"
    )
    assert "source_validation_plan_authority_not_locked" in packet["validation_blockers"]
    assert packet["validation_passed"] is False


def test_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("validation_dry_run_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads(
        (
            REPO_ROOT
            / "contracts/operator_review/"
            "abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)


def test_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    _seed_ready_validation_plan(tmp_path)
    packet = write_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run(
        tmp_path,
        out_root=tmp_path,
    )
    out_json = (
        tmp_path
        / "out/operator_review/"
        "abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run.run(
        repo_root=tmp_path,
        out_root=tmp_path,
    )

    assert second["validation_dry_run_hash"] == packet["validation_dry_run_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_markdown() -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run(
        REPO_ROOT
    )
    markdown = (
        render_abx_codegen_phase1_operator_decision_evidence_collection_validation_dry_run_markdown(
            packet
        )
    )

    assert (
        markdown[0]
        == "# ABX Codegen Phase 1 Operator Decision Evidence Collection Validation Dry Run"
    )
    assert any("validation_passed" in line for line in markdown)
    assert any("Validation Result Summary" in line for line in markdown)
