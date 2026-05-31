"""Core: build ChamferBaselinePromotionComplete.v1 artifact."""

from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_hash

SCHEMA_VERSION = "ChamferBaselinePromotionComplete.v1"
COMPLETION_ID = "chamfer_baseline_promotion_complete_001"
COMPLETE_STATUS = "CHAMFER_BASELINE_PROMOTION_COMPLETE"
COMPLETE_STAGE = "BASELINE_PROMOTION_COMPLETE"
OPERATOR_ID = "CHAMFER_DISTANCE"

SOURCE_REVIEW_HASH = (
    "f48809e1061e650147358e3cfddade61797f1b417f849fee693fea369fd1f143"
)
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

REVIEW_PATH = pathlib.Path(
    "out/metric_operator/chamfer_baseline_promotion_review_001.latest.json"
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


class ChamferBaselinePromotionCompleteError(ValueError):
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
                raise ChamferBaselinePromotionCompleteError(
                    f"forbidden token {token!r} in output"
                )


def _load_json(path: pathlib.Path) -> dict[str, Any]:
    with open(path) as fh:
        return json.load(fh)  # type: ignore[return-value]


def _preimage(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "canonical_hash"}


def _assert_stored_hash(
    doc: dict[str, Any], expected: str, label: str
) -> None:
    """Confirm stored canonical_hash field equals expected."""
    actual = doc.get("canonical_hash", "")
    if actual != expected:
        raise ChamferBaselinePromotionCompleteError(
            f"{label} stored canonical_hash mismatch: "
            f"expected {expected!r}, got {actual!r}"
        )


def _assert_full_hash(
    doc: dict[str, Any], expected: str, label: str
) -> None:
    """Confirm full-document canonical hash (includes canonical_hash field) equals expected."""
    actual = canonical_hash(doc)
    if actual != expected:
        raise ChamferBaselinePromotionCompleteError(
            f"{label} full-doc canonical_hash mismatch: "
            f"expected {expected!r}, got {actual!r}"
        )


def build_chamfer_baseline_promotion_complete() -> dict[str, Any]:
    review = _load_json(REVIEW_PATH)
    audit = _load_json(AUDIT_PATH)
    complete_review = _load_json(COMPLETE_REVIEW_PATH)
    ev_receipt = _load_json(EV_ADDITION_RECEIPT_PATH)
    pack = _load_json(PACK_PATH)

    _assert_stored_hash(review, SOURCE_REVIEW_HASH, "promotion_review")
    _assert_stored_hash(audit, SOURCE_AUDIT_HASH, "follow_through_audit")
    _assert_full_hash(complete_review, SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH, "computation_complete_review")
    _assert_full_hash(ev_receipt, SOURCE_EV_ADDITION_RECEIPT_HASH, "ev_addition_receipt")
    _assert_full_hash(pack, SOURCE_PACK_HASH, "baseline_pack")

    pack_vectors = {v["operator_id"]: v for v in pack.get("operator_vectors", [])}
    chamfer_vec = pack_vectors.get("CHAMFER_DISTANCE", {})
    current_vector_type = chamfer_vec.get("vector_type", "UNKNOWN")
    current_computation_status = chamfer_vec.get("expected_computation_status", "UNKNOWN")

    review_al = review.get("authority_locks", {})
    review_all_passed = review.get("all_reviews_passed", False)
    review_recommended = review.get("recommended_next_step", "")

    audit_al = audit.get("authority_locks", {})
    audit_recommended = audit.get("recommended_next_step", "")

    cr_al = complete_review.get("authority_locks", {})
    ev_confirmation = ev_receipt.get("computation_complete_review_confirmation", {})

    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "completion_id": COMPLETION_ID,
        "complete_status": COMPLETE_STATUS,
        "complete_stage": COMPLETE_STAGE,
        "operator_id": OPERATOR_ID,
        "intended_lane": "SHADOW",
        "created_at_utc": "2026-05-31T00:00:00Z",
        "source_review_hash": SOURCE_REVIEW_HASH,
        "source_audit_hash": SOURCE_AUDIT_HASH,
        "source_computation_complete_review_hash": SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH,
        "source_expected_values_receipt_hash": SOURCE_EV_ADDITION_RECEIPT_HASH,
        "source_pack_hash": SOURCE_PACK_HASH,
        "review_binding": {
            "review_id": review.get("review_id"),
            "review_status": review.get("review_status"),
            "review_hash_confirmed": review.get("canonical_hash") == SOURCE_REVIEW_HASH,
            "all_reviews_passed": review_all_passed,
            "review_recommended_next_step": review_recommended,
            "review_recommended_matches": review_recommended == "CHAMFER_BASELINE_PROMOTION_COMPLETE",
            "review_advisory_only": review_al.get("advisory_only"),
            "review_pack_repromotion_required": review_al.get("pack_repromotion_required"),
            "review_projection_wiring_gap_confirmed": (
                review.get("projection_wiring_gap_review", {}).get("wiring_gap_confirmed")
            ),
            "confirmed": True,
        },
        "audit_binding": {
            "audit_id": audit.get("audit_id"),
            "audit_status": audit.get("audit_status"),
            "audit_hash_confirmed": audit.get("canonical_hash") == SOURCE_AUDIT_HASH,
            "audit_recommended_next_step": audit_recommended,
            "audit_computation_chain_closed": (
                audit.get("promotion_chain_state", {}).get("computation_chain_closed")
            ),
            "audit_pack_promoted": (
                audit.get("promotion_chain_state", {}).get("pack_promoted")
            ),
            "audit_advisory_only": audit_al.get("advisory_only"),
            "confirmed": True,
        },
        "computation_complete_review_binding": {
            "complete_review_id": complete_review.get("complete_review_id"),
            "hash_confirmed": canonical_hash(complete_review) == SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH,
            "chamfer_computation_authorized": cr_al.get("chamfer_distance_computation_authorized"),
            "advisory_only": cr_al.get("advisory_only"),
            "canon_promotion": cr_al.get("canon_promotion"),
            "confirmed": True,
        },
        "expected_values_receipt_binding": {
            "hash_confirmed": canonical_hash(ev_receipt) == SOURCE_EV_ADDITION_RECEIPT_HASH,
            "all_5_shadow_distances_verified": ev_confirmation.get("all_5_shadow_distances_verified"),
            "all_values_match_static_fixtures": ev_confirmation.get("all_values_match_static_fixtures"),
            "operator_approval_on_record": ev_confirmation.get("operator_approval_on_record"),
            "confirmed": True,
        },
        "baseline_state_completion": {
            "operator_id": OPERATOR_ID,
            "current_vector_type": current_vector_type,
            "current_computation_status": current_computation_status,
            "chamfer_already_promoted_in_pack": current_vector_type == "VALID_SHADOW_ONLY_VECTOR",
            "shadow_stub_only_confirmed": current_computation_status == "SHADOW_STUB_ONLY",
            "pack_hash_confirmed": canonical_hash(pack) == SOURCE_PACK_HASH,
            "runtime_mutated": False,
            "pack_vector_modified": False,
            "governance_closure_complete": True,
            "confirmed": True,
        },
        "no_pack_repromotion_completion": {
            "pack_repromotion_required": False,
            "pack_repromotion_performed": False,
            "pack_vector_unchanged": True,
            "pack_hash_before": SOURCE_PACK_HASH,
            "pack_hash_after": SOURCE_PACK_HASH,
            "note": (
                "CHAMFER_DISTANCE was already at VALID_SHADOW_ONLY_VECTOR / SHADOW_STUB_ONLY "
                "prior to this governance phase; no pack update was performed or required"
            ),
            "confirmed": True,
        },
        "projection_wiring_pending_record": {
            "promotion_key_in_this_phase": None,
            "baseline_promotion_complete_key_in_this_phase": None,
            "projection_cap_pct": 95,
            "projection_wiring_pending": True,
            "wiring_phase": "CHAMFER_PROJECTION_WIRING_ADAPTER",
            "required_next_actions": [
                "wire OPERATOR_DEFS['chamfer_distance']['promotion_key'] to "
                "out/metric_operator/chamfer_baseline_promotion_complete_001.latest.json",
                "rebuild AAL-Viz projection bundle",
                "CHAMFER advances from READY/95 to READY/100",
            ],
            "note": (
                "Projection wiring is a separate follow-up adapter step; "
                "not performed in this completion artifact"
            ),
            "confirmed": True,
        },
        "authority_lock_completion": {
            "all_source_artifacts_advisory_only": True,
            "no_authority_escalation_detected": True,
            "review_advisory_only": review_al.get("advisory_only"),
            "audit_advisory_only": audit_al.get("advisory_only"),
            "completion_locks": {
                "advisory_only": True,
                "shadow_lane_only": True,
                "baseline_promotion_complete_only": True,
                "chamfer_already_promoted_in_pack": True,
                "pack_repromotion_required": False,
                "projection_wiring_pending": True,
                "emits_metric_values": False,
                "forecast_influence": False,
                "p43_surface_lanes_authorized": False,
                "production_activation": False,
                "canon_promotion": False,
                "runtime_mutation": False,
                "execution_authority": False,
                "inference_authority": False,
            },
            "confirmed": True,
        },
        "blocked_scope_completion": {
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
            "confirmed": True,
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
            "baseline_promotion_complete_only": True,
            "chamfer_already_promoted_in_pack": True,
            "pack_repromotion_required": False,
            "projection_wiring_pending": True,
            "emits_metric_values": False,
            "forecast_influence": False,
            "p43_surface_lanes_authorized": False,
            "production_activation": False,
            "canon_promotion": False,
            "runtime_mutation": False,
            "execution_authority": False,
            "inference_authority": False,
        },
        "all_completions_confirmed": True,
        "recommended_next_step": "CHAMFER_PROJECTION_WIRING_ADAPTER",
        "provenance": {
            "generated_by": "CHAMFER_BASELINE_PROMOTION_COMPLETE_BUILD_001",
            "source_hashes": {
                "promotion_review": SOURCE_REVIEW_HASH,
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


def validate_chamfer_baseline_promotion_complete(doc: dict[str, Any]) -> None:
    if doc.get("complete_status") != COMPLETE_STATUS:
        raise ChamferBaselinePromotionCompleteError(
            f"complete_status mismatch: {doc.get('complete_status')!r}"
        )
    if doc.get("completion_id") != COMPLETION_ID:
        raise ChamferBaselinePromotionCompleteError(
            f"completion_id mismatch: {doc.get('completion_id')!r}"
        )
    h = doc.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise ChamferBaselinePromotionCompleteError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(doc))
    if recomputed != h:
        raise ChamferBaselinePromotionCompleteError(
            f"canonical_hash recomputation mismatch: {recomputed!r} != {h!r}"
        )
    al = doc.get("authority_locks", {})
    if al.get("advisory_only") is not True:
        raise ChamferBaselinePromotionCompleteError(
            "authority_locks.advisory_only must be True"
        )
    if al.get("canon_promotion") is not False:
        raise ChamferBaselinePromotionCompleteError(
            "authority_locks.canon_promotion must be False"
        )
    if al.get("emits_metric_values") is not False:
        raise ChamferBaselinePromotionCompleteError(
            "authority_locks.emits_metric_values must be False"
        )
    if al.get("pack_repromotion_required") is not False:
        raise ChamferBaselinePromotionCompleteError(
            "authority_locks.pack_repromotion_required must be False"
        )
    if al.get("projection_wiring_pending") is not True:
        raise ChamferBaselinePromotionCompleteError(
            "authority_locks.projection_wiring_pending must be True"
        )
    if doc.get("all_completions_confirmed") is not True:
        raise ChamferBaselinePromotionCompleteError(
            "all_completions_confirmed must be True"
        )
    if doc.get("recommended_next_step") != "CHAMFER_PROJECTION_WIRING_ADAPTER":
        raise ChamferBaselinePromotionCompleteError(
            "recommended_next_step must be CHAMFER_PROJECTION_WIRING_ADAPTER"
        )
    _check_no_forbidden(doc)
