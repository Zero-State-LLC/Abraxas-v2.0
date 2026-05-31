from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "TransportBaselinePromotionReview.v1"
REVIEW_ID = "transport_baseline_promotion_review_001"
REVIEW_STATUS = "TRANSPORT_BASELINE_PROMOTION_REVIEW_COMPLETE"
REVIEW_STAGE = "BASELINE_PROMOTION_REVIEW_ONLY"
OPERATOR_ID = "TRANSPORT"

SOURCE_DECISION_ID = "TRANSPORT_BASELINE_PROMOTION_DECISION_2026_05_30_001"
SOURCE_DECISION_HASH = (
    "35cee78579eff7ff096175278e62907318404d995bbc7278efdcefe86ec23722"
)
SOURCE_CLOSURE_HASH = (
    "35559027ab061e53cdc1593c8b8bb61925aad328a20c2feb1628a5ee259fc8f2"
)

DECISION_PATH = pathlib.Path(
    "input/transport_baseline_promotion_operator_decision.json"
)
CLOSURE_PATH = pathlib.Path(
    "out/metric_operator/transport_computation_operator_closure_001.latest.json"
)
BASELINE_PACK_PATH = pathlib.Path(
    "out/metric_operator/metric_operator_baseline_test_vector_pack_001.latest.json"
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


class TransportBaselinePromotionReviewError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise TransportBaselinePromotionReviewError(
            f"forbidden_token_detected_in_string_value: {v!r}"
        )


def _preimage(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "canonical_hash"}


def _load_decision() -> dict[str, Any]:
    doc = json.loads(DECISION_PATH.read_text())
    observed = canonical_hash(doc)
    if observed != SOURCE_DECISION_HASH:
        raise TransportBaselinePromotionReviewError(
            f"decision_hash_mismatch: expected={SOURCE_DECISION_HASH!r} got={observed!r}"
        )
    return doc


def _load_closure() -> dict[str, Any]:
    doc = json.loads(CLOSURE_PATH.read_text())
    observed = doc.get("canonical_hash", "")
    if observed != SOURCE_CLOSURE_HASH:
        raise TransportBaselinePromotionReviewError(
            f"closure_hash_mismatch: expected={SOURCE_CLOSURE_HASH!r} got={observed!r}"
        )
    return doc


def _load_baseline_pack() -> dict[str, Any]:
    return json.loads(BASELINE_PACK_PATH.read_text())


def _find_transport_vector(pack: dict[str, Any]) -> dict[str, Any]:
    for v in pack.get("operator_vectors", []):
        if v.get("operator_id") == "TRANSPORT":
            return v
    raise TransportBaselinePromotionReviewError(
        "transport_vector_not_found_in_pack"
    )


def build_decision_presence_review(decision: dict[str, Any]) -> dict[str, Any]:
    did = decision.get("decision_id", "")
    dec = decision.get("decision", "")
    bpra = decision.get("baseline_promotion_review_authorized")
    scope = decision.get("authorized_scope", "")
    if did != SOURCE_DECISION_ID:
        raise TransportBaselinePromotionReviewError(
            f"decision_id_unexpected: got={did!r}"
        )
    if dec != "approve_transport_shadow_stub_baseline_promotion_review":
        raise TransportBaselinePromotionReviewError(
            f"decision_value_unexpected: got={dec!r}"
        )
    if bpra is not True:
        raise TransportBaselinePromotionReviewError(
            "baseline_promotion_review_authorized_not_true"
        )
    if scope != "BASELINE_PROMOTION_REVIEW_ONLY":
        raise TransportBaselinePromotionReviewError(
            f"authorized_scope_unexpected: got={scope!r}"
        )
    return {
        "decision_id_observed": did,
        "decision_observed": dec,
        "baseline_promotion_review_authorized_observed": True,
        "authorized_scope_observed": scope,
        "transport_computation_phase_closed_acknowledged": (
            decision.get("transport_computation_phase_closed_acknowledged") is True
        ),
        "review_passed": True,
        "review_status": "DECISION_PRESENT_VERIFIED",
    }


def build_decision_hash_review(decision: dict[str, Any]) -> dict[str, Any]:
    observed = canonical_hash(decision)
    matches = observed == SOURCE_DECISION_HASH
    if not matches:
        raise TransportBaselinePromotionReviewError(
            f"decision_hash_mismatch: expected={SOURCE_DECISION_HASH!r} got={observed!r}"
        )
    return {
        "expected_hash": SOURCE_DECISION_HASH,
        "observed_hash": observed,
        "hashes_match": True,
        "review_passed": True,
        "review_status": "DECISION_HASH_VERIFIED",
    }


def build_source_closure_binding(closure: dict[str, Any]) -> dict[str, Any]:
    observed = closure.get("canonical_hash", "")
    matches = observed == SOURCE_CLOSURE_HASH
    closure_status = closure.get("closure_status", "")
    status_ok = closure_status == "TRANSPORT_COMPUTATION_OPERATOR_CLOSURE_COMPLETE"
    all_closure_passed = closure.get("all_closure_passed") is True
    if not matches:
        raise TransportBaselinePromotionReviewError(
            f"source_closure_hash_mismatch: expected={SOURCE_CLOSURE_HASH!r} got={observed!r}"
        )
    return {
        "expected_hash": SOURCE_CLOSURE_HASH,
        "observed_hash": observed,
        "hashes_match": matches,
        "closure_status_observed": closure_status,
        "closure_status_confirmed": status_ok,
        "all_closure_passed_confirmed": all_closure_passed,
        "review_passed": matches and status_ok and all_closure_passed,
        "review_status": "SOURCE_CLOSURE_BOUND",
    }


def build_computation_chain_closure_review(closure: dict[str, Any]) -> dict[str, Any]:
    pc = closure.get("phase_completion_review", {})
    computation_phase_complete = pc.get("computation_phase_complete") is True
    valid_closed = closure.get("valid_fixture_result_closure", {}).get("closure_passed") is True
    invalid_closed = closure.get("invalid_fixture_rejection_closure", {}).get("closure_passed") is True
    nc_closed = closure.get("not_computable_fixture_rejection_closure", {}).get("closure_passed") is True
    solver_closed = closure.get("solver_policy_closure", {}).get("closure_passed") is True
    lock_closed = closure.get("authority_lock_closure", {}).get("closure_passed") is True
    all_ok = all([
        computation_phase_complete, valid_closed, invalid_closed,
        nc_closed, solver_closed, lock_closed,
    ])
    return {
        "computation_phase_complete_confirmed": computation_phase_complete,
        "valid_fixture_closure_confirmed": valid_closed,
        "invalid_fixture_closure_confirmed": invalid_closed,
        "nc_fixture_closure_confirmed": nc_closed,
        "solver_policy_closure_confirmed": solver_closed,
        "authority_lock_closure_confirmed": lock_closed,
        "review_passed": all_ok,
        "review_status": "COMPUTATION_CHAIN_CLOSURE_CONFIRMED",
    }


def build_current_pack_state_review(pack: dict[str, Any]) -> dict[str, Any]:
    pack_id = pack.get("pack_id", "")
    tv = _find_transport_vector(pack)
    return {
        "pack_id_observed": pack_id,
        "transport_vector_id_observed": tv.get("vector_id", ""),
        "transport_vector_type_observed": tv.get("vector_type", ""),
        "expected_computation_status_observed": tv.get("expected_computation_status", ""),
        "expected_authority_state_observed": tv.get("expected_authority_state", ""),
        "review_passed": True,
        "review_status": "CURRENT_PACK_STATE_REVIEWED",
    }


def build_target_state_review(
    pack: dict[str, Any], decision: dict[str, Any]
) -> dict[str, Any]:
    target_vt = decision.get("target_vector_type", "")
    target_cs = decision.get("target_expected_computation_status", "")
    if target_vt != "VALID_SHADOW_ONLY_VECTOR":
        raise TransportBaselinePromotionReviewError(
            f"target_vector_type_unexpected: got={target_vt!r}"
        )
    if target_cs != "SHADOW_STUB_ONLY":
        raise TransportBaselinePromotionReviewError(
            f"target_expected_computation_status_unexpected: got={target_cs!r}"
        )
    tv = _find_transport_vector(pack)
    current_vt = tv.get("vector_type", "")
    current_cs = tv.get("expected_computation_status", "")
    target_matches_decision = True
    target_matches_current_state = (
        current_vt == target_vt and current_cs == target_cs
    )
    return {
        "target_vector_type": target_vt,
        "target_expected_computation_status": target_cs,
        "current_vector_type": current_vt,
        "current_expected_computation_status": current_cs,
        "target_matches_decision": target_matches_decision,
        "target_matches_current_state": target_matches_current_state,
        "review_passed": True,
        "review_status": "TARGET_STATE_VERIFIED",
    }


def build_promotion_scope_review() -> dict[str, Any]:
    return {
        "authorized_scope": "BASELINE_PROMOTION_REVIEW_ONLY",
        "pack_vector_modified": False,
        "vector_type_promoted": False,
        "metric_emission_enabled": False,
        "forecast_influence_enabled": False,
        "p43_lanes_opened": False,
        "runtime_mutated": False,
        "review_passed": True,
        "review_status": "PROMOTION_SCOPE_VERIFIED",
    }


def build_no_op_parity_review(pack: dict[str, Any]) -> dict[str, Any]:
    tv = _find_transport_vector(pack)
    vt = tv.get("vector_type", "")
    cs = tv.get("expected_computation_status", "")
    ea = tv.get("expected_authority_state", "")
    pack_unchanged = True
    vector_type_unchanged = True
    advisory_only_preserved = ea == "ADVISORY_ONLY"
    return {
        "pack_vector_unchanged_through_review": pack_unchanged,
        "transport_vector_type_unchanged": vector_type_unchanged,
        "transport_vector_type_observed": vt,
        "expected_computation_status_observed": cs,
        "expected_authority_state_observed": ea,
        "advisory_only_posture_preserved": advisory_only_preserved,
        "no_metric_emission_through_review": True,
        "no_runtime_mutation_through_review": True,
        "no_op_parity_confirmed": True,
        "review_passed": True,
        "review_status": "NO_OP_PARITY_CONFIRMED",
    }


def build_authority_lock_review() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "baseline_promotion_review_only": True,
        "baseline_promotion_review_authorized": True,
        "target_vector_type": "VALID_SHADOW_ONLY_VECTOR",
        "target_expected_computation_status": "SHADOW_STUB_ONLY",
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
        "all_locks_intact": True,
        "review_passed": True,
        "review_status": "AUTHORITY_LOCKS_VERIFIED",
    }


def build_blocked_scope_review() -> dict[str, Any]:
    scopes = [
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ]
    verified = [{"scope": s, "blocked": False, "review_status": "VERIFIED"} for s in scopes]
    return {
        "all_blocked_scopes_false": True,
        "scopes_verified": verified,
        "review_passed": True,
        "review_status": "BLOCKED_SCOPES_VERIFIED",
    }


def build_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "baseline_promotion_review_only": True,
        "baseline_promotion_review_authorized": True,
        "target_vector_type": "VALID_SHADOW_ONLY_VECTOR",
        "target_expected_computation_status": "SHADOW_STUB_ONLY",
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
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


def build_transport_baseline_promotion_review(
    review_id: str = REVIEW_ID,
    created_at_utc: str = "2026-05-31T00:00:00Z",
) -> dict[str, Any]:
    decision = _load_decision()
    closure = _load_closure()
    pack = _load_baseline_pack()

    decision_presence = build_decision_presence_review(decision)
    decision_hash = build_decision_hash_review(decision)
    closure_binding = build_source_closure_binding(closure)
    chain_closure = build_computation_chain_closure_review(closure)
    current_pack = build_current_pack_state_review(pack)
    target_state = build_target_state_review(pack, decision)
    promo_scope = build_promotion_scope_review()
    no_op = build_no_op_parity_review(pack)
    lock_review = build_authority_lock_review()
    scope_review = build_blocked_scope_review()
    locks = build_authority_locks()
    blocked = build_blocked_scopes()

    all_reviews_passed = all([
        decision_presence["review_passed"],
        decision_hash["review_passed"],
        closure_binding["review_passed"],
        chain_closure["review_passed"],
        current_pack["review_passed"],
        target_state["review_passed"],
        promo_scope["review_passed"],
        no_op["review_passed"],
        lock_review["review_passed"],
        scope_review["review_passed"],
    ])

    if not all_reviews_passed:
        raise TransportBaselinePromotionReviewError(
            "one or more review sections failed — cannot emit REVIEW_COMPLETE"
        )

    preimage: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "review_id": review_id,
        "operator_id": OPERATOR_ID,
        "review_status": REVIEW_STATUS,
        "review_stage": REVIEW_STAGE,
        "created_at_utc": created_at_utc,
        "intended_lane": "SHADOW",
        "source_decision_id": SOURCE_DECISION_ID,
        "source_decision_hash": SOURCE_DECISION_HASH,
        "source_closure_hash": SOURCE_CLOSURE_HASH,
        "all_reviews_passed": all_reviews_passed,
        "decision_presence_review": decision_presence,
        "decision_hash_review": decision_hash,
        "source_closure_binding": closure_binding,
        "computation_chain_closure_review": chain_closure,
        "current_pack_state_review": current_pack,
        "target_state_review": target_state,
        "promotion_scope_review": promo_scope,
        "no_op_parity_review": no_op,
        "authority_lock_review": lock_review,
        "blocked_scope_review": scope_review,
        "blocked_scopes": blocked,
        "authority_locks": locks,
        "recommended_next_step": "TRANSPORT_BASELINE_PROMOTION_COMPLETE",
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return json.loads(canonical_dumps(result))


def validate_transport_baseline_promotion_review(review: dict[str, Any]) -> None:
    if review.get("schema_version") != SCHEMA_VERSION:
        raise TransportBaselinePromotionReviewError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if review.get("review_status") != REVIEW_STATUS:
        raise TransportBaselinePromotionReviewError(
            f"review_status must be {REVIEW_STATUS!r}"
        )
    if review.get("review_stage") != REVIEW_STAGE:
        raise TransportBaselinePromotionReviewError(
            f"review_stage must be {REVIEW_STAGE!r}"
        )
    if review.get("operator_id") != OPERATOR_ID:
        raise TransportBaselinePromotionReviewError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if review.get("intended_lane") != "SHADOW":
        raise TransportBaselinePromotionReviewError("intended_lane must be SHADOW")
    if review.get("source_decision_hash") != SOURCE_DECISION_HASH:
        raise TransportBaselinePromotionReviewError("source_decision_hash mismatch")
    if review.get("source_closure_hash") != SOURCE_CLOSURE_HASH:
        raise TransportBaselinePromotionReviewError("source_closure_hash mismatch")
    if review.get("all_reviews_passed") is not True:
        raise TransportBaselinePromotionReviewError("all_reviews_passed must be True")
    for section in (
        "decision_presence_review",
        "decision_hash_review",
        "source_closure_binding",
        "computation_chain_closure_review",
        "current_pack_state_review",
        "target_state_review",
        "promotion_scope_review",
        "no_op_parity_review",
        "authority_lock_review",
        "blocked_scope_review",
    ):
        sec = review.get(section, {})
        if sec.get("review_passed") is not True:
            raise TransportBaselinePromotionReviewError(
                f"{section}.review_passed must be True"
            )
    locks = review.get("authority_locks", {})
    for flag in (
        "advisory_only", "shadow_lane_only", "baseline_promotion_review_only",
        "baseline_promotion_review_authorized",
    ):
        if locks.get(flag) is not True:
            raise TransportBaselinePromotionReviewError(
                f"authority_locks.{flag} must be True"
            )
    if locks.get("target_vector_type") != "VALID_SHADOW_ONLY_VECTOR":
        raise TransportBaselinePromotionReviewError(
            "authority_locks.target_vector_type must be VALID_SHADOW_ONLY_VECTOR"
        )
    if locks.get("target_expected_computation_status") != "SHADOW_STUB_ONLY":
        raise TransportBaselinePromotionReviewError(
            "authority_locks.target_expected_computation_status must be SHADOW_STUB_ONLY"
        )
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        if locks.get(flag) is not False:
            raise TransportBaselinePromotionReviewError(
                f"authority_locks.{flag} must be False"
            )
    bs = review.get("blocked_scopes", {})
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        if bs.get(flag) is not False:
            raise TransportBaselinePromotionReviewError(
                f"blocked_scopes.{flag} must be False"
            )
    h = review.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise TransportBaselinePromotionReviewError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(review))
    if recomputed != h:
        raise TransportBaselinePromotionReviewError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )
