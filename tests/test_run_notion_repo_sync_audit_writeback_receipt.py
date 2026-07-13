"""Tests for core/notion_repo_sync_audit_writeback_receipt.py (candidate f9e1235de3b6756f)"""

from core.notion_repo_sync_audit_writeback_receipt import (
    ARTIFACT_TYPE,
    RECEIPT_ID,
    RECEIPT_STATUS_READY,
    RECEIPT_STATUS_NOT_COMPUTABLE,
    AUTHORITY_LOCKS,
    DANGEROUS_TRUE_KEYS,
)

def test_artifact_and_ids():
    assert ARTIFACT_TYPE == "NotionRepoSyncAuditWritebackReceipt.v1"
    assert RECEIPT_ID == "ABRAXAS_NOTION_REPO_SYNC_AUDIT_WRITEBACK_RECEIPT_001"
    assert RECEIPT_STATUS_READY == "NOTION_REPO_SYNC_AUDIT_WRITEBACK_RECEIPT_READY_ADVISORY_ONLY"
    assert RECEIPT_STATUS_NOT_COMPUTABLE == "NOTION_REPO_SYNC_AUDIT_WRITEBACK_RECEIPT_NOT_COMPUTABLE"

def test_authority_locks_all_false():
    assert all(v is False for v in AUTHORITY_LOCKS.values())
    assert len(AUTHORITY_LOCKS) >= 10

def test_dangerous_true_keys():
    assert "canon_mutation" in DANGEROUS_TRUE_KEYS
    assert "notion_writeback_allowed" in DANGEROUS_TRUE_KEYS
    assert len(DANGEROUS_TRUE_KEYS) > 5
