from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinTestVectorFixturePlan.v1"
FIXTURE_PLAN_TYPE = "WASSERSTEIN_TEST_VECTOR_FIXTURE_PLAN"
OPERATOR_ID = "WASSERSTEIN"
SOURCE_SCHEMA_PLAN_HASH = (
    "77e06b11f427973e478076464db2055c1baae555f88f7d32be5cfb7b877088b3"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_FIXTURE_STAGE = ("FIXTURE_PLAN_ONLY", "BLOCKED_PENDING_OPERATOR_REVIEW")
ALLOWED_IMPL_STATUS = ("PLANNED_ONLY", "NOT_IMPLEMENTED", "BLOCKED_PENDING_REVIEW")

VALID_GROUP_IDS = ("valid-001", "valid-002", "valid-003", "valid-004", "valid-005")
INVALID_GROUP_IDS = (
    "invalid-001",
    "invalid-002",
    "invalid-003",
    "invalid-004",
    "invalid-005",
)
NC_GROUP_IDS = ("nc-001", "nc-002", "nc-003", "nc-004")

ALLOWED_VALID_SCHEMA_TYPE = (
    "DISTRIBUTION_PAIR_SCHEMA",
    "WEIGHTED_HISTOGRAM_SCHEMA",
    "REFERENCE_VECTOR_SCHEMA",
    "GROUND_METRIC_SCHEMA",
    "DEGENERATE_DISTRIBUTION_SCHEMA",
)
ALLOWED_INVALID_REASON = (
    "MISSING_REQUIRED_FIELD",
    "EMPTY_DISTRIBUTION",
    "INVALID_WEIGHT_SUM",
    "DIMENSION_MISMATCH",
    "GROUND_METRIC_UNDECLARED",
)
ALLOWED_NC_REASON = (
    "EMPTY_INPUT",
    "GROUND_METRIC_UNDECLARED",
    "NUMERICAL_POLICY_MISSING",
    "DIMENSIONALITY_UNDECLARED",
)
ALLOWED_NC_STATE = ("NOT_COMPUTABLE", "REJECTED_INPUT", "VALIDATION_ERROR")

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
)


class WassersteinTestVectorFixturePlanValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


# ---------------------------------------------------------------------------
# Default sub-structures
# ---------------------------------------------------------------------------


