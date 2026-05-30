"""WassersteinCpuBaselineComputationReceipt.v1 — core module.

Lane:   SHADOW
Scope:  TEST_VECTOR_COMPUTATION_ONLY
Solver: DETERMINISTIC_1D_SORTED_CDF_TRANSPORT_ONLY
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinCpuBaselineComputationReceipt.v1"
RECEIPT_TYPE = "WASSERSTEIN_CPU_BASELINE_COMPUTATION_RECEIPT"
OPERATOR_ID = "WASSERSTEIN"
RECEIPT_ID = "wasserstein_cpu_baseline_computation_receipt_001"
COMPUTATION_STATUS = "WASSERSTEIN_CPU_BASELINE_COMPUTATION_COMPLETE"
INTENDED_LANE = "SHADOW"
COMPUTATION_STAGE = "TEST_VECTOR_COMPUTATION_ONLY"

SOURCE_GATE_HASH = (
    "2b2d5e5ad006027eafb852090ed4396a5035e444a5a60e94f17c1782ffd328c9"
)

FIXTURE_DIR = Path("input/fixtures/wasserstein")

SOLVER_POLICY = "DETERMINISTIC_1D_SORTED_CDF_TRANSPORT_ONLY"
FLOAT64_DECLARATION = "IEEE_754_BINARY64_REQUIRED"
EPSILON_REL = 1e-9
EPSILON_ABS = 1e-12
MAX_DISTRIBUTION_LENGTH = 16
MAX_COORDINATE_MAGNITUDE = 1_000_000.0

# Comparison tolerance for matching computed values to fixture expected values.
# Fixture expected values are provided to 6 decimal places of precision; this
# tolerance absorbs rounding in those declared values.
FIXTURE_COMPARISON_ABS_TOL = 1e-5

NOT_COMPUTABLE_BRANCHES = frozenset({
    "EMPTY_DISTRIBUTION",
    "UNBALANCED_MASS",
    "NEGATIVE_MASS",
    "NON_FINITE_WEIGHT",
    "NON_FINITE_COORDINATE",
    "MISSING_REQUIRED_FIELD",
    "MISMATCHED_SUPPORT_WEIGHT_LENGTH",
})


class WassersteinCpuBaselineComputationError(ValueError):
    pass


# ---------------------------------------------------------------------------
# Pure-Python solver kernels (shadow-only, no external dependencies)
# ---------------------------------------------------------------------------


def _w1_sorted_cdf(p: list[float], q: list[float], support: list[float]) -> float:
    """1-Wasserstein via sorted cumulative-distribution method (1D)."""
    n = len(support)
    cdf_p = 0.0
    cdf_q = 0.0
    result = 0.0
    for k in range(n - 1):
        cdf_p += p[k]
        cdf_q += q[k]
        result += abs(cdf_p - cdf_q) * (support[k + 1] - support[k])
    return result


def _euclidean_distance(v1: list[float], v2: list[float]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))


def _greedy_min_cost_transport(
    supply: list[float], demand: list[float], cost: list[list[float]]
) -> float:
    s = list(supply)
    d = list(demand)
    n, m = len(s), len(d)
    total = 0.0
    while True:
        best: tuple[int, int, float] | None = None
        for i in range(n):
            if s[i] <= 1e-12:
                continue
            for j in range(m):
                if d[j] <= 1e-12:
                    continue
                if best is None or cost[i][j] < best[2]:
                    best = (i, j, cost[i][j])
        if best is None:
            break
        i, j, c = best
        amount = min(s[i], d[j])
        total += amount * c
        s[i] -= amount
        d[j] -= amount
    return total


# ---------------------------------------------------------------------------
# Per-fixture dispatch
# ---------------------------------------------------------------------------


def _dispatch_valid(f: dict[str, Any]) -> dict[str, Any]:
    fixture_id = f["fixture_id"]
    group = f["fixture_group"]
    inp = f["input"]

    if group == "DISTRIBUTION_PAIR_SCHEMA":
        computed = _w1_sorted_cdf(
            inp["p"], inp["q"], [float(x) for x in inp["support"]]
        )
    elif group == "WEIGHTED_HISTOGRAM_SCHEMA":
        edges = [float(x) for x in inp["bin_edges"]]
        midpoints = [(edges[k] + edges[k + 1]) / 2.0 for k in range(len(edges) - 1)]
        computed = _w1_sorted_cdf(inp["weights_p"], inp["weights_q"], midpoints)
    elif group == "REFERENCE_VECTOR_SCHEMA":
        computed = _euclidean_distance(
            [float(x) for x in inp["reference_vector"]],
            [float(x) for x in inp["query_vector"]],
        )
    elif group == "GROUND_METRIC_SCHEMA":
        computed = _greedy_min_cost_transport(inp["p"], inp["q"], inp["cost_matrix"])
    elif group == "DEGENERATE_DISTRIBUTION_SCHEMA":
        computed = _w1_sorted_cdf(
            inp["p"], inp["q"], [float(x) for x in inp["support"]]
        )
    else:
        raise WassersteinCpuBaselineComputationError(
            f"unknown_valid_fixture_group:{group}"
        )

    expected = f.get("expected_wasserstein_distance")
    distance_matched: bool
    if expected is not None:
        distance_matched = abs(computed - float(expected)) <= FIXTURE_COMPARISON_ABS_TOL
    else:
        distance_matched = True

    return {
        "fixture_id": fixture_id,
        "fixture_type": "VALID",
        "fixture_group": group,
        "computation_status": "SHADOW_COMPUTATION_COMPLETE",
        "computation_attempted": True,
        "shadow_lane": INTENDED_LANE,
        "shadow_transport_value": computed,
        "expected_distance": expected,
        "distance_matched": distance_matched,
        "comparison_abs_tolerance": FIXTURE_COMPARISON_ABS_TOL,
        "solver_policy": SOLVER_POLICY,
        "metric_value_emitted": False,
        "emits_metric_values": False,
    }


def _dispatch_invalid(f: dict[str, Any]) -> dict[str, Any]:
    return {
        "fixture_id": f["fixture_id"],
        "fixture_type": "INVALID",
        "fixture_group": f["fixture_group"],
        "computation_status": "INVALID_INPUT",
        "computation_attempted": False,
        "rejection_reason": f["rejection_reason"],
        "shadow_lane": INTENDED_LANE,
        "metric_value_emitted": False,
        "emits_metric_values": False,
    }


def _dispatch_nc(f: dict[str, Any]) -> dict[str, Any]:
    return {
        "fixture_id": f["fixture_id"],
        "fixture_type": "NOT_COMPUTABLE",
        "fixture_group": f["fixture_group"],
        "computation_status": "NOT_COMPUTABLE",
        "computation_attempted": False,
        "rejection_reason": f["rejection_reason"],
        "shadow_lane": INTENDED_LANE,
        "metric_value_emitted": False,
        "emits_metric_values": False,
    }


def run_computation(
    valid_fixtures: list[dict[str, Any]],
    invalid_fixtures: list[dict[str, Any]],
    nc_fixtures: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    valid_results = [_dispatch_valid(f) for f in valid_fixtures]
    invalid_results = [_dispatch_invalid(f) for f in invalid_fixtures]
    nc_results = [_dispatch_nc(f) for f in nc_fixtures]
    return valid_results, invalid_results, nc_results


# ---------------------------------------------------------------------------
# Sub-structure builders
# ---------------------------------------------------------------------------


def build_comparison_summary(
    valid_results: list[dict[str, Any]],
    invalid_results: list[dict[str, Any]],
    nc_results: list[dict[str, Any]],
) -> dict[str, Any]:
    valid_matched = sum(1 for r in valid_results if r.get("distance_matched"))
    invalid_routed = sum(
        1 for r in invalid_results if r.get("computation_status") == "INVALID_INPUT"
    )
    nc_routed = sum(
        1 for r in nc_results if r.get("computation_status") == "NOT_COMPUTABLE"
    )
    all_matched = (
        valid_matched == len(valid_results)
        and invalid_routed == len(invalid_results)
        and nc_routed == len(nc_results)
    )
    return {
        "total_valid": len(valid_results),
        "valid_matched": valid_matched,
        "total_invalid": len(invalid_results),
        "invalid_routed_as_invalid_input": invalid_routed,
        "total_not_computable": len(nc_results),
        "nc_routed_as_not_computable": nc_routed,
        "all_matched": all_matched,
        "comparison_abs_tolerance": FIXTURE_COMPARISON_ABS_TOL,
        "comparison_basis": "FIXTURE_DECLARED_EXPECTED_DISTANCE",
    }


def build_solver_policy_summary() -> dict[str, Any]:
    return {
        "solver_policy": SOLVER_POLICY,
        "float64_precision_declaration": FLOAT64_DECLARATION,
        "epsilon_rel": EPSILON_REL,
        "epsilon_abs": EPSILON_ABS,
        "max_distribution_length": MAX_DISTRIBUTION_LENGTH,
        "max_coordinate_magnitude": MAX_COORDINATE_MAGNITUDE,
        "not_computable_branches": sorted(NOT_COMPUTABLE_BRANCHES),
        "deterministic": True,
        "shadow_only": True,
        "no_external_solver": True,
    }


def build_blocked_scopes() -> dict[str, bool]:
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


def build_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "test_vector_computation_only": True,
        "wasserstein_cpu_baseline_computation_authorized": True,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


# ---------------------------------------------------------------------------
# Finalize / hash / serialize / build
# ---------------------------------------------------------------------------


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def validate_wasserstein_cpu_baseline_computation_receipt(
    packet: dict[str, Any],
) -> None:
    required = {
        "schema_version",
        "receipt_type",
        "receipt_id",
        "operator_id",
        "intended_lane",
        "computation_stage",
        "computation_status",
        "source_gate_hash",
        "valid_fixture_results",
        "invalid_fixture_results",
        "not_computable_fixture_results",
        "comparison_summary",
        "solver_policy_summary",
        "blocked_scopes",
        "authority_locks",
        "provenance",
        "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise WassersteinCpuBaselineComputationError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise WassersteinCpuBaselineComputationError("schema_version_mismatch")
    if packet["receipt_type"] != RECEIPT_TYPE:
        raise WassersteinCpuBaselineComputationError("receipt_type_mismatch")
    if packet["operator_id"] != OPERATOR_ID:
        raise WassersteinCpuBaselineComputationError("operator_id_mismatch")
    if packet["source_gate_hash"] != SOURCE_GATE_HASH:
        raise WassersteinCpuBaselineComputationError("source_gate_hash_mismatch")
    if packet["intended_lane"] != INTENDED_LANE:
        raise WassersteinCpuBaselineComputationError("intended_lane_mismatch")
    if packet["computation_stage"] != COMPUTATION_STAGE:
        raise WassersteinCpuBaselineComputationError("computation_stage_mismatch")
    if packet["computation_status"] != COMPUTATION_STATUS:
        raise WassersteinCpuBaselineComputationError("computation_status_mismatch")

    valid_r = packet["valid_fixture_results"]
    if len(valid_r) != 5:
        raise WassersteinCpuBaselineComputationError("valid_fixture_results_count_mismatch")
    for r in valid_r:
        if r.get("computation_status") != "SHADOW_COMPUTATION_COMPLETE":
            raise WassersteinCpuBaselineComputationError(
                f"valid_fixture_not_complete:{r.get('fixture_id')}"
            )
        if r.get("computation_attempted") is not True:
            raise WassersteinCpuBaselineComputationError(
                f"computation_attempted_must_be_true:{r.get('fixture_id')}"
            )
        if r.get("distance_matched") is not True:
            raise WassersteinCpuBaselineComputationError(
                f"distance_not_matched:{r.get('fixture_id')}"
            )
        if r.get("metric_value_emitted") is not False:
            raise WassersteinCpuBaselineComputationError(
                f"metric_value_emitted_must_be_false:{r.get('fixture_id')}"
            )

    invalid_r = packet["invalid_fixture_results"]
    if len(invalid_r) != 5:
        raise WassersteinCpuBaselineComputationError("invalid_fixture_results_count_mismatch")
    for r in invalid_r:
        if r.get("computation_status") != "INVALID_INPUT":
            raise WassersteinCpuBaselineComputationError(
                f"invalid_fixture_wrong_status:{r.get('fixture_id')}"
            )
        if r.get("computation_attempted") is not False:
            raise WassersteinCpuBaselineComputationError(
                f"computation_attempted_must_be_false_for_invalid:{r.get('fixture_id')}"
            )

    nc_r = packet["not_computable_fixture_results"]
    if len(nc_r) != 4:
        raise WassersteinCpuBaselineComputationError("nc_fixture_results_count_mismatch")
    for r in nc_r:
        if r.get("computation_status") != "NOT_COMPUTABLE":
            raise WassersteinCpuBaselineComputationError(
                f"nc_fixture_wrong_status:{r.get('fixture_id')}"
            )
        if r.get("computation_attempted") is not False:
            raise WassersteinCpuBaselineComputationError(
                f"computation_attempted_must_be_false_for_nc:{r.get('fixture_id')}"
            )

    cs = packet["comparison_summary"]
    if not cs.get("all_matched"):
        raise WassersteinCpuBaselineComputationError("comparison_summary_not_all_matched")

    al = packet["authority_locks"]
    if al.get("wasserstein_cpu_baseline_computation_authorized") is not True:
        raise WassersteinCpuBaselineComputationError(
            "wasserstein_cpu_baseline_computation_authorized_must_be_true"
        )
    if al.get("emits_metric_values") is not False:
        raise WassersteinCpuBaselineComputationError("emits_metric_values_must_be_false")
    if al.get("execution_authority") is not False:
        raise WassersteinCpuBaselineComputationError("execution_authority_must_be_false")
    if al.get("shadow_lane_only") is not True:
        raise WassersteinCpuBaselineComputationError("shadow_lane_only_must_be_true")

    bs = packet["blocked_scopes"]
    for flag in (
        "emits_metric_values",
        "forecast_influence",
        "p43_surface_lanes",
        "production_activation",
        "canon_promotion",
        "runtime_mutation",
        "execution_authority",
        "inference_authority",
    ):
        if bs.get(flag) is not False:
            raise WassersteinCpuBaselineComputationError(
                f"blocked_scopes.{flag}_must_be_false"
            )

    h = packet.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise WassersteinCpuBaselineComputationError(
            "canonical_hash must be a 64-char hex string"
        )
    expected_h = canonical_hash(_preimage(packet))
    if h != expected_h:
        raise WassersteinCpuBaselineComputationError(
            f"canonical_hash_mismatch:stored={h!r}:expected={expected_h!r}"
        )


def serialize_wasserstein_cpu_baseline_computation_receipt(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_wasserstein_cpu_baseline_computation_receipt(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": RECEIPT_TYPE,
        "receipt_id": RECEIPT_ID,
        "operator_id": OPERATOR_ID,
        "intended_lane": INTENDED_LANE,
        "computation_stage": COMPUTATION_STAGE,
        "computation_status": COMPUTATION_STATUS,
        "source_gate_hash": SOURCE_GATE_HASH,
        **payload,
        "authority_locks": payload.get("authority_locks", build_authority_locks()),
        "blocked_scopes": payload.get("blocked_scopes", build_blocked_scopes()),
    }
    base["canonical_hash"] = canonical_hash(_preimage(base))
    validate_wasserstein_cpu_baseline_computation_receipt(base)
    return _finalize(base)
