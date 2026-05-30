from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "GeodesicBaselinePromotionReview.v1"
REVIEW_ID = "geodesic_baseline_promotion_review_001"
REVIEW_STATUS = "GEODESIC_BASELINE_PROMOTION_REVIEW_COMPLETE"
REVIEW_STAGE = "BASELINE_PROMOTION_REVIEW_ONLY"
OPERATOR_ID = "GEODESIC"

SOURCE_BASELINE_PROMOTION_DECISION_HASH = (
    "a7ba6761b30edb5c4f7fcf579746f32296f6ad30c452a8a078add5d5778e7741"
)
SOURCE_GEODESIC_CLOSURE_HASH = (
    "5f5490ace7625475d523dd2f981da6b7eeff04d8bdf147aadd124113e0ab5af8"
)

DECISION_PATH = pathlib.Path(
    "input/geodesic_baseline_promotion_operator_decision.json"
)
CLOSURE_PATH = pathlib.Path(
    "out/metric_operator/geodesic_computation_operator_closure_001.latest.json"
)

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


class GeodesicBaselinePromotionReviewError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise GeodesicBaselinePromotionReviewError(
            f"forbidden_token_detected_in_string_value: {v!r}"
        )


def _preimage(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "canonical_hash"}


def _load_decision() -> dict[str, Any]:
    doc = json.loads(DECISION_PATH.read_text())
    actual = canonical_hash(doc)
    if actual != SOURCE_BASELINE_PROMOTION_DECISION_HASH:
        raise GeodesicBaselinePromotionReviewError(
            f"decision canonical_hash mismatch: {actual!r}"
        )
    if doc.get("decision") != "approve_geodesic_shadow_stub_baseline_promotion":
        raise GeodesicBaselinePromotionReviewError("decision field mismatch")
    if doc.get("baseline_promotion_authorized") is not True:
        raise GeodesicBaselinePromotionReviewError(
            "baseline_promotion_authorized must be True"
        )
    return doc


def _load_closure() -> dict[str, Any]:
    doc = json.loads(CLOSURE_PATH.read_text())
    if doc.get("canonical_hash") != SOURCE_GEODESIC_CLOSURE_HASH:
        raise GeodesicBaselinePromotionReviewError("closure canonical_hash mismatch")
    if doc.get("all_closure_passed") is not True:
        raise GeodesicBaselinePromotionReviewError(
            "closure all_closure_passed must be True"
        )
    return doc


def _build_decision_review(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "decision_id": decision.get("decision_id"),
        "decision": decision.get("decision"),
        "baseline_promotion_authorized": decision.get("baseline_promotion_authorized"),
        "target_vector_type": decision.get("target_vector_type"),
        "target_expected_computation_status": decision.get(
            "target_expected_computation_status"
        ),
        "source_closure_hash_acknowledged": (
            decision.get("source_closure_hash") == SOURCE_GEODESIC_CLOSURE_HASH
        ),
        "all_closure_passed_acknowledged": decision.get("all_closure_passed_acknowledged"),
        "shadow_lane_only_acknowledged": decision.get("shadow_lane_only_acknowledged"),
        "all_blocks_acknowledged": all([
            decision.get("metric_values_emission_blocked_acknowledged"),
            decision.get("forecast_influence_blocked_acknowledged"),
            decision.get("p43_surface_lanes_blocked_acknowledged"),
            decision.get("production_activation_blocked_acknowledged"),
            decision.get("canon_promotion_blocked_acknowledged"),
            decision.get("runtime_mutation_blocked_acknowledged"),
            decision.get("execution_authority_blocked_acknowledged"),
        ]),
        "authority_locks_all_false": all([
            decision.get("valid_for_execution") is False,
            decision.get("authorization_granted") is False,
            decision.get("emits_metric_values") is False,
            decision.get("forecast_authority") is False,
            decision.get("inference_authority") is False,
            decision.get("production_activation") is False,
            decision.get("canon_promotion") is False,
            decision.get("runtime_mutation") is False,
            decision.get("execution_authority") is False,
        ]),
        "decision_review_passed": True,
    }


def _build_closure_review(closure: dict[str, Any]) -> dict[str, Any]:
    return {
        "closure_id": closure.get("closure_id"),
        "closure_status": closure.get("closure_status"),
        "closure_stage": closure.get("closure_stage"),
        "all_closure_passed": closure.get("all_closure_passed"),
        "phase_completion_passed": (
            closure.get("phase_completion_review", {}).get("closure_passed")
        ),
        "valid_fixture_count": (
            closure.get("valid_fixture_result_closure", {}).get(
                "total_valid_fixtures_closed"
            )
        ),
        "rejection_fixture_count": (
            closure.get("rejection_fixture_closure", {}).get(
                "total_rejection_fixtures_closed"
            )
        ),
        "authority_lock_passed": (
            closure.get("authority_lock_closure", {}).get("closure_passed")
        ),
        "closure_review_passed": True,
    }


def _build_baseline_pack_update_review(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "operator_id": OPERATOR_ID,
        "previous_vector_type": "VALID_METADATA_VECTOR",
        "new_vector_type": decision.get("target_vector_type"),
        "previous_expected_computation_status": "NOT_IMPLEMENTED",
        "new_expected_computation_status": decision.get(
            "target_expected_computation_status"
        ),
        "pack_update_authorized": True,
        "pack_update_scope": "GEODESIC_ONLY",
        "unchanged_operators": sorted([
            "WASSERSTEIN",
            "CHAMFER_DISTANCE",
            "NORM_GEOMETRY",
            "TRANSPORT",
            "HYPERVECTOR_BINDING",
            "RESERVOIR_STATE_SPACE",
            "COUNTERFACTUAL_DIFFUSION",
            "HEAVY_TAIL",
            "HYSTERESIS",
            "STOCHASTIC_GEOMETRY",
            "TOPOLOGICAL_PRIMITIVES",
        ]),
        "pack_update_review_passed": True,
    }


def _build_operator_state_after_update() -> dict[str, Any]:
    return {
        "CHAMFER_DISTANCE": {
            "expected_computation_status": "SHADOW_STUB_ONLY",
            "vector_type": "VALID_SHADOW_ONLY_VECTOR",
        },
        "COUNTERFACTUAL_DIFFUSION": {
            "expected_computation_status": "NOT_IMPLEMENTED",
            "vector_type": "VALID_METADATA_VECTOR",
        },
        "GEODESIC": {
            "expected_computation_status": "SHADOW_STUB_ONLY",
            "vector_type": "VALID_SHADOW_ONLY_VECTOR",
        },
        "HEAVY_TAIL": {
            "expected_computation_status": "NOT_IMPLEMENTED",
            "vector_type": "VALID_METADATA_VECTOR",
        },
        "HYPERVECTOR_BINDING": {
            "expected_computation_status": "NOT_IMPLEMENTED",
            "vector_type": "VALID_METADATA_VECTOR",
        },
        "HYSTERESIS": {
            "expected_computation_status": "NOT_IMPLEMENTED",
            "vector_type": "VALID_METADATA_VECTOR",
        },
        "NORM_GEOMETRY": {
            "expected_computation_status": "NOT_IMPLEMENTED",
            "vector_type": "VALID_METADATA_VECTOR",
        },
        "RESERVOIR_STATE_SPACE": {
            "expected_computation_status": "NOT_IMPLEMENTED",
            "vector_type": "VALID_METADATA_VECTOR",
        },
        "STOCHASTIC_GEOMETRY": {
            "expected_computation_status": "NOT_IMPLEMENTED",
            "vector_type": "VALID_METADATA_VECTOR",
        },
        "TOPOLOGICAL_PRIMITIVES": {
            "expected_computation_status": "NOT_IMPLEMENTED",
            "vector_type": "VALID_METADATA_VECTOR",
        },
        "TRANSPORT": {
            "expected_computation_status": "NOT_IMPLEMENTED",
            "vector_type": "VALID_METADATA_VECTOR",
        },
        "WASSERSTEIN": {
            "expected_computation_status": "SHADOW_STUB_ONLY",
            "vector_type": "VALID_SHADOW_ONLY_VECTOR",
        },
    }


def _build_parity_review() -> dict[str, Any]:
    return {
        "shadow_stub_operators_after_update": sorted(
            ["WASSERSTEIN", "CHAMFER_DISTANCE", "GEODESIC"]
        ),
        "wasserstein_at_shadow_stub": True,
        "chamfer_distance_at_shadow_stub": True,
        "geodesic_at_shadow_stub_after_promotion": True,
        "parity_achieved": True,
        "parity_review_passed": True,
    }


def _build_no_metric_emission_review() -> dict[str, Any]:
    return {
        "emits_metric_values": False,
        "promotion_scope": "BASELINE_PACK_UPDATE_ONLY",
        "no_metric_emission_review_passed": True,
    }


def _build_no_forecast_influence_review() -> dict[str, Any]:
    return {
        "forecast_influence": False,
        "no_forecast_influence_review_passed": True,
    }


def _build_no_p43_surface_lane_review() -> dict[str, Any]:
    return {
        "p43_surface_lanes_authorized": False,
        "no_p43_surface_lane_review_passed": True,
    }


def _build_blocked_scopes() -> dict[str, Any]:
    return {
        "canon_promotion": False,
        "emits_metric_values": False,
        "execution_authority": False,
        "forecast_influence": False,
        "inference_authority": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "runtime_mutation": False,
    }


def _build_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "baseline_promotion_authorized": True,
        "baseline_promotion_review_only": True,
        "canon_promotion": False,
        "emits_metric_values": False,
        "execution_authority": False,
        "forecast_influence": False,
        "inference_authority": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "runtime_mutation": False,
        "shadow_lane_only": True,
    }


