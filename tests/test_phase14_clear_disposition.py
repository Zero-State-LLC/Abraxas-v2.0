"""Phase 14 CLEAR disposition draft + research_canary writer migration."""

from __future__ import annotations

from pathlib import Path

from core.production_convergence.clear_disposition_draft import (
    build_clear_disposition_draft,
)
from core.production_convergence.clear_reference import build_clear_reference_analysis
from core.production_convergence.phase14 import (
    MIGRATED_PATHS,
    build_phase14_receipt,
)

REPO = Path(__file__).resolve().parents[1]


def test_phase14_receipt_and_canary_writer_migrated() -> None:
    receipt = build_phase14_receipt()
    assert (
        receipt["schema_version"]
        == "phase14_clear_disposition_and_canary_writer.v1"
    )
    assert receipt["candidate_status"] == "NOT_READY"
    assert receipt["external_production_authorized"] is False
    assert receipt["mass_deletion_authorized"] is False
    assert receipt["deletions_executed"] is False
    assert receipt["clear_operator_disposition_status"] == "PENDING_OPERATOR"
    assert receipt["clear_engineering_disposition_status"] == "DRAFT_ISSUED"
    assert receipt["dual_control_required"] is True
    assert receipt["summary"]["migrated_count"] == 1
    assert len(receipt["canonical_hash"]) == 64
    for rel in MIGRATED_PATHS:
        text = (REPO / rel).read_text(encoding="utf-8")
        assert "write_classified_json" in text, rel
        assert "write_canonical_json(" not in text, rel


def test_clear_disposition_draft_non_delete_and_pending_dual_control() -> None:
    analysis = build_clear_reference_analysis(REPO)
    consumed = {item["path"] for item in analysis["inputs_consumed"]}
    assert "out/production_convergence/phase13_writer_migration.v1.json" in consumed

    draft = build_clear_disposition_draft(REPO)
    assert draft["schema_version"] == "clear_disposition_draft.v1"
    assert draft["engineering_disposition_status"] == "DRAFT_ISSUED"
    assert draft["operator_disposition_status"] == "PENDING_OPERATOR"
    assert draft["mass_deletion_authorized"] is False
    assert draft["deletions_executed"] is False
    assert draft["paths_deleted"] == []
    assert draft["dual_control"]["status"] == "PENDING"
    assert draft["dual_control"]["control_a_attestation"] is None
    assert draft["dual_control"]["control_b_attestation"] is None
    assert draft["summary"]["deletion_proposed_count"] == 0
    assert draft["clear_analysis_canonical_hash"] == analysis["canonical_hash"]
    for entry in draft["entries"]:
        assert entry["deletion_proposed"] is False
        assert entry["execution_authorized"] is False
        assert entry["engineering_disposition"] == entry["recommended_action"]
