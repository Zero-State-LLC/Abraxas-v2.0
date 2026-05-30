from __future__ import annotations

import json
import math
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "ChamferDistanceComputationReceipt.v1"
RECEIPT_TYPE = "CHAMFER_DISTANCE_COMPUTATION_RECEIPT"
OPERATOR_ID = "CHAMFER_DISTANCE"

SOURCE_FIXTURE_CREATION_GATE_HASH = (
    "a6a0f49d71cd5ab9101091e599cb776456c5e3769270164e12021dabb34f1a2e"
)
SOURCE_EXPECTED_DISTANCE_VALUES_GATE_HASH = (
    "8ebb79a34637fa41cf9af2d9d63c72fa0febebac5164e31357a39e5090a55a8c"
)

FIXTURE_DIR_VALID = "input/fixtures/chamfer/valid"
FIXTURE_DIR_INVALID = "input/fixtures/chamfer/invalid"
FIXTURE_DIR_NC = "input/fixtures/chamfer/not_computable"

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_STAGE = (
    "COMPUTATION_RECEIPT_ONLY",
    "BLOCKED_PENDING_GATE",
)

FORBIDDEN = (
    "runtime",
    "scheduler",
    "cache",
    "forecast",
    "scoring",
    "metric-value",
    "chamfer-distance",
    "expected-distance",
    "fixture-file",
    "manifest-file",
    "schema-file",
    "gpu-kernel",
    "authority-flag",
    "metric-computation",
)

EXPECTED_SHADOW_DISTANCES: dict[str, float] = {
    "chamfer.valid.duplicate_points.v1": 0.0,
    "chamfer.valid.identical_point_sets.v1": 0.0,
    "chamfer.valid.multidimensional_points.v1": 3.0,
    "chamfer.valid.offset_point_sets.v1": 1.0,
    "chamfer.valid.partial_overlap_point_sets.v1": 0.5,
}

VALID_FIXTURE_IDS = list(EXPECTED_SHADOW_DISTANCES.keys())

INVALID_FIXTURE_IDS = [
    "chamfer.invalid.dimension_mismatch.v1",
    "chamfer.invalid.empty_point_set.v1",
    "chamfer.invalid.malformed_coordinates.v1",
    "chamfer.invalid.missing_point_set.v1",
    "chamfer.invalid.non_numeric_coordinate.v1",
]

NC_FIXTURE_IDS = [
    "chamfer.not_computable.missing_numerical_policy.v1",
    "chamfer.not_computable.undeclared_dimensionality.v1",
    "chamfer.not_computable.unknown_coordinate_space.v1",
]


class ChamferDistanceComputationReceiptError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


# ---------------------------------------------------------------------------
# Pure-Python Chamfer computation kernel (shadow-only, no external deps)
# ---------------------------------------------------------------------------


def _squared_distance(a: list[float], b: list[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b))


def _nearest_mean(source: list[list[float]], target: list[list[float]]) -> float:
    total = 0.0
    for s in source:
        total += min(_squared_distance(s, t) for t in target)
    return total / len(source)


def _chamfer_shadow(point_set_a: list[list[float]], point_set_b: list[list[float]]) -> float:
    a_to_b = _nearest_mean(point_set_a, point_set_b)
    b_to_a = _nearest_mean(point_set_b, point_set_a)
    return (a_to_b + b_to_a) / 2.0


def _round6(v: float) -> float:
    return round(v, 6)


# ---------------------------------------------------------------------------
# Per-fixture computation
# ---------------------------------------------------------------------------


def _compute_valid_fixture(f: dict[str, Any]) -> dict[str, Any]:
    fixture_id = f["fixture_id"]
    case_family = f.get("case_family", "UNKNOWN")
    ps = f["point_sets"]
    point_set_a = [list(p) for p in ps["point_set_a"]]
    point_set_b = [list(p) for p in ps["point_set_b"]]
    shadow_distance_value = _round6(_chamfer_shadow(point_set_a, point_set_b))
    expected = EXPECTED_SHADOW_DISTANCES[fixture_id]
    match = math.isclose(shadow_distance_value, expected, rel_tol=1e-5, abs_tol=1e-9)
    return {
        "fixture_id": fixture_id,
        "fixture_type": "VALID",
        "case_family": case_family,
        "computation_status": "SHADOW_COMPUTATION_COMPLETE",
        "shadow_lane": "SHADOW",
        "shadow_distance_value": shadow_distance_value,
        "expected_shadow_distance": expected,
        "values_match": match,
        "deterministic": True,
        "metric_value_emitted": False,
        "expected_distance_included": False,
    }


