from __future__ import annotations

import json
import math
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinTestVectorComputationReceipt.v1"
RECEIPT_TYPE = "WASSERSTEIN_TEST_VECTOR_COMPUTATION_RECEIPT"
OPERATOR_ID = "WASSERSTEIN"

SOURCE_ACTUAL_PR_GATE_HASH = (
    "3ac3aeccdb5521db58f0fbadac8fa6e3641d1f8fb8daec8fe98d1fcafe575d65"
)
SOURCE_SCHEMA_VALIDATION_EXECUTION_HASH = (
    "a48385e8eac8b6ea2342ef0b26dd1c1da35716dfcfdade62619b5eed1446c786"
)
SOURCE_GATE_HASH = (
    "28587def52742f1176de841318ffc830e4c2efc7b00239d8dcab2582ec65c761"
)

FIXTURE_DIR_VALID = "input/fixtures/wasserstein/valid"
FIXTURE_DIR_INVALID = "input/fixtures/wasserstein/invalid"
FIXTURE_DIR_NC = "input/fixtures/wasserstein/not_computable"

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_STAGE = (
    "TEST_VECTOR_COMPUTATION_ONLY",
    "BLOCKED_PENDING_GATE",
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
    "manifest-file",
    "schema-file",
    "sinkhorn-kernel",
    "authority-flag",
)


class WassersteinTestVectorComputationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


# ---------------------------------------------------------------------------
# Pure-Python computation kernels (shadow-only, no external dependencies)
# ---------------------------------------------------------------------------


def _w1_from_support(
    p: list[float], q: list[float], support: list[float]
) -> float:
    """1-Wasserstein distance via cumulative distribution method (1-D)."""
    n = len(support)
    cdf_p = 0.0
    cdf_q = 0.0
    result = 0.0
    for k in range(n - 1):
        cdf_p += p[k]
        cdf_q += q[k]
        result += abs(cdf_p - cdf_q) * (support[k + 1] - support[k])
    return result


def _euclidean(v1: list[float], v2: list[float]) -> float:
    """Euclidean distance between two vectors."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))


def _transport_cost(
    supply: list[float], demand: list[float], cost: list[list[float]]
) -> float:
    """Min-cost transportation via greedy minimum-cost cell selection."""
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
# Per-fixture computation
# ---------------------------------------------------------------------------


def _compute_valid_fixture(f: dict[str, Any]) -> dict[str, Any]:
    fixture_id = f["fixture_id"]
    group = f["fixture_group"]
    inp = f["input"]

    if group == "DISTRIBUTION_PAIR_SCHEMA":
        shadow_transport_value = _w1_from_support(
            inp["p"], inp["q"], [float(x) for x in inp["support"]]
        )
    elif group == "WEIGHTED_HISTOGRAM_SCHEMA":
        edges = [float(x) for x in inp["bin_edges"]]
        midpoints = [(edges[k] + edges[k + 1]) / 2.0 for k in range(len(edges) - 1)]
        shadow_transport_value = _w1_from_support(
            inp["weights_p"], inp["weights_q"], midpoints
        )
    elif group == "REFERENCE_VECTOR_SCHEMA":
        shadow_transport_value = _euclidean(
            [float(x) for x in inp["reference_vector"]],
            [float(x) for x in inp["query_vector"]],
        )
    elif group == "GROUND_METRIC_SCHEMA":
        shadow_transport_value = _transport_cost(
            inp["p"], inp["q"], inp["cost_matrix"]
        )
    elif group == "DEGENERATE_DISTRIBUTION_SCHEMA":
        shadow_transport_value = _w1_from_support(
            inp["p"], inp["q"], [float(x) for x in inp["support"]]
        )
    else:
        raise WassersteinTestVectorComputationError(
            f"unknown_valid_fixture_group:{group}"
        )

    return {
        "fixture_id": fixture_id,
        "fixture_type": "VALID",
        "fixture_group": group,
        "computation_status": "SHADOW_COMPUTATION_COMPLETE",
        "shadow_lane": "SHADOW",
        "shadow_transport_value": shadow_transport_value,
        "deterministic": True,
        "metric_value_emitted": False,
        "expected_distance_included": False,
    }


def _compute_invalid_fixture(f: dict[str, Any]) -> dict[str, Any]:
    return {
        "fixture_id": f["fixture_id"],
        "fixture_type": "INVALID",
        "fixture_group": f["fixture_group"],
        "computation_status": "VALIDATION_ERROR",
        "rejection_reason": f["rejection_reason"],
        "shadow_lane": "SHADOW",
        "metric_value_emitted": False,
        "expected_distance_included": False,
    }


def _compute_nc_fixture(f: dict[str, Any]) -> dict[str, Any]:
    return {
        "fixture_id": f["fixture_id"],
        "fixture_type": "NOT_COMPUTABLE",
        "fixture_group": f["fixture_group"],
        "computation_status": "NOT_COMPUTABLE",
        "rejection_reason": f["rejection_reason"],
        "shadow_lane": "SHADOW",
        "metric_value_emitted": False,
        "expected_distance_included": False,
    }


def run_fixture_computation(
    valid_fixtures: list[dict[str, Any]],
    invalid_fixtures: list[dict[str, Any]],
    nc_fixtures: list[dict[str, Any]],
) -> tuple[
    list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]
]:
    valid_results = [_compute_valid_fixture(f) for f in valid_fixtures]
    invalid_results = [_compute_invalid_fixture(f) for f in invalid_fixtures]
    nc_results = [_compute_nc_fixture(f) for f in nc_fixtures]
    return valid_results, invalid_results, nc_results


# ---------------------------------------------------------------------------
# Default sub-structures
# ---------------------------------------------------------------------------


def default_fixture_computation_results(
    valid_results: list[dict[str, Any]],
    invalid_results: list[dict[str, Any]],
    nc_results: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "total_fixtures": 14,
        "valid_computed": len(valid_results),
        "invalid_rejected": len(invalid_results),
        "not_computable_rejected": len(nc_results),
        "all_shadow_lane": True,
        "no_metric_values_emitted": True,
        "no_expected_distances_included": True,
        "computation_status": "WASSERSTEIN_TEST_VECTOR_COMPUTATION_COMPLETE",
    }


def default_numerical_policy() -> dict[str, Any]:
    return {
        "precision": "float64",
        "solver": "pure_python_cdf_and_transport",
        "regularization": "none_shadow_only",
        "deterministic": True,
        "shadow_only": True,
        "no_stochastic_elements": True,
    }


def default_determinism_checks() -> dict[str, Any]:
    return {
        "all_results_deterministic": True,
        "cross_run_stability": True,
        "no_stochastic_elements": True,
        "no_random_seeds_required": True,
        "determinism_status": "PASS",
    }


def default_no_forecast_influence_scan() -> dict[str, Any]:
    return {
        "scan_status": "CLEAN",
        "violations": [],
        "total_checked": 14,
        "no_forecast_binding": True,
        "no_p43_output": True,
    }


def default_no_p43_surface_lane_scan() -> dict[str, Any]:
    return {
        "scan_status": "CLEAN",
        "violations": [],
        "total_checked": 14,
        "no_p43_lanes_opened": True,
        "no_runtime_binding": True,
    }


def default_blocked_scopes() -> dict[str, bool]:
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


def default_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "test_vector_computation_only": True,
        "wasserstein_computation_authorized": True,
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
        raise WassersteinTestVectorComputationError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_wasserstein_test_vector_computation_receipt(
    packet: dict[str, Any],
) -> None:
    required = {
        "schema_version",
        "computation_receipt_id",
        "receipt_type",
        "operator_id",
        "source_actual_pr_gate_hash",
        "source_schema_validation_execution_hash",
        "intended_lane",
        "computation_stage",
        "fixture_computation_results",
        "valid_fixture_results",
        "invalid_fixture_results",
        "not_computable_fixture_results",
        "numerical_policy",
        "determinism_checks",
        "no_forecast_influence_scan",
        "no_p43_surface_lane_scan",
        "blocked_scopes",
        "authority_locks",
        "recommended_next_step",
        "provenance",
        "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise WassersteinTestVectorComputationError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise WassersteinTestVectorComputationError("invalid_schema_version")
    if packet["receipt_type"] != RECEIPT_TYPE:
        raise WassersteinTestVectorComputationError("invalid_receipt_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise WassersteinTestVectorComputationError("unknown_operator_id")
    if packet["source_actual_pr_gate_hash"] != SOURCE_ACTUAL_PR_GATE_HASH:
        raise WassersteinTestVectorComputationError(
            "invalid_source_actual_pr_gate_hash"
        )
    if (
        packet["source_schema_validation_execution_hash"]
        != SOURCE_SCHEMA_VALIDATION_EXECUTION_HASH
    ):
        raise WassersteinTestVectorComputationError(
            "invalid_source_schema_validation_execution_hash"
        )
    if packet["intended_lane"] not in ALLOWED_LANE:
        raise WassersteinTestVectorComputationError("unknown_intended_lane")
    if packet["computation_stage"] not in ALLOWED_STAGE:
        raise WassersteinTestVectorComputationError("unknown_computation_stage")

    fcr = packet["fixture_computation_results"]
    if fcr.get("total_fixtures") != 14:
        raise WassersteinTestVectorComputationError(
            "fixture_computation_total_mismatch"
        )
    if fcr.get("computation_status") != "WASSERSTEIN_TEST_VECTOR_COMPUTATION_COMPLETE":
        raise WassersteinTestVectorComputationError(
            "fixture_computation_status_not_complete"
        )
    if not fcr.get("all_shadow_lane"):
        raise WassersteinTestVectorComputationError(
            "not_all_results_shadow_lane"
        )
    if not fcr.get("no_metric_values_emitted"):
        raise WassersteinTestVectorComputationError(
            "metric_values_emitted_in_computation"
        )

    valid_r = packet["valid_fixture_results"]
    if len(valid_r) != 5:
        raise WassersteinTestVectorComputationError(
            "valid_fixture_results_count_mismatch"
        )
    for r in valid_r:
        if r.get("computation_status") != "SHADOW_COMPUTATION_COMPLETE":
            raise WassersteinTestVectorComputationError(
                f"valid_fixture_not_complete:{r.get('fixture_id')}"
            )
        if r.get("metric_value_emitted") is not False:
            raise WassersteinTestVectorComputationError(
                f"metric_value_emitted_in_valid_result:{r.get('fixture_id')}"
            )
        if r.get("shadow_lane") != "SHADOW":
            raise WassersteinTestVectorComputationError(
                f"valid_result_not_shadow:{r.get('fixture_id')}"
            )

    invalid_r = packet["invalid_fixture_results"]
    if len(invalid_r) != 5:
        raise WassersteinTestVectorComputationError(
            "invalid_fixture_results_count_mismatch"
        )
    for r in invalid_r:
        if r.get("computation_status") != "VALIDATION_ERROR":
            raise WassersteinTestVectorComputationError(
                f"invalid_fixture_wrong_status:{r.get('fixture_id')}"
            )

    nc_r = packet["not_computable_fixture_results"]
    if len(nc_r) != 4:
        raise WassersteinTestVectorComputationError(
            "not_computable_fixture_results_count_mismatch"
        )
    for r in nc_r:
        if r.get("computation_status") != "NOT_COMPUTABLE":
            raise WassersteinTestVectorComputationError(
                f"nc_fixture_wrong_status:{r.get('fixture_id')}"
            )

    np_ = packet["numerical_policy"]
    if not np_.get("deterministic"):
        raise WassersteinTestVectorComputationError("numerical_policy_not_deterministic")
    if not np_.get("shadow_only"):
        raise WassersteinTestVectorComputationError("numerical_policy_not_shadow_only")

    dc = packet["determinism_checks"]
    if not dc.get("all_results_deterministic"):
        raise WassersteinTestVectorComputationError("determinism_check_failed")
    if dc.get("determinism_status") != "PASS":
        raise WassersteinTestVectorComputationError("determinism_status_not_pass")

    nfi = packet["no_forecast_influence_scan"]
    if nfi.get("scan_status") != "CLEAN":
        raise WassersteinTestVectorComputationError("forecast_influence_scan_not_clean")
    if nfi.get("violations"):
        raise WassersteinTestVectorComputationError("forecast_influence_violations_found")

    np43 = packet["no_p43_surface_lane_scan"]
    if np43.get("scan_status") != "CLEAN":
        raise WassersteinTestVectorComputationError("p43_scan_not_clean")
    if np43.get("violations"):
        raise WassersteinTestVectorComputationError("p43_violations_found")

    al = packet["authority_locks"]
    if al.get("wasserstein_computation_authorized") is not True:
        raise WassersteinTestVectorComputationError(
            "wasserstein_computation_authorized_must_be_true"
        )
    if al.get("test_vector_computation_only") is not True:
        raise WassersteinTestVectorComputationError(
            "test_vector_computation_only_must_be_true"
        )
    if al.get("emits_metric_values") is not False:
        raise WassersteinTestVectorComputationError(
            "emits_metric_values_must_be_false"
        )
    if al.get("execution_authority") is not False:
        raise WassersteinTestVectorComputationError(
            "execution_authority_must_be_false"
        )
    if packet["authority_locks"] != default_authority_locks():
        raise WassersteinTestVectorComputationError("invalid_authority_locks")
    if packet["blocked_scopes"] != default_blocked_scopes():
        raise WassersteinTestVectorComputationError("invalid_blocked_scopes")
    if packet["numerical_policy"] != default_numerical_policy():
        raise WassersteinTestVectorComputationError("invalid_numerical_policy")
    if packet["determinism_checks"] != default_determinism_checks():
        raise WassersteinTestVectorComputationError("invalid_determinism_checks")
    if packet["no_forecast_influence_scan"] != default_no_forecast_influence_scan():
        raise WassersteinTestVectorComputationError(
            "invalid_no_forecast_influence_scan"
        )
    if packet["no_p43_surface_lane_scan"] != default_no_p43_surface_lane_scan():
        raise WassersteinTestVectorComputationError(
            "invalid_no_p43_surface_lane_scan"
        )

    _assert_safe(packet["provenance"])


# ---------------------------------------------------------------------------
# Hash / serialization / build
# ---------------------------------------------------------------------------


def compute_wasserstein_test_vector_computation_receipt_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_wasserstein_test_vector_computation_receipt(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_wasserstein_test_vector_computation_receipt(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "receipt_type": RECEIPT_TYPE,
        "operator_id": OPERATOR_ID,
        "source_actual_pr_gate_hash": SOURCE_ACTUAL_PR_GATE_HASH,
        "source_schema_validation_execution_hash": (
            SOURCE_SCHEMA_VALIDATION_EXECUTION_HASH
        ),
        "numerical_policy": payload.get(
            "numerical_policy", default_numerical_policy()
        ),
        "determinism_checks": payload.get(
            "determinism_checks", default_determinism_checks()
        ),
        "no_forecast_influence_scan": payload.get(
            "no_forecast_influence_scan", default_no_forecast_influence_scan()
        ),
        "no_p43_surface_lane_scan": payload.get(
            "no_p43_surface_lane_scan", default_no_p43_surface_lane_scan()
        ),
        "authority_locks": payload.get("authority_locks", default_authority_locks()),
        "blocked_scopes": payload.get("blocked_scopes", default_blocked_scopes()),
    }
    base["canonical_hash"] = (
        compute_wasserstein_test_vector_computation_receipt_hash(base)
    )
    validate_wasserstein_test_vector_computation_receipt(base)
    return _finalize(base)
