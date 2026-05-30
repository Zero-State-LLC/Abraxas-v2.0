from __future__ import annotations

import pytest

from core.chamfer_expected_values_addition_receipt import (
    EXPECTED_CHAMFER_DISTANCES,
    INVALID_FIXTURE_IDS,
    NC_FIXTURE_IDS,
    SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH,
    SOURCE_EXPECTED_DISTANCE_VALUES_GATE_HASH,
    VALID_FIXTURE_FILES,
    ChamferExpectedValuesAdditionReceiptError,
    build_chamfer_expected_values_addition_receipt,
    compute_chamfer_expected_values_addition_receipt_hash,
    default_authority_locks,
    default_blocked_scopes,
    default_computation_complete_review_confirmation,
    default_expected_values_addition_summary,
    serialize_chamfer_expected_values_addition_receipt,
)


def _payload() -> dict:
    return {
        "addition_receipt_id": "chamfer_expected_values_addition_receipt_001",
        "intended_lane": "SHADOW",
        "addition_stage": "EXPECTED_VALUES_ADDITION_ONLY",
        "expected_values_addition_summary": default_expected_values_addition_summary(),
        "computation_complete_review_confirmation": (
            default_computation_complete_review_confirmation()
        ),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "CHAMFER_EXPECTED_VALUES_GATE",
        "provenance": {
            "source": "CHAMFER_EXPECTED_VALUES_ADDITION_RECEIPT",
            "evidence_refs": [
                f"ChamferDistanceComputationCompleteReview.v1:{SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH}",
            ],
            "generated_by": "PATCH_CHAMFER_EXPECTED_VALUES_ADDITION_RECEIPT_001",
            "upstream_schema_refs": [],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def test_build_valid_packet() -> None:
    packet = build_chamfer_expected_values_addition_receipt(_payload())
    assert packet["receipt_type"] == "CHAMFER_EXPECTED_VALUES_ADDITION_RECEIPT"
    assert packet["operator_id"] == "CHAMFER_DISTANCE"
    assert "canonical_hash" in packet


def test_hash_deterministic() -> None:
    p1 = build_chamfer_expected_values_addition_receipt(_payload())
    p2 = build_chamfer_expected_values_addition_receipt(_payload())
    assert p1["canonical_hash"] == p2["canonical_hash"]


def test_hash_function() -> None:
    packet = build_chamfer_expected_values_addition_receipt(_payload())
    h = compute_chamfer_expected_values_addition_receipt_hash(packet)
    assert h == packet["canonical_hash"]


def test_serialize_produces_string() -> None:
    packet = build_chamfer_expected_values_addition_receipt(_payload())
    s = serialize_chamfer_expected_values_addition_receipt(packet)
    assert isinstance(s, str)
    assert "CHAMFER_EXPECTED_VALUES_ADDITION_RECEIPT" in s


def test_invalid_lane_raises() -> None:
    p = _payload()
    p["intended_lane"] = "PRODUCTION"
    with pytest.raises(ChamferExpectedValuesAdditionReceiptError):
        build_chamfer_expected_values_addition_receipt(p)


def test_invalid_addition_stage_raises() -> None:
    p = _payload()
    p["addition_stage"] = "WRONG"
    with pytest.raises(ChamferExpectedValuesAdditionReceiptError):
        build_chamfer_expected_values_addition_receipt(p)


def test_authority_lock_violation_raises() -> None:
    p = _payload()
    al = dict(default_authority_locks())
    al["emits_metric_values"] = True
    p["authority_locks"] = al
    with pytest.raises(ChamferExpectedValuesAdditionReceiptError):
        build_chamfer_expected_values_addition_receipt(p)


def test_forbidden_token_raises() -> None:
    p = _payload()
    p["provenance"]["source"] = "cache_source"
    with pytest.raises(ChamferExpectedValuesAdditionReceiptError, match="forbidden"):
        build_chamfer_expected_values_addition_receipt(p)


def test_expected_chamfer_distances_all_5() -> None:
    assert len(EXPECTED_CHAMFER_DISTANCES) == 5
    assert EXPECTED_CHAMFER_DISTANCES["chamfer.valid.duplicate_points.v1"] == 0.0
    assert EXPECTED_CHAMFER_DISTANCES["chamfer.valid.multidimensional_points.v1"] == 3.0
    assert EXPECTED_CHAMFER_DISTANCES["chamfer.valid.offset_point_sets.v1"] == 1.0
    assert EXPECTED_CHAMFER_DISTANCES["chamfer.valid.partial_overlap_point_sets.v1"] == 0.5


def test_valid_fixture_files_all_5() -> None:
    assert len(VALID_FIXTURE_FILES) == 5


def test_invalid_fixture_ids_count() -> None:
    assert len(INVALID_FIXTURE_IDS) == 5


def test_nc_fixture_ids_count() -> None:
    assert len(NC_FIXTURE_IDS) == 3


def test_source_hashes_present() -> None:
    assert len(SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH) == 64
    assert len(SOURCE_EXPECTED_DISTANCE_VALUES_GATE_HASH) == 64


def test_addition_summary_present() -> None:
    s = default_expected_values_addition_summary()
    assert s["total_valid_fixtures"] == 5
    assert s["expected_distances_present_in_fixtures"] is True
    assert s["addition_status"] == "EXPECTED_VALUES_PRESENT_IN_FIXTURE_FILES"


def test_computation_complete_review_confirmation() -> None:
    c = default_computation_complete_review_confirmation()
    assert c["all_5_shadow_distances_verified"] is True
    assert c["all_values_match_static_fixtures"] is True
    assert c["computation_complete_review_status"] == "CONFIRMED"


def test_authority_locks_defaults() -> None:
    al = default_authority_locks()
    assert al["emits_metric_values"] is False
    assert al["production_activation"] is False


def test_blocked_scopes_all_false() -> None:
    assert all(v is False for v in default_blocked_scopes().values())
