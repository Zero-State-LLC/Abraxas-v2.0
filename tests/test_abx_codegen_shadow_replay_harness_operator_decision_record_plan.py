from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_shadow_replay_harness_operator_decision_record_plan import (
    build_abx_codegen_shadow_replay_harness_operator_decision_record_plan,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_shadow_replay_harness_operator_decision_record_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_shadow_replay_harness_operator_decision_record_plan.v1.schema.json"
)


def test_codegen_operator_decision_record_plan_is_advisory_only() -> None:
    packet = build_abx_codegen_shadow_replay_harness_operator_decision_record_plan(
        repo_root=REPO_ROOT
    )

    assert packet["artifact_type"] == "AbxCodegenShadowReplayHarnessOperatorDecisionRecordPlan.v1"
    assert (
        packet["operator_decision_record_plan_status"]
        == "ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_PLAN_READY"
    )
    assert packet["planned_record_type"] == "CodegenOperatorDecisionRecord.v1"
    assert packet["record_creation_authorized"] is False
    assert packet["operator_decision_attested"] is False
    assert packet["implementation_authorization_granted"] is False
    assert packet["decision_record_created"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert "decision_record_creation" in packet["blocked_actions"]
    assert "operator_decision_attestation" in packet["blocked_actions"]


def test_codegen_operator_decision_record_plan_maps_notion_template_fields() -> None:
    packet = build_abx_codegen_shadow_replay_harness_operator_decision_record_plan(
        repo_root=REPO_ROOT
    )

    fields = {field["field"] for field in packet["required_record_fields"]}
    assert "source_proposal_id" in fields
    assert "source_receipt_id" in fields
    assert "operator_decision" in fields
    assert "operator_attestation" in fields

    decisions = {decision["decision"] for decision in packet["allowed_decisions"]}
    assert decisions == {
        "APPROVE",
        "REJECT",
        "REQUEST_REFINEMENT",
        "ESCALATE_TO_META_GATE",
        "DEFER",
    }
    assert packet["meta_gate_requirements"]["codegen_spine_self_authorization_allowed"] is False
    assert (
        packet["meta_gate_requirements"][
            "meta_gate_authorization_record_required_after_positive_decision"
        ]
        is True
    )
    assert packet["operator_attestation_requirements"]["human_operator_required"] is True
    assert packet["operator_attestation_requirements"]["codex_or_spine_attestation_allowed"] is False


def test_codegen_operator_decision_record_plan_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_shadow_replay_harness_operator_decision_record_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_operator_decision_record_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_"
        "record_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_shadow_replay_harness_operator_decision_record_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_shadow_replay_harness_operator_decision_record_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
    assert first_md.startswith(
        "# ABX Codegen Shadow Replay Harness Operator Decision Record Plan\n"
    )
