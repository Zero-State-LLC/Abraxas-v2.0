from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan import (
    build_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan,
    render_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan.v1.schema.json"
)


def test_codegen_meta_gate_authorization_record_template_plan_is_held() -> None:
    packet = build_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["meta_gate_authorization_record_template_plan_status"]
        == "ABX_CODEGEN_META_GATE_AUTHORIZATION_RECORD_TEMPLATE_PLAN_HELD_FOR_OPERATOR"
    )
    assert packet["source_operator_decision_record_template_plan"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_meta_gate_authorization_record_template_is_reference_only() -> None:
    packet = build_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan(
        repo_root=REPO_ROOT
    )

    template = packet["authorization_record_template"]
    assert template["record_id_pattern"].startswith("MGAUTH-CODEGEN-")
    assert "review_evidence" in template["required_sections"]
    assert template["record_creation_authorized"] is False
    assert template["continuation_authority_granted"] is False
    assert all(
        spec["timestamp_policy"].endswith("no_wall_clock_generation")
        for spec in packet["source_notion_specs"]
    )


def test_codegen_meta_gate_chain_seal_template_denies_sealing_and_promotion() -> None:
    packet = build_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan(
        repo_root=REPO_ROOT
    )

    seal = packet["chain_seal_template"]
    assert seal["seal_phases"] == ["dry_run", "operator_review", "real_seal"]
    assert seal["post_seal_allowed_step"] == "normal_canary_promotion_gate_review_only"
    assert seal["dry_run_creation_authorized"] is False
    assert seal["real_seal_creation_authorized"] is False
    assert seal["post_seal_promotion_authority_granted"] is False


def test_codegen_meta_gate_scope_boundaries_are_fail_closed() -> None:
    packet = build_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan(
        repo_root=REPO_ROOT
    )

    policy = packet["scope_boundary_policy"]
    assert "authorization_record_creation_or_sealing_logic" in policy["red_zone_forbidden"]
    assert "meta_gate_or_meta_gate_authorization_chain_controls" in policy["red_zone_forbidden"]
    assert policy["red_zone_recommendation"] == "BLOCK_POLICY_VIOLATION"
    assert policy["boundary_enforcement_authorized"] is False


def test_codegen_meta_gate_requires_missing_upstream_operator_evidence() -> None:
    packet = build_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan(
        repo_root=REPO_ROOT
    )

    assert all(item["required"] is True for item in packet["required_upstream_evidence"])
    assert all(
        item["evidence_present_in_this_plan"] is False
        for item in packet["required_upstream_evidence"]
    )
    assert "operator_attestation_missing" in packet["implementation_blockers"]
    assert "positive_meta_gate_operator_decision_record_missing" in packet[
        "implementation_blockers"
    ]


def test_codegen_meta_gate_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_meta_gate_fails_closed_without_source(tmp_path: Path) -> None:
    packet = build_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan(
        repo_root=tmp_path
    )

    assert packet["meta_gate_authorization_record_template_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_operator_decision_record_template_plan"]["source_ready"] is False
    assert packet["authorization_record_template"]["template_status"] == "NOT_COMPUTABLE"
    assert packet["chain_seal_template"]["template_status"] == "NOT_COMPUTABLE"


def test_codegen_meta_gate_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_meta_gate_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_meta_gate_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan_markdown(
        packet
    )

    assert markdown[0] == "# ABX Codegen Intelligence Spine Meta-Gate Authorization Record Template Plan"
    assert any("authorization_record_creation_or_sealing_logic" in line for line in markdown)
    assert any("meta_gate_real_seal_creation_denied" in line for line in markdown)
