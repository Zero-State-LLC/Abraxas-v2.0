from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "GeodesicComputationImplementationPlan.v1"
PLAN_ID = "geodesic_computation_implementation_plan_001"
PLAN_STATUS = "GEODESIC_COMPUTATION_IMPLEMENTATION_PLAN_DEFINED"
IMPLEMENTATION_STAGE = "IMPLEMENTATION_PLAN_ONLY"
OPERATOR_ID = "GEODESIC"

SOURCE_OPERATOR_DECISION_HASH = (
    "f73af2e76de5193ecf61e3f33037db6b1d01099393c83aba43ff8568f31c8d4a"
)
SOURCE_AUTHORIZATION_REVIEW_HASH = (
    "623418c5d09d26c8371e8d2db3d06f4f377cf7a031b54af3a46c4d194c35d2b3"
)
SOURCE_COMPLETE_REVIEW_HASH = (
    "6725e3c494726bae452619e2b0e235a25761aea27262668a1548cd62d5feeb5a"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")

OPERATOR_DECISION_PATH = pathlib.Path(
    "input/geodesic_computation_operator_decision.json"
)
AUTHORIZATION_REVIEW_PATH = pathlib.Path(
    "out/metric_operator/geodesic_computation_authorization_review_001.latest.json"
)
COMPLETE_REVIEW_PATH = pathlib.Path(
    "out/metric_operator/geodesic_expected_values_complete_review_001.latest.json"
)

FORBIDDEN = (
    "geodesic-distance",
    "dijkstra-execution",
    "shortest-path-computation",
    "metric-value",
    "metric-computation",
    "fixture-file",
    "manifest-file",
    "schema-file",
    "numpy",
    "scipy",
    "gpu-kernel",
)


class GeodesicComputationImplementationPlanValidationError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise GeodesicComputationImplementationPlanValidationError(
            "forbidden_token_detected_in_string_value"
        )


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def _verify_operator_decision() -> None:
    doc = json.loads(OPERATOR_DECISION_PATH.read_text())
    actual = canonical_hash(doc)
    if actual != SOURCE_OPERATOR_DECISION_HASH:
        raise GeodesicComputationImplementationPlanValidationError(
            f"operator_decision canonical_hash mismatch: {actual!r}"
        )
    if doc.get("decision") != "approve_geodesic_shadow_computation":
        raise GeodesicComputationImplementationPlanValidationError(
            "operator_decision.decision must be approve_geodesic_shadow_computation"
        )
    if doc.get("computation_lane_authorized") != "TEST_VECTOR_COMPUTATION_ONLY":
        raise GeodesicComputationImplementationPlanValidationError(
            "operator_decision.computation_lane_authorized must be TEST_VECTOR_COMPUTATION_ONLY"
        )


def _verify_authorization_review() -> None:
    doc = json.loads(AUTHORIZATION_REVIEW_PATH.read_text())
    if doc.get("canonical_hash") != SOURCE_AUTHORIZATION_REVIEW_HASH:
        raise GeodesicComputationImplementationPlanValidationError(
            "authorization_review canonical_hash mismatch"
        )


def _verify_complete_review() -> None:
    doc = json.loads(COMPLETE_REVIEW_PATH.read_text())
    if doc.get("canonical_hash") != SOURCE_COMPLETE_REVIEW_HASH:
        raise GeodesicComputationImplementationPlanValidationError(
            "complete_review canonical_hash mismatch"
        )


def build_algorithm_plan() -> dict[str, Any]:
    return {
        "algorithm_family": "CPU_REFERENCE_SHORTEST_PATH",
        "implementation_constraint": "CPU_ONLY_NO_GPU",
        "graph_representation": "ADJACENCY_LIST_FROM_EDGE_LIST",
        "traversal_strategy": "SINGLE_SOURCE_SINGLE_TARGET_SHORTEST_PATH",
        "edge_weight_handling": "POSITIVE_WEIGHTS_ONLY",
        "negative_weight_policy": "REJECT_AS_INVALID_INPUT",
        "self_loop_handling": "ZERO_DISTANCE_IF_SOURCE_EQUALS_TARGET",
        "unweighted_graph_handling": "UNIT_WEIGHT_PER_HOP",
        "graph_parsing_policy": "DETERMINISTIC_SORTED_EDGE_ORDER",
        "runtime_metric_emission": False,
        "gpu_kernel_authorized": False,
        "external_library_authorized": False,
        "shadow_stub_only": True,
        "plan_notes": (
            "CPU reference implementation only. "
            "Graph parsed deterministically from sorted edge list. "
            "Negative edge weights cause INVALID rejection. "
            "Source equals target returns distance zero. "
            "Unweighted edges treated as unit weight. "
            "No runtime metric emission. No GPU. No external solver."
        ),
    }


def build_supported_fixture_scope() -> dict[str, Any]:
    return {
        "total_fixture_count": 13,
        "valid_fixture_count": 5,
        "invalid_fixture_count": 4,
        "not_computable_fixture_count": 4,
        "computation_applies_to": "VALID_FIXTURES_ONLY",
        "invalid_fixtures_rejected_before_computation": True,
        "not_computable_fixtures_rejected_before_computation": True,
        "fixture_corpus_source": "geodesic_expected_values_complete_review_001",
    }


def build_valid_fixture_computation_plan() -> dict[str, Any]:
    return {
        "fixture_ids": [
            "geodesic.valid.valid_001_simple_connected_weighted_graph.v1",
            "geodesic.valid.valid_002_multi_hop_graph.v1",
            "geodesic.valid.valid_003_self_loop.v1",
            "geodesic.valid.valid_004_unweighted_graph.v1",
            "geodesic.valid.valid_005_complete_graph.v1",
        ],
        "computation_steps": [
            "parse_graph_from_edge_list_deterministically",
            "validate_all_edge_weights_positive_or_zero",
            "check_source_equals_target_for_zero_distance",
            "run_cpu_reference_shortest_path",
            "return_computed_distance_as_float",
        ],
        "output_field": "computed_geodesic_distance",
        "expected_field": "expected_geodesic_distance",
        "comparison_applies": True,
        "metric_emission_applies": False,
        "forecast_influence_applies": False,
    }


def build_invalid_fixture_rejection_plan() -> dict[str, Any]:
    return {
        "fixture_ids": [
            "geodesic.invalid.invalid_001_missing_source_node.v1",
            "geodesic.invalid.invalid_002_missing_target_node.v1",
            "geodesic.invalid.invalid_003_missing_edge_list.v1",
            "geodesic.invalid.invalid_004_negative_edge_weight.v1",
        ],
        "rejection_triggers": [
            "missing_source_node",
            "missing_target_node",
            "missing_edge_list",
            "negative_edge_weight_present",
        ],
        "rejection_outcome": "INVALID_INPUT",
        "computation_attempted": False,
        "rejection_confirmed_before_computation": True,
    }


def build_not_computable_fixture_rejection_plan() -> dict[str, Any]:
    return {
        "fixture_ids": [
            "geodesic.not_computable.nc_001_empty_graph.v1",
            "geodesic.not_computable.nc_002_disconnected_graph.v1",
            "geodesic.not_computable.nc_003_source_not_in_graph.v1",
            "geodesic.not_computable.nc_004_target_not_in_graph.v1",
        ],
        "not_computable_triggers": [
            "empty_graph_no_nodes",
            "source_and_target_not_connected",
            "source_node_not_in_graph",
            "target_node_not_in_graph",
        ],
        "not_computable_outcome": "NOT_COMPUTABLE",
        "computation_attempted": False,
        "not_computable_confirmed_before_computation": True,
    }


def build_deterministic_ordering_policy() -> dict[str, Any]:
    return {
        "edge_list_sort_key": "source_node_then_target_node_then_weight",
        "node_id_type": "STRING_LEXICOGRAPHIC",
        "tie_breaking": "LEXICOGRAPHIC_NODE_ID_ORDER",
        "graph_construction_order": "SORTED_EDGE_LIST",
        "adjacency_representation": "SORTED_ADJACENCY_LIST",
        "determinism_guarantee": True,
        "policy_notes": (
            "All graph structures built from sorted edge lists. "
            "Ties in distance broken by lexicographic node ID order. "
            "Output is deterministic given identical input."
        ),
    }


def build_numerical_policy() -> dict[str, Any]:
    return {
        "distance_type": "FLOAT64",
        "zero_distance_representation": 0.0,
        "infinity_representation": "NOT_COMPUTABLE_OUTCOME",
        "negative_weight_policy": "REJECT_BEFORE_COMPUTATION",
        "precision_standard": "IEEE_754_DOUBLE",
        "rounding_policy": "NO_ROUNDING_AT_COMPUTATION",
        "emission_policy": "NO_METRIC_EMISSION",
    }


def build_comparison_policy() -> dict[str, Any]:
    return {
        "comparison_target_field": "expected_geodesic_distance",
        "comparison_computed_field": "computed_geodesic_distance",
        "comparison_method": "EXACT_FLOAT64_EQUALITY",
        "tolerance": 0.0,
        "pass_outcome": "COMPUTATION_MATCHES_EXPECTED",
        "fail_outcome": "COMPUTATION_DIVERGES_FROM_EXPECTED",
        "comparison_applies_to": "VALID_FIXTURES_ONLY",
        "metric_emission_on_comparison": False,
        "forecast_influence_on_comparison": False,
    }


def build_blocked_scopes() -> dict[str, Any]:
    return {
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
        "geodesic_computation_implementation_authorized": False,
    }


def build_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "implementation_plan_only": True,
        "expected_geodesic_distances_authorized": True,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
        "geodesic_computation_implementation_authorized": False,
    }


def build_computation_implementation_plan(
    plan_id: str = PLAN_ID,
    created_at_utc: str = "2026-05-30T00:00:00Z",
    intended_lane: str = "SHADOW",
) -> dict[str, Any]:
    if intended_lane not in ALLOWED_LANE:
        raise GeodesicComputationImplementationPlanValidationError(
            f"intended_lane must be one of {ALLOWED_LANE}"
        )

    _verify_operator_decision()
    _verify_authorization_review()
    _verify_complete_review()

    preimage: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "plan_id": plan_id,
        "operator_id": OPERATOR_ID,
        "plan_status": PLAN_STATUS,
        "implementation_stage": IMPLEMENTATION_STAGE,
        "created_at_utc": created_at_utc,
        "intended_lane": intended_lane,
        "source_operator_decision_hash": SOURCE_OPERATOR_DECISION_HASH,
        "source_computation_authorization_review_hash": SOURCE_AUTHORIZATION_REVIEW_HASH,
        "source_expected_values_complete_review_hash": SOURCE_COMPLETE_REVIEW_HASH,
        "algorithm_plan": build_algorithm_plan(),
        "supported_fixture_scope": build_supported_fixture_scope(),
        "valid_fixture_computation_plan": build_valid_fixture_computation_plan(),
        "invalid_fixture_rejection_plan": build_invalid_fixture_rejection_plan(),
        "not_computable_fixture_rejection_plan": build_not_computable_fixture_rejection_plan(),
        "deterministic_ordering_policy": build_deterministic_ordering_policy(),
        "numerical_policy": build_numerical_policy(),
        "comparison_policy": build_comparison_policy(),
        "blocked_scopes": build_blocked_scopes(),
        "authority_locks": build_authority_locks(),
        "recommended_next_step": "GEODESIC_COMPUTATION_IMPLEMENTATION_GATE",
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return _finalize(result)


