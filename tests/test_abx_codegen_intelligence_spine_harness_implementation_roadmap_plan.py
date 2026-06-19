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


def test_codegen_harness_implementation_roadmap_is_authorized_for_phase_one() -> None:
    packet = build_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["harness_implementation_roadmap_plan_status"]
        == "ABX_CODEGEN_HARNESS_IMPLEMENTATION_ROADMAP_PLAN_AUTHORIZED"
    )
    assert packet["source_testing_validation_strategy_plan"]["source_ready"] is True
    assert packet["implementation_authorization_source"]["source_ready"] is True
    assert packet["implementation_authorization_source"]["implementation_authorization_granted"] is True
    assert packet["recommended_next_lane"] == "CORE_CODEGEN_SHADOW_REPLAY_HARNESS_IMPLEMENTATION"
    assert packet["valid_for_implementation"] is True


def test_codegen_harness_implementation_roadmap_held_without_authorization(tmp_path: Path) -> None:
    gate_path = (
        tmp_path
        / "out/audit/abx_codegen_intelligence_spine_shadow_replay_harness_implementation_authorization_gate_001.latest.json"
    )
    gate_path.parent.mkdir(parents=True, exist_ok=True)
    gate_path.write_text(
        json.dumps(
            {
                "artifact_type": (
                    "AbxCodegenIntelligenceSpineShadowReplayHarnessImplementationAuthorizationGate.v1"
                ),
                "authorization_gate_status": (
                    "SHADOW_REPLAY_HARNESS_IMPLEMENTATION_AUTHORIZATION_HELD_FOR_OPERATOR"
                ),
                "implementation_authorization_granted": False,
                "operator_review_required": True,
                "valid_for_implementation": False,
            }
        ),
        encoding="utf-8",
    )
    testing_path = (
        REPO_ROOT
        / "out/audit/abx_codegen_intelligence_spine_testing_validation_strategy_plan_001.latest.json"
    )
    target_testing = (
        tmp_path
        / "out/audit/abx_codegen_intelligence_spine_testing_validation_strategy_plan_001.latest.json"
    )
    target_testing.parent.mkdir(parents=True, exist_ok=True)
    target_testing.write_text(testing_path.read_text(encoding="utf-8"), encoding="utf-8")
    packet = build_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan(
        repo_root=tmp_path
    )
    assert (
        packet["harness_implementation_roadmap_plan_status"]
        == "ABX_CODEGEN_HARNESS_IMPLEMENTATION_ROADMAP_PLAN_HELD_FOR_OPERATOR"
    )


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
    phase_statuses = {phase["phase"]: phase["phase_status"] for phase in packet["phases"]}
    assert phase_statuses["Phase 1: Core Foundation"] == "AUTHORIZED_IN_PROGRESS"
    assert phase_statuses["Phase 2: Self-Modification & Meta-Gate Support"] == (
        "BLOCKED_PENDING_OPERATOR_AUTHORIZATION"
    )
    assert packet["phases"][0]["implementation_authorized"] is True
    assert all(phase["implementation_authorized"] is False for phase in packet["phases"][1:])


def test_codegen_harness_roadmap_starting_point_is_not_authorized() -> None:
    packet = build_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan(
        repo_root=REPO_ROOT
    )
    starting_point = packet["recommended_starting_point"]

    assert starting_point["notion_recommended_phase"] == "Phase 1: Core Foundation"
    assert starting_point["repo_authorized_starting_point"] == "PHASE_1_CORE_FOUNDATION"
    assert starting_point["minimal_working_loop_authorized"] is True
    assert starting_point["phase_1_detail_code_authorized"] is True
    assert "phase_2_plus_pending_separate_authorization" in packet["roadmap_blockers"]


def test_codegen_harness_roadmap_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is True
    assert packet["authority_locks"]["harness_implementation"] is True
    assert packet["authority_locks"]["shadow_replay_execution"] is False


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
    assert any("phase_2_plus_pending_separate_authorization" in line for line in markdown)
