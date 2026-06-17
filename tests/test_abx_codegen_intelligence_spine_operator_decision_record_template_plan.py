from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_operator_decision_record_template_plan import (
    build_abx_codegen_intelligence_spine_operator_decision_record_template_plan,
    render_abx_codegen_intelligence_spine_operator_decision_record_template_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_intelligence_spine_operator_decision_record_template_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_operator_decision_record_template_plan.v1.schema.json"
)


def test_codegen_operator_decision_record_template_plan_is_held_for_operator() -> None:
    packet = build_abx_codegen_intelligence_spine_operator_decision_record_template_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["operator_decision_record_template_plan_status"]
        == "ABX_CODEGEN_OPERATOR_DECISION_RECORD_TEMPLATE_PLAN_HELD_FOR_OPERATOR"
    )
    assert packet["source_harness_interface_spec_plan"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_operator_decision_record_template_families_are_reference_only() -> None:
    packet = build_abx_codegen_intelligence_spine_operator_decision_record_template_plan(
        repo_root=REPO_ROOT
    )

    assert [family["template_family"] for family in packet["template_families"]] == [
        "standard_codegen_proposal_odr",
        "meta_gate_self_improvement_odr",
    ]
    assert all(
        family["record_creation_authorized"] is False
        for family in packet["template_families"]
    )
    assert all(
        spec["timestamp_policy"] == "template_placeholder_only_no_wall_clock_generation"
        for spec in packet["source_notion_specs"]
    )


def test_codegen_operator_decision_record_template_sections_and_vocabularies() -> None:
    packet = build_abx_codegen_intelligence_spine_operator_decision_record_template_plan(
        repo_root=REPO_ROOT
    )

    sections = {section["section"] for section in packet["required_sections"]}
    assert "proposal_summary" in sections
    assert "shadow_replay_results" in sections
    assert "authorization_and_provenance" in sections
    assert "HOLD_FOR_META_GATE" in packet["decision_vocabularies"]["receipt_recommendations_referenced"]
    assert packet["decision_vocabularies"]["vocabulary_authority_granted"] is False


def test_codegen_operator_decision_record_template_meta_gate_denies_promotion() -> None:
    packet = build_abx_codegen_intelligence_spine_operator_decision_record_template_plan(
        repo_root=REPO_ROOT
    )

    requirements = {item["requirement"]: item for item in packet["meta_gate_requirements"]}
    assert (
        requirements[
            "complete_full_meta_gate_authorization_chain_before_promotion_consideration"
        ]["authorization_granted"]
        is False
    )
    assert (
        requirements[
            "state_that_meta_gate_odr_does_not_grant_promotion_authority"
        ]["authorization_granted"]
        is False
    )
    assert packet["template_output_policy"]["operator_decision_record_emitted_by_this_plan"] is False
    assert packet["template_output_policy"]["meta_gate_authorization_record_emitted_by_this_plan"] is False


def test_codegen_operator_decision_record_template_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_operator_decision_record_template_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_operator_decision_record_template_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_intelligence_spine_operator_decision_record_template_plan(
        repo_root=tmp_path
    )

    assert packet["operator_decision_record_template_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_harness_interface_spec_plan"]["source_ready"] is False
    assert all(
        family["template_status"] == "NOT_COMPUTABLE"
        for family in packet["template_families"]
    )


def test_codegen_operator_decision_record_template_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_operator_decision_record_template_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_operator_decision_record_template_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_operator_decision_record_template_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_operator_decision_record_template_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_operator_decision_record_template_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_operator_decision_record_template_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_operator_decision_record_template_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_operator_decision_record_template_plan_markdown(
        packet
    )

    assert markdown[0] == "# ABX Codegen Intelligence Spine Operator Decision Record Template Plan"
    assert any("meta_gate_self_improvement_odr" in line for line in markdown)
    assert any("decision_record_creation_denied" in line for line in markdown)
