"""Phase 11 production-convergence writer migration."""

from __future__ import annotations

from pathlib import Path

from core.production_convergence.phase11 import (
    MIGRATED_PATHS,
    build_phase11_writer_migration_receipt,
)

REPO = Path(__file__).resolve().parents[1]


def test_phase11_receipt_and_migrated_paths() -> None:
    receipt = build_phase11_writer_migration_receipt()
    assert receipt["schema_version"] == "phase11_writer_migration.v1"
    assert receipt["candidate_status"] == "NOT_READY"
    assert receipt["external_production_authorized"] is False
    assert receipt["summary"]["migrated_count"] == 7
    assert receipt["summary"]["doctrine_count"] == 1
    assert receipt["summary"]["fusion_count"] == 2
    assert receipt["summary"]["shadow_count"] == 1
    assert receipt["summary"]["governance_spine_count"] == 3
    assert len(receipt["canonical_hash"]) == 64
    for rel in MIGRATED_PATHS:
        text = (REPO / rel).read_text(encoding="utf-8")
        assert "write_classified_json" in text, rel
        assert "write_canonical_json(" not in text, rel
