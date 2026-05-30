from __future__ import annotations

import pytest

from core.canonical.json import canonical_hash
from core.geodesic_computation_complete_review import (
    OPERATOR_ID,
    REVIEW_ID,
    REVIEW_STAGE,
    REVIEW_STATUS,
    SCHEMA_VERSION,
    SOURCE_COMPUTATION_RECEIPT_HASH,
    SOURCE_IMPLEMENTATION_GATE_HASH,
    SOURCE_IMPLEMENTATION_PLAN_HASH,
    GeodesicComputationCompleteReviewError,
    build_computation_complete_review,
    validate_computation_complete_review,
)


# ── build + round-trip ─────────────────────────────────────────────────────────


def test_build_returns_dict():
    assert isinstance(build_computation_complete_review(), dict)


def test_schema_version():
    assert build_computation_complete_review()["schema_version"] == SCHEMA_VERSION


def test_review_id():
    assert build_computation_complete_review()["review_id"] == REVIEW_ID


def test_operator_id():
    assert build_computation_complete_review()["operator_id"] == OPERATOR_ID


def test_review_status():
    assert build_computation_complete_review()["review_status"] == REVIEW_STATUS


def test_review_stage():
    assert build_computation_complete_review()["review_stage"] == REVIEW_STAGE


def test_intended_lane():
    assert build_computation_complete_review()["intended_lane"] == "SHADOW"


def test_source_receipt_hash():
    assert (
        build_computation_complete_review()["source_computation_receipt_hash"]
        == SOURCE_COMPUTATION_RECEIPT_HASH
    )


def test_source_gate_hash():
    assert (
        build_computation_complete_review()["source_implementation_gate_hash"]
        == SOURCE_IMPLEMENTATION_GATE_HASH
    )


def test_source_plan_hash():
    assert (
        build_computation_complete_review()["source_implementation_plan_hash"]
        == SOURCE_IMPLEMENTATION_PLAN_HASH
    )


def test_all_reviews_passed():
    assert build_computation_complete_review()["all_reviews_passed"] is True


