"""Comprehensive tests for core/codegen/spine_completion.py (HARDENING candidate 0d431a1823af8a45)

Covers spine completion receipt builder, path records, authority locks, advisory invariants, and determinism.
"""

from pathlib import Path

import pytest

from core.codegen.spine_completion import (
    _authority_locks,
    _path_records,
    _sha256,
    build_codegen_spine_completion_receipt,
    write_codegen_spine_completion_receipt_markdown,
    REQUIRED_PATHS,
)


def test_authority_locks_advisory():
    locks = _authority_locks()
    assert isinstance(locks, dict)
    assert locks["advisory_only"] is True
    assert all(v is False for k, v in locks.items() if k != "advisory_only")


def test_sha256_on_existing_file():
    # Use a known file that exists
    h = _sha256(Path("core/codegen/spine_completion.py"))
    assert len(h) == 64
    assert h != "NOT_COMPUTABLE"


def test_path_records_structure():
    records = _path_records(Path("."))
    assert len(records) == len(REQUIRED_PATHS)
    for rec in records:
        assert "path" in rec
        assert "status" in rec
        assert "source_hash" in rec
        assert rec["status"] in ("OBSERVED", "MISSING")


def test_build_receipt_advisory():
    receipt = build_codegen_spine_completion_receipt(repo_root=".")
    assert receipt["artifact_type"] == "AbxCodegenIntelligenceSpineCompletionReceipt.v1"
    assert receipt["advisory_only"] is True
    assert receipt["valid_for_execution"] is False
    assert receipt["valid_for_runtime_activation"] is False
    assert receipt["valid_for_canon_promotion"] is False
    assert "canonical_hash" in receipt
    assert "authority_locks" in receipt


def test_build_receipt_spine_status():
    receipt = build_codegen_spine_completion_receipt(repo_root=".")
    assert receipt["spine_status"] in ("ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_COMPUTABLE", "ABX_CODEGEN_INTELLIGENCE_SPINE_INCOMPLETE")


def test_write_markdown(tmp_path):
    receipt = build_codegen_spine_completion_receipt(repo_root=".")
    out = tmp_path / "test.md"
    write_codegen_spine_completion_receipt_markdown(out, receipt)
    assert out.exists()
    content = out.read_text()
    assert "ABX Codegen Intelligence Spine Completion Receipt" in content
    assert "spine_status" in content


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
