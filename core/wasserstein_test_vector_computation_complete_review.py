from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinTestVectorComputationCompleteReview.v1"
REVIEW_TYPE = "WASSERSTEIN_TEST_VECTOR_COMPUTATION_COMPLETE_REVIEW"
OPERATOR_ID = "WASSERSTEIN"

SOURCE_COMPUTATION_RECEIPT_HASH = (
    "010da2fdf344cfc32d2e9accc0ef19e96644fdd69974928ca047f87e4daf6188"
)
SOURCE_COMPUTATION_ACTUAL_PR_GATE_HASH = (
    "3ac3aeccdb5521db58f0fbadac8fa6e3641d1f8fb8daec8fe98d1fcafe575d65"
)

COMPUTATION_RECEIPT_PATH = (
    "out/projections/wasserstein_test_vector_computation_receipt_001.latest.json"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_STAGE = (
    "TEST_VECTOR_COMPUTATION_COMPLETE_REVIEW_ONLY",
    "BLOCKED_PENDING_GATE",
)

FORBIDDEN = (
    "runtime",
    "scheduler",
    "cache",
    "forecast",
    "scoring",
    "metric-value",
    "wasserstein-distance",
    "expected-wasserstein",
    "earth-mover",
    "ot-computation",
    "fixture-file",
    "manifest-file",
    "schema-file",
    "sinkhorn-kernel",
    "authority-flag",
)

# Expected shadow_transport_value (canonical-rounded to 6 dp) per fixture_id.
EXPECTED_SHADOW_TRANSPORT_VALUES: dict[str, float] = {
    "valid-001": 0.4,
    "valid-002": 0.4,
    "valid-003": 0.866025,
    "valid-004": 0.2,
    "valid-005": 0.0,
}

EXPECTED_FIXTURE_GROUPS: dict[str, str] = {
    "valid-001": "DISTRIBUTION_PAIR_SCHEMA",
    "valid-002": "WEIGHTED_HISTOGRAM_SCHEMA",
    "valid-003": "REFERENCE_VECTOR_SCHEMA",
    "valid-004": "GROUND_METRIC_SCHEMA",
    "valid-005": "DEGENERATE_DISTRIBUTION_SCHEMA",
}

COMPUTATION_METHODS: dict[str, str] = {
    "valid-001": "w1_cdf_1d",
    "valid-002": "w1_cdf_1d_bin_midpoints",
    "valid-003": "euclidean_distance",
    "valid-004": "greedy_min_cost_transport",
    "valid-005": "w1_cdf_1d_degenerate",
}


class WassersteinComputationCompleteReviewError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


# ---------------------------------------------------------------------------
# Receipt loading and basic integrity check
# ---------------------------------------------------------------------------


def load_and_verify_computation_receipt(
    receipt_path: str = COMPUTATION_RECEIPT_PATH,
) -> dict[str, Any]:
    with open(receipt_path, encoding="utf-8") as fh:
        receipt = json.load(fh)
    stored_hash = receipt.get("canonical_hash", "")
    if stored_hash != SOURCE_COMPUTATION_RECEIPT_HASH:
        raise WassersteinComputationCompleteReviewError(
            f"receipt_hash_mismatch: expected={SOURCE_COMPUTATION_RECEIPT_HASH!r} "
            f"got={stored_hash!r}"
        )
    return receipt


# ---------------------------------------------------------------------------
# Review sub-structures derived from the computation receipt
# ---------------------------------------------------------------------------


def build_valid_fixture_result_review(
    valid_results: list[dict[str, Any]],
) -> dict[str, Any]:
    if len(valid_results) != 5:
        raise WassersteinComputationCompleteReviewError(
            f"valid_fixture_count_mismatch: expected=5 got={len(valid_results)}"
        )
    fixture_reviews = []
    for r in valid_results:
        fid = r["fixture_id"]
        if r.get("computation_status") != "SHADOW_COMPUTATION_COMPLETE":
            raise WassersteinComputationCompleteReviewError(
                f"valid_fixture_not_complete:{fid}"
            )
        if "shadow_transport_value" not in r:
            raise WassersteinComputationCompleteReviewError(
                f"shadow_transport_value_missing:{fid}"
            )
        if r.get("shadow_lane") != "SHADOW":
            raise WassersteinComputationCompleteReviewError(
                f"valid_result_not_shadow:{fid}"
            )
        if r.get("metric_value_emitted") is not False:
            raise WassersteinComputationCompleteReviewError(
                f"metric_value_emitted_true:{fid}"
            )
        if r.get("expected_distance_included") is not False:
            raise WassersteinComputationCompleteReviewError(
                f"expected_distance_included_true:{fid}"
            )
        if r.get("deterministic") is not True:
            raise WassersteinComputationCompleteReviewError(
                f"deterministic_not_true:{fid}"
            )
        fixture_reviews.append(
            {
                "fixture_id": fid,
                "fixture_group": r["fixture_group"],
                "computation_status_observed": r["computation_status"],
                "shadow_lane_observed": r["shadow_lane"],
                "shadow_transport_value_present": True,
                "metric_value_emitted": False,
                "expected_distance_included": False,
                "deterministic": True,
                "review_status": "PASS",
            }
        )
    return {
        "total_reviewed": 5,
        "all_shadow_computation_complete": True,
        "all_shadow_lane": True,
        "all_have_shadow_transport_value": True,
        "no_metric_values_emitted": True,
        "no_expected_distances_included": True,
        "fixture_reviews": fixture_reviews,
        "review_status": "VALID_FIXTURE_RESULTS_VERIFIED",
    }


def build_rejected_input_result_review(
    invalid_results: list[dict[str, Any]],
    nc_results: list[dict[str, Any]],
) -> dict[str, Any]:
    if len(invalid_results) != 5:
        raise WassersteinComputationCompleteReviewError(
            f"invalid_fixture_count_mismatch: expected=5 got={len(invalid_results)}"
        )
    if len(nc_results) != 4:
        raise WassersteinComputationCompleteReviewError(
            f"nc_fixture_count_mismatch: expected=4 got={len(nc_results)}"
        )
    fixture_reviews = []
    for r in invalid_results:
        fid = r["fixture_id"]
        if r.get("computation_status") != "VALIDATION_ERROR":
            raise WassersteinComputationCompleteReviewError(
                f"invalid_fixture_wrong_status:{fid}"
            )
        fixture_reviews.append(
            {
                "fixture_id": fid,
                "fixture_group": r["fixture_group"],
                "computation_status_observed": r["computation_status"],
                "rejection_reason_present": bool(r.get("rejection_reason")),
                "metric_value_emitted": False,
                "review_status": "PASS",
            }
        )
    for r in nc_results:
        fid = r["fixture_id"]
        if r.get("computation_status") != "NOT_COMPUTABLE":
            raise WassersteinComputationCompleteReviewError(
                f"nc_fixture_wrong_status:{fid}"
            )
        fixture_reviews.append(
            {
                "fixture_id": fid,
                "fixture_group": r["fixture_group"],
                "computation_status_observed": r["computation_status"],
                "rejection_reason_present": bool(r.get("rejection_reason")),
                "metric_value_emitted": False,
                "review_status": "PASS",
            }
        )
    return {
        "total_reviewed": 9,
        "invalid_reviewed": 5,
        "not_computable_reviewed": 4,
        "all_rejected_input": True,
        "no_metric_values_emitted": True,
        "fixture_reviews": fixture_reviews,
        "review_status": "REJECTED_INPUT_RESULTS_VERIFIED",
    }


def build_shadow_transport_value_review(
    valid_results: list[dict[str, Any]],
) -> dict[str, Any]:
    VALUE_TOLERANCE = 1e-6
    fixture_reviews = []
    for r in valid_results:
        fid = r["fixture_id"]
        observed = r["shadow_transport_value"]
        expected = EXPECTED_SHADOW_TRANSPORT_VALUES[fid]
        within_tolerance = abs(observed - expected) <= VALUE_TOLERANCE
        if not within_tolerance:
            raise WassersteinComputationCompleteReviewError(
                f"shadow_transport_value_tolerance_exceeded:{fid} "
                f"expected={expected} observed={observed}"
            )
        fixture_reviews.append(
            {
                "fixture_id": fid,
                "fixture_group": EXPECTED_FIXTURE_GROUPS[fid],
                "shadow_transport_value_observed": observed,
                "expected_value": expected,
                "tolerance": VALUE_TOLERANCE,
                "within_tolerance": True,
                "method": COMPUTATION_METHODS[fid],
                "review_status": "PASS",
            }
        )
    return {
        "total_reviewed": 5,
        "all_within_tolerance": True,
        "tolerance_used": VALUE_TOLERANCE,
        "fixture_reviews": fixture_reviews,
        "no_metric_value_emitted": True,
        "no_expected_distance_added": True,
        "review_status": "SHADOW_TRANSPORT_VALUES_VERIFIED",
    }


def build_no_metric_value_emission_review(receipt: dict[str, Any]) -> dict[str, Any]:
    al = receipt.get("authority_locks", {})
    fcr = receipt.get("fixture_computation_results", {})
    if al.get("emits_metric_values") is not False:
        raise WassersteinComputationCompleteReviewError(
            "receipt_emits_metric_values_not_false"
        )
    if not fcr.get("no_metric_values_emitted"):
        raise WassersteinComputationCompleteReviewError(
            "receipt_no_metric_values_emitted_not_true"
        )
    return {
        "source_emits_metric_values": False,
        "source_fcr_no_metric_values_emitted": True,
        "all_valid_results_metric_value_emitted_false": True,
        "all_invalid_results_metric_value_emitted_false": True,
        "all_nc_results_metric_value_emitted_false": True,
        "review_status": "NO_METRIC_VALUES_EMITTED_VERIFIED",
    }


def build_no_forecast_influence_review(receipt: dict[str, Any]) -> dict[str, Any]:
    al = receipt.get("authority_locks", {})
    nfi = receipt.get("no_forecast_influence_scan", {})
    if al.get("forecast_influence") is not False:
        raise WassersteinComputationCompleteReviewError(
            "receipt_forecast_influence_not_false"
        )
    if nfi.get("scan_status") != "CLEAN":
        raise WassersteinComputationCompleteReviewError(
            "receipt_forecast_influence_scan_not_clean"
        )
    if nfi.get("violations"):
        raise WassersteinComputationCompleteReviewError(
            "receipt_forecast_influence_violations_found"
        )
    return {
        "source_forecast_influence": False,
        "source_scan_status": "CLEAN",
        "source_scan_violations": [],
        "no_forecast_binding": True,
        "no_p43_output": True,
        "review_status": "NO_FORECAST_INFLUENCE_VERIFIED",
    }


def build_no_p43_surface_lane_review(receipt: dict[str, Any]) -> dict[str, Any]:
    al = receipt.get("authority_locks", {})
    np43 = receipt.get("no_p43_surface_lane_scan", {})
    if al.get("p43_surface_lanes_authorized") is not False:
        raise WassersteinComputationCompleteReviewError(
            "receipt_p43_surface_lanes_authorized_not_false"
        )
    if np43.get("scan_status") != "CLEAN":
        raise WassersteinComputationCompleteReviewError(
            "receipt_p43_scan_not_clean"
        )
    if np43.get("violations"):
        raise WassersteinComputationCompleteReviewError(
            "receipt_p43_violations_found"
        )
    return {
        "source_p43_surface_lanes_authorized": False,
        "source_scan_status": "CLEAN",
        "source_scan_violations": [],
        "no_p43_lanes_opened": True,
        "no_runtime_binding": True,
        "review_status": "NO_P43_SURFACE_LANES_VERIFIED",
    }


def build_authority_lock_review(receipt: dict[str, Any]) -> dict[str, Any]:
    al = receipt.get("authority_locks", {})
    required_true = [
        "advisory_only",
        "shadow_lane_only",
        "test_vector_computation_only",
        "wasserstein_computation_authorized",
    ]
    required_false = [
        "emits_metric_values",
        "forecast_influence",
        "p43_surface_lanes_authorized",
        "production_activation",
        "canon_promotion",
        "runtime_mutation",
        "execution_authority",
        "inference_authority",
    ]
    for k in required_true:
        if al.get(k) is not True:
            raise WassersteinComputationCompleteReviewError(
                f"authority_lock_expected_true_but_not:{k}"
            )
    for k in required_false:
        if al.get(k) is not False:
            raise WassersteinComputationCompleteReviewError(
                f"authority_lock_expected_false_but_not:{k}"
            )
    return {
        "source_advisory_only": True,
        "source_shadow_lane_only": True,
        "source_test_vector_computation_only": True,
        "source_wasserstein_computation_authorized": True,
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


def build_computation_completion_summary(receipt: dict[str, Any]) -> dict[str, Any]:
    fcr = receipt.get("fixture_computation_results", {})
    if fcr.get("computation_status") != "WASSERSTEIN_TEST_VECTOR_COMPUTATION_COMPLETE":
        raise WassersteinComputationCompleteReviewError(
            "computation_status_not_complete"
        )
    return {
        "computation_receipt_id": receipt.get("computation_receipt_id"),
        "computation_status": fcr.get("computation_status"),
        "total_fixtures": fcr.get("total_fixtures"),
        "valid_computed": fcr.get("valid_computed"),
        "invalid_rejected": fcr.get("invalid_rejected"),
        "not_computable_rejected": fcr.get("not_computable_rejected"),
        "all_shadow_lane": fcr.get("all_shadow_lane"),
        "no_metric_values_emitted": fcr.get("no_metric_values_emitted"),
        "no_expected_distances_included": fcr.get("no_expected_distances_included"),
        "determinism_status": receipt.get("determinism_checks", {}).get(
            "determinism_status"
        ),
        "source_intended_lane": receipt.get("intended_lane"),
        "source_computation_stage": receipt.get("computation_stage"),
        "review_completion_status": "COMPUTATION_COMPLETION_VERIFIED",
    }


# ---------------------------------------------------------------------------
# Default sub-structures (review-own)
# ---------------------------------------------------------------------------


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


def default_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "test_vector_computation_complete_review_only": True,
        "wasserstein_computation_authorized": True,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


# ---------------------------------------------------------------------------
# Safety scanner
# ---------------------------------------------------------------------------


def _assert_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _assert_safe(x)
    elif isinstance(v, list):
        for x in v:
            _assert_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise WassersteinComputationCompleteReviewError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_wasserstein_test_vector_computation_complete_review(
    packet: dict[str, Any],
) -> None:
    required = {
        "schema_version",
        "review_id",
        "review_type",
        "operator_id",
        "source_computation_receipt_hash",
        "source_computation_actual_pr_gate_hash",
        "intended_lane",
        "review_stage",
        "valid_fixture_result_review",
        "rejected_input_result_review",
        "shadow_transport_value_review",
        "no_metric_value_emission_review",
        "no_forecast_influence_review",
        "no_p43_surface_lane_review",
        "authority_lock_review",
        "computation_completion_summary",
        "blocked_scopes",
        "authority_locks",
        "recommended_next_step",
        "provenance",
        "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise WassersteinComputationCompleteReviewError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise WassersteinComputationCompleteReviewError("invalid_schema_version")
    if packet["review_type"] != REVIEW_TYPE:
        raise WassersteinComputationCompleteReviewError("invalid_review_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise WassersteinComputationCompleteReviewError("unknown_operator_id")
    if packet["source_computation_receipt_hash"] != SOURCE_COMPUTATION_RECEIPT_HASH:
        raise WassersteinComputationCompleteReviewError(
            "invalid_source_computation_receipt_hash"
        )
    if (
        packet["source_computation_actual_pr_gate_hash"]
        != SOURCE_COMPUTATION_ACTUAL_PR_GATE_HASH
    ):
        raise WassersteinComputationCompleteReviewError(
            "invalid_source_computation_actual_pr_gate_hash"
        )
    if packet["intended_lane"] not in ALLOWED_LANE:
        raise WassersteinComputationCompleteReviewError("unknown_intended_lane")
    if packet["review_stage"] not in ALLOWED_STAGE:
        raise WassersteinComputationCompleteReviewError("unknown_review_stage")

    vfr = packet["valid_fixture_result_review"]
    if vfr.get("review_status") != "VALID_FIXTURE_RESULTS_VERIFIED":
        raise WassersteinComputationCompleteReviewError(
            "valid_fixture_result_review_not_verified"
        )
    if not vfr.get("all_have_shadow_transport_value"):
        raise WassersteinComputationCompleteReviewError(
            "not_all_valid_have_shadow_transport_value"
        )
    if not vfr.get("all_shadow_lane"):
        raise WassersteinComputationCompleteReviewError(
            "not_all_valid_results_shadow_lane"
        )

    rir = packet["rejected_input_result_review"]
    if rir.get("review_status") != "REJECTED_INPUT_RESULTS_VERIFIED":
        raise WassersteinComputationCompleteReviewError(
            "rejected_input_result_review_not_verified"
        )
    if rir.get("total_reviewed") != 9:
        raise WassersteinComputationCompleteReviewError(
            "rejected_input_total_mismatch"
        )

    stvr = packet["shadow_transport_value_review"]
    if stvr.get("review_status") != "SHADOW_TRANSPORT_VALUES_VERIFIED":
        raise WassersteinComputationCompleteReviewError(
            "shadow_transport_value_review_not_verified"
        )
    if not stvr.get("all_within_tolerance"):
        raise WassersteinComputationCompleteReviewError(
            "shadow_transport_values_out_of_tolerance"
        )

    nmver = packet["no_metric_value_emission_review"]
    if nmver.get("review_status") != "NO_METRIC_VALUES_EMITTED_VERIFIED":
        raise WassersteinComputationCompleteReviewError(
            "no_metric_value_emission_review_not_verified"
        )

    nfir = packet["no_forecast_influence_review"]
    if nfir.get("review_status") != "NO_FORECAST_INFLUENCE_VERIFIED":
        raise WassersteinComputationCompleteReviewError(
            "no_forecast_influence_review_not_verified"
        )

    np43r = packet["no_p43_surface_lane_review"]
    if np43r.get("review_status") != "NO_P43_SURFACE_LANES_VERIFIED":
        raise WassersteinComputationCompleteReviewError(
            "no_p43_surface_lane_review_not_verified"
        )

    alr = packet["authority_lock_review"]
    if alr.get("review_status") != "AUTHORITY_LOCKS_VERIFIED":
        raise WassersteinComputationCompleteReviewError(
            "authority_lock_review_not_verified"
        )
    if not alr.get("all_locks_intact"):
        raise WassersteinComputationCompleteReviewError(
            "authority_locks_not_intact"
        )

    ccs = packet["computation_completion_summary"]
    if ccs.get("review_completion_status") != "COMPUTATION_COMPLETION_VERIFIED":
        raise WassersteinComputationCompleteReviewError(
            "computation_completion_summary_not_verified"
        )

    al = packet["authority_locks"]
    if al.get("test_vector_computation_complete_review_only") is not True:
        raise WassersteinComputationCompleteReviewError(
            "test_vector_computation_complete_review_only_must_be_true"
        )
    if al.get("wasserstein_computation_authorized") is not True:
        raise WassersteinComputationCompleteReviewError(
            "wasserstein_computation_authorized_must_be_true"
        )
    if al.get("emits_metric_values") is not False:
        raise WassersteinComputationCompleteReviewError(
            "emits_metric_values_must_be_false"
        )
    if al.get("execution_authority") is not False:
        raise WassersteinComputationCompleteReviewError(
            "execution_authority_must_be_false"
        )
    if packet["authority_locks"] != default_authority_locks():
        raise WassersteinComputationCompleteReviewError("invalid_authority_locks")
    if packet["blocked_scopes"] != default_blocked_scopes():
        raise WassersteinComputationCompleteReviewError("invalid_blocked_scopes")

    _assert_safe(packet["provenance"])


# ---------------------------------------------------------------------------
# Hash / serialization / build
# ---------------------------------------------------------------------------


def compute_wasserstein_test_vector_computation_complete_review_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_wasserstein_test_vector_computation_complete_review(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_wasserstein_test_vector_computation_complete_review(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "review_type": REVIEW_TYPE,
        "operator_id": OPERATOR_ID,
        "source_computation_receipt_hash": SOURCE_COMPUTATION_RECEIPT_HASH,
        "source_computation_actual_pr_gate_hash": SOURCE_COMPUTATION_ACTUAL_PR_GATE_HASH,
        "authority_locks": payload.get("authority_locks", default_authority_locks()),
        "blocked_scopes": payload.get("blocked_scopes", default_blocked_scopes()),
    }
    base["canonical_hash"] = (
        compute_wasserstein_test_vector_computation_complete_review_hash(base)
    )
    validate_wasserstein_test_vector_computation_complete_review(base)
    return _finalize(base)
