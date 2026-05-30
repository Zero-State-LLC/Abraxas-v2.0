from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "GeodesicTestVectorFixturePlan.v1"
FIXTURE_PLAN_TYPE = "GEODESIC_TEST_VECTOR_FIXTURE_PLAN"
OPERATOR_ID = "GEODESIC"
SOURCE_SCHEMA_PLAN_HASH = (
    "23b4c2aaf51238f2a285829c1e4744422bc13fc50fc3f8b5dd27f26ffed35830"
)
SOURCE_AUTHORIZATION_REVIEW_HASH = (
    "78c7ebdfc509950ad5eebdc03aaf7d0a67856db7060ca9c9f9d80c5726730d51"
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
)
NC_GROUP_IDS = ("nc-001", "nc-002", "nc-003", "nc-004")

ALLOWED_INVALID_REASON = (
    "MISSING_REQUIRED_FIELD",
    "NEGATIVE_EDGE_WEIGHT",
)
ALLOWED_NC_REASON = (
    "EMPTY_INPUT",
    "DISCONNECTED_GRAPH",
    "SOURCE_NODE_NOT_IN_GRAPH",
    "TARGET_NODE_NOT_IN_GRAPH",
)
ALLOWED_NC_STATE = ("NOT_COMPUTABLE", "REJECTED_INPUT", "VALIDATION_ERROR")

FORBIDDEN = (
    "runtime",
    "scheduler",
    "cache",
    "forecast",
    "scoring",
    "metric-value",
    "geodesic-distance",
    "dijkstra-execution",
    "shortest-path-computation",
    "fixture-file",
    "manifest-file",
    "schema-file",
    "numpy",
    "scipy",
    "gpu-kernel",
)


class GeodesicTestVectorFixturePlanValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise GeodesicTestVectorFixturePlanValidationError(
            "forbidden_token_detected_in_string_value"
        )


def build_valid_fixture_plan() -> list[dict[str, Any]]:
    return [
        {
            "fixture_plan_id": "valid-001",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "implementation_status": "PLANNED_ONLY",
            "blocked_outputs": ["expected_geodesic_distances", "metric_values"],
            "case_family": "SIMPLE_CONNECTED_WEIGHTED_GRAPH",
            "description": (
                "Plan-only fixture: simple connected weighted graph (3 nodes, 3 edges); "
                "direct single-hop connection is shortest path. "
                "No geodesic distance value declared."
            ),
        },
        {
            "fixture_plan_id": "valid-002",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "implementation_status": "PLANNED_ONLY",
            "blocked_outputs": ["expected_geodesic_distances", "metric_values"],
            "case_family": "MULTI_HOP_GRAPH",
            "description": (
                "Plan-only fixture: multi-hop graph (4 nodes, 5 edges); "
                "indirect path through intermediate nodes is cheaper than direct edge. "
                "No geodesic distance value declared."
            ),
        },
        {
            "fixture_plan_id": "valid-003",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "implementation_status": "PLANNED_ONLY",
            "blocked_outputs": ["expected_geodesic_distances", "metric_values"],
            "case_family": "SELF_LOOP",
            "description": (
                "Plan-only fixture: source_node equals target_node; "
                "expected geodesic distance is 0.0 by convention. "
                "No geodesic distance value declared."
            ),
        },
        {
            "fixture_plan_id": "valid-004",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "implementation_status": "PLANNED_ONLY",
            "blocked_outputs": ["expected_geodesic_distances", "metric_values"],
            "case_family": "UNWEIGHTED_GRAPH",
            "description": (
                "Plan-only fixture: unweighted graph with all edge weights equal to 1.0; "
                "BFS-equivalent result; 3-hop shortest path. "
                "No geodesic distance value declared."
            ),
        },
        {
            "fixture_plan_id": "valid-005",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "implementation_status": "PLANNED_ONLY",
            "blocked_outputs": ["expected_geodesic_distances", "metric_values"],
            "case_family": "COMPLETE_GRAPH",
            "description": (
                "Plan-only fixture: complete graph (5 nodes, 10 directed edges); "
                "direct single-hop edge is always the shortest path. "
                "No geodesic distance value declared."
            ),
        },
    ]


