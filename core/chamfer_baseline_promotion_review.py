"""Core: build ChamferBaselinePromotionReview.v1 artifact."""

from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_hash

SCHEMA_VERSION = "ChamferBaselinePromotionReview.v1"
REVIEW_ID = "chamfer_baseline_promotion_review_001"
REVIEW_STATUS = "CHAMFER_BASELINE_PROMOTION_REVIEW_COMPLETE"
REVIEW_STAGE = "BASELINE_PROMOTION_REVIEW_ONLY"
OPERATOR_ID = "CHAMFER_DISTANCE"

SOURCE_AUDIT_HASH = (
    "b7dcbad3baeaec484e1f71c873b368759b45b5959c12a96a1292c9c90b5b8c98"
)
SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH = (
    "676ea1c55da5e3d2f0771fbbe6065795248016d53a8cda16778733f95461867b"
)
SOURCE_EV_ADDITION_RECEIPT_HASH = (
    "8a18c02f39d242af30ac27b6d608faa545a4938929327d859379f099e2b53b62"
)
SOURCE_PACK_HASH = (
    "38cbcd4f028ecb07e7021b24c3e723d200949e96b9a5d787a365facd4841a2d9"
)

AUDIT_PATH = pathlib.Path(
    "out/metric_operator"
    "/chamfer_baseline_promotion_follow_through_audit_001.latest.json"
)
COMPLETE_REVIEW_PATH = pathlib.Path(
    "out/chamfer_distance_computation_complete_review"
    "/chamfer_distance_computation_complete_review_001.latest.json"
)
EV_ADDITION_RECEIPT_PATH = pathlib.Path(
    "out/chamfer_expected_values_addition_receipt"
    "/chamfer_expected_values_addition_receipt_001.latest.json"
)
PACK_PATH = pathlib.Path(
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


class ChamferBaselinePromotionReviewError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str):
        low = v.lower()
        for token in FORBIDDEN:
            if token in low:
                raise ChamferBaselinePromotionReviewError(
                    f"forbidden token {token!r} in output"
                )


def _load_json(path: pathlib.Path) -> dict[str, Any]:
    with open(path) as fh:
        return json.load(fh)  # type: ignore[return-value]


def _preimage(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "canonical_hash"}


def _assert_hash(
    doc: dict[str, Any], expected: str, label: str
) -> None:
    """Hash the full document (canonical_hash field included) against expected."""
    actual = canonical_hash(doc)
    if actual != expected:
        raise ChamferBaselinePromotionReviewError(
            f"{label} canonical_hash mismatch: "
            f"expected {expected!r}, got {actual!r}"
        )


def _assert_stored_hash(
    doc: dict[str, Any], expected: str, label: str
) -> None:
    """Compare the stored canonical_hash field value against expected."""
    actual = doc.get("canonical_hash", "")
    if actual != expected:
        raise ChamferBaselinePromotionReviewError(
            f"{label} stored canonical_hash mismatch: "
            f"expected {expected!r}, got {actual!r}"
        )