def test_canonical_hash_64_chars():
    h = build_computation_complete_review()["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_correct():
    r = build_computation_complete_review()
    pre = {k: v for k, v in r.items() if k != "canonical_hash"}
    assert canonical_hash(pre) == r["canonical_hash"]


def test_validate_passes():
    validate_computation_complete_review(build_computation_complete_review())


def test_replay_stable():
    assert build_computation_complete_review() == build_computation_complete_review()


def test_recommended_next_step():
    assert (
        build_computation_complete_review()["recommended_next_step"]
        == "GEODESIC_COMPUTATION_OPERATOR_CLOSURE"
    )


# ── valid fixture result review ────────────────────────────────────────────────


def test_valid_review_passed():
    assert (
        build_computation_complete_review()["valid_fixture_result_review"]["review_passed"]
        is True
    )


def test_valid_review_all_match():
    vr = build_computation_complete_review()["valid_fixture_result_review"]
    assert vr["all_match_confirmed"] is True


def test_valid_review_total_5():
    vr = build_computation_complete_review()["valid_fixture_result_review"]
    assert vr["total_valid_fixtures"] == 5


def test_valid_review_per_fixture_count():
    vr = build_computation_complete_review()["valid_fixture_result_review"]
    assert len(vr["per_fixture"]) == 5


def test_valid_review_per_fixture_all_match():
    vr = build_computation_complete_review()["valid_fixture_result_review"]
    for pf in vr["per_fixture"]:
        assert pf["comparison_outcome"] == "MATCH"
        assert pf["corpus_distance_confirmed"] is True
        assert pf["review_passed"] is True


def test_valid_001_distance():
    vr = build_computation_complete_review()["valid_fixture_result_review"]
    r = next(p for p in vr["per_fixture"] if "valid_001" in p["fixture_id"])
    assert r["computed_geodesic_distance"] == 3.0


def test_valid_003_self_loop_zero():
    vr = build_computation_complete_review()["valid_fixture_result_review"]
    r = next(p for p in vr["per_fixture"] if "valid_003" in p["fixture_id"])
    assert r["computed_geodesic_distance"] == 0.0


def test_valid_005_distance():
    vr = build_computation_complete_review()["valid_fixture_result_review"]
    r = next(p for p in vr["per_fixture"] if "valid_005" in p["fixture_id"])
    assert r["computed_geodesic_distance"] == 1.5


def test_valid_per_fixture_no_metric_emitted():
    vr = build_computation_complete_review()["valid_fixture_result_review"]
    for pf in vr["per_fixture"]:
        assert pf["metric_emitted_confirmed_false"] is True


# ── invalid fixture rejection review ──────────────────────────────────────────


def test_invalid_review_passed():
    assert (
        build_computation_complete_review()["invalid_fixture_rejection_review"]["review_passed"]
        is True
    )


def test_invalid_review_total_4():
    ir = build_computation_complete_review()["invalid_fixture_rejection_review"]
    assert ir["total_invalid_fixtures"] == 4


def test_invalid_review_all_rejected_correctly():
    ir = build_computation_complete_review()["invalid_fixture_rejection_review"]
    assert ir["all_rejected_correctly_confirmed"] is True


def test_invalid_review_per_fixture_count():
    ir = build_computation_complete_review()["invalid_fixture_rejection_review"]
    assert len(ir["per_fixture"]) == 4


def test_invalid_review_per_fixture_all_pass():
    ir = build_computation_complete_review()["invalid_fixture_rejection_review"]
    for pf in ir["per_fixture"]:
        assert pf["rejection_outcome"] == "INVALID_INPUT"
        assert pf["computation_attempted_confirmed_false"] is True
        assert pf["review_passed"] is True


# ── not_computable fixture rejection review ────────────────────────────────────


def test_nc_review_passed():
    assert (
        build_computation_complete_review()["not_computable_fixture_rejection_review"][
            "review_passed"
        ]
        is True
    )


def test_nc_review_total_4():
    nc = build_computation_complete_review()["not_computable_fixture_rejection_review"]
    assert nc["total_not_computable_fixtures"] == 4


def test_nc_review_all_confirmed():
    nc = build_computation_complete_review()["not_computable_fixture_rejection_review"]
    assert nc["all_not_computable_correctly_confirmed"] is True


def test_nc_review_per_fixture_count():
    nc = build_computation_complete_review()["not_computable_fixture_rejection_review"]
    assert len(nc["per_fixture"]) == 4


def test_nc_review_per_fixture_all_pass():
    nc = build_computation_complete_review()["not_computable_fixture_rejection_review"]
    for pf in nc["per_fixture"]:
        assert pf["not_computable_outcome"] == "NOT_COMPUTABLE"
        assert pf["computation_attempted_confirmed_false"] is True
        assert pf["reason_confirmed"] is True
        assert pf["review_passed"] is True


def test_nc_001_empty_input_reason():
    nc = build_computation_complete_review()["not_computable_fixture_rejection_review"]
    r = next(p for p in nc["per_fixture"] if "nc_001" in p["fixture_id"])
    assert r["not_computable_reason"] == "EMPTY_INPUT"


def test_nc_002_disconnected_reason():
    nc = build_computation_complete_review()["not_computable_fixture_rejection_review"]
    r = next(p for p in nc["per_fixture"] if "nc_002" in p["fixture_id"])
    assert r["not_computable_reason"] == "DISCONNECTED_GRAPH"


# ── comparison summary review ──────────────────────────────────────────────────


def test_cs_review_passed():
    assert (
        build_computation_complete_review()["comparison_summary_review"]["review_passed"]
        is True
    )


def test_cs_review_all_match_confirmed():
    cs = build_computation_complete_review()["comparison_summary_review"]
    assert cs["all_valid_match_confirmed_true"] is True


def test_cs_review_mismatch_zero():
    cs = build_computation_complete_review()["comparison_summary_review"]
    assert cs["mismatch_count_confirmed_zero"] is True


def test_cs_review_match_count_5():
    cs = build_computation_complete_review()["comparison_summary_review"]
    assert cs["match_count_confirmed"] is True


# ── block section reviews ──────────────────────────────────────────────────────


def test_no_metric_emission_review_passed():
    b = build_computation_complete_review()["no_metric_emission_review"]
    assert b["emits_metric_values"] is False
    assert b["review_passed"] is True


def test_no_forecast_influence_review_passed():
    b = build_computation_complete_review()["no_forecast_influence_review"]
    assert b["forecast_influence"] is False
    assert b["review_passed"] is True


def test_no_p43_review_passed():
    b = build_computation_complete_review()["no_p43_surface_lane_review"]
    assert b["p43_surface_lanes_authorized"] is False
    assert b["review_passed"] is True


# ── authority lock review ──────────────────────────────────────────────────────


def test_authority_lock_review_passed():
    assert (
        build_computation_complete_review()["authority_lock_review"]["review_passed"] is True
    )


def test_authority_lock_all_true_confirmed():
    lr = build_computation_complete_review()["authority_lock_review"]
    assert lr["all_true_locks_confirmed"] is True


def test_authority_lock_all_false_confirmed():
    lr = build_computation_complete_review()["authority_lock_review"]
    assert lr["all_false_locks_confirmed"] is True


def test_authority_lock_stage_confirmed():
    lr = build_computation_complete_review()["authority_lock_review"]
    assert lr["computation_stage_confirmed"] is True


def test_authority_lock_lane_confirmed():
    lr = build_computation_complete_review()["authority_lock_review"]
    assert lr["intended_lane_confirmed"] is True


# ── blocked scopes ─────────────────────────────────────────────────────────────


def test_blocked_scopes_all_false():
    bs = build_computation_complete_review()["blocked_scopes"]
    for key, val in bs.items():
        assert val is False, f"blocked_scopes.{key} must be False"


# ── authority locks ────────────────────────────────────────────────────────────


def test_lock_advisory_only():
    assert build_computation_complete_review()["authority_locks"]["advisory_only"] is True


def test_lock_shadow_lane_only():
    assert build_computation_complete_review()["authority_locks"]["shadow_lane_only"] is True


def test_lock_computation_complete_review_only():
    assert (
        build_computation_complete_review()["authority_locks"][
            "computation_complete_review_only"
        ]
        is True
    )


def test_lock_test_vector_computation_only():
    assert (
        build_computation_complete_review()["authority_locks"]["test_vector_computation_only"]
        is True
    )


def test_lock_geodesic_authorized():
    assert (
        build_computation_complete_review()["authority_locks"][
            "geodesic_computation_implementation_authorized"
        ]
        is True
    )


def test_lock_emits_metric_values_false():
    assert (
        build_computation_complete_review()["authority_locks"]["emits_metric_values"] is False
    )


def test_lock_execution_authority_false():
    assert (
        build_computation_complete_review()["authority_locks"]["execution_authority"] is False
    )


def test_lock_production_activation_false():
    assert (
        build_computation_complete_review()["authority_locks"]["production_activation"] is False
    )


# ── validate rejects bad inputs ────────────────────────────────────────────────


def test_validate_rejects_wrong_schema():
    r = build_computation_complete_review()
    r["schema_version"] = "Wrong.v1"
    with pytest.raises(GeodesicComputationCompleteReviewError):
        validate_computation_complete_review(r)


def test_validate_rejects_wrong_status():
    r = build_computation_complete_review()
    r["review_status"] = "WRONG"
    with pytest.raises(GeodesicComputationCompleteReviewError):
        validate_computation_complete_review(r)


def test_validate_rejects_hash_mismatch():
    r = build_computation_complete_review()
    r["canonical_hash"] = "a" * 64
    with pytest.raises(GeodesicComputationCompleteReviewError):
        validate_computation_complete_review(r)


def test_validate_rejects_wrong_receipt_hash():
    r = build_computation_complete_review()
    r["source_computation_receipt_hash"] = "b" * 64
    r["canonical_hash"] = canonical_hash(
        {k: v for k, v in r.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicComputationCompleteReviewError):
        validate_computation_complete_review(r)


def test_validate_rejects_all_reviews_not_passed():
    r = build_computation_complete_review()
    r["all_reviews_passed"] = False
    r["canonical_hash"] = canonical_hash(
        {k: v for k, v in r.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicComputationCompleteReviewError):
        validate_computation_complete_review(r)


def test_validate_rejects_execution_authority_true():
    r = build_computation_complete_review()
    r["authority_locks"]["execution_authority"] = True
    r["canonical_hash"] = canonical_hash(
        {k: v for k, v in r.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicComputationCompleteReviewError):
        validate_computation_complete_review(r)
