from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_governance_decision_vocabulary_plan import (
    build_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan,
    render_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts.codegen import run_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_governance_decision_vocabulary_plan.v1.schema.json"
)


def test_codegen_governance_vocabulary_plan_is_held() -> None:
    packet = build_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["governance_decision_vocabulary_plan_status"]
        == "ABX_CODEGEN_GOVERNANCE_DECISION_VOCABULARY_PLAN_HELD_FOR_OPERATOR"
    )
    assert packet["source_shadow_replay_integration_exploration_plan"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_governance_vocabulary_distinguishes_hold_and_block() -> None:
    packet = build_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan(
        repo_root=REPO_ROOT
    )

    distinctions = {item["term"]: item for item in packet["hold_block_distinctions"]}
    assert distinctions["HOLD_FOR_OPERATOR"]["recovery_path"] == (
        "operator_decision_record_or_additional_evidence"
    )
    assert distinctions["HOLD_FOR_META_GATE"]["recovery_path"] == (
        "meta_gate_authorization_chain_plus_elevated_operator_review"
    )
    assert distinctions["BLOCK_POLICY_VIOLATION"]["recovery_path"] == (
        "new_or_substantially_remediated_proposal"
    )
    assert all(item["routing_authorized"] is False for item in distinctions.values())


def test_codegen_governance_vocabulary_recommendation_enum_is_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan(
        repo_root=REPO_ROOT
    )

    assert [item["value"] for item in packet["recommended_decision_enum"]] == [
        "PROMOTE_TO_CANARY",
        "HOLD_FOR_OPERATOR",
        "HOLD_FOR_META_GATE",
        "BLOCK_POLICY_VIOLATION",
        "BLOCK_REPLAY_FAILURE",
        "REJECT",
        "REFINE_PROPOSAL",
    ]
    by_value = {item["value"]: item for item in packet["recommended_decision_enum"]}
    assert by_value["PROMOTE_TO_CANARY"]["promotion_blockers_required"] is False
    assert by_value["HOLD_FOR_OPERATOR"]["promotion_blockers_required"] is True
    assert by_value["BLOCK_REPLAY_FAILURE"]["classification"] == "hard_block"


def test_codegen_governance_vocabulary_promotion_blocker_policy_is_plan_only() -> None:
    packet = build_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan(
        repo_root=REPO_ROOT
    )

    policy = packet["promotion_blocker_policy"]
    assert policy["required_when_recommendation_not_promote_to_canary"] is True
    assert policy["machine_readable_reasons_required"] is True
    assert "self_modification_detected" in policy["example_blockers"]
    assert "governance_compliance_failed" in policy["example_blockers"]
    assert policy["blocker_population_authorized"] is False


def test_codegen_governance_vocabulary_self_modification_routes_to_meta_gate_only() -> None:
    packet = build_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan(
        repo_root=REPO_ROOT
    )

    policy = packet["self_modification_policy"]
    assert policy["self_modification_risk_recommendation"] == "HOLD_FOR_META_GATE"
    assert policy["must_hold"] is True
    assert policy["dedicated_meta_gate_authorization_chain_required"] is True
    assert policy["direct_promotion_allowed"] is False
    assert policy["routing_authorized"] is False


def test_codegen_governance_vocabulary_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_governance_vocabulary_fails_closed_without_source(tmp_path: Path) -> None:
    packet = build_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan(
        repo_root=tmp_path
    )

    assert packet["governance_decision_vocabulary_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_shadow_replay_integration_exploration_plan"]["source_ready"] is False
    assert all(
        item["distinction_status"] == "NOT_COMPUTABLE"
        for item in packet["hold_block_distinctions"]
    )


def test_codegen_governance_vocabulary_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_governance_vocabulary_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_governance_decision_vocabulary_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_governance_vocabulary_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_governance_decision_vocabulary_plan_markdown(
        packet
    )

    assert markdown[0] == "# ABX Codegen Intelligence Spine Governance Decision Vocabulary Plan"
    assert any("HOLD_FOR_META_GATE" in line for line in markdown)
    assert any("promotion_blocker_population_denied" in line for line in markdown)
