from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan import (
    build_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan,
    render_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts.codegen import (
    run_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan.v1.schema.json"
)


def test_codegen_improvement_proposal_wiring_spec_plan_is_held() -> None:
    packet = build_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["wiring_spec_plan_status"]
        == "ABX_CODEGEN_IMPROVEMENT_PROPOSAL_SHADOW_REPLAY_WIRING_SPEC_PLAN_HELD_FOR_OPERATOR"
    )
    assert packet["source_shadow_replay_integration_exploration_plan"]["source_ready"] is True
    assert packet["source_phase1_operator_review_request"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_improvement_proposal_wiring_maps_required_inputs() -> None:
    packet = build_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan(
        repo_root=REPO_ROOT
    )

    mapping = {item["proposal_field"]: item for item in packet["input_mapping"]}
    assert mapping["proposal_id"]["harness_input"] == "candidate_id"
    assert mapping["contract_deltas"]["transformation"] == "canonical_serialization_required"
    assert (
        mapping["risk_assessment.self_modification_risk"]["transformation"]
        == "forces_hold_for_meta_gate_planning_path"
    )
    assert mapping["promotion_path"]["transformation"] == "direct_canon_path_forbidden"
    assert mapping["provenance"]["harness_input"] == "provenance_chain"


def test_codegen_improvement_proposal_wiring_denies_replay_and_receipts() -> None:
    packet = build_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan(
        repo_root=REPO_ROOT
    )

    steps = {item["step"]: item["step_status"] for item in packet["processing_steps"]}
    assert steps["execute_deterministic_replays"] == "NOT_AUTHORIZED"
    assert steps["compute_replay_hashes"] == "NOT_AUTHORIZED"
    assert packet["authority_locks"]["deterministic_replay_execution"] is False
    assert packet["authority_locks"]["receipt_creation"] is False
    assert packet["authority_locks"]["target_harness_module_creation"] is False


def test_codegen_improvement_proposal_wiring_output_mapping_uses_deterministic_ids() -> None:
    packet = build_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan(
        repo_root=REPO_ROOT
    )

    output = {item["receipt_field"]: item for item in packet["output_mapping"]}
    assert output["receipt_id"]["mapping"] == "deterministic_hash_template_no_timestamp_generation"
    assert (
        output["shadow_run_id"]["mapping"]
        == "deterministic_source_observed_identifier_required"
    )
    assert output["recommendation"]["mapping"] == "expanded_hold_block_recommendation_enum"


def test_codegen_improvement_proposal_wiring_recommendations_do_not_route() -> None:
    packet = build_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan(
        repo_root=REPO_ROOT
    )

    rules = {item["replay_condition"]: item for item in packet["recommendation_rules"]}
    assert rules["self_modification_flag_true"]["recommendation"] == "HOLD_FOR_META_GATE"
    assert rules["policy_boundary_violation"]["recommendation"] == "BLOCK_POLICY_VIOLATION"
    assert (
        rules["hash_divergence_or_missing_required_proofs"]["recommendation"]
        == "BLOCK_REPLAY_FAILURE"
    )
    assert all(item["routing_authorized"] is False for item in rules.values())


def test_codegen_improvement_proposal_wiring_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_improvement_proposal_wiring_fails_closed_without_sources(tmp_path: Path) -> None:
    packet = build_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan(
        repo_root=tmp_path
    )

    assert packet["wiring_spec_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_shadow_replay_integration_exploration_plan"]["source_ready"] is False
    assert packet["source_phase1_operator_review_request"]["source_ready"] is False
    assert all(item["mapping_status"] == "NOT_COMPUTABLE" for item in packet["input_mapping"])


def test_codegen_improvement_proposal_wiring_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_improvement_proposal_wiring_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_improvement_proposal_wiring_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan_markdown(
        packet
    )

    assert (
        markdown[0]
        == "# ABX Codegen Intelligence Spine ImprovementProposal Shadow Replay Wiring Spec Plan"
    )
    assert any("proposal_id -> candidate_id" in line for line in markdown)
    assert any("shadow_replay_execution_denied" in line for line in markdown)
