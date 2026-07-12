"""Tests for core/abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt.py

GOVERNANCE class candidate.

Covers receipt building, status transitions, snapshot logic, scoped readiness, post-regeneration validation, markdown rendering, and governance preservation invariants.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from core.abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt import (
    build_abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt,
    render_markdown,
    write_abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt,
    _scoped_receipt_ready,
    _post_regeneration_valid,
    _audit_snapshot,
    NOT_COMPUTABLE,
)


def test_scoped_receipt_ready_true():
    ready = {
        "schema_version": "AbxResearchCanaryOrphanOutputRegistryInclusionScopedExecutionReceipt.v1",
        "status": "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_SCOPED_EXECUTION_RECEIPT_EMITTED",
        "registry_mutation_performed": True,
        "recommended_next_lane": "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_AUDIT_REGENERATION_RECEIPT_001",
    }
    assert _scoped_receipt_ready(ready) is True


def test_scoped_receipt_ready_false():
    not_ready = {"status": "BLOCKED"}
    assert _scoped_receipt_ready(not_ready) is False


def test_post_regeneration_valid_true():
    post = {
        "audit_id": "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_AUDIT_001",
        "coverage_summary": {
            "orphan_research_output_count": 0,
            "lane_id_gap_count": 0,
            "output_path_gap_count": 0,
        },
    }
    assert _post_regeneration_valid(post) is True


def test_post_regeneration_valid_false():
    post = {"coverage_summary": {"orphan_research_output_count": 5}}
    assert _post_regeneration_valid(post) is False


def test_audit_snapshot():
    audit = {"audit_hash": "abc", "audit_status": "COMPLETE", "coverage_summary": {"orphan_research_output_count": 3}}
    snap = _audit_snapshot(audit)
    assert snap["orphan_research_output_count"] == 3


def test_build_receipt_blocked_when_not_ready(tmp_path):
    # No scoped receipt present → blocked
    receipt = build_abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt(source_root=tmp_path)
    assert receipt["status"] == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_AUDIT_REGENERATION_RECEIPT_BLOCKED"
    assert receipt["advisory_only"] is True
    assert receipt["projection_only"] is True


def test_render_markdown():
    packet = {
        "status": "EMITTED",
        "downstream_status": "COMPLETE",
        "included_orphan_path_count": 12,
    }
    lines = render_markdown(packet)
    assert any("EMITTED" in line for line in lines)
    assert any("12" in line for line in lines)


def test_write_receipt_creates_files(tmp_path):
    # Minimal happy path by mocking dependencies
    with patch("core.abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt._scoped_receipt_ready", return_value=True), \
         patch("core.abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt.build_abx_research_canary_artifact_registry_coverage_audit", return_value={"audit_id": "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_AUDIT_001", "coverage_summary": {"orphan_research_output_count": 0, "lane_id_gap_count": 0, "output_path_gap_count": 0}}), \
         patch("core.abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt._post_regeneration_valid", return_value=True):
        
        receipt = write_abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt(source_root=tmp_path, out_root=tmp_path)
        assert receipt["status"].endswith("_EMITTED")
        json_path = tmp_path / "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt_001.latest.json"
        md_path = tmp_path / "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt_001.latest.md"
        assert json_path.exists()
        assert md_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
