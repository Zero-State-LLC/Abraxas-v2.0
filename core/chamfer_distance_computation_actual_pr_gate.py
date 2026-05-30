from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "ChamferDistanceComputationActualPrGate.v1"
GATE_TYPE = "CHAMFER_DISTANCE_COMPUTATION_ACTUAL_PR_GATE"
OPERATOR_ID = "CHAMFER_DISTANCE"

SOURCE_COMPUTATION_AUTHORIZATION_REVIEW_HASH = (
    "70ffc00a53b98802d3600b8cd9bec2053cab4fc89c7349c3e7c8423c94474de2"
)
SOURCE_COMPUTATION_RECEIPT_HASH = (
    "9a977688924391e714b3ce27a8ba3b73acfa26fb112d7fb0f9e8862f425a4ebc"
)
SOURCE_OPERATOR_DECISION_ID = (
    "CHAMFER_DISTANCE_COMPUTATION_OPERATOR_DECISION_2026_05_30_001"
)
SOURCE_OPERATOR_DECISION_HASH = (
    "b99bc776812c1d1b2d5438b7eb9b642567a24e34f19f35b365faf6fbc787643b"
)
SOURCE_FIXTURE_CREATION_GATE_HASH = (
    "a6a0f49d71cd5ab9101091e599cb776456c5e3769270164e12021dabb34f1a2e"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_GATE_STAGE = (
    "COMPUTATION_ACTUAL_PR_GATE_ONLY",
    "BLOCKED_PENDING_OPERATOR_DECISION",
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


class ChamferDistanceComputationActualPrGateError(ValueError):
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


def default_operator_decision_verification() -> dict[str, Any]:
    return {
        "operator_decision_id": SOURCE_OPERATOR_DECISION_ID,
        "operator_decision_hash": SOURCE_OPERATOR_DECISION_HASH,
        "operator_id_verified": "Daniel Meyer",
        "decision_verified": "approve_chamfer_distance_computation",
        "computation_lane_verified": "COMPUTATION_RECEIPT_ONLY",
        "upstream_authorization_review_hash_verified": SOURCE_COMPUTATION_AUTHORIZATION_REVIEW_HASH,
        "source_computation_receipt_hash": SOURCE_COMPUTATION_RECEIPT_HASH,
        "verification_status": "VERIFIED",
    }


def default_authorized_computation_scope() -> dict[str, Any]:
    return {
        "scope": "COMPUTATION_RECEIPT_ONLY",
        "authorized_lanes": ["SHADOW"],
        "fixture_count": 13,
        "no_forecast_influence": True,
        "no_runtime_binding": True,
        "no_p43_surface_lane_output": True,
        "no_production_activation": True,
        "computation_scope_status": "AUTHORIZED",
    }


def default_authorized_fixture_manifest() -> dict[str, Any]:
    return {
        "total_authorized_fixtures": 13,
        "valid_fixtures": 5,
        "invalid_fixtures": 5,
        "not_computable_fixtures": 3,
        "source_fixture_creation_gate_hash": SOURCE_FIXTURE_CREATION_GATE_HASH,
        "manifest_status": "AUTHORIZED_FOR_BOUNDED_COMPUTATION",
    }


def default_computation_constraints() -> dict[str, Any]:
    return {
        "bounded_to_validated_fixtures_only": True,
        "shadow_lane_only": True,
        "no_metric_value_emission": True,
        "no_expected_distance_addition": True,
        "no_p43_surface_lanes": True,
        "no_production_activation": True,
        "no_canon_promotion": True,
        "no_runtime_mutation": True,
        "no_execution_authority": True,
        "no_inference_authority": True,
        "constraints_status": "ALL_CONSTRAINTS_ENFORCED",
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
        "pr_gate_only": True,
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
        raise ChamferDistanceComputationActualPrGateError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------


def validate_chamfer_distance_computation_actual_pr_gate(
    packet: dict[str, Any],
) -> None:
    if packet.get("schema_version") != SCHEMA_VERSION:
        raise ChamferDistanceComputationActualPrGateError("invalid_schema_version")
    if packet.get("gate_type") != GATE_TYPE:
        raise ChamferDistanceComputationActualPrGateError("invalid_gate_type")
    if packet.get("operator_id") != OPERATOR_ID:
        raise ChamferDistanceComputationActualPrGateError("invalid_operator_id")
    if packet.get("intended_lane") not in ALLOWED_LANE:
        raise ChamferDistanceComputationActualPrGateError("invalid_lane")
    if packet.get("gate_stage") not in ALLOWED_GATE_STAGE:
        raise ChamferDistanceComputationActualPrGateError("invalid_gate_stage")
    al = packet.get("authority_locks", {})
    if al.get("emits_metric_values") is not False:
        raise ChamferDistanceComputationActualPrGateError("authority_lock_violation")
    if al.get("production_activation") is not False:
        raise ChamferDistanceComputationActualPrGateError("authority_lock_violation")
    if al.get("canon_promotion") is not False:
        raise ChamferDistanceComputationActualPrGateError("authority_lock_violation")
    _assert_safe(packet.get("provenance", {}))


# ---------------------------------------------------------------------------
# Build / hash / serialize
# ---------------------------------------------------------------------------


def compute_chamfer_distance_computation_actual_pr_gate_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_chamfer_distance_computation_actual_pr_gate(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(packet)


def build_chamfer_distance_computation_actual_pr_gate(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base = {
        "schema_version": SCHEMA_VERSION,
        "gate_type": GATE_TYPE,
        "operator_id": OPERATOR_ID,
        **payload,
    }
    base["canonical_hash"] = compute_chamfer_distance_computation_actual_pr_gate_hash(base)
    validate_chamfer_distance_computation_actual_pr_gate(base)
    return _finalize(base)
