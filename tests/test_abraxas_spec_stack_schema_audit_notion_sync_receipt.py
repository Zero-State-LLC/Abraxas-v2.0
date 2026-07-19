from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abraxas_spec_stack_schema_audit_notion_sync_receipt import (
    OUT_PATH,
    build_abraxas_spec_stack_schema_audit_notion_sync_receipt,
    write_abraxas_spec_stack_schema_audit_notion_sync_receipt,
)
from core.abraxas_spec_stack_schema_audit_common import spec_stack_governance_envelope
from core.canonical.json import canonical_hash
from scripts.codegen import run_abraxas_spec_stack_schema_audit_notion_sync_receipt

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/abraxas_spec_stack_schema_audit_notion_sync_receipt.v1.schema.json"
)


def test_notion_sync_receipt_governance_envelope() -> None:
    packet = build_abraxas_spec_stack_schema_audit_notion_sync_receipt(REPO_ROOT)
    for key, value in spec_stack_governance_envelope().items():
        assert packet[key] == value


def test_notion_sync_receipt_ready_when_sources_present() -> None:
    packet = build_abraxas_spec_stack_schema_audit_notion_sync_receipt(REPO_ROOT)
    assert packet["status"] == "ABRAXAS_SPEC_STACK_SCHEMA_AUDIT_NOTION_SYNC_RECEIPT_READY"
    assert packet["packet_blockers"] == []
    assert packet["manual_operator_copy_paste_only"] is True


def test_notion_sync_receipt_schema_validates() -> None:
    packet = build_abraxas_spec_stack_schema_audit_notion_sync_receipt(REPO_ROOT)
    without_hash = dict(packet)
    sync_receipt_hash = without_hash.pop("sync_receipt_hash")
    assert sync_receipt_hash == canonical_hash(without_hash)
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_notion_sync_receipt_denies_authority() -> None:
    packet = build_abraxas_spec_stack_schema_audit_notion_sync_receipt(REPO_ROOT)
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["notion_writeback_allowed"] is False
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_notion_sync_receipt_runner_writes_stable_outputs(tmp_path: Path) -> None:
    packet = write_abraxas_spec_stack_schema_audit_notion_sync_receipt(
        REPO_ROOT,
        out_root=tmp_path,
    )
    target = tmp_path / OUT_PATH
    md_target = target.with_suffix(".md")
    first_json = target.read_text(encoding="utf-8")
    first_md = md_target.read_text(encoding="utf-8")
    second = run_abraxas_spec_stack_schema_audit_notion_sync_receipt.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )
    assert second["sync_receipt_hash"] == packet["sync_receipt_hash"]
    assert first_json == target.read_text(encoding="utf-8")
    assert first_md == md_target.read_text(encoding="utf-8")


def test_notion_sync_receipt_lists_six_notion_surfaces() -> None:
    packet = build_abraxas_spec_stack_schema_audit_notion_sync_receipt(REPO_ROOT)
    assert len(packet["notion_sync_surfaces"]) == 6
