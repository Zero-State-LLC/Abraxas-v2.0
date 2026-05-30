from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "ChamferExpectedValuesGate.v1"
GATE_TYPE = "CHAMFER_EXPECTED_VALUES_GATE"
OPERATOR_ID = "CHAMFER_DISTANCE"

SOURCE_COMPUTATION_RECEIPT_HASH = (
    "9a977688924391e714b3ce27a8ba3b73acfa26fb112d7fb0f9e8862f425a4ebc"
)
SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH = (
    "a562df48b1d323cc92111297b2b7ea3421dbb48b85704b2b9efa3cd12102e2d7"
)
SOURCE_EXPECTED_VALUES_ADDITION_RECEIPT_HASH = (
    "c84fff6b939645c4a31ecad111be0d662da9001f12ed8f8a9d26860c6756c724"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_STAGE = (
    "EXPECTED_VALUES_GATE_ONLY",
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

SHADOW_DISTANCE_VALUES: dict[str, float] = {
    "chamfer.valid.duplicate_points.v1": 0.0,
    "chamfer.valid.identical_point_sets.v1": 0.0,
    "chamfer.valid.multidimensional_points.v1": 3.0,
    "chamfer.valid.offset_point_sets.v1": 1.0,
    "chamfer.valid.partial_overlap_point_sets.v1": 0.5,
}

VALID_FIXTURE_CASE_FAMILIES: dict[str, str] = {
    "chamfer.valid.duplicate_points.v1": "DUPLICATE_POINTS",
    "chamfer.valid.identical_point_sets.v1": "IDENTICAL_POINT_SETS",
    "chamfer.valid.multidimensional_points.v1": "MULTIDIMENSIONAL_POINTS",
    "chamfer.valid.offset_point_sets.v1": "OFFSET_POINT_SETS",
    "chamfer.valid.partial_overlap_point_sets.v1": "PARTIAL_OVERLAP_POINT_SETS",
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


class ChamferExpectedValuesGateError(ValueError):
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


def default_shadow_distance_gate_verification() -> dict[str, Any]:
    return {
        "all_5_shadow_distances_locked": True,
        "shadow_distance_values": SHADOW_DISTANCE_VALUES,
        "fixture_case_families": VALID_FIXTURE_CASE_FAMILIES,
        "invalid_fixture_ids": INVALID_FIXTURE_IDS,
        "nc_fixture_ids": NC_FIXTURE_IDS,
        "source_computation_complete_review_hash": SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH,
        "shadow_distance_gate_status": "PASS",
    }


def default_expected_values_gate_checks() -> dict[str, Any]:
    return {
        "expected_values_present_in_fixtures": True,
        "expected_values_match_computation_receipt": True,
        "no_additional_values_added": True,
        "no_metric_values_emitted": True,
        "source_addition_receipt_hash": SOURCE_EXPECTED_VALUES_ADDITION_RECEIPT_HASH,
        "gate_checks_status": "ALL_CHECKS_PASS",
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
        "expected_values_gate_only": True,
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
        raise ChamferExpectedValuesGateError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------


def validate_chamfer_expected_values_gate(packet: dict[str, Any]) -> None:
    if packet.get("schema_version") != SCHEMA_VERSION:
        raise ChamferExpectedValuesGateError("invalid_schema_version")
    if packet.get("gate_type") != GATE_TYPE:
        raise ChamferExpectedValuesGateError("invalid_gate_type")
    if packet.get("operator_id") != OPERATOR_ID:
        raise ChamferExpectedValuesGateError("invalid_operator_id")
    if packet.get("intended_lane") not in ALLOWED_LANE:
        raise ChamferExpectedValuesGateError("invalid_lane")
    if packet.get("gate_stage") not in ALLOWED_STAGE:
        raise ChamferExpectedValuesGateError("invalid_gate_stage")
    al = packet.get("authority_locks", {})
    if al.get("emits_metric_values") is not False:
        raise ChamferExpectedValuesGateError("authority_lock_violation")
    if al.get("production_activation") is not False:
        raise ChamferExpectedValuesGateError("authority_lock_violation")
    if al.get("canon_promotion") is not False:
        raise ChamferExpectedValuesGateError("authority_lock_violation")
    _assert_safe(packet.get("provenance", {}))


# ---------------------------------------------------------------------------
# Build / hash / serialize
# ---------------------------------------------------------------------------


def compute_chamfer_expected_values_gate_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_chamfer_expected_values_gate(packet: dict[str, Any]) -> str:
    return canonical_dumps(packet)


def build_chamfer_expected_values_gate(payload: dict[str, Any]) -> dict[str, Any]:
    base = {
        "schema_version": SCHEMA_VERSION,
        "gate_type": GATE_TYPE,
        "operator_id": OPERATOR_ID,
        **payload,
    }
    base["canonical_hash"] = compute_chamfer_expected_values_gate_hash(base)
    validate_chamfer_expected_values_gate(base)
    return _finalize(base)
