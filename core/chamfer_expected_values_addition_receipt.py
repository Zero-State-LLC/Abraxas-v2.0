from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "ChamferExpectedValuesAdditionReceipt.v1"
RECEIPT_TYPE = "CHAMFER_EXPECTED_VALUES_ADDITION_RECEIPT"
OPERATOR_ID = "CHAMFER_DISTANCE"

SOURCE_EXPECTED_DISTANCE_VALUES_GATE_HASH = (
    "8ebb79a34637fa41cf9af2d9d63c72fa0febebac5164e31357a09e5090a55a8c"
)
SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH = (
    "a562df48b1d323cc92111297b2b7ea3421dbb48b85704b2b9efa3cd12102e2d7"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_STAGE = ("EXPECTED_VALUES_ADDITION_ONLY", "BLOCKED_PENDING_GATE")

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

VALID_FIXTURE_FILES = {
    "chamfer.valid.duplicate_points.v1": (
        "input/fixtures/chamfer/valid/duplicate_points.v1.json"
    ),
    "chamfer.valid.identical_point_sets.v1": (
        "input/fixtures/chamfer/valid/identical_point_sets.v1.json"
    ),
    "chamfer.valid.multidimensional_points.v1": (
        "input/fixtures/chamfer/valid/multidimensional_points.v1.json"
    ),
    "chamfer.valid.offset_point_sets.v1": (
        "input/fixtures/chamfer/valid/offset_point_sets.v1.json"
    ),
    "chamfer.valid.partial_overlap_point_sets.v1": (
        "input/fixtures/chamfer/valid/partial_overlap_point_sets.v1.json"
    ),
}

EXPECTED_CHAMFER_DISTANCES: dict[str, float] = {
    "chamfer.valid.duplicate_points.v1": 0.0,
    "chamfer.valid.identical_point_sets.v1": 0.0,
    "chamfer.valid.multidimensional_points.v1": 3.0,
    "chamfer.valid.offset_point_sets.v1": 1.0,
    "chamfer.valid.partial_overlap_point_sets.v1": 0.5,
}

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


class ChamferExpectedValuesAdditionReceiptError(ValueError):
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


def default_expected_values_addition_summary() -> dict[str, Any]:
    return {
        "total_valid_fixtures": 5,
        "expected_distances_present_in_fixtures": True,
        "all_expected_distances_static": True,
        "no_runtime_computation_required": True,
        "expected_distance_fixture_ids": list(EXPECTED_CHAMFER_DISTANCES.keys()),
        "expected_distances": EXPECTED_CHAMFER_DISTANCES,
        "invalid_fixture_ids_no_expected_distance": INVALID_FIXTURE_IDS,
        "nc_fixture_ids_no_expected_distance": NC_FIXTURE_IDS,
        "addition_status": "EXPECTED_VALUES_PRESENT_IN_FIXTURE_FILES",
    }


def default_computation_complete_review_confirmation() -> dict[str, Any]:
    return {
        "computation_complete_review_hash": SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH,
        "all_5_shadow_distances_verified": True,
        "all_values_match_static_fixtures": True,
        "operator_approval_on_record": True,
        "computation_complete_review_status": "CONFIRMED",
    }


def default_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "expected_values_addition_only": True,
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
        raise ChamferExpectedValuesAdditionReceiptError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------


def validate_chamfer_expected_values_addition_receipt(
    packet: dict[str, Any],
) -> None:
    if packet.get("schema_version") != SCHEMA_VERSION:
        raise ChamferExpectedValuesAdditionReceiptError("invalid_schema_version")
    if packet.get("receipt_type") != RECEIPT_TYPE:
        raise ChamferExpectedValuesAdditionReceiptError("invalid_receipt_type")
    if packet.get("operator_id") != OPERATOR_ID:
        raise ChamferExpectedValuesAdditionReceiptError("invalid_operator_id")
    if packet.get("intended_lane") not in ALLOWED_LANE:
        raise ChamferExpectedValuesAdditionReceiptError("invalid_lane")
    if packet.get("addition_stage") not in ALLOWED_STAGE:
        raise ChamferExpectedValuesAdditionReceiptError("invalid_addition_stage")
    al = packet.get("authority_locks", {})
    if al.get("emits_metric_values") is not False:
        raise ChamferExpectedValuesAdditionReceiptError("authority_lock_violation")
    if al.get("production_activation") is not False:
        raise ChamferExpectedValuesAdditionReceiptError("authority_lock_violation")
    _assert_safe(packet.get("provenance", {}))


# ---------------------------------------------------------------------------
# Build / hash / serialize
# ---------------------------------------------------------------------------


def compute_chamfer_expected_values_addition_receipt_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_chamfer_expected_values_addition_receipt(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(packet)


def build_chamfer_expected_values_addition_receipt(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": RECEIPT_TYPE,
        "operator_id": OPERATOR_ID,
        **payload,
    }
    base["canonical_hash"] = compute_chamfer_expected_values_addition_receipt_hash(base)
    validate_chamfer_expected_values_addition_receipt(base)
    return _finalize(base)
