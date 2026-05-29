from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinTestVectorFixtureSchemaValidationPlan.v1"
PLAN_TYPE = "WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_PLAN"
OPERATOR_ID = "WASSERSTEIN"

SOURCE_COMPLETE_REVIEW_HASH = (
    "08500a6b86b460b03a8858135de0d3c526e9baf58ec4e2c554dd9e03500ac51e"
)
SOURCE_GATE_HASH = (
    "28587def52742f1176de841318ffc830e4c2efc7b00239d8dcab2582ec65c761"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_VALIDATION_STAGE = (
    "FIXTURE_SCHEMA_VALIDATION_PLAN_ONLY",
    "BLOCKED_PENDING_PLAN",
)

EXPECTED_VALID_COUNT = 5
EXPECTED_INVALID_COUNT = 5
EXPECTED_NC_COUNT = 4
EXPECTED_TOTAL = 14

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


class WassersteinTestVectorFixtureSchemaValidationPlanValidationError(ValueError):
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


def default_fixture_schema_validation_scope() -> dict[str, Any]:
    return {
        "total_fixtures": EXPECTED_TOTAL,
        "groups": ["valid", "invalid", "not_computable"],
        "fixture_counts": {
            "valid": EXPECTED_VALID_COUNT,
            "invalid": EXPECTED_INVALID_COUNT,
            "not_computable": EXPECTED_NC_COUNT,
        },
        "validation_approach": "json_parse_and_field_verification",
        "source_gate_hash_pin_check": True,
        "no_computation_posture_check": True,
        "authority_posture_check": True,
    }


def default_valid_fixture_validation_plan() -> list[dict[str, Any]]:
    return [
        {
            "fixture_id": "valid-001",
            "fixture_group": "DISTRIBUTION_PAIR_SCHEMA",
            "checks": [
                "json_parses",
                "fixture_type_is_VALID",
                "input_has_p_and_q_and_support",
                "source_gate_hash_pinned",
                "metric_value_emitted_is_false",
                "expected_distance_included_is_false",
                "intended_lane_is_SHADOW",
            ],
        },
        {
            "fixture_id": "valid-002",
            "fixture_group": "WEIGHTED_HISTOGRAM_SCHEMA",
            "checks": [
                "json_parses",
                "fixture_type_is_VALID",
                "input_has_bin_edges_and_weights",
                "source_gate_hash_pinned",
                "metric_value_emitted_is_false",
                "expected_distance_included_is_false",
                "intended_lane_is_SHADOW",
            ],
        },
        {
            "fixture_id": "valid-003",
            "fixture_group": "REFERENCE_VECTOR_SCHEMA",
            "checks": [
                "json_parses",
                "fixture_type_is_VALID",
                "input_has_reference_vector_and_query_vector",
                "source_gate_hash_pinned",
                "metric_value_emitted_is_false",
                "expected_distance_included_is_false",
                "intended_lane_is_SHADOW",
            ],
        },
        {
            "fixture_id": "valid-004",
            "fixture_group": "GROUND_METRIC_SCHEMA",
            "checks": [
                "json_parses",
                "fixture_type_is_VALID",
                "input_has_cost_matrix_and_distributions",
                "source_gate_hash_pinned",
                "metric_value_emitted_is_false",
                "expected_distance_included_is_false",
                "intended_lane_is_SHADOW",
            ],
        },
        {
            "fixture_id": "valid-005",
            "fixture_group": "DEGENERATE_DISTRIBUTION_SCHEMA",
            "checks": [
                "json_parses",
                "fixture_type_is_VALID",
                "input_has_p_and_q_and_support",
                "source_gate_hash_pinned",
                "metric_value_emitted_is_false",
                "expected_distance_included_is_false",
                "intended_lane_is_SHADOW",
            ],
        },
    ]


def default_invalid_fixture_validation_plan() -> list[dict[str, Any]]:
    return [
        {
            "fixture_id": "invalid-001",
            "fixture_group": "MISSING_REQUIRED_FIELD",
            "checks": [
                "json_parses",
                "fixture_type_is_INVALID",
                "rejection_reason_present",
                "rejection_reason_contains_missing_required_field",
                "source_gate_hash_pinned",
                "metric_value_emitted_is_false",
                "expected_distance_included_is_false",
                "intended_lane_is_SHADOW",
            ],
        },
        {
            "fixture_id": "invalid-002",
            "fixture_group": "EMPTY_DISTRIBUTION",
            "checks": [
                "json_parses",
                "fixture_type_is_INVALID",
                "rejection_reason_present",
                "rejection_reason_contains_empty_distribution",
                "source_gate_hash_pinned",
                "metric_value_emitted_is_false",
                "expected_distance_included_is_false",
                "intended_lane_is_SHADOW",
            ],
        },
        {
            "fixture_id": "invalid-003",
            "fixture_group": "INVALID_WEIGHT_SUM",
            "checks": [
                "json_parses",
                "fixture_type_is_INVALID",
                "rejection_reason_present",
                "rejection_reason_contains_invalid_weight_sum",
                "source_gate_hash_pinned",
                "metric_value_emitted_is_false",
                "expected_distance_included_is_false",
                "intended_lane_is_SHADOW",
            ],
        },
        {
            "fixture_id": "invalid-004",
            "fixture_group": "DIMENSION_MISMATCH",
            "checks": [
                "json_parses",
                "fixture_type_is_INVALID",
                "rejection_reason_present",
                "rejection_reason_contains_dimension_mismatch",
                "source_gate_hash_pinned",
                "metric_value_emitted_is_false",
                "expected_distance_included_is_false",
                "intended_lane_is_SHADOW",
            ],
        },
        {
            "fixture_id": "invalid-005",
            "fixture_group": "GROUND_METRIC_UNDECLARED",
            "checks": [
                "json_parses",
                "fixture_type_is_INVALID",
                "rejection_reason_present",
                "rejection_reason_contains_ground_metric_undeclared",
                "source_gate_hash_pinned",
                "metric_value_emitted_is_false",
                "expected_distance_included_is_false",
                "intended_lane_is_SHADOW",
            ],
        },
    ]


def default_not_computable_fixture_validation_plan() -> list[dict[str, Any]]:
    return [
        {
            "fixture_id": "nc-001",
            "fixture_group": "EMPTY_INPUT",
            "checks": [
                "json_parses",
                "fixture_type_is_NOT_COMPUTABLE",
                "rejection_reason_present",
                "rejection_reason_contains_not_computable",
                "source_gate_hash_pinned",
                "metric_value_emitted_is_false",
                "expected_distance_included_is_false",
                "intended_lane_is_SHADOW",
            ],
        },
        {
            "fixture_id": "nc-002",
            "fixture_group": "GROUND_METRIC_UNDECLARED",
            "checks": [
                "json_parses",
                "fixture_type_is_NOT_COMPUTABLE",
                "rejection_reason_present",
                "rejection_reason_contains_not_computable",
                "source_gate_hash_pinned",
                "metric_value_emitted_is_false",
                "expected_distance_included_is_false",
                "intended_lane_is_SHADOW",
            ],
        },
        {
            "fixture_id": "nc-003",
            "fixture_group": "NUMERICAL_POLICY_MISSING",
            "checks": [
                "json_parses",
                "fixture_type_is_NOT_COMPUTABLE",
                "rejection_reason_present",
                "rejection_reason_contains_not_computable",
                "source_gate_hash_pinned",
                "metric_value_emitted_is_false",
                "expected_distance_included_is_false",
                "intended_lane_is_SHADOW",
            ],
        },
        {
            "fixture_id": "nc-004",
            "fixture_group": "DIMENSIONALITY_UNDECLARED",
            "checks": [
                "json_parses",
                "fixture_type_is_NOT_COMPUTABLE",
                "rejection_reason_present",
                "rejection_reason_contains_not_computable",
                "source_gate_hash_pinned",
                "metric_value_emitted_is_false",
                "expected_distance_included_is_false",
                "intended_lane_is_SHADOW",
            ],
        },
    ]


def default_no_metric_value_scan_plan() -> dict[str, Any]:
    return {
        "check_id": "no_metric_value_scan",
        "field": "metric_value_emitted",
        "expected_value": False,
        "applies_to": "all_14_fixtures",
        "scan_method": "field_equality_check",
        "failure_action": "BLOCK_VALIDATION",
    }


def default_no_expected_distance_scan_plan() -> dict[str, Any]:
    return {
        "check_id": "no_expected_distance_scan",
        "field": "expected_wasserstein_distance_included",
        "expected_value": False,
        "applies_to": "all_14_fixtures",
        "scan_method": "field_equality_check",
        "failure_action": "BLOCK_VALIDATION",
    }


def default_authority_lock_scan_plan() -> dict[str, Any]:
    return {
        "check_id": "authority_lock_scan",
        "checks": [
            {
                "name": "fixture_creation_authorized_is_true",
                "field": "fixture_creation_authorized",
                "expected_value": True,
                "applies_to": "all_14_fixtures",
            },
            {
                "name": "intended_lane_is_SHADOW",
                "field": "intended_lane",
                "expected_value": "SHADOW",
                "applies_to": "all_14_fixtures",
            },
            {
                "name": "source_gate_hash_pinned",
                "field": "source_gate_hash",
                "expected_value": SOURCE_GATE_HASH,
                "applies_to": "all_14_fixtures",
            },
            {
                "name": "no_execution_authority_granted",
                "field": "execution_authority",
                "expected_value": None,
                "applies_to": "all_14_fixtures",
                "check_type": "field_absent",
            },
            {
                "name": "no_computation_authorization",
                "check_type": "no_computation_fields_present",
                "applies_to": "all_14_fixtures",
            },
        ],
        "failure_action": "BLOCK_VALIDATION",
    }


def default_blocked_scopes() -> dict[str, bool]:
    return {
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
        "fixture_schema_validation_plan_only": True,
        "fixture_schema_validation_executed": False,
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
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _validate_valid_plan(plan: list[dict[str, Any]]) -> None:
    if len(plan) != EXPECTED_VALID_COUNT:
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            f"valid_plan_count_mismatch:expected={EXPECTED_VALID_COUNT}"
        )
    for entry in plan:
        if entry.get("fixture_id", "").split("-")[0] != "valid":
            raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
                f"invalid_fixture_id_in_valid_plan:{entry.get('fixture_id')}"
            )


def _validate_invalid_plan(plan: list[dict[str, Any]]) -> None:
    if len(plan) != EXPECTED_INVALID_COUNT:
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            f"invalid_plan_count_mismatch:expected={EXPECTED_INVALID_COUNT}"
        )
    for entry in plan:
        if entry.get("fixture_id", "").split("-")[0] != "invalid":
            raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
                f"non_invalid_fixture_in_invalid_plan:{entry.get('fixture_id')}"
            )


def _validate_nc_plan(plan: list[dict[str, Any]]) -> None:
    if len(plan) != EXPECTED_NC_COUNT:
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            f"nc_plan_count_mismatch:expected={EXPECTED_NC_COUNT}"
        )
    for entry in plan:
        if entry.get("fixture_id", "").split("-")[0] != "nc":
            raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
                f"non_nc_fixture_in_nc_plan:{entry.get('fixture_id')}"
            )


def validate_wasserstein_test_vector_fixture_schema_validation_plan(
    packet: dict[str, Any],
) -> None:
    required = {
        "schema_version",
        "validation_plan_id",
        "plan_type",
        "operator_id",
        "source_complete_review_hash",
        "intended_lane",
        "validation_stage",
        "fixture_schema_validation_scope",
        "valid_fixture_validation_plan",
        "invalid_fixture_validation_plan",
        "not_computable_fixture_validation_plan",
        "no_metric_value_scan_plan",
        "no_expected_distance_scan_plan",
        "authority_lock_scan_plan",
        "blocked_scopes",
        "authority_locks",
        "recommended_next_step",
        "provenance",
        "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            "invalid_schema_version"
        )
    if packet["plan_type"] != PLAN_TYPE:
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            "invalid_plan_type"
        )
    if packet["operator_id"] != OPERATOR_ID:
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            "unknown_operator_id"
        )
    if packet["source_complete_review_hash"] != SOURCE_COMPLETE_REVIEW_HASH:
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            "invalid_source_complete_review_hash"
        )
    if packet["intended_lane"] not in ALLOWED_LANE:
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            "unknown_intended_lane"
        )
    if packet["validation_stage"] not in ALLOWED_VALIDATION_STAGE:
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            "unknown_validation_stage"
        )

    scope = packet["fixture_schema_validation_scope"]
    if scope.get("total_fixtures") != EXPECTED_TOTAL:
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            "scope_total_fixtures_mismatch"
        )

    _validate_valid_plan(packet["valid_fixture_validation_plan"])
    _validate_invalid_plan(packet["invalid_fixture_validation_plan"])
    _validate_nc_plan(packet["not_computable_fixture_validation_plan"])

    al = packet["authority_locks"]
    if al.get("fixture_schema_validation_executed") is not False:
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            "fixture_schema_validation_executed_must_be_false"
        )
    if al.get("wasserstein_computation_authorized") is not False:
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            "wasserstein_computation_must_be_unauthorized"
        )
    if al.get("fixture_schema_validation_plan_only") is not True:
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            "fixture_schema_validation_plan_only_must_be_true"
        )
    if packet["authority_locks"] != default_authority_locks():
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            "invalid_authority_locks"
        )
    if packet["blocked_scopes"] != default_blocked_scopes():
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            "invalid_blocked_scopes"
        )
    if (
        packet["valid_fixture_validation_plan"]
        != default_valid_fixture_validation_plan()
    ):
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            "invalid_valid_fixture_validation_plan"
        )
    if (
        packet["invalid_fixture_validation_plan"]
        != default_invalid_fixture_validation_plan()
    ):
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            "invalid_invalid_fixture_validation_plan"
        )
    if (
        packet["not_computable_fixture_validation_plan"]
        != default_not_computable_fixture_validation_plan()
    ):
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            "invalid_not_computable_fixture_validation_plan"
        )
    if packet["no_metric_value_scan_plan"] != default_no_metric_value_scan_plan():
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            "invalid_no_metric_value_scan_plan"
        )
    if (
        packet["no_expected_distance_scan_plan"]
        != default_no_expected_distance_scan_plan()
    ):
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            "invalid_no_expected_distance_scan_plan"
        )
    if packet["authority_lock_scan_plan"] != default_authority_lock_scan_plan():
        raise WassersteinTestVectorFixtureSchemaValidationPlanValidationError(
            "invalid_authority_lock_scan_plan"
        )

    _assert_safe(packet["provenance"])


# ---------------------------------------------------------------------------
# Hashing / serialization / build
# ---------------------------------------------------------------------------


def compute_wasserstein_test_vector_fixture_schema_validation_plan_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_wasserstein_test_vector_fixture_schema_validation_plan(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_wasserstein_test_vector_fixture_schema_validation_plan(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "plan_type": PLAN_TYPE,
        "operator_id": OPERATOR_ID,
        "source_complete_review_hash": SOURCE_COMPLETE_REVIEW_HASH,
        "fixture_schema_validation_scope": payload.get(
            "fixture_schema_validation_scope",
            default_fixture_schema_validation_scope(),
        ),
        "valid_fixture_validation_plan": payload.get(
            "valid_fixture_validation_plan",
            default_valid_fixture_validation_plan(),
        ),
        "invalid_fixture_validation_plan": payload.get(
            "invalid_fixture_validation_plan",
            default_invalid_fixture_validation_plan(),
        ),
        "not_computable_fixture_validation_plan": payload.get(
            "not_computable_fixture_validation_plan",
            default_not_computable_fixture_validation_plan(),
        ),
        "no_metric_value_scan_plan": payload.get(
            "no_metric_value_scan_plan",
            default_no_metric_value_scan_plan(),
        ),
        "no_expected_distance_scan_plan": payload.get(
            "no_expected_distance_scan_plan",
            default_no_expected_distance_scan_plan(),
        ),
        "authority_lock_scan_plan": payload.get(
            "authority_lock_scan_plan",
            default_authority_lock_scan_plan(),
        ),
        "authority_locks": payload.get("authority_locks", default_authority_locks()),
        "blocked_scopes": payload.get("blocked_scopes", default_blocked_scopes()),
    }
    base["canonical_hash"] = (
        compute_wasserstein_test_vector_fixture_schema_validation_plan_hash(base)
    )
    validate_wasserstein_test_vector_fixture_schema_validation_plan(base)
    return _finalize(base)
