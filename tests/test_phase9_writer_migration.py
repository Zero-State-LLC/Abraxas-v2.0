"""Phase 9 production-convergence writer migration + CLEAR analysis."""

from __future__ import annotations

from pathlib import Path

from core.production_convergence.clear_reference import build_clear_reference_analysis
from core.production_convergence.phase9 import (
    MIGRATED_PATHS,
    build_phase9_writer_migration_receipt,
)

REPO = Path(__file__).resolve().parents[1]


def test_phase9_receipt_and_migrated_paths() -> None:
    receipt = build_phase9_writer_migration_receipt()
    assert receipt["schema_version"] == "phase9_writer_migration.v1"
    assert receipt["candidate_status"] == "NOT_READY"
    assert receipt["summary"]["migrated_count"] == 20
    assert receipt["summary"]["replay_count"] == 12
    assert receipt["summary"]["viz_count"] == 8
    assert len(receipt["canonical_hash"]) == 64
    for rel in MIGRATED_PATHS:
        text = (REPO / rel).read_text(encoding="utf-8")
        assert "write_classified_json" in text
        assert "write_canonical_json(" not in text


def test_clear_reference_analysis_advisory() -> None:
    report = build_clear_reference_analysis(REPO)
    assert report["schema_version"] == "clear_reference_analysis.v1"
    assert report["mode"] == "advisory_report_only"
    assert report["fail_closed"] is False
    assert report["mass_deletion_authorized"] is False
    assert report["external_production_authorized"] is False
    assert report["candidate_status"] == "NOT_READY"
    assert report["summary"]["entry_count"] >= 1
    assert len(report["canonical_hash"]) == 64
    for entry in report["entries"]:
        assert entry["recommended_action"] in {
            "KEEP",
            "DEPRECATE_DOCUMENT_ONLY",
            "DEFER_CLEAR",
            "MERGE_CANDIDATE",
        }
