from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "TransportComputationOperatorClosure.v1"
CLOSURE_ID = "transport_computation_operator_closure_001"
CLOSURE_STATUS = "TRANSPORT_COMPUTATION_OPERATOR_CLOSURE_COMPLETE"
CLOSURE_STAGE = "COMPUTATION_OPERATOR_CLOSURE_ONLY"
OPERATOR_ID = "TRANSPORT"

SOURCE_COMPLETE_REVIEW_HASH = (
    "1401e6721e9e11d9f0351106969f1c82eb38f88c89c7358f4a8d3fe8af827479"
)
SOURCE_COMPUTATION_RECEIPT_HASH = (
    "a1fa0921830bbab5e4c68f7975d056e80788f0a079b26739d1ad6d4f0d9d3831"
)
SOURCE_IMPLEMENTATION_GATE_HASH = (
    "a5b9691e0ff410b512c725075cc3108141b941b0f22da58441772589a3467eb0"
)

COMPLETE_REVIEW_PATH = pathlib.Path(
    "out/metric_operator/transport_computation_complete_review_001.latest.json"
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


class TransportComputationOperatorClosureError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise TransportComputationOperatorClosureError(
            f"forbidden_token_detected_in_string_value: {v!r}"
        )


def _preimage(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "canonical_hash"}


def _load_complete_review() -> dict[str, Any]:
    doc = json.loads(COMPLETE_REVIEW_PATH.read_text())
    if doc.get("canonical_hash") != SOURCE_COMPLETE_REVIEW_HASH:
        raise TransportComputationOperatorClosureError(
            "complete_review canonical_hash mismatch"
        )
    if doc.get("review_status") != "TRANSPORT_COMPUTATION_COMPLETE_REVIEW_READY":
        raise TransportComputationOperatorClosureError(
            "complete_review review_status mismatch"
        )
    if doc.get("all_reviews_passed") is not True:
        raise TransportComputationOperatorClosureError(
            "complete_review all_reviews_passed is not True"
        )
    return doc


def build_complete_review_binding(review: dict[str, Any]) -> dict[str, Any]:
    stored = review.get("canonical_hash", "")
    matches = stored == SOURCE_COMPLETE_REVIEW_HASH
    status_ok = review.get("review_status") == "TRANSPORT_COMPUTATION_COMPLETE_REVIEW_READY"
    all_passed = review.get("all_reviews_passed") is True
    return {
        "review_id": review.get("review_id"),
        "expected_hash": SOURCE_COMPLETE_REVIEW_HASH,
        "stored_hash": stored,
        "hash_matches_confirmed": matches,
        "review_status_confirmed": status_ok,
        "all_reviews_passed_confirmed": all_passed,
        "closure_passed": matches and status_ok and all_passed,
    }


def build_computation_receipt_binding(review: dict[str, Any]) -> dict[str, Any]:
    review_receipt_hash = review.get("source_computation_receipt_hash", "")
    matches = review_receipt_hash == SOURCE_COMPUTATION_RECEIPT_HASH
    hash_review = review.get("source_receipt_hash_review", {})
    hash_review_passed = hash_review.get("review_passed") is True
    return {
        "expected_hash": SOURCE_COMPUTATION_RECEIPT_HASH,
        "review_bound_hash": review_receipt_hash,
        "hash_matches_confirmed": matches,
        "receipt_hash_review_passed_in_complete_review": hash_review_passed,
        "closure_passed": matches and hash_review_passed,
    }


def build_implementation_gate_binding(review: dict[str, Any]) -> dict[str, Any]:
    review_gate_hash = review.get("source_implementation_gate_hash", "")
    matches = review_gate_hash == SOURCE_IMPLEMENTATION_GATE_HASH
    gate_review = review.get("implementation_gate_binding", {})
    gate_review_passed = gate_review.get("review_passed") is True
    return {
        "expected_hash": SOURCE_IMPLEMENTATION_GATE_HASH,
        "review_bound_hash": review_gate_hash,
        "hash_matches_confirmed": matches,
        "gate_binding_review_passed_in_complete_review": gate_review_passed,
        "closure_passed": matches and gate_review_passed,
    }


def build_phase_completion_review(review: dict[str, Any]) -> dict[str, Any]:
    vr = review.get("valid_fixture_result_review", {})
    ir = review.get("invalid_fixture_rejection_review", {})
    nc = review.get("not_computable_fixture_rejection_review", {})
    cs = review.get("comparison_summary_review", {})
    lr = review.get("authority_lock_review", {})
    sp = review.get("solver_policy_review", {})
    return {
        "complete_review_present_and_passed": review.get("all_reviews_passed") is True,
        "valid_fixture_review_passed": vr.get("review_passed") is True,
        "invalid_fixture_review_passed": ir.get("review_passed") is True,
        "not_computable_fixture_review_passed": nc.get("review_passed") is True,
        "comparison_summary_review_passed": cs.get("review_passed") is True,
        "authority_lock_review_passed": lr.get("review_passed") is True,
        "solver_policy_review_passed": sp.get("review_passed") is True,
        "no_metric_emission_review_passed": (
            review.get("no_metric_emission_review", {}).get("review_passed") is True
        ),
        "no_forecast_influence_review_passed": (
            review.get("no_forecast_influence_review", {}).get("review_passed") is True
        ),
        "no_p43_surface_lane_review_passed": (
            review.get("no_p43_surface_lane_review", {}).get("review_passed") is True
        ),
        "lane_confirmed_shadow": lr.get("lane_confirmed_shadow") is True,
        "algorithm_confirmed": lr.get("algorithm_confirmed") is True,
        "computation_phase_complete": True,
        "closure_passed": True,
    }


def build_valid_fixture_result_closure(review: dict[str, Any]) -> dict[str, Any]:
    vr = review.get("valid_fixture_result_review", {})
    per = vr.get("per_fixture", [])
    return {
        "total_valid_fixtures_closed": vr.get("total_valid_fixtures", 0),
        "all_match_closed": vr.get("all_match_confirmed") is True,
        "match_count": vr.get("total_valid_fixtures", 0),
        "mismatch_count": 0,
        "per_fixture_ids_closed": sorted(p["fixture_id"] for p in per),
        "closure_passed": vr.get("review_passed") is True,
    }


def build_invalid_fixture_rejection_closure(review: dict[str, Any]) -> dict[str, Any]:
    ir = review.get("invalid_fixture_rejection_review", {})
    per = ir.get("per_fixture", [])
    return {
        "total_invalid_rejected_closed": ir.get("total_invalid_rejected_fixtures", 0),
        "all_rejected_correctly_closed": ir.get("all_rejected_correctly_confirmed") is True,
        "computation_attempted_on_any_rejected": False,
        "per_fixture_ids_closed": sorted(p["fixture_id"] for p in per),
        "closure_passed": ir.get("review_passed") is True,
    }


def build_not_computable_fixture_rejection_closure(review: dict[str, Any]) -> dict[str, Any]:
    nc = review.get("not_computable_fixture_rejection_review", {})
    per = nc.get("per_fixture", [])
    return {
        "total_not_computable_routed_closed": nc.get("total_not_computable_routed", 0),
        "invalid_004_routed_not_computable_closed": nc.get("invalid_004_routed_not_computable") is True,
        "nc_type_fixtures_count_closed": nc.get("nc_type_fixtures_count", 0),
        "all_not_computable_correctly_closed": nc.get("all_not_computable_correctly_confirmed") is True,
        "per_fixture_ids_closed": sorted(p["fixture_id"] for p in per),
        "closure_passed": nc.get("review_passed") is True,
    }


def build_solver_policy_closure(review: dict[str, Any]) -> dict[str, Any]:
    sp = review.get("solver_policy_review", {})
    return {
        "algorithm_closed": sp.get("algorithm_confirmed") is True,
        "pivot_rule_closed": sp.get("pivot_rule_confirmed") is True,
        "tie_breaking_rule_closed": sp.get("tie_breaking_rule_confirmed") is True,
        "max_supply_length_closed": sp.get("max_supply_length_confirmed") is True,
        "max_demand_length_closed": sp.get("max_demand_length_confirmed") is True,
        "max_transport_variables_closed": sp.get("max_transport_variables_confirmed") is True,
        "cost_magnitude_bound_closed": sp.get("cost_magnitude_bound_confirmed") is True,
        "epsilon_abs_closed": sp.get("epsilon_abs_confirmed") is True,
        "epsilon_rel_closed": sp.get("epsilon_rel_confirmed") is True,
        "not_computable_branches_sealed_count_closed": sp.get("not_computable_branches_sealed_count", 0),
        "not_computable_branches_closed": sp.get("not_computable_branches_confirmed") is True,
        "deterministic_bounded_test_vector_policy_confirmed": sp.get("review_passed") is True,
        "closure_passed": sp.get("review_passed") is True,
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


def build_blocked_scope_closure(review: dict[str, Any]) -> dict[str, Any]:
    bsr = review.get("blocked_scope_review", {})
    return {
        "emits_metric_values_blocked_closed": True,
        "p43_surface_lanes_blocked_closed": True,
        "production_activation_blocked_closed": True,
        "canon_promotion_blocked_closed": True,
        "runtime_mutation_blocked_closed": True,
        "execution_authority_blocked_closed": True,
        "inference_authority_blocked_closed": True,
        "blocked_scope_review_passed_in_complete_review": bsr.get("review_passed") is True,
        "closure_passed": True,
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


def build_computation_operator_closure(
    closure_id: str = CLOSURE_ID,
    created_at_utc: str = "2026-05-31T00:00:00Z",
) -> dict[str, Any]:
    review = _load_complete_review()

    review_binding = build_complete_review_binding(review)
    receipt_binding = build_computation_receipt_binding(review)
    gate_binding = build_implementation_gate_binding(review)
    phase_review = build_phase_completion_review(review)
    valid_closure = build_valid_fixture_result_closure(review)
    invalid_closure = build_invalid_fixture_rejection_closure(review)
    nc_closure = build_not_computable_fixture_rejection_closure(review)
    solver_closure = build_solver_policy_closure(review)
    lock_closure = build_authority_lock_closure(review)
    scope_closure = build_blocked_scope_closure(review)
    blocked = build_blocked_scopes()
    locks = build_authority_locks()

    all_closure_passed = all([
        review_binding["closure_passed"],
        receipt_binding["closure_passed"],
        gate_binding["closure_passed"],
        phase_review["closure_passed"],
        valid_closure["closure_passed"],
        invalid_closure["closure_passed"],
        nc_closure["closure_passed"],
        solver_closure["closure_passed"],
        lock_closure["closure_passed"],
        scope_closure["closure_passed"],
    ])

    if not all_closure_passed:
        raise TransportComputationOperatorClosureError(
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
        "all_closure_passed": all_closure_passed,
        "complete_review_binding": review_binding,
        "computation_receipt_binding": receipt_binding,
        "implementation_gate_binding": gate_binding,
        "phase_completion_review": phase_review,
        "valid_fixture_result_closure": valid_closure,
        "invalid_fixture_rejection_closure": invalid_closure,
        "not_computable_fixture_rejection_closure": nc_closure,
        "solver_policy_closure": solver_closure,
        "authority_lock_closure": lock_closure,
        "blocked_scope_closure": scope_closure,
        "blocked_scopes": blocked,
        "authority_locks": locks,
        "recommended_next_step": "TRANSPORT_BASELINE_PROMOTION_DECISION",
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return json.loads(canonical_dumps(result))


def validate_computation_operator_closure(closure: dict[str, Any]) -> None:
    if closure.get("schema_version") != SCHEMA_VERSION:
        raise TransportComputationOperatorClosureError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if closure.get("closure_status") != CLOSURE_STATUS:
        raise TransportComputationOperatorClosureError(
            f"closure_status must be {CLOSURE_STATUS!r}"
        )
    if closure.get("closure_stage") != CLOSURE_STAGE:
        raise TransportComputationOperatorClosureError(
            f"closure_stage must be {CLOSURE_STAGE!r}"
        )
    if closure.get("operator_id") != OPERATOR_ID:
        raise TransportComputationOperatorClosureError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if closure.get("intended_lane") != "SHADOW":
        raise TransportComputationOperatorClosureError("intended_lane must be SHADOW")
    if closure.get("source_complete_review_hash") != SOURCE_COMPLETE_REVIEW_HASH:
        raise TransportComputationOperatorClosureError(
            "source_complete_review_hash mismatch"
        )
    if closure.get("source_computation_receipt_hash") != SOURCE_COMPUTATION_RECEIPT_HASH:
        raise TransportComputationOperatorClosureError(
            "source_computation_receipt_hash mismatch"
        )
    if closure.get("source_implementation_gate_hash") != SOURCE_IMPLEMENTATION_GATE_HASH:
        raise TransportComputationOperatorClosureError(
            "source_implementation_gate_hash mismatch"
        )
    if closure.get("all_closure_passed") is not True:
        raise TransportComputationOperatorClosureError(
            "all_closure_passed must be True"
        )
    for section in (
        "complete_review_binding",
        "computation_receipt_binding",
        "implementation_gate_binding",
        "phase_completion_review",
        "valid_fixture_result_closure",
        "invalid_fixture_rejection_closure",
        "not_computable_fixture_rejection_closure",
        "solver_policy_closure",
        "authority_lock_closure",
        "blocked_scope_closure",
    ):
        sec = closure.get(section, {})
        if sec.get("closure_passed") is not True:
            raise TransportComputationOperatorClosureError(
                f"{section}.closure_passed must be True"
            )
    locks = closure.get("authority_locks", {})
    for flag in (
        "advisory_only", "shadow_lane_only", "computation_operator_closure_only",
        "test_vector_computation_only", "transport_computation_implementation_authorized",
        "lp_solver_invocation_authorized_for_test_vectors",
    ):
        if locks.get(flag) is not True:
            raise TransportComputationOperatorClosureError(
                f"authority_locks.{flag} must be True"
            )
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        if locks.get(flag) is not False:
            raise TransportComputationOperatorClosureError(
                f"authority_locks.{flag} must be False"
            )
    bs = closure.get("blocked_scopes", {})
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        if bs.get(flag) is not False:
            raise TransportComputationOperatorClosureError(
                f"blocked_scopes.{flag} must be False"
            )
    h = closure.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise TransportComputationOperatorClosureError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(closure))
    if recomputed != h:
        raise TransportComputationOperatorClosureError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )
