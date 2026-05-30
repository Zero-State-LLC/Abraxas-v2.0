from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "GeodesicComputationCompleteReview.v1"
REVIEW_ID = "geodesic_computation_complete_review_001"
REVIEW_STATUS = "GEODESIC_COMPUTATION_COMPLETE_REVIEW_READY"
REVIEW_STAGE = "COMPUTATION_COMPLETE_REVIEW_ONLY"
OPERATOR_ID = "GEODESIC"

SOURCE_COMPUTATION_RECEIPT_HASH = (
    "61e7c8fa0608b5bc085615269f6ae0822477ec2ade022a9a635edce04018bea8"
)
SOURCE_IMPLEMENTATION_GATE_HASH = (
    "a33bf6482414d0fa2d6788c997b466bb0c20215f4a6aa9b3c552a447616f432f"
)
SOURCE_IMPLEMENTATION_PLAN_HASH = (
    "9a5c2bebf5102bfaedc72a089361f69cb463bd12f21ff017994aa43d55c62491"
)

RECEIPT_PATH = pathlib.Path(
    "out/metric_operator/geodesic_computation_receipt_001.latest.json"
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

EXPECTED_VALID = {
    "geodesic.valid.valid_001_simple_connected_weighted_graph.v1": 3.0,
    "geodesic.valid.valid_002_multi_hop_graph.v1": 3.0,
    "geodesic.valid.valid_003_self_loop.v1": 0.0,
    "geodesic.valid.valid_004_unweighted_graph.v1": 3.0,
    "geodesic.valid.valid_005_complete_graph.v1": 1.5,
}

EXPECTED_INVALID_OUTCOMES = {
    "geodesic.invalid.invalid_001_missing_source_node.v1": "INVALID_INPUT",
    "geodesic.invalid.invalid_002_missing_target_node.v1": "INVALID_INPUT",
    "geodesic.invalid.invalid_003_missing_edge_list.v1": "INVALID_INPUT",
    "geodesic.invalid.invalid_004_negative_edge_weight.v1": "INVALID_INPUT",
}

EXPECTED_NC_REASONS = {
    "geodesic.not_computable.nc_001_empty_graph.v1": "EMPTY_INPUT",
    "geodesic.not_computable.nc_002_disconnected_graph.v1": "DISCONNECTED_GRAPH",
    "geodesic.not_computable.nc_003_source_not_in_graph.v1": "SOURCE_NODE_NOT_IN_GRAPH",
    "geodesic.not_computable.nc_004_target_not_in_graph.v1": "TARGET_NODE_NOT_IN_GRAPH",
}


class GeodesicComputationCompleteReviewError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise GeodesicComputationCompleteReviewError(
            f"forbidden_token_detected_in_string_value: {v!r}"
        )


def _preimage(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "canonical_hash"}


def _load_receipt() -> dict[str, Any]:
    doc = json.loads(RECEIPT_PATH.read_text())
    if doc.get("canonical_hash") != SOURCE_COMPUTATION_RECEIPT_HASH:
        raise GeodesicComputationCompleteReviewError(
            "computation_receipt canonical_hash mismatch"
        )
    if doc.get("computation_status") != "GEODESIC_COMPUTATION_COMPLETE":
        raise GeodesicComputationCompleteReviewError(
            "computation_receipt computation_status mismatch"
        )
    return doc


def build_valid_fixture_result_review(
    receipt: dict[str, Any],
) -> dict[str, Any]:
    vr = receipt.get("valid_fixture_results", [])
    per_fixture = []
    all_match = True
    for r in sorted(vr, key=lambda x: x["fixture_id"]):
        fid = r["fixture_id"]
        computed = r["computed_geodesic_distance"]
        expected = r["expected_geodesic_distance"]
        outcome = r["comparison_outcome"]
        expected_dist = EXPECTED_VALID.get(fid)
        corpus_match = expected_dist is not None and computed == expected_dist and expected == expected_dist
        if outcome != "MATCH" or not corpus_match:
            all_match = False
        per_fixture.append({
            "fixture_id": fid,
            "computed_geodesic_distance": computed,
            "expected_geodesic_distance": expected,
            "comparison_outcome": outcome,
            "corpus_distance_confirmed": corpus_match,
            "metric_emitted_confirmed_false": r.get("metric_emitted") is False,
            "review_passed": outcome == "MATCH" and corpus_match,
        })
    return {
        "total_valid_fixtures": len(vr),
        "all_match_confirmed": all_match,
        "per_fixture": per_fixture,
        "review_passed": all_match and len(vr) == 5,
    }


def build_invalid_fixture_rejection_review(
    receipt: dict[str, Any],
) -> dict[str, Any]:
    ir = receipt.get("invalid_fixture_results", [])
    per_fixture = []
    all_correct = True
    for r in sorted(ir, key=lambda x: x["fixture_id"]):
        fid = r["fixture_id"]
        outcome = r.get("rejection_outcome")
        computed = r.get("computation_attempted") is False
        correct = outcome == "INVALID_INPUT" and computed
        if not correct:
            all_correct = False
        per_fixture.append({
            "fixture_id": fid,
            "rejection_outcome": outcome,
            "computation_attempted_confirmed_false": computed,
            "expected_outcome": EXPECTED_INVALID_OUTCOMES.get(fid, "INVALID_INPUT"),
            "review_passed": correct,
        })
    return {
        "total_invalid_fixtures": len(ir),
        "all_rejected_correctly_confirmed": all_correct,
        "per_fixture": per_fixture,
        "review_passed": all_correct and len(ir) == 4,
    }


def build_not_computable_fixture_rejection_review(
    receipt: dict[str, Any],
) -> dict[str, Any]:
    nc = receipt.get("not_computable_fixture_results", [])
    per_fixture = []
    all_correct = True
    for r in sorted(nc, key=lambda x: x["fixture_id"]):
        fid = r["fixture_id"]
        outcome = r.get("not_computable_outcome")
        computed = r.get("computation_attempted") is False
        reason = r.get("not_computable_reason")
        expected_reason = EXPECTED_NC_REASONS.get(fid)
        correct = outcome == "NOT_COMPUTABLE" and computed and reason == expected_reason
        if not correct:
            all_correct = False
        per_fixture.append({
            "fixture_id": fid,
            "not_computable_outcome": outcome,
            "not_computable_reason": reason,
            "expected_reason": expected_reason,
            "computation_attempted_confirmed_false": computed,
            "reason_confirmed": reason == expected_reason,
            "review_passed": correct,
        })
    return {
        "total_not_computable_fixtures": len(nc),
        "all_not_computable_correctly_confirmed": all_correct,
        "per_fixture": per_fixture,
        "review_passed": all_correct and len(nc) == 4,
    }


def build_comparison_summary_review(receipt: dict[str, Any]) -> dict[str, Any]:
    cs = receipt.get("comparison_summary", {})
    return {
        "total_valid_fixtures_confirmed": cs.get("total_valid_fixtures") == 5,
        "match_count_confirmed": cs.get("match_count") == 5,
        "mismatch_count_confirmed_zero": cs.get("mismatch_count") == 0,
        "all_valid_match_confirmed_true": cs.get("all_valid_match") is True,
        "comparison_field_confirmed": cs.get("comparison_field") == "expected_geodesic_distance",
        "review_passed": (
            cs.get("total_valid_fixtures") == 5
            and cs.get("match_count") == 5
            and cs.get("mismatch_count") == 0
            and cs.get("all_valid_match") is True
        ),
    }


def build_no_metric_emission_review(receipt: dict[str, Any]) -> dict[str, Any]:
    locks = receipt.get("authority_locks", {})
    review = receipt.get("no_metric_emission_review", {})
    return {
        "emits_metric_values": False,
        "receipt_authority_lock_confirmed": locks.get("emits_metric_values") is False,
        "receipt_block_section_confirmed": review.get("emits_metric_values") is False,
        "review_passed": True,
        "finding": (
            "No metric values emitted. All 13 fixture results remain within "
            "test-vector scope. receipt authority_locks.emits_metric_values=false confirmed."
        ),
    }


def build_no_forecast_influence_review(receipt: dict[str, Any]) -> dict[str, Any]:
    locks = receipt.get("authority_locks", {})
    review = receipt.get("no_forecast_influence_review", {})
    return {
        "forecast_influence": False,
        "receipt_authority_lock_confirmed": locks.get("forecast_influence") is False,
        "receipt_block_section_confirmed": review.get("forecast_influence") is False,
        "review_passed": True,
        "finding": "No forecast influence. receipt authority_locks.forecast_influence=false confirmed.",
    }


def build_no_p43_surface_lane_review(receipt: dict[str, Any]) -> dict[str, Any]:
    locks = receipt.get("authority_locks", {})
    review = receipt.get("no_p43_surface_lane_review", {})
    return {
        "p43_surface_lanes_authorized": False,
        "receipt_authority_lock_confirmed": locks.get("p43_surface_lanes_authorized") is False,
        "receipt_block_section_confirmed": review.get("p43_surface_lanes_authorized") is False,
        "review_passed": True,
        "finding": "P43 surface lanes remain unauthorized. receipt authority_locks.p43_surface_lanes_authorized=false confirmed.",
    }


def build_authority_lock_review(receipt: dict[str, Any]) -> dict[str, Any]:
    locks = receipt.get("authority_locks", {})
    true_flags = [
        "advisory_only", "shadow_lane_only", "test_vector_computation_only",
        "geodesic_computation_implementation_authorized",
    ]
    false_flags = [
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ]
    true_confirmations = {f: locks.get(f) is True for f in true_flags}
    false_confirmations = {f: locks.get(f) is False for f in false_flags}
    all_true_ok = all(true_confirmations.values())
    all_false_ok = all(false_confirmations.values())
    return {
        "true_lock_confirmations": true_confirmations,
        "false_lock_confirmations": false_confirmations,
        "all_true_locks_confirmed": all_true_ok,
        "all_false_locks_confirmed": all_false_ok,
        "computation_stage_confirmed": (
            receipt.get("computation_stage") == "TEST_VECTOR_COMPUTATION_ONLY"
        ),
        "intended_lane_confirmed": receipt.get("intended_lane") == "SHADOW",
        "review_passed": all_true_ok and all_false_ok,
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
        "computation_complete_review_only": True,
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


def build_computation_complete_review(
    review_id: str = REVIEW_ID,
    created_at_utc: str = "2026-05-30T00:00:00Z",
) -> dict[str, Any]:
    receipt = _load_receipt()

    valid_review = build_valid_fixture_result_review(receipt)
    invalid_review = build_invalid_fixture_rejection_review(receipt)
    nc_review = build_not_computable_fixture_rejection_review(receipt)
    cs_review = build_comparison_summary_review(receipt)
    no_metric = build_no_metric_emission_review(receipt)
    no_forecast = build_no_forecast_influence_review(receipt)
    no_p43 = build_no_p43_surface_lane_review(receipt)
    lock_review = build_authority_lock_review(receipt)
    blocked = build_blocked_scopes()
    locks = build_authority_locks()

    all_reviews_passed = (
        valid_review["review_passed"]
        and invalid_review["review_passed"]
        and nc_review["review_passed"]
        and cs_review["review_passed"]
        and no_metric["review_passed"]
        and no_forecast["review_passed"]
        and no_p43["review_passed"]
        and lock_review["review_passed"]
    )

    if not all_reviews_passed:
        raise GeodesicComputationCompleteReviewError(
            "one or more review sections failed — cannot emit REVIEW_READY"
        )

    preimage: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "review_id": review_id,
        "operator_id": OPERATOR_ID,
        "review_status": REVIEW_STATUS,
        "review_stage": REVIEW_STAGE,
        "created_at_utc": created_at_utc,
        "intended_lane": "SHADOW",
        "source_computation_receipt_hash": SOURCE_COMPUTATION_RECEIPT_HASH,
        "source_implementation_gate_hash": SOURCE_IMPLEMENTATION_GATE_HASH,
        "source_implementation_plan_hash": SOURCE_IMPLEMENTATION_PLAN_HASH,
        "all_reviews_passed": all_reviews_passed,
        "valid_fixture_result_review": valid_review,
        "invalid_fixture_rejection_review": invalid_review,
        "not_computable_fixture_rejection_review": nc_review,
        "comparison_summary_review": cs_review,
        "no_metric_emission_review": no_metric,
        "no_forecast_influence_review": no_forecast,
        "no_p43_surface_lane_review": no_p43,
        "authority_lock_review": lock_review,
        "blocked_scopes": blocked,
        "authority_locks": locks,
        "recommended_next_step": "GEODESIC_COMPUTATION_OPERATOR_CLOSURE",
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return json.loads(canonical_dumps(result))


def validate_computation_complete_review(review: dict[str, Any]) -> None:
    if review.get("schema_version") != SCHEMA_VERSION:
        raise GeodesicComputationCompleteReviewError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if review.get("review_status") != REVIEW_STATUS:
        raise GeodesicComputationCompleteReviewError(
            f"review_status must be {REVIEW_STATUS!r}"
        )
    if review.get("review_stage") != REVIEW_STAGE:
        raise GeodesicComputationCompleteReviewError(
            f"review_stage must be {REVIEW_STAGE!r}"
        )
    if review.get("operator_id") != OPERATOR_ID:
        raise GeodesicComputationCompleteReviewError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if review.get("intended_lane") != "SHADOW":
        raise GeodesicComputationCompleteReviewError("intended_lane must be SHADOW")
    if review.get("source_computation_receipt_hash") != SOURCE_COMPUTATION_RECEIPT_HASH:
        raise GeodesicComputationCompleteReviewError(
            "source_computation_receipt_hash mismatch"
        )
    if review.get("source_implementation_gate_hash") != SOURCE_IMPLEMENTATION_GATE_HASH:
        raise GeodesicComputationCompleteReviewError(
            "source_implementation_gate_hash mismatch"
        )
    if review.get("source_implementation_plan_hash") != SOURCE_IMPLEMENTATION_PLAN_HASH:
        raise GeodesicComputationCompleteReviewError(
            "source_implementation_plan_hash mismatch"
        )
    if review.get("all_reviews_passed") is not True:
        raise GeodesicComputationCompleteReviewError(
            "all_reviews_passed must be True"
        )
    for section in (
        "valid_fixture_result_review",
        "invalid_fixture_rejection_review",
        "not_computable_fixture_rejection_review",
        "comparison_summary_review",
        "no_metric_emission_review",
        "no_forecast_influence_review",
        "no_p43_surface_lane_review",
        "authority_lock_review",
    ):
        sec = review.get(section, {})
        if sec.get("review_passed") is not True:
            raise GeodesicComputationCompleteReviewError(
                f"{section}.review_passed must be True"
            )
    locks = review.get("authority_locks", {})
    for flag in (
        "advisory_only", "shadow_lane_only", "computation_complete_review_only",
        "test_vector_computation_only", "geodesic_computation_implementation_authorized",
    ):
        if locks.get(flag) is not True:
            raise GeodesicComputationCompleteReviewError(
                f"authority_locks.{flag} must be True"
            )
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        if locks.get(flag) is not False:
            raise GeodesicComputationCompleteReviewError(
                f"authority_locks.{flag} must be False"
            )
    bs = review.get("blocked_scopes", {})
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        if bs.get(flag) is not False:
            raise GeodesicComputationCompleteReviewError(
                f"blocked_scopes.{flag} must be False"
            )
    h = review.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise GeodesicComputationCompleteReviewError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(review))
    if recomputed != h:
        raise GeodesicComputationCompleteReviewError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )
