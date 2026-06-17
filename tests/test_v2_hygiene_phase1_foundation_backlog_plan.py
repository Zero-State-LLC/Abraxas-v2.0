from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_hygiene_phase1_foundation_backlog_plan import (
    build_v2_hygiene_phase1_foundation_backlog_plan,
    render_v2_hygiene_phase1_foundation_backlog_plan_markdown,
    write_v2_hygiene_phase1_foundation_backlog_plan,
)
from scripts import run_v2_hygiene_phase1_foundation_backlog_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/v2_hygiene_phase1_foundation_backlog_plan.v1.schema.json"


def test_v2_hygiene_phase1_foundation_backlog_plan_ready() -> None:
    first = build_v2_hygiene_phase1_foundation_backlog_plan(REPO_ROOT)
    second = build_v2_hygiene_phase1_foundation_backlog_plan(REPO_ROOT)

    assert first["plan_hash"] == second["plan_hash"]
    assert first["status"] == "V2_HYGIENE_PHASE1_FOUNDATION_BACKLOG_PLAN_READY"
    assert first["source_ready"] is True
    assert first["task_summary"]["total_task_count"] == 14
    assert first["task_summary"]["p0_task_count"] == 6
    assert first["task_summary"]["blocked_task_count"] == 14
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_v2_hygiene_phase1_foundation_backlog_plan_denies_implementation_authority() -> None:
    packet = build_v2_hygiene_phase1_foundation_backlog_plan(REPO_ROOT)

    assert packet["implementation_authorized"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["valid_for_execution"] is False
    assert packet["safe_to_prepare_patch"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["acceptance_gate_summary"]["safe_to_create_hygiene_code"] is False
    assert packet["acceptance_gate_summary"]["safe_to_create_schema_files"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert all(task["implementation_authorized"] is False for task in packet["task_records"])


def test_v2_hygiene_phase1_foundation_backlog_plan_maps_notion_priorities() -> None:
    packet = build_v2_hygiene_phase1_foundation_backlog_plan(REPO_ROOT)
    tasks = {task["task_id"]: task for task in packet["task_records"]}

    assert tasks["phase1_p0_001"]["task"] == "Set up folder structure"
    assert tasks["phase1_p0_002"]["repo_path"] == "abraxas/v2/hygiene/loop_dynamics.py"
    assert tasks["phase1_p0_006"]["task"] == "Implement LoopAwarenessRune"
    assert tasks["phase1_p1_010"]["task"] == "Implement remaining 3 runes"
    assert tasks["phase1_p2_012"]["deliverable"] == "loop_dynamics and output_register schemas"
    assert {source["title"] for source in packet["notion_phase1_sources"]} >= {
        "Phase 1: Foundations & Hygiene Layer",
        "v2.0 Schema Contracts",
        "Versioning & Release Hygiene Policy",
        "Phase 1 - Implementation Checklist",
    }


def test_v2_hygiene_phase1_foundation_backlog_plan_fails_closed_without_sources(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_phase1_foundation_backlog_plan(tmp_path)

    assert packet["status"] == "V2_HYGIENE_PHASE1_FOUNDATION_BACKLOG_PLAN_BLOCKED"
    assert packet["source_ready"] is False
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["implementation_authorized"] is False
    assert packet["blockers"]


def test_v2_hygiene_phase1_foundation_backlog_plan_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_foundation_backlog_plan(REPO_ROOT)
    packet_without_hash = dict(packet)
    plan_hash = packet_without_hash.pop("plan_hash")
    assert plan_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_phase1_foundation_backlog_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_foundation_backlog_plan(REPO_ROOT, out_root=tmp_path)
    out_json = tmp_path / "out/sync/v2_hygiene_phase1_foundation_backlog_plan/latest.json"
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_foundation_backlog_plan.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["plan_hash"] == packet["plan_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_phase1_foundation_backlog_plan_markdown() -> None:
    packet = build_v2_hygiene_phase1_foundation_backlog_plan(REPO_ROOT)
    markdown = render_v2_hygiene_phase1_foundation_backlog_plan_markdown(packet)

    assert markdown[0] == "# v2.0 Hygiene Phase 1 Foundation Backlog Plan"
    assert any("phase1_p0_001" in line for line in markdown)
    assert any("blocked_task_count" in line for line in markdown)
