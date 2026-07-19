from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_schema_master_registry_alignment_plan import (
    build_abx_codegen_intelligence_spine_schema_master_registry_alignment_plan,
    render_abx_codegen_intelligence_spine_schema_master_registry_alignment_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts.codegen import run_abx_codegen_intelligence_spine_schema_master_registry_alignment_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_schema_master_registry_alignment_plan.v1.schema.json"
)


def test_codegen_schema_master_registry_alignment_plan_is_held() -> None:
    packet = build_abx_codegen_intelligence_spine_schema_master_registry_alignment_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["schema_master_registry_alignment_plan_status"]
        == "ABX_CODEGEN_SCHEMA_MASTER_REGISTRY_ALIGNMENT_PLAN_HELD_FOR_OPERATOR"
    )
    assert packet["source_object_model_schema_plan"]["source_ready"] is True
    assert packet["source_module_surface_plan"]["source_ready"] is True
    assert packet["source_sample_fixture_normalization_plan"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_schema_master_registry_alignment_binds_planned_codegen_schemas() -> None:
    packet = build_abx_codegen_intelligence_spine_schema_master_registry_alignment_plan(
        repo_root=REPO_ROOT
    )

    bindings = {item["schema_id"]: item for item in packet["schema_registry_bindings"]}
    assert set(bindings) == {
        "PatchContract.v1",
        "CodeDropEnvelope.v1",
        "PolicyReviewPacket.v1",
        "CodegenHandoffPacket.v1",
    }
    assert (
        bindings["PatchContract.v1"]["repo_path"]
        == "contracts/codegen/patch_contract.v1.schema.json"
    )
    assert (
        bindings["PolicyReviewPacket.v1"]["used_by_rune"]
        == "RUNE.CODEGEN.POLICY_REVIEW"
    )
    assert all(
        item["implementation_status"] == "PLANNED"
        for item in packet["schema_registry_bindings"]
    )
    assert all(
        item["schema_creation_authorized"] is False
        for item in packet["schema_registry_bindings"]
    )
    assert all(
        item["runtime_binding_authorized"] is False
        for item in packet["schema_registry_bindings"]
    )
    assert all(
        item["rune_invocation_authorized"] is False
        for item in packet["schema_registry_bindings"]
    )


def test_codegen_schema_master_registry_alignment_records_required_ledger_fields() -> None:
    packet = build_abx_codegen_intelligence_spine_schema_master_registry_alignment_plan(
        repo_root=REPO_ROOT
    )

    assert packet["required_schema_fields"] == [
        "schema_id",
        "version",
        "owner",
        "route",
        "used_by_runes",
        "direction",
        "repo_path",
        "required_fields",
        "governance_locks",
        "provenance_requirements",
        "not_computable_conditions",
        "golden_tests",
        "implementation_status",
    ]


def test_codegen_schema_master_registry_alignment_records_golden_test_classes() -> None:
    packet = build_abx_codegen_intelligence_spine_schema_master_registry_alignment_plan(
        repo_root=REPO_ROOT
    )

    assert packet["required_golden_test_classes"] == [
        "schema_validation_success",
        "schema_validation_failure",
        "deterministic_serialization_hash",
        "governance_lock_preservation",
        "missing_provenance_failure",
        "not_computable_behavior",
        "forbidden_status_rejection",
        "route_rune_compatibility",
        "no_authority_escalation",
    ]


def test_codegen_schema_master_registry_alignment_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_schema_master_registry_alignment_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert "patch_contract_schema_creation" in packet["blocked_actions"]
    assert "runtime_behavior_creation" in packet["blocked_actions"]
    assert "schema_registry_implementation_status_promotion" in packet["blocked_actions"]


def test_codegen_schema_master_registry_alignment_fails_closed_without_sources(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_intelligence_spine_schema_master_registry_alignment_plan(
        repo_root=tmp_path
    )

    assert packet["schema_master_registry_alignment_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_object_model_schema_plan"]["source_ready"] is False
    assert packet["source_module_surface_plan"]["source_ready"] is False
    assert packet["source_sample_fixture_normalization_plan"]["source_ready"] is False
    assert all(
        item["binding_status"] == "NOT_COMPUTABLE"
        for item in packet["schema_registry_bindings"]
    )


def test_codegen_schema_master_registry_alignment_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_schema_master_registry_alignment_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_schema_master_registry_alignment_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_schema_master_registry_alignment_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_schema_master_registry_alignment_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_schema_master_registry_alignment_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_schema_master_registry_alignment_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_schema_master_registry_alignment_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_schema_master_registry_alignment_plan_markdown(
        packet
    )

    assert markdown[0] == (
        "# ABX Codegen Intelligence Spine Schema Master Registry Alignment Plan"
    )
    assert any("PatchContract.v1" in line for line in markdown)
    assert any("schema_validation_success" in line for line in markdown)
    assert any("runtime_behavior_creation" in line for line in markdown)
