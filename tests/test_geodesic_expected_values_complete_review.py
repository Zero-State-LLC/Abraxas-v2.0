from __future__ import annotations

import pytest

from core.canonical.json import canonical_hash
from core.geodesic_expected_values_complete_review import (
    ADDITION_STAGE,
    DECLARED_EXPECTED_VALUES,
    REVIEW_ID,
    REVIEW_STATUS,
    SCHEMA_VERSION,
    SOURCE_ADDITION_RECEIPT_HASH,
    SOURCE_EXPECTED_VALUES_GATE_HASH,
    GeodesicExpectedValuesCompleteReviewValidationError,
    build_complete_review,
    validate_complete_review,
)


# ── build + validate round-trip ────────────────────────────────────────────────


def test_build_returns_dict():
    assert isinstance(build_complete_review(), dict)


def test_schema_version():
    assert build_complete_review()["schema_version"] == SCHEMA_VERSION


def test_review_id():
    assert build_complete_review()["review_id"] == REVIEW_ID


def test_review_status():
    assert build_complete_review()["review_status"] == REVIEW_STATUS


def test_addition_stage():
    assert build_complete_review()["addition_stage"] == ADDITION_STAGE


def test_intended_lane():
    assert build_complete_review()["intended_lane"] == "SHADOW"


def test_source_addition_receipt_hash():
    assert build_complete_review()["source_addition_receipt_hash"] == SOURCE_ADDITION_RECEIPT_HASH


def test_source_gate_hash():
    assert build_complete_review()["source_expected_values_gate_hash"] == SOURCE_EXPECTED_VALUES_GATE_HASH


