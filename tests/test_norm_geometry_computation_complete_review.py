from __future__ import annotations

import pytest

from core.canonical.json import canonical_hash
from core.norm_geometry_computation_complete_review import (
    OPERATOR_ID,
    REVIEW_ID,
    REVIEW_STAGE,
    REVIEW_STATUS,
    SCHEMA_VERSION,
    SOURCE_COMPUTATION_RECEIPT_HASH,
    SOURCE_CPU_BASELINE_PLAN_HASH,
    SOURCE_IMPLEMENTATION_GATE_HASH,
    NormGeometryComputationCompleteReviewError,
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


def test_source_cpu_baseline_plan_hash():
    assert (
        build_computation_complete_review()["source_cpu_baseline_plan_hash"]
        == SOURCE_CPU_BASELINE_PLAN_HASH
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
        == "NORM_GEOMETRY_COMPUTATION_OPERATOR_CLOSURE"
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


def test_valid_review_total_6():
    vr = build_computation_complete_review()["valid_fixture_result_review"]
    assert vr["total_valid_fixtures"] == 6


def test_valid_review_per_fixture_count():
    vr = build_computation_complete_review()["valid_fixture_result_review"]
    assert len(vr["per_fixture"]) == 6


def test_valid_review_per_fixture_all_pass():
    vr = build_computation_complete_review()["valid_fixture_result_review"]
    for pf in vr["per_fixture"]:
        assert pf["comparison_outcome"] == "MATCH"
        assert pf["corpus_distance_confirmed"] is True
        assert pf["review_passed"] is True


def test_valid_v001_l1_distance():
    vr = build_computation_complete_review()["valid_fixture_result_review"]
    r = next(p for p in vr["per_fixture"] if "v001" in p["fixture_id"])
    assert r["computed_lp_distance"] == 12.0


def test_valid_v002_l2_distance():
    vr = build_computation_complete_review()["valid_fixture_result_review"]
    r = next(p for p in vr["per_fixture"] if "v002" in p["fixture_id"])
    assert r["computed_lp_distance"] == 5.0


def test_valid_v003_linf_distance():
    vr = build_computation_complete_review()["valid_fixture_result_review"]
    r = next(p for p in vr["per_fixture"] if "v003" in p["fixture_id"])
    assert r["computed_lp_distance"] == 7.0


def test_valid_v004_identical_zero():
    vr = build_computation_complete_review()["valid_fixture_result_review"]
    r = next(p for p in vr["per_fixture"] if "v004" in p["fixture_id"])
    assert r["computed_lp_distance"] == 0.0


def test_valid_v005_general_p3():
    vr = build_computation_complete_review()["valid_fixture_result_review"]
    r = next(p for p in vr["per_fixture"] if "v005" in p["fixture_id"])
    assert r["computed_lp_distance"] == 6.0


def test_valid_v006_single_element():
    vr = build_computation_complete_review()["valid_fixture_result_review"]
    r = next(p for p in vr["per_fixture"] if "v006" in p["fixture_id"])
    assert r["computed_lp_distance"] == 3.0


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


def test_nc_review_all_correct():
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


def test_nc_001_empty_vector_reason():
    nc = build_computation_complete_review()["not_computable_fixture_rejection_review"]
    r = next(p for p in nc["per_fixture"] if "nc001" in p["fixture_id"])
    assert r["not_computable_reason"] == "EMPTY_VECTOR"


def test_nc_002_p_lt_one_reason():
    nc = build_computation_complete_review()["not_computable_fixture_rejection_review"]
    r = next(p for p in nc["per_fixture"] if "nc002" in p["fixture_id"])
    assert r["not_computable_reason"] == "P_PARAMETER_LT_ONE"


def test_nc_003_non_finite_reason():
    nc = build_computation_complete_review()["not_computable_fixture_rejection_review"]
    r = next(p for p in nc["per_fixture"] if "nc003" in p["fixture_id"])
    assert r["not_computable_reason"] == "NON_FINITE_ELEMENT_VALUE"


def test_nc_004_mismatched_reason():
    nc = build_computation_complete_review()["not_computable_fixture_rejection_review"]
    r = next(p for p in nc["per_fixture"] if "nc004" in p["fixture_id"])
    assert r["not_computable_reason"] == "MISMATCHED_VECTOR_LENGTH"


# ── comparison summary review ──────────────────────────────────────────────────


def test_comparison_summary_review_passed():
    assert (
        build_computation_complete_review()["comparison_summary_review"]["review_passed"]
        is True
    )


def test_comparison_summary_total_6():
    cs = build_computation_complete_review()["comparison_summary_review"]
    assert cs["total_valid_fixtures_confirmed"] is True


def test_comparison_summary_match_6():
    cs = build_computation_complete_review()["comparison_summary_review"]
    assert cs["match_count_confirmed"] is True


def test_comparison_summary_mismatch_zero():
    cs = build_computation_complete_review()["comparison_summary_review"]
    assert cs["mismatch_count_confirmed_zero"] is True


def test_comparison_summary_field_confirmed():
    cs = build_computation_complete_review()["comparison_summary_review"]
    assert cs["comparison_field_confirmed"] is True


def test_comparison_summary_all_valid_match():
    cs = build_computation_complete_review()["comparison_summary_review"]
    assert cs["all_valid_match_confirmed_true"] is True


# ── no_metric_emission review ──────────────────────────────────────────────────


def test_no_metric_emission_review_passed():
    assert (
        build_computation_complete_review()["no_metric_emission_review"]["review_passed"]
        is True
    )


def test_no_metric_emission_emits_false():
    r = build_computation_complete_review()["no_metric_emission_review"]
    assert r["emits_metric_values"] is False


def test_no_metric_emission_receipt_lock_confirmed():
    r = build_computation_complete_review()["no_metric_emission_review"]
    assert r["receipt_authority_lock_confirmed"] is True


# ── no_forecast_influence review ───────────────────────────────────────────────


def test_no_forecast_influence_review_passed():
    assert (
        build_computation_complete_review()["no_forecast_influence_review"]["review_passed"]
        is True
    )


def test_no_forecast_influence_projection_lane_false():
    r = build_computation_complete_review()["no_forecast_influence_review"]
    assert r["projection_lane_influence"] is False


def test_no_forecast_influence_receipt_lock_confirmed():
    r = build_computation_complete_review()["no_forecast_influence_review"]
    assert r["receipt_authority_lock_confirmed"] is True


# ── no_p43_surface_lane review ─────────────────────────────────────────────────


def test_no_p43_surface_lane_review_passed():
    assert (
        build_computation_complete_review()["no_p43_surface_lane_review"]["review_passed"]
        is True
    )


def test_no_p43_surface_lanes_false():
    r = build_computation_complete_review()["no_p43_surface_lane_review"]
    assert r["p43_surface_lanes_authorized"] is False


def test_no_p43_receipt_lock_confirmed():
    r = build_computation_complete_review()["no_p43_surface_lane_review"]
    assert r["receipt_authority_lock_confirmed"] is True


# ── authority_lock review ──────────────────────────────────────────────────────


def test_authority_lock_review_passed():
    assert (
        build_computation_complete_review()["authority_lock_review"]["review_passed"]
        is True
    )


def test_authority_lock_review_all_true_confirmed():
    alr = build_computation_complete_review()["authority_lock_review"]
    assert alr["all_true_locks_confirmed"] is True


def test_authority_lock_review_all_false_confirmed():
    alr = build_computation_complete_review()["authority_lock_review"]
    assert alr["all_false_locks_confirmed"] is True


def test_authority_lock_review_computation_stage():
    alr = build_computation_complete_review()["authority_lock_review"]
    assert alr["computation_stage_confirmed"] is True


def test_authority_lock_review_intended_lane():
    alr = build_computation_complete_review()["authority_lock_review"]
    assert alr["intended_lane_confirmed"] is True


# ── review authority locks ─────────────────────────────────────────────────────


def test_authority_locks_advisory_only():
    assert build_computation_complete_review()["authority_locks"]["advisory_only"] is True


def test_authority_locks_shadow_lane_only():
    assert build_computation_complete_review()["authority_locks"]["shadow_lane_only"] is True


def test_authority_locks_computation_complete_review_only():
    assert (
        build_computation_complete_review()["authority_locks"][
            "computation_complete_review_only"
        ]
        is True
    )


def test_authority_locks_test_vector_computation_only():
    assert (
        build_computation_complete_review()["authority_locks"]["test_vector_computation_only"]
        is True
    )


def test_authority_locks_norm_geometry_authorized():
    assert (
        build_computation_complete_review()["authority_locks"][
            "norm_geometry_computation_implementation_authorized"
        ]
        is True
    )


def test_authority_locks_emits_metric_false():
    assert build_computation_complete_review()["authority_locks"]["emits_metric_values"] is False


def test_authority_locks_forecast_influence_false():
    assert (
        build_computation_complete_review()["authority_locks"]["forecast_influence"] is False
    )


def test_authority_locks_p43_false():
    assert (
        build_computation_complete_review()["authority_locks"]["p43_surface_lanes_authorized"]
        is False
    )


def test_authority_locks_production_false():
    assert (
        build_computation_complete_review()["authority_locks"]["production_activation"] is False
    )


def test_authority_locks_canon_false():
    assert (
        build_computation_complete_review()["authority_locks"]["canon_promotion"] is False
    )


def test_authority_locks_runtime_mutation_false():
    assert (
        build_computation_complete_review()["authority_locks"]["runtime_mutation"] is False
    )


def test_authority_locks_execution_authority_false():
    assert (
        build_computation_complete_review()["authority_locks"]["execution_authority"] is False
    )


def test_authority_locks_inference_authority_false():
    assert (
        build_computation_complete_review()["authority_locks"]["inference_authority"] is False
    )


# ── blocked scopes ─────────────────────────────────────────────────────────────


def test_blocked_scopes_all_false():
    bs = build_computation_complete_review()["blocked_scopes"]
    for key, val in bs.items():
        assert val is False, f"blocked_scopes.{key} must be False, got {val!r}"


# ── validate: wrong schema_version ────────────────────────────────────────────


def test_validate_wrong_schema_version():
    r = build_computation_complete_review()
    r["schema_version"] = "WRONG"
    with pytest.raises(NormGeometryComputationCompleteReviewError, match="schema_version"):
        validate_computation_complete_review(r)


def test_validate_wrong_review_status():
    r = build_computation_complete_review()
    r["review_status"] = "WRONG"
    with pytest.raises(NormGeometryComputationCompleteReviewError, match="review_status"):
        validate_computation_complete_review(r)


def test_validate_wrong_operator_id():
    r = build_computation_complete_review()
    r["operator_id"] = "WRONG"
    with pytest.raises(NormGeometryComputationCompleteReviewError, match="operator_id"):
        validate_computation_complete_review(r)


def test_validate_wrong_intended_lane():
    r = build_computation_complete_review()
    r["intended_lane"] = "PRODUCTION"
    with pytest.raises(NormGeometryComputationCompleteReviewError, match="intended_lane"):
        validate_computation_complete_review(r)


def test_validate_wrong_receipt_hash():
    r = build_computation_complete_review()
    r["source_computation_receipt_hash"] = "a" * 64
    with pytest.raises(
        NormGeometryComputationCompleteReviewError, match="source_computation_receipt_hash"
    ):
        validate_computation_complete_review(r)


def test_validate_wrong_gate_hash():
    r = build_computation_complete_review()
    r["source_implementation_gate_hash"] = "b" * 64
    with pytest.raises(
        NormGeometryComputationCompleteReviewError, match="source_implementation_gate_hash"
    ):
        validate_computation_complete_review(r)


def test_validate_wrong_cpu_baseline_hash():
    r = build_computation_complete_review()
    r["source_cpu_baseline_plan_hash"] = "c" * 64
    with pytest.raises(
        NormGeometryComputationCompleteReviewError, match="source_cpu_baseline_plan_hash"
    ):
        validate_computation_complete_review(r)


def test_validate_canonical_hash_mismatch():
    r = build_computation_complete_review()
    r["canonical_hash"] = "d" * 64
    with pytest.raises(NormGeometryComputationCompleteReviewError, match="canonical_hash"):
        validate_computation_complete_review(r)


def test_validate_wrong_authority_lock_emits():
    r = build_computation_complete_review()
    r["authority_locks"] = dict(r["authority_locks"])
    r["authority_locks"]["emits_metric_values"] = True
    with pytest.raises(
        NormGeometryComputationCompleteReviewError, match="emits_metric_values"
    ):
        validate_computation_complete_review(r)


def test_validate_wrong_authority_lock_advisory():
    r = build_computation_complete_review()
    r["authority_locks"] = dict(r["authority_locks"])
    r["authority_locks"]["advisory_only"] = False
    with pytest.raises(NormGeometryComputationCompleteReviewError, match="advisory_only"):
        validate_computation_complete_review(r)
