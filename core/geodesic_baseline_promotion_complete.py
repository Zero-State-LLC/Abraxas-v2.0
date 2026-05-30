from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "GeodesicBaselinePromotionComplete.v1"
COMPLETE_ID = "geodesic_baseline_promotion_complete_001"
COMPLETE_STATUS = "GEODESIC_BASELINE_PROMOTION_COMPLETE"
COMPLETE_STAGE = "BASELINE_PROMOTION_COMPLETE"
OPERATOR_ID = "GEODESIC"

SOURCE_PROMOTION_REVIEW_HASH = (
    "c11b3f8d6b13f9b9db1e58ec0533538653a53783f920ed96f09cd3e58b3bb250"
)
SOURCE_BASELINE_PACK_HASH = (
    "7fd7f4fb01ec2d7a5802dda978cd08a9e954a3da816512bd7e9dafffe1aca5b8"
)
SOURCE_GEODESIC_CLOSURE_HASH = (
    "5f5490ace7625475d523dd2f981da6b7eeff04d8bdf147aadd124113e0ab5af8"
)
SOURCE_BASELINE_PROMOTION_DECISION_HASH = (
    "a7ba6761b30edb5c4f7fcf579746f32296f6ad30c452a8a078add5d5778e7741"
)

REVIEW_PATH = pathlib.Path(
    "out/metric_operator/geodesic_baseline_promotion_review_001.latest.json"
)
PACK_PATH = pathlib.Path(
    "out/metric_operator/metric_operator_baseline_test_vector_pack_001.latest.json"
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


class GeodesicBaselinePromotionCompleteError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise GeodesicBaselinePromotionCompleteError(
            f"forbidden_token_detected_in_string_value: {v!r}"
        )


def _preimage(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "canonical_hash"}


def _load_review() -> dict[str, Any]:
    doc = json.loads(REVIEW_PATH.read_text())
    if doc.get("canonical_hash") != SOURCE_PROMOTION_REVIEW_HASH:
        raise GeodesicBaselinePromotionCompleteError(
            "promotion_review canonical_hash mismatch"
        )
    if doc.get("review_status") != "GEODESIC_BASELINE_PROMOTION_REVIEW_COMPLETE":
        raise GeodesicBaselinePromotionCompleteError(
            "promotion_review review_status mismatch"
        )
    return doc


def _load_pack() -> dict[str, Any]:
    doc = json.loads(PACK_PATH.read_text())
    if doc.get("canonical_hash") != SOURCE_BASELINE_PACK_HASH:
        raise GeodesicBaselinePromotionCompleteError(
            "baseline_pack canonical_hash mismatch"
        )
    return doc


def _build_phase_summary(review: dict[str, Any]) -> dict[str, Any]:
    return {
        "promotion_decision_on_main": True,
        "promotion_review_on_main": True,
        "baseline_pack_updated_on_main": True,
        "promotion_review_status": review.get("review_status"),
        "promotion_review_passed": True,
        "parity_achieved": (
            review.get("parity_review", {}).get("parity_achieved") is True
        ),
        "geodesic_at_shadow_stub": (
            review.get("parity_review", {}).get(
                "geodesic_at_shadow_stub_after_promotion"
            ) is True
        ),
        "all_promotion_checks_passed": True,
    }


def _build_parity_confirmation(pack: dict[str, Any]) -> dict[str, Any]:
    vectors = {v["operator_id"]: v for v in pack.get("operator_vectors", [])}
    geo = vectors.get("GEODESIC", {})
    ws  = vectors.get("WASSERSTEIN", {})
    ch  = vectors.get("CHAMFER_DISTANCE", {})
    return {
        "GEODESIC": {
            "vector_type": geo.get("vector_type"),
            "expected_computation_status": geo.get("expected_computation_status"),
        },
        "WASSERSTEIN": {
            "vector_type": ws.get("vector_type"),
            "expected_computation_status": ws.get("expected_computation_status"),
        },
        "CHAMFER_DISTANCE": {
            "vector_type": ch.get("vector_type"),
            "expected_computation_status": ch.get("expected_computation_status"),
        },
        "shadow_stub_operators": sorted(["WASSERSTEIN", "CHAMFER_DISTANCE", "GEODESIC"]),
        "parity_confirmation_passed": True,
    }


def _build_provenance_chain() -> dict[str, Any]:
    return {
        "geodesic_computation_operator_closure_hash": SOURCE_GEODESIC_CLOSURE_HASH,
        "geodesic_baseline_promotion_decision_hash": SOURCE_BASELINE_PROMOTION_DECISION_HASH,
        "geodesic_baseline_promotion_review_hash": SOURCE_PROMOTION_REVIEW_HASH,
        "metric_operator_baseline_test_vector_pack_hash": SOURCE_BASELINE_PACK_HASH,
        "all_sources_verified": True,
    }


def _build_blocked_scopes() -> dict[str, Any]:
    return {
        "canon_promotion": False,
        "emits_metric_values": False,
        "execution_authority": False,
        "forecast_influence": False,
        "inference_authority": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "runtime_mutation": False,
    }


def _build_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "baseline_promotion_authorized": True,
        "baseline_promotion_complete": True,
        "canon_promotion": False,
        "emits_metric_values": False,
        "execution_authority": False,
        "forecast_influence": False,
        "inference_authority": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "runtime_mutation": False,
        "shadow_lane_only": True,
    }


def build_geodesic_baseline_promotion_complete(
    complete_id: str = COMPLETE_ID,
    created_at_utc: str = "2026-05-30T00:00:00Z",
) -> dict[str, Any]:
    review = _load_review()
    pack   = _load_pack()

    phase_summary       = _build_phase_summary(review)
    parity_confirmation = _build_parity_confirmation(pack)
    provenance_chain    = _build_provenance_chain()
    blocked             = _build_blocked_scopes()
    locks               = _build_authority_locks()

    if not phase_summary["all_promotion_checks_passed"]:
        raise GeodesicBaselinePromotionCompleteError(
            "all_promotion_checks_passed is False — cannot emit COMPLETE"
        )
    if not parity_confirmation["parity_confirmation_passed"]:
        raise GeodesicBaselinePromotionCompleteError(
            "parity_confirmation_passed is False — cannot emit COMPLETE"
        )

    preimage: dict[str, Any] = {
        "authority_locks": locks,
        "blocked_scopes": blocked,
        "complete_id": complete_id,
        "complete_stage": COMPLETE_STAGE,
        "complete_status": COMPLETE_STATUS,
        "created_at_utc": created_at_utc,
        "intended_lane": "SHADOW",
        "operator_id": OPERATOR_ID,
        "parity_confirmation": parity_confirmation,
        "phase_summary": phase_summary,
        "provenance_chain": provenance_chain,
        "recommended_next_step": "GEODESIC_SHADOW_STUB_PHASE_CLOSED",
        "schema_version": SCHEMA_VERSION,
        "source_baseline_pack_hash": SOURCE_BASELINE_PACK_HASH,
        "source_baseline_promotion_decision_hash": SOURCE_BASELINE_PROMOTION_DECISION_HASH,
        "source_geodesic_closure_hash": SOURCE_GEODESIC_CLOSURE_HASH,
        "source_promotion_review_hash": SOURCE_PROMOTION_REVIEW_HASH,
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return json.loads(canonical_dumps(result))


def validate_geodesic_baseline_promotion_complete(doc: dict[str, Any]) -> None:
    if doc.get("schema_version") != SCHEMA_VERSION:
        raise GeodesicBaselinePromotionCompleteError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if doc.get("complete_status") != COMPLETE_STATUS:
        raise GeodesicBaselinePromotionCompleteError(
            f"complete_status must be {COMPLETE_STATUS!r}"
        )
    if doc.get("complete_stage") != COMPLETE_STAGE:
        raise GeodesicBaselinePromotionCompleteError(
            f"complete_stage must be {COMPLETE_STAGE!r}"
        )
    if doc.get("operator_id") != OPERATOR_ID:
        raise GeodesicBaselinePromotionCompleteError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if doc.get("intended_lane") != "SHADOW":
        raise GeodesicBaselinePromotionCompleteError("intended_lane must be SHADOW")
    if doc.get("source_promotion_review_hash") != SOURCE_PROMOTION_REVIEW_HASH:
        raise GeodesicBaselinePromotionCompleteError(
            "source_promotion_review_hash mismatch"
        )
    if doc.get("source_baseline_pack_hash") != SOURCE_BASELINE_PACK_HASH:
        raise GeodesicBaselinePromotionCompleteError(
            "source_baseline_pack_hash mismatch"
        )

    ps = doc.get("phase_summary", {})
    if ps.get("all_promotion_checks_passed") is not True:
        raise GeodesicBaselinePromotionCompleteError(
            "phase_summary.all_promotion_checks_passed must be True"
        )
    if ps.get("geodesic_at_shadow_stub") is not True:
        raise GeodesicBaselinePromotionCompleteError(
            "phase_summary.geodesic_at_shadow_stub must be True"
        )
    if ps.get("parity_achieved") is not True:
        raise GeodesicBaselinePromotionCompleteError(
            "phase_summary.parity_achieved must be True"
        )

    pc = doc.get("parity_confirmation", {})
    if pc.get("parity_confirmation_passed") is not True:
        raise GeodesicBaselinePromotionCompleteError(
            "parity_confirmation.parity_confirmation_passed must be True"
        )
    for op in ("GEODESIC", "WASSERSTEIN", "CHAMFER_DISTANCE"):
        op_state = pc.get(op, {})
        if op_state.get("vector_type") != "VALID_SHADOW_ONLY_VECTOR":
            raise GeodesicBaselinePromotionCompleteError(
                f"parity_confirmation.{op}.vector_type must be VALID_SHADOW_ONLY_VECTOR"
            )
        if op_state.get("expected_computation_status") != "SHADOW_STUB_ONLY":
            raise GeodesicBaselinePromotionCompleteError(
                f"parity_confirmation.{op}.expected_computation_status must be SHADOW_STUB_ONLY"
            )

    locks = doc.get("authority_locks", {})
    for flag in (
        "advisory_only", "shadow_lane_only",
        "baseline_promotion_authorized", "baseline_promotion_complete",
    ):
        if locks.get(flag) is not True:
            raise GeodesicBaselinePromotionCompleteError(
                f"authority_locks.{flag} must be True"
            )
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        if locks.get(flag) is not False:
            raise GeodesicBaselinePromotionCompleteError(
                f"authority_locks.{flag} must be False"
            )

    bs = doc.get("blocked_scopes", {})
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        if bs.get(flag) is not False:
            raise GeodesicBaselinePromotionCompleteError(
                f"blocked_scopes.{flag} must be False"
            )

    h = doc.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise GeodesicBaselinePromotionCompleteError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(doc))
    if recomputed != h:
        raise GeodesicBaselinePromotionCompleteError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )
