from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_artifact_registry_integration_plan import (
    build_abx_codegen_intelligence_spine_artifact_registry_integration_plan,
    render_abx_codegen_intelligence_spine_artifact_registry_integration_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_intelligence_spine_artifact_registry_integration_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_artifact_registry_integration_plan.v1.schema.json"
)


def test_codegen_artifact_registry_integration_plan_ready() -> None:
    packet = build_abx_codegen_intelligence_spine_artifact_registry_integration_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["artifact_registry_integration_plan_status"]
        == "ABX_CODEGEN_ARTIFACT_REGISTRY_INTEGRATION_PLAN_READY"
    )
    assert packet["source_continuity_lane_conventions_plan"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_artifact_registry_types_are_planning_only() -> None:
    packet = build_abx_codegen_intelligence_spine_artifact_registry_integration_plan(
        repo_root=REPO_ROOT
    )

    assert [item["artifact_type"] for item in packet["artifact_types_to_register"]] == [
        "ImprovementProposal.v1",
        "ShadowImprovementReceipt.v1",
        "CodegenOperatorDecisionRecord.v1",
        "MetaGateAuthorizationRecord.v1",
        "MetaGateChainSeal.v1",
    ]
    assert all(
        item["registration_status"] == "PLANNING_ONLY"
        for item in packet["artifact_types_to_register"]
    )
    assert all(
        item["registration_authorized"] is False
        for item in packet["artifact_types_to_register"]
    )


def test_codegen_artifact_registry_timestamp_is_source_observed_only() -> None:
    packet = build_abx_codegen_intelligence_spine_artifact_registry_integration_plan(
        repo_root=REPO_ROOT
    )
    requirements = packet["registration_requirements"]

    assert "source_observed_timestamp" in requirements["required_fields"]
    assert "timestamp" not in requirements["required_fields"]
    assert "wall-clock generation time is forbidden" in requirements["timestamp_policy"]
    assert requirements["registration_write_authorized"] is False


def test_codegen_artifact_registry_lineage_and_integration_are_not_enforcement() -> None:
    packet = build_abx_codegen_intelligence_spine_artifact_registry_integration_plan(
        repo_root=REPO_ROOT
    )

    assert all(rule["required"] is True for rule in packet["lineage_rules"])
    assert all(rule["enforcement_authorized"] is False for rule in packet["lineage_rules"])
    assert all(
        point["registry_call_authorized"] is False for point in packet["integration_points"]
    )
    assert packet["future_considerations"]["future_policy_authorized_by_this_plan"] is False


def test_codegen_artifact_registry_plan_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_artifact_registry_integration_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_artifact_registry_plan_fails_closed_without_source(tmp_path: Path) -> None:
    packet = build_abx_codegen_intelligence_spine_artifact_registry_integration_plan(
        repo_root=tmp_path
    )

    assert packet["artifact_registry_integration_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_continuity_lane_conventions_plan"]["source_ready"] is False
    assert all(
        item["registration_status"] == "NOT_COMPUTABLE"
        for item in packet["artifact_types_to_register"]
    )


def test_codegen_artifact_registry_plan_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_artifact_registry_integration_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_artifact_registry_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_artifact_registry_integration_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_artifact_registry_integration_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_artifact_registry_integration_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_artifact_registry_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_artifact_registry_integration_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_artifact_registry_integration_plan_markdown(
        packet
    )

    assert (
        markdown[0]
        == "# ABX Codegen Intelligence Spine Artifact Registry Integration Plan"
    )
    assert any("ImprovementProposal.v1: PLANNING_ONLY" in line for line in markdown)
    assert any("registration_write_authorized: False" in line for line in markdown)
