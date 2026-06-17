from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_harness_implementation_roadmap_plan import (
    build_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan,
    render_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_harness_implementation_roadmap_plan.v1.schema.json"
)


def test_codegen_harness_implementation_roadmap_is_held_for_operator() -> None:
    packet = build_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["harness_implementation_roadmap_plan_status"]
        == "ABX_CODEGEN_HARNESS_IMPLEMENTATION_ROADMAP_PLAN_HELD_FOR_OPERATOR"
    )
    assert packet["source_testing_validation_strategy_plan"]["source_ready"] is True
    assert packet["implementation_authorization_source"]["source_ready"] is True
    assert packet["implementation_authorization_source"]["implementation_authorization_granted"] is False
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_codegen_harness_implementation_roadmap_preserves_phases_as_blocked() -> None:
    packet = build_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan(
        repo_root=REPO_ROOT
    )

    assert [phase["phase"] for phase in packet["phases"]] == [
        "Phase 1: Core Foundation",
        "Phase 2: Self-Modification & Meta-Gate Support",
        "Phase 3: Robustness & Integration",
        "Phase 4: Advanced Features",
    ]
    assert all(
        phase["phase_status"] == "BLOCKED_PENDING_OPERATOR_AUTHORIZATION"
        for phase in packet["phases"]
    )
    assert all(phase["implementation_authorized"] is False for phase in packet["phases"])


def test_codegen_harness_roadmap_starting_point_is_not_authorized() -> None:
    packet = build_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan(
        repo_root=REPO_ROOT
    )
    starting_point = packet["recommended_starting_point"]

    assert starting_point["notion_recommended_phase"] == "Phase 1: Core Foundation"
    assert starting_point["repo_authorized_starting_point"] == "NOT_AUTHORIZED"
    assert starting_point["minimal_working_loop_authorized"] is False
    assert starting_point["phase_1_detail_code_authorized"] is False
    assert "implementation_authorization_gate_held_for_operator" in packet["roadmap_blockers"]


def test_codegen_harness_roadmap_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_harness_roadmap_fails_closed_without_sources(tmp_path: Path) -> None:
    packet = build_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan(
        repo_root=tmp_path
    )

    assert packet["harness_implementation_roadmap_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_testing_validation_strategy_plan"]["source_ready"] is False
    assert packet["implementation_authorization_source"]["source_ready"] is False
    assert all(phase["phase_status"] == "NOT_COMPUTABLE" for phase in packet["phases"])


def test_codegen_harness_roadmap_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_harness_roadmap_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_harness_implementation_roadmap_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_harness_roadmap_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan_markdown(
        packet
    )

    assert markdown[0] == "# ABX Codegen Intelligence Spine Harness Implementation Roadmap Plan"
    assert any("Phase 1: Core Foundation" in line for line in markdown)
    assert any("implementation_authorization_gate_held_for_operator" in line for line in markdown)
