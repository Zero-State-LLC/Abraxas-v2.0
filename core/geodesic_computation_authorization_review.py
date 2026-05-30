from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "GeodesicComputationAuthorizationReview.v1"
REVIEW_ID = "geodesic_computation_authorization_review_001"
REVIEW_STATUS = "GEODESIC_COMPUTATION_AUTHORIZATION_REVIEW_READY"
REVIEW_STAGE = "COMPUTATION_AUTHORIZATION_REVIEW_ONLY"
OPERATOR_ID = "GEODESIC"

SOURCE_COMPLETE_REVIEW_HASH = (
    "6725e3c494726bae452619e2b0e235a25761aea27262668a1548cd62d5feeb5a"
)
SOURCE_ADDITION_RECEIPT_HASH = (
    "37de3d6c5f1051d997bfe1efad2874b929a582904c94fbcfb3a0151900d7f331"
)
SOURCE_GATE_HASH = (
    "1b234f27f43f7bbddbd53d272b3c84d1f84bd3239a95289db42101b2c1ec88a0"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")

COMPLETE_REVIEW_PATH = pathlib.Path(
    "out/metric_operator/geodesic_expected_values_complete_review_001.latest.json"
)
ADDITION_RECEIPT_PATH = pathlib.Path(
    "out/metric_operator/geodesic_expected_values_addition_receipt_001.latest.json"
)

DECLARED_EXPECTED_VALUES: dict[str, float] = {
    "geodesic.valid.valid_001_simple_connected_weighted_graph.v1": 3.0,
    "geodesic.valid.valid_002_multi_hop_graph.v1": 3.0,
    "geodesic.valid.valid_003_self_loop.v1": 0.0,
    "geodesic.valid.valid_004_unweighted_graph.v1": 3.0,
    "geodesic.valid.valid_005_complete_graph.v1": 1.5,
}

FORBIDDEN = (
    "geodesic-distance",
    "dijkstra-execution",
    "shortest-path-computation",
    "metric-value",
    "metric-computation",
    "fixture-file",
    "manifest-file",
    "schema-file",
    "numpy",
    "scipy",
    "gpu-kernel",
)


class GeodesicComputationAuthorizationReviewValidationError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise GeodesicComputationAuthorizationReviewValidationError(
            "forbidden_token_detected_in_string_value"
        )


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def _load_and_verify_complete_review() -> dict[str, Any]:
    doc = json.loads(COMPLETE_REVIEW_PATH.read_text())
    actual = doc.get("canonical_hash", "")
    if actual != SOURCE_COMPLETE_REVIEW_HASH:
        raise GeodesicComputationAuthorizationReviewValidationError(
            f"complete_review canonical_hash mismatch: {actual!r}"
        )
    return doc


def _load_and_verify_addition_receipt() -> dict[str, Any]:
    doc = json.loads(ADDITION_RECEIPT_PATH.read_text())
    actual = doc.get("canonical_hash", "")
    if actual != SOURCE_ADDITION_RECEIPT_HASH:
        raise GeodesicComputationAuthorizationReviewValidationError(
            f"addition_receipt canonical_hash mismatch: {actual!r}"
        )
    return doc


def build_fixture_corpus_readiness_review(complete_review: dict[str, Any]) -> dict[str, Any]:
    corpus = complete_review.get("corpus_review_summary", {})
    valid_review = complete_review.get("valid_fixture_review", {})
    return {
        "total_fixture_count": corpus.get("total_fixture_count"),
        "valid_fixture_count": corpus.get("valid_fixture_count"),
        "invalid_fixture_count": corpus.get("invalid_fixture_count"),
        "not_computable_fixture_count": corpus.get("not_computable_fixture_count"),
        "all_valid_fixtures_have_expected_distance": (
            corpus.get("valid_fixtures_with_expected_distance") == 5
        ),
        "invalid_fixtures_excluded": corpus.get("invalid_fixtures_with_expected_distance") == 0,
        "not_computable_fixtures_excluded": (
            corpus.get("not_computable_fixtures_with_expected_distance") == 0
        ),
        "corpus_consistent": corpus.get("corpus_consistent") is True,
        "all_gate_hashes_consistent": valid_review.get("all_gate_hashes_consistent") is True,
        "corpus_ready_for_computation_authorization": (
            corpus.get("valid_fixture_count") == 5
            and corpus.get("valid_fixtures_with_expected_distance") == 5
            and corpus.get("invalid_fixtures_with_expected_distance") == 0
            and corpus.get("not_computable_fixtures_with_expected_distance") == 0
            and corpus.get("corpus_consistent") is True
            and valid_review.get("all_gate_hashes_consistent") is True
        ),
    }


def build_expected_values_readiness_review(complete_review: dict[str, Any]) -> dict[str, Any]:
    valid_review = complete_review.get("valid_fixture_review", {})
    entries = valid_review.get("fixture_entries", [])
    declared_match = valid_review.get("all_values_match_declared") is True
    return {
        "declared_fixture_count": len(DECLARED_EXPECTED_VALUES),
        "all_values_match_declared": declared_match,
        "declared_values": {
            fid: ev for fid, ev in DECLARED_EXPECTED_VALUES.items()
        },
        "expected_values_source_gate_hash": SOURCE_GATE_HASH,
        "expected_values_source_gate_hash_prefix": SOURCE_GATE_HASH[:16] + "…",
        "all_fixtures_gate_consistent": valid_review.get("all_gate_hashes_consistent") is True,
        "fixture_entry_count_confirmed": len(entries) == 5,
        "expected_values_ready_for_computation_authorization": declared_match and len(entries) == 5,
    }


def build_computation_scope_review() -> dict[str, Any]:
    return {
        "intended_computation_scope": "SHADOW_STUB_ONLY",
        "computation_implementation_authorized": False,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
        "scope_finding": (
            "GEODESIC computation implementation is not authorized by this review. "
            "This artifact is advisory-only. A separate operator decision artifact "
            "is required before computation implementation may proceed."
        ),
    }


def build_authority_lock_review() -> dict[str, Any]:
    return {
        "advisory_only_confirmed": True,
        "shadow_lane_only_confirmed": True,
        "no_metric_emission_confirmed": True,
        "no_forecast_influence_confirmed": True,
        "no_p43_surface_lanes_confirmed": True,
        "no_production_activation_confirmed": True,
        "no_canon_promotion_confirmed": True,
        "no_runtime_mutation_confirmed": True,
        "no_execution_authority_confirmed": True,
        "no_inference_authority_confirmed": True,
        "authority_lock_review_finding": (
            "All authority locks verified consistent with SHADOW-only advisory posture. "
            "No locks modified by this review."
        ),
    }


def build_operator_authorization_requirement() -> dict[str, Any]:
    return {
        "separate_operator_decision_required": True,
        "operator_decision_artifact_present": False,
        "computation_blocked_pending_operator_decision": True,
        "requirement_description": (
            "GEODESIC computation implementation requires a separate operator decision artifact "
            "authorizing bounded SHADOW computation. This review recommends authorization "
            "but does not grant it. The operator decision artifact must set "
            "geodesic_computation_authorized=true before implementation may proceed."
        ),
    }


def build_authorization_recommendation(
    corpus_ready: bool,
    values_ready: bool,
) -> dict[str, Any]:
    recommend = corpus_ready and values_ready
    return {
        "recommend_geodesic_computation_authorization": recommend,
        "recommendation_basis": (
            "Fixture corpus is complete (5 valid, 4 invalid, 4 not_computable), "
            "all 5 expected values verified against gate, corpus consistent. "
            "Advisory recommendation only — does not activate computation."
        ) if recommend else (
            "Corpus or expected values readiness checks did not pass — "
            "authorization not recommended at this time."
        ),
        "geodesic_computation_authorized": False,
        "authorization_advisory_only": True,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
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
        "geodesic_computation_authorized": False,
    }


def build_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "expected_values_addition_only": True,
        "expected_geodesic_distances_authorized": True,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
        "geodesic_computation_authorized": False,
    }


def build_computation_authorization_review(
    review_id: str = REVIEW_ID,
    created_at_utc: str = "2026-05-30T00:00:00Z",
    intended_lane: str = "SHADOW",
) -> dict[str, Any]:
    if intended_lane not in ALLOWED_LANE:
        raise GeodesicComputationAuthorizationReviewValidationError(
            f"intended_lane must be one of {ALLOWED_LANE}"
        )

    complete_review = _load_and_verify_complete_review()
    _load_and_verify_addition_receipt()

    corpus_review = build_fixture_corpus_readiness_review(complete_review)
    values_review = build_expected_values_readiness_review(complete_review)
    computation_scope = build_computation_scope_review()
    lock_review = build_authority_lock_review()
    op_requirement = build_operator_authorization_requirement()
    auth_recommendation = build_authorization_recommendation(
        corpus_ready=corpus_review["corpus_ready_for_computation_authorization"],
        values_ready=values_review["expected_values_ready_for_computation_authorization"],
    )
    blocked = build_blocked_scopes()
    locks = build_authority_locks()

    preimage: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "review_id": review_id,
        "operator_id": OPERATOR_ID,
        "review_status": REVIEW_STATUS,
        "review_stage": REVIEW_STAGE,
        "created_at_utc": created_at_utc,
        "intended_lane": intended_lane,
        "source_expected_values_complete_review_hash": SOURCE_COMPLETE_REVIEW_HASH,
        "source_expected_values_addition_receipt_hash": SOURCE_ADDITION_RECEIPT_HASH,
        "source_expected_values_gate_hash": SOURCE_GATE_HASH,
        "fixture_corpus_readiness_review": corpus_review,
        "expected_values_readiness_review": values_review,
        "computation_scope_review": computation_scope,
        "authority_lock_review": lock_review,
        "operator_authorization_requirement": op_requirement,
        "authorization_recommendation": auth_recommendation,
        "blocked_scopes": blocked,
        "authority_locks": locks,
        "recommended_next_step": "GEODESIC_COMPUTATION_OPERATOR_DECISION",
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return _finalize(result)


def validate_computation_authorization_review(review: dict[str, Any]) -> None:
    if review.get("schema_version") != SCHEMA_VERSION:
        raise GeodesicComputationAuthorizationReviewValidationError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if review.get("review_status") != REVIEW_STATUS:
        raise GeodesicComputationAuthorizationReviewValidationError(
            f"review_status must be {REVIEW_STATUS!r}"
        )
    if review.get("review_stage") != REVIEW_STAGE:
        raise GeodesicComputationAuthorizationReviewValidationError(
            f"review_stage must be {REVIEW_STAGE!r}"
        )
    if review.get("operator_id") != OPERATOR_ID:
        raise GeodesicComputationAuthorizationReviewValidationError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if review.get("intended_lane") not in ALLOWED_LANE:
        raise GeodesicComputationAuthorizationReviewValidationError(
            f"intended_lane must be one of {ALLOWED_LANE}"
        )
    if review.get("source_expected_values_complete_review_hash") != SOURCE_COMPLETE_REVIEW_HASH:
        raise GeodesicComputationAuthorizationReviewValidationError(
            "source_expected_values_complete_review_hash mismatch"
        )
    if review.get("source_expected_values_addition_receipt_hash") != SOURCE_ADDITION_RECEIPT_HASH:
        raise GeodesicComputationAuthorizationReviewValidationError(
            "source_expected_values_addition_receipt_hash mismatch"
        )
    if review.get("source_expected_values_gate_hash") != SOURCE_GATE_HASH:
        raise GeodesicComputationAuthorizationReviewValidationError(
            "source_expected_values_gate_hash mismatch"
        )
    locks = review.get("authority_locks", {})
    for flag in ("advisory_only", "shadow_lane_only", "expected_values_addition_only",
                 "expected_geodesic_distances_authorized"):
        if locks.get(flag) is not True:
            raise GeodesicComputationAuthorizationReviewValidationError(
                f"authority_locks.{flag} must be True"
            )
    for flag in ("emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
                 "production_activation", "canon_promotion", "runtime_mutation",
                 "execution_authority", "inference_authority", "geodesic_computation_authorized"):
        if locks.get(flag) is not False:
            raise GeodesicComputationAuthorizationReviewValidationError(
                f"authority_locks.{flag} must be False"
            )
    auth = review.get("authorization_recommendation", {})
    if auth.get("geodesic_computation_authorized") is not False:
        raise GeodesicComputationAuthorizationReviewValidationError(
            "authorization_recommendation.geodesic_computation_authorized must be False"
        )
    if auth.get("emits_metric_values") is not False:
        raise GeodesicComputationAuthorizationReviewValidationError(
            "authorization_recommendation.emits_metric_values must be False"
        )
    bs = review.get("blocked_scopes", {})
    if bs.get("geodesic_computation_authorized") is not False:
        raise GeodesicComputationAuthorizationReviewValidationError(
            "blocked_scopes.geodesic_computation_authorized must be False"
        )
    op_req = review.get("operator_authorization_requirement", {})
    if op_req.get("separate_operator_decision_required") is not True:
        raise GeodesicComputationAuthorizationReviewValidationError(
            "operator_authorization_requirement.separate_operator_decision_required must be True"
        )
    if op_req.get("operator_decision_artifact_present") is not False:
        raise GeodesicComputationAuthorizationReviewValidationError(
            "operator_authorization_requirement.operator_decision_artifact_present must be False"
        )
    h = review.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise GeodesicComputationAuthorizationReviewValidationError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(review))
    if recomputed != h:
        raise GeodesicComputationAuthorizationReviewValidationError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )
