"""Tests: WassersteinCpuBaselineComputationCompleteReview.v1."""

from __future__ import annotations

import json
import pathlib

import pytest

from core.wasserstein_cpu_baseline_computation_complete_review import (
    EXPECTED_INVALID_COUNT,
    EXPECTED_NC_COUNT,
    EXPECTED_VALID_COUNT,
    KERNEL_RECORDS,
    REVIEW_ID,
    REVIEW_STATUS,
    REVIEW_TYPE,
    SCHEMA_VERSION,
    SOURCE_COMPUTATION_RECEIPT_HASH,
    SOURCE_RECEIPT_LOCKED_SOLVER_POLICY,
    WassersteinCpuBaselineComputationCompleteReviewError,
    build_authority_lock_review,
    build_blocked_scope_review,
    build_comparison_summary_review,
    build_helper_kernel_scope_review,
    build_invalid_fixture_rejection_review,
    build_no_forecast_influence_review,
    build_no_metric_emission_review,
    build_no_p43_surface_lane_review,
    build_not_computable_fixture_rejection_review,
    build_receipt_presence_review,
    build_solver_policy_review,
    build_source_receipt_hash_review,
    build_valid_fixture_result_review,
    build_wasserstein_cpu_baseline_computation_complete_review,
    compute_wasserstein_cpu_baseline_computation_complete_review_hash,
    default_authority_locks,
    default_blocked_scopes,
    serialize_wasserstein_cpu_baseline_computation_complete_review,
)

_RECEIPT_PATH = (
    "out/metric_operator/"
    "wasserstein_cpu_baseline_computation_receipt_001.latest.json"
)


def _load_receipt() -> dict:
    return json.loads(pathlib.Path(_RECEIPT_PATH).read_text(encoding="utf-8"))


_RECEIPT = _load_receipt()
_VALID_RESULTS = _RECEIPT["valid_fixture_results"]
_INVALID_RESULTS = _RECEIPT["invalid_fixture_results"]
_NC_RESULTS = _RECEIPT["not_computable_fixture_results"]


def _payload(receipt: dict | None = None) -> dict:
    r = receipt if receipt is not None else _RECEIPT
    return {
        "review_id": REVIEW_ID,
        "intended_lane": "SHADOW",
        "review_stage": "COMPUTATION_COMPLETE_REVIEW_ONLY",
        "receipt_presence_review": build_receipt_presence_review(r),
        "source_receipt_hash_review": build_source_receipt_hash_review(r),
        "valid_fixture_result_review": build_valid_fixture_result_review(r["valid_fixture_results"]),
        "invalid_fixture_rejection_review": build_invalid_fixture_rejection_review(r["invalid_fixture_results"]),
        "not_computable_fixture_rejection_review": build_not_computable_fixture_rejection_review(r["not_computable_fixture_results"]),
        "comparison_summary_review": build_comparison_summary_review(r),
        "solver_policy_review": build_solver_policy_review(r),
        "helper_kernel_scope_review": build_helper_kernel_scope_review(),
        "no_metric_emission_review": build_no_metric_emission_review(r),
        "no_forecast_influence_review": build_no_forecast_influence_review(r),
        "no_p43_surface_lane_review": build_no_p43_surface_lane_review(r),
        "authority_lock_review": build_authority_lock_review(r),
        "blocked_scope_review": build_blocked_scope_review(r),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "WASSERSTEIN_CPU_BASELINE_COMPUTATION_AUTHORIZATION_DECISION",
        "provenance": {
            "source": "WASSERSTEIN_CPU_BASELINE_COMPUTATION_COMPLETE_REVIEW",
            "evidence_refs": [
                "WassersteinCpuBaselineComputationReceipt.v1:wasserstein_cpu_baseline_computation_receipt_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/wasserstein_cpu_baseline_computation_complete_review.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_schema_version() -> None:
    assert SCHEMA_VERSION == "WassersteinCpuBaselineComputationCompleteReview.v1"


def test_review_type() -> None:
    assert REVIEW_TYPE == "WASSERSTEIN_CPU_BASELINE_COMPUTATION_COMPLETE_REVIEW"


def test_review_status_constant() -> None:
    assert REVIEW_STATUS == "WASSERSTEIN_CPU_BASELINE_COMPUTATION_COMPLETE_REVIEW_READY"


def test_review_id_constant() -> None:
    assert REVIEW_ID == "wasserstein_cpu_baseline_computation_complete_review_001"


def test_source_computation_receipt_hash() -> None:
    assert (
        SOURCE_COMPUTATION_RECEIPT_HASH
        == "8c03e94b23efb32b6901117fab1cefdb134ea0ca4bf883b218711d46e57c336c"
    )


def test_solver_policy_constant() -> None:
    assert SOURCE_RECEIPT_LOCKED_SOLVER_POLICY == "DETERMINISTIC_1D_SORTED_CDF_TRANSPORT_ONLY"


def test_expected_counts() -> None:
    assert EXPECTED_VALID_COUNT == 5
    assert EXPECTED_INVALID_COUNT == 5
    assert EXPECTED_NC_COUNT == 4


def test_kernel_records_count() -> None:
    assert len(KERNEL_RECORDS) == 3


def test_kernel_records_all_lawful() -> None:
    for k in KERNEL_RECORDS:
        assert k["lawful"] is True, k["kernel_name"]


def test_kernel_records_no_runtime_authority_expansion() -> None:
    for k in KERNEL_RECORDS:
        assert k["runtime_authority_expansion"] is False, k["kernel_name"]


def test_kernel_records_classification() -> None:
    for k in KERNEL_RECORDS:
        assert k["classification"] == "TEST_VECTOR_FIXTURE_HELPER_KERNEL", k["kernel_name"]


# ---------------------------------------------------------------------------
# Receipt loading
# ---------------------------------------------------------------------------

def test_receipt_loads_correctly() -> None:
    assert _RECEIPT["computation_status"] == "WASSERSTEIN_CPU_BASELINE_COMPUTATION_COMPLETE"


def test_receipt_hash_matches_constant() -> None:
    assert _RECEIPT["canonical_hash"] == SOURCE_COMPUTATION_RECEIPT_HASH


def test_receipt_valid_count() -> None:
    assert len(_VALID_RESULTS) == 5


def test_receipt_invalid_count() -> None:
    assert len(_INVALID_RESULTS) == 5


def test_receipt_nc_count() -> None:
    assert len(_NC_RESULTS) == 4


# ---------------------------------------------------------------------------
# build_receipt_presence_review
# ---------------------------------------------------------------------------

def test_receipt_presence_review_status() -> None:
    r = build_receipt_presence_review(_RECEIPT)
    assert r["review_status"] == "RECEIPT_PRESENT_VERIFIED"


def test_receipt_presence_review_fields() -> None:
    r = build_receipt_presence_review(_RECEIPT)
    assert r["receipt_path_found"] is True
    assert r["receipt_id_present"] is True
    assert r["schema_version_present"] is True
    assert r["computation_status_present"] is True


def test_receipt_presence_review_missing_fields_raises() -> None:
    with pytest.raises(WassersteinCpuBaselineComputationCompleteReviewError):
        build_receipt_presence_review({})


# ---------------------------------------------------------------------------
# build_source_receipt_hash_review
# ---------------------------------------------------------------------------

def test_source_receipt_hash_review_status() -> None:
    r = build_source_receipt_hash_review(_RECEIPT)
    assert r["review_status"] == "SOURCE_RECEIPT_HASH_VERIFIED"


def test_source_receipt_hash_review_hashes_match() -> None:
    r = build_source_receipt_hash_review(_RECEIPT)
    assert r["hashes_match"] is True
    assert r["expected_hash"] == SOURCE_COMPUTATION_RECEIPT_HASH
    assert r["observed_hash"] == SOURCE_COMPUTATION_RECEIPT_HASH


def test_source_receipt_hash_review_wrong_hash_raises() -> None:
    bad = dict(_RECEIPT, canonical_hash="deadbeef")
    with pytest.raises(WassersteinCpuBaselineComputationCompleteReviewError, match="receipt_hash_mismatch"):
        build_source_receipt_hash_review(bad)


# ---------------------------------------------------------------------------
# build_valid_fixture_result_review
# ---------------------------------------------------------------------------

def test_valid_fixture_result_review_status() -> None:
    r = build_valid_fixture_result_review(_VALID_RESULTS)
    assert r["review_status"] == "VALID_FIXTURE_RESULTS_VERIFIED"


def test_valid_fixture_result_review_total() -> None:
    r = build_valid_fixture_result_review(_VALID_RESULTS)
    assert r["total_reviewed"] == 5


def test_valid_fixture_result_review_all_complete() -> None:
    r = build_valid_fixture_result_review(_VALID_RESULTS)
    assert r["all_computation_complete"] is True


def test_valid_fixture_result_review_all_shadow() -> None:
    r = build_valid_fixture_result_review(_VALID_RESULTS)
    assert r["all_shadow_lane"] is True


def test_valid_fixture_result_review_all_distance_matched() -> None:
    r = build_valid_fixture_result_review(_VALID_RESULTS)
    assert r["all_distance_matched"] is True


def test_valid_fixture_result_review_no_metric_values() -> None:
    r = build_valid_fixture_result_review(_VALID_RESULTS)
    assert r["no_metric_values_emitted"] is True


def test_valid_fixture_result_review_fixture_count() -> None:
    r = build_valid_fixture_result_review(_VALID_RESULTS)
    assert len(r["fixture_reviews"]) == 5


def test_valid_fixture_result_review_all_pass() -> None:
    r = build_valid_fixture_result_review(_VALID_RESULTS)
    for fr in r["fixture_reviews"]:
        assert fr["review_status"] == "PASS"


def test_valid_fixture_result_review_wrong_count_raises() -> None:
    with pytest.raises(WassersteinCpuBaselineComputationCompleteReviewError, match="valid_fixture_count_mismatch"):
        build_valid_fixture_result_review(_VALID_RESULTS[:3])


def test_valid_fixture_result_review_wrong_status_raises() -> None:
    bad = [dict(r, computation_status="SOMETHING_ELSE") for r in _VALID_RESULTS]
    with pytest.raises(WassersteinCpuBaselineComputationCompleteReviewError, match="valid_fixture_wrong_status"):
        build_valid_fixture_result_review(bad)


def test_valid_fixture_result_review_no_distance_match_raises() -> None:
    bad = [dict(r, distance_matched=False) for r in _VALID_RESULTS]
    with pytest.raises(WassersteinCpuBaselineComputationCompleteReviewError, match="valid_fixture_distance_not_matched"):
        build_valid_fixture_result_review(bad)


# ---------------------------------------------------------------------------
# build_invalid_fixture_rejection_review
# ---------------------------------------------------------------------------

def test_invalid_fixture_rejection_review_status() -> None:
    r = build_invalid_fixture_rejection_review(_INVALID_RESULTS)
    assert r["review_status"] == "INVALID_FIXTURE_REJECTIONS_VERIFIED"


def test_invalid_fixture_rejection_review_total() -> None:
    r = build_invalid_fixture_rejection_review(_INVALID_RESULTS)
    assert r["total_reviewed"] == 5


def test_invalid_fixture_rejection_review_all_invalid_input() -> None:
    r = build_invalid_fixture_rejection_review(_INVALID_RESULTS)
    assert r["all_invalid_input_status"] is True


def test_invalid_fixture_rejection_review_all_not_attempted() -> None:
    r = build_invalid_fixture_rejection_review(_INVALID_RESULTS)
    assert r["all_computation_not_attempted"] is True


def test_invalid_fixture_rejection_review_no_metric_values() -> None:
    r = build_invalid_fixture_rejection_review(_INVALID_RESULTS)
    assert r["no_metric_values_emitted"] is True


def test_invalid_fixture_rejection_review_fixture_count() -> None:
    r = build_invalid_fixture_rejection_review(_INVALID_RESULTS)
    assert len(r["fixture_reviews"]) == 5


def test_invalid_fixture_rejection_review_all_pass() -> None:
    r = build_invalid_fixture_rejection_review(_INVALID_RESULTS)
    for fr in r["fixture_reviews"]:
        assert fr["review_status"] == "PASS"


def test_invalid_fixture_rejection_review_wrong_count_raises() -> None:
    with pytest.raises(WassersteinCpuBaselineComputationCompleteReviewError, match="invalid_fixture_count_mismatch"):
        build_invalid_fixture_rejection_review(_INVALID_RESULTS[:2])


def test_invalid_fixture_rejection_review_wrong_status_raises() -> None:
    bad = [dict(r, computation_status="SHADOW_COMPUTATION_COMPLETE") for r in _INVALID_RESULTS]
    with pytest.raises(WassersteinCpuBaselineComputationCompleteReviewError, match="invalid_fixture_wrong_status"):
        build_invalid_fixture_rejection_review(bad)


def test_invalid_fixture_rejection_review_computation_attempted_raises() -> None:
    bad = [dict(r, computation_attempted=True) for r in _INVALID_RESULTS]
    with pytest.raises(WassersteinCpuBaselineComputationCompleteReviewError, match="invalid_fixture_computation_attempted_true"):
        build_invalid_fixture_rejection_review(bad)


# ---------------------------------------------------------------------------
# build_not_computable_fixture_rejection_review
# ---------------------------------------------------------------------------

def test_nc_fixture_rejection_review_status() -> None:
    r = build_not_computable_fixture_rejection_review(_NC_RESULTS)
    assert r["review_status"] == "NOT_COMPUTABLE_FIXTURE_REJECTIONS_VERIFIED"


def test_nc_fixture_rejection_review_total() -> None:
    r = build_not_computable_fixture_rejection_review(_NC_RESULTS)
    assert r["total_reviewed"] == 4


def test_nc_fixture_rejection_review_all_not_computable() -> None:
    r = build_not_computable_fixture_rejection_review(_NC_RESULTS)
    assert r["all_not_computable_status"] is True


def test_nc_fixture_rejection_review_all_not_attempted() -> None:
    r = build_not_computable_fixture_rejection_review(_NC_RESULTS)
    assert r["all_computation_not_attempted"] is True


def test_nc_fixture_rejection_review_no_metric_values() -> None:
    r = build_not_computable_fixture_rejection_review(_NC_RESULTS)
    assert r["no_metric_values_emitted"] is True


def test_nc_fixture_rejection_review_fixture_count() -> None:
    r = build_not_computable_fixture_rejection_review(_NC_RESULTS)
    assert len(r["fixture_reviews"]) == 4


def test_nc_fixture_rejection_review_all_pass() -> None:
    r = build_not_computable_fixture_rejection_review(_NC_RESULTS)
    for fr in r["fixture_reviews"]:
        assert fr["review_status"] == "PASS"


def test_nc_fixture_rejection_review_wrong_count_raises() -> None:
    with pytest.raises(WassersteinCpuBaselineComputationCompleteReviewError, match="nc_fixture_count_mismatch"):
        build_not_computable_fixture_rejection_review(_NC_RESULTS[:2])


def test_nc_fixture_rejection_review_wrong_status_raises() -> None:
    bad = [dict(r, computation_status="INVALID_INPUT") for r in _NC_RESULTS]
    with pytest.raises(WassersteinCpuBaselineComputationCompleteReviewError, match="nc_fixture_wrong_status"):
        build_not_computable_fixture_rejection_review(bad)


# ---------------------------------------------------------------------------
# build_comparison_summary_review
# ---------------------------------------------------------------------------

def test_comparison_summary_review_status() -> None:
    r = build_comparison_summary_review(_RECEIPT)
    assert r["review_status"] == "COMPARISON_SUMMARY_VERIFIED"


def test_comparison_summary_review_all_matched() -> None:
    r = build_comparison_summary_review(_RECEIPT)
    assert r["all_matched_observed"] is True


def test_comparison_summary_review_counts() -> None:
    r = build_comparison_summary_review(_RECEIPT)
    assert r["valid_matched_observed"] == 5
    assert r["invalid_routed_observed"] == 5
    assert r["nc_routed_observed"] == 4


def test_comparison_summary_review_basis() -> None:
    r = build_comparison_summary_review(_RECEIPT)
    assert r["comparison_basis_observed"] == "FIXTURE_DECLARED_EXPECTED_DISTANCE"


def test_comparison_summary_review_not_all_matched_raises() -> None:
    bad = dict(_RECEIPT)
    bad["comparison_summary"] = dict(_RECEIPT["comparison_summary"], all_matched=False)
    with pytest.raises(WassersteinCpuBaselineComputationCompleteReviewError, match="comparison_summary_all_matched_false"):
        build_comparison_summary_review(bad)


# ---------------------------------------------------------------------------
# build_solver_policy_review
# ---------------------------------------------------------------------------

def test_solver_policy_review_status() -> None:
    r = build_solver_policy_review(_RECEIPT)
    assert r["review_status"] == "SOLVER_POLICY_VERIFIED"


def test_solver_policy_review_policy_observed() -> None:
    r = build_solver_policy_review(_RECEIPT)
    assert r["solver_policy_observed"] == "DETERMINISTIC_1D_SORTED_CDF_TRANSPORT_ONLY"


def test_solver_policy_review_deterministic() -> None:
    r = build_solver_policy_review(_RECEIPT)
    assert r["deterministic_observed"] is True


def test_solver_policy_review_no_external_solver() -> None:
    r = build_solver_policy_review(_RECEIPT)
    assert r["no_external_solver_observed"] is True


def test_solver_policy_review_shadow_only() -> None:
    r = build_solver_policy_review(_RECEIPT)
    assert r["shadow_only_observed"] is True


def test_solver_policy_review_wrong_policy_raises() -> None:
    bad = dict(_RECEIPT)
    bad["solver_policy_summary"] = dict(_RECEIPT["solver_policy_summary"], solver_policy="SOME_OTHER_POLICY")
    with pytest.raises(WassersteinCpuBaselineComputationCompleteReviewError, match="solver_policy_mismatch"):
        build_solver_policy_review(bad)


# ---------------------------------------------------------------------------
# build_helper_kernel_scope_review
# ---------------------------------------------------------------------------

def test_helper_kernel_scope_review_status() -> None:
    r = build_helper_kernel_scope_review()
    assert r["review_status"] == "HELPER_KERNELS_VERIFIED_TEST_VECTOR_FIXTURE_HELPERS_ONLY"


def test_helper_kernel_scope_review_kernel_count() -> None:
    r = build_helper_kernel_scope_review()
    assert len(r["kernels_reviewed"]) == 3


def test_helper_kernel_scope_review_all_classified() -> None:
    r = build_helper_kernel_scope_review()
    assert r["all_classified_as_test_vector_fixture_helpers"] is True


def test_helper_kernel_scope_review_no_runtime_authority_expansion() -> None:
    r = build_helper_kernel_scope_review()
    assert r["no_runtime_authority_expansion"] is True


def test_helper_kernel_scope_review_kernel_names() -> None:
    r = build_helper_kernel_scope_review()
    names = {k["kernel_name"] for k in r["kernels_reviewed"]}
    assert names == {"_w1_sorted_cdf", "_euclidean_distance", "_greedy_min_cost_transport"}


def test_helper_kernel_scope_review_all_kernels_pass() -> None:
    r = build_helper_kernel_scope_review()
    for k in r["kernels_reviewed"]:
        assert k["review_status"] == "PASS"
        assert k["runtime_authority_expansion"] is False
        assert k["classification"] == "TEST_VECTOR_FIXTURE_HELPER_KERNEL"


def test_helper_kernel_scope_review_euclidean_serves_reference_vector() -> None:
    r = build_helper_kernel_scope_review()
    euc = next(k for k in r["kernels_reviewed"] if k["kernel_name"] == "_euclidean_distance")
    assert "REFERENCE_VECTOR" in euc["fixture_families_served"]
    assert "valid-003" in euc["fixture_ids_served"]


def test_helper_kernel_scope_review_greedy_serves_ground_metric() -> None:
    r = build_helper_kernel_scope_review()
    gmc = next(k for k in r["kernels_reviewed"] if k["kernel_name"] == "_greedy_min_cost_transport")
    assert "GROUND_METRIC" in gmc["fixture_families_served"]
    assert "valid-004" in gmc["fixture_ids_served"]


def test_helper_kernel_scope_review_w1_cdf_serves_three_families() -> None:
    r = build_helper_kernel_scope_review()
    w1 = next(k for k in r["kernels_reviewed"] if k["kernel_name"] == "_w1_sorted_cdf")
    assert "DISTRIBUTION_PAIR" in w1["fixture_families_served"]
    assert "WEIGHTED_HISTOGRAM" in w1["fixture_families_served"]
    assert "DEGENERATE_DISTRIBUTION" in w1["fixture_families_served"]


def test_helper_kernel_scope_review_fixture_family_bindings_count() -> None:
    r = build_helper_kernel_scope_review()
    assert len(r["fixture_family_bindings"]) == 3


# ---------------------------------------------------------------------------
# build_no_metric_emission_review
# ---------------------------------------------------------------------------

def test_no_metric_emission_review_status() -> None:
    r = build_no_metric_emission_review(_RECEIPT)
    assert r["review_status"] == "NO_METRIC_VALUES_EMITTED_VERIFIED"


def test_no_metric_emission_review_source_false() -> None:
    r = build_no_metric_emission_review(_RECEIPT)
    assert r["source_emits_metric_values"] is False


def test_no_metric_emission_review_all_false() -> None:
    r = build_no_metric_emission_review(_RECEIPT)
    assert r["all_valid_metric_value_emitted_false"] is True
    assert r["all_invalid_metric_value_emitted_false"] is True
    assert r["all_nc_metric_value_emitted_false"] is True


def test_no_metric_emission_review_emits_metric_values_true_raises() -> None:
    bad = dict(_RECEIPT)
    bad["authority_locks"] = dict(_RECEIPT["authority_locks"], emits_metric_values=True)
    with pytest.raises(WassersteinCpuBaselineComputationCompleteReviewError, match="source_emits_metric_values_not_false"):
        build_no_metric_emission_review(bad)


# ---------------------------------------------------------------------------
# build_no_forecast_influence_review
# ---------------------------------------------------------------------------

def test_no_forecast_influence_review_status() -> None:
    r = build_no_forecast_influence_review(_RECEIPT)
    assert r["review_status"] == "NO_FORECAST_INFLUENCE_VERIFIED"


def test_no_forecast_influence_review_fields() -> None:
    r = build_no_forecast_influence_review(_RECEIPT)
    assert r["source_forecast_influence"] is False
    assert r["no_forecast_binding"] is True
    assert r["no_p43_output"] is True


def test_no_forecast_influence_review_raises_if_true() -> None:
    bad = dict(_RECEIPT)
    bad["authority_locks"] = dict(_RECEIPT["authority_locks"], forecast_influence=True)
    with pytest.raises(WassersteinCpuBaselineComputationCompleteReviewError, match="source_forecast_influence_not_false"):
        build_no_forecast_influence_review(bad)


# ---------------------------------------------------------------------------
# build_no_p43_surface_lane_review
# ---------------------------------------------------------------------------

def test_no_p43_surface_lane_review_status() -> None:
    r = build_no_p43_surface_lane_review(_RECEIPT)
    assert r["review_status"] == "NO_P43_SURFACE_LANES_VERIFIED"


def test_no_p43_surface_lane_review_fields() -> None:
    r = build_no_p43_surface_lane_review(_RECEIPT)
    assert r["source_p43_surface_lanes_authorized"] is False
    assert r["no_p43_lanes_opened"] is True
    assert r["no_runtime_binding"] is True


def test_no_p43_surface_lane_review_raises_if_true() -> None:
    bad = dict(_RECEIPT)
    bad["authority_locks"] = dict(_RECEIPT["authority_locks"], p43_surface_lanes_authorized=True)
    with pytest.raises(WassersteinCpuBaselineComputationCompleteReviewError, match="source_p43_surface_lanes_authorized_not_false"):
        build_no_p43_surface_lane_review(bad)


# ---------------------------------------------------------------------------
# build_authority_lock_review
# ---------------------------------------------------------------------------

def test_authority_lock_review_status() -> None:
    r = build_authority_lock_review(_RECEIPT)
    assert r["review_status"] == "AUTHORITY_LOCKS_VERIFIED"


def test_authority_lock_review_all_locks_intact() -> None:
    r = build_authority_lock_review(_RECEIPT)
    assert r["all_locks_intact"] is True


def test_authority_lock_review_true_locks() -> None:
    r = build_authority_lock_review(_RECEIPT)
    assert r["source_advisory_only"] is True
    assert r["source_shadow_lane_only"] is True
    assert r["source_test_vector_computation_only"] is True
    assert r["source_wasserstein_cpu_baseline_computation_authorized"] is True


def test_authority_lock_review_false_locks() -> None:
    r = build_authority_lock_review(_RECEIPT)
    assert r["source_emits_metric_values"] is False
    assert r["source_forecast_influence"] is False
    assert r["source_p43_surface_lanes_authorized"] is False
    assert r["source_production_activation"] is False
    assert r["source_canon_promotion"] is False
    assert r["source_runtime_mutation"] is False
    assert r["source_execution_authority"] is False
    assert r["source_inference_authority"] is False


def test_authority_lock_review_broken_lock_raises() -> None:
    bad = dict(_RECEIPT)
    bad["authority_locks"] = dict(_RECEIPT["authority_locks"], advisory_only=False)
    with pytest.raises(WassersteinCpuBaselineComputationCompleteReviewError, match="authority_lock_check_failed"):
        build_authority_lock_review(bad)


# ---------------------------------------------------------------------------
# build_blocked_scope_review
# ---------------------------------------------------------------------------

def test_blocked_scope_review_status() -> None:
    r = build_blocked_scope_review(_RECEIPT)
    assert r["review_status"] == "BLOCKED_SCOPES_VERIFIED"


def test_blocked_scope_review_all_false() -> None:
    r = build_blocked_scope_review(_RECEIPT)
    assert r["all_blocked_scopes_false"] is True


def test_blocked_scope_review_verified_count() -> None:
    r = build_blocked_scope_review(_RECEIPT)
    assert len(r["blocked_scopes_verified"]) == len(_RECEIPT["blocked_scopes"])


def test_blocked_scope_review_raises_if_scope_true() -> None:
    bad = dict(_RECEIPT)
    bad["blocked_scopes"] = dict(_RECEIPT["blocked_scopes"], emits_metric_values=True)
    with pytest.raises(WassersteinCpuBaselineComputationCompleteReviewError, match="blocked_scope_not_false"):
        build_blocked_scope_review(bad)


# ---------------------------------------------------------------------------
# default_authority_locks / default_blocked_scopes
# ---------------------------------------------------------------------------

def test_default_authority_locks_true_keys() -> None:
    al = default_authority_locks()
    assert al["advisory_only"] is True
    assert al["shadow_lane_only"] is True
    assert al["computation_complete_review_only"] is True
    assert al["test_vector_computation_only"] is True
    assert al["wasserstein_cpu_baseline_implementation_authorized"] is True


def test_default_authority_locks_false_keys() -> None:
    al = default_authority_locks()
    assert al["emits_metric_values"] is False
    assert al["forecast_influence"] is False
    assert al["p43_surface_lanes_authorized"] is False
    assert al["production_activation"] is False
    assert al["canon_promotion"] is False
    assert al["runtime_mutation"] is False
    assert al["execution_authority"] is False
    assert al["inference_authority"] is False


def test_default_blocked_scopes_all_false() -> None:
    bs = default_blocked_scopes()
    for scope, value in bs.items():
        assert value is False, scope


# ---------------------------------------------------------------------------
# build_wasserstein_cpu_baseline_computation_complete_review (end-to-end)
# ---------------------------------------------------------------------------

def test_end_to_end_build_status() -> None:
    packet = build_wasserstein_cpu_baseline_computation_complete_review(_payload())
    assert packet["review_status"] == "WASSERSTEIN_CPU_BASELINE_COMPUTATION_COMPLETE_REVIEW_READY"


def test_end_to_end_schema_version() -> None:
    packet = build_wasserstein_cpu_baseline_computation_complete_review(_payload())
    assert packet["schema_version"] == "WassersteinCpuBaselineComputationCompleteReview.v1"


def test_end_to_end_review_type() -> None:
    packet = build_wasserstein_cpu_baseline_computation_complete_review(_payload())
    assert packet["review_type"] == "WASSERSTEIN_CPU_BASELINE_COMPUTATION_COMPLETE_REVIEW"


def test_end_to_end_operator_id() -> None:
    packet = build_wasserstein_cpu_baseline_computation_complete_review(_payload())
    assert packet["operator_id"] == "WASSERSTEIN"


def test_end_to_end_intended_lane() -> None:
    packet = build_wasserstein_cpu_baseline_computation_complete_review(_payload())
    assert packet["intended_lane"] == "SHADOW"


def test_end_to_end_review_stage() -> None:
    packet = build_wasserstein_cpu_baseline_computation_complete_review(_payload())
    assert packet["review_stage"] == "COMPUTATION_COMPLETE_REVIEW_ONLY"


def test_end_to_end_source_receipt_hash() -> None:
    packet = build_wasserstein_cpu_baseline_computation_complete_review(_payload())
    assert packet["source_computation_receipt_hash"] == SOURCE_COMPUTATION_RECEIPT_HASH


def test_end_to_end_canonical_hash_present() -> None:
    packet = build_wasserstein_cpu_baseline_computation_complete_review(_payload())
    assert "canonical_hash" in packet
    assert len(packet["canonical_hash"]) == 64


def test_end_to_end_canonical_hash_deterministic() -> None:
    p1 = build_wasserstein_cpu_baseline_computation_complete_review(_payload())
    p2 = build_wasserstein_cpu_baseline_computation_complete_review(_payload())
    assert p1["canonical_hash"] == p2["canonical_hash"]


def test_end_to_end_authority_locks_intact() -> None:
    packet = build_wasserstein_cpu_baseline_computation_complete_review(_payload())
    al = packet["authority_locks"]
    assert al["emits_metric_values"] is False
    assert al["forecast_influence"] is False
    assert al["p43_surface_lanes_authorized"] is False
    assert al["production_activation"] is False
    assert al["canon_promotion"] is False
    assert al["runtime_mutation"] is False
    assert al["execution_authority"] is False
    assert al["inference_authority"] is False
    assert al["advisory_only"] is True
    assert al["shadow_lane_only"] is True
    assert al["computation_complete_review_only"] is True
    assert al["wasserstein_cpu_baseline_implementation_authorized"] is True


def test_end_to_end_blocked_scopes_all_false() -> None:
    packet = build_wasserstein_cpu_baseline_computation_complete_review(_payload())
    for scope, value in packet["blocked_scopes"].items():
        assert value is False, scope


def test_end_to_end_all_review_sections_present() -> None:
    packet = build_wasserstein_cpu_baseline_computation_complete_review(_payload())
    required = [
        "receipt_presence_review", "source_receipt_hash_review",
        "valid_fixture_result_review", "invalid_fixture_rejection_review",
        "not_computable_fixture_rejection_review", "comparison_summary_review",
        "solver_policy_review", "helper_kernel_scope_review",
        "no_metric_emission_review", "no_forecast_influence_review",
        "no_p43_surface_lane_review", "authority_lock_review", "blocked_scope_review",
    ]
    for section in required:
        assert section in packet, f"missing section: {section}"


def test_end_to_end_recommended_next_step() -> None:
    packet = build_wasserstein_cpu_baseline_computation_complete_review(_payload())
    assert packet["recommended_next_step"] == "WASSERSTEIN_CPU_BASELINE_COMPUTATION_AUTHORIZATION_DECISION"


# ---------------------------------------------------------------------------
# compute_hash
# ---------------------------------------------------------------------------

def test_compute_hash_excludes_canonical_hash() -> None:
    packet = build_wasserstein_cpu_baseline_computation_complete_review(_payload())
    h1 = compute_wasserstein_cpu_baseline_computation_complete_review_hash(packet)
    packet_no_hash = dict(packet)
    packet_no_hash.pop("canonical_hash", None)
    h2 = compute_wasserstein_cpu_baseline_computation_complete_review_hash(packet_no_hash)
    assert h1 == h2


def test_compute_hash_is_64_hex_chars() -> None:
    packet = build_wasserstein_cpu_baseline_computation_complete_review(_payload())
    h = compute_wasserstein_cpu_baseline_computation_complete_review_hash(packet)
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


# ---------------------------------------------------------------------------
# serialize
# ---------------------------------------------------------------------------

def test_serialize_produces_valid_json() -> None:
    packet = build_wasserstein_cpu_baseline_computation_complete_review(_payload())
    text = serialize_wasserstein_cpu_baseline_computation_complete_review(packet)
    parsed = json.loads(text)
    assert parsed["schema_version"] == SCHEMA_VERSION


def test_serialize_canonical_hash_survives_roundtrip() -> None:
    packet = build_wasserstein_cpu_baseline_computation_complete_review(_payload())
    text = serialize_wasserstein_cpu_baseline_computation_complete_review(packet)
    parsed = json.loads(text)
    assert parsed["canonical_hash"] == packet["canonical_hash"]