def validate_computation_implementation_plan(plan: dict[str, Any]) -> None:
    if plan.get("schema_version") != SCHEMA_VERSION:
        raise GeodesicComputationImplementationPlanValidationError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if plan.get("plan_status") != PLAN_STATUS:
        raise GeodesicComputationImplementationPlanValidationError(
            f"plan_status must be {PLAN_STATUS!r}"
        )
    if plan.get("implementation_stage") != IMPLEMENTATION_STAGE:
        raise GeodesicComputationImplementationPlanValidationError(
            f"implementation_stage must be {IMPLEMENTATION_STAGE!r}"
        )
    if plan.get("operator_id") != OPERATOR_ID:
        raise GeodesicComputationImplementationPlanValidationError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if plan.get("intended_lane") not in ALLOWED_LANE:
        raise GeodesicComputationImplementationPlanValidationError(
            f"intended_lane must be one of {ALLOWED_LANE}"
        )
    if plan.get("source_operator_decision_hash") != SOURCE_OPERATOR_DECISION_HASH:
        raise GeodesicComputationImplementationPlanValidationError(
            "source_operator_decision_hash mismatch"
        )
    if plan.get("source_computation_authorization_review_hash") != SOURCE_AUTHORIZATION_REVIEW_HASH:
        raise GeodesicComputationImplementationPlanValidationError(
            "source_computation_authorization_review_hash mismatch"
        )
    if plan.get("source_expected_values_complete_review_hash") != SOURCE_COMPLETE_REVIEW_HASH:
        raise GeodesicComputationImplementationPlanValidationError(
            "source_expected_values_complete_review_hash mismatch"
        )
    locks = plan.get("authority_locks", {})
    for flag in ("advisory_only", "shadow_lane_only", "implementation_plan_only",
                 "expected_geodesic_distances_authorized"):
        if locks.get(flag) is not True:
            raise GeodesicComputationImplementationPlanValidationError(
                f"authority_locks.{flag} must be True"
            )
    for flag in ("emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
                 "production_activation", "canon_promotion", "runtime_mutation",
                 "execution_authority", "inference_authority",
                 "geodesic_computation_implementation_authorized"):
        if locks.get(flag) is not False:
            raise GeodesicComputationImplementationPlanValidationError(
                f"authority_locks.{flag} must be False"
            )
    scope = plan.get("supported_fixture_scope", {})
    if scope.get("total_fixture_count") != 13:
        raise GeodesicComputationImplementationPlanValidationError(
            "supported_fixture_scope.total_fixture_count must be 13"
        )
    if scope.get("valid_fixture_count") != 5:
        raise GeodesicComputationImplementationPlanValidationError(
            "supported_fixture_scope.valid_fixture_count must be 5"
        )
    vcp = plan.get("valid_fixture_computation_plan", {})
    if len(vcp.get("fixture_ids", [])) != 5:
        raise GeodesicComputationImplementationPlanValidationError(
            "valid_fixture_computation_plan.fixture_ids must contain 5 entries"
        )
    if vcp.get("metric_emission_applies") is not False:
        raise GeodesicComputationImplementationPlanValidationError(
            "valid_fixture_computation_plan.metric_emission_applies must be False"
        )
    alg = plan.get("algorithm_plan", {})
    if alg.get("runtime_metric_emission") is not False:
        raise GeodesicComputationImplementationPlanValidationError(
            "algorithm_plan.runtime_metric_emission must be False"
        )
    if alg.get("gpu_kernel_authorized") is not False:
        raise GeodesicComputationImplementationPlanValidationError(
            "algorithm_plan.gpu_kernel_authorized must be False"
        )
    bs = plan.get("blocked_scopes", {})
    if bs.get("geodesic_computation_implementation_authorized") is not False:
        raise GeodesicComputationImplementationPlanValidationError(
            "blocked_scopes.geodesic_computation_implementation_authorized must be False"
        )
    h = plan.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise GeodesicComputationImplementationPlanValidationError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(plan))
    if recomputed != h:
        raise GeodesicComputationImplementationPlanValidationError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )
