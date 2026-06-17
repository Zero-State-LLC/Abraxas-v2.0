from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_phase1_operator_decision_evidence_collection_dry_run import (
    write_abx_codegen_phase1_operator_decision_evidence_collection_dry_run,
)
from core.abx_codegen_phase1_operator_decision_evidence_collection_validation_plan import (
    build_abx_codegen_phase1_operator_decision_evidence_collection_validation_plan,
    render_abx_codegen_phase1_operator_decision_evidence_collection_validation_plan_markdown,
    write_abx_codegen_phase1_operator_decision_evidence_collection_validation_plan,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_phase1_operator_decision_evidence_collection_validation_plan

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_codegen_phase1_operator_decision_evidence_collection_validation_plan_ready() -> None:
    first = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_plan(
        REPO_ROOT
    )
    second = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_plan(
        REPO_ROOT
    )

    assert first["validation_plan_hash"] == second["validation_plan_hash"]
    assert (
        first["status"]
        == "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_PLAN_READY"
    )
    assert first["source_dry_run_ready"] is True
    assert first["validation_blockers"] == []
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_codegen_phase1_operator_decision_evidence_collection_validation_plan_denies_authority() -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_plan(
        REPO_ROOT
    )

    assert packet["validation_plan_only"] is True
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
    assert all(check["passed"] is True for check in packet["authority_lock_checks"])


def test_codegen_phase1_operator_decision_evidence_collection_validation_plan_checks_bundle_shape() -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_plan(
        REPO_ROOT
    )
    checks = {check["group_id"]: check for check in packet["bundle_group_checks"]}

    assert set(checks) == {
        "operator_identity",
        "operator_decision",
        "authority_acknowledgements",
        "provenance_evidence",
        "evidence_outputs",
    }
    assert checks["operator_identity"]["attested"] is False
    assert checks["operator_identity"]["field_count"] == 4
    assert checks["operator_identity"]["missing_field_count"] == 4
    assert all(check["passed"] is True for check in packet["bundle_group_checks"])
    assert all(check["passed"] is True for check in packet["invariant_checks"])


def test_codegen_phase1_operator_decision_evidence_collection_validation_plan_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_plan(
        tmp_path
    )

    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["source_dry_run_observed"] is False
    assert packet["source_dry_run_ready"] is False
    assert "source_dry_run_missing_or_unreadable" in packet["blockers"]
    assert "source_dry_run_missing_or_not_ready" in packet["validation_blockers"]
    assert packet["valid_for_decision_record"] is False


def test_codegen_phase1_operator_decision_evidence_collection_validation_plan_blocks_mutated_source(
    tmp_path: Path,
) -> None:
    write_abx_codegen_phase1_operator_decision_evidence_collection_dry_run(
        REPO_ROOT,
        out_root=tmp_path,
    )
    dry_run_path = (
        tmp_path
        / "out/operator_review/"
        "abx_codegen_phase1_operator_decision_evidence_collection_dry_run_001.latest.json"
    )
    payload = json.loads(dry_run_path.read_text(encoding="utf-8"))
    payload["readiness_summary"]["groups_ready"] = 1
    dry_run_path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_plan(
        tmp_path
    )

    assert (
        packet["status"]
        == "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_PLAN_BLOCKED_BY_DRY_RUN"
    )
    assert "summary_groups_ready" in packet["validation_blockers"]


def test_codegen_phase1_operator_decision_evidence_collection_validation_plan_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_plan(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("validation_plan_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads(
        (
            REPO_ROOT
            / "contracts/operator_review/"
            "abx_codegen_phase1_operator_decision_evidence_collection_validation_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)


def test_codegen_phase1_operator_decision_evidence_collection_validation_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_abx_codegen_phase1_operator_decision_evidence_collection_validation_plan(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = (
        tmp_path
        / "out/operator_review/"
        "abx_codegen_phase1_operator_decision_evidence_collection_validation_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_phase1_operator_decision_evidence_collection_validation_plan.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["validation_plan_hash"] == packet["validation_plan_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_phase1_operator_decision_evidence_collection_validation_plan_markdown() -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_validation_plan(
        REPO_ROOT
    )
    markdown = (
        render_abx_codegen_phase1_operator_decision_evidence_collection_validation_plan_markdown(
            packet
        )
    )

    assert (
        markdown[0]
        == "# ABX Codegen Phase 1 Operator Decision Evidence Collection Validation Plan"
    )
    assert any("source_dry_run_ready" in line for line in markdown)
    assert any("Bundle Group Checks" in line for line in markdown)
