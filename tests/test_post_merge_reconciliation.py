"""Tests for core/codegen/post_merge_reconciliation.py (HARDENING candidate cd8c18b3c85c2410)"""

from core.codegen.post_merge_reconciliation import (
    build_post_merge_reconciliation_receipt,
    build_continuity_signal,
)

def test_build_receipt_shape_and_locks():
    completion_receipt = {
        "observed_path_count": 42,
        "required_path_count": 50,
        "canonical_hash": "abc123",
        "spine_status": "COMPLETE",
    }
    phase_merge_refs = {"phase_a": "ref1", "phase_b": "ref2"}
    continuity_signals = [
        build_continuity_signal(path="p1", status="OK", detail="detail1"),
        build_continuity_signal(path="p2", status="PARTIAL", detail="detail2"),
    ]
    receipt = build_post_merge_reconciliation_receipt(
        timestamp="2026-07-12T00:00:00Z",
        completion_receipt=completion_receipt,
        phase_merge_refs=phase_merge_refs,
        continuity_signals=continuity_signals,
    )
    assert isinstance(receipt, dict)
    assert receipt["schema_version"] == "AbxCodegenPostMergeReconciliation.v1"
    assert receipt["receipt_status"] == "ABX_CODEGEN_SPINE_POST_MERGE_RECONCILED"
    assert receipt["path_coverage"] == "42/50"
    locks = receipt["authority_locks"]
    assert locks["advisory_only"] is True
    assert locks["canon_mutation"] is False
    assert locks["production_activation"] is False
    assert receipt["valid_for_execution"] is False
    assert receipt["valid_for_canon_promotion"] is False
    assert "canonical_hash" in receipt

def test_build_continuity_signal():
    sig = build_continuity_signal(path="test/path", status="INFERRED", detail="test detail")
    assert sig["path"] == "test/path"
    assert sig["status"] == "INFERRED"
    assert sig["valid_for_execution"] is False

def test_receipt_with_empty_signals():
    receipt = build_post_merge_reconciliation_receipt(
        timestamp="2026-07-12T00:00:00Z",
        completion_receipt={"observed_path_count": 0, "required_path_count": 10, "canonical_hash": "def456"},
        phase_merge_refs={},
        continuity_signals=[],
    )
    assert receipt["path_coverage"] == "0/10"
    assert receipt["continuity_signals"] == []
