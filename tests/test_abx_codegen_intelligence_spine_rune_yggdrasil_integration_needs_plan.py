from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan import (
    build_abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan,
    render_abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan.v1.schema.json"
)


def test_codegen_rune_yggdrasil_integration_needs_plan_ready() -> None:
    packet = build_abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["integration_needs_plan_status"]
        == "ABX_CODEGEN_RUNE_YGGDRASIL_INTEGRATION_NEEDS_PLAN_READY"
    )
    assert packet["source_codegen_operator_decision_record_review"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_rune_yggdrasil_candidates_are_planning_only() -> None:
    packet = build_abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan(
        repo_root=REPO_ROOT
    )

    assert [item["rune"] for item in packet["candidate_runes"]] == [
        "RUNE.CODEGEN.PROPOSE",
        "RUNE.CODEGEN.SHADOW_REPLAY",
        "RUNE.CODEGEN.META_GATE",
        "RUNE.CODEGEN.ODR",
        "RUNE.CODEGEN.SEAL",
    ]
    assert all(item["candidate_status"] == "PLANNING_ONLY" for item in packet["candidate_runes"])
    assert all(item["registration_authorized"] is False for item in packet["candidate_runes"])
    assert all(
        item["binding_matrix_update_authorized"] is False for item in packet["candidate_runes"]
    )


def test_codegen_rune_yggdrasil_routes_are_projection_only_and_unregistered() -> None:
    packet = build_abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan(
        repo_root=REPO_ROOT
    )

    assert [item["route_family"] for item in packet["candidate_route_families"]] == [
        "codegen.proposal.generate",
        "codegen.shadow.replay",
        "codegen.meta.gate",
        "codegen.operator.decision",
    ]
    assert packet["route_defaults"]["meta_gate_operator_review_bypass_allowed"] is False
    assert all(
        item["default_authority"] == "projection_only"
        for item in packet["candidate_route_families"]
    )
    assert all(
        item["route_registration_authorized"] is False
        for item in packet["candidate_route_families"]
    )
    assert all(
        item["runtime_binding_authorized"] is False
        for item in packet["candidate_route_families"]
    )


def test_codegen_rune_yggdrasil_plan_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_rune_yggdrasil_plan_fails_closed_without_source(tmp_path: Path) -> None:
    packet = build_abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan(
        repo_root=tmp_path
    )

    assert packet["integration_needs_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_codegen_operator_decision_record_review"]["source_ready"] is False
    assert all(
        item["candidate_status"] == "NOT_COMPUTABLE" for item in packet["candidate_runes"]
    )
    assert all(
        item["route_status"] == "NOT_COMPUTABLE"
        for item in packet["candidate_route_families"]
    )


def test_codegen_rune_yggdrasil_plan_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_rune_yggdrasil_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_rune_yggdrasil_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan_markdown(
        packet
    )

    assert (
        markdown[0]
        == "# ABX Codegen Intelligence Spine Rune YGGDRASIL Integration Needs Plan"
    )
    assert any("RUNE.CODEGEN.SHADOW_REPLAY: PLANNING_ONLY" in line for line in markdown)
    assert any("codegen.meta.gate: PLANNING_ONLY" in line for line in markdown)