def default_valid_fixture_plan() -> list[dict[str, Any]]:
    return [
        {
            "fixture_plan_id": "valid-001",
            "schema_group_id": "valid-001",
            "schema_type": "DISTRIBUTION_PAIR_SCHEMA",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "description": (
                "Plan-only fixture for standard discrete distribution pair: two "
                "finite distributions over a shared support, non-negative weights "
                "summing to 1. No Wasserstein values declared."
            ),
            "planned_inputs": {
                "distribution_a": "N-element weight vector + N-element support vector",
                "distribution_b": "M-element weight vector + M-element support vector",
                "ground_metric": "EUCLIDEAN_DECLARED",
            },
            "blocked_outputs": [
                "expected_wasserstein_distances",
                "metric_values",
            ],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_plan_id": "valid-002",
            "schema_group_id": "valid-002",
            "schema_type": "WEIGHTED_HISTOGRAM_SCHEMA",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "description": (
                "Plan-only fixture for parallel weights-and-support-arrays layout; "
                "weights normalised to sum to 1 before schema registration. "
                "No Wasserstein values declared."
            ),
            "planned_inputs": {
                "weights_a": "N-element normalised weight array",
                "support_a": "N-element support point array",
                "weights_b": "N-element normalised weight array",
                "support_b": "N-element support point array",
            },
            "blocked_outputs": [
                "expected_wasserstein_distances",
                "metric_values",
            ],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_plan_id": "valid-003",
            "schema_group_id": "valid-003",
            "schema_type": "REFERENCE_VECTOR_SCHEMA",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "description": (
                "Plan-only fixture for 1D reference vectors with known analytic "
                "Wasserstein-1 result; intended for deterministic replay and "
                "regression validation once fixture creation is authorised."
            ),
            "planned_inputs": {
                "distribution_a": "1D sorted support + uniform weights",
                "distribution_b": "1D sorted support + uniform weights",
                "ground_metric": "EUCLIDEAN_DECLARED",
            },
            "blocked_outputs": [
                "expected_wasserstein_distances",
                "metric_values",
            ],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_plan_id": "valid-004",
            "schema_group_id": "valid-004",
            "schema_type": "GROUND_METRIC_SCHEMA",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "description": (
                "Plan-only fixture for Euclidean cost matrix specification for 2D "
                "discrete OT inputs; ground metric must be frozen before fixture "
                "creation. No Wasserstein values declared."
            ),
            "planned_inputs": {
                "distribution_a": "2D support points + weights",
                "distribution_b": "2D support points + weights",
                "ground_metric": "EUCLIDEAN_DECLARED",
                "cost_matrix": "N x M pairwise Euclidean cost (planned, not computed)",
            },
            "blocked_outputs": [
                "expected_wasserstein_distances",
                "metric_values",
                "cost_matrix_values",
            ],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_plan_id": "valid-005",
            "schema_group_id": "valid-005",
            "schema_type": "DEGENERATE_DISTRIBUTION_SCHEMA",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "description": (
                "Plan-only fixture for near-degenerate distributions: single "
                "non-zero weight entry or all mass at one support point; valid "
                "schema but edge-case input. No Wasserstein values declared."
            ),
            "planned_inputs": {
                "distribution_a": "1-element weight vector + 1-element support vector",
                "distribution_b": "1-element weight vector + 1-element support vector",
                "ground_metric": "EUCLIDEAN_DECLARED",
            },
            "blocked_outputs": [
                "expected_wasserstein_distances",
                "metric_values",
            ],
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_invalid_fixture_plan() -> list[dict[str, Any]]:
    return [
        {
            "fixture_plan_id": "invalid-001",
            "schema_group_id": "invalid-001",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "target_field": "distribution_a",
            "expected_failure": "validation_error_missing_distribution_a",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "description": (
                "Plan-only invalid fixture: distribution_a field absent from "
                "input; schema contract violated at the required-field level."
            ),
            "blocked_outputs": [
                "expected_wasserstein_distances",
                "metric_values",
            ],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_plan_id": "invalid-002",
            "schema_group_id": "invalid-002",
            "invalid_reason": "EMPTY_DISTRIBUTION",
            "target_field": "distribution_a_weights",
            "expected_failure": "validation_error_empty_distribution",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "description": (
                "Plan-only invalid fixture: distribution_a_weights array is "
                "zero-length; empty distribution violates schema contract."
            ),
            "blocked_outputs": [
                "expected_wasserstein_distances",
                "metric_values",
            ],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_plan_id": "invalid-003",
            "schema_group_id": "invalid-003",
            "invalid_reason": "INVALID_WEIGHT_SUM",
            "target_field": "distribution_b_weights",
            "expected_failure": "validation_error_weights_do_not_sum_to_one",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "description": (
                "Plan-only invalid fixture: distribution_b weights do not sum "
                "to 1 within tolerance; normalisation contract violated."
            ),
            "blocked_outputs": [
                "expected_wasserstein_distances",
                "metric_values",
            ],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_plan_id": "invalid-004",
            "schema_group_id": "invalid-004",
            "invalid_reason": "DIMENSION_MISMATCH",
            "target_field": "distribution_support",
            "expected_failure": "validation_error_support_dimension_mismatch",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "description": (
                "Plan-only invalid fixture: distribution_a support is 1D and "
                "distribution_b support is 2D; dimensionality mismatch violates "
                "schema contract."
            ),
            "blocked_outputs": [
                "expected_wasserstein_distances",
                "metric_values",
            ],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_plan_id": "invalid-005",
            "schema_group_id": "invalid-005",
            "invalid_reason": "GROUND_METRIC_UNDECLARED",
            "target_field": "ground_metric",
            "expected_failure": "validation_error_ground_metric_not_declared",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "description": (
                "Plan-only invalid fixture: 2D input provided with no ground "
                "metric declared; OT cost matrix cannot be constructed without "
                "a declared ground metric."
            ),
            "blocked_outputs": [
                "expected_wasserstein_distances",
                "metric_values",
            ],
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_not_computable_fixture_plan() -> list[dict[str, Any]]:
    return [
        {
            "fixture_plan_id": "nc-001",
            "schema_group_id": "nc-001",
            "not_computable_reason": "EMPTY_INPUT",
            "expected_state": "NOT_COMPUTABLE",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "description": (
                "Plan-only NOT_COMPUTABLE fixture: both distribution weight arrays "
                "are zero-length; Wasserstein distance is undefined and must yield "
                "NOT_COMPUTABLE state."
            ),
            "blocked_outputs": [
                "expected_wasserstein_distances",
                "metric_values",
            ],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_plan_id": "nc-002",
            "schema_group_id": "nc-002",
            "not_computable_reason": "GROUND_METRIC_UNDECLARED",
            "expected_state": "REJECTED_INPUT",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "description": (
                "Plan-only NOT_COMPUTABLE fixture: multi-dimensional input without "
                "a declared ground metric; OT cost matrix cannot be constructed; "
                "input must be rejected."
            ),
            "blocked_outputs": [
                "expected_wasserstein_distances",
                "metric_values",
            ],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_plan_id": "nc-003",
            "schema_group_id": "nc-003",
            "not_computable_reason": "NUMERICAL_POLICY_MISSING",
            "expected_state": "REJECTED_INPUT",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "description": (
                "Plan-only NOT_COMPUTABLE fixture: float precision policy not "
                "declared; computation cannot proceed without explicit float64 "
                "declaration; input must be rejected."
            ),
            "blocked_outputs": [
                "expected_wasserstein_distances",
                "metric_values",
            ],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "fixture_plan_id": "nc-004",
            "schema_group_id": "nc-004",
            "not_computable_reason": "DIMENSIONALITY_UNDECLARED",
            "expected_state": "VALIDATION_ERROR",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "description": (
                "Plan-only NOT_COMPUTABLE fixture: distribution dimensionality not "
                "declared in schema; required for OT algorithm selection; must "
                "yield VALIDATION_ERROR."
            ),
            "blocked_outputs": [
                "expected_wasserstein_distances",
                "metric_values",
            ],
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_determinism_requirements() -> dict[str, Any]:
    return {
        "sort_by_fixture_id": True,
        "stable_serialization_required": True,
        "canonical_hash_required": True,
        "nondeterministic_ordering_allowed": False,
        "replay_stable": True,
        "blocked_outputs_sorted": True,
    }


def default_numerical_policy_requirements() -> dict[str, Any]:
    return {
        "float_precision": "float64",
        "weight_sum_tolerance": "1e-9",
        "policy_declared": True,
        "policy_enforced_at_fixture_validation": False,
        "metric_value_computation_allowed": False,
    }


def default_blocked_scopes() -> dict[str, bool]:
    return {
        "fixture_files_generated": False,
        "wasserstein_computation": False,
        "emits_metric_values": False,
        "expected_wasserstein_distances_added": False,
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
        "fixture_plan_only": True,
        "fixture_files_generated": False,
        "wasserstein_computation_authorized": False,
        "emits_metric_values": False,
        "expected_wasserstein_distances_added": False,
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
        raise WassersteinTestVectorFixturePlanValidationError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_wasserstein_test_vector_fixture_plan(packet: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "fixture_plan_id",
        "fixture_plan_type",
        "operator_id",
        "source_schema_plan_hash",
        "intended_lane",
        "fixture_stage",
        "valid_fixture_plan",
        "invalid_fixture_plan",
        "not_computable_fixture_plan",
        "determinism_requirements",
        "numerical_policy_requirements",
        "blocked_scopes",
        "authority_locks",
        "recommended_next_step",
        "provenance",
        "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise WassersteinTestVectorFixturePlanValidationError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise WassersteinTestVectorFixturePlanValidationError("invalid_schema_version")
    if packet["fixture_plan_type"] != FIXTURE_PLAN_TYPE:
        raise WassersteinTestVectorFixturePlanValidationError("invalid_fixture_plan_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise WassersteinTestVectorFixturePlanValidationError("unknown_operator_id")
    if packet["source_schema_plan_hash"] != SOURCE_SCHEMA_PLAN_HASH:
        raise WassersteinTestVectorFixturePlanValidationError(
            "invalid_source_schema_plan_hash"
        )
    if packet["intended_lane"] not in ALLOWED_LANE:
        raise WassersteinTestVectorFixturePlanValidationError("unknown_intended_lane")
    if packet["fixture_stage"] not in ALLOWED_FIXTURE_STAGE:
        raise WassersteinTestVectorFixturePlanValidationError("unknown_fixture_stage")

    # valid fixture plan — must have one entry per valid schema group
    valid_plan = packet["valid_fixture_plan"]
    if not valid_plan:
        raise WassersteinTestVectorFixturePlanValidationError(
            "valid_fixture_plan_must_be_non_empty"
        )
    seen_v: set[str] = set()
    for entry in valid_plan:
        fid = entry.get("fixture_plan_id")
        if fid in seen_v:
            raise WassersteinTestVectorFixturePlanValidationError(
                "duplicate_valid_fixture_plan_id"
            )
        seen_v.add(fid)
        if entry.get("schema_group_id") not in VALID_GROUP_IDS:
            raise WassersteinTestVectorFixturePlanValidationError(
                "unknown_valid_schema_group_id"
            )
        if entry.get("schema_type") not in ALLOWED_VALID_SCHEMA_TYPE:
            raise WassersteinTestVectorFixturePlanValidationError(
                "unknown_valid_schema_type"
            )
        if entry.get("fixture_stage") not in ALLOWED_FIXTURE_STAGE:
            raise WassersteinTestVectorFixturePlanValidationError(
                "unknown_valid_fixture_stage"
            )
        if entry.get("implementation_status") not in ALLOWED_IMPL_STATUS:
            raise WassersteinTestVectorFixturePlanValidationError(
                "unknown_valid_implementation_status"
            )

    # invalid fixture plan
    invalid_plan = packet["invalid_fixture_plan"]
    if not invalid_plan:
        raise WassersteinTestVectorFixturePlanValidationError(
            "invalid_fixture_plan_must_be_non_empty"
        )
    seen_i: set[str] = set()
    for entry in invalid_plan:
        fid = entry.get("fixture_plan_id")
        if fid in seen_i:
            raise WassersteinTestVectorFixturePlanValidationError(
                "duplicate_invalid_fixture_plan_id"
            )
        seen_i.add(fid)
        if entry.get("schema_group_id") not in INVALID_GROUP_IDS:
            raise WassersteinTestVectorFixturePlanValidationError(
                "unknown_invalid_schema_group_id"
            )
        if entry.get("invalid_reason") not in ALLOWED_INVALID_REASON:
            raise WassersteinTestVectorFixturePlanValidationError(
                "unknown_invalid_reason"
            )
        if entry.get("fixture_stage") not in ALLOWED_FIXTURE_STAGE:
            raise WassersteinTestVectorFixturePlanValidationError(
                "unknown_invalid_fixture_stage"
            )
        if entry.get("implementation_status") not in ALLOWED_IMPL_STATUS:
            raise WassersteinTestVectorFixturePlanValidationError(
                "unknown_invalid_implementation_status"
            )

    # not_computable fixture plan
    nc_plan = packet["not_computable_fixture_plan"]
    if not nc_plan:
        raise WassersteinTestVectorFixturePlanValidationError(
            "not_computable_fixture_plan_must_be_non_empty"
        )
    seen_nc: set[str] = set()
    for entry in nc_plan:
        fid = entry.get("fixture_plan_id")
        if fid in seen_nc:
            raise WassersteinTestVectorFixturePlanValidationError(
                "duplicate_nc_fixture_plan_id"
            )
        seen_nc.add(fid)
        if entry.get("schema_group_id") not in NC_GROUP_IDS:
            raise WassersteinTestVectorFixturePlanValidationError(
                "unknown_nc_schema_group_id"
            )
        if entry.get("not_computable_reason") not in ALLOWED_NC_REASON:
            raise WassersteinTestVectorFixturePlanValidationError(
                "unknown_nc_reason"
            )
        if entry.get("expected_state") not in ALLOWED_NC_STATE:
            raise WassersteinTestVectorFixturePlanValidationError(
                "unknown_nc_expected_state"
            )
        if entry.get("fixture_stage") not in ALLOWED_FIXTURE_STAGE:
            raise WassersteinTestVectorFixturePlanValidationError(
                "unknown_nc_fixture_stage"
            )
        if entry.get("implementation_status") not in ALLOWED_IMPL_STATUS:
            raise WassersteinTestVectorFixturePlanValidationError(
                "unknown_nc_implementation_status"
            )

    if packet["determinism_requirements"] != default_determinism_requirements():
        raise WassersteinTestVectorFixturePlanValidationError(
            "invalid_determinism_requirements"
        )
    if packet["numerical_policy_requirements"] != default_numerical_policy_requirements():
        raise WassersteinTestVectorFixturePlanValidationError(
            "invalid_numerical_policy_requirements"
        )
    if packet["blocked_scopes"] != default_blocked_scopes():
        raise WassersteinTestVectorFixturePlanValidationError("invalid_blocked_scopes")
    if packet["authority_locks"] != default_authority_locks():
        raise WassersteinTestVectorFixturePlanValidationError("invalid_authority_locks")

    _assert_safe(packet["provenance"])


# ---------------------------------------------------------------------------
# Hashing / serialization / build
# ---------------------------------------------------------------------------


def compute_wasserstein_test_vector_fixture_plan_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_wasserstein_test_vector_fixture_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_wasserstein_test_vector_fixture_plan(payload: dict[str, Any]) -> dict[str, Any]:
    def _sort_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        result = sorted(entries, key=lambda x: x["fixture_plan_id"])
        for e in result:
            e["blocked_outputs"] = sorted(e.get("blocked_outputs", []))
        return result

    base: dict[str, Any] = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "fixture_plan_type": FIXTURE_PLAN_TYPE,
        "operator_id": OPERATOR_ID,
        "source_schema_plan_hash": SOURCE_SCHEMA_PLAN_HASH,
        "valid_fixture_plan": _sort_entries(
            payload.get("valid_fixture_plan", default_valid_fixture_plan())
        ),
        "invalid_fixture_plan": _sort_entries(
            payload.get("invalid_fixture_plan", default_invalid_fixture_plan())
        ),
        "not_computable_fixture_plan": _sort_entries(
            payload.get(
                "not_computable_fixture_plan", default_not_computable_fixture_plan()
            )
        ),
        "determinism_requirements": payload.get(
            "determinism_requirements", default_determinism_requirements()
        ),
        "numerical_policy_requirements": payload.get(
            "numerical_policy_requirements", default_numerical_policy_requirements()
        ),
        "blocked_scopes": payload.get("blocked_scopes", default_blocked_scopes()),
        "authority_locks": payload.get("authority_locks", default_authority_locks()),
    }
    base["canonical_hash"] = compute_wasserstein_test_vector_fixture_plan_hash(base)
    validate_wasserstein_test_vector_fixture_plan(base)
    return _finalize(base)
