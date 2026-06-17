from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_phase1_code_detail_plan import (
    build_abx_codegen_intelligence_spine_phase1_code_detail_plan,
    render_abx_codegen_intelligence_spine_phase1_code_detail_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_intelligence_spine_phase1_code_detail_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_phase1_code_detail_plan.v1.schema.json"
)


def test_codegen_phase1_code_detail_is_held_for_operator() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_code_detail_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["phase1_code_detail_plan_status"]
        == "ABX_CODEGEN_PHASE1_CODE_DETAIL_PLAN_HELD_FOR_OPERATOR"
    )
    assert packet["source_harness_implementation_roadmap_plan"]["source_ready"] is True
    assert packet["target_file"] == "core/codegen_shadow_replay_harness.py"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_phase1_planned_interfaces_are_blocked() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_code_detail_plan(
        repo_root=REPO_ROOT
    )

    assert [item["interface_name"] for item in packet["planned_interfaces"]] == [
        "run_codegen_shadow_replay",
        "_validate_proposal",
        "_build_replay_config",
        "_execute_replays",
        "_evaluate_proof_flags",
        "_determine_recommendation",
        "_build_receipt",
        "_build_error_receipt",
    ]
    assert all(
        item["interface_status"] == "BLOCKED_PENDING_OPERATOR_AUTHORIZATION"
        for item in packet["planned_interfaces"]
    )
    assert all(
        item["implementation_authorized"] is False for item in packet["planned_interfaces"]
    )


def test_codegen_phase1_receipt_and_promotion_are_not_authorized() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_code_detail_plan(
        repo_root=REPO_ROOT
    )
    recommendations = {item["recommendation"]: item for item in packet["draft_recommendation_values"]}

    assert "source_observed_timestamp" in [
        item["field"] for item in packet["draft_receipt_fields"]
    ]
    assert "timestamp" not in [item["field"] for item in packet["draft_receipt_fields"]]
    assert all(
        item["receipt_creation_authorized"] is False
        for item in packet["draft_receipt_fields"]
    )
    assert recommendations["PROMOTE_TO_CANARY"]["promotion_authorized"] is False
    assert recommendations["PROMOTE_TO_CANARY"]["routing_authorized"] is False


def test_codegen_phase1_next_steps_are_blocked_or_reference_only() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_code_detail_plan(
        repo_root=REPO_ROOT
    )

    assert all(item["authorized"] is False for item in packet["phase1_next_steps"])
    assert "core_codegen_shadow_replay_harness_write_denied" in packet["implementation_blockers"]
    assert "promotion_to_canary_denied" in packet["implementation_blockers"]


def test_codegen_phase1_code_detail_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_code_detail_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_phase1_code_detail_fails_closed_without_source(tmp_path: Path) -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_code_detail_plan(repo_root=tmp_path)

    assert packet["phase1_code_detail_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_harness_implementation_roadmap_plan"]["source_ready"] is False
    assert all(
        item["interface_status"] == "NOT_COMPUTABLE"
        for item in packet["planned_interfaces"]
    )


def test_codegen_phase1_code_detail_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_code_detail_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_phase1_code_detail_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_phase1_code_detail_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_phase1_code_detail_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_phase1_code_detail_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_phase1_code_detail_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_code_detail_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_phase1_code_detail_plan_markdown(
        packet
    )

    assert markdown[0] == "# ABX Codegen Intelligence Spine Phase 1 Code Detail Plan"
    assert any("run_codegen_shadow_replay" in line for line in markdown)
    assert any("promotion_to_canary_denied" in line for line in markdown)