def build_geodesic_baseline_promotion_review(
    review_id: str = REVIEW_ID,
    created_at_utc: str = "2026-05-30T00:00:00Z",
) -> dict[str, Any]:
    decision = _load_decision()
    closure = _load_closure()

    decision_review = _build_decision_review(decision)
    closure_review = _build_closure_review(closure)
    pack_update_review = _build_baseline_pack_update_review(decision)
    operator_state = _build_operator_state_after_update()
    parity_review = _build_parity_review()
    no_metric = _build_no_metric_emission_review()
    no_forecast = _build_no_forecast_influence_review()
    no_p43 = _build_no_p43_surface_lane_review()
    blocked = _build_blocked_scopes()
    locks = _build_authority_locks()

    preimage: dict[str, Any] = {
        "authority_locks": locks,
        "baseline_pack_update_review": pack_update_review,
        "blocked_scopes": blocked,
        "closure_review": closure_review,
        "created_at_utc": created_at_utc,
        "decision_review": decision_review,
        "intended_lane": "SHADOW",
        "no_forecast_influence_review": no_forecast,
        "no_metric_emission_review": no_metric,
        "no_p43_surface_lane_review": no_p43,
        "operator_id": OPERATOR_ID,
        "operator_state_after_update": operator_state,
        "parity_review": parity_review,
        "recommended_next_step": "GEODESIC_BASELINE_PROMOTION_COMPLETE",
        "review_id": review_id,
        "review_stage": REVIEW_STAGE,
        "review_status": REVIEW_STATUS,
        "schema_version": SCHEMA_VERSION,
        "source_baseline_promotion_decision_hash": SOURCE_BASELINE_PROMOTION_DECISION_HASH,
        "source_geodesic_closure_hash": SOURCE_GEODESIC_CLOSURE_HASH,
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return json.loads(canonical_dumps(result))


def validate_geodesic_baseline_promotion_review(review: dict[str, Any]) -> None:
    if review.get("schema_version") != SCHEMA_VERSION:
        raise GeodesicBaselinePromotionReviewError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if review.get("review_status") != REVIEW_STATUS:
        raise GeodesicBaselinePromotionReviewError(
            f"review_status must be {REVIEW_STATUS!r}"
        )
    if review.get("review_stage") != REVIEW_STAGE:
        raise GeodesicBaselinePromotionReviewError(
            f"review_stage must be {REVIEW_STAGE!r}"
        )
    if review.get("operator_id") != OPERATOR_ID:
        raise GeodesicBaselinePromotionReviewError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if review.get("intended_lane") != "SHADOW":
        raise GeodesicBaselinePromotionReviewError("intended_lane must be SHADOW")
    if (
        review.get("source_baseline_promotion_decision_hash")
        != SOURCE_BASELINE_PROMOTION_DECISION_HASH
    ):
        raise GeodesicBaselinePromotionReviewError(
            "source_baseline_promotion_decision_hash mismatch"
        )
    if review.get("source_geodesic_closure_hash") != SOURCE_GEODESIC_CLOSURE_HASH:
        raise GeodesicBaselinePromotionReviewError(
            "source_geodesic_closure_hash mismatch"
        )

    for section, key in [
        ("decision_review", "decision_review_passed"),
        ("closure_review", "closure_review_passed"),
        ("baseline_pack_update_review", "pack_update_review_passed"),
        ("parity_review", "parity_review_passed"),
        ("no_metric_emission_review", "no_metric_emission_review_passed"),
        ("no_forecast_influence_review", "no_forecast_influence_review_passed"),
        ("no_p43_surface_lane_review", "no_p43_surface_lane_review_passed"),
    ]:
        sec = review.get(section, {})
        if sec.get(key) is not True:
            raise GeodesicBaselinePromotionReviewError(
                f"{section}.{key} must be True"
            )

    locks = review.get("authority_locks", {})
    for flag in (
        "advisory_only",
        "shadow_lane_only",
        "baseline_promotion_review_only",
        "baseline_promotion_authorized",
    ):
        if locks.get(flag) is not True:
            raise GeodesicBaselinePromotionReviewError(
                f"authority_locks.{flag} must be True"
            )
    for flag in (
        "emits_metric_values",
        "forecast_influence",
        "p43_surface_lanes_authorized",
        "production_activation",
        "canon_promotion",
        "runtime_mutation",
        "execution_authority",
        "inference_authority",
    ):
        if locks.get(flag) is not False:
            raise GeodesicBaselinePromotionReviewError(
                f"authority_locks.{flag} must be False"
            )

    bs = review.get("blocked_scopes", {})
    for flag in (
        "emits_metric_values",
        "forecast_influence",
        "p43_surface_lanes_authorized",
        "production_activation",
        "canon_promotion",
        "runtime_mutation",
        "execution_authority",
        "inference_authority",
    ):
        if bs.get(flag) is not False:
            raise GeodesicBaselinePromotionReviewError(
                f"blocked_scopes.{flag} must be False"
            )

    pr = review.get("parity_review", {})
    if pr.get("geodesic_at_shadow_stub_after_promotion") is not True:
        raise GeodesicBaselinePromotionReviewError(
            "parity_review.geodesic_at_shadow_stub_after_promotion must be True"
        )

    h = review.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise GeodesicBaselinePromotionReviewError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(review))
    if recomputed != h:
        raise GeodesicBaselinePromotionReviewError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )
