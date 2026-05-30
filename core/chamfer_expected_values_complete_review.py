from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "ChamferExpectedValuesCompleteReview.v1"
REVIEW_TYPE = "CHAMFER_EXPECTED_VALUES_COMPLETE_REVIEW"
OPERATOR_ID = "CHAMFER_DISTANCE"

SOURCE_EXPECTED_VALUES_ADDITION_RECEIPT_HASH = (
    "c84fff6b939645c4a31ecad111be0d662da9001f12ed8f8a9d26860c6756c724"
)
SOURCE_EXPECTED_VALUES_GATE_HASH = (
    "a0952c077acb489a77ab9c5c15bab02ee10887a009a44d43e3207913bbee4045"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_STAGE = (
    "EXPECTED_VALUES_COMPLETE_REVIEW_ONLY",
    "BLOCKED_PENDING_REVIEW",
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

FINAL_SHADOW_DISTANCES: dict[str, float] = {
    "chamfer.valid.duplicate_points.v1": 0.0,
    "chamfer.valid.identical_point_sets.v1": 0.0,
    "chamfer.valid.multidimensional_points.v1": 3.0,
    "chamfer.valid.offset_point_sets.v1": 1.0,
    "chamfer.valid.partial_overlap_point_sets.v1": 0.5,
}


class ChamferExpectedValuesCompleteReviewError(ValueError):
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


def default_final_expected_values_summary() -> dict[str, Any]:
    return {
        "total_valid_fixtures": 5,
        "all_expected_distances_confirmed": True,
        "final_shadow_distances": FINAL_SHADOW_DISTANCES,
        "addition_receipt_confirmed": True,
        "gate_confirmed": True,
        "source_addition_receipt_hash": SOURCE_EXPECTED_VALUES_ADDITION_RECEIPT_HASH,
        "source_gate_hash": SOURCE_EXPECTED_VALUES_GATE_HASH,
        "final_expected_values_status": "CONFIRMED_AND_SEALED",
    }


def default_chain_completion_summary() -> dict[str, Any]:
    return {
        "computation_receipt_complete": True,
        "authorization_review_complete": True,
        "pr_gate_complete": True,
        "computation_complete_review_complete": True,
        "expected_values_addition_receipt_complete": True,
        "expected_values_gate_complete": True,
        "chain_completion_status": "ALL_STEPS_COMPLETE",
        "recommended_next_phase": "CHAMFER_DISTANCE_OPERATOR_BASELINE_IMPLEMENTATION",
    }


def default_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "complete_review_only": True,
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
        raise ChamferExpectedValuesCompleteReviewError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------


def validate_chamfer_expected_values_complete_review(
    packet: dict[str, Any],
) -> None:
    if packet.get("schema_version") != SCHEMA_VERSION:
        raise ChamferExpectedValuesCompleteReviewError("invalid_schema_version")
    if packet.get("review_type") != REVIEW_TYPE:
        raise ChamferExpectedValuesCompleteReviewError("invalid_review_type")
    if packet.get("operator_id") != OPERATOR_ID:
        raise ChamferExpectedValuesCompleteReviewError("invalid_operator_id")
    if packet.get("intended_lane") not in ALLOWED_LANE:
        raise ChamferExpectedValuesCompleteReviewError("invalid_lane")
    if packet.get("review_stage") not in ALLOWED_STAGE:
        raise ChamferExpectedValuesCompleteReviewError("invalid_review_stage")
    al = packet.get("authority_locks", {})
    if al.get("emits_metric_values") is not False:
        raise ChamferExpectedValuesCompleteReviewError("authority_lock_violation")
    if al.get("production_activation") is not False:
        raise ChamferExpectedValuesCompleteReviewError("authority_lock_violation")
    if al.get("canon_promotion") is not False:
        raise ChamferExpectedValuesCompleteReviewError("authority_lock_violation")
    _assert_safe(packet.get("provenance", {}))


# ---------------------------------------------------------------------------
# Build / hash / serialize
# ---------------------------------------------------------------------------


def compute_chamfer_expected_values_complete_review_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_chamfer_expected_values_complete_review(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(packet)


def build_chamfer_expected_values_complete_review(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base = {
        "schema_version": SCHEMA_VERSION,
        "review_type": REVIEW_TYPE,
        "operator_id": OPERATOR_ID,
        **payload,
    }
    base["canonical_hash"] = compute_chamfer_expected_values_complete_review_hash(base)
    validate_chamfer_expected_values_complete_review(base)
    return _finalize(base)