def build_invalid_fixture_plan() -> list[dict[str, Any]]:
    return [
        {
            "fixture_plan_id": "invalid-001",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "implementation_status": "PLANNED_ONLY",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "target_field": "source_node",
            "expected_failure": "validation_error_missing_source_node",
            "blocked_outputs": ["expected_geodesic_distances", "metric_values"],
            "description": (
                "Plan-only invalid fixture: source_node field absent from input; "
                "schema contract violated at the required-field level."
            ),
        },
        {
            "fixture_plan_id": "invalid-002",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "implementation_status": "PLANNED_ONLY",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "target_field": "target_node",
            "expected_failure": "validation_error_missing_target_node",
            "blocked_outputs": ["expected_geodesic_distances", "metric_values"],
            "description": (
                "Plan-only invalid fixture: target_node field absent from input; "
                "schema contract violated at the required-field level."
            ),
        },
        {
            "fixture_plan_id": "invalid-003",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "implementation_status": "PLANNED_ONLY",
            "invalid_reason": "MISSING_REQUIRED_FIELD",
            "target_field": "edge_list",
            "expected_failure": "validation_error_missing_edge_list",
            "blocked_outputs": ["expected_geodesic_distances", "metric_values"],
            "description": (
                "Plan-only invalid fixture: edge_list field absent from input; "
                "schema contract violated at the required-field level."
            ),
        },
        {
            "fixture_plan_id": "invalid-004",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "implementation_status": "PLANNED_ONLY",
            "invalid_reason": "NEGATIVE_EDGE_WEIGHT",
            "target_field": "edge_list[*].weight",
            "expected_failure": "validation_error_negative_edge_weight",
            "blocked_outputs": ["expected_geodesic_distances", "metric_values"],
            "description": (
                "Plan-only invalid fixture: one or more edges carry a negative weight; "
                "all edge weights must be >= 0.0."
            ),
        },
    ]


def build_not_computable_fixture_plan() -> list[dict[str, Any]]:
    return [
        {
            "fixture_plan_id": "nc-001",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "implementation_status": "PLANNED_ONLY",
            "not_computable_reason": "EMPTY_INPUT",
            "expected_state": "NOT_COMPUTABLE",
            "blocked_outputs": ["expected_geodesic_distances", "metric_values"],
            "description": (
                "Plan-only NOT_COMPUTABLE fixture: empty graph (zero nodes); "
                "geodesic distance is undefined and must yield NOT_COMPUTABLE state."
            ),
        },
        {
            "fixture_plan_id": "nc-002",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "implementation_status": "PLANNED_ONLY",
            "not_computable_reason": "DISCONNECTED_GRAPH",
            "expected_state": "NOT_COMPUTABLE",
            "blocked_outputs": ["expected_geodesic_distances", "metric_values"],
            "description": (
                "Plan-only NOT_COMPUTABLE fixture: source and target nodes lie in "
                "disconnected graph components; no path exists and distance is NOT_COMPUTABLE."
            ),
        },
        {
            "fixture_plan_id": "nc-003",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "implementation_status": "PLANNED_ONLY",
            "not_computable_reason": "SOURCE_NODE_NOT_IN_GRAPH",
            "expected_state": "NOT_COMPUTABLE",
            "blocked_outputs": ["expected_geodesic_distances", "metric_values"],
            "description": (
                "Plan-only NOT_COMPUTABLE fixture: source_node identifier not present "
                "in the graph node set; must yield NOT_COMPUTABLE."
            ),
        },
        {
            "fixture_plan_id": "nc-004",
            "fixture_stage": "FIXTURE_PLAN_ONLY",
            "implementation_status": "PLANNED_ONLY",
            "not_computable_reason": "TARGET_NODE_NOT_IN_GRAPH",
            "expected_state": "NOT_COMPUTABLE",
            "blocked_outputs": ["expected_geodesic_distances", "metric_values"],
            "description": (
                "Plan-only NOT_COMPUTABLE fixture: target_node identifier not present "
                "in the graph node set; must yield NOT_COMPUTABLE."
            ),
        },
    ]


