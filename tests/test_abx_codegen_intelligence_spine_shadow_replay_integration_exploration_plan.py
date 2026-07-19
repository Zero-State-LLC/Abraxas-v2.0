from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan import (
    build_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan,
    render_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts.codegen import run_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan.v1.schema.json"
)


def test_codegen_shadow_replay_integration_exploration_plan_is_held() -> None:
    packet = build_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["shadow_replay_integration_exploration_plan_status"]
        == "ABX_CODEGEN_SHADOW_REPLAY_INTEGRATION_EXPLORATION_PLAN_HELD_FOR_OPERATOR"
    )
    assert packet["source_self_improvement_boundary_policy_plan"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_shadow_replay_integration_maps_proposal_fields() -> None:
    packet = build_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan(
        repo_root=REPO_ROOT
    )

    mapping = {item["proposal_field"]: item for item in packet["proposal_to_harness_mapping"]}
    assert mapping["proposal_id"]["harness_input"] == "candidate_id"
    assert mapping["contract_deltas"]["mapping"] == "canonical_serialization_required"
    assert (
        mapping["risk_assessment.self_modification_risk"]["mapping"]
        == "forces_meta_gate_planning_path"
    )
    assert mapping["promotion_path"]["mapping"] == "canon_direct_path_forbidden"


def test_codegen_shadow_replay_constraints_do_not_authorize_execution() -> None:
    packet = build_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan(
        repo_root=REPO_ROOT
    )

    constraints = packet["replay_constraints"]
    assert constraints["minimum_run_count"] == 12
    assert constraints["no_network_required"] is True
    assert constraints["no_file_write_required"] is True
    assert constraints["constraint_enforcement_authorized"] is False
    assert constraints["deterministic_replay_execution_authorized"] is False


def test_codegen_shadow_replay_proof_flags_are_plan_only() -> None:
    packet = build_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan(
        repo_root=REPO_ROOT
    )

    assert "authority_lock_invariance_observed" in packet["proof_flag_plan"]["standard_flags"]
    assert "no_code_mutation_in_shadow_observed" in packet["proof_flag_plan"][
        "codegen_specific_flags"
    ]
    assert packet["proof_flag_plan"]["proof_flag_evaluation_authorized"] is False


def test_codegen_shadow_replay_status_rules_do_not_route() -> None:
    packet = build_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan(
        repo_root=REPO_ROOT
    )

    rules = {item["shadow_replay_status"]: item for item in packet["status_and_recommendation_rules"]}
    assert rules["REPLAY_FAIL_HASH_DIVERGENCE"]["recommendation"] == "BLOCK_REPLAY_FAILURE"
    assert rules["REPLAY_INCOMPLETE"]["recommendation"] == "HOLD_FOR_OPERATOR"
    assert rules["REPLAY_PASS_WITH_META_GATE_TRIGGER"]["recommendation"] == "HOLD_FOR_META_GATE"
    assert all(item["routing_authorized"] is False for item in rules.values())


def test_codegen_shadow_replay_integration_strategy_denies_outputs() -> None:
    packet = build_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan(
        repo_root=REPO_ROOT
    )

    strategy = packet["integration_strategy"]
    assert strategy["target_module"] == "core/codegen_shadow_replay_harness.py"
    assert strategy["reuse_p103_patterns"] is True
    assert strategy["shared_library_refactor_authorized"] is False
    assert strategy["target_module_creation_authorized"] is False
    assert strategy["shadow_improvement_receipt_creation_authorized"] is False
    assert strategy["operator_decision_record_attachment_authorized"] is False


def test_codegen_shadow_replay_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_shadow_replay_fails_closed_without_source(tmp_path: Path) -> None:
    packet = build_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan(
        repo_root=tmp_path
    )

    assert packet["shadow_replay_integration_exploration_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_self_improvement_boundary_policy_plan"]["source_ready"] is False
    assert all(
        item["planned_reuse_status"] == "NOT_COMPUTABLE"
        for item in packet["observed_p103_replay_patterns"]
    )


def test_codegen_shadow_replay_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_shadow_replay_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_shadow_replay_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan_markdown(
        packet
    )

    assert markdown[0] == "# ABX Codegen Intelligence Spine Shadow Replay Integration Exploration Plan"
    assert any("proposal_id -> candidate_id" in line for line in markdown)
    assert any("deterministic_replay_execution_denied" in line for line in markdown)
