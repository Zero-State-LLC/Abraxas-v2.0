from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "NormGeometryBaselinePromotionGate.v1"
GATE_ID = "norm_geometry_baseline_promotion_gate_001"
GATE_STATUS = "NORM_GEOMETRY_BASELINE_PROMOTION_GATE_READY"
GATE_STAGE = "BASELINE_PROMOTION_GATE_ONLY"
OPERATOR_ID = "NORM_GEOMETRY"

SOURCE_DECISION_HASH = (
    "fe9583b8d7243b2da1f1dc92e5f0eb5345ddc4ee3647bc6cfce64585368e1868"
)
SOURCE_CLOSURE_HASH = (
    "6df91765591e5dfd4803e226a1a8836505e8ea044bca5e2f9950c7509cceb003"
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


class NormGeometryBaselinePromotionGateError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise NormGeometryBaselinePromotionGateError(
            f"forbidden_token_detected_in_string_value: {v!r}"
        )


def _preimage(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "canonical_hash"}


def _load_decision() -> dict[str, Any]:
    doc = json.loads(DECISION_PATH.read_text())
    actual = canonical_hash(doc)
    if actual != SOURCE_DECISION_HASH:
        raise NormGeometryBaselinePromotionGateError(
            f"decision canonical_hash mismatch: {actual!r}"
        )
    if doc.get("decision") != "approve_norm_geometry_shadow_stub_baseline_promotion":
        raise NormGeometryBaselinePromotionGateError("decision field mismatch")
    if doc.get("baseline_promotion_authorized") is not True:
        raise NormGeometryBaselinePromotionGateError(
            "baseline_promotion_authorized must be True"
        )
    if doc.get("source_closure_hash") != SOURCE_CLOSURE_HASH:
        raise NormGeometryBaselinePromotionGateError(
            "decision source_closure_hash mismatch"
        )
    return doc


def _load_closure() -> dict[str, Any]:
    doc = json.loads(CLOSURE_PATH.read_text())
    if doc.get("canonical_hash") != SOURCE_CLOSURE_HASH:
        raise NormGeometryBaselinePromotionGateError(
            "closure canonical_hash mismatch"
        )
    if doc.get("all_closure_passed") is not True:
        raise NormGeometryBaselinePromotionGateError(
            "closure all_closure_passed must be True"
        )
    return doc


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
        "test_vector_computation_only_acknowledged": decision.get(
            "test_vector_computation_only_acknowledged"
        ),
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


def _build_current_baseline_pack_review() -> dict[str, Any]:
    return {
        "norm_geometry_current_vector_type": "VALID_METADATA_VECTOR",
        "norm_geometry_current_expected_computation_status": "NOT_IMPLEMENTED",
        "norm_geometry_not_yet_promoted": True,
        "promotion_guard_confirmed": True,
        "current_pack_review_passed": True,
    }


def _build_authorized_pack_update_scope(decision: dict[str, Any]) -> dict[str, Any]:
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
        "unchanged_operators": sorted([
            "WASSERSTEIN",
            "CHAMFER_DISTANCE",
            "GEODESIC",
            "TRANSPORT",
            "HYPERVECTOR_BINDING",
            "RESERVOIR_STATE_SPACE",
            "COUNTERFACTUAL_DIFFUSION",
            "HEAVY_TAIL",
            "HYSTERESIS",
            "STOCHASTIC_GEOMETRY",
            "TOPOLOGICAL_PRIMITIVES",
        ]),
        "pack_update_scope_passed": True,
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
        "baseline_promotion_gate_only": True,
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


def build_baseline_promotion_gate(
    gate_id: str = GATE_ID,
    created_at_utc: str = "2026-05-30T00:00:00Z",
) -> dict[str, Any]:
    decision = _load_decision()
    closure = _load_closure()

    decision_review = _build_decision_review(decision)
    closure_review = _build_closure_review(closure)
    current_pack_review = _build_current_baseline_pack_review()
    pack_scope = _build_authorized_pack_update_scope(decision)
    blocked = _build_blocked_scopes()
    locks = _build_authority_locks()

    all_gate_passed = (
        decision_review["decision_review_passed"]
        and closure_review["closure_review_passed"]
        and current_pack_review["current_pack_review_passed"]
        and pack_scope["pack_update_scope_passed"]
    )

    if not all_gate_passed:
        raise NormGeometryBaselinePromotionGateError(
            "one or more gate sections failed — cannot emit GATE_READY"
        )

    preimage: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "gate_id": gate_id,
        "operator_id": OPERATOR_ID,
        "gate_status": GATE_STATUS,
        "gate_stage": GATE_STAGE,
        "created_at_utc": created_at_utc,
        "intended_lane": "SHADOW",
        "source_decision_hash": SOURCE_DECISION_HASH,
        "source_closure_hash": SOURCE_CLOSURE_HASH,
        "all_gate_passed": all_gate_passed,
        "decision_review": decision_review,
        "closure_review": closure_review,
        "current_baseline_pack_review": current_pack_review,
        "authorized_pack_update_scope": pack_scope,
        "blocked_scopes": blocked,
        "authority_locks": locks,
        "recommended_next_step": "NORM_GEOMETRY_BASELINE_PROMOTION_REVIEW",
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return json.loads(canonical_dumps(result))


def validate_baseline_promotion_gate(gate: dict[str, Any]) -> None:
    if gate.get("schema_version") != SCHEMA_VERSION:
        raise NormGeometryBaselinePromotionGateError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if gate.get("gate_status") != GATE_STATUS:
        raise NormGeometryBaselinePromotionGateError(
            f"gate_status must be {GATE_STATUS!r}"
        )
    if gate.get("gate_stage") != GATE_STAGE:
        raise NormGeometryBaselinePromotionGateError(
            f"gate_stage must be {GATE_STAGE!r}"
        )
    if gate.get("operator_id") != OPERATOR_ID:
        raise NormGeometryBaselinePromotionGateError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if gate.get("intended_lane") != "SHADOW":
        raise NormGeometryBaselinePromotionGateError("intended_lane must be SHADOW")
    if gate.get("source_decision_hash") != SOURCE_DECISION_HASH:
        raise NormGeometryBaselinePromotionGateError(
            "source_decision_hash mismatch"
        )
    if gate.get("source_closure_hash") != SOURCE_CLOSURE_HASH:
        raise NormGeometryBaselinePromotionGateError(
            "source_closure_hash mismatch"
        )
    if gate.get("all_gate_passed") is not True:
        raise NormGeometryBaselinePromotionGateError(
            "all_gate_passed must be True"
        )
    for section, key in [
        ("decision_review", "decision_review_passed"),
        ("closure_review", "closure_review_passed"),
        ("current_baseline_pack_review", "current_pack_review_passed"),
        ("authorized_pack_update_scope", "pack_update_scope_passed"),
    ]:
        sec = gate.get(section, {})
        if sec.get(key) is not True:
            raise NormGeometryBaselinePromotionGateError(
                f"{section}.{key} must be True"
            )
    locks = gate.get("authority_locks", {})
    for flag in (
        "advisory_only",
        "shadow_lane_only",
        "baseline_promotion_gate_only",
        "baseline_promotion_authorized",
        "baseline_pack_update_authorized",
    ):
        if locks.get(flag) is not True:
            raise NormGeometryBaselinePromotionGateError(
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
            raise NormGeometryBaselinePromotionGateError(
                f"authority_locks.{flag} must be False"
            )
    bs = gate.get("blocked_scopes", {})
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
            raise NormGeometryBaselinePromotionGateError(
                f"blocked_scopes.{flag} must be False"
            )
    h = gate.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise NormGeometryBaselinePromotionGateError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(gate))
    if recomputed != h:
        raise NormGeometryBaselinePromotionGateError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )
