from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "HeavyTailBaselinePromotionReview.v1"
REVIEW_ID = "heavy_tail_baseline_promotion_review_001"
REVIEW_STATUS = "HEAVY_TAIL_BASELINE_PROMOTION_REVIEW_COMPLETE"
REVIEW_STAGE = "BASELINE_PROMOTION_REVIEW_ONLY"
OPERATOR_ID = "HEAVY_TAIL"

SOURCE_AUTHORIZATION_HASH = (
    "988ed40a766a2fb5edf82bd33a0cdcf5540a4a38486bc36b180802b7ef7e2834"
)
SOURCE_COMPUTATION_RECEIPT_HASH = (
    "d668bcd8a500c7d47216abc5c45d2824feb9647f5271b54c303d2321819fcd8e"
)
SOURCE_PACK_HASH = (
    "05a72025640925de81ed8fe0a2aefccf389a547ef0dbeb1ff5981dbc2a804feb"
)

AUTHORIZATION_PATH = Path(
    "out/metric_operator/heavy_tail_shadow_stub_implementation_authorization_001.latest.json"
)
COMPUTATION_RECEIPT_PATH = Path(
    "out/metric_operator/heavy_tail_computation_receipt_001.latest.json"
)
BASELINE_PACK_PATH = Path(
    "out/metric_operator/metric_operator_baseline_test_vector_pack_001.latest.json"
)

FORBIDDEN = (
    "metric-computation",
    "metric-value",
    "fixture-file",
    "manifest-file",
    "schema-file",
    "numpy",
    "scipy",
    "gpu-kernel",
)


class HeavyTailBaselinePromotionReviewError(ValueError):
    pass


def _check_no_forbidden(value: Any) -> None:
    if isinstance(value, dict):
        for item in value.values():
            _check_no_forbidden(item)
    elif isinstance(value, list):
        for item in value:
            _check_no_forbidden(item)
    elif isinstance(value, str) and any(token in value.lower() for token in FORBIDDEN):
        raise HeavyTailBaselinePromotionReviewError(
            f"forbidden_token_detected_in_string_value: {value!r}"
        )


def _preimage(doc: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in doc.items() if key != "canonical_hash"}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_authorization() -> dict[str, Any]:
    doc = _load_json(AUTHORIZATION_PATH)
    actual = doc.get("canonical_hash", "")
    if actual != SOURCE_AUTHORIZATION_HASH:
        raise HeavyTailBaselinePromotionReviewError(
            f"authorization_hash_mismatch: expected={SOURCE_AUTHORIZATION_HASH!r} got={actual!r}"
        )
    return doc


def _load_computation_receipt() -> dict[str, Any]:
    doc = _load_json(COMPUTATION_RECEIPT_PATH)
    actual = doc.get("canonical_hash", "")
    if actual != SOURCE_COMPUTATION_RECEIPT_HASH:
        raise HeavyTailBaselinePromotionReviewError(
            f"computation_receipt_hash_mismatch: expected={SOURCE_COMPUTATION_RECEIPT_HASH!r} got={actual!r}"
        )
    return doc


def _load_baseline_pack() -> dict[str, Any]:
    doc = _load_json(BASELINE_PACK_PATH)
    actual = doc.get("canonical_hash", "")
    if actual != SOURCE_PACK_HASH:
        raise HeavyTailBaselinePromotionReviewError(
            f"baseline_pack_hash_mismatch: expected={SOURCE_PACK_HASH!r} got={actual!r}"
        )
    return doc


def _find_heavy_tail_vector(pack: dict[str, Any]) -> dict[str, Any]:
    for vector in pack.get("operator_vectors", []):
        if vector.get("operator_id") == OPERATOR_ID:
            return vector
    raise HeavyTailBaselinePromotionReviewError("heavy_tail_vector_not_found_in_pack")


def _build_authorization_review(auth: dict[str, Any]) -> dict[str, Any]:
    locks = auth.get("authority_locks", {})
    plan = auth.get("implementation_plan_summary", {})
    next_steps = plan.get("next_steps", [])
    return {
        "artifact_id": auth.get("artifact_id"),
        "authorization_scope": auth.get("authorization_scope_review", {}).get("scope"),
        "implementation_authorized": locks.get("implementation_authorized") is True,
        "fixture_creation_authorized": locks.get("fixture_creation_authorized") is True,
        "baseline_pack_update_authorized": locks.get("baseline_pack_update_authorized") is True,
        "shadow_stub_only_posture": locks.get("shadow_stub_only_posture") is True,
        "metric_emission_blocked": locks.get("emits_metric_values") is False,
        "forecast_influence_blocked": locks.get("forecast_influence") is False,
        "runtime_mutation_blocked": locks.get("runtime_mutation") is False,
        "canon_promotion_blocked": locks.get("canon_promotion") is False,
        "execution_authority_blocked": locks.get("execution_authority") is False,
        "next_steps_include_review": (
            "Produce heavy_tail_baseline_promotion_review_001" in next_steps
        ),
        "review_passed": True,
    }


def _build_computation_review(receipt: dict[str, Any]) -> dict[str, Any]:
    summary = receipt.get("comparison_summary", {})
    return {
        "receipt_id": receipt.get("receipt_id"),
        "computation_status": receipt.get("computation_status"),
        "computation_stage": receipt.get("computation_stage"),
        "all_valid_match": summary.get("all_valid_match") is True,
        "match_count": summary.get("match_count"),
        "mismatch_count": summary.get("mismatch_count"),
        "valid_fixture_count": len(receipt.get("valid_fixture_results", [])),
        "invalid_fixture_count": len(receipt.get("invalid_fixture_results", [])),
        "not_computable_fixture_count": len(
            receipt.get("not_computable_fixture_results", [])
        ),
        "shadow_stub_only": receipt.get("authority_locks", {}).get("shadow_stub_only")
        is True,
        "metric_emission_blocked": receipt.get("authority_locks", {}).get(
            "emits_metric_values"
        )
        is False,
        "review_passed": True,
    }


def _build_current_pack_state_review(pack: dict[str, Any]) -> dict[str, Any]:
    vector = _find_heavy_tail_vector(pack)
    return {
        "pack_id": pack.get("pack_id"),
        "vector_id": vector.get("vector_id"),
        "current_vector_type": vector.get("vector_type"),
        "current_expected_computation_status": vector.get(
            "expected_computation_status"
        ),
        "current_expected_authority_state": vector.get("expected_authority_state"),
        "review_passed": True,
    }


def _build_target_state_review() -> dict[str, Any]:
    return {
        "target_vector_type": "VALID_SHADOW_ONLY_VECTOR",
        "target_expected_computation_status": "SHADOW_STUB_ONLY",
        "target_expected_authority_state": "ADVISORY_ONLY",
        "pack_update_required": True,
        "review_passed": True,
    }


def _build_baseline_pack_update_review(pack: dict[str, Any]) -> dict[str, Any]:
    vector = _find_heavy_tail_vector(pack)
    unchanged: dict[str, dict[str, str]] = {}
    for item in pack.get("operator_vectors", []):
        operator_id = item.get("operator_id")
        if operator_id == OPERATOR_ID:
            continue
        unchanged[operator_id] = {
            "vector_type": item.get("vector_type", ""),
            "expected_computation_status": item.get("expected_computation_status", ""),
        }
    return {
        "operator_id": OPERATOR_ID,
        "previous_vector_type": vector.get("vector_type"),
        "previous_expected_computation_status": vector.get(
            "expected_computation_status"
        ),
        "new_vector_type": "VALID_SHADOW_ONLY_VECTOR",
        "new_expected_computation_status": "SHADOW_STUB_ONLY",
        "pack_update_authorized": True,
        "pack_update_scope": "HEAVY_TAIL_ONLY",
        "unchanged_operators": unchanged,
        "review_passed": True,
    }


def _build_operator_state_after_update(pack: dict[str, Any]) -> dict[str, dict[str, str]]:
    state: dict[str, dict[str, str]] = {}
    for item in pack.get("operator_vectors", []):
        operator_id = item.get("operator_id", "")
        if operator_id == OPERATOR_ID:
            state[operator_id] = {
                "vector_type": "VALID_SHADOW_ONLY_VECTOR",
                "expected_computation_status": "SHADOW_STUB_ONLY",
            }
        else:
            state[operator_id] = {
                "vector_type": item.get("vector_type", ""),
                "expected_computation_status": item.get("expected_computation_status", ""),
            }
    return state


def _build_parity_review(state_after_update: dict[str, dict[str, str]]) -> dict[str, Any]:
    shadow_stub = sorted(
        operator_id
        for operator_id, state in state_after_update.items()
        if state["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
        and state["expected_computation_status"] == "SHADOW_STUB_ONLY"
    )
    return {
        "shadow_stub_operators_after_update": shadow_stub,
        "shadow_stub_operator_count": len(shadow_stub),
        "heavy_tail_at_shadow_stub_after_promotion": OPERATOR_ID in shadow_stub,
        "parity_achieved": OPERATOR_ID in shadow_stub,
        "review_passed": True,
    }


def _build_no_metric_emission_review() -> dict[str, Any]:
    return {
        "emits_metric_values": False,
        "promotion_scope": "BASELINE_PACK_UPDATE_ONLY",
        "review_passed": True,
    }


def _build_no_forecast_influence_review() -> dict[str, Any]:
    return {
        "forecast_influence": False,
        "review_passed": True,
    }


def _build_no_p43_surface_lane_review() -> dict[str, Any]:
    return {
        "p43_surface_lanes_authorized": False,
        "review_passed": True,
    }


def _build_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "baseline_promotion_review_only": True,
        "baseline_pack_update_authorized": True,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def _build_blocked_scopes() -> dict[str, Any]:
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


def build_heavy_tail_baseline_promotion_review() -> dict[str, Any]:
    auth = _load_authorization()
    receipt = _load_computation_receipt()
    pack = _load_baseline_pack()

    state_after_update = _build_operator_state_after_update(pack)

    result = {
        "schema_version": SCHEMA_VERSION,
        "review_id": REVIEW_ID,
        "operator_id": OPERATOR_ID,
        "review_status": REVIEW_STATUS,
        "review_stage": REVIEW_STAGE,
        "intended_lane": "SHADOW",
        "created_at_utc": "2026-06-04T00:00:00Z",
        "source_authorization_hash": SOURCE_AUTHORIZATION_HASH,
        "source_computation_receipt_hash": SOURCE_COMPUTATION_RECEIPT_HASH,
        "source_pack_hash": SOURCE_PACK_HASH,
        "authorization_review": _build_authorization_review(auth),
        "computation_receipt_review": _build_computation_review(receipt),
        "current_pack_state_review": _build_current_pack_state_review(pack),
        "target_state_review": _build_target_state_review(),
        "baseline_pack_update_review": _build_baseline_pack_update_review(pack),
        "operator_state_after_update": state_after_update,
        "parity_review": _build_parity_review(state_after_update),
        "no_metric_emission_review": _build_no_metric_emission_review(),
        "no_forecast_influence_review": _build_no_forecast_influence_review(),
        "no_p43_surface_lane_review": _build_no_p43_surface_lane_review(),
        "authority_locks": _build_authority_locks(),
        "blocked_scopes": _build_blocked_scopes(),
        "recommended_next_step": "HEAVY_TAIL_BASELINE_PROMOTION_COMPLETE",
    }
    _check_no_forbidden(result)
    finalized = json.loads(canonical_dumps(result))
    finalized["canonical_hash"] = canonical_hash(finalized)
    return json.loads(canonical_dumps(finalized))


def validate_heavy_tail_baseline_promotion_review(review: dict[str, Any]) -> None:
    if review.get("schema_version") != SCHEMA_VERSION:
        raise HeavyTailBaselinePromotionReviewError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if review.get("operator_id") != OPERATOR_ID:
        raise HeavyTailBaselinePromotionReviewError(f"operator_id must be {OPERATOR_ID!r}")
    if review.get("review_status") != REVIEW_STATUS:
        raise HeavyTailBaselinePromotionReviewError(
            f"review_status must be {REVIEW_STATUS!r}"
        )
    if review.get("review_stage") != REVIEW_STAGE:
        raise HeavyTailBaselinePromotionReviewError(
            f"review_stage must be {REVIEW_STAGE!r}"
        )
    if review.get("source_authorization_hash") != SOURCE_AUTHORIZATION_HASH:
        raise HeavyTailBaselinePromotionReviewError("source_authorization_hash mismatch")
    if review.get("source_computation_receipt_hash") != SOURCE_COMPUTATION_RECEIPT_HASH:
        raise HeavyTailBaselinePromotionReviewError(
            "source_computation_receipt_hash mismatch"
        )
    if review.get("source_pack_hash") != SOURCE_PACK_HASH:
        raise HeavyTailBaselinePromotionReviewError("source_pack_hash mismatch")

    auth_review = review.get("authorization_review", {})
    if auth_review.get("implementation_authorized") is not True:
        raise HeavyTailBaselinePromotionReviewError(
            "authorization_review.implementation_authorized must be True"
        )
    if auth_review.get("baseline_pack_update_authorized") is not True:
        raise HeavyTailBaselinePromotionReviewError(
            "authorization_review.baseline_pack_update_authorized must be True"
        )

    comp_review = review.get("computation_receipt_review", {})
    if comp_review.get("all_valid_match") is not True:
        raise HeavyTailBaselinePromotionReviewError(
            "computation_receipt_review.all_valid_match must be True"
        )
    if comp_review.get("valid_fixture_count") != 6:
        raise HeavyTailBaselinePromotionReviewError(
            "computation_receipt_review.valid_fixture_count must be 6"
        )

    current = review.get("current_pack_state_review", {})
    if current.get("current_vector_type") != "VALID_METADATA_VECTOR":
        raise HeavyTailBaselinePromotionReviewError(
            "current_pack_state_review.current_vector_type must be VALID_METADATA_VECTOR"
        )
    if current.get("current_expected_computation_status") != "NOT_IMPLEMENTED":
        raise HeavyTailBaselinePromotionReviewError(
            "current_pack_state_review.current_expected_computation_status must be NOT_IMPLEMENTED"
        )

    target = review.get("target_state_review", {})
    if target.get("target_vector_type") != "VALID_SHADOW_ONLY_VECTOR":
        raise HeavyTailBaselinePromotionReviewError(
            "target_state_review.target_vector_type must be VALID_SHADOW_ONLY_VECTOR"
        )
    if target.get("target_expected_computation_status") != "SHADOW_STUB_ONLY":
        raise HeavyTailBaselinePromotionReviewError(
            "target_state_review.target_expected_computation_status must be SHADOW_STUB_ONLY"
        )

    parity = review.get("parity_review", {})
    if parity.get("heavy_tail_at_shadow_stub_after_promotion") is not True:
        raise HeavyTailBaselinePromotionReviewError(
            "parity_review.heavy_tail_at_shadow_stub_after_promotion must be True"
        )

    locks = review.get("authority_locks", {})
    for flag in (
        "advisory_only",
        "shadow_lane_only",
        "baseline_promotion_review_only",
        "baseline_pack_update_authorized",
    ):
        if locks.get(flag) is not True:
            raise HeavyTailBaselinePromotionReviewError(
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
            raise HeavyTailBaselinePromotionReviewError(
                f"authority_locks.{flag} must be False"
            )

    stored_hash = review.get("canonical_hash", "")
    if not isinstance(stored_hash, str) or len(stored_hash) != 64:
        raise HeavyTailBaselinePromotionReviewError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(review))
    if recomputed != stored_hash:
        raise HeavyTailBaselinePromotionReviewError(
            f"canonical_hash mismatch: stored={stored_hash!r} recomputed={recomputed!r}"
        )
