from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.notion_writeback_authorization_gate import (
    GATE_ID,
    build_notion_writeback_authorization_gate,
)
from core.sync.notion_writeback_dry_run_plan import build_notion_writeback_dry_run_plan
from scripts import run_notion_writeback_authorization_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/notion_writeback_authorization_gate.v1.schema.json"


def test_gate_fails_closed_when_dry_run_is_not_ready() -> None:
    packet = build_notion_writeback_authorization_gate(repo_root=REPO_ROOT)

    assert packet["gate_id"] == GATE_ID
    assert packet["gate_status"] == "NOT_COMPUTABLE"
    assert packet["dry_run_plan_ready"] is False
    assert packet["writeback_authorized"] is False
    assert packet["writeback_performed"] is False
    assert packet["notion_writeback"] is False
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_gate_requires_operator_authorization_after_ready_dry_run(tmp_path: Path) -> None:
    dry_run = build_notion_writeback_dry_run_plan(
        repo_root=REPO_ROOT,
        target_page_id="page_123",
        target_label="ABX Sync Index",
    )
    dry_run_path = tmp_path / "out/sync/notion_writeback_dry_run_plan/latest.json"
    write_canonical_json(dry_run_path, dry_run)

    packet = build_notion_writeback_authorization_gate(
        repo_root=tmp_path,
        dry_run_plan_path="out/sync/notion_writeback_dry_run_plan/latest.json",
    )

    assert packet["gate_status"] == "OPERATOR_AUTHORIZATION_REQUIRED"
    assert packet["dry_run_plan_ready"] is True
    assert packet["operator_authorization_observed"] is False
    assert packet["eligible_for_mutation_gate_planning"] is False
    assert packet["writeback_authorized"] is False


def test_gate_becomes_planning_eligible_with_nonexecuting_operator_record(tmp_path: Path) -> None:
    dry_run = build_notion_writeback_dry_run_plan(
        repo_root=REPO_ROOT,
        target_page_id="page_123",
        target_label="ABX Sync Index",
    )
    dry_run_path = tmp_path / "out/sync/notion_writeback_dry_run_plan/latest.json"
    auth_path = tmp_path / "input/notion_writeback_operator_authorization.json"
    write_canonical_json(dry_run_path, dry_run)
    write_canonical_json(
        auth_path,
        {
            "artifact_type": "NotionWritebackOperatorAuthorization.v1",
            "operator_decision": "APPROVE_NOTION_WRITEBACK_DRY_RUN_TO_MUTATION_GATE",
            "authorizes_live_writeback": False,
            "authorizes_mutation_gate_planning": True,
            "advisory_only": True,
        },
    )

    packet = build_notion_writeback_authorization_gate(
        repo_root=tmp_path,
        dry_run_plan_path="out/sync/notion_writeback_dry_run_plan/latest.json",
        operator_authorization_path="input/notion_writeback_operator_authorization.json",
    )

    assert packet["gate_status"] == "MUTATION_GATE_PLANNING_ELIGIBLE"
    assert packet["eligible_for_mutation_gate_planning"] is True
    assert packet["recommended_next_lane"] == "NOTION_WRITEBACK_MUTATION_GATE_PLAN"
    assert packet["writeback_authorized"] is False
    assert packet["notion_writeback"] is False


def test_schema_validates_packet_and_hash_is_stable() -> None:
    packet = build_notion_writeback_authorization_gate(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_runner_writes_byte_stable_artifacts(tmp_path: Path) -> None:
    out_json = tmp_path / "out/sync/notion_writeback_authorization_gate/latest.json"
    out_md = tmp_path / "out/sync/notion_writeback_authorization_gate/latest.md"
    first = run_notion_writeback_authorization_gate.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_notion_writeback_authorization_gate.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
