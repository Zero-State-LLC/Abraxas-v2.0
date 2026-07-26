"""Phase 8 production-convergence writer migration receipt."""

from __future__ import annotations

from pathlib import Path

from core.production_convergence.phase8 import (
    MIGRATED_PATHS,
    build_phase8_writer_migration_receipt,
)

REPO = Path(__file__).resolve().parents[1]


def test_phase8_receipt_shape_and_paths_exist() -> None:
    receipt = build_phase8_writer_migration_receipt()
    assert receipt["schema_version"] == "phase8_writer_migration.v1"
    assert receipt["candidate_status"] == "NOT_READY"
    assert receipt["summary"]["migrated_count"] == 14
    assert len(receipt["canonical_hash"]) == 64
    for rel in MIGRATED_PATHS:
        text = (REPO / rel).read_text(encoding="utf-8")
        assert "write_classified_json" in text
        assert "write_canonical_json(" not in text
