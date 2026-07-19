from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.notion_repo_sync_audit_writeback_receipt import (
    AUTHORITY_LOCKS,
    build_notion_repo_sync_audit_writeback_receipt,
)
from scripts.notion import run_notion_repo_sync_audit_writeback_receipt

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/notion_repo_sync_audit_writeback_receipt.v1.schema.json"


def test_notion_repo_sync_audit_writeback_receipt_is_advisory_only() -> None:
    packet = build_notion_repo_sync_audit_writeback_receipt(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "NotionRepoSyncAuditWritebackReceipt.v1"
    assert packet["receipt_id"] == "ABRAXAS_NOTION_REPO_SYNC_AUDIT_WRITEBACK_RECEIPT_001"
    assert packet["receipt_status"] == "NOTION_REPO_SYNC_AUDIT_WRITEBACK_RECEIPT_READY_ADVISORY_ONLY"
    assert packet["source_readiness"] == "SOURCE_ARTIFACTS_READY"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False
    assert packet["valid_for_execution"] is False
    assert packet["authority_locks"] == AUTHORITY_LOCKS
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["writeback_scope"]["operator_authorized_this_sync_writeback"] is True
    assert packet["writeback_scope"]["observed_writeback_page_url"] == (
        "https://app.notion.com/p/3823e8ba2f5c8199ae13c04610f89801"
    )
    assert packet["writeback_scope"]["writeback_global_authority_granted"] is False
    assert packet["writeback_scope"]["writeback_allows_future_automation"] is False
    assert packet["execution_authority"] is False
    assert packet["github_writeback_allowed"] is False


def test_source_artifacts_are_observed_and_ordered() -> None:
    packet = build_notion_repo_sync_audit_writeback_receipt(repo_root=REPO_ROOT)

    records = packet["source_artifact_records"]
    assert [record["source_id"] for record in records] == sorted(
        record["source_id"] for record in records
    )
    assert all(record["classification"] == "OBSERVED" for record in records)
    assert all(record["authority_drift_observed"] is False for record in records)
    assert any(
        record["source_id"] == "completion_validation_approval_gate"
        and record["source_hash"]
        == "522010e1faf62fe1f006ae3050928bad12db1412da9a71702f75623bbc8487d7"
        for record in records
    )


def test_notion_sources_record_stale_status_without_authority() -> None:
    packet = build_notion_repo_sync_audit_writeback_receipt(repo_root=REPO_ROOT)

    classifications = {
        record["source_id"]: record["classification"]
        for record in packet["notion_source_records"]
    }
    assert classifications["live_status_dashboard_2026_06_12"] == "STALE_STATUS_BASELINE"
    assert (
        classifications["canon_spine"]
        == "P130_P132_REFERENCE_STALE_UNLESS_REAUTHORIZED"
    )
    assert packet["decision_record_creation_authorized"] is False
    assert packet["activation_authorized"] is False
    assert packet["promotion_authorized"] is False
    assert packet["registration_authorized"] is False


def test_missing_source_artifact_fails_closed(tmp_path: Path) -> None:
    packet = build_notion_repo_sync_audit_writeback_receipt(repo_root=tmp_path)

    assert packet["receipt_status"] == "NOTION_REPO_SYNC_AUDIT_WRITEBACK_RECEIPT_NOT_COMPUTABLE"
    assert packet["source_readiness"] == "NOT_COMPUTABLE"
    assert packet["source_blockers"]
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False
    assert packet["valid_for_execution"] is False


def test_authority_expanding_source_fails_closed(tmp_path: Path) -> None:
    source_path = (
        tmp_path
        / "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate_001.latest.json"
    )
    payload = {
        "status": "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_APPROVAL_GATE_READY_FOR_SEPARATE_RECORD_COMPLETION_VALIDATION_PLANNING",
        "execution_authority": True,
    }
    write_canonical_json(source_path, payload)

    packet = build_notion_repo_sync_audit_writeback_receipt(repo_root=tmp_path)

    record = next(
        record
        for record in packet["source_artifact_records"]
        if record["source_id"] == "completion_validation_approval_gate"
    )
    assert record["classification"] == "AUTHORITY_DRIFT"
    assert record["authority_drift_keys"] == ["execution_authority"]
    assert packet["receipt_status"] == "NOTION_REPO_SYNC_AUDIT_WRITEBACK_RECEIPT_NOT_COMPUTABLE"
    assert packet["valid_for_execution"] is False


def test_hash_and_schema_validation() -> None:
    packet = build_notion_repo_sync_audit_writeback_receipt(repo_root=REPO_ROOT)
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))

    validate(packet, schema)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)


def test_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = tmp_path / "out/audit/notion_repo_sync_audit_writeback_receipt_001.latest.json"
    out_md = tmp_path / "out/audit/notion_repo_sync_audit_writeback_receipt_001.latest.md"

    first = run_notion_repo_sync_audit_writeback_receipt.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_notion_repo_sync_audit_writeback_receipt.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
    assert first_md.startswith("# Notion Repo Sync Audit Writeback Receipt 001\n")
