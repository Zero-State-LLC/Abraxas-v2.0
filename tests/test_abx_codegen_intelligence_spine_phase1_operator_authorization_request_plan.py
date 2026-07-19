from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan import (
    build_abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan,
    render_abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts.codegen import (
    run_abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan.v1.schema.json"
)


def test_codegen_phase1_operator_request_plan_is_held() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["phase1_operator_authorization_request_plan_status"]
        == "ABX_CODEGEN_PHASE1_OPERATOR_AUTHORIZATION_REQUEST_PLAN_HELD_FOR_OPERATOR"
    )
    assert packet["source_phase1_boundary_review"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_phase1_operator_request_plan_scopes_requested_authorization() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan(
        repo_root=REPO_ROOT
    )

    scope = packet["authorization_request_scope"]
    assert scope["target_module"] == "core/codegen_shadow_replay_harness.py"
    assert scope["request_creates_authorization"] is False
    assert scope["request_creates_operator_decision_record"] is False
    assert scope["operator_attestation_present"] is False


def test_codegen_phase1_operator_request_plan_requires_human_decision_fields() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan(
        repo_root=REPO_ROOT
    )

    fields = {item["field"] for item in packet["required_operator_decision_fields"]}
    assert "operator_decision" in fields
    assert "human_rationale" in fields
    assert "operator_attestation" in fields

    decisions = {item["decision"]: item for item in packet["allowed_operator_decisions"]}
    assert "APPROVE_PHASE1_IMPLEMENTATION" in decisions
    assert all(
        item["grants_authority_in_this_artifact"] is False
        for item in decisions.values()
    )


def test_codegen_phase1_operator_request_plan_preserves_denials() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan(
        repo_root=REPO_ROOT
    )

    denials = {item["action"]: item for item in packet["explicit_denials"]}
    assert denials["operator_decision_record_creation"]["authorized"] is False
    assert denials["operator_attestation"]["authorized"] is False
    assert denials["phase1_implementation"]["authorized"] is False
    assert denials["shadow_replay_execution"]["authorized"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_phase1_operator_request_plan_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan(
        repo_root=tmp_path
    )

    assert packet["phase1_operator_authorization_request_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_phase1_boundary_review"]["source_ready"] is False
    assert all(
        item["field_status"] == "NOT_COMPUTABLE"
        for item in packet["required_operator_decision_fields"]
    )


def test_codegen_phase1_operator_request_plan_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_phase1_operator_request_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = (
        run_abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan.run(
            repo_root=REPO_ROOT,
            out_json=out_json,
            out_md=out_md,
        )
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = (
        run_abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan.run(
            repo_root=REPO_ROOT,
            out_json=out_json,
            out_md=out_md,
        )
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_phase1_operator_request_plan_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan(
        repo_root=REPO_ROOT
    )
    markdown = (
        render_abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan_markdown(
            packet
        )
    )

    assert (
        markdown[0]
        == "# ABX Codegen Intelligence Spine Phase 1 Operator Authorization Request Plan"
    )
    assert any("APPROVE_PHASE1_IMPLEMENTATION" in line for line in markdown)
    assert any("operator_attestation" in line for line in markdown)
