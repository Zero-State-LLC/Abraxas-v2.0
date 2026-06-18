from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_hygiene_loop_awareness_alignment_plan import (
    build_v2_hygiene_loop_awareness_alignment_plan,
    render_v2_hygiene_loop_awareness_alignment_plan_markdown,
)
from scripts import run_v2_hygiene_loop_awareness_alignment_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/v2_hygiene_loop_awareness_alignment_plan.v1.schema.json"


def test_v2_hygiene_alignment_plan_ready_and_advisory() -> None:
    packet = build_v2_hygiene_loop_awareness_alignment_plan(REPO_ROOT)

    assert packet["artifact_type"] == "V2HygieneLoopAwarenessAlignmentPlan.v1"
    assert packet["plan_status"] == "V2_HYGIENE_LOOP_AWARENESS_ALIGNMENT_PLAN_READY"
    assert packet["source_audit_ready"] is True
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["safe_to_prepare_patch"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["evidence_only"] is True
    assert packet["valid_for_execution"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_v2_hygiene_alignment_plan_reflects_ready_audit_posture() -> None:
    packet = build_v2_hygiene_loop_awareness_alignment_plan(REPO_ROOT)
    workstreams = {
        item["workstream"]: item for item in packet["planned_work_items"]
    }

    assert packet["source_audit_status"] == "V2_HYGIENE_LOOP_AWARENESS_AUDIT_READY"
    assert packet["alignment_required_count"] == 0
    assert packet["alignment_required_workstreams"] == []
    assert len(workstreams) == 7
    assert all(item["alignment_required"] is False for item in packet["planned_work_items"])
    assert all(item["source_check_status"] == "PASSED" for item in packet["planned_work_items"])
    assert all(item["authority_granted"] is False for item in packet["planned_work_items"])


def test_v2_hygiene_alignment_plan_fails_closed_without_source(tmp_path: Path) -> None:
    packet = build_v2_hygiene_loop_awareness_alignment_plan(tmp_path)

    assert packet["plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_audit_observed"] is False
    assert packet["source_audit_ready"] is False
    assert packet["source_audit_hash"] == "NOT_COMPUTABLE"
    assert packet["planned_work_items"] == []
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["valid_for_execution"] is False


def test_v2_hygiene_alignment_plan_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_loop_awareness_alignment_plan(REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("plan_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_alignment_plan_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = tmp_path / "out/sync/v2_hygiene_loop_awareness_alignment_plan/latest.json"
    out_md = tmp_path / "out/sync/v2_hygiene_loop_awareness_alignment_plan/latest.md"

    first = run_v2_hygiene_loop_awareness_alignment_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_loop_awareness_alignment_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_alignment_plan_markdown_names_gates() -> None:
    packet = build_v2_hygiene_loop_awareness_alignment_plan(REPO_ROOT)
    markdown = render_v2_hygiene_loop_awareness_alignment_plan_markdown(packet)

    assert markdown[0] == "# v2.0 Hygiene Loop-Awareness Alignment Plan"
    assert any("V2-HYGIENE-GATE-001" in line for line in markdown)
    assert any("safe_to_auto_continue" in line for line in markdown)
