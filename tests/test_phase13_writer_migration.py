"""Phase 13 production-convergence artifact-contract writer migration."""

from __future__ import annotations

from pathlib import Path

from core.production_convergence.clear_operator_review import (
    build_clear_operator_review_packet,
)
from core.production_convergence.clear_reference import build_clear_reference_analysis
from core.production_convergence.phase13 import (
    MIGRATED_PATHS,
    build_phase13_writer_migration_receipt,
)

REPO = Path(__file__).resolve().parents[1]


def test_phase13_receipt_and_migrated_paths() -> None:
    receipt = build_phase13_writer_migration_receipt()
    assert receipt["schema_version"] == "phase13_writer_migration.v1"
    assert receipt["candidate_status"] == "NOT_READY"
    assert receipt["external_production_authorized"] is False
    assert receipt["mass_deletion_authorized"] is False
    assert receipt["clear_operator_disposition_status"] == "PENDING_OPERATOR"
    assert receipt["summary"]["migrated_count"] == 27
    assert len(receipt["canonical_hash"]) == 64
    for rel in MIGRATED_PATHS:
        text = (REPO / rel).read_text(encoding="utf-8")
        assert "write_classified_json" in text, rel
        assert "write_canonical_json(" not in text, rel


def test_clear_consumes_phase12_and_stays_advisory() -> None:
    analysis = build_clear_reference_analysis(REPO)
    assert analysis["mass_deletion_authorized"] is False
    assert analysis["candidate_status"] == "NOT_READY"
    consumed = {item["path"] for item in analysis["inputs_consumed"]}
    assert "out/production_convergence/phase12_writer_migration.v1.json" in consumed

    packet = build_clear_operator_review_packet(REPO)
    assert packet["operator_disposition_status"] == "PENDING_OPERATOR"
    assert packet["mass_deletion_authorized"] is False
    assert packet["dual_control_required"] is True
    assert packet["external_production_authorized"] is False