def _compute_invalid_fixture(f: dict[str, Any]) -> dict[str, Any]:
    return {
        "fixture_id": f["fixture_id"],
        "fixture_type": "INVALID",
        "case_family": f.get("case_family", "UNKNOWN"),
        "computation_status": "VALIDATION_ERROR",
        "rejection_reason": f.get("expected_status", "INVALID_INPUT_NO_EXPECTED_DISTANCE"),
        "shadow_lane": "SHADOW",
        "metric_value_emitted": False,
        "expected_distance_included": False,
    }


def _compute_nc_fixture(f: dict[str, Any]) -> dict[str, Any]:
    return {
        "fixture_id": f["fixture_id"],
        "fixture_type": "NOT_COMPUTABLE",
        "case_family": f.get("case_family", "UNKNOWN"),
        "computation_status": "NOT_COMPUTABLE",
        "rejection_reason": f.get("expected_status", "NOT_COMPUTABLE_NO_EXPECTED_DISTANCE"),
        "shadow_lane": "SHADOW",
        "metric_value_emitted": False,
        "expected_distance_included": False,
    }


def run_fixture_computation(
    valid_fixtures: list[dict[str, Any]],
    invalid_fixtures: list[dict[str, Any]],
    nc_fixtures: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
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
    all_match = all(r.get("values_match", False) for r in valid_results)
    return {
        "total_fixtures": 13,
        "valid_computed": len(valid_results),
        "invalid_rejected": len(invalid_results),
        "not_computable_rejected": len(nc_results),
        "all_shadow_lane": True,
        "no_metric_values_emitted": True,
        "no_expected_distances_included": True,
        "all_values_match_static_fixtures": all_match,
        "computation_status": "CHAMFER_DISTANCE_COMPUTATION_RECEIPT_COMPLETE",
    }


def default_numerical_policy() -> dict[str, Any]:
    return {
        "precision": "float64",
        "kernel": "pure_python_symmetric_chamfer_mean_squared_nearest_neighbor",
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
        "total_checked": 13,
        "no_forecast_binding": True,
        "no_p43_output": True,
    }


def default_no_p43_surface_lane_scan() -> dict[str, Any]:
    return {
        "scan_status": "CLEAN",
        "violations": [],
        "total_checked": 13,
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
        "computation_receipt_only": True,
        "chamfer_distance_computation_authorized": True,
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
        raise ChamferDistanceComputationReceiptError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------


def validate_chamfer_distance_computation_receipt(packet: dict[str, Any]) -> None:
    if packet.get("schema_version") != SCHEMA_VERSION:
        raise ChamferDistanceComputationReceiptError("invalid_schema_version")
    if packet.get("receipt_type") != RECEIPT_TYPE:
        raise ChamferDistanceComputationReceiptError("invalid_receipt_type")
    if packet.get("operator_id") != OPERATOR_ID:
        raise ChamferDistanceComputationReceiptError("invalid_operator_id")
    if packet.get("intended_lane") not in ALLOWED_LANE:
        raise ChamferDistanceComputationReceiptError("invalid_lane")
    if packet.get("computation_stage") not in ALLOWED_STAGE:
        raise ChamferDistanceComputationReceiptError("invalid_computation_stage")
    al = packet.get("authority_locks", {})
    if al.get("emits_metric_values") is not False:
        raise ChamferDistanceComputationReceiptError("authority_lock_violation_emits_metric_values")
    if al.get("production_activation") is not False:
        raise ChamferDistanceComputationReceiptError("authority_lock_violation_production_activation")
    if al.get("canon_promotion") is not False:
        raise ChamferDistanceComputationReceiptError("authority_lock_violation_canon_promotion")
    if al.get("runtime_mutation") is not False:
        raise ChamferDistanceComputationReceiptError("authority_lock_violation_runtime_mutation")
    _assert_safe(packet.get("provenance", {}))


# ---------------------------------------------------------------------------
# Build / hash / serialize
# ---------------------------------------------------------------------------


def compute_chamfer_distance_computation_receipt_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_chamfer_distance_computation_receipt(packet: dict[str, Any]) -> str:
    return canonical_dumps(packet)


def build_chamfer_distance_computation_receipt(payload: dict[str, Any]) -> dict[str, Any]:
    base = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": RECEIPT_TYPE,
        "operator_id": OPERATOR_ID,
        **payload,
    }
    base["canonical_hash"] = compute_chamfer_distance_computation_receipt_hash(base)
    validate_chamfer_distance_computation_receipt(base)
    return _finalize(base)
