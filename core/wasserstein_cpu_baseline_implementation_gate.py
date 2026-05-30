"""WassersteinCpuBaselineImplementationGate.v1 — operator gate artifact builder."""
from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinCpuBaselineImplementationGate.v1"
GATE_ID = "wasserstein_cpu_baseline_implementation_gate_001"
GATE_STATUS = "WASSERSTEIN_CPU_BASELINE_IMPLEMENTATION_GATE_READY"
GATE_STAGE = "COMPUTATION_IMPLEMENTATION_GATE_ONLY"
OPERATOR_ID = "WASSERSTEIN"

SOURCE_OPERATOR_DECISION_HASH = (
    "c110a945ec7c8b395d9d12af11cd0ed06ebc6182a272198fdd7617a54bcdab0a"
)

OPERATOR_DECISION_PATH = pathlib.Path(
    "input/wasserstein_cpu_baseline_implementation_authorization_operator_decision.json"
)

FIXTURE_DIR = pathlib.Path("input/fixtures/wasserstein")

REQUIRED_LOCKED_CONSTANT_KEYS = (
    "solver_policy",
    "supported_fixture_scope",
    "float64_precision_declaration",
    "balance_tolerance_declaration",
    "max_distribution_length_declaration",
    "max_coordinate_magnitude_declaration",
    "not_computable_branch_enumeration_confirmation",
)

EXPECTED_SOLVER_POLICY = "DETERMINISTIC_1D_SORTED_CDF_TRANSPORT_ONLY"
EXPECTED_FIXTURE_SCOPE = "EXISTING_WASSERSTEIN_TEST_VECTOR_FIXTURES_ONLY"
EXPECTED_FLOAT64_DECLARATION = "IEEE_754_BINARY64_REQUIRED"
EXPECTED_IMPLEMENTATION_LANE = "TEST_VECTOR_COMPUTATION_ONLY"
EXPECTED_BASELINE_TARGET = "SHADOW_STUB_ONLY"

EXPECTED_NOT_COMPUTABLE_BRANCHES = frozenset({
    "EMPTY_DISTRIBUTION",
    "UNBALANCED_MASS",
    "NEGATIVE_MASS",
    "NON_FINITE_WEIGHT",
    "NON_FINITE_COORDINATE",
    "MISSING_REQUIRED_FIELD",
    "MISMATCHED_SUPPORT_WEIGHT_LENGTH",
})

FORBIDDEN = (
    "executable", "callable", "runtime", "scheduler", "cache",
    "forecast", "scoring", "metric-computation", "metric-value",
    "geodesic-distance", "numpy", "scipy", "gpu-kernel",
    "dijkstra-execution", "shortest-path-computation",
    "fixture-file", "manifest-file", "schema-file",
)


class WassersteinCpuBaselineImplementationGateValidationError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise WassersteinCpuBaselineImplementationGateValidationError(
            "forbidden_token_detected_in_string_value"
        )


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _verify_operator_decision() -> dict[str, Any]:
    doc = json.loads(OPERATOR_DECISION_PATH.read_text())
    h = canonical_hash(doc)
    if h != SOURCE_OPERATOR_DECISION_HASH:
        raise WassersteinCpuBaselineImplementationGateValidationError(
            f"operator_decision canonical_hash mismatch: computed={h!r}"
        )
    if doc.get("decision") != "approve_wasserstein_shadow_cpu_baseline_implementation":
        raise WassersteinCpuBaselineImplementationGateValidationError(
            "operator_decision.decision mismatch"
        )
    if doc.get("implementation_lane_authorized") != EXPECTED_IMPLEMENTATION_LANE:
        raise WassersteinCpuBaselineImplementationGateValidationError(
            "operator_decision.implementation_lane_authorized mismatch"
        )
    if doc.get("baseline_target") != EXPECTED_BASELINE_TARGET:
        raise WassersteinCpuBaselineImplementationGateValidationError(
            "operator_decision.baseline_target mismatch"
        )
    lc = doc.get("locked_constants", {})
    for key in REQUIRED_LOCKED_CONSTANT_KEYS:
        if key not in lc:
            raise WassersteinCpuBaselineImplementationGateValidationError(
                f"operator_decision.locked_constants missing key: {key!r}"
            )
    if lc.get("solver_policy") != EXPECTED_SOLVER_POLICY:
        raise WassersteinCpuBaselineImplementationGateValidationError(
            "operator_decision.locked_constants.solver_policy mismatch"
        )
    if lc.get("supported_fixture_scope") != EXPECTED_FIXTURE_SCOPE:
        raise WassersteinCpuBaselineImplementationGateValidationError(
            "operator_decision.locked_constants.supported_fixture_scope mismatch"
        )
    if lc.get("float64_precision_declaration") != EXPECTED_FLOAT64_DECLARATION:
        raise WassersteinCpuBaselineImplementationGateValidationError(
            "operator_decision.locked_constants.float64_precision_declaration mismatch"
        )
    nc_branches = set(lc.get("not_computable_branch_enumeration_confirmation", []))
    if nc_branches != EXPECTED_NOT_COMPUTABLE_BRANCHES:
        raise WassersteinCpuBaselineImplementationGateValidationError(
            f"not_computable_branch_enumeration_confirmation mismatch: {sorted(nc_branches)!r}"
        )
    for ack_key in (
        "shadow_lane_only_acknowledged",
        "test_vector_computation_only_acknowledged",
        "metric_values_emission_blocked_acknowledged",
        "forecast_influence_blocked_acknowledged",
        "p43_surface_lanes_blocked_acknowledged",
        "production_activation_blocked_acknowledged",
        "canon_promotion_blocked_acknowledged",
        "runtime_mutation_blocked_acknowledged",
        "execution_authority_blocked_acknowledged",
    ):
        if doc.get(ack_key) is not True:
            raise WassersteinCpuBaselineImplementationGateValidationError(
                f"operator_decision.{ack_key} must be True"
            )
    for block_key in (
        "valid_for_execution",
        "authorization_granted",
        "emits_metric_values",
        "forecast_authority",
        "inference_authority",
        "production_activation",
        "canon_promotion",
        "runtime_mutation",
        "execution_authority",
    ):
        if doc.get(block_key) is not False:
            raise WassersteinCpuBaselineImplementationGateValidationError(
                f"operator_decision.{block_key} must be False"
            )
    return doc


