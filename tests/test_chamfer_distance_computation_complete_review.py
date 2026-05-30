from __future__ import annotations

import pytest

from core.chamfer_distance_computation_complete_review import (
    COMPUTATION_METHODS,
    EXPECTED_FIXTURE_CASE_FAMILIES,
    EXPECTED_SHADOW_DISTANCES,
    SOURCE_COMPUTATION_ACTUAL_PR_GATE_HASH,
    SOURCE_COMPUTATION_RECEIPT_HASH,
    ChamferComputationCompleteReviewError,
    build_chamfer_distance_computation_complete_review,
    compute_chamfer_distance_computation_complete_review_hash,
    default_authority_locks,
    default_blocked_scopes,
    default_invalid_fixture_review,
    default_nc_fixture_review,
    default_pr_gate_confirmation,
    default_shadow_distance_verification,
    serialize_chamfer_distance_computation_complete_review,
)


def _payload() -> dict:
    return {
        "complete_review_id": "chamfer_distance_computation_complete_review_001",
        "intended_lane": "SHADOW",
        "review_stage": "COMPUTATION_COMPLETE_REVIEW_ONLY",
        "shadow_distance_verification": default_shadow_distance_verification(),
        "pr_gate_confirmation": default_pr_gate_confirmation(),
        "invalid_fixture_review": default_invalid_fixture_review(),
        "nc_fixture_review": default_nc_fixture_review(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "CHAMFER_EXPECTED_VALUES_ADDITION_RECEIPT",
        "provenance": {
            "source": "CHAMFER_DISTANCE_COMPUTATION_COMPLETE_REVIEW",
            "evidence_refs": [
                f"ChamferDistanceComputationReceipt.v1:{SOURCE_COMPUTATION_RECEIPT_HASH}",
            ],
            "generated_by": "PATCH_CHAMFER_DISTANCE_COMPUTATION_COMPLETE_REVIEW_001",
            "upstream_schema_refs": [],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def test_build_valid_packet() -> None:
    packet = build_chamfer_distance_computation_complete_review(_payload())
    assert packet["review_type"] == "CHAMFER_DISTANCE_COMPUTATION_COMPLETE_REVIEW"
    assert packet["operator_id"] == "CHAMFER_DISTANCE"
    assert "canonical_hash" in packet


def test_hash_deterministic() -> None:
    p1 = build_chamfer_distance_computation_complete_review(_payload())
    p2 = build_chamfer_distance_computation_complete_review(_payload())
    assert p1["canonical_hash"] == p2["canonical_hash"]


def test_hash_function() -> None:
    packet = build_chamfer_distance_computation_complete_review(_payload())
    h = compute_chamfer_distance_computation_complete_review_hash(packet)
    assert h == packet["canonical_hash"]


def test_serialize_produces_string() -> None:
    packet = build_chamfer_distance_computation_complete_review(_payload())
    s = serialize_chamfer_distance_computation_complete_review(packet)
    assert isinstance(s, str)
    assert "CHAMFER_DISTANCE_COMPUTATION_COMPLETE_REVIEW" in s


def test_invalid_lane_raises() -> None:
    p = _payload()
    p["intended_lane"] = "PRODUCTION"
    with pytest.raises(ChamferComputationCompleteReviewError):
        build_chamfer_distance_computation_complete_review(p)


def test_invalid_review_stage_raises() -> None:
    p = _payload()
    p["review_stage"] = "WRONG"
    with pytest.raises(ChamferComputationCompleteReviewError):
        build_chamfer_distance_computation_complete_review(p)


def test_authority_lock_violation_raises() -> None:
    p = _payload()
    al = dict(default_authority_locks())
    al["emits_metric_values"] = True
    p["authority_locks"] = al
    with pytest.raises(ChamferComputationCompleteReviewError):
        build_chamfer_distance_computation_complete_review(p)


def test_forbidden_token_raises() -> None:
    p = _payload()
    p["provenance"]["source"] = "scheduler_source"
    with pytest.raises(ChamferComputationCompleteReviewError, match="forbidden"):
        build_chamfer_distance_computation_complete_review(p)


def test_expected_shadow_distances() -> None:
    assert EXPECTED_SHADOW_DISTANCES["chamfer.valid.duplicate_points.v1"] == 0.0
    assert EXPECTED_SHADOW_DISTANCES["chamfer.valid.multidimensional_points.v1"] == 3.0
    assert EXPECTED_SHADOW_DISTANCES["chamfer.valid.offset_point_sets.v1"] == 1.0
    assert EXPECTED_SHADOW_DISTANCES["chamfer.valid.partial_overlap_point_sets.v1"] == 0.5


def test_fixture_case_families_all_5() -> None:
    assert len(EXPECTED_FIXTURE_CASE_FAMILIES) == 5


def test_computation_methods_all_5() -> None:
    assert len(COMPUTATION_METHODS) == 5
    for fid in EXPECTED_SHADOW_DISTANCES:
        assert fid in COMPUTATION_METHODS


def test_source_hashes_present() -> None:
    assert len(SOURCE_COMPUTATION_RECEIPT_HASH) == 64
    assert len(SOURCE_COMPUTATION_ACTUAL_PR_GATE_HASH) == 64


def test_shadow_distance_verification_pass() -> None:
    sdv = default_shadow_distance_verification()
    assert sdv["all_5_valid_fixtures_verified"] is True
    assert sdv["all_values_match"] is True
    assert sdv["shadow_distance_verification_status"] == "PASS"


def test_pr_gate_confirmation() -> None:
    pgc = default_pr_gate_confirmation()
    assert pgc["pr_gate_verified"] is True
    assert pgc["pr_gate_confirmation_status"] == "CONFIRMED"


def test_invalid_fixture_review() -> None:
    ifr = default_invalid_fixture_review()
    assert ifr["total_invalid"] == 5
    assert ifr["all_rejected_correctly"] is True


def test_nc_fixture_review() -> None:
    ncr = default_nc_fixture_review()
    assert ncr["total_not_computable"] == 3
    assert ncr["all_rejected_correctly"] is True


def test_authority_locks_defaults() -> None:
    al = default_authority_locks()
    assert al["emits_metric_values"] is False
    assert al["production_activation"] is False
    assert al["canon_promotion"] is False


def test_blocked_scopes_all_false() -> None:
    assert all(v is False for v in default_blocked_scopes().values())
