from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan import (
    build_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan,
    render_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts.codegen import (
    run_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan."
    "v1.schema.json"
)


def test_codegen_recommended_patch_sequence_precondition_plan_is_held() -> None:
    packet = build_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan(
        repo_root=REPO_ROOT
    )

    assert packet["recommended_patch_sequence_precondition_plan_status"] == (
        "ABX_CODEGEN_RECOMMENDED_PATCH_SEQUENCE_PRECONDITION_PLAN_HELD_FOR_OPERATOR"
    )
    assert packet["source_schema_master_registry_alignment_plan"]["source_ready"] is True
    assert packet["source_phase1_implementation_boundary_review"]["source_ready"] is True
    assert packet["source_phase1_operator_review_request"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_recommended_patch_sequence_matches_notion_sequence() -> None:
    packet = build_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan(
        repo_root=REPO_ROOT
    )

    steps = [item["sequence_step"] for item in packet["recommended_patch_sequence"]]
    assert steps == [
        "audit_existing_codegen_modules",
        "avoid_duplicate_codegen_authority_surfaces",
        "add_or_align_contracts_codegen_schemas",
        "add_patch_contract_builder",
        "add_code_drop_envelope_builder",
        "add_policy_review_packet_builder",
        "add_incremental_patch_enforcer",
        "add_repo_state_binder_and_seal_validator",
        "add_codegen_handoff_packet_builder",
        "add_golden_tests",
        "update_docs",
    ]
    assert all(
        item["authorized_in_this_plan"] is False
        for item in packet["recommended_patch_sequence"]
    )


def test_codegen_recommended_patch_sequence_preconditions_remain_unsatisfied() -> None:
    packet = build_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan(
        repo_root=REPO_ROOT
    )

    groups = {item["group"]: item for item in packet["precondition_groups"]}
    assert set(groups) == {
        "schema_authorization",
        "operator_authorization",
        "validation_authorization",
        "runtime_containment",
    }
    assert all(
        requirement["satisfied"] is False
        for group in groups.values()
        for requirement in group["requirements"]
    )
    assert (
        groups["operator_authorization"]["requirements"][0]["requirement"]
        == "operator_decision_record_with_human_rationale"
    )


def test_codegen_recommended_patch_sequence_readiness_is_not_implementation_ready() -> None:
    packet = build_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan(
        repo_root=REPO_ROOT
    )

    readiness = packet["implementation_readiness_assessment"]
    assert readiness["notion_patch_class"] == "IMPLEMENTATION_PLAN_first"
    assert readiness["schema_master_alignment_ready"] is True
    assert readiness["phase1_boundary_review_ready"] is True
    assert readiness["phase1_operator_review_request_held"] is True
    assert readiness["operator_authorization_present"] is False
    assert readiness["schema_creation_authorization_present"] is False
    assert readiness["module_creation_authorization_present"] is False
    assert readiness["implementation_readiness"] == "HELD_FOR_OPERATOR"


def test_codegen_recommended_patch_sequence_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert "patch_contract_builder_creation" in packet["blocked_actions"]
    assert "implementation_prompt_emission" in packet["blocked_actions"]


def test_codegen_recommended_patch_sequence_fails_closed_without_sources(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan(
        repo_root=tmp_path
    )

    assert packet["recommended_patch_sequence_precondition_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_schema_master_registry_alignment_plan"]["source_ready"] is False
    assert packet["source_phase1_implementation_boundary_review"]["source_ready"] is False
    assert packet["source_phase1_operator_review_request"]["source_ready"] is False
    assert all(
        item["step_status"] == "NOT_COMPUTABLE"
        for item in packet["recommended_patch_sequence"]
    )


def test_codegen_recommended_patch_sequence_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_recommended_patch_sequence_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_recommended_patch_sequence_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan_markdown(
        packet
    )

    assert markdown[0] == (
        "# ABX Codegen Intelligence Spine Recommended Patch Sequence Precondition Plan"
    )
    assert any("add_patch_contract_builder" in line for line in markdown)
    assert any("operator_authorization" in line for line in markdown)
    assert any("implementation_prompt_emission" in line for line in markdown)
