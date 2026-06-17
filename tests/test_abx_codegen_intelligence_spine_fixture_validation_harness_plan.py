from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_fixture_validation_harness_plan import (
    build_abx_codegen_intelligence_spine_fixture_validation_harness_plan,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_intelligence_spine_fixture_validation_harness_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_fixture_validation_harness_plan.v1.schema.json"
)


def test_codegen_fixture_validation_harness_plan_is_advisory_only() -> None:
    packet = build_abx_codegen_intelligence_spine_fixture_validation_harness_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["artifact_type"]
        == "AbxCodegenIntelligenceSpineFixtureValidationHarnessPlan.v1"
    )
    assert (
        packet["plan_status"]
        == "ABX_CODEGEN_INTELLIGENCE_SPINE_FIXTURE_VALIDATION_HARNESS_PLAN_READY"
    )
    assert packet["target_surface"] == "ABX_CODEGEN_INTELLIGENCE_SPINE_001"
    assert packet["harness_implementation_performed"] is False
    assert packet["shadow_replay_execution_performed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert all(value is False for value in packet["authority_locks"].values())
    assert "harness_implementation" in packet["blocked_actions"]
    assert "receipt_creation" in packet["blocked_actions"]


def test_codegen_fixture_validation_harness_plan_maps_notion_requirements() -> None:
    packet = build_abx_codegen_intelligence_spine_fixture_validation_harness_plan(
        repo_root=REPO_ROOT
    )

    interface_names = {item["name"] for item in packet["planned_interfaces"]}
    assert "run_codegen_shadow_replay" in interface_names
    assert "_validate_proposal" in interface_names
    assert "_determine_recommendation" in interface_names

    proof_flags = {item["flag"] for item in packet["planned_proof_flags"]}
    assert "authority_lock_invariance_observed" in proof_flags
    assert "codegen_deterministic_output_observed" in proof_flags
    assert "meta_gate_extra_checks_passed" in proof_flags

    taxonomy = {item["code_prefix"]: item for item in packet["failure_taxonomy"]}
    assert taxonomy["VAL-"]["default_recommendation"] == "REJECT"
    assert taxonomy["RPL-"]["default_recommendation"] == "BLOCK_REPLAY_FAILURE"
    assert taxonomy["META-"]["default_recommendation"] == "HOLD_FOR_META_GATE"
    assert packet["fixture_inventory"]["valid_fixture_count"] == 4
    assert packet["fixture_inventory"]["negative_fixture_count"] == 5


def test_codegen_fixture_validation_harness_plan_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_fixture_validation_harness_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_fixture_validation_harness_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_fixture_validation_harness_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_fixture_validation_harness_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_fixture_validation_harness_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
    assert first_md.startswith(
        "# ABX Codegen Intelligence Spine Fixture Validation Harness Plan\n"
    )
