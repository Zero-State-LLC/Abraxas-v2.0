from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "ChamferDistanceComputationAuthorizationReview.v1"
REVIEW_TYPE = "CHAMFER_DISTANCE_COMPUTATION_AUTHORIZATION_REVIEW"
OPERATOR_ID = "CHAMFER_DISTANCE"

SOURCE_COMPUTATION_RECEIPT_HASH = (
    "9a977688924391e714b3ce27a8ba3b73acfa26fb112d7fb0f9e8862f425a4ebc"
)
SOURCE_FIXTURE_CREATION_GATE_HASH = (
    "a6a0f49d71cd5ab9101091e599cb776456c5e3769270164e12021dabb34f1a2e"
)
SOURCE_EXPECTED_DISTANCE_VALUES_GATE_HASH = (
    "8ebb79a34637fa41cf9af2d9d63c72fa0febebac5164e31357a39e5090a55a8c"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_REVIEW_STAGE = (
    "COMPUTATION_AUTHORIZATION_REVIEW_ONLY",
    "BLOCKED_PENDING_AUTHORIZATION_REVIEW",
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


class ChamferDistanceComputationAuthorizationReviewError(ValueError):
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


def default_fixture_corpus_readiness_review() -> dict[str, Any]:
    return {
        "total_fixtures_verified": 13,
        "valid_fixtures": 5,
        "invalid_fixtures": 5,
        "not_computable_fixtures": 3,
        "all_fixture_files_present": True,
        "all_gate_hashes_pinned": True,
        "source_fixture_creation_gate_hash": SOURCE_FIXTURE_CREATION_GATE_HASH,
        "source_expected_distance_values_gate_hash": SOURCE_EXPECTED_DISTANCE_VALUES_GATE_HASH,
        "corpus_readiness_status": "READY",
    }


def default_computation_receipt_review() -> dict[str, Any]:
    return {
        "computation_receipt_executed": True,
        "all_13_fixtures_processed": True,
        "all_5_valid_values_match_static": True,
        "no_metric_values_emitted": True,
        "no_expected_distances_included": True,
        "computation_receipt_sealed": True,
        "operator_approval_on_record": True,
        "source_computation_receipt_hash": SOURCE_COMPUTATION_RECEIPT_HASH,
        "computation_receipt_review_status": "COMPLETE",
    }


def default_computation_scope_review() -> dict[str, Any]:
    return {
        "computation_scope": "BOUNDED_FIXTURE_ONLY",
        "scope_restricted_to": [
            "valid_fixture_inputs_only",
            "shadow_lane_only",
            "no_production_data",
            "no_runtime_mutation",
            "no_forecast_influence",
        ],
        "excluded_scopes": [
            "p43_surface_lanes",
            "production_activation",
            "canon_promotion",
            "metric_value_emission",
            "expected_distance_addition",
            "execution_authority",
            "inference_authority",
        ],
        "computation_scope_status": "ELIGIBLE_FOR_BOUNDED_AUTHORIZATION",
    }


def default_authority_lock_review() -> dict[str, Any]:
    return {
        "all_authority_locks_preserved": True,
        "advisory_only_confirmed": True,
        "shadow_lane_only_confirmed": True,
        "no_metric_emission_confirmed": True,
        "no_production_activation_confirmed": True,
        "no_canon_promotion_confirmed": True,
        "no_runtime_mutation_confirmed": True,
        "authority_lock_review_status": "PASS",
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
        "authorization_review_only": True,
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
        raise ChamferDistanceComputationAuthorizationReviewError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------


def validate_chamfer_distance_computation_authorization_review(
    packet: dict[str, Any],
) -> None:
    if packet.get("schema_version") != SCHEMA_VERSION:
        raise ChamferDistanceComputationAuthorizationReviewError("invalid_schema_version")
    if packet.get("review_type") != REVIEW_TYPE:
        raise ChamferDistanceComputationAuthorizationReviewError("invalid_review_type")
    if packet.get("operator_id") != OPERATOR_ID:
        raise ChamferDistanceComputationAuthorizationReviewError("invalid_operator_id")
    if packet.get("intended_lane") not in ALLOWED_LANE:
        raise ChamferDistanceComputationAuthorizationReviewError("invalid_lane")
    if packet.get("review_stage") not in ALLOWED_REVIEW_STAGE:
        raise ChamferDistanceComputationAuthorizationReviewError("invalid_review_stage")
    al = packet.get("authority_locks", {})
    if al.get("emits_metric_values") is not False:
        raise ChamferDistanceComputationAuthorizationReviewError("authority_lock_violation")
    if al.get("production_activation") is not False:
        raise ChamferDistanceComputationAuthorizationReviewError("authority_lock_violation")
    if al.get("canon_promotion") is not False:
        raise ChamferDistanceComputationAuthorizationReviewError("authority_lock_violation")
    _assert_safe(packet.get("provenance", {}))


# ---------------------------------------------------------------------------
# Build / hash / serialize
# ---------------------------------------------------------------------------


def compute_chamfer_distance_computation_authorization_review_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_chamfer_distance_computation_authorization_review(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(packet)


def build_chamfer_distance_computation_authorization_review(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base = {
        "schema_version": SCHEMA_VERSION,
        "review_type": REVIEW_TYPE,
        "operator_id": OPERATOR_ID,
        **payload,
    }
    base["canonical_hash"] = compute_chamfer_distance_computation_authorization_review_hash(base)
    validate_chamfer_distance_computation_authorization_review(base)
    return _finalize(base)
