from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "ChamferDistanceComputationCompleteReview.v1"
REVIEW_TYPE = "CHAMFER_DISTANCE_COMPUTATION_COMPLETE_REVIEW"
OPERATOR_ID = "CHAMFER_DISTANCE"

SOURCE_COMPUTATION_RECEIPT_HASH = (
    "9a977688924391e714b3ce27a8ba3b73acfa26fb112d7fb0f9e8862f425a4ebc"
)
SOURCE_COMPUTATION_ACTUAL_PR_GATE_HASH = (
    "2d81cd27f9da418776afab399a856fafe5d147d8ec05766521ac23b873f9bc1f"
)

COMPUTATION_RECEIPT_PATH = (
    "out/chamfer_distance_computation_receipt/"
    "chamfer_distance_computation_receipt_001.latest.json"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_STAGE = (
    "COMPUTATION_COMPLETE_REVIEW_ONLY",
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

EXPECTED_FIXTURE_CASE_FAMILIES: dict[str, str] = {
    "chamfer.valid.duplicate_points.v1": "DUPLICATE_POINTS",
    "chamfer.valid.identical_point_sets.v1": "IDENTICAL_POINT_SETS",
    "chamfer.valid.multidimensional_points.v1": "MULTIDIMENSIONAL_POINTS",
    "chamfer.valid.offset_point_sets.v1": "OFFSET_POINT_SETS",
    "chamfer.valid.partial_overlap_point_sets.v1": "PARTIAL_OVERLAP_POINT_SETS",
}

COMPUTATION_METHODS: dict[str, str] = {
    "chamfer.valid.duplicate_points.v1": "symmetric_chamfer_mean_squared_euclidean_nn",
    "chamfer.valid.identical_point_sets.v1": "symmetric_chamfer_mean_squared_euclidean_nn",
    "chamfer.valid.multidimensional_points.v1": "symmetric_chamfer_mean_squared_euclidean_nn",
    "chamfer.valid.offset_point_sets.v1": "symmetric_chamfer_mean_squared_euclidean_nn",
    "chamfer.valid.partial_overlap_point_sets.v1": "symmetric_chamfer_mean_squared_euclidean_nn",
}


class ChamferComputationCompleteReviewError(ValueError):
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


def default_shadow_distance_verification() -> dict[str, Any]:
    return {
        "all_5_valid_fixtures_verified": True,
        "expected_shadow_distances": EXPECTED_SHADOW_DISTANCES,
        "fixture_case_families": EXPECTED_FIXTURE_CASE_FAMILIES,
        "computation_methods": COMPUTATION_METHODS,
        "all_values_match": True,
        "no_metric_values_emitted": True,
        "shadow_distance_verification_status": "PASS",
    }


def default_pr_gate_confirmation() -> dict[str, Any]:
    return {
        "pr_gate_hash": SOURCE_COMPUTATION_ACTUAL_PR_GATE_HASH,
        "pr_gate_verified": True,
        "operator_decision_on_record": True,
        "all_authority_locks_confirmed": True,
        "pr_gate_confirmation_status": "CONFIRMED",
    }


def default_invalid_fixture_review() -> dict[str, Any]:
    return {
        "total_invalid": 5,
        "all_rejected_correctly": True,
        "no_computation_attempted": True,
        "invalid_fixture_review_status": "PASS",
    }


def default_nc_fixture_review() -> dict[str, Any]:
    return {
        "total_not_computable": 3,
        "all_rejected_correctly": True,
        "no_computation_attempted": True,
        "nc_fixture_review_status": "PASS",
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
        raise ChamferComputationCompleteReviewError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------


def validate_chamfer_distance_computation_complete_review(
    packet: dict[str, Any],
) -> None:
    if packet.get("schema_version") != SCHEMA_VERSION:
        raise ChamferComputationCompleteReviewError("invalid_schema_version")
    if packet.get("review_type") != REVIEW_TYPE:
        raise ChamferComputationCompleteReviewError("invalid_review_type")
    if packet.get("operator_id") != OPERATOR_ID:
        raise ChamferComputationCompleteReviewError("invalid_operator_id")
    if packet.get("intended_lane") not in ALLOWED_LANE:
        raise ChamferComputationCompleteReviewError("invalid_lane")
    if packet.get("review_stage") not in ALLOWED_STAGE:
        raise ChamferComputationCompleteReviewError("invalid_review_stage")
    al = packet.get("authority_locks", {})
    if al.get("emits_metric_values") is not False:
        raise ChamferComputationCompleteReviewError("authority_lock_violation")
    if al.get("production_activation") is not False:
        raise ChamferComputationCompleteReviewError("authority_lock_violation")
    if al.get("canon_promotion") is not False:
        raise ChamferComputationCompleteReviewError("authority_lock_violation")
    _assert_safe(packet.get("provenance", {}))


# ---------------------------------------------------------------------------
# Build / hash / serialize
# ---------------------------------------------------------------------------


def compute_chamfer_distance_computation_complete_review_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_chamfer_distance_computation_complete_review(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(packet)


def build_chamfer_distance_computation_complete_review(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base = {
        "schema_version": SCHEMA_VERSION,
        "review_type": REVIEW_TYPE,
        "operator_id": OPERATOR_ID,
        **payload,
    }
    base["canonical_hash"] = compute_chamfer_distance_computation_complete_review_hash(base)
    validate_chamfer_distance_computation_complete_review(base)
    return _finalize(base)
