from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan import (
    build_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan,
    render_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts.codegen import run_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan.v1.schema.json"
)


def test_codegen_self_improvement_boundary_policy_plan_is_held() -> None:
    packet = build_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["self_improvement_boundary_policy_plan_status"]
        == "ABX_CODEGEN_SELF_IMPROVEMENT_BOUNDARY_POLICY_PLAN_HELD_FOR_OPERATOR"
    )
    assert packet["source_meta_gate_authorization_record_template_plan"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_self_improvement_boundary_triggers_do_not_route() -> None:
    packet = build_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan(
        repo_root=REPO_ROOT
    )

    assert [item["trigger"] for item in packet["meta_gate_triggers"]] == [
        "self_modification_risk_true",
        "self_modification_detected_true",
        "target_surface_is_codegen_spine_or_core_governance_contract",
        "proposal_type_self_improvement",
    ]
    assert all(item["routing_authorized"] is False for item in packet["meta_gate_triggers"])


def test_codegen_self_improvement_boundary_zones_are_encoded() -> None:
    packet = build_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan(
        repo_root=REPO_ROOT
    )

    assert packet["green_zone_policy"]["still_requires_meta_gate_and_normal_promotion"] is True
    assert packet["green_zone_policy"]["proposal_authority_granted"] is False
    assert (
        packet["yellow_zone_policy"]["required_review"]
        == "meta_gate_plus_elevated_operator_review"
    )
    assert packet["yellow_zone_policy"]["proposal_authority_granted"] is False
    assert packet["red_zone_policy"]["required_recommendation"] == "BLOCK_POLICY_VIOLATION"
    assert packet["red_zone_policy"]["auto_rejection_execution_authorized"] is False


def test_codegen_self_improvement_red_zone_blocks_core_controls() -> None:
    packet = build_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan(
        repo_root=REPO_ROOT
    )

    forbidden = packet["red_zone_policy"]["forbidden_targets"]
    assert "core_governance_promotion_gates" in forbidden
    assert "authorization_record_creation_or_sealing_logic" in forbidden
    assert "meta_gate_or_meta_gate_authorization_chain_controls" in forbidden
    assert "operator_review_bypass_or_self_authorization_mechanisms" in forbidden
    assert "foundational_authority_lock_definitions" in forbidden


def test_codegen_self_improvement_chain_outline_is_non_authoritative() -> None:
    packet = build_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan(
        repo_root=REPO_ROOT
    )

    assert [item["step"] for item in packet["chain_outline"]] == [
        "meta_gate_trigger_receipt",
        "meta_gate_operator_review_request",
        "meta_gate_operator_decision_record",
        "meta_gate_authorization_record_plan",
        "meta_gate_authorization_record_creation",
        "meta_gate_chain_seal_dry_run_and_real",
        "meta_gate_chain_compression_audit",
        "post_meta_gate_promotion_gate",
    ]
    assert all(
        item["artifact_creation_authorized"] is False for item in packet["chain_outline"]
    )


def test_codegen_self_improvement_validation_requirements_are_plan_only() -> None:
    packet = build_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan(
        repo_root=REPO_ROOT
    )

    requirements = {item["requirement"]: item for item in packet["future_validation_requirements"]}
    assert (
        requirements["red_zone_targets_must_emit_block_policy_violation"][
            "implementation_authorized"
        ]
        is False
    )
    assert (
        requirements["codegen_spine_must_not_create_or_sign_own_meta_gate_records"][
            "implementation_authorized"
        ]
        is False
    )


def test_codegen_self_improvement_boundary_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_self_improvement_boundary_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan(
        repo_root=tmp_path
    )

    assert packet["self_improvement_boundary_policy_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_meta_gate_authorization_record_template_plan"]["source_ready"] is False
    assert all(
        item["trigger_status"] == "NOT_COMPUTABLE" for item in packet["meta_gate_triggers"]
    )
    assert packet["red_zone_policy"]["policy_status"] == "NOT_COMPUTABLE"


def test_codegen_self_improvement_boundary_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_self_improvement_boundary_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_self_improvement_boundary_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan_markdown(
        packet
    )

    assert markdown[0] == "# ABX Codegen Intelligence Spine Self-Improvement Boundary Policy Plan"
    assert any("self_modification_risk_true" in line for line in markdown)
    assert any("authorization_record_creation_or_sealing_logic" in line for line in markdown)
