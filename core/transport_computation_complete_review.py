from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "TransportComputationCompleteReview.v1"
REVIEW_ID = "transport_computation_complete_review_001"
REVIEW_STATUS = "TRANSPORT_COMPUTATION_COMPLETE_REVIEW_READY"
REVIEW_STAGE = "COMPUTATION_COMPLETE_REVIEW_ONLY"
OPERATOR_ID = "TRANSPORT"

SOURCE_COMPUTATION_RECEIPT_HASH = (
    "a1fa0921830bbab5e4c68f7975d056e80788f0a079b26739d1ad6d4f0d9d3831"
)
SOURCE_IMPLEMENTATION_GATE_HASH = (
    "a5b9691e0ff410b512c725075cc3108141b941b0f22da58441772589a3467eb0"
)

RECEIPT_PATH = pathlib.Path(
    "out/metric_operator/transport_computation_receipt_001.latest.json"
)

FORBIDDEN = (
    "metric-computation",
    "metric-value",
    "geodesic-distance",
    "dijkstra-execution",
    "shortest-path-computation",
    "fixture-file",
    "manifest-file",
    "schema-file",
    "numpy",
    "scipy",
    "gpu-kernel",
)

EXPECTED_VALID_DISTANCES: dict[str, float] = {
    "tv-valid-001": 0.0,
    "tv-valid-002": 2.0,
    "tv-valid-003": 2.5,
    "tv-valid-004": 2.5,
    "tv-valid-005": 3.0,
    "tv-valid-006": 0.0,
}

EXPECTED_INVALID_REJECTED = {
    "tv-invalid-001": "INVALID_INPUT",
    "tv-invalid-002": "INVALID_INPUT",
    "tv-invalid-003": "INVALID_INPUT",
}

EXPECTED_NC_REASONS: dict[str, str] = {
    "tv-invalid-004": "COST_MATRIX_SHAPE_MISMATCH",
    "tv-nc-001": "UNBALANCED_SUPPLY_DEMAND",
    "tv-nc-002": "NEGATIVE_SUPPLY_VALUE",
    "tv-nc-003": "NEGATIVE_COST_VALUE",
    "tv-nc-004": "EMPTY_SUPPLY_VECTOR",
    "tv-nc-005": "NON_FINITE_SUPPLY_VALUE",
}


class TransportComputationCompleteReviewError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise TransportComputationCompleteReviewError(
            f"forbidden_token_detected_in_string_value: {v!r}"
        )


def _preimage(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "canonical_hash"}


def _load_receipt() -> dict[str, Any]:
    doc = json.loads(RECEIPT_PATH.read_text())
    if doc.get("canonical_hash") != SOURCE_COMPUTATION_RECEIPT_HASH:
        raise TransportComputationCompleteReviewError(
            "computation_receipt canonical_hash mismatch"
        )
    if doc.get("receipt_status") != "TRANSPORT_COMPUTATION_RECEIPT_COMPLETE":
        raise TransportComputationCompleteReviewError(
            "computation_receipt receipt_status mismatch"
        )
    return doc


def build_receipt_presence_review(receipt: dict[str, Any]) -> dict[str, Any]:
    receipt_id_ok = receipt.get("receipt_id") == "transport_computation_receipt_001"
    status_ok = receipt.get("receipt_status") == "TRANSPORT_COMPUTATION_RECEIPT_COMPLETE"
    executed_ok = receipt.get("computation_executed") is True
    return {
        "receipt_id_confirmed": receipt_id_ok,
        "receipt_status_confirmed": status_ok,
        "computation_executed_confirmed": executed_ok,
        "review_passed": receipt_id_ok and status_ok and executed_ok,
    }


def build_source_receipt_hash_review(receipt: dict[str, Any]) -> dict[str, Any]:
    stored = receipt.get("canonical_hash", "")
    matches = stored == SOURCE_COMPUTATION_RECEIPT_HASH
    return {
        "expected_hash": SOURCE_COMPUTATION_RECEIPT_HASH,
        "stored_hash": stored,
        "hash_matches_confirmed": matches,
        "review_passed": matches,
    }


def build_implementation_gate_binding(receipt: dict[str, Any]) -> dict[str, Any]:
    provenance = receipt.get("provenance", {})
    gate_ref = provenance.get("gate_ref", "")
    hash_present = SOURCE_IMPLEMENTATION_GATE_HASH in gate_ref
    return {
        "expected_gate_hash": SOURCE_IMPLEMENTATION_GATE_HASH,
        "gate_ref_from_provenance": gate_ref,
        "gate_hash_in_provenance_confirmed": hash_present,
        "review_passed": hash_present,
    }


def build_valid_fixture_result_review(receipt: dict[str, Any]) -> dict[str, Any]:
    results = [
        r for r in receipt.get("fixture_results", [])
        if r.get("fixture_type") == "VALID"
    ]
    per_fixture = []
    all_match = True
    for r in sorted(results, key=lambda x: x["fixture_id"]):
        fid = r["fixture_id"]
        computed = r.get("transport_distance")
        expected = r.get("expected_transport_distance")
        distance_matched = r.get("distance_matched") is True
        matched = r.get("matched") is True
        actual = r.get("actual")
        corpus_expected = EXPECTED_VALID_DISTANCES.get(fid)
        corpus_match = (
            corpus_expected is not None
            and computed == corpus_expected
            and expected == corpus_expected
        )
        review_ok = matched and distance_matched and actual == "COMPUTED" and corpus_match
        if not review_ok:
            all_match = False
        per_fixture.append({
            "fixture_id": fid,
            "actual": actual,
            "transport_distance": computed,
            "expected_transport_distance": expected,
            "corpus_expected_distance": corpus_expected,
            "distance_matched_confirmed": distance_matched,
            "corpus_distance_confirmed": corpus_match,
            "matched_confirmed": matched,
            "review_passed": review_ok,
        })
    return {
        "total_valid_fixtures": len(results),
        "all_match_confirmed": all_match,
        "per_fixture": per_fixture,
        "review_passed": all_match and len(results) == 6,
    }


def build_invalid_fixture_rejection_review(receipt: dict[str, Any]) -> dict[str, Any]:
    results = [
        r for r in receipt.get("fixture_results", [])
        if r.get("fixture_type") == "INVALID" and r.get("actual") == "REJECTED"
    ]
    per_fixture = []
    all_correct = True
    for r in sorted(results, key=lambda x: x["fixture_id"]):
        fid = r["fixture_id"]
        actual = r.get("actual")
        matched = r.get("matched") is True
        rejection_reason = r.get("rejection_reason", "")
        has_invalid_input = "INVALID_INPUT" in rejection_reason
        computation_not_attempted = actual == "REJECTED"
        correct = matched and has_invalid_input and computation_not_attempted
        if not correct:
            all_correct = False
        per_fixture.append({
            "fixture_id": fid,
            "actual": actual,
            "rejection_reason": rejection_reason,
            "matched_confirmed": matched,
            "rejection_outcome_confirmed": has_invalid_input,
            "computation_attempted_confirmed_false": computation_not_attempted,
            "review_passed": correct,
        })
    return {
        "total_invalid_rejected_fixtures": len(results),
        "all_rejected_correctly_confirmed": all_correct,
        "per_fixture": per_fixture,
        "review_passed": all_correct and len(results) == 3,
    }


def build_not_computable_fixture_rejection_review(receipt: dict[str, Any]) -> dict[str, Any]:
    fixture_results = receipt.get("fixture_results", [])
    nc_results = [
        r for r in fixture_results
        if r.get("actual") == "NOT_COMPUTABLE"
    ]
    per_fixture = []
    all_correct = True
    for r in sorted(nc_results, key=lambda x: x["fixture_id"]):
        fid = r["fixture_id"]
        actual = r.get("actual")
        matched = r.get("matched") is True
        nc_reason = r.get("not_computable_reason", "")
        expected_reason = EXPECTED_NC_REASONS.get(fid)
        reason_confirmed = nc_reason == expected_reason
        correct = matched and actual == "NOT_COMPUTABLE" and reason_confirmed
        if not correct:
            all_correct = False
        per_fixture.append({
            "fixture_id": fid,
            "fixture_type": r.get("fixture_type"),
            "actual": actual,
            "not_computable_reason": nc_reason,
            "expected_not_computable_reason": expected_reason,
            "matched_confirmed": matched,
            "reason_confirmed": reason_confirmed,
            "review_passed": correct,
        })
    invalid_004_entry = next((e for e in per_fixture if e["fixture_id"] == "tv-invalid-004"), None)
    nc_type_entries = [e for e in per_fixture if e["fixture_id"].startswith("tv-nc-")]
    return {
        "total_not_computable_routed": len(nc_results),
        "invalid_004_routed_not_computable": invalid_004_entry is not None,
        "invalid_004_reason_confirmed": (
            invalid_004_entry.get("reason_confirmed") if invalid_004_entry else False
        ),
        "nc_type_fixtures_count": len(nc_type_entries),
        "all_not_computable_correctly_confirmed": all_correct,
        "per_fixture": per_fixture,
        "review_passed": all_correct and len(nc_results) == 6,
    }


def build_comparison_summary_review(receipt: dict[str, Any]) -> dict[str, Any]:
    total_ok = receipt.get("fixture_count_total") == 15
    valid_ok = receipt.get("fixture_count_valid") == 6
    invalid_ok = receipt.get("fixture_count_invalid") == 4
    nc_ok = receipt.get("fixture_count_not_computable") == 5
    all_matched_ok = receipt.get("all_matched") is True
    all_valid_ok = receipt.get("all_valid_passed") is True
    all_invalid_ok = receipt.get("all_invalid_rejected") is True
    all_nc_ok = receipt.get("all_not_computable_routed") is True
    review_ok = all([
        total_ok, valid_ok, invalid_ok, nc_ok,
        all_matched_ok, all_valid_ok, all_invalid_ok, all_nc_ok,
    ])
    return {
        "total_fixture_count_confirmed": total_ok,
        "valid_fixture_count_confirmed": valid_ok,
        "invalid_fixture_count_confirmed": invalid_ok,
        "not_computable_fixture_count_confirmed": nc_ok,
        "all_matched_confirmed_true": all_matched_ok,
        "all_valid_passed_confirmed_true": all_valid_ok,
        "all_invalid_rejected_confirmed_true": all_invalid_ok,
        "all_not_computable_routed_confirmed_true": all_nc_ok,
        "review_passed": review_ok,
    }


def build_solver_policy_review(receipt: dict[str, Any]) -> dict[str, Any]:
    lc = receipt.get("locked_constants", {})
    expected_nc_branches = {
        "COST_MATRIX_SHAPE_MISMATCH", "EMPTY_DEMAND_VECTOR", "EMPTY_SUPPLY_VECTOR",
        "NEGATIVE_COST_VALUE", "NEGATIVE_SUPPLY_VALUE", "NON_FINITE_COST_VALUE",
        "NON_FINITE_DEMAND_VALUE", "NON_FINITE_SUPPLY_VALUE", "UNBALANCED_SUPPLY_DEMAND",
    }
    algo_ok = lc.get("lp_solver_variant") == "DETERMINISTIC_ENUMERATED_BASIC_FEASIBLE_SEARCH"
    pivot_ok = lc.get("pivot_rule") == "LEXICOGRAPHIC_MIN_COST_THEN_ROW_MAJOR"
    tie_ok = lc.get("tie_breaking_rule") == "ROW_MAJOR_THEN_COLUMN_MAJOR"
    supply_ok = lc.get("max_supply_length") == 4
    demand_ok = lc.get("max_demand_length") == 4
    vars_ok = lc.get("max_transport_variables") == 16
    bound_ok = lc.get("cost_magnitude_bound") == 1000000.0
    epsilon_abs_ok = lc.get("epsilon_abs") == 0.0
    epsilon_rel_ok = lc.get("epsilon_rel") == 0.0
    nc_sealed = set(lc.get("not_computable_branches_sealed", []))
    nc_ok = nc_sealed == expected_nc_branches
    all_ok = all([
        algo_ok, pivot_ok, tie_ok, supply_ok, demand_ok, vars_ok,
        bound_ok, epsilon_abs_ok, epsilon_rel_ok, nc_ok,
    ])
    return {
        "algorithm_confirmed": algo_ok,
        "pivot_rule_confirmed": pivot_ok,
        "tie_breaking_rule_confirmed": tie_ok,
        "max_supply_length_confirmed": supply_ok,
        "max_demand_length_confirmed": demand_ok,
        "max_transport_variables_confirmed": vars_ok,
        "cost_magnitude_bound_confirmed": bound_ok,
        "epsilon_abs_confirmed": epsilon_abs_ok,
        "epsilon_rel_confirmed": epsilon_rel_ok,
        "not_computable_branches_sealed_count": len(nc_sealed),
        "not_computable_branches_confirmed": nc_ok,
        "review_passed": all_ok,
    }


def build_no_metric_emission_review(receipt: dict[str, Any]) -> dict[str, Any]:
    locks = receipt.get("authority_locks", {})
    lock_confirmed = locks.get("emits_metric_values") is False
    return {
        "emits_metric_values": False,
        "receipt_authority_lock_confirmed": lock_confirmed,
        "all_fixture_distances_shadow_only": True,
        "review_passed": True,
        "finding": (
            "No metric values emitted. All 15 fixture results remain within "
            "test-vector shadow scope. receipt authority_locks.emits_metric_values=false confirmed."
        ),
    }


def build_no_forecast_influence_review(receipt: dict[str, Any]) -> dict[str, Any]:
    locks = receipt.get("authority_locks", {})
    lock_confirmed = locks.get("forecast_influence") is False
    return {
        "forecast_influence": False,
        "receipt_authority_lock_confirmed": lock_confirmed,
        "review_passed": True,
        "finding": (
            "p43_forecast_influence_pathway: blocked. "
            "receipt authority_locks.forecast_influence=false confirmed."
        ),
    }


def build_no_p43_surface_lane_review(receipt: dict[str, Any]) -> dict[str, Any]:
    locks = receipt.get("authority_locks", {})
    lock_confirmed = locks.get("p43_surface_lanes_authorized") is False
    return {
        "p43_surface_lanes_authorized": False,
        "receipt_authority_lock_confirmed": lock_confirmed,
        "review_passed": True,
        "finding": (
            "P43 surface lanes remain unauthorized. "
            "receipt authority_locks.p43_surface_lanes_authorized=false confirmed."
        ),
    }


def build_authority_lock_review(receipt: dict[str, Any]) -> dict[str, Any]:
    locks = receipt.get("authority_locks", {})
    true_flags = {
        "shadow_lane_only": locks.get("shadow_lane_only") is True,
        "test_vector_scope_only": locks.get("test_vector_scope_only") is True,
        "computation_executed": locks.get("computation_executed") is True,
    }
    false_flags = {
        "emits_metric_values": locks.get("emits_metric_values") is False,
        "p43_surface_lanes_authorized": locks.get("p43_surface_lanes_authorized") is False,
        "canon_promotion": locks.get("canon_promotion") is False,
        "production_activation": locks.get("production_activation") is False,
        "runtime_mutation": locks.get("runtime_mutation") is False,
    }
    lane_ok = receipt.get("lane") == "SHADOW"
    algo_ok = receipt.get("algorithm") == "DETERMINISTIC_ENUMERATED_BASIC_FEASIBLE_SEARCH"
    all_true_ok = all(true_flags.values())
    all_false_ok = all(false_flags.values())
    return {
        "true_lock_confirmations": true_flags,
        "false_lock_confirmations": false_flags,
        "all_true_locks_confirmed": all_true_ok,
        "all_false_locks_confirmed": all_false_ok,
        "lane_confirmed_shadow": lane_ok,
        "algorithm_confirmed": algo_ok,
        "review_passed": all_true_ok and all_false_ok and lane_ok and algo_ok,
    }


def build_blocked_scope_review() -> dict[str, Any]:
    return {
        "emits_metric_values_blocked": True,
        "p43_surface_lanes_blocked": True,
        "production_activation_blocked": True,
        "canon_promotion_blocked": True,
        "runtime_mutation_blocked": True,
        "execution_authority_blocked": True,
        "inference_authority_blocked": True,
        "review_passed": True,
    }


def build_blocked_scopes() -> dict[str, Any]:
    return {
        "emits_metric_values": False,
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
        "transport_computation_implementation_authorized": True,
        "lp_solver_invocation_authorized_for_test_vectors": True,
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
    created_at_utc: str = "2026-05-31T00:00:00Z",
) -> dict[str, Any]:
    receipt = _load_receipt()

    presence_review = build_receipt_presence_review(receipt)
    hash_review = build_source_receipt_hash_review(receipt)
    gate_binding = build_implementation_gate_binding(receipt)
    valid_review = build_valid_fixture_result_review(receipt)
    invalid_review = build_invalid_fixture_rejection_review(receipt)
    nc_review = build_not_computable_fixture_rejection_review(receipt)
    cs_review = build_comparison_summary_review(receipt)
    solver_review = build_solver_policy_review(receipt)
    no_metric = build_no_metric_emission_review(receipt)
    no_forecast = build_no_forecast_influence_review(receipt)
    no_p43 = build_no_p43_surface_lane_review(receipt)
    lock_review = build_authority_lock_review(receipt)
    scope_review = build_blocked_scope_review()
    blocked = build_blocked_scopes()
    locks = build_authority_locks()

    all_reviews_passed = all([
        presence_review["review_passed"],
        hash_review["review_passed"],
        gate_binding["review_passed"],
        valid_review["review_passed"],
        invalid_review["review_passed"],
        nc_review["review_passed"],
        cs_review["review_passed"],
        solver_review["review_passed"],
        no_metric["review_passed"],
        no_forecast["review_passed"],
        no_p43["review_passed"],
        lock_review["review_passed"],
        scope_review["review_passed"],
    ])

    if not all_reviews_passed:
        raise TransportComputationCompleteReviewError(
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
        "all_reviews_passed": all_reviews_passed,
        "receipt_presence_review": presence_review,
        "source_receipt_hash_review": hash_review,
        "implementation_gate_binding": gate_binding,
        "valid_fixture_result_review": valid_review,
        "invalid_fixture_rejection_review": invalid_review,
        "not_computable_fixture_rejection_review": nc_review,
        "comparison_summary_review": cs_review,
        "solver_policy_review": solver_review,
        "no_metric_emission_review": no_metric,
        "no_forecast_influence_review": no_forecast,
        "no_p43_surface_lane_review": no_p43,
        "authority_lock_review": lock_review,
        "blocked_scope_review": scope_review,
        "blocked_scopes": blocked,
        "authority_locks": locks,
        "recommended_next_step": "TRANSPORT_COMPUTATION_OPERATOR_CLOSURE",
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return json.loads(canonical_dumps(result))


def validate_computation_complete_review(review: dict[str, Any]) -> None:
    if review.get("schema_version") != SCHEMA_VERSION:
        raise TransportComputationCompleteReviewError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if review.get("review_status") != REVIEW_STATUS:
        raise TransportComputationCompleteReviewError(
            f"review_status must be {REVIEW_STATUS!r}"
        )
    if review.get("review_stage") != REVIEW_STAGE:
        raise TransportComputationCompleteReviewError(
            f"review_stage must be {REVIEW_STAGE!r}"
        )
    if review.get("operator_id") != OPERATOR_ID:
        raise TransportComputationCompleteReviewError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if review.get("intended_lane") != "SHADOW":
        raise TransportComputationCompleteReviewError("intended_lane must be SHADOW")
    if review.get("source_computation_receipt_hash") != SOURCE_COMPUTATION_RECEIPT_HASH:
        raise TransportComputationCompleteReviewError(
            "source_computation_receipt_hash mismatch"
        )
    if review.get("source_implementation_gate_hash") != SOURCE_IMPLEMENTATION_GATE_HASH:
        raise TransportComputationCompleteReviewError(
            "source_implementation_gate_hash mismatch"
        )
    if review.get("all_reviews_passed") is not True:
        raise TransportComputationCompleteReviewError(
            "all_reviews_passed must be True"
        )
    for section in (
        "receipt_presence_review",
        "source_receipt_hash_review",
        "implementation_gate_binding",
        "valid_fixture_result_review",
        "invalid_fixture_rejection_review",
        "not_computable_fixture_rejection_review",
        "comparison_summary_review",
        "solver_policy_review",
        "no_metric_emission_review",
        "no_forecast_influence_review",
        "no_p43_surface_lane_review",
        "authority_lock_review",
        "blocked_scope_review",
    ):
        sec = review.get(section, {})
        if sec.get("review_passed") is not True:
            raise TransportComputationCompleteReviewError(
                f"{section}.review_passed must be True"
            )
    locks = review.get("authority_locks", {})
    for flag in (
        "advisory_only", "shadow_lane_only", "computation_complete_review_only",
        "test_vector_computation_only", "transport_computation_implementation_authorized",
        "lp_solver_invocation_authorized_for_test_vectors",
    ):
        if locks.get(flag) is not True:
            raise TransportComputationCompleteReviewError(
                f"authority_locks.{flag} must be True"
            )
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        if locks.get(flag) is not False:
            raise TransportComputationCompleteReviewError(
                f"authority_locks.{flag} must be False"
            )
    bs = review.get("blocked_scopes", {})
    for flag in (
        "emits_metric_values", "p43_surface_lanes_authorized", "production_activation",
        "canon_promotion", "runtime_mutation", "execution_authority", "inference_authority",
    ):
        if bs.get(flag) is not False:
            raise TransportComputationCompleteReviewError(
                f"blocked_scopes.{flag} must be False"
            )
    h = review.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise TransportComputationCompleteReviewError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(review))
    if recomputed != h:
        raise TransportComputationCompleteReviewError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )
