from __future__ import annotations

import pytest

from core.chamfer_expected_values_complete_review import (
    FINAL_SHADOW_DISTANCES,
    SOURCE_EXPECTED_VALUES_ADDITION_RECEIPT_HASH,
    SOURCE_EXPECTED_VALUES_GATE_HASH,
    ChamferExpectedValuesCompleteReviewError,
    build_chamfer_expected_values_complete_review,
    compute_chamfer_expected_values_complete_review_hash,
    default_authority_locks,
    default_blocked_scopes,
    default_chain_completion_summary,
    default_final_expected_values_summary,
    serialize_chamfer_expected_values_complete_review,
)


def _payload() -> dict:
    return {
        "complete_review_id": "chamfer_expected_values_complete_review_001",
        "intended_lane": "SHADOW",
        "review_stage": "EXPECTED_VALUES_COMPLETE_REVIEW_ONLY",
        "final_expected_values_summary": default_final_expected_values_summary(),
        "chain_completion_summary": default_chain_completion_summary(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "CHAMFER_DISTANCE_OPERATOR_BASELINE_IMPLEMENTATION",
        "provenance": {
            "source": "CHAMFER_EXPECTED_VALUES_COMPLETE_REVIEW",
            "evidence_refs": [
                f"ChamferExpectedValuesAdditionReceipt.v1:{SOURCE_EXPECTED_VALUES_ADDITION_RECEIPT_HASH}",
                f"ChamferExpectedValuesGate.v1:{SOURCE_EXPECTED_VALUES_GATE_HASH}",
            ],
            "generated_by": "PATCH_CHAMFER_EXPECTED_VALUES_COMPLETE_REVIEW_001",
            "upstream_schema_refs": [],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def test_build_valid_packet() -> None:
    packet = build_chamfer_expected_values_complete_review(_payload())
    assert packet["review_type"] == "CHAMFER_EXPECTED_VALUES_COMPLETE_REVIEW"
    assert packet["operator_id"] == "CHAMFER_DISTANCE"
    assert "canonical_hash" in packet


def test_hash_deterministic() -> None:
    p1 = build_chamfer_expected_values_complete_review(_payload())
    p2 = build_chamfer_expected_values_complete_review(_payload())
    assert p1["canonical_hash"] == p2["canonical_hash"]


def test_hash_function() -> None:
    packet = build_chamfer_expected_values_complete_review(_payload())
    h = compute_chamfer_expected_values_complete_review_hash(packet)
    assert h == packet["canonical_hash"]


def test_serialize_produces_string() -> None:
    packet = build_chamfer_expected_values_complete_review(_payload())
    s = serialize_chamfer_expected_values_complete_review(packet)
    assert isinstance(s, str)
    assert "CHAMFER_EXPECTED_VALUES_COMPLETE_REVIEW" in s


def test_invalid_lane_raises() -> None:
    p = _payload()
    p["intended_lane"] = "PRODUCTION"
    with pytest.raises(ChamferExpectedValuesCompleteReviewError):
        build_chamfer_expected_values_complete_review(p)


def test_invalid_review_stage_raises() -> None:
    p = _payload()
    p["review_stage"] = "WRONG"
    with pytest.raises(ChamferExpectedValuesCompleteReviewError):
        build_chamfer_expected_values_complete_review(p)


def test_authority_lock_violation_raises() -> None:
    p = _payload()
    al = dict(default_authority_locks())
    al["emits_metric_values"] = True
    p["authority_locks"] = al
    with pytest.raises(ChamferExpectedValuesCompleteReviewError):
        build_chamfer_expected_values_complete_review(p)


def test_forbidden_token_raises() -> None:
    p = _payload()
    p["provenance"]["source"] = "scoring_source"
    with pytest.raises(ChamferExpectedValuesCompleteReviewError, match="forbidden"):
        build_chamfer_expected_values_complete_review(p)


def test_final_shadow_distances_all_5() -> None:
    assert len(FINAL_SHADOW_DISTANCES) == 5
    assert FINAL_SHADOW_DISTANCES["chamfer.valid.duplicate_points.v1"] == 0.0
    assert FINAL_SHADOW_DISTANCES["chamfer.valid.multidimensional_points.v1"] == 3.0
    assert FINAL_SHADOW_DISTANCES["chamfer.valid.offset_point_sets.v1"] == 1.0
    assert FINAL_SHADOW_DISTANCES["chamfer.valid.partial_overlap_point_sets.v1"] == 0.5


def test_source_hashes_present() -> None:
    assert len(SOURCE_EXPECTED_VALUES_ADDITION_RECEIPT_HASH) == 64
    assert len(SOURCE_EXPECTED_VALUES_GATE_HASH) == 64


def test_final_expected_values_summary() -> None:
    s = default_final_expected_values_summary()
    assert s["total_valid_fixtures"] == 5
    assert s["all_expected_distances_confirmed"] is True
    assert s["final_expected_values_status"] == "CONFIRMED_AND_SEALED"


def test_chain_completion_summary_all_steps_complete() -> None:
    c = default_chain_completion_summary()
    assert c["chain_completion_status"] == "ALL_STEPS_COMPLETE"
    assert c["computation_receipt_complete"] is True
    assert c["authorization_review_complete"] is True
    assert c["pr_gate_complete"] is True
    assert c["computation_complete_review_complete"] is True
    assert c["expected_values_addition_receipt_complete"] is True
    assert c["expected_values_gate_complete"] is True
    assert c["recommended_next_phase"] == "CHAMFER_DISTANCE_OPERATOR_BASELINE_IMPLEMENTATION"


def test_authority_locks_defaults() -> None:
    al = default_authority_locks()
    assert al["emits_metric_values"] is False
    assert al["production_activation"] is False
    assert al["canon_promotion"] is False


def test_blocked_scopes_all_false() -> None:
    assert all(v is False for v in default_blocked_scopes().values())
