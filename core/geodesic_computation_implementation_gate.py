from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "GeodesicComputationImplementationGate.v1"
GATE_ID = "geodesic_computation_implementation_gate_001"
GATE_STATUS = "GEODESIC_COMPUTATION_IMPLEMENTATION_GATE_READY"
GATE_STAGE = "COMPUTATION_IMPLEMENTATION_GATE_ONLY"
OPERATOR_ID = "GEODESIC"

SOURCE_IMPLEMENTATION_PLAN_HASH = (
    "9a5c2bebf5102bfaedc72a089361f69cb463bd12f21ff017994aa43d55c62491"
)
SOURCE_OPERATOR_DECISION_HASH = (
    "f73af2e76de5193ecf61e3f33037db6b1d01099393c83aba43ff8568f31c8d4a"
)
SOURCE_AUTHORIZATION_REVIEW_HASH = (
    "623418c5d09d26c8371e8d2db3d06f4f377cf7a031b54af3a46c4d194c35d2b3"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")

IMPLEMENTATION_PLAN_PATH = pathlib.Path(
    "out/metric_operator/geodesic_computation_implementation_plan_001.latest.json"
)
OPERATOR_DECISION_PATH = pathlib.Path(
    "input/geodesic_computation_operator_decision.json"
)
AUTHORIZATION_REVIEW_PATH = pathlib.Path(
    "out/metric_operator/geodesic_computation_authorization_review_001.latest.json"
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


class GeodesicComputationImplementationGateValidationError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise GeodesicComputationImplementationGateValidationError(
            "forbidden_token_detected_in_string_value"
        )


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def _verify_implementation_plan() -> dict[str, Any]:
    doc = json.loads(IMPLEMENTATION_PLAN_PATH.read_text())
    if doc.get("canonical_hash") != SOURCE_IMPLEMENTATION_PLAN_HASH:
        raise GeodesicComputationImplementationGateValidationError(
            "implementation_plan canonical_hash mismatch"
        )
    if doc.get("plan_status") != "GEODESIC_COMPUTATION_IMPLEMENTATION_PLAN_DEFINED":
        raise GeodesicComputationImplementationGateValidationError(
            "implementation_plan plan_status mismatch"
        )
    return doc


def _verify_operator_decision() -> None:
    doc = json.loads(OPERATOR_DECISION_PATH.read_text())
    if canonical_hash(doc) != SOURCE_OPERATOR_DECISION_HASH:
        raise GeodesicComputationImplementationGateValidationError(
            "operator_decision canonical_hash mismatch"
        )
    if doc.get("decision") != "approve_geodesic_shadow_computation":
        raise GeodesicComputationImplementationGateValidationError(
            "operator_decision.decision mismatch"
        )


def _verify_authorization_review() -> None:
    doc = json.loads(AUTHORIZATION_REVIEW_PATH.read_text())
    if doc.get("canonical_hash") != SOURCE_AUTHORIZATION_REVIEW_HASH:
        raise GeodesicComputationImplementationGateValidationError(
            "authorization_review canonical_hash mismatch"
        )


def build_implementation_plan_review(plan: dict[str, Any]) -> dict[str, Any]:
    alg = plan.get("algorithm_plan", {})
    scope = plan.get("supported_fixture_scope", {})
    return {
        "plan_id_confirmed": plan.get("plan_id"),
        "plan_status_confirmed": plan.get("plan_status"),
        "algorithm_family_confirmed": alg.get("algorithm_family"),
        "cpu_only_confirmed": alg.get("implementation_constraint") == "CPU_ONLY_NO_GPU",
        "no_gpu_confirmed": alg.get("gpu_kernel_authorized") is False,
        "no_external_library_confirmed": alg.get("external_library_authorized") is False,
        "no_runtime_metric_emission_confirmed": alg.get("runtime_metric_emission") is False,
        "negative_weight_rejection_confirmed": (
            alg.get("negative_weight_policy") == "REJECT_AS_INVALID_INPUT"
        ),
        "self_loop_zero_distance_confirmed": (
            alg.get("self_loop_handling") == "ZERO_DISTANCE_IF_SOURCE_EQUALS_TARGET"
        ),
        "determinism_guaranteed_confirmed": plan.get(
            "deterministic_ordering_policy", {}
        ).get("determinism_guarantee") is True,
        "total_fixture_count_confirmed": scope.get("total_fixture_count") == 13,
        "valid_fixture_count_confirmed": scope.get("valid_fixture_count") == 5,
        "plan_review_passed": True,
    }


def build_authorized_implementation_scope() -> dict[str, Any]:
    return {
        "authorized_lane": "SHADOW",
        "authorized_computation_type": "TEST_VECTOR_COMPUTATION_ONLY",
        "authorized_fixture_corpus": "GEODESIC_13_FIXTURE_CORPUS",
        "authorized_algorithm": "CPU_REFERENCE_SHORTEST_PATH",
        "geodesic_computation_implementation_authorized": True,
        "bounded_scope_only": True,
        "implementation_notes": (
            "Bounded SHADOW test-vector computation authorized. "
            "CPU reference only. 13-fixture corpus only. "
            "No metric emission. No forecast influence. No P43 lanes."
        ),
    }


def build_valid_fixture_scope() -> dict[str, Any]:
    return {
        "fixture_count": 5,
        "fixture_ids": [
            "geodesic.valid.valid_001_simple_connected_weighted_graph.v1",
            "geodesic.valid.valid_002_multi_hop_graph.v1",
            "geodesic.valid.valid_003_self_loop.v1",
            "geodesic.valid.valid_004_unweighted_graph.v1",
            "geodesic.valid.valid_005_complete_graph.v1",
        ],
        "computation_authorized": True,
        "comparison_target_field": "expected_geodesic_distance",
        "output_field": "computed_geodesic_distance",
        "metric_emission_authorized": False,
        "forecast_influence_authorized": False,
    }


def build_rejection_fixture_scope() -> dict[str, Any]:
    return {
        "invalid_fixture_count": 4,
        "invalid_fixture_ids": [
            "geodesic.invalid.invalid_001_missing_source_node.v1",
            "geodesic.invalid.invalid_002_missing_target_node.v1",
            "geodesic.invalid.invalid_003_missing_edge_list.v1",
            "geodesic.invalid.invalid_004_negative_edge_weight.v1",
        ],
        "invalid_rejection_outcome": "INVALID_INPUT",
        "not_computable_fixture_count": 4,
        "not_computable_fixture_ids": [
            "geodesic.not_computable.nc_001_empty_graph.v1",
            "geodesic.not_computable.nc_002_disconnected_graph.v1",
            "geodesic.not_computable.nc_003_source_not_in_graph.v1",
            "geodesic.not_computable.nc_004_target_not_in_graph.v1",
        ],
        "not_computable_rejection_outcome": "NOT_COMPUTABLE",
        "computation_attempted_on_rejected": False,
    }


def build_no_metric_emission_block() -> dict[str, Any]:
    return {
        "emits_metric_values": False,
        "metric_emission_blocked": True,
        "block_confirmed": True,
        "block_finding": (
            "No runtime metric values emitted by GEODESIC computation implementation. "
            "Computed distances written to test-vector output only."
        ),
    }


def build_no_forecast_influence_block() -> dict[str, Any]:
    return {
        "forecast_influence": False,
        "forecast_influence_blocked": True,
        "block_confirmed": True,
        "block_finding": (
            "No forecast influence. GEODESIC computation implementation "
            "does not feed forecast lanes."
        ),
    }


def build_no_p43_surface_lane_block() -> dict[str, Any]:
    return {
        "p43_surface_lanes_authorized": False,
        "p43_blocked": True,
        "block_confirmed": True,
        "block_finding": "P43 surface lanes remain unauthorized by this gate.",
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
    }


def build_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "implementation_gate_only": True,
        "geodesic_computation_implementation_authorized": True,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def build_computation_implementation_gate(
    gate_id: str = GATE_ID,
    created_at_utc: str = "2026-05-30T00:00:00Z",
    intended_lane: str = "SHADOW",
) -> dict[str, Any]:
    if intended_lane not in ALLOWED_LANE:
        raise GeodesicComputationImplementationGateValidationError(
            f"intended_lane must be one of {ALLOWED_LANE}"
        )

    plan = _verify_implementation_plan()
    _verify_operator_decision()
    _verify_authorization_review()

    plan_review = build_implementation_plan_review(plan)
    auth_scope = build_authorized_implementation_scope()
    valid_scope = build_valid_fixture_scope()
    rejection_scope = build_rejection_fixture_scope()
    no_metric = build_no_metric_emission_block()
    no_forecast = build_no_forecast_influence_block()
    no_p43 = build_no_p43_surface_lane_block()
    blocked = build_blocked_scopes()
    locks = build_authority_locks()

    preimage: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "gate_id": gate_id,
        "operator_id": OPERATOR_ID,
        "gate_status": GATE_STATUS,
        "gate_stage": GATE_STAGE,
        "created_at_utc": created_at_utc,
        "intended_lane": intended_lane,
        "source_implementation_plan_hash": SOURCE_IMPLEMENTATION_PLAN_HASH,
        "source_operator_decision_hash": SOURCE_OPERATOR_DECISION_HASH,
        "source_computation_authorization_review_hash": SOURCE_AUTHORIZATION_REVIEW_HASH,
        "implementation_plan_review": plan_review,
        "authorized_implementation_scope": auth_scope,
        "valid_fixture_scope": valid_scope,
        "rejection_fixture_scope": rejection_scope,
        "no_metric_emission_block": no_metric,
        "no_forecast_influence_block": no_forecast,
        "no_p43_surface_lane_block": no_p43,
        "blocked_scopes": blocked,
        "authority_locks": locks,
        "recommended_next_step": "GEODESIC_COMPUTATION_IMPLEMENTATION",
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return _finalize(result)


def validate_computation_implementation_gate(gate: dict[str, Any]) -> None:
    if gate.get("schema_version") != SCHEMA_VERSION:
        raise GeodesicComputationImplementationGateValidationError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if gate.get("gate_status") != GATE_STATUS:
        raise GeodesicComputationImplementationGateValidationError(
            f"gate_status must be {GATE_STATUS!r}"
        )
    if gate.get("gate_stage") != GATE_STAGE:
        raise GeodesicComputationImplementationGateValidationError(
            f"gate_stage must be {GATE_STAGE!r}"
        )
    if gate.get("operator_id") != OPERATOR_ID:
        raise GeodesicComputationImplementationGateValidationError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if gate.get("intended_lane") not in ALLOWED_LANE:
        raise GeodesicComputationImplementationGateValidationError(
            f"intended_lane must be one of {ALLOWED_LANE}"
        )
    if gate.get("source_implementation_plan_hash") != SOURCE_IMPLEMENTATION_PLAN_HASH:
        raise GeodesicComputationImplementationGateValidationError(
            "source_implementation_plan_hash mismatch"
        )
    if gate.get("source_operator_decision_hash") != SOURCE_OPERATOR_DECISION_HASH:
        raise GeodesicComputationImplementationGateValidationError(
            "source_operator_decision_hash mismatch"
        )
    if gate.get("source_computation_authorization_review_hash") != SOURCE_AUTHORIZATION_REVIEW_HASH:
        raise GeodesicComputationImplementationGateValidationError(
            "source_computation_authorization_review_hash mismatch"
        )
    locks = gate.get("authority_locks", {})
    for flag in ("advisory_only", "shadow_lane_only", "implementation_gate_only",
                 "geodesic_computation_implementation_authorized"):
        if locks.get(flag) is not True:
            raise GeodesicComputationImplementationGateValidationError(
                f"authority_locks.{flag} must be True"
            )
    for flag in ("emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
                 "production_activation", "canon_promotion", "runtime_mutation",
                 "execution_authority", "inference_authority"):
        if locks.get(flag) is not False:
            raise GeodesicComputationImplementationGateValidationError(
                f"authority_locks.{flag} must be False"
            )
    auth = gate.get("authorized_implementation_scope", {})
    if auth.get("geodesic_computation_implementation_authorized") is not True:
        raise GeodesicComputationImplementationGateValidationError(
            "authorized_implementation_scope.geodesic_computation_implementation_authorized must be True"
        )
    if auth.get("authorized_computation_type") != "TEST_VECTOR_COMPUTATION_ONLY":
        raise GeodesicComputationImplementationGateValidationError(
            "authorized_implementation_scope.authorized_computation_type must be TEST_VECTOR_COMPUTATION_ONLY"
        )
    bs = gate.get("blocked_scopes", {})
    for flag in ("emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
                 "production_activation", "canon_promotion", "runtime_mutation",
                 "execution_authority", "inference_authority"):
        if bs.get(flag) is not False:
            raise GeodesicComputationImplementationGateValidationError(
                f"blocked_scopes.{flag} must be False"
            )
    pr = gate.get("implementation_plan_review", {})
    if pr.get("plan_review_passed") is not True:
        raise GeodesicComputationImplementationGateValidationError(
            "implementation_plan_review.plan_review_passed must be True"
        )
    h = gate.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise GeodesicComputationImplementationGateValidationError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(gate))
    if recomputed != h:
        raise GeodesicComputationImplementationGateValidationError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )
