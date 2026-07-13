"""Tests for core/sync/documentation_alignment_receipt.py (GOVERNANCE candidate a60256f3530cb219)"""

from pathlib import Path

from core.sync.documentation_alignment_receipt import (
    build_documentation_alignment_receipt,
    _source_hashes,
    SOURCE_ARTIFACT_PATHS,
)

def test_build_documentation_alignment_receipt():
    receipt = build_documentation_alignment_receipt(".")
    assert receipt["artifact_type"] == "DocumentationAlignmentReceipt.v1"
    assert "source_artifact_hashes" in receipt
    assert isinstance(receipt["source_artifact_hashes"], dict)
    assert len(receipt["source_artifact_hashes"]) == len(SOURCE_ARTIFACT_PATHS)
    assert receipt["status"] == "DOCUMENTATION_ALIGNMENT_RECEIPT_EMITTED_ADVISORY_ONLY"

def test_source_hashes_structure():
    root = Path(".")
    hashes = _source_hashes(root)
    assert isinstance(hashes, dict)
    for path in list(SOURCE_ARTIFACT_PATHS)[:3]:
        assert path in hashes
        val = hashes[path]
        assert val == "NOT_COMPUTABLE" or (isinstance(val, str) and len(val) == 64)