def _build_locked_constants_binding(decision: dict[str, Any]) -> dict[str, Any]:
    lc = decision["locked_constants"]
    return {
        "solver_policy": lc["solver_policy"],
        "supported_fixture_scope": lc["supported_fixture_scope"],
        "float64_precision_declaration": lc["float64_precision_declaration"],
        "balance_tolerance_declaration": lc["balance_tolerance_declaration"],
        "max_distribution_length_declaration": lc["max_distribution_length_declaration"],
        "max_coordinate_magnitude_declaration": lc["max_coordinate_magnitude_declaration"],
        "not_computable_branch_enumeration_confirmation": sorted(
            lc["not_computable_branch_enumeration_confirmation"]
        ),
        "all_constants_locked": True,
        "constants_count": len(REQUIRED_LOCKED_CONSTANT_KEYS),
        "constants_valid_for_test_vector_scope": True,
    }


def _build_fixture_scope_review() -> dict[str, Any]:
    valid_count = len(sorted((FIXTURE_DIR / "valid").iterdir()))
    invalid_count = len(sorted((FIXTURE_DIR / "invalid").iterdir()))
    nc_count = len(sorted((FIXTURE_DIR / "not_computable").iterdir()))
    total = valid_count + invalid_count + nc_count
    return {
        "supported_fixture_scope": EXPECTED_FIXTURE_SCOPE,
        "valid_fixture_count": valid_count,
        "invalid_fixture_count": invalid_count,
        "not_computable_fixture_count": nc_count,
        "total_fixture_count": total,
        "computation_implementation_not_yet_executed": True,
        "fixture_scope_confirmed": True,
    }


def build_authorized_implementation_scope(
    locked_constants: dict[str, Any],
) -> dict[str, Any]:
    return {
        "wasserstein_cpu_baseline_implementation_authorized": True,
        "authorized_computation_type": "TEST_VECTOR_COMPUTATION_ONLY",
        "bounded_scope_only": True,
        "fixture_scope": EXPECTED_FIXTURE_SCOPE,
        "runtime_scope": "SHADOW_LANE_ONLY",
        "locked_constants_binding": locked_constants,
    }


def build_no_metric_emission_block() -> dict[str, Any]:
    return {
        "emits_metric_values": False,
        "metric_emission_blocked": True,
        "block_confirmed": True,
        "block_finding": (
            "Wasserstein CPU baseline implementation gate does not grant "
            "any authority to emit metric values."
        ),
    }


def build_no_forecast_influence_block() -> dict[str, Any]:
    return {
        "forecast_influence": False,
        "forecast_influence_blocked": True,
        "block_confirmed": True,
        "block_finding": (
            "No projection lane influence. Wasserstein CPU baseline implementation "
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
        "wasserstein_cpu_baseline_implementation_authorized": True,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def validate_wasserstein_cpu_baseline_implementation_gate(
    gate: dict[str, Any],
) -> None:
    if gate.get("schema_version") != SCHEMA_VERSION:
        raise WassersteinCpuBaselineImplementationGateValidationError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if gate.get("gate_status") != GATE_STATUS:
        raise WassersteinCpuBaselineImplementationGateValidationError(
            f"gate_status must be {GATE_STATUS!r}"
        )
    if gate.get("gate_stage") != GATE_STAGE:
        raise WassersteinCpuBaselineImplementationGateValidationError(
            f"gate_stage must be {GATE_STAGE!r}"
        )
    if gate.get("operator_id") != OPERATOR_ID:
        raise WassersteinCpuBaselineImplementationGateValidationError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if gate.get("source_operator_decision_hash") != SOURCE_OPERATOR_DECISION_HASH:
        raise WassersteinCpuBaselineImplementationGateValidationError(
            "source_operator_decision_hash mismatch"
        )
    locks = gate.get("authority_locks", {})
    for flag in (
        "advisory_only",
        "shadow_lane_only",
        "implementation_gate_only",
        "wasserstein_cpu_baseline_implementation_authorized",
    ):
        if locks.get(flag) is not True:
            raise WassersteinCpuBaselineImplementationGateValidationError(
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
            raise WassersteinCpuBaselineImplementationGateValidationError(
                f"authority_locks.{flag} must be False"
            )
    auth = gate.get("authorized_implementation_scope", {})
    if auth.get("wasserstein_cpu_baseline_implementation_authorized") is not True:
        raise WassersteinCpuBaselineImplementationGateValidationError(
            "authorized_implementation_scope"
            ".wasserstein_cpu_baseline_implementation_authorized must be True"
        )
    if auth.get("authorized_computation_type") != "TEST_VECTOR_COMPUTATION_ONLY":
        raise WassersteinCpuBaselineImplementationGateValidationError(
            "authorized_computation_type must be TEST_VECTOR_COMPUTATION_ONLY"
        )
    lc = auth.get("locked_constants_binding", {})
    if lc.get("all_constants_locked") is not True:
        raise WassersteinCpuBaselineImplementationGateValidationError(
            "locked_constants_binding.all_constants_locked must be True"
        )
    if lc.get("constants_count") != 7:
        raise WassersteinCpuBaselineImplementationGateValidationError(
            "locked_constants_binding.constants_count must be 7"
        )
    nc = lc.get("not_computable_branch_enumeration_confirmation", [])
    if set(nc) != EXPECTED_NOT_COMPUTABLE_BRANCHES:
        raise WassersteinCpuBaselineImplementationGateValidationError(
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
            raise WassersteinCpuBaselineImplementationGateValidationError(
                f"blocked_scopes.{flag} must be False"
            )
    fsr = gate.get("fixture_scope_review", {})
    if fsr.get("fixture_scope_confirmed") is not True:
        raise WassersteinCpuBaselineImplementationGateValidationError(
            "fixture_scope_review.fixture_scope_confirmed must be True"
        )
    if fsr.get("computation_implementation_not_yet_executed") is not True:
        raise WassersteinCpuBaselineImplementationGateValidationError(
            "fixture_scope_review.computation_implementation_not_yet_executed must be True"
        )
    h = gate.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise WassersteinCpuBaselineImplementationGateValidationError(
            "canonical_hash must be a 64-char hex string"
        )
    preimage = {k: v for k, v in gate.items() if k != "canonical_hash"}
    expected = canonical_hash(preimage)
    if h != expected:
        raise WassersteinCpuBaselineImplementationGateValidationError(
            f"canonical_hash mismatch: stored={h!r} expected={expected!r}"
        )


def build_wasserstein_cpu_baseline_implementation_gate(
    gate_id: str = GATE_ID,
    created_at_utc: str = "2026-05-30T00:00:00Z",
    intended_lane: str = "SHADOW",
) -> dict[str, Any]:
    decision = _verify_operator_decision()

    locked_constants = _build_locked_constants_binding(decision)
    fixture_scope = _build_fixture_scope_review()
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
        "source_operator_decision_hash": SOURCE_OPERATOR_DECISION_HASH,
        "locked_constants_binding": locked_constants,
        "fixture_scope_review": fixture_scope,
        "authorized_implementation_scope": auth_scope,
        "no_metric_emission_block": no_metric,
        "no_forecast_influence_block": no_forecast,
        "no_p43_surface_lane_block": no_p43,
        "blocked_scopes": blocked,
        "authority_locks": locks,
        "recommended_next_step": (
            "WASSERSTEIN_IMPLEMENTATION_AUTHORIZED_BOUNDED_SHADOW_COMPUTATION_PR"
        ),
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return _finalize(result)
