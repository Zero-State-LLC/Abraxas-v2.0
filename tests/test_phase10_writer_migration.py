"""Phase 10 production-convergence writer migration."""

from __future__ import annotations

from pathlib import Path

from core.production_convergence.phase10 import (
    MIGRATED_PATHS,
    build_phase10_writer_migration_receipt,
)

REPO = Path(__file__).resolve().parents[1]


def test_phase10_receipt_and_migrated_paths() -> None:
    receipt = build_phase10_writer_migration_receipt()
    assert receipt["schema_version"] == "phase10_writer_migration.v1"
    assert receipt["candidate_status"] == "NOT_READY"
    assert receipt["external_production_authorized"] is False
    assert receipt["summary"]["migrated_count"] == 17
    assert receipt["summary"]["viz_replay_count"] == 8
    assert receipt["summary"]["wpd_research_count"] == 5
    assert receipt["summary"]["canary_companion_count"] == 4
    assert len(receipt["canonical_hash"]) == 64
    for rel in MIGRATED_PATHS:
        text = (REPO / rel).read_text(encoding="utf-8")
        assert "write_classified_json" in text, rel
        assert "write_canonical_json(" not in text, rel
