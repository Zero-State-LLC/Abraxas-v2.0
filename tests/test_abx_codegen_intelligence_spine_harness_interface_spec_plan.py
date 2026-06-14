from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_harness_interface_spec_plan import (
    build_abx_codegen_intelligence_spine_harness_interface_spec_plan,
    render_abx_codegen_intelligence_spine_harness_interface_spec_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_intelligence_spine_harness_interface_spec_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_harness_interface_spec_plan.v1.schema.json"
)


def test_codegen_harness_interface_spec_is_held_for_operator() -> None:
    packet = build_abx_codegen_intelligence_spine_harness_interface_spec_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["harness_interface_spec_plan_status"]
        == "ABX_CODEGEN_HARNESS_INTERFACE_SPEC_PLAN_HELD_FOR_OPERATOR"
    )
    assert packet["source_phase1_code_detail_plan"]["source_ready"] is True
    assert packet["target_module"] == "core/codegen_shadow_replay_harness.py"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_harness_interface_spec_preserves_architecture_and_interfaces() -> None:
    packet = build_abx_codegen_intelligence_spine_harness_interface_spec_plan(
        repo_root=REPO_ROOT
    )

    assert [stage["stage"] for stage in packet["architecture_stages"]] == [
        "ImprovementProposal.v1",
        "Validation & Normalization Layer",
        "Replay Configuration Builder",
        "Deterministic Replay Executor",
        "Proof Flag Evaluator",
        "Status & Recommendation Engine",
        "ShadowImprovementReceipt.v1 Builder",
        "Canonical JSON Output + Artifact Registry Registration",
    ]
    assert [item["interface_name"] for item in packet["core_interfaces"]] == [
        "run_codegen_shadow_replay",
        "_validate_proposal",
        "_build_replay_config",
        "_execute_deterministic_replays",
        "_evaluate_proof_flags",
        "_determine_recommendation",
        "_build_receipt",
    ]
    assert all(item["implementation_authorized"] is False for item in packet["core_interfaces"])


def test_codegen_harness_interface_spec_proof_flags_and_meta_gate_are_reference_only() -> None:
    packet = build_abx_codegen_intelligence_spine_harness_interface_spec_plan(
        repo_root=REPO_ROOT
    )

    assert "authority_lock_invariance_observed" in packet["proof_flags"]["standard"]
    assert "meta_gate_extra_checks_passed" in packet["proof_flags"]["codegen_specific"]
    assert packet["proof_flags"]["proof_flag_evaluation_authorized"] is False
    assert all(
        rule["implementation_authorized"] is False
        for rule in packet["meta_gate_handling_rules"]
    )


def test_codegen_harness_interface_spec_denies_outputs_and_integrations() -> None:
    packet = build_abx_codegen_intelligence_spine_harness_interface_spec_plan(
        repo_root=REPO_ROOT
    )

    assert packet["integration_guidance"]["prefer_extend_research_shadow_replay_audit"] is True
    assert packet["integration_guidance"]["shared_replay_utility_refactor_allowed_by_this_plan"] is False
    assert packet["integration_guidance"]["p103_reuse_authorized"] is False
    assert packet["output_requirements"]["canonical_output_write_authorized"] is False
    assert packet["output_requirements"]["artifact_registry_registration_authorized"] is False
    assert packet["output_requirements"]["receipt_creation_authorized"] is False


def test_codegen_harness_interface_spec_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_harness_interface_spec_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_harness_interface_spec_fails_closed_without_source(tmp_path: Path) -> None:
    packet = build_abx_codegen_intelligence_spine_harness_interface_spec_plan(
        repo_root=tmp_path
    )

    assert packet["harness_interface_spec_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_phase1_code_detail_plan"]["source_ready"] is False
    assert all(stage["stage_status"] == "NOT_COMPUTABLE" for stage in packet["architecture_stages"])


def test_codegen_harness_interface_spec_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_harness_interface_spec_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_harness_interface_spec_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_harness_interface_spec_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_harness_interface_spec_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_harness_interface_spec_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_harness_interface_spec_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_harness_interface_spec_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_harness_interface_spec_plan_markdown(
        packet
    )

    assert markdown[0] == "# ABX Codegen Intelligence Spine Harness Interface Spec Plan"
    assert any("run_codegen_shadow_replay" in line for line in markdown)
    assert any("target_module_creation_denied" in line for line in markdown)
