from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_hygiene_phase2_module_skeleton_backlog_plan import (
    build_v2_hygiene_phase2_module_skeleton_backlog_plan,
    render_v2_hygiene_phase2_module_skeleton_backlog_plan_markdown,
    write_v2_hygiene_phase2_module_skeleton_backlog_plan,
)
from scripts import run_v2_hygiene_phase2_module_skeleton_backlog_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/v2_hygiene_phase2_module_skeleton_backlog_plan.v1.schema.json"


def test_v2_hygiene_phase2_module_skeleton_backlog_plan_ready() -> None:
    first = build_v2_hygiene_phase2_module_skeleton_backlog_plan(REPO_ROOT)
    second = build_v2_hygiene_phase2_module_skeleton_backlog_plan(REPO_ROOT)

    assert first["plan_hash"] == second["plan_hash"]
    assert first["status"] == "V2_HYGIENE_PHASE2_MODULE_SKELETON_BACKLOG_PLAN_READY"
    assert first["source_ready"] is True
    assert first["module_summary"]["total_module_count"] == 4
    assert first["module_summary"]["blocked_module_count"] == 4
    assert first["deliverable_summary"]["total_deliverable_count"] == 5
    assert first["deliverable_summary"]["high_priority_deliverable_count"] == 2
    assert first["deliverable_summary"]["blocked_deliverable_count"] == 5
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_v2_hygiene_phase2_module_skeleton_backlog_plan_denies_implementation_authority() -> None:
    packet = build_v2_hygiene_phase2_module_skeleton_backlog_plan(REPO_ROOT)

    assert packet["implementation_authorized"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["valid_for_execution"] is False
    assert packet["safe_to_prepare_patch"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["acceptance_gate_summary"]["safe_to_create_module_code"] is False
    assert packet["acceptance_gate_summary"]["safe_to_create_module_tests"] is False
    assert packet["acceptance_gate_summary"]["safe_to_register_modules"] is False
    assert packet["acceptance_gate_summary"]["safe_to_integrate_hygiene_pipeline"] is False
    assert packet["acceptance_gate_summary"]["safe_to_promote_out_of_advisory"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert all(
        module["module_creation_authorized"] is False
        for module in packet["module_records"]
    )
    assert all(
        deliverable["implementation_authorized"] is False
        for deliverable in packet["deliverable_records"]
    )


def test_v2_hygiene_phase2_module_skeleton_backlog_plan_maps_notion_modules() -> None:
    packet = build_v2_hygiene_phase2_module_skeleton_backlog_plan(REPO_ROOT)
    modules = {module["module_id"]: module for module in packet["module_records"]}
    deliverables = {
        deliverable["deliverable_id"]: deliverable
        for deliverable in packet["deliverable_records"]
    }

    assert modules["retrocausal_signal_hygiene_module"]["owner_runes"] == [
        "LoopAwarenessRune",
        "HyperstitionTagRune",
    ]
    assert modules["mandatory_output_schema_enforcer"]["planned_repo_path"] == (
        "abraxas/v2/modules/output_schema_enforcer"
    )
    assert modules["self_adversarial_testing_loop"]["initial_posture"] == "ADVISORY_ONLY"
    assert modules["hyperstition_potency_evaluator"]["owner_runes"] == [
        "HyperstitionTagRune"
    ]
    assert deliverables["phase2_high_001"]["deliverable"] == "Four module skeleton classes"
    assert deliverables["phase2_medium_004"]["deliverable"] == (
        "Promotion criteria documentation"
    )
    assert packet["phase3_status"] == "PLACEHOLDER_HELD_FOR_FUTURE_DETAIL"
    assert packet["phase4_status"] == "PLACEHOLDER_HELD_FOR_FUTURE_DETAIL"


def test_v2_hygiene_phase2_module_skeleton_backlog_plan_fails_closed_without_sources(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_phase2_module_skeleton_backlog_plan(tmp_path)

    assert packet["status"] == "V2_HYGIENE_PHASE2_MODULE_SKELETON_BACKLOG_PLAN_BLOCKED"
    assert packet["source_ready"] is False
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["implementation_authorized"] is False
    assert packet["blockers"]


def test_v2_hygiene_phase2_module_skeleton_backlog_plan_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase2_module_skeleton_backlog_plan(REPO_ROOT)
    packet_without_hash = dict(packet)
    plan_hash = packet_without_hash.pop("plan_hash")
    assert plan_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_phase2_module_skeleton_backlog_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase2_module_skeleton_backlog_plan(
        REPO_ROOT, out_root=tmp_path
    )
    out_json = tmp_path / "out/sync/v2_hygiene_phase2_module_skeleton_backlog_plan/latest.json"
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase2_module_skeleton_backlog_plan.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["plan_hash"] == packet["plan_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_phase2_module_skeleton_backlog_plan_markdown() -> None:
    packet = build_v2_hygiene_phase2_module_skeleton_backlog_plan(REPO_ROOT)
    markdown = render_v2_hygiene_phase2_module_skeleton_backlog_plan_markdown(packet)

    assert markdown[0] == "# v2.0 Hygiene Phase 2 Module Skeleton Backlog Plan"
    assert any("retrocausal_signal_hygiene_module" in line for line in markdown)
    assert any("phase2_high_001" in line for line in markdown)
    assert any("blocked_module_count" in line for line in markdown)