def test_canonical_hash_64_chars():
    h = build_complete_review()["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_correct():
    review = build_complete_review()
    pre = {k: v for k, v in review.items() if k != "canonical_hash"}
    assert canonical_hash(pre) == review["canonical_hash"]


def test_validate_passes():
    validate_complete_review(build_complete_review())


def test_replay_stable():
    assert build_complete_review() == build_complete_review()


def test_recommended_next_step():
    assert build_complete_review()["recommended_next_step"] == "GEODESIC_COMPUTATION_AUTHORIZATION_REVIEW"


# ── corpus review summary ──────────────────────────────────────────────────────


def test_total_fixture_count():
    assert build_complete_review()["corpus_review_summary"]["total_fixture_count"] == 13


def test_valid_fixture_count():
    assert build_complete_review()["corpus_review_summary"]["valid_fixture_count"] == 5


def test_invalid_fixture_count():
    assert build_complete_review()["corpus_review_summary"]["invalid_fixture_count"] == 4


def test_nc_fixture_count():
    assert build_complete_review()["corpus_review_summary"]["not_computable_fixture_count"] == 4


def test_valid_with_expected_distance():
    assert build_complete_review()["corpus_review_summary"]["valid_fixtures_with_expected_distance"] == 5


def test_invalid_with_expected_distance_zero():
    assert build_complete_review()["corpus_review_summary"]["invalid_fixtures_with_expected_distance"] == 0


def test_nc_with_expected_distance_zero():
    assert build_complete_review()["corpus_review_summary"]["not_computable_fixtures_with_expected_distance"] == 0


def test_corpus_consistent():
    assert build_complete_review()["corpus_review_summary"]["corpus_consistent"] is True


# ── valid fixture review ───────────────────────────────────────────────────────


def test_valid_fixture_review_count():
    assert build_complete_review()["valid_fixture_review"]["reviewed_count"] == 5


def test_valid_fixture_review_all_match():
    assert build_complete_review()["valid_fixture_review"]["all_values_match_declared"] is True


def test_valid_fixture_review_gate_hashes():
    assert build_complete_review()["valid_fixture_review"]["all_gate_hashes_consistent"] is True


def test_valid_fixture_review_declared_values():
    entries = build_complete_review()["valid_fixture_review"]["fixture_entries"]
    val_map = {e["fixture_id"]: e["expected_geodesic_distance"] for e in entries}
    for fid, declared in DECLARED_EXPECTED_VALUES.items():
        assert val_map[fid] == declared, f"{fid}: {val_map[fid]} != {declared}"


def test_valid_fixture_review_all_included_true():
    entries = build_complete_review()["valid_fixture_review"]["fixture_entries"]
    for e in entries:
        assert e["expected_geodesic_distance_included"] is True


def test_valid_fixture_review_value_matches():
    entries = build_complete_review()["valid_fixture_review"]["fixture_entries"]
    for e in entries:
        assert e["value_matches_declared"] is True


# ── invalid fixture review ─────────────────────────────────────────────────────


def test_invalid_fixture_review_count():
    assert build_complete_review()["invalid_fixture_review"]["reviewed_count"] == 4


def test_invalid_fixture_review_all_excluded():
    assert build_complete_review()["invalid_fixture_review"]["all_excluded"] is True


def test_invalid_fixture_review_entries_excluded():
    entries = build_complete_review()["invalid_fixture_review"]["fixture_entries"]
    for e in entries:
        assert e["excluded_confirmed"] is True
        assert e["expected_geodesic_distance_included"] is False


# ── not-computable fixture review ─────────────────────────────────────────────


def test_nc_fixture_review_count():
    assert build_complete_review()["not_computable_fixture_review"]["reviewed_count"] == 4


def test_nc_fixture_review_all_excluded():
    assert build_complete_review()["not_computable_fixture_review"]["all_excluded"] is True


def test_nc_fixture_review_entries_excluded():
    entries = build_complete_review()["not_computable_fixture_review"]["fixture_entries"]
    for e in entries:
        assert e["excluded_confirmed"] is True
        assert e["expected_geodesic_distance_included"] is False


# ── posture confirmation ───────────────────────────────────────────────────────


def test_posture_emits_metric_values_false():
    assert build_complete_review()["posture_confirmation"]["emits_metric_values"] is False


def test_posture_forecast_influence_false():
    assert build_complete_review()["posture_confirmation"]["forecast_influence"] is False


def test_posture_p43_false():
    assert build_complete_review()["posture_confirmation"]["p43_surface_lanes_authorized"] is False


def test_posture_production_activation_false():
    assert build_complete_review()["posture_confirmation"]["production_activation"] is False


def test_posture_canon_promotion_false():
    assert build_complete_review()["posture_confirmation"]["canon_promotion"] is False


def test_posture_runtime_mutation_false():
    assert build_complete_review()["posture_confirmation"]["runtime_mutation"] is False


def test_posture_execution_authority_false():
    assert build_complete_review()["posture_confirmation"]["execution_authority"] is False


def test_posture_shadow_lane_only():
    assert build_complete_review()["posture_confirmation"]["shadow_lane_only"] is True


def test_posture_confirmed():
    assert build_complete_review()["posture_confirmation"]["posture_confirmed"] is True


# ── authority locks ────────────────────────────────────────────────────────────


def test_lock_advisory_only():
    assert build_complete_review()["authority_locks"]["advisory_only"] is True


def test_lock_shadow_lane_only():
    assert build_complete_review()["authority_locks"]["shadow_lane_only"] is True


def test_lock_expected_values_addition_only():
    assert build_complete_review()["authority_locks"]["expected_values_addition_only"] is True


def test_lock_expected_geodesic_distances_authorized():
    assert build_complete_review()["authority_locks"]["expected_geodesic_distances_authorized"] is True


def test_lock_emits_metric_values_false():
    assert build_complete_review()["authority_locks"]["emits_metric_values"] is False


def test_lock_forecast_influence_false():
    assert build_complete_review()["authority_locks"]["forecast_influence"] is False


def test_lock_p43_surface_lanes_false():
    assert build_complete_review()["authority_locks"]["p43_surface_lanes_authorized"] is False


def test_lock_production_activation_false():
    assert build_complete_review()["authority_locks"]["production_activation"] is False


def test_lock_canon_promotion_false():
    assert build_complete_review()["authority_locks"]["canon_promotion"] is False


def test_lock_runtime_mutation_false():
    assert build_complete_review()["authority_locks"]["runtime_mutation"] is False


def test_lock_execution_authority_false():
    assert build_complete_review()["authority_locks"]["execution_authority"] is False


def test_lock_inference_authority_false():
    assert build_complete_review()["authority_locks"]["inference_authority"] is False


# ── validate rejects bad inputs ────────────────────────────────────────────────


def test_validate_rejects_wrong_schema_version():
    review = build_complete_review()
    review["schema_version"] = "Wrong.v1"
    with pytest.raises(GeodesicExpectedValuesCompleteReviewValidationError):
        validate_complete_review(review)


def test_validate_rejects_wrong_status():
    review = build_complete_review()
    review["review_status"] = "WRONG"
    with pytest.raises(GeodesicExpectedValuesCompleteReviewValidationError):
        validate_complete_review(review)


def test_validate_rejects_hash_mismatch():
    review = build_complete_review()
    review["canonical_hash"] = "a" * 64
    with pytest.raises(GeodesicExpectedValuesCompleteReviewValidationError):
        validate_complete_review(review)


def test_validate_rejects_wrong_receipt_hash():
    review = build_complete_review()
    review["source_addition_receipt_hash"] = "b" * 64
    review["canonical_hash"] = canonical_hash(
        {k: v for k, v in review.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicExpectedValuesCompleteReviewValidationError):
        validate_complete_review(review)


def test_validate_rejects_emits_metric_values_true():
    review = build_complete_review()
    review["authority_locks"]["emits_metric_values"] = True
    review["canonical_hash"] = canonical_hash(
        {k: v for k, v in review.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicExpectedValuesCompleteReviewValidationError):
        validate_complete_review(review)