def build_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "canon_promotion": False,
        "emits_expected_geodesic_distances": False,
        "emits_metric_values": False,
        "execution_authority": False,
        "fixture_files_generated": False,
        "fixture_plan_only": True,
        "forecast_influence": False,
        "inference_authority": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "runtime_mutation": False,
    }


def build_blocked_scopes() -> dict[str, Any]:
    return {
        "canon_promotion": False,
        "emits_expected_geodesic_distances": False,
        "emits_metric_values": False,
        "execution_authority": False,
        "fixture_files_generated": False,
        "forecast_influence": False,
        "inference_authority": False,
        "p43_surface_lanes": False,
        "production_activation": False,
        "runtime_mutation": False,
        "geodesic_computation": False,
    }


def build_determinism_requirements() -> dict[str, Any]:
    return {
        "blocked_outputs_sorted": True,
        "canonical_hash_required": True,
        "nondeterministic_ordering_allowed": False,
        "replay_stable": True,
        "sort_by_fixture_id": True,
        "stable_serialization_required": True,
    }


def build_numerical_policy_requirements() -> dict[str, Any]:
    return {
        "float_precision": "float64",
        "metric_value_computation_allowed": False,
        "policy_declared": True,
        "policy_enforced_at_fixture_validation": False,
        "weight_non_negative_required": True,
    }


def build_fixture_plan(
    plan_id: str = "geodesic_test_vector_fixture_plan_001",
    created_at_utc: str = "2026-05-30T00:00:00Z",
    intended_lane: str = "SHADOW",
) -> dict[str, Any]:
    if intended_lane not in ALLOWED_LANE:
        raise GeodesicTestVectorFixturePlanValidationError(
            f"intended_lane must be one of {ALLOWED_LANE}"
        )

    valid_plan = build_valid_fixture_plan()
    invalid_plan = build_invalid_fixture_plan()
    nc_plan = build_not_computable_fixture_plan()

    _validate_valid_plan(valid_plan)
    _validate_invalid_plan(invalid_plan)
    _validate_nc_plan(nc_plan)

    preimage: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "fixture_plan_type": FIXTURE_PLAN_TYPE,
        "fixture_plan_id": plan_id,
        "fixture_stage": "FIXTURE_PLAN_ONLY",
        "operator_id": OPERATOR_ID,
        "created_at_utc": created_at_utc,
        "intended_lane": intended_lane,
        "source_schema_plan_hash": SOURCE_SCHEMA_PLAN_HASH,
        "source_authorization_review_hash": SOURCE_AUTHORIZATION_REVIEW_HASH,
        "valid_fixture_plan": valid_plan,
        "invalid_fixture_plan": invalid_plan,
        "not_computable_fixture_plan": nc_plan,
        "authority_locks": build_authority_locks(),
        "blocked_scopes": build_blocked_scopes(),
        "determinism_requirements": build_determinism_requirements(),
        "numerical_policy_requirements": build_numerical_policy_requirements(),
        "recommended_next_step": "GEODESIC_TEST_VECTOR_FIXTURE_CREATION_READINESS_REVIEW",
    }

    serialized = canonical_dumps(preimage)
    result = json.loads(serialized)
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return _finalize(result)


def _validate_valid_plan(plan: list[dict[str, Any]]) -> None:
    ids = tuple(g["fixture_plan_id"] for g in plan)
    if ids != VALID_GROUP_IDS:
        raise GeodesicTestVectorFixturePlanValidationError(
            f"valid fixture plan group IDs must be {VALID_GROUP_IDS}, got {ids}"
        )
    for g in plan:
        if g.get("fixture_stage") not in ALLOWED_FIXTURE_STAGE:
            raise GeodesicTestVectorFixturePlanValidationError(
                f"invalid fixture_stage in valid group {g['fixture_plan_id']}"
            )
        if g.get("implementation_status") not in ALLOWED_IMPL_STATUS:
            raise GeodesicTestVectorFixturePlanValidationError(
                f"invalid implementation_status in valid group {g['fixture_plan_id']}"
            )


def _validate_invalid_plan(plan: list[dict[str, Any]]) -> None:
    ids = tuple(g["fixture_plan_id"] for g in plan)
    if ids != INVALID_GROUP_IDS:
        raise GeodesicTestVectorFixturePlanValidationError(
            f"invalid fixture plan group IDs must be {INVALID_GROUP_IDS}, got {ids}"
        )
    for g in plan:
        if g.get("invalid_reason") not in ALLOWED_INVALID_REASON:
            raise GeodesicTestVectorFixturePlanValidationError(
                f"invalid invalid_reason in group {g['fixture_plan_id']}"
            )


def _validate_nc_plan(plan: list[dict[str, Any]]) -> None:
    ids = tuple(g["fixture_plan_id"] for g in plan)
    if ids != NC_GROUP_IDS:
        raise GeodesicTestVectorFixturePlanValidationError(
            f"NC fixture plan group IDs must be {NC_GROUP_IDS}, got {ids}"
        )
    for g in plan:
        if g.get("not_computable_reason") not in ALLOWED_NC_REASON:
            raise GeodesicTestVectorFixturePlanValidationError(
                f"invalid not_computable_reason in group {g['fixture_plan_id']}"
            )
        if g.get("expected_state") not in ALLOWED_NC_STATE:
            raise GeodesicTestVectorFixturePlanValidationError(
                f"invalid expected_state in NC group {g['fixture_plan_id']}"
            )


def validate_fixture_plan(plan: dict[str, Any]) -> None:
    if plan.get("schema_version") != SCHEMA_VERSION:
        raise GeodesicTestVectorFixturePlanValidationError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if plan.get("fixture_plan_type") != FIXTURE_PLAN_TYPE:
        raise GeodesicTestVectorFixturePlanValidationError(
            f"fixture_plan_type must be {FIXTURE_PLAN_TYPE!r}"
        )
    if plan.get("operator_id") != OPERATOR_ID:
        raise GeodesicTestVectorFixturePlanValidationError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if plan.get("fixture_stage") not in ALLOWED_FIXTURE_STAGE:
        raise GeodesicTestVectorFixturePlanValidationError(
            f"fixture_stage must be one of {ALLOWED_FIXTURE_STAGE}"
        )
    if plan.get("intended_lane") not in ALLOWED_LANE:
        raise GeodesicTestVectorFixturePlanValidationError(
            f"intended_lane must be one of {ALLOWED_LANE}"
        )
    locks = plan.get("authority_locks", {})
    if locks.get("fixture_plan_only") is not True:
        raise GeodesicTestVectorFixturePlanValidationError(
            "authority_locks.fixture_plan_only must be True"
        )
    if locks.get("emits_metric_values") is not False:
        raise GeodesicTestVectorFixturePlanValidationError(
            "authority_locks.emits_metric_values must be False"
        )
    if locks.get("emits_expected_geodesic_distances") is not False:
        raise GeodesicTestVectorFixturePlanValidationError(
            "authority_locks.emits_expected_geodesic_distances must be False"
        )
    if locks.get("fixture_files_generated") is not False:
        raise GeodesicTestVectorFixturePlanValidationError(
            "authority_locks.fixture_files_generated must be False"
        )
    if plan.get("source_schema_plan_hash") != SOURCE_SCHEMA_PLAN_HASH:
        raise GeodesicTestVectorFixturePlanValidationError(
            "source_schema_plan_hash mismatch"
        )
    if plan.get("source_authorization_review_hash") != SOURCE_AUTHORIZATION_REVIEW_HASH:
        raise GeodesicTestVectorFixturePlanValidationError(
            "source_authorization_review_hash mismatch"
        )
    if len(plan.get("valid_fixture_plan", [])) != 5:
        raise GeodesicTestVectorFixturePlanValidationError(
            "valid_fixture_plan must contain exactly 5 groups"
        )
    if len(plan.get("invalid_fixture_plan", [])) != 4:
        raise GeodesicTestVectorFixturePlanValidationError(
            "invalid_fixture_plan must contain exactly 4 groups"
        )
    if len(plan.get("not_computable_fixture_plan", [])) != 4:
        raise GeodesicTestVectorFixturePlanValidationError(
            "not_computable_fixture_plan must contain exactly 4 groups"
        )
    h = plan.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise GeodesicTestVectorFixturePlanValidationError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(plan))
    if recomputed != h:
        raise GeodesicTestVectorFixturePlanValidationError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )
