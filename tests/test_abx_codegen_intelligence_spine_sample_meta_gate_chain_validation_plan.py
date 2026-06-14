from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan import (
    build_abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan,
    render_abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan.v1.schema.json"
)


def test_codegen_sample_meta_gate_chain_validation_plan_is_held() -> None:
    packet = build_abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["sample_meta_gate_chain_validation_plan_status"]
        == "ABX_CODEGEN_SAMPLE_META_GATE_CHAIN_VALIDATION_PLAN_HELD_FOR_OPERATOR"
    )
    assert packet["source_wiring_spec_plan"]["source_ready"] is True
    assert packet["source_meta_gate_authorization_record_template_plan"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_sample_meta_gate_chain_classifies_all_artifact_roles() -> None:
    packet = build_abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan(
        repo_root=REPO_ROOT
    )

    artifacts = {item["artifact_role"]: item for item in packet["sample_chain_artifacts"]}
    assert artifacts["ImprovementProposal.v1"]["canonical_fixture_emission_authorized"] is False
    assert (
        artifacts["ShadowImprovementReceipt.v1"]["observed_recommendation_or_decision"]
        == "HOLD_FOR_META_GATE"
    )
    assert artifacts["Meta-Gate Operator Decision Record"]["record_creation_authorized"] is False
    assert artifacts["Meta-Gate Authorization Record"]["record_creation_authorized"] is False
    assert artifacts["Meta-Gate Chain Seal"]["seal_creation_authorized"] is False


def test_codegen_sample_meta_gate_chain_normalization_blocks_fixture_use() -> None:
    packet = build_abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan(
        repo_root=REPO_ROOT
    )

    policy = packet["normalization_policy"]
    assert policy["example_timestamps_are_source_observed_only"] is True
    assert policy["wall_clock_generation_authorized"] is False
    assert policy["ellipsis_blocks_must_be_replaced_before_fixture_use"] is True
    assert policy["canonical_fixture_output_authorized"] is False
    assert "examples_contain_ellipsis_blocks" in packet["example_limitations"]


def test_codegen_sample_meta_gate_chain_validation_rules_are_plan_only() -> None:
    packet = build_abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan(
        repo_root=REPO_ROOT
    )

    rules = {item["rule"]: item for item in packet["validation_rules"]}
    assert (
        rules["self_improvement_proposal_must_route_to_hold_for_meta_gate"][
            "validation_execution_authorized"
        ]
        is False
    )
    assert (
        rules["real_chain_seal_example_cannot_be_treated_as_actual_seal"][
            "planned_validation_status"
        ]
        == "SAMPLE_CHAIN_VALIDATION_DEFINED_HELD_FOR_OPERATOR"
    )
    assert (
        rules["post_seal_step_is_canary_review_only_not_execution"][
            "validation_execution_authorized"
        ]
        is False
    )


def test_codegen_sample_meta_gate_chain_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert "operator_attestation_fabrication" in packet["blocked_actions"]
    assert "meta_gate_chain_seal_creation" in packet["blocked_actions"]


def test_codegen_sample_meta_gate_chain_fails_closed_without_sources(tmp_path: Path) -> None:
    packet = build_abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan(
        repo_root=tmp_path
    )

    assert packet["sample_meta_gate_chain_validation_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_wiring_spec_plan"]["source_ready"] is False
    assert packet["source_meta_gate_authorization_record_template_plan"]["source_ready"] is False
    assert all(
        item["sample_status"] == "NOT_COMPUTABLE"
        for item in packet["sample_chain_artifacts"]
    )


def test_codegen_sample_meta_gate_chain_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_sample_meta_gate_chain_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_sample_meta_gate_chain_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan_markdown(
        packet
    )

    assert (
        markdown[0]
        == "# ABX Codegen Intelligence Spine Sample Meta-Gate Chain Validation Plan"
    )
    assert any("ShadowImprovementReceipt.v1" in line for line in markdown)
    assert any("meta_gate_chain_seal_creation" in line for line in markdown)
