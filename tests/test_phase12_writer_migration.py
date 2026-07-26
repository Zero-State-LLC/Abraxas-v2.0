"""Phase 12 production-convergence writer migration + CLEAR review packet."""

from __future__ import annotations

from pathlib import Path

from core.production_convergence.clear_operator_review import (
    build_clear_operator_review_packet,
)
from core.production_convergence.clear_reference import build_clear_reference_analysis
from core.production_convergence.phase12 import (
    MIGRATED_PATHS,
    build_phase12_writer_migration_receipt,
)

REPO = Path(__file__).resolve().parents[1]


def test_phase12_receipt_and_migrated_paths() -> None:
    receipt = build_phase12_writer_migration_receipt()
    assert receipt["schema_version"] == "phase12_writer_migration.v1"
    assert receipt["candidate_status"] == "NOT_READY"
    assert receipt["external_production_authorized"] is False
    assert receipt["mass_deletion_authorized"] is False
    assert receipt["clear_operator_disposition_status"] == "PENDING_OPERATOR"
    assert receipt["summary"]["migrated_count"] == 11
    assert len(receipt["canonical_hash"]) == 64
    for rel in MIGRATED_PATHS:
        text = (REPO / rel).read_text(encoding="utf-8")
        assert "write_classified_json" in text, rel
        assert "write_canonical_json(" not in text, rel


def test_clear_operator_review_pending_and_advisory() -> None:
    analysis = build_clear_reference_analysis(REPO)
    assert analysis["mass_deletion_authorized"] is False
    assert analysis["candidate_status"] == "NOT_READY"
    # Phase 9–11 receipts are now required inputs.
    consumed = {item["path"] for item in analysis["inputs_consumed"]}
    assert "out/production_convergence/phase11_writer_migration.v1.json" in consumed

    packet = build_clear_operator_review_packet(REPO)
    assert packet["schema_version"] == "clear_operator_review.v1"
    assert packet["operator_disposition_status"] == "PENDING_OPERATOR"
    assert packet["mass_deletion_authorized"] is False
    assert packet["dual_control_required"] is True
    assert packet["external_production_authorized"] is False
    assert packet["clear_analysis_canonical_hash"] == analysis["canonical_hash"]
    assert len(packet["canonical_hash"]) == 64
