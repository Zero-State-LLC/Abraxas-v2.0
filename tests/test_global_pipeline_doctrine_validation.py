from __future__ import annotations

from pathlib import Path

from core.global_pipeline_doctrine_validation import (
    build_global_pipeline_doctrine_validation_operator_review_packet,
    build_global_pipeline_doctrine_validation_proof,
    write_global_pipeline_doctrine_validation_artifacts,
)


def test_proof_packet_is_deterministic_and_fail_closed() -> None:
    first = build_global_pipeline_doctrine_validation_proof()
    second = build_global_pipeline_doctrine_validation_proof()
    assert first["proof_id"] == second["proof_id"]
    assert first["schema_version"] == "GlobalPipelineDoctrineValidationProof.v1"
    assert first["advisory_only"] is True
    assert first["projection_only"] is True
    assert first["non_authoritative"] is True
    assert first["execution_authority"] is False
    assert first["pipeline_count"] == 18
    assert first["observed_validation_count"] == 8
    assert first["missing_validation_count"] == 10
    assert first["legacy_contract_posture_count"] == 8
    assert first["missing_contract_count"] == 10
    assert first["recommended_next_state"] == "hold"
    assert "operator_review_queue" not in first["missing_contract_ids"]
    assert "operator_review_queue" not in first["missing_validation_ids"]


def test_operator_review_packet_stays_repair_required_until_spine_is_complete() -> None:
    proof = build_global_pipeline_doctrine_validation_proof()
    review = build_global_pipeline_doctrine_validation_operator_review_packet(proof)
    assert review["schema_version"] == "GlobalPipelineDoctrineValidationOperatorReviewPacket.v1"
    assert review["state"] == "repair_required"
    assert review["priority"] == "P1"
    assert "LEGACY_CONTRACT_POSTURE_PRESENT" in review["blocked_reasons"]
    assert "MISSING_GLOBAL_PIPELINE_CONTRACTS" in review["blocked_reasons"]
    assert "MISSING_GLOBAL_PIPELINE_VALIDATION_COVERAGE" in review["blocked_reasons"]


def test_writer_emits_both_global_pipeline_doctrine_validation_artifacts(tmp_path: Path) -> None:
    written = write_global_pipeline_doctrine_validation_artifacts(tmp_path, source_root=".")
    assert (tmp_path / "out/global_pipeline_doctrine_validation/latest.json").exists()
    assert (
        tmp_path / "out/global_pipeline_doctrine_validation/operator_review_packet.latest.json"
    ).exists()
    assert written["proof_packet"]["pipeline_count"] == 18
