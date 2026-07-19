from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.notion_writeback_dry_run_plan import (
    OUT_JSON,
    OUT_MD,
    PLAN_ID,
    build_notion_writeback_dry_run_plan,
)
from scripts.notion import run_notion_writeback_dry_run_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/notion_writeback_dry_run_plan.v1.schema.json"


def test_dry_run_plan_fails_closed_without_target() -> None:
    packet = build_notion_writeback_dry_run_plan(repo_root=REPO_ROOT)

    assert packet["plan_id"] == PLAN_ID
    assert packet["plan_status"] == "NOT_COMPUTABLE"
    assert packet["target_state"] == "TARGET_NOT_CONFIGURED"
    assert packet["planned_operations"] == []
    assert packet["writeback_performed"] is False
    assert packet["notion_writeback"] is False
    assert packet["valid_for_execution"] is False


def test_configured_dry_run_plans_only_allowlisted_operations(tmp_path: Path) -> None:
    source = tmp_path / "out/sync/sync_snapshot.latest.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Sync\n", encoding="utf-8")

    packet = build_notion_writeback_dry_run_plan(
        repo_root=tmp_path,
        target_page_id="page_123",
        target_label="ABX Sync Index",
        source_artifacts=("out/sync/sync_snapshot.latest.md",),
    )

    assert packet["plan_status"] == "DRY_RUN_PLAN_READY"
    assert packet["target_state"] == "TARGET_CONFIGURED"
    assert [op["operation_id"] for op in packet["planned_operations"]] == [
        "notion_update_allowed_properties",
        "notion_append_sync_receipt",
    ]
    assert all(op["dry_run_only"] is True for op in packet["planned_operations"])
    assert all(op["requires_operator_authorization_record"] is True for op in packet["planned_operations"])
    assert packet["source_artifact_hashes"]["out/sync/sync_snapshot.latest.md"] == hashlib.sha256(
        source.read_bytes()
    ).hexdigest()


def test_authority_locks_and_forbidden_actions_remain_fail_closed() -> None:
    packet = build_notion_writeback_dry_run_plan(
        repo_root=REPO_ROOT,
        target_page_id="page_123",
        target_label="ABX Sync Index",
    )

    assert packet["writeback_authorized"] is False
    assert packet["github_writeback"] is False
    assert packet["dry_run_only"] is True
    assert all(value is False for value in packet["authority_locks"].values())
    assert "unverified_notion_write" in packet["forbidden_actions"]
    assert "canon_promotion" in packet["forbidden_actions"]


def test_schema_validates_packet_and_hash_is_stable() -> None:
    packet = build_notion_writeback_dry_run_plan(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_runner_writes_byte_stable_artifacts(tmp_path: Path) -> None:
    source = tmp_path / "out/sync/sync_snapshot.latest.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Sync\n", encoding="utf-8")
    out_json = tmp_path / "out/sync/notion_writeback_dry_run_plan/latest.json"
    out_md = tmp_path / "out/sync/notion_writeback_dry_run_plan/latest.md"

    first = run_notion_writeback_dry_run_plan.run(
        repo_root=tmp_path,
        out_json=out_json,
        out_md=out_md,
        target_page_id="page_123",
        target_label="ABX Sync Index",
        source_artifacts=("out/sync/sync_snapshot.latest.md",),
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_notion_writeback_dry_run_plan.run(
        repo_root=tmp_path,
        out_json=out_json,
        out_md=out_md,
        target_page_id="page_123",
        target_label="ABX Sync Index",
        source_artifacts=("out/sync/sync_snapshot.latest.md",),
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_repo_output_path_constants() -> None:
    assert run_notion_writeback_dry_run_plan.OUT_JSON == OUT_JSON
    assert run_notion_writeback_dry_run_plan.OUT_MD == OUT_MD
