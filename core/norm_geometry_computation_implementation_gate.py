from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "NormGeometryComputationImplementationGate.v1"
GATE_ID = "norm_geometry_computation_implementation_gate_001"
GATE_STATUS = "NORM_GEOMETRY_COMPUTATION_IMPLEMENTATION_GATE_READY"
GATE_STAGE = "COMPUTATION_IMPLEMENTATION_GATE_ONLY"
OPERATOR_ID = "NORM_GEOMETRY"

SOURCE_CPU_BASELINE_PLAN_HASH = (
    "6fc421451f739bcf25769d3104e3ed2c0eef27ba1d77a36b00afce042fb63c57"
)
SOURCE_OPERATOR_DECISION_HASH = (
    "96b90cf6f06e2c78fe12b12ddb880a99839c67993c131d95f7d7578a04fa2bee"
)
SOURCE_AUTHORIZATION_PREP_HASH = (
    "445b2bf295ce52d53c2cd89691e4fec00226ba61ce5b0d4350e16d56b8f27a7b"
)
SOURCE_SCHEMA_PLAN_HASH = (
    "f6609b133ea3493b018aa3b9e56fbd3d42144979e37cbfb6c7d4e7408585c822"
)

CPU_BASELINE_PLAN_PATH = pathlib.Path(
    "out/metric_operator/"
    "norm_geometry_cpu_baseline_implementation_plan_001.latest.json"
)
OPERATOR_DECISION_PATH = pathlib.Path(
    "input/norm_geometry_implementation_authorization_operator_decision.json"
)
AUTHORIZATION_PREP_PATH = pathlib.Path(
    "out/metric_operator/implementation_authorization_prep_001.latest.json"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")

FORBIDDEN = (
    "executable", "callable", "runtime", "scheduler", "cache",
    "forecast", "scoring", "metric-computation", "metric-value",
    "geodesic-distance", "numpy", "scipy", "gpu-kernel",
    "dijkstra-execution", "shortest-path-computation",
    "fixture-file", "manifest-file", "schema-file",
)


class NormGeometryComputationImplementationGateValidationError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise NormGeometryComputationImplementationGateValidationError(
            "forbidden_token_detected_in_string_value"
        )


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def _verify_cpu_baseline_plan() -> dict[str, Any]:
    doc = json.loads(CPU_BASELINE_PLAN_PATH.read_text())
    if doc.get("canonical_hash") != SOURCE_CPU_BASELINE_PLAN_HASH:
        raise NormGeometryComputationImplementationGateValidationError(
            "cpu_baseline_plan canonical_hash mismatch"
        )
    return doc


def _verify_operator_decision() -> dict[str, Any]:
    doc = json.loads(OPERATOR_DECISION_PATH.read_text())
    h = canonical_hash(doc)
    if h != SOURCE_OPERATOR_DECISION_HASH:
        raise NormGeometryComputationImplementationGateValidationError(
            f"operator_decision canonical_hash mismatch: computed={h!r}"
        )
    if doc.get("decision") != "approve_norm_geometry_shadow_computation_implementation":
        raise NormGeometryComputationImplementationGateValidationError(
            "operator_decision.decision mismatch"
        )
    if doc.get("implementation_lane_authorized") != "TEST_VECTOR_COMPUTATION_ONLY":
        raise NormGeometryComputationImplementationGateValidationError(
            "operator_decision.implementation_lane_authorized mismatch"
        )
    if doc.get("authorization_granted") is not False:
        raise NormGeometryComputationImplementationGateValidationError(
            "operator_decision.authorization_granted must be false"
        )
    return doc


def _verify_authorization_prep() -> dict[str, Any]:
    doc = json.loads(AUTHORIZATION_PREP_PATH.read_text())
    if doc.get("canonical_hash") != SOURCE_AUTHORIZATION_PREP_HASH:
        raise NormGeometryComputationImplementationGateValidationError(
            "authorization_prep canonical_hash mismatch"
        )
    return doc


def _build_locked_constants_binding(decision: dict[str, Any]) -> dict[str, Any]:
    lc = decision.get("locked_constants", {})
    nc_branches = lc.get("not_computable_branch_enumeration_confirmation", [])
    return {
        "float64_precision_declaration": lc.get("float64_precision_declaration"),
        "p_inf_sentinel_value_declaration": lc.get("p_inf_sentinel_value_declaration"),
        "max_element_magnitude_declaration": lc.get("max_element_magnitude_declaration"),
        "max_p_value_declaration": lc.get("max_p_value_declaration"),
        "not_computable_branch_enumeration_confirmation": sorted(nc_branches),
        "all_constants_locked": True,
        "constants_count": 5,
    }


def build_authorized_implementation_scope(
    locked_constants: dict[str, Any],
) -> dict[str, Any]:
    return {
        "authorized_lane": "SHADOW",
        "authorized_computation_type": "TEST_VECTOR_COMPUTATION_ONLY",
        "authorized_fixture_corpus": "NORM_GEOMETRY_14_INLINE_FIXTURE_CORPUS",
        "authorized_algorithm": "CPU_REFERENCE_CLOSED_FORM_LP_NORM",
        "norm_geometry_computation_implementation_authorized": True,
        "bounded_scope_only": True,
        "locked_constants_binding": locked_constants,
        "implementation_notes": (
            "Bounded SHADOW test-vector computation authorized. "
            "CPU reference closed-form Lp norm only. "
            "14-inline-fixture corpus (6 valid, 4 invalid, 4 NOT_COMPUTABLE). "
            "No metric emission. No projection lane influence. No P43 lanes."
        ),
    }


def build_valid_fixture_scope() -> dict[str, Any]:
    return {
        "fixture_count": 6,
        "fixture_ids": [
            "ng.valid.v001_l1_norm",
            "ng.valid.v002_l2_norm",
            "ng.valid.v003_l_inf_norm",
            "ng.valid.v004_identical_vectors",
            "ng.valid.v005_general_lp_p3",
            "ng.valid.v006_single_element",
        ],
        "computation_authorized": True,
        "comparison_target_field": "expected_lp_distance",
        "output_field": "computed_lp_distance",
        "metric_emission_authorized": False,
        "forecast_influence_authorized": False,
    }


def build_rejection_fixture_scope() -> dict[str, Any]:
    return {
        "invalid_fixture_count": 4,
        "invalid_fixture_ids": [
            "ng.invalid.i001_missing_vector_x",
            "ng.invalid.i002_missing_vector_y",
            "ng.invalid.i003_missing_p_parameter",
            "ng.invalid.i004_mismatched_lengths",
        ],
        "invalid_rejection_outcome": "INVALID_INPUT",
        "not_computable_fixture_count": 4,
        "not_computable_fixture_ids": [
            "ng.nc.nc001_empty_vector",
            "ng.nc.nc002_p_below_minimum",
            "ng.nc.nc003_non_finite_element",
            "ng.nc.nc004_mismatched_vector_length",
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
            "No metric values emitted by NORM_GEOMETRY computation implementation. "
            "Computed Lp distances written to test-vector output only."
        ),
    }


def build_no_forecast_influence_block() -> dict[str, Any]:
    return {
        "forecast_influence": False,
        "forecast_influence_blocked": True,
        "block_confirmed": True,
        "block_finding": (
            "No projection lane influence. NORM_GEOMETRY computation implementation "
            "does not feed projection lanes."
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
        "norm_geometry_computation_implementation_authorized": True,
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
        raise NormGeometryComputationImplementationGateValidationError(
            f"intended_lane must be one of {ALLOWED_LANE}"
        )

    _verify_cpu_baseline_plan()
    decision = _verify_operator_decision()
    _verify_authorization_prep()

    locked_constants = _build_locked_constants_binding(decision)
    auth_scope = build_authorized_implementation_scope(locked_constants)
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
        "source_cpu_baseline_plan_hash": SOURCE_CPU_BASELINE_PLAN_HASH,
        "source_operator_decision_hash": SOURCE_OPERATOR_DECISION_HASH,
        "source_authorization_prep_hash": SOURCE_AUTHORIZATION_PREP_HASH,
        "source_schema_plan_hash": SOURCE_SCHEMA_PLAN_HASH,
        "authorized_implementation_scope": auth_scope,
        "valid_fixture_scope": valid_scope,
        "rejection_fixture_scope": rejection_scope,
        "no_metric_emission_block": no_metric,
        "no_forecast_influence_block": no_forecast,
        "no_p43_surface_lane_block": no_p43,
        "blocked_scopes": blocked,
        "authority_locks": locks,
        "recommended_next_step": "NORM_GEOMETRY_COMPUTATION_IMPLEMENTATION",
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return _finalize(result)


def validate_computation_implementation_gate(gate: dict[str, Any]) -> None:
    if gate.get("schema_version") != SCHEMA_VERSION:
        raise NormGeometryComputationImplementationGateValidationError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if gate.get("gate_status") != GATE_STATUS:
        raise NormGeometryComputationImplementationGateValidationError(
            f"gate_status must be {GATE_STATUS!r}"
        )
    if gate.get("gate_stage") != GATE_STAGE:
        raise NormGeometryComputationImplementationGateValidationError(
            f"gate_stage must be {GATE_STAGE!r}"
        )
    if gate.get("operator_id") != OPERATOR_ID:
        raise NormGeometryComputationImplementationGateValidationError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if gate.get("intended_lane") not in ALLOWED_LANE:
        raise NormGeometryComputationImplementationGateValidationError(
            f"intended_lane must be one of {ALLOWED_LANE}"
        )
    if gate.get("source_cpu_baseline_plan_hash") != SOURCE_CPU_BASELINE_PLAN_HASH:
        raise NormGeometryComputationImplementationGateValidationError(
            "source_cpu_baseline_plan_hash mismatch"
        )
    if gate.get("source_operator_decision_hash") != SOURCE_OPERATOR_DECISION_HASH:
        raise NormGeometryComputationImplementationGateValidationError(
            "source_operator_decision_hash mismatch"
        )
    if gate.get("source_authorization_prep_hash") != SOURCE_AUTHORIZATION_PREP_HASH:
        raise NormGeometryComputationImplementationGateValidationError(
            "source_authorization_prep_hash mismatch"
        )
    locks = gate.get("authority_locks", {})
    for flag in (
        "advisory_only", "shadow_lane_only", "implementation_gate_only",
        "norm_geometry_computation_implementation_authorized",
    ):
        if locks.get(flag) is not True:
            raise NormGeometryComputationImplementationGateValidationError(
                f"authority_locks.{flag} must be True"
            )
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        if locks.get(flag) is not False:
            raise NormGeometryComputationImplementationGateValidationError(
                f"authority_locks.{flag} must be False"
            )
    auth = gate.get("authorized_implementation_scope", {})
    if auth.get("norm_geometry_computation_implementation_authorized") is not True:
        raise NormGeometryComputationImplementationGateValidationError(
            "authorized_implementation_scope."
            "norm_geometry_computation_implementation_authorized must be True"
        )
    if auth.get("authorized_computation_type") != "TEST_VECTOR_COMPUTATION_ONLY":
        raise NormGeometryComputationImplementationGateValidationError(
            "authorized_computation_type must be TEST_VECTOR_COMPUTATION_ONLY"
        )
    lc = auth.get("locked_constants_binding", {})
    if lc.get("all_constants_locked") is not True:
        raise NormGeometryComputationImplementationGateValidationError(
            "locked_constants_binding.all_constants_locked must be True"
        )
    if lc.get("constants_count") != 5:
        raise NormGeometryComputationImplementationGateValidationError(
            "locked_constants_binding.constants_count must be 5"
        )
    bs = gate.get("blocked_scopes", {})
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        if bs.get(flag) is not False:
            raise NormGeometryComputationImplementationGateValidationError(
                f"blocked_scopes.{flag} must be False"
            )
    h = gate.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise NormGeometryComputationImplementationGateValidationError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(gate))
    if recomputed != h:
        raise NormGeometryComputationImplementationGateValidationError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )
