from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "TransportComputationImplementationGate.v1"
GATE_ID = "transport_computation_implementation_gate_001"
GATE_STATUS = "TRANSPORT_COMPUTATION_IMPLEMENTATION_GATE_READY"
GATE_STAGE = "COMPUTATION_IMPLEMENTATION_GATE_ONLY"
OPERATOR_ID = "TRANSPORT"

SOURCE_DECISION_RECORD_HASH = (
    "2cd378187842043c93d4a66ed6e0f6a83b59cc1a3a8415c259abd70e5e1cb935"
)
SOURCE_OPERATOR_DECISION_HASH = (
    "eaa3006ac9e2f8433c588cf94a1a1a464744abc6b82e4a96da12c8d1759c1a6e"
)

DECISION_RECORD_PATH = pathlib.Path(
    "out/metric_operator/"
    "transport_implementation_authorization_decision_record_001.latest.json"
)
OPERATOR_DECISION_PATH = pathlib.Path(
    "input/transport_implementation_authorization_operator_decision.json"
)

REQUIRED_LOCKED_CONSTANT_KEYS = (
    "lp_solver_variant_declaration",
    "pivot_rule_declaration",
    "tie_breaking_rule_declaration",
    "balance_tolerance_declaration",
    "max_problem_size_declaration",
    "cost_matrix_magnitude_bound_declaration",
    "not_computable_branch_enumeration_confirmation",
)

EXPECTED_NOT_COMPUTABLE_BRANCHES = frozenset({
    "UNBALANCED_SUPPLY_DEMAND",
    "NEGATIVE_SUPPLY_VALUE",
    "NEGATIVE_COST_VALUE",
    "EMPTY_SUPPLY_VECTOR",
    "EMPTY_DEMAND_VECTOR",
    "NON_FINITE_SUPPLY_VALUE",
    "NON_FINITE_DEMAND_VALUE",
    "NON_FINITE_COST_VALUE",
    "COST_MATRIX_SHAPE_MISMATCH",
})

FORBIDDEN = (
    "executable", "callable", "runtime", "scheduler", "cache",
    "forecast", "scoring", "metric-computation", "metric-value",
    "geodesic-distance", "numpy", "scipy", "gpu-kernel",
    "dijkstra-execution", "shortest-path-computation",
    "fixture-file", "manifest-file", "schema-file",
)


class TransportComputationImplementationGateValidationError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise TransportComputationImplementationGateValidationError(
            "forbidden_token_detected_in_string_value"
        )


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def _verify_decision_record() -> dict[str, Any]:
    doc = json.loads(DECISION_RECORD_PATH.read_text())
    h = doc.get("canonical_hash", "")
    if h != SOURCE_DECISION_RECORD_HASH:
        raise TransportComputationImplementationGateValidationError(
            f"decision_record canonical_hash mismatch: stored={h!r}"
        )
    if doc.get("record_status") != "TRANSPORT_IMPLEMENTATION_AUTHORIZATION_DECISION_RECORDED":
        raise TransportComputationImplementationGateValidationError(
            "decision_record.record_status mismatch"
        )
    if doc.get("implementation_lane_authorized") != "TEST_VECTOR_COMPUTATION_ONLY":
        raise TransportComputationImplementationGateValidationError(
            "decision_record.implementation_lane_authorized mismatch"
        )
    if doc.get("baseline_target") != "SHADOW_STUB_ONLY":
        raise TransportComputationImplementationGateValidationError(
            "decision_record.baseline_target mismatch"
        )
    if doc.get("source_operator_decision_hash") != SOURCE_OPERATOR_DECISION_HASH:
        raise TransportComputationImplementationGateValidationError(
            "decision_record.source_operator_decision_hash mismatch"
        )
    lcr = doc.get("locked_constants_record", {})
    if lcr.get("all_locked_constants_present") is not True:
        raise TransportComputationImplementationGateValidationError(
            "decision_record.locked_constants_record.all_locked_constants_present must be True"
        )
    dvr = doc.get("decision_validation_review", {})
    if dvr.get("decision_valid") is not True:
        raise TransportComputationImplementationGateValidationError(
            "decision_record.decision_validation_review.decision_valid must be True"
        )
    bsar = doc.get("blocked_scope_acknowledgement_review", {})
    if bsar.get("all_acknowledgements_confirmed") is not True:
        raise TransportComputationImplementationGateValidationError(
            "decision_record.blocked_scope_acknowledgement_review"
            ".all_acknowledgements_confirmed must be True"
        )
    return doc


