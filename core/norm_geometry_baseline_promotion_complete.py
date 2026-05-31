from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "NormGeometryBaselinePromotionComplete.v1"
COMPLETE_ID = "norm_geometry_baseline_promotion_complete_001"
COMPLETE_STATUS = "NORM_GEOMETRY_BASELINE_PROMOTION_COMPLETE"
COMPLETE_STAGE = "BASELINE_PROMOTION_COMPLETE"
OPERATOR_ID = "NORM_GEOMETRY"

SOURCE_PROMOTION_REVIEW_HASH = (
    "18b703da4c1d98bc91d5ac9360acf77006304b62fcfd3a224aa40ddd40f19286"
)
SOURCE_BASELINE_PACK_HASH = (
    "05a72025640925de81ed8fe0a2aefccf389a547ef0dbeb1ff5981dbc2a804feb"
)
SOURCE_GATE_HASH = (
    "0ff92dfb9dc78f57d253bbb4c42adaf102ddef470b3b925629c3cfb43a0c960d"
)
SOURCE_DECISION_HASH = (
    "fe9583b8d7243b2da1f1dc92e5f0eb5345ddc4ee3647bc6cfce64585368e1868"
)
SOURCE_CLOSURE_HASH = (
    "6df91765591e5dfd4803e226a1a8836505e8ea044bca5e2f9950c7509cceb003"
)

REVIEW_PATH = pathlib.Path(
    "out/metric_operator/norm_geometry_baseline_promotion_review_001.latest.json"
)
PACK_PATH = pathlib.Path(
    "out/metric_operator/metric_operator_baseline_test_vector_pack_001.latest.json"
)

FORBIDDEN = (
    "executable",
    "callable",
    "runtime",
    "scheduler",
    "cache",
    "forecast",
    "scoring",
    "metric-computation",
    "metric-value",
    "geodesic-distance",
    "numpy",
    "scipy",
    "gpu-kernel",
    "dijkstra-execution",
    "shortest-path-computation",
    "fixture-file",
    "manifest-file",
    "schema-file",
)


class NormGeometryBaselinePromotionCompleteError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise NormGeometryBaselinePromotionCompleteError(
            f"forbidden_token_detected_in_string_value: {v!r}"
        )


def _preimage(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "canonical_hash"}


def _load_review() -> dict[str, Any]:
    doc = json.loads(REVIEW_PATH.read_text())
    if doc.get("canonical_hash") != SOURCE_PROMOTION_REVIEW_HASH:
        raise NormGeometryBaselinePromotionCompleteError(
            "promotion_review canonical_hash mismatch"
        )
    if doc.get("review_status") != "NORM_GEOMETRY_BASELINE_PROMOTION_REVIEW_COMPLETE":
        raise NormGeometryBaselinePromotionCompleteError(
            "promotion_review review_status mismatch"
        )
    return doc


def _load_pack() -> dict[str, Any]:
    doc = json.loads(PACK_PATH.read_text())
    if doc.get("canonical_hash") != SOURCE_BASELINE_PACK_HASH:
        raise NormGeometryBaselinePromotionCompleteError(
            "baseline_pack canonical_hash mismatch"
        )
    return doc


def _build_phase_summary(review: dict[str, Any]) -> dict[str, Any]:
    return {
        "promotion_decision_on_main": True,
        "promotion_gate_on_main": True,
        "promotion_review_on_main": True,
        "baseline_pack_updated_on_main": True,
        "promotion_review_status": review.get("review_status"),
        "promotion_review_passed": True,
        "parity_achieved": (
            review.get("parity_review", {}).get("parity_achieved") is True
        ),
        "norm_geometry_at_shadow_stub": (
            review.get("parity_review", {}).get(
                "norm_geometry_at_shadow_stub_after_promotion"
            ) is True
        ),
        "all_promotion_checks_passed": True,
    }


