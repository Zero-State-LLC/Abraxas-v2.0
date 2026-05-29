from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinTestVectorSchemaPlan.v1"
PLAN_TYPE = "WASSERSTEIN_TEST_VECTOR_SCHEMA_PLAN"
OPERATOR_ID = "WASSERSTEIN"

ALLOWED_SCHEMA_FAMILY = (
    "VALID_VECTOR_SCHEMA",
    "INVALID_VECTOR_SCHEMA",
    "NOT_COMPUTABLE_SCHEMA",
    "MIXED_SCHEMA_PLAN",
)
ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_SCHEMA_STAGE = (
    "SCHEMA_PLAN_ONLY",
    "SCHEMA_REQUIREMENTS_ONLY",
    "SCHEMA_LAYOUT_ONLY",
    "BLOCKED_PENDING_OPERATOR_REVIEW",
)
ALLOWED_SCHEMA_TYPE = (
    "DISTRIBUTION_PAIR_SCHEMA",
    "WEIGHTED_HISTOGRAM_SCHEMA",
    "DEGENERATE_DISTRIBUTION_SCHEMA",
    "REFERENCE_VECTOR_SCHEMA",
    "GROUND_METRIC_SCHEMA",
)
ALLOWED_INVALID_REASON = (
    "MISSING_REQUIRED_FIELD",
    "EMPTY_DISTRIBUTION",
    "INVALID_WEIGHT_SUM",
    "NEGATIVE_WEIGHT",
    "DIMENSION_MISMATCH",
    "GROUND_METRIC_UNDECLARED",
    "AUTHORITY_FLAG_TRUE",
)
ALLOWED_NC_REASON = (
    "EMPTY_INPUT",
    "MALFORMED_SCHEMA",
    "DIMENSIONALITY_UNDECLARED",
    "GROUND_METRIC_UNDECLARED",
    "NUMERICAL_POLICY_MISSING",
    "INPUT_CONTRACT_VIOLATION",
)
ALLOWED_NC_STATE = ("NOT_COMPUTABLE", "VALIDATION_ERROR", "REJECTED_INPUT")
ALLOWED_IMPL_STATUS = ("PLANNED_ONLY", "NOT_IMPLEMENTED", "BLOCKED_PENDING_REVIEW")
LOCKED_FALSE_FLAGS = (
    "production_activation",
    "canon_promotion",
    "scheduler_mutation",
    "runtime_authority",
    "runtime_mutation",
    "forecast_influence",
    "execution_authority",
    "token_minting_allowed",
    "valid_for_execution",
    "activation_approved",
    "authorization_granted",
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
    "schema-file",
    "sinkhorn-kernel",
)


class WassersteinTestVectorSchemaPlanValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def default_valid_schema_groups() -> list[dict[str, Any]]:
    return [
        {
            "group_id": "valid-001",
            "schema_type": "DISTRIBUTION_PAIR_SCHEMA",
            "description": (
                "Standard discrete distribution pair: two finite distributions over a shared "
                "support with non-negative weights summing to 1."
            ),
            "expected_input_contract": "distribution_pair_fields_declared",
            "blocked_operations": ["wasserstein_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-002",
            "schema_type": "WEIGHTED_HISTOGRAM_SCHEMA",
            "description": (
                "Distribution expressed as parallel weights and support arrays; "
                "weights normalised to sum to 1 before schema registration."
            ),
            "expected_input_contract": "weights_and_support_arrays_declared",
            "blocked_operations": ["wasserstein_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-003",
            "schema_type": "REFERENCE_VECTOR_SCHEMA",
            "description": (
                "1D reference vectors with known analytic Wasserstein-1 result; "
                "used for deterministic replay and regression validation."
            ),
            "expected_input_contract": "reference_vector_fields_declared",
            "blocked_operations": ["wasserstein_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-004",
            "schema_type": "GROUND_METRIC_SCHEMA",
            "description": (
                "Euclidean cost matrix specification for 2D discrete OT inputs; "
                "ground metric must be frozen before fixture creation."
            ),
            "expected_input_contract": "ground_metric_declared",
            "blocked_operations": ["wasserstein_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "valid-005",
            "schema_type": "DEGENERATE_DISTRIBUTION_SCHEMA",
            "description": (
                "Near-degenerate distributions: single non-zero weight entry or "
                "all mass at one support point; valid schema but edge-case input."
            ),
            "expected_input_contract": "degenerate_distribution_fields_declared",
            "blocked_operations": ["wasserstein_computation"],
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_invalid_schema_groups() -> list[dict[str, Any]]:
    return [
        {
            "group_id": "invalid-001",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "target_field": "distribution_a",
            "expected_failure": "validation_error_missing_distribution_a",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "invalid-002",
            "invalid_reason": "EMPTY_DISTRIBUTION",
            "target_field": "distribution_a_weights",
            "expected_failure": "validation_error_empty_distribution",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "invalid-003",
            "invalid_reason": "INVALID_WEIGHT_SUM",
            "target_field": "distribution_b_weights",
            "expected_failure": "validation_error_weights_do_not_sum_to_one",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "invalid-004",
            "invalid_reason": "DIMENSION_MISMATCH",
            "target_field": "distribution_support",
            "expected_failure": "validation_error_support_dimension_mismatch",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "invalid-005",
            "invalid_reason": "GROUND_METRIC_UNDECLARED",
            "target_field": "ground_metric",
            "expected_failure": "validation_error_ground_metric_not_declared",
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_not_computable_schema_groups() -> list[dict[str, Any]]:
    return [
        {
            "group_id": "nc-001",
            "not_computable_reason": "EMPTY_INPUT",
            "description": (
                "Zero-element distribution: both weights arrays are empty; "
                "Wasserstein distance is undefined and must yield NOT_COMPUTABLE."
            ),
            "expected_state": "NOT_COMPUTABLE",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "nc-002",
            "not_computable_reason": "GROUND_METRIC_UNDECLARED",
            "description": (
                "Multi-dimensional input without a declared ground metric; "
                "OT cost matrix cannot be constructed."
            ),
            "expected_state": "REJECTED_INPUT",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "nc-003",
            "not_computable_reason": "NUMERICAL_POLICY_MISSING",
            "description": (
                "Float precision policy not specified; "
                "computation cannot proceed without explicit float64 declaration."
            ),
            "expected_state": "REJECTED_INPUT",
            "implementation_status": "PLANNED_ONLY",
        },
        {
            "group_id": "nc-004",
            "not_computable_reason": "DIMENSIONALITY_UNDECLARED",
            "description": (
                "Distribution dimensionality not declared in schema; "
                "required for OT algorithm selection."
            ),
            "expected_state": "VALIDATION_ERROR",
            "implementation_status": "PLANNED_ONLY",
        },
    ]


def default_schema_layout_plan() -> dict[str, bool]:
    return {
        "schema_files_added": False,
        "fixture_files_added": False,
        "schema_directory_declared": True,
        "validation_layout_declared": True,
        "expected_metric_values_declared": False,
    }


def default_schema_constraints() -> dict[str, bool]:
    return {
        "schema_files_generated": False,
        "fixture_files_generated": False,
        "metric_values_added": False,
        "expected_wasserstein_distances_added": False,
        "wasserstein_math_added": False,
        "scoring_added": False,
        "runtime_binding_added": False,
        "forecast_influence_added": False,
    }


def default_validation_plan() -> dict[str, bool]:
    return {
        "requires_valid_schema_tests": True,
        "requires_invalid_schema_tests": True,
        "requires_not_computable_schema_tests": True,
        "requires_schema_validation": True,
        "requires_no_metric_value_scan": True,
        "requires_no_authority_scan": True,
        "requires_no_fixture_file_scan": True,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_schema_files": False,
        "emits_fixture_files": False,
        "emits_metric_values": False,
        "emits_expected_wasserstein_distances": False,
        "emits_wasserstein_outputs": False,
        "emits_scores": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_schema_plan": True,
        "emits_schema_group_metadata": True,
    }


def _assert_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _assert_safe(x)
    elif isinstance(v, list):
        for x in v:
            _assert_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise WassersteinTestVectorSchemaPlanValidationError(
            "forbidden_provenance_reference_detected"
        )


def _assert_unique(items: list[dict[str, Any]], key: str, err: str) -> None:
    seen: set[str] = set()
    for item in items:
        ident = item.get(key)
        if ident in seen:
            raise WassersteinTestVectorSchemaPlanValidationError(err)
        seen.add(ident)


def validate_wasserstein_test_vector_schema_plan(packet: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "plan_id",
        "plan_type",
        "operator_id",
        "source_dossier_refs",
        "source_metric_registry_refs",
        "source_baseline_vector_pack_refs",
        "schema_scope",
        "valid_schema_groups",
        "invalid_schema_groups",
        "not_computable_schema_groups",
        "schema_layout_plan",
        "schema_constraints",
        "validation_plan",
        "output_contract",
        "governance_flags",
        "provenance",
        "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise WassersteinTestVectorSchemaPlanValidationError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise WassersteinTestVectorSchemaPlanValidationError("invalid_schema_version")
    if packet["plan_type"] != PLAN_TYPE:
        raise WassersteinTestVectorSchemaPlanValidationError("invalid_plan_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise WassersteinTestVectorSchemaPlanValidationError("unknown_operator_id")

    scope = packet["schema_scope"]
    if scope.get("schema_family") not in ALLOWED_SCHEMA_FAMILY:
        raise WassersteinTestVectorSchemaPlanValidationError("unknown_schema_family")
    if scope.get("intended_lane") not in ALLOWED_LANE:
        raise WassersteinTestVectorSchemaPlanValidationError("unknown_intended_lane")
    if scope.get("schema_stage") not in ALLOWED_SCHEMA_STAGE:
        raise WassersteinTestVectorSchemaPlanValidationError("unknown_schema_stage")

    valid = packet["valid_schema_groups"]
    invalid = packet["invalid_schema_groups"]
    nc = packet["not_computable_schema_groups"]

    if not valid:
        raise WassersteinTestVectorSchemaPlanValidationError(
            "valid_schema_groups_must_be_non_empty"
        )
    if not invalid:
        raise WassersteinTestVectorSchemaPlanValidationError(
            "invalid_schema_groups_must_be_non_empty"
        )
    if not nc:
        raise WassersteinTestVectorSchemaPlanValidationError(
            "not_computable_schema_groups_must_be_non_empty"
        )

    _assert_unique(valid, "group_id", "duplicate_group_id")
    _assert_unique(invalid, "group_id", "duplicate_group_id")
    _assert_unique(nc, "group_id", "duplicate_group_id")

    for entry in valid:
        if entry.get("schema_type") not in ALLOWED_SCHEMA_TYPE:
            raise WassersteinTestVectorSchemaPlanValidationError("unknown_schema_type")
        if entry.get("implementation_status") not in ALLOWED_IMPL_STATUS:
            raise WassersteinTestVectorSchemaPlanValidationError(
                "unknown_implementation_status"
            )
    for entry in invalid:
        if entry.get("invalid_reason") not in ALLOWED_INVALID_REASON:
            raise WassersteinTestVectorSchemaPlanValidationError("unknown_invalid_reason")
        if entry.get("implementation_status") not in ALLOWED_IMPL_STATUS:
            raise WassersteinTestVectorSchemaPlanValidationError(
                "unknown_implementation_status"
            )
    for entry in nc:
        if entry.get("not_computable_reason") not in ALLOWED_NC_REASON:
            raise WassersteinTestVectorSchemaPlanValidationError(
                "unknown_not_computable_reason"
            )
        if entry.get("expected_state") not in ALLOWED_NC_STATE:
            raise WassersteinTestVectorSchemaPlanValidationError("unknown_expected_state")
        if entry.get("implementation_status") not in ALLOWED_IMPL_STATUS:
            raise WassersteinTestVectorSchemaPlanValidationError(
                "unknown_implementation_status"
            )

    if packet["schema_layout_plan"] != default_schema_layout_plan():
        raise WassersteinTestVectorSchemaPlanValidationError("invalid_schema_layout_plan")
    if packet["schema_constraints"] != default_schema_constraints():
        raise WassersteinTestVectorSchemaPlanValidationError("invalid_schema_constraints")
    if packet["validation_plan"] != default_validation_plan():
        raise WassersteinTestVectorSchemaPlanValidationError("invalid_validation_plan")
    if packet["output_contract"] != default_output_contract():
        raise WassersteinTestVectorSchemaPlanValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise WassersteinTestVectorSchemaPlanValidationError(
                f"authority_lock_must_be_false:{flag}"
            )

    _assert_safe(packet["provenance"])


def compute_wasserstein_test_vector_schema_plan_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_wasserstein_test_vector_schema_plan(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_wasserstein_test_vector_schema_plan(payload: dict[str, Any]) -> dict[str, Any]:
    valid = sorted(
        payload.get("valid_schema_groups", default_valid_schema_groups()),
        key=lambda x: x["group_id"],
    )
    invalid = sorted(
        payload.get("invalid_schema_groups", default_invalid_schema_groups()),
        key=lambda x: x["group_id"],
    )
    nc = sorted(
        payload.get("not_computable_schema_groups", default_not_computable_schema_groups()),
        key=lambda x: x["group_id"],
    )
    for item in valid:
        item["blocked_operations"] = sorted(item.get("blocked_operations", []))

    base: dict[str, Any] = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "plan_type": PLAN_TYPE,
        "operator_id": OPERATOR_ID,
        "source_dossier_refs": sorted(payload.get("source_dossier_refs", [])),
        "source_metric_registry_refs": sorted(
            payload.get("source_metric_registry_refs", [])
        ),
        "source_baseline_vector_pack_refs": sorted(
            payload.get("source_baseline_vector_pack_refs", [])
        ),
        "valid_schema_groups": valid,
        "invalid_schema_groups": invalid,
        "not_computable_schema_groups": nc,
        "schema_layout_plan": payload.get(
            "schema_layout_plan", default_schema_layout_plan()
        ),
        "schema_constraints": payload.get(
            "schema_constraints", default_schema_constraints()
        ),
        "validation_plan": payload.get("validation_plan", default_validation_plan()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_wasserstein_test_vector_schema_plan_hash(base)
    validate_wasserstein_test_vector_schema_plan(base)
    return _finalize(base)