def _verify_operator_decision() -> dict[str, Any]:
    doc = json.loads(OPERATOR_DECISION_PATH.read_text())
    h = canonical_hash(doc)
    if h != SOURCE_OPERATOR_DECISION_HASH:
        raise TransportComputationImplementationGateValidationError(
            f"operator_decision canonical_hash mismatch: computed={h!r}"
        )
    if doc.get("decision") != "approve_transport_shadow_computation_implementation":
        raise TransportComputationImplementationGateValidationError(
            "operator_decision.decision mismatch"
        )
    if doc.get("implementation_lane_authorized") != "TEST_VECTOR_COMPUTATION_ONLY":
        raise TransportComputationImplementationGateValidationError(
            "operator_decision.implementation_lane_authorized mismatch"
        )
    if doc.get("authorization_granted") is not False:
        raise TransportComputationImplementationGateValidationError(
            "operator_decision.authorization_granted must be False"
        )
    return doc


def _build_locked_constants_binding(decision_record: dict[str, Any]) -> dict[str, Any]:
    lcr = decision_record.get("locked_constants_record", {})
    nc_branches = lcr.get("not_computable_branch_enumeration_confirmation", [])
    mps = lcr.get("max_problem_size_declaration", {})
    return {
        "lp_solver_variant_declaration": lcr.get("lp_solver_variant_declaration"),
        "pivot_rule_declaration": lcr.get("pivot_rule_declaration"),
        "tie_breaking_rule_declaration": lcr.get("tie_breaking_rule_declaration"),
        "balance_tolerance_declaration": lcr.get("balance_tolerance_declaration"),
        "max_problem_size_declaration": {
            "max_supply_length": mps.get("max_supply_length"),
            "max_demand_length": mps.get("max_demand_length"),
            "max_transport_variables": mps.get("max_transport_variables"),
        },
        "cost_matrix_magnitude_bound_declaration": lcr.get(
            "cost_matrix_magnitude_bound_declaration"
        ),
        "not_computable_branch_enumeration_confirmation": sorted(nc_branches),
        "all_constants_locked": True,
        "constants_count": 7,
    }


def build_authorized_implementation_scope(
    locked_constants: dict[str, Any],
) -> dict[str, Any]:
    return {
        "authorized_lane": "SHADOW",
        "authorized_computation_type": "TEST_VECTOR_COMPUTATION_ONLY",
        "authorized_algorithm": "DETERMINISTIC_ENUMERATED_BASIC_FEASIBLE_SEARCH",
        "transport_computation_implementation_authorized": True,
        "lp_solver_invocation_authorized_for_test_vectors": True,
        "bounded_scope_only": True,
        "locked_constants_binding": locked_constants,
        "implementation_notes": (
            "Bounded SHADOW test-vector computation authorized. "
            "Deterministic enumerated basic feasible search LP solver only. "
            "Max problem size 4x4 (16 transport variables). "
            "9 NOT_COMPUTABLE branches enumerated and sealed. "
            "No metric emission. No projection lane influence. No P43 lanes. "
            "LP solver invocation permitted for test vectors only within this scope."
        ),
    }


def build_no_metric_emission_block() -> dict[str, Any]:
    return {
        "emits_metric_values": False,
        "metric_emission_blocked": True,
        "block_confirmed": True,
        "block_finding": (
            "No metric values emitted by TRANSPORT computation implementation. "
            "Computed transport distances written to test-vector output only."
        ),
    }


def build_no_forecast_influence_block() -> dict[str, Any]:
    return {
        "forecast_influence": False,
        "forecast_influence_blocked": True,
        "block_confirmed": True,
        "block_finding": (
            "No projection lane influence. TRANSPORT computation implementation "
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
        "transport_computation_implementation_authorized": True,
        "lp_solver_invocation_authorized_for_test_vectors": True,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def validate_transport_computation_implementation_gate(gate: dict[str, Any]) -> None:
    if gate.get("schema_version") != SCHEMA_VERSION:
        raise TransportComputationImplementationGateValidationError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if gate.get("gate_status") != GATE_STATUS:
        raise TransportComputationImplementationGateValidationError(
            f"gate_status must be {GATE_STATUS!r}"
        )
    if gate.get("gate_stage") != GATE_STAGE:
        raise TransportComputationImplementationGateValidationError(
            f"gate_stage must be {GATE_STAGE!r}"
        )
    if gate.get("operator_id") != OPERATOR_ID:
        raise TransportComputationImplementationGateValidationError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if gate.get("source_decision_record_hash") != SOURCE_DECISION_RECORD_HASH:
        raise TransportComputationImplementationGateValidationError(
            "source_decision_record_hash mismatch"
        )
    if gate.get("source_operator_decision_hash") != SOURCE_OPERATOR_DECISION_HASH:
        raise TransportComputationImplementationGateValidationError(
            "source_operator_decision_hash mismatch"
        )
    locks = gate.get("authority_locks", {})
    for flag in (
        "advisory_only",
        "shadow_lane_only",
        "implementation_gate_only",
        "transport_computation_implementation_authorized",
        "lp_solver_invocation_authorized_for_test_vectors",
    ):
        if locks.get(flag) is not True:
            raise TransportComputationImplementationGateValidationError(
                f"authority_locks.{flag} must be True"
            )
    for flag in (
        "emits_metric_values",
        "forecast_influence",
        "p43_surface_lanes_authorized",
        "production_activation",
        "canon_promotion",
        "runtime_mutation",
        "execution_authority",
        "inference_authority",
    ):
        if locks.get(flag) is not False:
            raise TransportComputationImplementationGateValidationError(
                f"authority_locks.{flag} must be False"
            )
    auth = gate.get("authorized_implementation_scope", {})
    if auth.get("transport_computation_implementation_authorized") is not True:
        raise TransportComputationImplementationGateValidationError(
            "authorized_implementation_scope"
            ".transport_computation_implementation_authorized must be True"
        )
    if auth.get("lp_solver_invocation_authorized_for_test_vectors") is not True:
        raise TransportComputationImplementationGateValidationError(
            "authorized_implementation_scope"
            ".lp_solver_invocation_authorized_for_test_vectors must be True"
        )
    if auth.get("authorized_computation_type") != "TEST_VECTOR_COMPUTATION_ONLY":
        raise TransportComputationImplementationGateValidationError(
            "authorized_computation_type must be TEST_VECTOR_COMPUTATION_ONLY"
        )
    lc = auth.get("locked_constants_binding", {})
    if lc.get("all_constants_locked") is not True:
        raise TransportComputationImplementationGateValidationError(
            "locked_constants_binding.all_constants_locked must be True"
        )
    if lc.get("constants_count") != 7:
        raise TransportComputationImplementationGateValidationError(
            "locked_constants_binding.constants_count must be 7"
        )
    nc = lc.get("not_computable_branch_enumeration_confirmation", [])
    if set(nc) != EXPECTED_NOT_COMPUTABLE_BRANCHES:
        raise TransportComputationImplementationGateValidationError(
            f"not_computable_branch_enumeration_confirmation mismatch: {sorted(nc)!r}"
        )
    bs = gate.get("blocked_scopes", {})
    for flag in (
        "emits_metric_values",
        "forecast_influence",
        "p43_surface_lanes_authorized",
        "production_activation",
        "canon_promotion",
        "runtime_mutation",
        "execution_authority",
        "inference_authority",
    ):
        if bs.get(flag) is not False:
            raise TransportComputationImplementationGateValidationError(
                f"blocked_scopes.{flag} must be False"
            )
    h = gate.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise TransportComputationImplementationGateValidationError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(gate))
    if recomputed != h:
        raise TransportComputationImplementationGateValidationError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )


def build_transport_computation_implementation_gate(
    gate_id: str = GATE_ID,
    created_at_utc: str = "2026-05-30T00:00:00Z",
    intended_lane: str = "SHADOW",
) -> dict[str, Any]:
    decision_record = _verify_decision_record()
    _verify_operator_decision()

    locked_constants = _build_locked_constants_binding(decision_record)
    auth_scope = build_authorized_implementation_scope(locked_constants)
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
        "source_decision_record_hash": SOURCE_DECISION_RECORD_HASH,
        "source_operator_decision_hash": SOURCE_OPERATOR_DECISION_HASH,
        "locked_constants_binding": locked_constants,
        "authorized_implementation_scope": auth_scope,
        "no_metric_emission_block": no_metric,
        "no_forecast_influence_block": no_forecast,
        "no_p43_surface_lane_block": no_p43,
        "blocked_scopes": blocked,
        "authority_locks": locks,
        "recommended_next_step": "TRANSPORT_IMPLEMENTATION_AUTHORIZED_BOUNDED_SHADOW_COMPUTATION_PR",
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return _finalize(result)
