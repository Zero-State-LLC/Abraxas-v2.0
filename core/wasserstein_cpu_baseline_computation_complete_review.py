"""Core: WassersteinCpuBaselineComputationCompleteReview.v1."""

from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinCpuBaselineComputationCompleteReview.v1"
REVIEW_TYPE = "WASSERSTEIN_CPU_BASELINE_COMPUTATION_COMPLETE_REVIEW"
REVIEW_STATUS = "WASSERSTEIN_CPU_BASELINE_COMPUTATION_COMPLETE_REVIEW_READY"
OPERATOR_ID = "WASSERSTEIN"
REVIEW_ID = "wasserstein_cpu_baseline_computation_complete_review_001"

SOURCE_COMPUTATION_RECEIPT_HASH = (
    "8c03e94b23efb32b6901117fab1cefdb134ea0ca4bf883b218711d46e57c336c"
)

COMPUTATION_RECEIPT_PATH = (
    "out/metric_operator/"
    "wasserstein_cpu_baseline_computation_receipt_001.latest.json"
)

ALLOWED_LANE = ("SHADOW",)
ALLOWED_STAGE = ("COMPUTATION_COMPLETE_REVIEW_ONLY",)

EXPECTED_VALID_COUNT = 5
EXPECTED_INVALID_COUNT = 5
EXPECTED_NC_COUNT = 4

KERNEL_RECORDS: list[dict[str, Any]] = [
    {
        "kernel_name": "_w1_sorted_cdf",
        "fixture_families": ["DISTRIBUTION_PAIR", "WEIGHTED_HISTOGRAM", "DEGENERATE_DISTRIBUTION"],
        "fixture_ids": ["valid-001", "valid-002", "valid-005"],
        "classification": "TEST_VECTOR_FIXTURE_HELPER_KERNEL",
        "runtime_authority_expansion": False,
        "lawful": True,
    },
    {
        "kernel_name": "_euclidean_distance",
        "fixture_families": ["REFERENCE_VECTOR"],
        "fixture_ids": ["valid-003"],
        "classification": "TEST_VECTOR_FIXTURE_HELPER_KERNEL",
        "runtime_authority_expansion": False,
        "lawful": True,
    },
    {
        "kernel_name": "_greedy_min_cost_transport",
        "fixture_families": ["GROUND_METRIC"],
        "fixture_ids": ["valid-004"],
        "classification": "TEST_VECTOR_FIXTURE_HELPER_KERNEL",
        "runtime_authority_expansion": False,
        "lawful": True,
    },
]

SOURCE_RECEIPT_LOCKED_SOLVER_POLICY = "DETERMINISTIC_1D_SORTED_CDF_TRANSPORT_ONLY"


class WassersteinCpuBaselineComputationCompleteReviewError(ValueError):
    pass


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def load_and_verify_computation_receipt(
    receipt_path: str = COMPUTATION_RECEIPT_PATH,
) -> dict[str, Any]:
    with open(receipt_path, encoding="utf-8") as fh:
        receipt = json.load(fh)
    stored_hash = receipt.get("canonical_hash", "")
    if stored_hash != SOURCE_COMPUTATION_RECEIPT_HASH:
        raise WassersteinCpuBaselineComputationCompleteReviewError(
            f"receipt_hash_mismatch: expected={SOURCE_COMPUTATION_RECEIPT_HASH!r} "
            f"got={stored_hash!r}"
        )
    return receipt


def build_receipt_presence_review(receipt: dict[str, Any]) -> dict[str, Any]:
    receipt_id_present = bool(receipt.get("receipt_id"))
    schema_version_present = bool(receipt.get("schema_version"))
    computation_status_present = bool(receipt.get("computation_status"))
    if not (receipt_id_present and schema_version_present and computation_status_present):
        raise WassersteinCpuBaselineComputationCompleteReviewError(
            "receipt_presence_check_failed: missing required top-level fields"
        )
    return {
        "receipt_path_found": True,
        "receipt_id_present": True,
        "schema_version_present": True,
        "computation_status_present": True,
        "review_status": "RECEIPT_PRESENT_VERIFIED",
    }


def build_source_receipt_hash_review(receipt: dict[str, Any]) -> dict[str, Any]:
    observed_hash = receipt.get("canonical_hash", "")
    hashes_match = observed_hash == SOURCE_COMPUTATION_RECEIPT_HASH
    if not hashes_match:
        raise WassersteinCpuBaselineComputationCompleteReviewError(
            f"source_receipt_hash_mismatch: expected={SOURCE_COMPUTATION_RECEIPT_HASH!r} "
            f"got={observed_hash!r}"
        )
    return {
        "expected_hash": SOURCE_COMPUTATION_RECEIPT_HASH,
        "observed_hash": observed_hash,
        "hashes_match": True,
        "review_status": "SOURCE_RECEIPT_HASH_VERIFIED",
    }


def build_valid_fixture_result_review(
    valid_results: list[dict[str, Any]],
) -> dict[str, Any]:
    if len(valid_results) != EXPECTED_VALID_COUNT:
        raise WassersteinCpuBaselineComputationCompleteReviewError(
            f"valid_fixture_count_mismatch: expected={EXPECTED_VALID_COUNT} "
            f"got={len(valid_results)}"
        )
    fixture_reviews = []
    for r in valid_results:
        fid = r["fixture_id"]
        if r.get("computation_status") != "SHADOW_COMPUTATION_COMPLETE":
            raise WassersteinCpuBaselineComputationCompleteReviewError(
                f"valid_fixture_wrong_status:{fid}:{r.get('computation_status')}"
            )
        if not r.get("distance_matched"):
            raise WassersteinCpuBaselineComputationCompleteReviewError(
                f"valid_fixture_distance_not_matched:{fid}"
            )
        if r.get("shadow_lane") != "SHADOW":
            raise WassersteinCpuBaselineComputationCompleteReviewError(
                f"valid_fixture_not_shadow:{fid}"
            )
        if r.get("metric_value_emitted") is not False:
            raise WassersteinCpuBaselineComputationCompleteReviewError(
                f"metric_value_emitted_true:{fid}"
            )
        fixture_reviews.append(
            {
                "fixture_id": fid,
                "fixture_group": r["fixture_group"],
                "computation_status_observed": r["computation_status"],
                "shadow_lane_observed": r["shadow_lane"],
                "distance_matched": True,
                "metric_value_emitted": False,
                "review_status": "PASS",
            }
        )
    return {
        "total_reviewed": EXPECTED_VALID_COUNT,
        "all_computation_complete": True,
        "all_shadow_lane": True,
        "all_distance_matched": True,
        "no_metric_values_emitted": True,
        "fixture_reviews": fixture_reviews,
        "review_status": "VALID_FIXTURE_RESULTS_VERIFIED",
    }


def build_invalid_fixture_rejection_review(
    invalid_results: list[dict[str, Any]],
) -> dict[str, Any]:
    if len(invalid_results) != EXPECTED_INVALID_COUNT:
        raise WassersteinCpuBaselineComputationCompleteReviewError(
            f"invalid_fixture_count_mismatch: expected={EXPECTED_INVALID_COUNT} "
            f"got={len(invalid_results)}"
        )
    fixture_reviews = []
    for r in invalid_results:
        fid = r["fixture_id"]
        if r.get("computation_status") != "INVALID_INPUT":
            raise WassersteinCpuBaselineComputationCompleteReviewError(
                f"invalid_fixture_wrong_status:{fid}:{r.get('computation_status')}"
            )
        if r.get("computation_attempted") is not False:
            raise WassersteinCpuBaselineComputationCompleteReviewError(
                f"invalid_fixture_computation_attempted_true:{fid}"
            )
        if r.get("metric_value_emitted") is not False:
            raise WassersteinCpuBaselineComputationCompleteReviewError(
                f"metric_value_emitted_true:{fid}"
            )
        fixture_reviews.append(
            {
                "fixture_id": fid,
                "fixture_group": r["fixture_group"],
                "computation_status_observed": r["computation_status"],
                "computation_attempted": False,
                "rejection_reason_present": bool(r.get("rejection_reason")),
                "metric_value_emitted": False,
                "review_status": "PASS",
            }
        )
    return {
        "total_reviewed": EXPECTED_INVALID_COUNT,
        "all_invalid_input_status": True,
        "all_computation_not_attempted": True,
        "no_metric_values_emitted": True,
        "fixture_reviews": fixture_reviews,
        "review_status": "INVALID_FIXTURE_REJECTIONS_VERIFIED",
    }


def build_not_computable_fixture_rejection_review(
    nc_results: list[dict[str, Any]],
) -> dict[str, Any]:
    if len(nc_results) != EXPECTED_NC_COUNT:
        raise WassersteinCpuBaselineComputationCompleteReviewError(
            f"nc_fixture_count_mismatch: expected={EXPECTED_NC_COUNT} "
            f"got={len(nc_results)}"
        )
    fixture_reviews = []
    for r in nc_results:
        fid = r["fixture_id"]
        if r.get("computation_status") != "NOT_COMPUTABLE":
            raise WassersteinCpuBaselineComputationCompleteReviewError(
                f"nc_fixture_wrong_status:{fid}:{r.get('computation_status')}"
            )
        if r.get("computation_attempted") is not False:
            raise WassersteinCpuBaselineComputationCompleteReviewError(
                f"nc_fixture_computation_attempted_true:{fid}"
            )
        if r.get("metric_value_emitted") is not False:
            raise WassersteinCpuBaselineComputationCompleteReviewError(
                f"metric_value_emitted_true:{fid}"
            )
        fixture_reviews.append(
            {
                "fixture_id": fid,
                "fixture_group": r["fixture_group"],
                "computation_status_observed": r["computation_status"],
                "computation_attempted": False,
                "rejection_reason_present": bool(r.get("rejection_reason")),
                "metric_value_emitted": False,
                "review_status": "PASS",
            }
        )
    return {
        "total_reviewed": EXPECTED_NC_COUNT,
        "all_not_computable_status": True,
        "all_computation_not_attempted": True,
        "no_metric_values_emitted": True,
        "fixture_reviews": fixture_reviews,
        "review_status": "NOT_COMPUTABLE_FIXTURE_REJECTIONS_VERIFIED",
    }


def build_comparison_summary_review(receipt: dict[str, Any]) -> dict[str, Any]:
    cs = receipt.get("comparison_summary", {})
    if not cs.get("all_matched"):
        raise WassersteinCpuBaselineComputationCompleteReviewError(
            "comparison_summary_all_matched_false"
        )
    if cs.get("valid_matched") != EXPECTED_VALID_COUNT:
        raise WassersteinCpuBaselineComputationCompleteReviewError(
            f"valid_matched_mismatch: expected={EXPECTED_VALID_COUNT} "
            f"got={cs.get('valid_matched')}"
        )
    if cs.get("invalid_routed_as_invalid_input") != EXPECTED_INVALID_COUNT:
        raise WassersteinCpuBaselineComputationCompleteReviewError(
            f"invalid_routed_mismatch: expected={EXPECTED_INVALID_COUNT} "
            f"got={cs.get('invalid_routed_as_invalid_input')}"
        )
    if cs.get("nc_routed_as_not_computable") != EXPECTED_NC_COUNT:
        raise WassersteinCpuBaselineComputationCompleteReviewError(
            f"nc_routed_mismatch: expected={EXPECTED_NC_COUNT} "
            f"got={cs.get('nc_routed_as_not_computable')}"
        )
    return {
        "all_matched_observed": True,
        "valid_matched_observed": EXPECTED_VALID_COUNT,
        "invalid_routed_observed": EXPECTED_INVALID_COUNT,
        "nc_routed_observed": EXPECTED_NC_COUNT,
        "comparison_basis_observed": cs.get("comparison_basis", ""),
        "comparison_abs_tolerance_observed": cs.get("comparison_abs_tolerance"),
        "review_status": "COMPARISON_SUMMARY_VERIFIED",
    }


def build_solver_policy_review(receipt: dict[str, Any]) -> dict[str, Any]:
    sp = receipt.get("solver_policy_summary", {})
    policy = sp.get("solver_policy", "")
    if policy != SOURCE_RECEIPT_LOCKED_SOLVER_POLICY:
        raise WassersteinCpuBaselineComputationCompleteReviewError(
            f"solver_policy_mismatch: expected={SOURCE_RECEIPT_LOCKED_SOLVER_POLICY!r} "
            f"got={policy!r}"
        )
    if not sp.get("deterministic"):
        raise WassersteinCpuBaselineComputationCompleteReviewError(
            "solver_policy_not_deterministic"
        )
    if not sp.get("no_external_solver"):
        raise WassersteinCpuBaselineComputationCompleteReviewError(
            "external_solver_present"
        )
    if not sp.get("shadow_only"):
        raise WassersteinCpuBaselineComputationCompleteReviewError(
            "solver_not_shadow_only"
        )
    nc_branches = sp.get("not_computable_branches", [])
    return {
        "solver_policy_observed": policy,
        "deterministic_observed": True,
        "no_external_solver_observed": True,
        "shadow_only_observed": True,
        "not_computable_branches_count_observed": len(nc_branches),
        "review_status": "SOLVER_POLICY_VERIFIED",
    }


def build_helper_kernel_scope_review() -> dict[str, Any]:
    kernels_reviewed = []
    fixture_family_bindings = []
    for k in KERNEL_RECORDS:
        if not k["lawful"]:
            raise WassersteinCpuBaselineComputationCompleteReviewError(
                f"helper_kernel_not_lawful:{k['kernel_name']}"
            )
        if k["runtime_authority_expansion"]:
            raise WassersteinCpuBaselineComputationCompleteReviewError(
                f"helper_kernel_expands_runtime_authority:{k['kernel_name']}"
            )
        if k["classification"] != "TEST_VECTOR_FIXTURE_HELPER_KERNEL":
            raise WassersteinCpuBaselineComputationCompleteReviewError(
                f"helper_kernel_wrong_classification:{k['kernel_name']}:"
                f"{k['classification']}"
            )
        kernels_reviewed.append(
            {
                "kernel_name": k["kernel_name"],
                "classification": k["classification"],
                "runtime_authority_expansion": False,
                "fixture_families_served": k["fixture_families"],
                "fixture_ids_served": k["fixture_ids"],
                "review_status": "PASS",
            }
        )
        fixture_family_bindings.append(
            {
                "kernel_name": k["kernel_name"],
                "fixture_families": k["fixture_families"],
                "fixture_ids": k["fixture_ids"],
            }
        )
    return {
        "kernels_reviewed": kernels_reviewed,
        "all_classified_as_test_vector_fixture_helpers": True,
        "no_runtime_authority_expansion": True,
        "fixture_family_bindings": fixture_family_bindings,
        "review_status": "HELPER_KERNELS_VERIFIED_TEST_VECTOR_FIXTURE_HELPERS_ONLY",
    }


def build_no_metric_emission_review(receipt: dict[str, Any]) -> dict[str, Any]:
    al = receipt.get("authority_locks", {})
    if al.get("emits_metric_values") is not False:
        raise WassersteinCpuBaselineComputationCompleteReviewError(
            "source_emits_metric_values_not_false"
        )
    valid_ok = all(
        not r.get("metric_value_emitted")
        for r in receipt.get("valid_fixture_results", [])
    )
    invalid_ok = all(
        not r.get("metric_value_emitted")
        for r in receipt.get("invalid_fixture_results", [])
    )
    nc_ok = all(
        not r.get("metric_value_emitted")
        for r in receipt.get("not_computable_fixture_results", [])
    )
    if not (valid_ok and invalid_ok and nc_ok):
        raise WassersteinCpuBaselineComputationCompleteReviewError(
            "metric_value_emitted_true_in_fixture_results"
        )
    return {
        "source_emits_metric_values": False,
        "all_valid_metric_value_emitted_false": True,
        "all_invalid_metric_value_emitted_false": True,
        "all_nc_metric_value_emitted_false": True,
        "review_status": "NO_METRIC_VALUES_EMITTED_VERIFIED",
    }


def build_no_forecast_influence_review(receipt: dict[str, Any]) -> dict[str, Any]:
    al = receipt.get("authority_locks", {})
    if al.get("forecast_influence") is not False:
        raise WassersteinCpuBaselineComputationCompleteReviewError(
            "source_forecast_influence_not_false"
        )
    return {
        "source_forecast_influence": False,
        "no_forecast_binding": True,
        "no_p43_output": True,
        "review_status": "NO_FORECAST_INFLUENCE_VERIFIED",
    }


def build_no_p43_surface_lane_review(receipt: dict[str, Any]) -> dict[str, Any]:
    al = receipt.get("authority_locks", {})
    if al.get("p43_surface_lanes_authorized") is not False:
        raise WassersteinCpuBaselineComputationCompleteReviewError(
            "source_p43_surface_lanes_authorized_not_false"
        )
    return {
        "source_p43_surface_lanes_authorized": False,
        "no_p43_lanes_opened": True,
        "no_runtime_binding": True,
        "review_status": "NO_P43_SURFACE_LANES_VERIFIED",
    }


def build_authority_lock_review(receipt: dict[str, Any]) -> dict[str, Any]:
    al = receipt.get("authority_locks", {})
    checks = {
        "advisory_only": al.get("advisory_only") is True,
        "shadow_lane_only": al.get("shadow_lane_only") is True,
        "test_vector_computation_only": al.get("test_vector_computation_only") is True,
        "wasserstein_cpu_baseline_computation_authorized": al.get("wasserstein_cpu_baseline_computation_authorized") is True,
        "emits_metric_values_false": al.get("emits_metric_values") is False,
        "forecast_influence_false": al.get("forecast_influence") is False,
        "p43_surface_lanes_authorized_false": al.get("p43_surface_lanes_authorized") is False,
        "production_activation_false": al.get("production_activation") is False,
        "canon_promotion_false": al.get("canon_promotion") is False,
        "runtime_mutation_false": al.get("runtime_mutation") is False,
        "execution_authority_false": al.get("execution_authority") is False,
        "inference_authority_false": al.get("inference_authority") is False,
    }
    failed = [k for k, v in checks.items() if not v]
    if failed:
        raise WassersteinCpuBaselineComputationCompleteReviewError(
            f"authority_lock_check_failed: {failed}"
        )
    return {
        "source_advisory_only": True,
        "source_shadow_lane_only": True,
        "source_test_vector_computation_only": True,
        "source_wasserstein_cpu_baseline_computation_authorized": True,
        "source_emits_metric_values": False,
        "source_forecast_influence": False,
        "source_p43_surface_lanes_authorized": False,
        "source_production_activation": False,
        "source_canon_promotion": False,
        "source_runtime_mutation": False,
        "source_execution_authority": False,
        "source_inference_authority": False,
        "all_locks_intact": True,
        "review_status": "AUTHORITY_LOCKS_VERIFIED",
    }


def build_blocked_scope_review(receipt: dict[str, Any]) -> dict[str, Any]:
    bs = receipt.get("blocked_scopes", {})
    verified = []
    for scope, value in bs.items():
        if value is not False:
            raise WassersteinCpuBaselineComputationCompleteReviewError(
                f"blocked_scope_not_false:{scope}={value}"
            )
        verified.append({"scope": scope, "blocked": False, "review_status": "PASS"})
    return {
        "all_blocked_scopes_false": True,
        "blocked_scopes_verified": verified,
        "review_status": "BLOCKED_SCOPES_VERIFIED",
    }


def default_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "computation_complete_review_only": True,
        "test_vector_computation_only": True,
        "wasserstein_cpu_baseline_implementation_authorized": True,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def default_blocked_scopes() -> dict[str, bool]:
    return {
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def compute_wasserstein_cpu_baseline_computation_complete_review_hash(
    payload: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(payload))


def build_wasserstein_cpu_baseline_computation_complete_review(
    payload: dict[str, Any],
) -> dict[str, Any]:
    packet = {
        "schema_version": SCHEMA_VERSION,
        "review_id": payload["review_id"],
        "review_type": REVIEW_TYPE,
        "operator_id": OPERATOR_ID,
        "review_status": REVIEW_STATUS,
        "source_computation_receipt_hash": SOURCE_COMPUTATION_RECEIPT_HASH,
        "intended_lane": payload["intended_lane"],
        "review_stage": payload["review_stage"],
        "receipt_presence_review": payload["receipt_presence_review"],
        "source_receipt_hash_review": payload["source_receipt_hash_review"],
        "valid_fixture_result_review": payload["valid_fixture_result_review"],
        "invalid_fixture_rejection_review": payload["invalid_fixture_rejection_review"],
        "not_computable_fixture_rejection_review": payload["not_computable_fixture_rejection_review"],
        "comparison_summary_review": payload["comparison_summary_review"],
        "solver_policy_review": payload["solver_policy_review"],
        "helper_kernel_scope_review": payload["helper_kernel_scope_review"],
        "no_metric_emission_review": payload["no_metric_emission_review"],
        "no_forecast_influence_review": payload["no_forecast_influence_review"],
        "no_p43_surface_lane_review": payload["no_p43_surface_lane_review"],
        "authority_lock_review": payload["authority_lock_review"],
        "blocked_scope_review": payload["blocked_scope_review"],
        "blocked_scopes": payload["blocked_scopes"],
        "authority_locks": payload["authority_locks"],
        "recommended_next_step": payload["recommended_next_step"],
        "provenance": payload["provenance"],
        "created_at_utc": payload["created_at_utc"],
    }
    packet["canonical_hash"] = compute_wasserstein_cpu_baseline_computation_complete_review_hash(packet)
    return _finalize(packet)


def serialize_wasserstein_cpu_baseline_computation_complete_review(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(packet)
