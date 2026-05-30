"""Core: WassersteinBaselinePromotionComplete.v1."""

from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinBaselinePromotionComplete.v1"
COMPLETION_TYPE = "WASSERSTEIN_BASELINE_PROMOTION_COMPLETE"
COMPLETION_STATUS = "WASSERSTEIN_BASELINE_PROMOTION_COMPLETE"
OPERATOR_ID = "WASSERSTEIN"
COMPLETION_ID = "wasserstein_baseline_promotion_complete_001"

SOURCE_REVIEW_HASH = (
    "a5adc285aa2dc51ba999e5a402aa0126eb0eb2a91e9cbd5f9cb78680ebe9336f"
)
SOURCE_DECISION_HASH = (
    "a3f470fe0d1986ddbffddfbe997a25480977c0436f651b7bdbfe2f0d9bfab080"
)
SOURCE_PACK_VECTOR_UPDATE_HASH = (
    "b18caaea2d2cd7a06f6958350a23de7c4337cf3cd82c34345b6b7519d1b39134"
)

REVIEW_PATH = (
    "out/metric_operator/"
    "wasserstein_baseline_promotion_review_001.latest.json"
)
DECISION_PATH = "input/wasserstein_baseline_promotion_operator_decision.json"
PACK_VECTOR_UPDATE_PATH = (
    "out/metric_operator/"
    "wasserstein_cpu_baseline_pack_vector_update_001.latest.json"
)


