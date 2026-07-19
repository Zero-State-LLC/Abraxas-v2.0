from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_phase1_operator_decision_evidence_collection_plan import (
    build_abx_codegen_phase1_operator_decision_evidence_collection_plan,
    render_abx_codegen_phase1_operator_decision_evidence_collection_plan_markdown,
    write_abx_codegen_phase1_operator_decision_evidence_collection_plan,
)
from core.canonical.json import canonical_hash
from scripts.codegen import run_abx_codegen_phase1_operator_decision_evidence_collection_plan

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_codegen_phase1_operator_decision_evidence_collection_plan_ready() -> None:
    first = build_abx_codegen_phase1_operator_decision_evidence_collection_plan(REPO_ROOT)
    second = build_abx_codegen_phase1_operator_decision_evidence_collection_plan(REPO_ROOT)

    assert first["plan_hash"] == second["plan_hash"]
    assert first["status"] == "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_PLAN_READY"
    assert first["source_review_ready"] is True
    assert first["evidence_collection_only"] is True
    assert first["recommended_default_decision"] == "HOLD_FOR_OPERATOR_REVIEW"
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_codegen_phase1_operator_decision_evidence_collection_plan_denies_authority() -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_plan(REPO_ROOT)

    assert packet["decision_record_created"] is False
    assert packet["authorization_record_created"] is False
    assert packet["authorization_record_lane_authorized"] is False
    assert packet["implementation_authorized"] is False
    assert packet["implementation_unblocked"] is False
    assert packet["shadow_replay_execution_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_phase1_operator_decision_evidence_collection_plan_groups_fields() -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_plan(REPO_ROOT)
    groups = {group["group_id"]: group for group in packet["evidence_bundle_groups"]}

    assert set(groups) == {
        "operator_identity",
        "operator_decision",
        "authority_acknowledgements",
        "provenance_evidence",
        "evidence_outputs",
    }
    assert "operator_id" in groups["operator_identity"]["required_fields"]
    assert "selected_decision" in groups["operator_decision"]["required_fields"]
    assert "reviewed_phase1_operator_decision_record_review_hash" in groups[
        "provenance_evidence"
    ]["required_fields"]
    assert "OPERATOR_DECISION_RECORD_CREATION" in packet["disallowed_follow_on_actions"]


def test_codegen_phase1_operator_decision_evidence_collection_plan_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_plan(tmp_path)

    assert packet["status"] == "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_PLAN_BLOCKED"
    assert packet["source_review_ready"] is False
    assert packet["source_review_hash"] == "NOT_COMPUTABLE"
    assert packet["decision_record_created"] is False
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["blockers"]


def test_codegen_phase1_operator_decision_evidence_collection_plan_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_plan(REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("plan_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads(
        (
            REPO_ROOT
            / "contracts/operator_review/"
            "abx_codegen_phase1_operator_decision_evidence_collection_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)


def test_codegen_phase1_operator_decision_evidence_collection_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_abx_codegen_phase1_operator_decision_evidence_collection_plan(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = (
        tmp_path
        / "out/operator_review/"
        "abx_codegen_phase1_operator_decision_evidence_collection_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_phase1_operator_decision_evidence_collection_plan.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["plan_hash"] == packet["plan_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_phase1_operator_decision_evidence_collection_plan_markdown() -> None:
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_plan(REPO_ROOT)
    markdown = render_abx_codegen_phase1_operator_decision_evidence_collection_plan_markdown(
        packet
    )

    assert markdown[0] == "# ABX Codegen Phase 1 Operator Decision Evidence Collection Plan"
    assert any("operator_identity" in line for line in markdown)
    assert any("reviewed_phase1_operator_decision_record_review_hash" in line for line in markdown)