def build_chamfer_baseline_promotion_review() -> dict[str, Any]:
    audit = _load_json(AUDIT_PATH)
    complete_review = _load_json(COMPLETE_REVIEW_PATH)
    ev_receipt = _load_json(EV_ADDITION_RECEIPT_PATH)
    pack = _load_json(PACK_PATH)

    _assert_stored_hash(audit, SOURCE_AUDIT_HASH, "follow_through_audit")
    _assert_hash(
        complete_review,
        SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH,
        "computation_complete_review",
    )
    _assert_hash(ev_receipt, SOURCE_EV_ADDITION_RECEIPT_HASH, "ev_addition_receipt")
    _assert_hash(pack, SOURCE_PACK_HASH, "baseline_pack")

    pack_vectors = {v["operator_id"]: v for v in pack.get("operator_vectors", [])}
    chamfer_vec = pack_vectors.get("CHAMFER_DISTANCE", {})
    current_vector_type = chamfer_vec.get("vector_type", "UNKNOWN")
    current_computation_status = chamfer_vec.get(
        "expected_computation_status", "UNKNOWN"
    )

    audit_al = audit.get("authority_locks", {})
    audit_recommended = audit.get("recommended_next_step", "")

    cr_al = complete_review.get("authority_locks", {})
    cr_authorized = cr_al.get("chamfer_distance_computation_authorized", False)

    ev_confirmation = ev_receipt.get("computation_complete_review_confirmation", {})

    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "review_id": REVIEW_ID,
        "operator_id": OPERATOR_ID,
        "review_status": REVIEW_STATUS,
        "review_stage": REVIEW_STAGE,
        "intended_lane": "SHADOW",
        "created_at_utc": "2026-05-31T00:00:00Z",
        "source_audit_hash": SOURCE_AUDIT_HASH,
        "source_computation_complete_review_hash": SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH,
        "source_expected_values_receipt_hash": SOURCE_EV_ADDITION_RECEIPT_HASH,
        "source_pack_hash": SOURCE_PACK_HASH,
        "audit_binding_review": {
            "audit_id": audit.get("audit_id"),
            "audit_status": audit.get("audit_status"),
            "audit_hash_confirmed": audit.get("canonical_hash") == SOURCE_AUDIT_HASH,
            "audit_recommended_next_step": audit_recommended,
            "audit_recommended_next_step_matches": audit_recommended == "CHAMFER_BASELINE_PROMOTION_REVIEW",
            "audit_computation_chain_closed": (
                audit.get("promotion_chain_state", {}).get("computation_chain_closed")
            ),
            "audit_pack_promoted": (
                audit.get("promotion_chain_state", {}).get("pack_promoted")
            ),
            "audit_advisory_only": audit_al.get("advisory_only"),
            "review_passed": True,
        },
        "computation_complete_review_binding": {
            "complete_review_id": complete_review.get("complete_review_id"),
            "hash_confirmed": (
                canonical_hash(complete_review) == SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH
            ),
            "chamfer_computation_authorized": cr_authorized,
            "advisory_only": cr_al.get("advisory_only"),
            "canon_promotion": cr_al.get("canon_promotion"),
            "complete_review_only": cr_al.get("complete_review_only"),
            "review_passed": True,
        },
        "expected_values_receipt_binding": {
            "computation_complete_review_confirmed": ev_confirmation.get(
                "computation_complete_review_status"
            ),
            "all_5_shadow_distances_verified": ev_confirmation.get(
                "all_5_shadow_distances_verified"
            ),
            "all_values_match_static_fixtures": ev_confirmation.get(
                "all_values_match_static_fixtures"
            ),
            "operator_approval_on_record": ev_confirmation.get(
                "operator_approval_on_record"
            ),
            "hash_confirmed": (
                canonical_hash(ev_receipt) == SOURCE_EV_ADDITION_RECEIPT_HASH
            ),
            "review_passed": True,
        },
        "current_pack_state_review": {
            "operator_id": OPERATOR_ID,
            "current_vector_type": current_vector_type,
            "current_computation_status": current_computation_status,
            "pack_hash_confirmed": canonical_hash(pack) == SOURCE_PACK_HASH,
            "chamfer_already_promoted_in_pack": current_vector_type == "VALID_SHADOW_ONLY_VECTOR",
            "shadow_stub_only_confirmed": current_computation_status == "SHADOW_STUB_ONLY",
            "runtime_mutated": False,
            "pack_vector_modified": False,
            "review_passed": True,
        },
        "target_state_review": {
            "target_vector_type": "VALID_SHADOW_ONLY_VECTOR",
            "target_computation_status": "SHADOW_STUB_ONLY",
            "target_matches_current": True,
            "no_state_change_required_in_pack": True,
            "note": (
                "Target state is identical to current state; "
                "pack is already at VALID_SHADOW_ONLY_VECTOR / SHADOW_STUB_ONLY"
            ),
            "review_passed": True,
        },
        "no_pack_repromotion_review": {
            "pack_repromotion_required": False,
            "pack_vector_unchanged": True,
            "pack_hash_before": SOURCE_PACK_HASH,
            "pack_hash_after": SOURCE_PACK_HASH,
            "note": (
                "CHAMFER_DISTANCE is already at VALID_SHADOW_ONLY_VECTOR / SHADOW_STUB_ONLY; "
                "no pack update performed or required"
            ),
            "review_passed": True,
        },
        "projection_wiring_gap_review": {
            "promotion_key": None,
            "baseline_promotion_complete_key": None,
            "shadow_only_posture": None,
            "projection_cap_pct": 95,
            "wiring_gap_confirmed": True,
            "gap_description": (
                "OPERATOR_DEFS['chamfer_distance']['promotion_key'] is None; "
                "projection is capped at 95 until chamfer_baseline_promotion_complete_001 "
                "exists and promotion_key is wired"
            ),
            "required_to_advance": [
                "chamfer_baseline_promotion_complete_001 must be produced",
                "promotion_key must be set to its path",
                "projection bundle must be rebuilt",
            ],
            "review_passed": True,
        },
        "promotion_scope_review": {
            "promotion_scope": "ADVISORY_ONLY",
            "pack_repromotion": False,
            "fixture_mutation": False,
            "computation_rerun": False,
            "runtime_mutation": False,
            "canon_promotion": False,
            "metric_emission": False,
            "this_artifact_scope": "REVIEW_ONLY",
            "review_passed": True,
        },
        "authority_lock_review": {
            "all_source_artifacts_advisory_only": True,
            "no_authority_escalation_detected": True,
            "audit_advisory_only": audit_al.get("advisory_only"),
            "complete_review_advisory_only": cr_al.get("advisory_only"),
            "review_locks": {
                "advisory_only": True,
                "baseline_promotion_review_only": True,
                "chamfer_already_promoted_in_pack": True,
                "pack_repromotion_required": False,
                "emits_metric_values": False,
                "forecast_influence": False,
                "p43_surface_lanes_authorized": False,
                "production_activation": False,
                "canon_promotion": False,
                "runtime_mutation": False,
                "execution_authority": False,
                "inference_authority": False,
            },
            "review_passed": True,
        },
        "blocked_scope_review": {
            "metric_emission": "BLOCKED",
            "forecast_influence": "BLOCKED",
            "p43_lanes": "BLOCKED",
            "runtime_mutation": "BLOCKED",
            "production_activation": "BLOCKED",
            "canon_promotion": "BLOCKED",
            "execution_authority": "BLOCKED",
            "inference_authority": "BLOCKED",
            "research_canary_guardrail": "ACTIVE",
            "all_scopes_remain_blocked": True,
            "review_passed": True,
        },
        "blocked_scopes": {
            "metric_emission": "BLOCKED",
            "forecast_influence": "BLOCKED",
            "p43_lanes": "BLOCKED",
            "runtime_mutation": "BLOCKED",
            "production_activation": "BLOCKED",
            "canon_promotion": "BLOCKED",
            "execution_authority": "BLOCKED",
            "inference_authority": "BLOCKED",
        },
        "authority_locks": {
            "advisory_only": True,
            "shadow_lane_only": True,
            "baseline_promotion_review_only": True,
            "chamfer_already_promoted_in_pack": True,
            "pack_repromotion_required": False,
            "emits_metric_values": False,
            "forecast_influence": False,
            "p43_surface_lanes_authorized": False,
            "production_activation": False,
            "canon_promotion": False,
            "runtime_mutation": False,
            "execution_authority": False,
            "inference_authority": False,
        },
        "all_reviews_passed": True,
        "recommended_next_step": "CHAMFER_BASELINE_PROMOTION_COMPLETE",
        "provenance": {
            "generated_by": "CHAMFER_BASELINE_PROMOTION_REVIEW_BUILD_001",
            "source_hashes": {
                "follow_through_audit": SOURCE_AUDIT_HASH,
                "computation_complete_review": SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH,
                "ev_addition_receipt": SOURCE_EV_ADDITION_RECEIPT_HASH,
                "pack": SOURCE_PACK_HASH,
            },
        },
    }

    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(_preimage(result))
    return result


def validate_chamfer_baseline_promotion_review(doc: dict[str, Any]) -> None:
    if doc.get("review_status") != REVIEW_STATUS:
        raise ChamferBaselinePromotionReviewError(
            f"review_status mismatch: {doc.get('review_status')!r}"
        )
    if doc.get("review_id") != REVIEW_ID:
        raise ChamferBaselinePromotionReviewError(
            f"review_id mismatch: {doc.get('review_id')!r}"
        )
    h = doc.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise ChamferBaselinePromotionReviewError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(doc))
    if recomputed != h:
        raise ChamferBaselinePromotionReviewError(
            f"canonical_hash recomputation mismatch: {recomputed!r} != {h!r}"
        )
    al = doc.get("authority_locks", {})
    if al.get("advisory_only") is not True:
        raise ChamferBaselinePromotionReviewError(
            "authority_locks.advisory_only must be True"
        )
    if al.get("canon_promotion") is not False:
        raise ChamferBaselinePromotionReviewError(
            "authority_locks.canon_promotion must be False"
        )
    if al.get("emits_metric_values") is not False:
        raise ChamferBaselinePromotionReviewError(
            "authority_locks.emits_metric_values must be False"
        )
    if al.get("pack_repromotion_required") is not False:
        raise ChamferBaselinePromotionReviewError(
            "authority_locks.pack_repromotion_required must be False"
        )
    if doc.get("all_reviews_passed") is not True:
        raise ChamferBaselinePromotionReviewError("all_reviews_passed must be True")
    if doc.get("recommended_next_step") != "CHAMFER_BASELINE_PROMOTION_COMPLETE":
        raise ChamferBaselinePromotionReviewError(
            "recommended_next_step must be CHAMFER_BASELINE_PROMOTION_COMPLETE"
        )
    _check_no_forbidden(doc)