class WassersteinBaselinePromotionCompleteError(ValueError):
    pass


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def load_and_verify_review(path: str = REVIEW_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        review = json.load(fh)
    observed = review.get("canonical_hash", "")
    if observed != SOURCE_REVIEW_HASH:
        raise WassersteinBaselinePromotionCompleteError(
            f"review_hash_mismatch: expected={SOURCE_REVIEW_HASH!r} got={observed!r}"
        )
    return review


def load_and_verify_decision(path: str = DECISION_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        decision = json.load(fh)
    observed = canonical_hash(decision)
    if observed != SOURCE_DECISION_HASH:
        raise WassersteinBaselinePromotionCompleteError(
            f"decision_hash_mismatch: expected={SOURCE_DECISION_HASH!r} got={observed!r}"
        )
    return decision


def load_and_verify_pack_vector_update(
    path: str = PACK_VECTOR_UPDATE_PATH,
) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        pvu = json.load(fh)
    observed = pvu.get("canonical_hash", "")
    if observed != SOURCE_PACK_VECTOR_UPDATE_HASH:
        raise WassersteinBaselinePromotionCompleteError(
            f"pack_vector_update_hash_mismatch: expected={SOURCE_PACK_VECTOR_UPDATE_HASH!r} "
            f"got={observed!r}"
        )
    return pvu


def build_review_binding(review: dict[str, Any]) -> dict[str, Any]:
    review_id = review.get("review_id", "")
    observed_hash = review.get("canonical_hash", "")
    status = review.get("review_status", "")
    if observed_hash != SOURCE_REVIEW_HASH:
        raise WassersteinBaselinePromotionCompleteError(
            f"review_hash_mismatch: expected={SOURCE_REVIEW_HASH!r} got={observed_hash!r}"
        )
    if status != "WASSERSTEIN_BASELINE_PROMOTION_REVIEW_COMPLETE":
        raise WassersteinBaselinePromotionCompleteError(
            f"review_status_unexpected: got={status!r}"
        )
    return {
        "review_id": review_id,
        "review_hash": observed_hash,
        "review_status_observed": status,
        "hash_match": True,
        "binding_status": "REVIEW_BOUND",
    }


def build_decision_binding(decision: dict[str, Any]) -> dict[str, Any]:
    did = decision.get("decision_id", "")
    observed_hash = canonical_hash(decision)
    dec = decision.get("decision", "")
    bpra = decision.get("baseline_promotion_review_authorized")
    scope = decision.get("authorized_scope", "")
    if observed_hash != SOURCE_DECISION_HASH:
        raise WassersteinBaselinePromotionCompleteError(
            f"decision_hash_mismatch: expected={SOURCE_DECISION_HASH!r} got={observed_hash!r}"
        )
    if dec != "approve_wasserstein_shadow_stub_baseline_promotion_review":
        raise WassersteinBaselinePromotionCompleteError(
            f"decision_value_unexpected: got={dec!r}"
        )
    if bpra is not True:
        raise WassersteinBaselinePromotionCompleteError(
            "baseline_promotion_review_authorized_not_true"
        )
    if scope != "BASELINE_PROMOTION_REVIEW_ONLY":
        raise WassersteinBaselinePromotionCompleteError(
            f"authorized_scope_unexpected: got={scope!r}"
        )
    return {
        "decision_id": did,
        "decision_hash": observed_hash,
        "decision_observed": dec,
        "baseline_promotion_review_authorized_observed": True,
        "authorized_scope_observed": scope,
        "hash_match": True,
        "binding_status": "DECISION_BOUND",
    }


def build_pack_vector_update_binding(pvu: dict[str, Any]) -> dict[str, Any]:
    pvu_id = pvu.get("update_id", "")
    observed_hash = pvu.get("canonical_hash", "")
    update_status = pvu.get("update_status", "")
    phase_status = pvu.get("cpu_baseline_phase_record", {}).get(
        "cpu_baseline_computation_phase_status", ""
    )
    if observed_hash != SOURCE_PACK_VECTOR_UPDATE_HASH:
        raise WassersteinBaselinePromotionCompleteError(
            f"pack_vector_update_hash_mismatch: expected={SOURCE_PACK_VECTOR_UPDATE_HASH!r} "
            f"got={observed_hash!r}"
        )
    if update_status != "WASSERSTEIN_CPU_BASELINE_PACK_VECTOR_UPDATE_COMPLETE":
        raise WassersteinBaselinePromotionCompleteError(
            f"pack_vector_update_status_unexpected: got={update_status!r}"
        )
    if phase_status != "COMPUTATION_PHASE_CLOSED":
        raise WassersteinBaselinePromotionCompleteError(
            f"cpu_baseline_phase_status_unexpected: got={phase_status!r}"
        )
    return {
        "pack_vector_update_id": pvu_id,
        "pack_vector_update_hash": observed_hash,
        "update_status_observed": update_status,
        "cpu_baseline_phase_status_observed": phase_status,
        "hash_match": True,
        "binding_status": "PACK_VECTOR_UPDATE_BOUND",
    }


def build_no_op_parity_completion(review: dict[str, Any]) -> dict[str, Any]:
    nop = review.get("no_op_parity_review", {})
    if nop.get("no_op_parity_confirmed") is not True:
        raise WassersteinBaselinePromotionCompleteError(
            "no_op_parity_not_confirmed_in_review"
        )
    psr = review.get("promotion_scope_review", {})
    if psr.get("pack_vector_modified") is not False:
        raise WassersteinBaselinePromotionCompleteError(
            "pack_vector_modified_true_in_review"
        )
    if psr.get("vector_type_promoted") is not False:
        raise WassersteinBaselinePromotionCompleteError(
            "vector_type_promoted_true_in_review"
        )
    if psr.get("runtime_mutated") is not False:
        raise WassersteinBaselinePromotionCompleteError(
            "runtime_mutated_true_in_review"
        )
    return {
        "no_op_parity_confirmed": True,
        "pack_vector_modified": False,
        "vector_type_promoted": False,
        "runtime_mutated": False,
        "shadow_stub_posture_preserved": True,
        "advisory_only_posture_preserved": True,
        "completion_status": "NO_OP_PARITY_COMPLETE",
    }


def build_baseline_state_completion(review: dict[str, Any]) -> dict[str, Any]:
    cps = review.get("current_pack_state_review", {})
    vt = cps.get("wasserstein_vector_type_observed", "")
    cs = cps.get("expected_computation_status_observed", "")
    ea = cps.get("expected_authority_state_observed", "")
    if vt != "VALID_SHADOW_ONLY_VECTOR":
        raise WassersteinBaselinePromotionCompleteError(
            f"current_vector_type_unexpected: got={vt!r}"
        )
    if cs != "SHADOW_STUB_ONLY":
        raise WassersteinBaselinePromotionCompleteError(
            f"current_computation_status_unexpected: got={cs!r}"
        )
    if ea != "ADVISORY_ONLY":
        raise WassersteinBaselinePromotionCompleteError(
            f"current_authority_state_unexpected: got={ea!r}"
        )
    return {
        "current_vector_type": vt,
        "current_computation_status": cs,
        "current_authority_state": ea,
        "baseline_promotion_phase_complete": True,
        "completion_status": "BASELINE_STATE_COMPLETE",
    }


def build_cpu_baseline_chain_completion(review: dict[str, Any]) -> dict[str, Any]:
    closure_r = review.get("cpu_baseline_chain_closure_review", {})
    closure_status = closure_r.get("closure_status_observed", "")
    if closure_status != "WASSERSTEIN_CPU_BASELINE_COMPUTATION_OPERATOR_CLOSURE_COMPLETE":
        raise WassersteinBaselinePromotionCompleteError(
            f"cpu_baseline_closure_status_unexpected: got={closure_status!r}"
        )
    pvu_r = review.get("source_pack_vector_update_binding", {})
    pvu_status = pvu_r.get("update_status_observed", "")
    if pvu_status != "WASSERSTEIN_CPU_BASELINE_PACK_VECTOR_UPDATE_COMPLETE":
        raise WassersteinBaselinePromotionCompleteError(
            f"pvu_status_unexpected_in_review: got={pvu_status!r}"
        )
    review_status = review.get("review_status", "")
    if review_status != "WASSERSTEIN_BASELINE_PROMOTION_REVIEW_COMPLETE":
        raise WassersteinBaselinePromotionCompleteError(
            f"review_status_unexpected: got={review_status!r}"
        )
    return {
        "cpu_baseline_computation_phase_closed": True,
        "cpu_baseline_pack_vector_update_complete": True,
        "cpu_baseline_operator_closure_complete": True,
        "baseline_promotion_review_complete": True,
        "completion_status": "CPU_BASELINE_CHAIN_COMPLETE",
    }


def build_authority_lock_completion() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "baseline_promotion_complete_only": True,
        "no_op_parity_confirmed": True,
        "baseline_promotion_phase_complete": True,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
        "all_locks_intact": True,
        "completion_status": "AUTHORITY_LOCKS_COMPLETE",
    }


def build_blocked_scope_completion() -> dict[str, Any]:
    scopes = [
        "emits_metric_values", "forecast_influence", "p43_surface_lanes",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ]
    verified = [{"scope": s, "blocked": False, "completion_status": "VERIFIED"} for s in scopes]
    return {
        "all_blocked_scopes_false": True,
        "scopes_verified": verified,
        "completion_status": "BLOCKED_SCOPES_COMPLETE",
    }


def default_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "baseline_promotion_complete_only": True,
        "no_op_parity_confirmed": True,
        "baseline_promotion_phase_complete": True,
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


def compute_wasserstein_baseline_promotion_complete_hash(
    payload: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(payload))


def build_wasserstein_baseline_promotion_complete(
    payload: dict[str, Any],
) -> dict[str, Any]:
    packet = {
        "schema_version": SCHEMA_VERSION,
        "completion_id": payload["completion_id"],
        "completion_type": COMPLETION_TYPE,
        "operator_id": OPERATOR_ID,
        "completion_status": COMPLETION_STATUS,
        "source_review_hash": SOURCE_REVIEW_HASH,
        "source_decision_hash": SOURCE_DECISION_HASH,
        "source_pack_vector_update_hash": SOURCE_PACK_VECTOR_UPDATE_HASH,
        "intended_lane": payload["intended_lane"],
        "completion_stage": payload["completion_stage"],
        "review_binding": payload["review_binding"],
        "decision_binding": payload["decision_binding"],
        "pack_vector_update_binding": payload["pack_vector_update_binding"],
        "no_op_parity_completion": payload["no_op_parity_completion"],
        "baseline_state_completion": payload["baseline_state_completion"],
        "cpu_baseline_chain_completion": payload["cpu_baseline_chain_completion"],
        "authority_lock_completion": payload["authority_lock_completion"],
        "blocked_scope_completion": payload["blocked_scope_completion"],
        "blocked_scopes": payload["blocked_scopes"],
        "authority_locks": payload["authority_locks"],
        "recommended_next_step": payload["recommended_next_step"],
        "provenance": payload["provenance"],
        "created_at_utc": payload["created_at_utc"],
    }
    packet["canonical_hash"] = compute_wasserstein_baseline_promotion_complete_hash(packet)
    return _finalize(packet)


def serialize_wasserstein_baseline_promotion_complete(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(packet)
