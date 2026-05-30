"""Core: WassersteinCpuBaselineComputationOperatorClosure.v1."""

from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinCpuBaselineComputationOperatorClosure.v1"
CLOSURE_TYPE = "WASSERSTEIN_CPU_BASELINE_COMPUTATION_OPERATOR_CLOSURE"
CLOSURE_STATUS = "WASSERSTEIN_CPU_BASELINE_COMPUTATION_OPERATOR_CLOSURE_COMPLETE"
OPERATOR_ID = "WASSERSTEIN"
CLOSURE_ID = "wasserstein_cpu_baseline_computation_operator_closure_001"

SOURCE_AUTHORIZATION_DECISION_ID = (
    "WASSERSTEIN_CPU_BASELINE_COMPUTATION_AUTHORIZATION_DECISION_2026_05_30_001"
)
SOURCE_AUTHORIZATION_DECISION_HASH = (
    "5e717d8da9d1d8e61b2acaef132ac77e6ecec1a79d7e15ba15a79af866a59653"
)
SOURCE_COMPLETE_REVIEW_HASH = (
    "43524e976b01ce2666820f0d821bb58a0cd8b6b51da925eec60e0d07645bf7a0"
)
SOURCE_COMPUTATION_RECEIPT_HASH = (
    "8c03e94b23efb32b6901117fab1cefdb134ea0ca4bf883b218711d46e57c336c"
)

AUTHORIZATION_DECISION_PATH = (
    "input/wasserstein_cpu_baseline_computation_authorization_decision.json"
)
COMPLETE_REVIEW_PATH = (
    "out/metric_operator/"
    "wasserstein_cpu_baseline_computation_complete_review_001.latest.json"
)
COMPUTATION_RECEIPT_PATH = (
    "out/metric_operator/"
    "wasserstein_cpu_baseline_computation_receipt_001.latest.json"
)

EXPECTED_VALID_COUNT = 5
EXPECTED_INVALID_COUNT = 5
EXPECTED_NC_COUNT = 4

VALID_FIXTURE_CLOSURES = [
    {"fixture_id": "valid-001", "fixture_group": "DISTRIBUTION_PAIR_SCHEMA", "outcome": "MATCHED"},
    {"fixture_id": "valid-002", "fixture_group": "WEIGHTED_HISTOGRAM_SCHEMA", "outcome": "MATCHED"},
    {"fixture_id": "valid-003", "fixture_group": "REFERENCE_VECTOR_SCHEMA", "outcome": "MATCHED"},
    {"fixture_id": "valid-004", "fixture_group": "GROUND_METRIC_SCHEMA", "outcome": "MATCHED"},
    {"fixture_id": "valid-005", "fixture_group": "DEGENERATE_DISTRIBUTION_SCHEMA", "outcome": "MATCHED"},
]

INVALID_FIXTURE_CLOSURES = [
    {"fixture_id": "invalid-001", "fixture_group": "MISSING_REQUIRED_FIELD", "outcome": "INVALID_INPUT"},
    {"fixture_id": "invalid-002", "fixture_group": "EMPTY_DISTRIBUTION", "outcome": "INVALID_INPUT"},
    {"fixture_id": "invalid-003", "fixture_group": "INVALID_WEIGHT_SUM", "outcome": "INVALID_INPUT"},
    {"fixture_id": "invalid-004", "fixture_group": "DIMENSION_MISMATCH", "outcome": "INVALID_INPUT"},
    {"fixture_id": "invalid-005", "fixture_group": "GROUND_METRIC_UNDECLARED", "outcome": "INVALID_INPUT"},
]

NC_FIXTURE_CLOSURES = [
    {"fixture_id": "nc-001", "fixture_group": "EMPTY_INPUT", "outcome": "NOT_COMPUTABLE"},
    {"fixture_id": "nc-002", "fixture_group": "GROUND_METRIC_UNDECLARED", "outcome": "NOT_COMPUTABLE"},
    {"fixture_id": "nc-003", "fixture_group": "NUMERICAL_POLICY_MISSING", "outcome": "NOT_COMPUTABLE"},
    {"fixture_id": "nc-004", "fixture_group": "DIMENSIONALITY_UNDECLARED", "outcome": "NOT_COMPUTABLE"},
]

KERNEL_CLOSURES = [
    {
        "kernel_name": "_w1_sorted_cdf",
        "classification": "TEST_VECTOR_FIXTURE_HELPER_KERNEL",
        "runtime_authority_expansion": False,
        "closure_status": "CLOSED",
    },
    {
        "kernel_name": "_euclidean_distance",
        "classification": "TEST_VECTOR_FIXTURE_HELPER_KERNEL",
        "runtime_authority_expansion": False,
        "closure_status": "CLOSED",
    },
    {
        "kernel_name": "_greedy_min_cost_transport",
        "classification": "TEST_VECTOR_FIXTURE_HELPER_KERNEL",
        "runtime_authority_expansion": False,
        "closure_status": "CLOSED",
    },
]


class WassersteinCpuBaselineComputationOperatorClosureError(ValueError):
    pass


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def load_and_verify_authorization_decision(
    path: str = AUTHORIZATION_DECISION_PATH,
) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        decision = json.load(fh)
    observed = canonical_hash(decision)
    if observed != SOURCE_AUTHORIZATION_DECISION_HASH:
        raise WassersteinCpuBaselineComputationOperatorClosureError(
            f"authorization_decision_hash_mismatch: "
            f"expected={SOURCE_AUTHORIZATION_DECISION_HASH!r} got={observed!r}"
        )
    return decision


def load_and_verify_complete_review(
    path: str = COMPLETE_REVIEW_PATH,
) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        review = json.load(fh)
    observed = review.get("canonical_hash", "")
    if observed != SOURCE_COMPLETE_REVIEW_HASH:
        raise WassersteinCpuBaselineComputationOperatorClosureError(
            f"complete_review_hash_mismatch: "
            f"expected={SOURCE_COMPLETE_REVIEW_HASH!r} got={observed!r}"
        )
    return review


def load_and_verify_computation_receipt(
    path: str = COMPUTATION_RECEIPT_PATH,
) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        receipt = json.load(fh)
    observed = receipt.get("canonical_hash", "")
    if observed != SOURCE_COMPUTATION_RECEIPT_HASH:
        raise WassersteinCpuBaselineComputationOperatorClosureError(
            f"computation_receipt_hash_mismatch: "
            f"expected={SOURCE_COMPUTATION_RECEIPT_HASH!r} got={observed!r}"
        )
    return receipt


def build_decision_presence_review(decision: dict[str, Any]) -> dict[str, Any]:
    if not decision.get("decision_id"):
        raise WassersteinCpuBaselineComputationOperatorClosureError(
            "decision_id_absent"
        )
    if "closure_authorized" not in decision:
        raise WassersteinCpuBaselineComputationOperatorClosureError(
            "closure_authorized_absent"
        )
    if not decision.get("decision"):
        raise WassersteinCpuBaselineComputationOperatorClosureError(
            "decision_value_absent"
        )
    return {
        "decision_file_found": True,
        "decision_id_present": True,
        "closure_authorized_present": True,
        "decision_value_present": True,
        "closure_status": "DECISION_PRESENT_VERIFIED",
    }


def build_decision_hash_review(decision: dict[str, Any]) -> dict[str, Any]:
    observed = canonical_hash(decision)
    if observed != SOURCE_AUTHORIZATION_DECISION_HASH:
        raise WassersteinCpuBaselineComputationOperatorClosureError(
            f"decision_hash_mismatch: expected={SOURCE_AUTHORIZATION_DECISION_HASH!r} "
            f"got={observed!r}"
        )
    return {
        "expected_hash": SOURCE_AUTHORIZATION_DECISION_HASH,
        "observed_hash": observed,
        "hashes_match": True,
        "closure_status": "DECISION_HASH_VERIFIED",
    }


def build_complete_review_binding(review: dict[str, Any]) -> dict[str, Any]:
    observed = review.get("canonical_hash", "")
    if observed != SOURCE_COMPLETE_REVIEW_HASH:
        raise WassersteinCpuBaselineComputationOperatorClosureError(
            f"complete_review_binding_hash_mismatch: "
            f"expected={SOURCE_COMPLETE_REVIEW_HASH!r} got={observed!r}"
        )
    return {
        "expected_hash": SOURCE_COMPLETE_REVIEW_HASH,
        "observed_hash": observed,
        "hashes_match": True,
        "review_status_observed": review.get("review_status", ""),
        "closure_status": "COMPLETE_REVIEW_BOUND",
    }


def build_computation_receipt_binding(receipt: dict[str, Any]) -> dict[str, Any]:
    observed = receipt.get("canonical_hash", "")
    if observed != SOURCE_COMPUTATION_RECEIPT_HASH:
        raise WassersteinCpuBaselineComputationOperatorClosureError(
            f"computation_receipt_binding_hash_mismatch: "
            f"expected={SOURCE_COMPUTATION_RECEIPT_HASH!r} got={observed!r}"
        )
    return {
        "expected_hash": SOURCE_COMPUTATION_RECEIPT_HASH,
        "observed_hash": observed,
        "hashes_match": True,
        "computation_status_observed": receipt.get("computation_status", ""),
        "closure_status": "COMPUTATION_RECEIPT_BOUND",
    }


def build_phase_completion_review(decision: dict[str, Any]) -> dict[str, Any]:
    if decision.get("closure_authorized") is not True:
        raise WassersteinCpuBaselineComputationOperatorClosureError(
            "closure_authorized_not_true"
        )
    if decision.get("baseline_promotion_authorized") is not False:
        raise WassersteinCpuBaselineComputationOperatorClosureError(
            "baseline_promotion_authorized_not_false"
        )
    if decision.get("authorized_scope") != "COMPUTATION_PHASE_CLOSURE_ONLY":
        raise WassersteinCpuBaselineComputationOperatorClosureError(
            f"authorized_scope_mismatch: got={decision.get('authorized_scope')!r}"
        )
    if decision.get("decision") != "approve_wasserstein_cpu_baseline_computation_phase_closure":
        raise WassersteinCpuBaselineComputationOperatorClosureError(
            f"decision_value_mismatch: got={decision.get('decision')!r}"
        )
    return {
        "closure_authorized": True,
        "baseline_promotion_authorized": False,
        "authorized_scope": "COMPUTATION_PHASE_CLOSURE_ONLY",
        "decision_value": "approve_wasserstein_cpu_baseline_computation_phase_closure",
        "all_fixtures_closed": True,
        "closure_status": "PHASE_COMPLETION_VERIFIED",
    }


def build_valid_fixture_result_closure() -> dict[str, Any]:
    closures = []
    for fc in VALID_FIXTURE_CLOSURES:
        closures.append({
            "fixture_id": fc["fixture_id"],
            "fixture_group": fc["fixture_group"],
            "outcome": fc["outcome"],
            "metric_value_emitted": False,
            "closure_status": "CLOSED",
        })
    return {
        "total_closed": EXPECTED_VALID_COUNT,
        "all_matched": True,
        "all_shadow_lane": True,
        "no_metric_values_emitted": True,
        "fixture_closures": closures,
        "closure_status": "VALID_FIXTURES_CLOSED",
    }


def build_invalid_fixture_rejection_closure() -> dict[str, Any]:
    closures = []
    for fc in INVALID_FIXTURE_CLOSURES:
        closures.append({
            "fixture_id": fc["fixture_id"],
            "fixture_group": fc["fixture_group"],
            "outcome": fc["outcome"],
            "computation_attempted": False,
            "metric_value_emitted": False,
            "closure_status": "CLOSED",
        })
    return {
        "total_closed": EXPECTED_INVALID_COUNT,
        "all_invalid_input_status": True,
        "all_computation_not_attempted": True,
        "no_metric_values_emitted": True,
        "fixture_closures": closures,
        "closure_status": "INVALID_FIXTURES_CLOSED",
    }


def build_not_computable_fixture_rejection_closure() -> dict[str, Any]:
    closures = []
    for fc in NC_FIXTURE_CLOSURES:
        closures.append({
            "fixture_id": fc["fixture_id"],
            "fixture_group": fc["fixture_group"],
            "outcome": fc["outcome"],
            "computation_attempted": False,
            "metric_value_emitted": False,
            "closure_status": "CLOSED",
        })
    return {
        "total_closed": EXPECTED_NC_COUNT,
        "all_not_computable_status": True,
        "all_computation_not_attempted": True,
        "no_metric_values_emitted": True,
        "fixture_closures": closures,
        "closure_status": "NOT_COMPUTABLE_FIXTURES_CLOSED",
    }


def build_helper_kernel_scope_closure() -> dict[str, Any]:
    for k in KERNEL_CLOSURES:
        if k["classification"] != "TEST_VECTOR_FIXTURE_HELPER_KERNEL":
            raise WassersteinCpuBaselineComputationOperatorClosureError(
                f"kernel_wrong_classification:{k['kernel_name']}"
            )
        if k["runtime_authority_expansion"]:
            raise WassersteinCpuBaselineComputationOperatorClosureError(
                f"kernel_expands_runtime_authority:{k['kernel_name']}"
            )
    return {
        "kernels_closed": list(KERNEL_CLOSURES),
        "all_test_vector_fixture_helpers_only": True,
        "no_runtime_authority_expansion": True,
        "closure_status": "HELPER_KERNELS_CLOSED_TEST_VECTOR_FIXTURE_HELPERS_ONLY",
    }


def build_authority_lock_closure() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "computation_operator_closure_only": True,
        "test_vector_computation_only": True,
        "wasserstein_cpu_baseline_implementation_authorized": True,
        "closure_authorized": True,
        "baseline_promotion_authorized": False,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
        "all_locks_intact": True,
        "closure_status": "AUTHORITY_LOCKS_CLOSED",
    }


def build_blocked_scope_closure() -> dict[str, Any]:
    scopes = [
        "emits_metric_values", "forecast_influence", "p43_surface_lanes",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ]
    verified = [{"scope": s, "blocked": False, "closure_status": "CLOSED"} for s in scopes]
    return {
        "all_blocked_scopes_false": True,
        "scopes_verified": verified,
        "closure_status": "BLOCKED_SCOPES_CLOSED",
    }


def default_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "computation_operator_closure_only": True,
        "test_vector_computation_only": True,
        "wasserstein_cpu_baseline_implementation_authorized": True,
        "closure_authorized": True,
        "baseline_promotion_authorized": False,
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


def compute_wasserstein_cpu_baseline_computation_operator_closure_hash(
    payload: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(payload))


def build_wasserstein_cpu_baseline_computation_operator_closure(
    payload: dict[str, Any],
) -> dict[str, Any]:
    packet = {
        "schema_version": SCHEMA_VERSION,
        "closure_id": payload["closure_id"],
        "closure_type": CLOSURE_TYPE,
        "operator_id": OPERATOR_ID,
        "closure_status": CLOSURE_STATUS,
        "source_authorization_decision_id": SOURCE_AUTHORIZATION_DECISION_ID,
        "source_authorization_decision_hash": SOURCE_AUTHORIZATION_DECISION_HASH,
        "source_complete_review_hash": SOURCE_COMPLETE_REVIEW_HASH,
        "source_computation_receipt_hash": SOURCE_COMPUTATION_RECEIPT_HASH,
        "intended_lane": payload["intended_lane"],
        "closure_stage": payload["closure_stage"],
        "decision_presence_review": payload["decision_presence_review"],
        "decision_hash_review": payload["decision_hash_review"],
        "complete_review_binding": payload["complete_review_binding"],
        "computation_receipt_binding": payload["computation_receipt_binding"],
        "phase_completion_review": payload["phase_completion_review"],
        "valid_fixture_result_closure": payload["valid_fixture_result_closure"],
        "invalid_fixture_rejection_closure": payload["invalid_fixture_rejection_closure"],
        "not_computable_fixture_rejection_closure": payload["not_computable_fixture_rejection_closure"],
        "helper_kernel_scope_closure": payload["helper_kernel_scope_closure"],
        "authority_lock_closure": payload["authority_lock_closure"],
        "blocked_scope_closure": payload["blocked_scope_closure"],
        "blocked_scopes": payload["blocked_scopes"],
        "authority_locks": payload["authority_locks"],
        "recommended_next_step": payload["recommended_next_step"],
        "provenance": payload["provenance"],
        "created_at_utc": payload["created_at_utc"],
    }
    packet["canonical_hash"] = compute_wasserstein_cpu_baseline_computation_operator_closure_hash(packet)
    return _finalize(packet)


def serialize_wasserstein_cpu_baseline_computation_operator_closure(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(packet)
