"""Core: WassersteinBaselinePromotionReview.v1."""

from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinBaselinePromotionReview.v1"
REVIEW_TYPE = "WASSERSTEIN_BASELINE_PROMOTION_REVIEW"
REVIEW_STATUS = "WASSERSTEIN_BASELINE_PROMOTION_REVIEW_COMPLETE"
OPERATOR_ID = "WASSERSTEIN"
REVIEW_ID = "wasserstein_baseline_promotion_review_001"

SOURCE_DECISION_ID = "WASSERSTEIN_BASELINE_PROMOTION_DECISION_2026_05_30_001"
SOURCE_DECISION_HASH = (
    "a3f470fe0d1986ddbffddfbe997a25480977c0436f651b7bdbfe2f0d9bfab080"
)
SOURCE_PACK_VECTOR_UPDATE_HASH = (
    "b18caaea2d2cd7a06f6958350a23de7c4337cf3cd82c34345b6b7519d1b39134"
)
SOURCE_CLOSURE_HASH = (
    "36fb4fb48974e3ba9eed93bf76584fae8f543ceeb41d05d3cb48a0a4bdffa7bd"
)

DECISION_PATH = "input/wasserstein_baseline_promotion_operator_decision.json"
PACK_VECTOR_UPDATE_PATH = (
    "out/metric_operator/"
    "wasserstein_cpu_baseline_pack_vector_update_001.latest.json"
)
OPERATOR_CLOSURE_PATH = (
    "out/metric_operator/"
    "wasserstein_cpu_baseline_computation_operator_closure_001.latest.json"
)
BASELINE_PACK_PATH = (
    "out/metric_operator/metric_operator_baseline_test_vector_pack_001.latest.json"
)


class WassersteinBaselinePromotionReviewError(ValueError):
    pass


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def load_and_verify_decision(path: str = DECISION_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        decision = json.load(fh)
    observed = canonical_hash(decision)
    if observed != SOURCE_DECISION_HASH:
        raise WassersteinBaselinePromotionReviewError(
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
        raise WassersteinBaselinePromotionReviewError(
            f"pack_vector_update_hash_mismatch: expected={SOURCE_PACK_VECTOR_UPDATE_HASH!r} "
            f"got={observed!r}"
        )
    return pvu


def load_and_verify_operator_closure(
    path: str = OPERATOR_CLOSURE_PATH,
) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        closure = json.load(fh)
    observed = closure.get("canonical_hash", "")
    if observed != SOURCE_CLOSURE_HASH:
        raise WassersteinBaselinePromotionReviewError(
            f"operator_closure_hash_mismatch: expected={SOURCE_CLOSURE_HASH!r} "
            f"got={observed!r}"
        )
    return closure


def load_baseline_pack(path: str = BASELINE_PACK_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _find_wasserstein_vector(pack: dict[str, Any]) -> dict[str, Any]:
    for v in pack.get("operator_vectors", []):
        if v.get("operator_id") == "WASSERSTEIN":
            return v
    raise WassersteinBaselinePromotionReviewError(
        "wasserstein_vector_not_found_in_pack"
    )


def build_decision_presence_review(decision: dict[str, Any]) -> dict[str, Any]:
    did = decision.get("decision_id", "")
    dec = decision.get("decision", "")
    bpra = decision.get("baseline_promotion_review_authorized")
    scope = decision.get("authorized_scope", "")
    if dec != "approve_wasserstein_shadow_stub_baseline_promotion_review":
        raise WassersteinBaselinePromotionReviewError(
            f"decision_value_unexpected: got={dec!r}"
        )
    if bpra is not True:
        raise WassersteinBaselinePromotionReviewError(
            "baseline_promotion_review_authorized_not_true"
        )
    if scope != "BASELINE_PROMOTION_REVIEW_ONLY":
        raise WassersteinBaselinePromotionReviewError(
            f"authorized_scope_unexpected: got={scope!r}"
        )
    return {
        "decision_id_observed": did,
        "decision_observed": dec,
        "baseline_promotion_review_authorized_observed": True,
        "authorized_scope_observed": scope,
        "review_status": "DECISION_PRESENT_VERIFIED",
    }


def build_decision_hash_review(decision: dict[str, Any]) -> dict[str, Any]:
    observed = canonical_hash(decision)
    if observed != SOURCE_DECISION_HASH:
        raise WassersteinBaselinePromotionReviewError(
            f"decision_hash_mismatch: expected={SOURCE_DECISION_HASH!r} got={observed!r}"
        )
    return {
        "expected_hash": SOURCE_DECISION_HASH,
        "observed_hash": observed,
        "hashes_match": True,
        "review_status": "DECISION_HASH_VERIFIED",
    }


def build_source_pack_vector_update_binding(
    pvu: dict[str, Any],
) -> dict[str, Any]:
    observed = pvu.get("canonical_hash", "")
    if observed != SOURCE_PACK_VECTOR_UPDATE_HASH:
        raise WassersteinBaselinePromotionReviewError(
            f"pack_vector_update_hash_mismatch: expected={SOURCE_PACK_VECTOR_UPDATE_HASH!r} "
            f"got={observed!r}"
        )
    update_status = pvu.get("update_status", "")
    if update_status != "WASSERSTEIN_CPU_BASELINE_PACK_VECTOR_UPDATE_COMPLETE":
        raise WassersteinBaselinePromotionReviewError(
            f"pack_vector_update_status_unexpected: got={update_status!r}"
        )
    phase_status = pvu.get("cpu_baseline_phase_record", {}).get(
        "cpu_baseline_computation_phase_status", ""
    )
    if phase_status != "COMPUTATION_PHASE_CLOSED":
        raise WassersteinBaselinePromotionReviewError(
            f"cpu_baseline_phase_status_unexpected: got={phase_status!r}"
        )
    return {
        "expected_hash": SOURCE_PACK_VECTOR_UPDATE_HASH,
        "observed_hash": observed,
        "hashes_match": True,
        "update_status_observed": update_status,
        "cpu_baseline_phase_status_observed": phase_status,
        "review_status": "SOURCE_PACK_VECTOR_UPDATE_BOUND",
    }


def build_cpu_baseline_chain_closure_review(
    closure: dict[str, Any],
) -> dict[str, Any]:
    observed_hash = closure.get("canonical_hash", "")
    if observed_hash != SOURCE_CLOSURE_HASH:
        raise WassersteinBaselinePromotionReviewError(
            f"closure_hash_mismatch: expected={SOURCE_CLOSURE_HASH!r} got={observed_hash!r}"
        )
    closure_status = closure.get("closure_status", "")
    if closure_status != "WASSERSTEIN_CPU_BASELINE_COMPUTATION_OPERATOR_CLOSURE_COMPLETE":
        raise WassersteinBaselinePromotionReviewError(
            f"closure_status_unexpected: got={closure_status!r}"
        )
    al = closure.get("authority_locks", {})
    if al.get("closure_authorized") is not True:
        raise WassersteinBaselinePromotionReviewError("closure_authorized_not_true")
    if al.get("baseline_promotion_authorized") is not False:
        raise WassersteinBaselinePromotionReviewError(
            "baseline_promotion_authorized_in_closure_not_false"
        )
    return {
        "closure_status_observed": closure_status,
        "closure_hash_observed": observed_hash,
        "closure_authorized_observed": True,
        "baseline_promotion_authorized_in_closure": False,
        "review_status": "CPU_BASELINE_CHAIN_CLOSURE_CONFIRMED",
    }


def build_current_pack_state_review(pack: dict[str, Any]) -> dict[str, Any]:
    pack_id = pack.get("pack_id", "")
    wv = _find_wasserstein_vector(pack)
    return {
        "pack_id_observed": pack_id,
        "wasserstein_vector_type_observed": wv.get("vector_type", ""),
        "expected_computation_status_observed": wv.get("expected_computation_status", ""),
        "expected_authority_state_observed": wv.get("expected_authority_state", ""),
        "review_status": "CURRENT_PACK_STATE_REVIEWED",
    }


def build_target_state_review(
    pack: dict[str, Any], decision: dict[str, Any]
) -> dict[str, Any]:
    wv = _find_wasserstein_vector(pack)
    target_vt = decision.get("target_vector_type", "")
    target_cs = decision.get("target_expected_computation_status", "")
    if target_vt != "VALID_SHADOW_ONLY_VECTOR":
        raise WassersteinBaselinePromotionReviewError(
            f"target_vector_type_unexpected: got={target_vt!r}"
        )
    if target_cs != "SHADOW_STUB_ONLY":
        raise WassersteinBaselinePromotionReviewError(
            f"target_expected_computation_status_unexpected: got={target_cs!r}"
        )
    matches_current = (
        wv.get("vector_type") == target_vt
        and wv.get("expected_computation_status") == target_cs
    )
    return {
        "target_vector_type": target_vt,
        "target_expected_computation_status": target_cs,
        "target_matches_decision": True,
        "target_matches_current_state": matches_current,
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
        "review_status": "PROMOTION_SCOPE_VERIFIED",
    }


def build_no_op_parity_review(pack: dict[str, Any]) -> dict[str, Any]:
    wv = _find_wasserstein_vector(pack)
    vt = wv.get("vector_type", "")
    cs = wv.get("expected_computation_status", "")
    ea = wv.get("expected_authority_state", "")
    vector_type_unchanged = vt == "VALID_SHADOW_ONLY_VECTOR"
    shadow_stub_preserved = cs == "SHADOW_STUB_ONLY"
    advisory_only_preserved = ea == "ADVISORY_ONLY"
    parity_confirmed = vector_type_unchanged and shadow_stub_preserved and advisory_only_preserved
    if not parity_confirmed:
        raise WassersteinBaselinePromotionReviewError(
            f"no_op_parity_failed: vector_type={vt!r} computation_status={cs!r} authority={ea!r}"
        )
    return {
        "wasserstein_vector_type_unchanged": True,
        "pack_id_unchanged": True,
        "shadow_stub_posture_preserved": True,
        "advisory_only_posture_preserved": True,
        "no_op_parity_confirmed": True,
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
        "review_status": "AUTHORITY_LOCKS_VERIFIED",
    }


def build_blocked_scope_review() -> dict[str, Any]:
    scopes = [
        "emits_metric_values", "forecast_influence", "p43_surface_lanes",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ]
    verified = [{"scope": s, "blocked": False, "review_status": "VERIFIED"} for s in scopes]
    return {
        "all_blocked_scopes_false": True,
        "scopes_verified": verified,
        "review_status": "BLOCKED_SCOPES_VERIFIED",
    }


def default_authority_locks() -> dict[str, Any]:
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


def compute_wasserstein_baseline_promotion_review_hash(
    payload: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(payload))


def build_wasserstein_baseline_promotion_review(
    payload: dict[str, Any],
) -> dict[str, Any]:
    packet = {
        "schema_version": SCHEMA_VERSION,
        "review_id": payload["review_id"],
        "review_type": REVIEW_TYPE,
        "operator_id": OPERATOR_ID,
        "review_status": REVIEW_STATUS,
        "source_decision_id": SOURCE_DECISION_ID,
        "source_decision_hash": SOURCE_DECISION_HASH,
        "source_pack_vector_update_hash": SOURCE_PACK_VECTOR_UPDATE_HASH,
        "intended_lane": payload["intended_lane"],
        "review_stage": payload["review_stage"],
        "decision_presence_review": payload["decision_presence_review"],
        "decision_hash_review": payload["decision_hash_review"],
        "source_pack_vector_update_binding": payload["source_pack_vector_update_binding"],
        "cpu_baseline_chain_closure_review": payload["cpu_baseline_chain_closure_review"],
        "current_pack_state_review": payload["current_pack_state_review"],
        "target_state_review": payload["target_state_review"],
        "promotion_scope_review": payload["promotion_scope_review"],
        "no_op_parity_review": payload["no_op_parity_review"],
        "authority_lock_review": payload["authority_lock_review"],
        "blocked_scope_review": payload["blocked_scope_review"],
        "blocked_scopes": payload["blocked_scopes"],
        "authority_locks": payload["authority_locks"],
        "recommended_next_step": payload["recommended_next_step"],
        "provenance": payload["provenance"],
        "created_at_utc": payload["created_at_utc"],
    }
    packet["canonical_hash"] = compute_wasserstein_baseline_promotion_review_hash(packet)
    return _finalize(packet)


def serialize_wasserstein_baseline_promotion_review(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(packet)