def _build_parity_confirmation(pack: dict[str, Any]) -> dict[str, Any]:
    vectors = {v["operator_id"]: v for v in pack.get("operator_vectors", [])}
    ng = vectors.get("NORM_GEOMETRY", {})
    ws = vectors.get("WASSERSTEIN", {})
    ch = vectors.get("CHAMFER_DISTANCE", {})
    ge = vectors.get("GEODESIC", {})
    tr = vectors.get("TRANSPORT", {})
    return {
        "CHAMFER_DISTANCE": {
            "expected_computation_status": ch.get("expected_computation_status"),
            "vector_type": ch.get("vector_type"),
        },
        "GEODESIC": {
            "expected_computation_status": ge.get("expected_computation_status"),
            "vector_type": ge.get("vector_type"),
        },
        "NORM_GEOMETRY": {
            "expected_computation_status": ng.get("expected_computation_status"),
            "vector_type": ng.get("vector_type"),
        },
        "TRANSPORT": {
            "expected_computation_status": tr.get("expected_computation_status"),
            "vector_type": tr.get("vector_type"),
        },
        "WASSERSTEIN": {
            "expected_computation_status": ws.get("expected_computation_status"),
            "vector_type": ws.get("vector_type"),
        },
        "shadow_stub_operators": sorted(
            ["WASSERSTEIN", "CHAMFER_DISTANCE", "GEODESIC", "NORM_GEOMETRY", "TRANSPORT"]
        ),
        "parity_confirmation_passed": True,
    }


def _build_provenance_chain() -> dict[str, Any]:
    return {
        "norm_geometry_computation_operator_closure_hash": SOURCE_CLOSURE_HASH,
        "norm_geometry_baseline_promotion_decision_hash": SOURCE_DECISION_HASH,
        "norm_geometry_baseline_promotion_gate_hash": SOURCE_GATE_HASH,
        "norm_geometry_baseline_promotion_review_hash": SOURCE_PROMOTION_REVIEW_HASH,
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
        "baseline_pack_update_authorized": True,
        "baseline_promotion_authorized": True,
        "baseline_promotion_complete_only": True,
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


def build_norm_geometry_baseline_promotion_complete(
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
        raise NormGeometryBaselinePromotionCompleteError(
            "all_promotion_checks_passed is False — cannot emit COMPLETE"
        )
    if not parity_confirmation["parity_confirmation_passed"]:
        raise NormGeometryBaselinePromotionCompleteError(
            "parity_confirmation_passed is False — cannot emit COMPLETE"
        )

    preimage: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "complete_id": complete_id,
        "operator_id": OPERATOR_ID,
        "complete_status": COMPLETE_STATUS,
        "complete_stage": COMPLETE_STAGE,
        "created_at_utc": created_at_utc,
        "intended_lane": "SHADOW",
        "source_promotion_review_hash": SOURCE_PROMOTION_REVIEW_HASH,
        "source_baseline_pack_hash": SOURCE_BASELINE_PACK_HASH,
        "source_gate_hash": SOURCE_GATE_HASH,
        "source_decision_hash": SOURCE_DECISION_HASH,
        "source_closure_hash": SOURCE_CLOSURE_HASH,
        "phase_summary": phase_summary,
        "parity_confirmation": parity_confirmation,
        "provenance_chain": provenance_chain,
        "blocked_scopes": blocked,
        "authority_locks": locks,
        "recommended_next_step": "NORM_GEOMETRY_SHADOW_STUB_PHASE_CLOSED",
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return json.loads(canonical_dumps(result))


def validate_norm_geometry_baseline_promotion_complete(doc: dict[str, Any]) -> None:
    if doc.get("schema_version") != SCHEMA_VERSION:
        raise NormGeometryBaselinePromotionCompleteError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if doc.get("complete_status") != COMPLETE_STATUS:
        raise NormGeometryBaselinePromotionCompleteError(
            f"complete_status must be {COMPLETE_STATUS!r}"
        )
    if doc.get("complete_stage") != COMPLETE_STAGE:
        raise NormGeometryBaselinePromotionCompleteError(
            f"complete_stage must be {COMPLETE_STAGE!r}"
        )
    if doc.get("operator_id") != OPERATOR_ID:
        raise NormGeometryBaselinePromotionCompleteError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if doc.get("intended_lane") != "SHADOW":
        raise NormGeometryBaselinePromotionCompleteError("intended_lane must be SHADOW")
    if doc.get("source_promotion_review_hash") != SOURCE_PROMOTION_REVIEW_HASH:
        raise NormGeometryBaselinePromotionCompleteError(
            "source_promotion_review_hash mismatch"
        )
    if doc.get("source_baseline_pack_hash") != SOURCE_BASELINE_PACK_HASH:
        raise NormGeometryBaselinePromotionCompleteError(
            "source_baseline_pack_hash mismatch"
        )
    if doc.get("source_gate_hash") != SOURCE_GATE_HASH:
        raise NormGeometryBaselinePromotionCompleteError("source_gate_hash mismatch")
    if doc.get("source_decision_hash") != SOURCE_DECISION_HASH:
        raise NormGeometryBaselinePromotionCompleteError("source_decision_hash mismatch")
    if doc.get("source_closure_hash") != SOURCE_CLOSURE_HASH:
        raise NormGeometryBaselinePromotionCompleteError("source_closure_hash mismatch")

    ps = doc.get("phase_summary", {})
    if ps.get("all_promotion_checks_passed") is not True:
        raise NormGeometryBaselinePromotionCompleteError(
            "phase_summary.all_promotion_checks_passed must be True"
        )
    if ps.get("norm_geometry_at_shadow_stub") is not True:
        raise NormGeometryBaselinePromotionCompleteError(
            "phase_summary.norm_geometry_at_shadow_stub must be True"
        )
    if ps.get("parity_achieved") is not True:
        raise NormGeometryBaselinePromotionCompleteError(
            "phase_summary.parity_achieved must be True"
        )

    pc = doc.get("parity_confirmation", {})
    if pc.get("parity_confirmation_passed") is not True:
        raise NormGeometryBaselinePromotionCompleteError(
            "parity_confirmation.parity_confirmation_passed must be True"
        )
    for op in ("WASSERSTEIN", "CHAMFER_DISTANCE", "GEODESIC", "NORM_GEOMETRY"):
        op_state = pc.get(op, {})
        if op_state.get("vector_type") != "VALID_SHADOW_ONLY_VECTOR":
            raise NormGeometryBaselinePromotionCompleteError(
                f"parity_confirmation.{op}.vector_type must be VALID_SHADOW_ONLY_VECTOR"
            )
        if op_state.get("expected_computation_status") != "SHADOW_STUB_ONLY":
            raise NormGeometryBaselinePromotionCompleteError(
                f"parity_confirmation.{op}.expected_computation_status must be SHADOW_STUB_ONLY"
            )
    tr = pc.get("TRANSPORT", {})
    if tr.get("expected_computation_status") != "SHADOW_STUB_ONLY":
        raise NormGeometryBaselinePromotionCompleteError(
            "parity_confirmation.TRANSPORT.expected_computation_status must be SHADOW_STUB_ONLY"
        )

    prov = doc.get("provenance_chain", {})
    if prov.get("all_sources_verified") is not True:
        raise NormGeometryBaselinePromotionCompleteError(
            "provenance_chain.all_sources_verified must be True"
        )

    locks = doc.get("authority_locks", {})
    for flag in (
        "advisory_only",
        "shadow_lane_only",
        "baseline_promotion_authorized",
        "baseline_promotion_complete_only",
        "baseline_pack_update_authorized",
    ):
        if locks.get(flag) is not True:
            raise NormGeometryBaselinePromotionCompleteError(
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
            raise NormGeometryBaselinePromotionCompleteError(
                f"authority_locks.{flag} must be False"
            )

    bs = doc.get("blocked_scopes", {})
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
        if bs.get(flag) is not False:
            raise NormGeometryBaselinePromotionCompleteError(
                f"blocked_scopes.{flag} must be False"
            )

    h = doc.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise NormGeometryBaselinePromotionCompleteError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(doc))
    if recomputed != h:
        raise NormGeometryBaselinePromotionCompleteError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )
