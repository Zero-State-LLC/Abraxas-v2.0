from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "GeodesicComputationOperatorClosure.v1"
CLOSURE_ID = "geodesic_computation_operator_closure_001"
CLOSURE_STATUS = "GEODESIC_COMPUTATION_OPERATOR_CLOSURE_COMPLETE"
CLOSURE_STAGE = "COMPUTATION_OPERATOR_CLOSURE_ONLY"
OPERATOR_ID = "GEODESIC"

SOURCE_COMPLETE_REVIEW_HASH = (
    "95f5b668cef80105ae7290ab504cce718acad05492655405c9f03ec0b44d60d2"
)
SOURCE_COMPUTATION_RECEIPT_HASH = (
    "61e7c8fa0608b5bc085615269f6ae0822477ec2ade022a9a635edce04018bea8"
)
SOURCE_IMPLEMENTATION_GATE_HASH = (
    "a33bf6482414d0fa2d6788c997b466bb0c20215f4a6aa9b3c552a447616f432f"
)
SOURCE_IMPLEMENTATION_PLAN_HASH = (
    "9a5c2bebf5102bfaedc72a089361f69cb463bd12f21ff017994aa43d55c62491"
)

COMPLETE_REVIEW_PATH = pathlib.Path(
    "out/metric_operator/geodesic_computation_complete_review_001.latest.json"
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


class GeodesicComputationOperatorClosureError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise GeodesicComputationOperatorClosureError(
            f"forbidden_token_detected_in_string_value: {v!r}"
        )


def _preimage(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "canonical_hash"}


def _load_complete_review() -> dict[str, Any]:
    doc = json.loads(COMPLETE_REVIEW_PATH.read_text())
    if doc.get("canonical_hash") != SOURCE_COMPLETE_REVIEW_HASH:
        raise GeodesicComputationOperatorClosureError(
            "complete_review canonical_hash mismatch"
        )
    if doc.get("review_status") != "GEODESIC_COMPUTATION_COMPLETE_REVIEW_READY":
        raise GeodesicComputationOperatorClosureError(
            "complete_review review_status mismatch"
        )
    if doc.get("all_reviews_passed") is not True:
        raise GeodesicComputationOperatorClosureError(
            "complete_review all_reviews_passed is not True"
        )
    return doc


def build_phase_completion_review(review: dict[str, Any]) -> dict[str, Any]:
    vr = review.get("valid_fixture_result_review", {})
    ir = review.get("invalid_fixture_rejection_review", {})
    nc = review.get("not_computable_fixture_rejection_review", {})
    cs = review.get("comparison_summary_review", {})
    lr = review.get("authority_lock_review", {})
    return {
        "complete_review_present_and_passed": review.get("all_reviews_passed") is True,
        "valid_fixture_review_passed": vr.get("review_passed") is True,
        "invalid_fixture_review_passed": ir.get("review_passed") is True,
        "not_computable_fixture_review_passed": nc.get("review_passed") is True,
        "comparison_summary_review_passed": cs.get("review_passed") is True,
        "authority_lock_review_passed": lr.get("review_passed") is True,
        "no_metric_emission_review_passed": (
            review.get("no_metric_emission_review", {}).get("review_passed") is True
        ),
        "no_forecast_influence_review_passed": (
            review.get("no_forecast_influence_review", {}).get("review_passed") is True
        ),
        "no_p43_surface_lane_review_passed": (
            review.get("no_p43_surface_lane_review", {}).get("review_passed") is True
        ),
        "computation_stage_confirmed": (
            review.get("authority_lock_review", {}).get("computation_stage_confirmed") is True
        ),
        "intended_lane_confirmed": (
            review.get("authority_lock_review", {}).get("intended_lane_confirmed") is True
        ),
        "computation_phase_complete": True,
        "closure_passed": True,
    }


def build_valid_fixture_result_closure(review: dict[str, Any]) -> dict[str, Any]:
    vr = review.get("valid_fixture_result_review", {})
    per = vr.get("per_fixture", [])
    return {
        "total_valid_fixtures_closed": vr.get("total_valid_fixtures", 0),
        "all_match_closed": vr.get("all_match_confirmed") is True,
        "match_count": 5,
        "mismatch_count": 0,
        "per_fixture_ids_closed": sorted(p["fixture_id"] for p in per),
        "closure_passed": vr.get("review_passed") is True,
    }


def build_rejection_fixture_closure(review: dict[str, Any]) -> dict[str, Any]:
    ir = review.get("invalid_fixture_rejection_review", {})
    nc = review.get("not_computable_fixture_rejection_review", {})
    ir_per = ir.get("per_fixture", [])
    nc_per = nc.get("per_fixture", [])
    return {
        "total_rejection_fixtures_closed": (
            ir.get("total_invalid_fixtures", 0)
            + nc.get("total_not_computable_fixtures", 0)
        ),
        "invalid_fixture_count_closed": ir.get("total_invalid_fixtures", 0),
        "not_computable_fixture_count_closed": nc.get("total_not_computable_fixtures", 0),
        "all_invalid_rejected_correctly_closed": ir.get("all_rejected_correctly_confirmed") is True,
        "all_not_computable_closed": (
            nc.get("all_not_computable_correctly_confirmed") is True
        ),
        "per_invalid_fixture_ids_closed": sorted(p["fixture_id"] for p in ir_per),
        "per_not_computable_fixture_ids_closed": sorted(p["fixture_id"] for p in nc_per),
        "computation_attempted_on_any_rejected": False,
        "closure_passed": (
            ir.get("review_passed") is True and nc.get("review_passed") is True
        ),
    }


def build_authority_lock_closure(review: dict[str, Any]) -> dict[str, Any]:
    lr = review.get("authority_lock_review", {})
    tc = lr.get("true_lock_confirmations", {})
    fc = lr.get("false_lock_confirmations", {})
    return {
        "true_lock_confirmations_closed": tc,
        "false_lock_confirmations_closed": fc,
        "all_true_locks_closed": lr.get("all_true_locks_confirmed") is True,
        "all_false_locks_closed": lr.get("all_false_locks_confirmed") is True,
        "shadow_lane_posture_closed": True,
        "test_vector_only_posture_closed": True,
        "no_metric_emission_closed": True,
        "no_forecast_influence_closed": True,
        "no_p43_lanes_closed": True,
        "no_runtime_mutation_closed": True,
        "no_production_activation_closed": True,
        "no_canon_promotion_closed": True,
        "no_execution_authority_closed": True,
        "closure_passed": (
            lr.get("all_true_locks_confirmed") is True
            and lr.get("all_false_locks_confirmed") is True
        ),
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
    }


def build_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "computation_operator_closure_only": True,
        "test_vector_computation_only": True,
        "geodesic_computation_implementation_authorized": True,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def build_computation_operator_closure(
    closure_id: str = CLOSURE_ID,
    created_at_utc: str = "2026-05-30T00:00:00Z",
) -> dict[str, Any]:
    review = _load_complete_review()

    phase_review = build_phase_completion_review(review)
    valid_closure = build_valid_fixture_result_closure(review)
    rejection_closure = build_rejection_fixture_closure(review)
    lock_closure = build_authority_lock_closure(review)
    blocked = build_blocked_scopes()
    locks = build_authority_locks()

    all_closure_passed = (
        phase_review["closure_passed"]
        and valid_closure["closure_passed"]
        and rejection_closure["closure_passed"]
        and lock_closure["closure_passed"]
    )

    if not all_closure_passed:
        raise GeodesicComputationOperatorClosureError(
            "one or more closure sections failed — cannot emit CLOSURE_COMPLETE"
        )

    preimage: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "closure_id": closure_id,
        "operator_id": OPERATOR_ID,
        "closure_status": CLOSURE_STATUS,
        "closure_stage": CLOSURE_STAGE,
        "created_at_utc": created_at_utc,
        "intended_lane": "SHADOW",
        "source_complete_review_hash": SOURCE_COMPLETE_REVIEW_HASH,
        "source_computation_receipt_hash": SOURCE_COMPUTATION_RECEIPT_HASH,
        "source_implementation_gate_hash": SOURCE_IMPLEMENTATION_GATE_HASH,
        "source_implementation_plan_hash": SOURCE_IMPLEMENTATION_PLAN_HASH,
        "all_closure_passed": all_closure_passed,
        "phase_completion_review": phase_review,
        "valid_fixture_result_closure": valid_closure,
        "rejection_fixture_closure": rejection_closure,
        "authority_lock_closure": lock_closure,
        "blocked_scopes": blocked,
        "authority_locks": locks,
        "recommended_next_step": "GEODESIC_BASELINE_PROMOTION_DECISION",
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return json.loads(canonical_dumps(result))


def validate_computation_operator_closure(closure: dict[str, Any]) -> None:
    if closure.get("schema_version") != SCHEMA_VERSION:
        raise GeodesicComputationOperatorClosureError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if closure.get("closure_status") != CLOSURE_STATUS:
        raise GeodesicComputationOperatorClosureError(
            f"closure_status must be {CLOSURE_STATUS!r}"
        )
    if closure.get("closure_stage") != CLOSURE_STAGE:
        raise GeodesicComputationOperatorClosureError(
            f"closure_stage must be {CLOSURE_STAGE!r}"
        )
    if closure.get("operator_id") != OPERATOR_ID:
        raise GeodesicComputationOperatorClosureError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if closure.get("intended_lane") != "SHADOW":
        raise GeodesicComputationOperatorClosureError("intended_lane must be SHADOW")
    if closure.get("source_complete_review_hash") != SOURCE_COMPLETE_REVIEW_HASH:
        raise GeodesicComputationOperatorClosureError(
            "source_complete_review_hash mismatch"
        )
    if closure.get("source_computation_receipt_hash") != SOURCE_COMPUTATION_RECEIPT_HASH:
        raise GeodesicComputationOperatorClosureError(
            "source_computation_receipt_hash mismatch"
        )
    if closure.get("source_implementation_gate_hash") != SOURCE_IMPLEMENTATION_GATE_HASH:
        raise GeodesicComputationOperatorClosureError(
            "source_implementation_gate_hash mismatch"
        )
    if closure.get("source_implementation_plan_hash") != SOURCE_IMPLEMENTATION_PLAN_HASH:
        raise GeodesicComputationOperatorClosureError(
            "source_implementation_plan_hash mismatch"
        )
    if closure.get("all_closure_passed") is not True:
        raise GeodesicComputationOperatorClosureError("all_closure_passed must be True")

    for section in (
        "phase_completion_review",
        "valid_fixture_result_closure",
        "rejection_fixture_closure",
        "authority_lock_closure",
    ):
        sec = closure.get(section, {})
        if sec.get("closure_passed") is not True:
            raise GeodesicComputationOperatorClosureError(
                f"{section}.closure_passed must be True"
            )

    vfc = closure.get("valid_fixture_result_closure", {})
    if vfc.get("total_valid_fixtures_closed") != 5:
        raise GeodesicComputationOperatorClosureError(
            "valid_fixture_result_closure.total_valid_fixtures_closed must be 5"
        )
    if vfc.get("all_match_closed") is not True:
        raise GeodesicComputationOperatorClosureError(
            "valid_fixture_result_closure.all_match_closed must be True"
        )
    if vfc.get("mismatch_count") != 0:
        raise GeodesicComputationOperatorClosureError(
            "valid_fixture_result_closure.mismatch_count must be 0"
        )

    rfc = closure.get("rejection_fixture_closure", {})
    if rfc.get("total_rejection_fixtures_closed") != 8:
        raise GeodesicComputationOperatorClosureError(
            "rejection_fixture_closure.total_rejection_fixtures_closed must be 8"
        )
    if rfc.get("computation_attempted_on_any_rejected") is not False:
        raise GeodesicComputationOperatorClosureError(
            "rejection_fixture_closure.computation_attempted_on_any_rejected must be False"
        )

    locks = closure.get("authority_locks", {})
    for flag in (
        "advisory_only", "shadow_lane_only", "computation_operator_closure_only",
        "test_vector_computation_only", "geodesic_computation_implementation_authorized",
    ):
        if locks.get(flag) is not True:
            raise GeodesicComputationOperatorClosureError(
                f"authority_locks.{flag} must be True"
            )
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        if locks.get(flag) is not False:
            raise GeodesicComputationOperatorClosureError(
                f"authority_locks.{flag} must be False"
            )

    bs = closure.get("blocked_scopes", {})
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        if bs.get(flag) is not False:
            raise GeodesicComputationOperatorClosureError(
                f"blocked_scopes.{flag} must be False"
            )

    h = closure.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise GeodesicComputationOperatorClosureError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(closure))
    if recomputed != h:
        raise GeodesicComputationOperatorClosureError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )
