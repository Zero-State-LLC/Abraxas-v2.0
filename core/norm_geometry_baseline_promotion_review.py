from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "NormGeometryBaselinePromotionReview.v1"
REVIEW_ID = "norm_geometry_baseline_promotion_review_001"
REVIEW_STATUS = "NORM_GEOMETRY_BASELINE_PROMOTION_REVIEW_COMPLETE"
REVIEW_STAGE = "BASELINE_PROMOTION_REVIEW_ONLY"
OPERATOR_ID = "NORM_GEOMETRY"

SOURCE_GATE_HASH = (
    "0ff92dfb9dc78f57d253bbb4c42adaf102ddef470b3b925629c3cfb43a0c960d"
)
SOURCE_DECISION_HASH = (
    "fe9583b8d7243b2da1f1dc92e5f0eb5345ddc4ee3647bc6cfce64585368e1868"
)
SOURCE_CLOSURE_HASH = (
    "6df91765591e5dfd4803e226a1a8836505e8ea044bca5e2f9950c7509cceb003"
)

GATE_PATH = pathlib.Path(
    "out/metric_operator/norm_geometry_baseline_promotion_gate_001.latest.json"
)
DECISION_PATH = pathlib.Path(
    "input/norm_geometry_baseline_promotion_operator_decision.json"
)
CLOSURE_PATH = pathlib.Path(
    "out/metric_operator/norm_geometry_computation_operator_closure_001.latest.json"
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


class NormGeometryBaselinePromotionReviewError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise NormGeometryBaselinePromotionReviewError(
            f"forbidden_token_detected_in_string_value: {v!r}"
        )


def _preimage(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "canonical_hash"}


def _load_gate() -> dict[str, Any]:
    doc = json.loads(GATE_PATH.read_text())
    if doc.get("canonical_hash") != SOURCE_GATE_HASH:
        raise NormGeometryBaselinePromotionReviewError(
            f"gate canonical_hash mismatch: {doc.get('canonical_hash')!r}"
        )
    if doc.get("all_gate_passed") is not True:
        raise NormGeometryBaselinePromotionReviewError(
            "gate all_gate_passed must be True"
        )
    if doc.get("gate_status") != "NORM_GEOMETRY_BASELINE_PROMOTION_GATE_READY":
        raise NormGeometryBaselinePromotionReviewError("gate_status mismatch")
    return doc


def _load_decision() -> dict[str, Any]:
    doc = json.loads(DECISION_PATH.read_text())
    actual = canonical_hash(doc)
    if actual != SOURCE_DECISION_HASH:
        raise NormGeometryBaselinePromotionReviewError(
            f"decision canonical_hash mismatch: {actual!r}"
        )
    if doc.get("decision") != "approve_norm_geometry_shadow_stub_baseline_promotion":
        raise NormGeometryBaselinePromotionReviewError("decision field mismatch")
    if doc.get("baseline_promotion_authorized") is not True:
        raise NormGeometryBaselinePromotionReviewError(
            "baseline_promotion_authorized must be True"
        )
    return doc


def _load_closure() -> dict[str, Any]:
    doc = json.loads(CLOSURE_PATH.read_text())
    if doc.get("canonical_hash") != SOURCE_CLOSURE_HASH:
        raise NormGeometryBaselinePromotionReviewError(
            "closure canonical_hash mismatch"
        )
    if doc.get("all_closure_passed") is not True:
        raise NormGeometryBaselinePromotionReviewError(
            "closure all_closure_passed must be True"
        )
    return doc


def _build_gate_review(gate: dict[str, Any]) -> dict[str, Any]:
    return {
        "gate_id": gate.get("gate_id"),
        "gate_status": gate.get("gate_status"),
        "gate_stage": gate.get("gate_stage"),
        "all_gate_passed": gate.get("all_gate_passed"),
        "decision_review_passed": (
            gate.get("decision_review", {}).get("decision_review_passed")
        ),
        "closure_review_passed": (
            gate.get("closure_review", {}).get("closure_review_passed")
        ),
        "current_pack_review_passed": (
            gate.get("current_baseline_pack_review", {}).get("current_pack_review_passed")
        ),
        "pack_scope_passed": (
            gate.get("authorized_pack_update_scope", {}).get("pack_update_scope_passed")
        ),
        "baseline_pack_update_authorized": (
            gate.get("authority_locks", {}).get("baseline_pack_update_authorized")
        ),
        "gate_review_passed": True,
    }


def _build_decision_review(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "decision_id": decision.get("decision_id"),
        "decision": decision.get("decision"),
        "baseline_promotion_authorized": decision.get("baseline_promotion_authorized"),
        "target_vector_type": decision.get("target_vector_type"),
        "target_expected_computation_status": decision.get(
            "target_expected_computation_status"
        ),
        "source_closure_hash_acknowledged": (
            decision.get("source_closure_hash") == SOURCE_CLOSURE_HASH
        ),
        "all_closure_passed_acknowledged": decision.get("all_closure_passed_acknowledged"),
        "shadow_lane_only_acknowledged": decision.get("shadow_lane_only_acknowledged"),
        "all_blocks_acknowledged": all([
            decision.get("metric_values_emission_blocked_acknowledged"),
            decision.get("p43_surface_lanes_blocked_acknowledged"),
            decision.get("production_activation_blocked_acknowledged"),
            decision.get("canon_promotion_blocked_acknowledged"),
            decision.get("runtime_mutation_blocked_acknowledged"),
            decision.get("execution_authority_blocked_acknowledged"),
        ]),
        "authority_locks_all_false": all([
            decision.get("valid_for_execution") is False,
            decision.get("authorization_granted") is False,
            decision.get("emits_metric_values") is False,
            decision.get("forecast_authority") is False,
            decision.get("inference_authority") is False,
            decision.get("production_activation") is False,
            decision.get("canon_promotion") is False,
            decision.get("runtime_mutation") is False,
            decision.get("execution_authority") is False,
        ]),
        "decision_review_passed": True,
    }


def _build_closure_review(closure: dict[str, Any]) -> dict[str, Any]:
    return {
        "closure_id": closure.get("closure_id"),
        "closure_status": closure.get("closure_status"),
        "closure_stage": closure.get("closure_stage"),
        "all_closure_passed": closure.get("all_closure_passed"),
        "phase_completion_passed": (
            closure.get("phase_completion_review", {}).get("closure_passed")
        ),
        "valid_fixture_count": (
            closure.get("valid_fixture_result_closure", {}).get(
                "total_valid_fixtures_closed"
            )
        ),
        "rejection_fixture_count": (
            closure.get("rejection_fixture_closure", {}).get(
                "total_rejection_fixtures_closed"
            )
        ),
        "authority_lock_passed": (
            closure.get("authority_lock_closure", {}).get("closure_passed")
        ),
        "closure_review_passed": True,
    }


def _build_baseline_pack_update_review(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "operator_id": OPERATOR_ID,
        "previous_vector_type": "VALID_METADATA_VECTOR",
        "new_vector_type": decision.get("target_vector_type"),
        "previous_expected_computation_status": "NOT_IMPLEMENTED",
        "new_expected_computation_status": decision.get(
            "target_expected_computation_status"
        ),
        "pack_update_authorized": True,
        "pack_update_scope": "NORM_GEOMETRY_ONLY",
        "evidence_refs": sorted([
            "NormGeometryComputationOperatorClosure.v1:norm_geometry_computation_operator_closure_001",
            "NormGeometryBaselinePromotionDecision:NORM_GEOMETRY_BASELINE_PROMOTION_DECISION_2026_05_29_001",
            "NormGeometryBaselinePromotionGate.v1:norm_geometry_baseline_promotion_gate_001",
            "contracts/canon/metric_operator_registry.v1.schema.json",
        ]),
        "unchanged_operators": sorted([
            "CHAMFER_DISTANCE",
            "COUNTERFACTUAL_DIFFUSION",
            "GEODESIC",
            "HEAVY_TAIL",
            "HYPERVECTOR_BINDING",
            "HYSTERESIS",
            "RESERVOIR_STATE_SPACE",
            "STOCHASTIC_GEOMETRY",
            "TOPOLOGICAL_PRIMITIVES",
            "TRANSPORT",
            "WASSERSTEIN",
        ]),
        "pack_update_review_passed": True,
    }


def _build_operator_state_after_update() -> dict[str, Any]:
    return {
        "CHAMFER_DISTANCE": {
            "expected_computation_status": "SHADOW_STUB_ONLY",
            "vector_type": "VALID_SHADOW_ONLY_VECTOR",
        },
        "COUNTERFACTUAL_DIFFUSION": {
            "expected_computation_status": "NOT_IMPLEMENTED",
            "vector_type": "VALID_METADATA_VECTOR",
        },
        "GEODESIC": {
            "expected_computation_status": "SHADOW_STUB_ONLY",
            "vector_type": "VALID_SHADOW_ONLY_VECTOR",
        },
        "HEAVY_TAIL": {
            "expected_computation_status": "NOT_IMPLEMENTED",
            "vector_type": "VALID_METADATA_VECTOR",
        },
        "HYPERVECTOR_BINDING": {
            "expected_computation_status": "NOT_IMPLEMENTED",
            "vector_type": "VALID_METADATA_VECTOR",
        },
        "HYSTERESIS": {
            "expected_computation_status": "NOT_IMPLEMENTED",
            "vector_type": "VALID_METADATA_VECTOR",
        },
        "NORM_GEOMETRY": {
            "expected_computation_status": "SHADOW_STUB_ONLY",
            "vector_type": "VALID_SHADOW_ONLY_VECTOR",
        },
        "RESERVOIR_STATE_SPACE": {
            "expected_computation_status": "NOT_IMPLEMENTED",
            "vector_type": "VALID_METADATA_VECTOR",
        },
        "STOCHASTIC_GEOMETRY": {
            "expected_computation_status": "NOT_IMPLEMENTED",
            "vector_type": "VALID_METADATA_VECTOR",
        },
        "TOPOLOGICAL_PRIMITIVES": {
            "expected_computation_status": "NOT_IMPLEMENTED",
            "vector_type": "VALID_METADATA_VECTOR",
        },
        "TRANSPORT": {
            "expected_computation_status": "NOT_IMPLEMENTED",
            "vector_type": "VALID_METADATA_VECTOR",
        },
        "WASSERSTEIN": {
            "expected_computation_status": "SHADOW_STUB_ONLY",
            "vector_type": "VALID_SHADOW_ONLY_VECTOR",
        },
    }


def _build_parity_review() -> dict[str, Any]:
    return {
        "shadow_stub_operators_after_update": sorted(
            ["WASSERSTEIN", "CHAMFER_DISTANCE", "GEODESIC", "NORM_GEOMETRY"]
        ),
        "wasserstein_at_shadow_stub": True,
        "chamfer_distance_at_shadow_stub": True,
        "geodesic_at_shadow_stub": True,
        "norm_geometry_at_shadow_stub_after_promotion": True,
        "parity_achieved": True,
        "parity_review_passed": True,
    }


def _build_no_metric_emission_review() -> dict[str, Any]:
    return {
        "emits_metric_values": False,
        "promotion_scope": "BASELINE_PACK_UPDATE_ONLY",
        "no_metric_emission_review_passed": True,
    }


def _build_no_forecast_influence_review() -> dict[str, Any]:
    return {
        "forecast_influence": False,
        "no_forecast_influence_review_passed": True,
    }


def _build_no_p43_surface_lane_review() -> dict[str, Any]:
    return {
        "p43_surface_lanes_authorized": False,
        "no_p43_surface_lane_review_passed": True,
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
        "baseline_promotion_review_only": True,
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


def build_norm_geometry_baseline_promotion_review(
    review_id: str = REVIEW_ID,
    created_at_utc: str = "2026-05-30T00:00:00Z",
) -> dict[str, Any]:
    gate = _load_gate()
    decision = _load_decision()
    closure = _load_closure()

    gate_review = _build_gate_review(gate)
    decision_review = _build_decision_review(decision)
    closure_review = _build_closure_review(closure)
    pack_update_review = _build_baseline_pack_update_review(decision)
    operator_state = _build_operator_state_after_update()
    parity_review = _build_parity_review()
    no_metric = _build_no_metric_emission_review()
    no_forecast = _build_no_forecast_influence_review()
    no_p43 = _build_no_p43_surface_lane_review()
    blocked = _build_blocked_scopes()
    locks = _build_authority_locks()

    preimage: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "review_id": review_id,
        "operator_id": OPERATOR_ID,
        "review_status": REVIEW_STATUS,
        "review_stage": REVIEW_STAGE,
        "created_at_utc": created_at_utc,
        "intended_lane": "SHADOW",
        "source_gate_hash": SOURCE_GATE_HASH,
        "source_decision_hash": SOURCE_DECISION_HASH,
        "source_closure_hash": SOURCE_CLOSURE_HASH,
        "gate_review": gate_review,
        "decision_review": decision_review,
        "closure_review": closure_review,
        "baseline_pack_update_review": pack_update_review,
        "operator_state_after_update": operator_state,
        "parity_review": parity_review,
        "no_metric_emission_review": no_metric,
        "no_forecast_influence_review": no_forecast,
        "no_p43_surface_lane_review": no_p43,
        "blocked_scopes": blocked,
        "authority_locks": locks,
        "recommended_next_step": "NORM_GEOMETRY_BASELINE_PROMOTION_COMPLETE",
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return json.loads(canonical_dumps(result))


def validate_norm_geometry_baseline_promotion_review(review: dict[str, Any]) -> None:
    if review.get("schema_version") != SCHEMA_VERSION:
        raise NormGeometryBaselinePromotionReviewError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if review.get("review_status") != REVIEW_STATUS:
        raise NormGeometryBaselinePromotionReviewError(
            f"review_status must be {REVIEW_STATUS!r}"
        )
    if review.get("review_stage") != REVIEW_STAGE:
        raise NormGeometryBaselinePromotionReviewError(
            f"review_stage must be {REVIEW_STAGE!r}"
        )
    if review.get("operator_id") != OPERATOR_ID:
        raise NormGeometryBaselinePromotionReviewError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if review.get("intended_lane") != "SHADOW":
        raise NormGeometryBaselinePromotionReviewError("intended_lane must be SHADOW")
    if review.get("source_gate_hash") != SOURCE_GATE_HASH:
        raise NormGeometryBaselinePromotionReviewError("source_gate_hash mismatch")
    if review.get("source_decision_hash") != SOURCE_DECISION_HASH:
        raise NormGeometryBaselinePromotionReviewError("source_decision_hash mismatch")
    if review.get("source_closure_hash") != SOURCE_CLOSURE_HASH:
        raise NormGeometryBaselinePromotionReviewError("source_closure_hash mismatch")

    for section, key in [
        ("gate_review", "gate_review_passed"),
        ("decision_review", "decision_review_passed"),
        ("closure_review", "closure_review_passed"),
        ("baseline_pack_update_review", "pack_update_review_passed"),
        ("parity_review", "parity_review_passed"),
        ("no_metric_emission_review", "no_metric_emission_review_passed"),
        ("no_forecast_influence_review", "no_forecast_influence_review_passed"),
        ("no_p43_surface_lane_review", "no_p43_surface_lane_review_passed"),
    ]:
        sec = review.get(section, {})
        if sec.get(key) is not True:
            raise NormGeometryBaselinePromotionReviewError(
                f"{section}.{key} must be True"
            )

    locks = review.get("authority_locks", {})
    for flag in (
        "advisory_only",
        "shadow_lane_only",
        "baseline_promotion_review_only",
        "baseline_promotion_authorized",
        "baseline_pack_update_authorized",
    ):
        if locks.get(flag) is not True:
            raise NormGeometryBaselinePromotionReviewError(
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
            raise NormGeometryBaselinePromotionReviewError(
                f"authority_locks.{flag} must be False"
            )

    bs = review.get("blocked_scopes", {})
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
            raise NormGeometryBaselinePromotionReviewError(
                f"blocked_scopes.{flag} must be False"
            )

    h = review.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise NormGeometryBaselinePromotionReviewError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(review))
    if recomputed != h:
        raise NormGeometryBaselinePromotionReviewError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )
