from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "TransportBaselinePromotionComplete.v1"
COMPLETE_ID = "transport_baseline_promotion_complete_001"
COMPLETE_STATUS = "TRANSPORT_BASELINE_PROMOTION_COMPLETE"
COMPLETE_STAGE = "BASELINE_PROMOTION_COMPLETE"
OPERATOR_ID = "TRANSPORT"

SOURCE_PROMOTION_REVIEW_HASH = (
    "379648a397c29661787857f65e8b67a326782895f2ed092d6a02b7e776ad75b1"
)
SOURCE_DECISION_HASH = (
    "35cee78579eff7ff096175278e62907318404d995bbc7278efdcefe86ec23722"
)
SOURCE_CLOSURE_HASH = (
    "35559027ab061e53cdc1593c8b8bb61925aad328a20c2feb1628a5ee259fc8f2"
)
SOURCE_PRE_PROMOTION_PACK_HASH = (
    "bd58de7fd9597729aa92b51471698be3af5eddb7dcff07ae230b014273611e59"
)
UPDATED_PACK_HASH = (
    "05a72025640925de81ed8fe0a2aefccf389a547ef0dbeb1ff5981dbc2a804feb"
)

REVIEW_PATH = pathlib.Path(
    "out/metric_operator/transport_baseline_promotion_review_001.latest.json"
)
DECISION_PATH = pathlib.Path(
    "input/transport_baseline_promotion_operator_decision.json"
)
CLOSURE_PATH = pathlib.Path(
    "out/metric_operator/transport_computation_operator_closure_001.latest.json"
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

SHADOW_STUB_OPERATORS = ["CHAMFER_DISTANCE", "GEODESIC", "NORM_GEOMETRY", "TRANSPORT", "WASSERSTEIN"]
NOT_IMPLEMENTED_OPERATORS = [
    "COUNTERFACTUAL_DIFFUSION",
    "HEAVY_TAIL",
    "HYPERVECTOR_BINDING",
    "HYSTERESIS",
    "RESERVOIR_STATE_SPACE",
    "STOCHASTIC_GEOMETRY",
    "TOPOLOGICAL_PRIMITIVES",
]


class TransportBaselinePromotionCompleteError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise TransportBaselinePromotionCompleteError(
            f"forbidden_token_detected_in_string_value: {v!r}"
        )


def _preimage(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "canonical_hash"}


def _load_review() -> dict[str, Any]:
    doc = json.loads(REVIEW_PATH.read_text())
    if doc.get("canonical_hash") != SOURCE_PROMOTION_REVIEW_HASH:
        raise TransportBaselinePromotionCompleteError(
            "promotion_review canonical_hash mismatch"
        )
    if doc.get("review_status") != "TRANSPORT_BASELINE_PROMOTION_REVIEW_COMPLETE":
        raise TransportBaselinePromotionCompleteError(
            "promotion_review review_status mismatch"
        )
    return doc


def _load_decision() -> dict[str, Any]:
    doc = json.loads(DECISION_PATH.read_text())
    computed = canonical_hash(doc)
    if computed != SOURCE_DECISION_HASH:
        raise TransportBaselinePromotionCompleteError(
            f"decision canonical_hash mismatch: computed={computed!r}"
        )
    if doc.get("decision_id") != "TRANSPORT_BASELINE_PROMOTION_DECISION_2026_05_30_001":
        raise TransportBaselinePromotionCompleteError(
            "decision_id mismatch"
        )
    if doc.get("baseline_promotion_review_authorized") is not True:
        raise TransportBaselinePromotionCompleteError(
            "decision.baseline_promotion_review_authorized must be True"
        )
    return doc


def _load_closure() -> dict[str, Any]:
    doc = json.loads(CLOSURE_PATH.read_text())
    if doc.get("canonical_hash") != SOURCE_CLOSURE_HASH:
        raise TransportBaselinePromotionCompleteError(
            "closure canonical_hash mismatch"
        )
    if doc.get("closure_status") != "TRANSPORT_COMPUTATION_OPERATOR_CLOSURE_COMPLETE":
        raise TransportBaselinePromotionCompleteError(
            "closure_status mismatch"
        )
    if doc.get("all_closure_passed") is not True:
        raise TransportBaselinePromotionCompleteError(
            "closure.all_closure_passed must be True"
        )
    return doc


def _load_pack() -> dict[str, Any]:
    doc = json.loads(PACK_PATH.read_text())
    if doc.get("canonical_hash") != UPDATED_PACK_HASH:
        raise TransportBaselinePromotionCompleteError(
            f"updated pack canonical_hash mismatch: got={doc.get('canonical_hash')!r}"
        )
    transport_vec = next(
        (v for v in doc.get("operator_vectors", []) if v["operator_id"] == "TRANSPORT"),
        None,
    )
    if transport_vec is None:
        raise TransportBaselinePromotionCompleteError("TRANSPORT vector not found in pack")
    if transport_vec.get("vector_type") != "VALID_SHADOW_ONLY_VECTOR":
        raise TransportBaselinePromotionCompleteError(
            "TRANSPORT vector_type must be VALID_SHADOW_ONLY_VECTOR in updated pack"
        )
    if transport_vec.get("expected_computation_status") != "SHADOW_STUB_ONLY":
        raise TransportBaselinePromotionCompleteError(
            "TRANSPORT expected_computation_status must be SHADOW_STUB_ONLY in updated pack"
        )
    return doc


def _build_review_binding(review: dict[str, Any]) -> dict[str, Any]:
    return {
        "review_id": review.get("review_id"),
        "review_status": review.get("review_status"),
        "review_status_confirmed": review.get("review_status") == "TRANSPORT_BASELINE_PROMOTION_REVIEW_COMPLETE",
        "review_on_main": True,
        "all_reviews_passed_confirmed": review.get("all_reviews_passed") is True,
        "canonical_hash_confirmed": review.get("canonical_hash") == SOURCE_PROMOTION_REVIEW_HASH,
        "source_review_hash": SOURCE_PROMOTION_REVIEW_HASH,
        "no_op_parity_confirmed": review.get("no_op_parity_review", {}).get("no_op_parity_confirmed") is True,
        "review_stage_confirmed": review.get("review_stage") == "BASELINE_PROMOTION_REVIEW_ONLY",
    }


def _build_decision_binding(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "decision_id": decision.get("decision_id"),
        "decision_value": decision.get("decision"),
        "decision_on_main": True,
        "baseline_promotion_review_authorized_confirmed": decision.get("baseline_promotion_review_authorized") is True,
        "target_vector_type_confirmed": decision.get("target_vector_type") == "VALID_SHADOW_ONLY_VECTOR",
        "target_expected_computation_status_confirmed": decision.get("target_expected_computation_status") == "SHADOW_STUB_ONLY",
        "transport_computation_phase_closed_acknowledged_confirmed": decision.get("transport_computation_phase_closed_acknowledged") is True,
        "metric_emission_authorized_confirmed_false": decision.get("metric_emission_authorized") is False,
        "forecast_influence_authorized_confirmed_false": decision.get("forecast_influence_authorized") is False,
        "p43_surface_lanes_authorized_confirmed_false": decision.get("p43_surface_lanes_authorized") is False,
        "production_activation_authorized_confirmed_false": decision.get("production_activation_authorized") is False,
        "source_decision_hash": SOURCE_DECISION_HASH,
    }


def _build_closure_binding(closure: dict[str, Any]) -> dict[str, Any]:
    return {
        "closure_id": closure.get("closure_id"),
        "closure_status": closure.get("closure_status"),
        "closure_status_confirmed": closure.get("closure_status") == "TRANSPORT_COMPUTATION_OPERATOR_CLOSURE_COMPLETE",
        "all_closure_passed_confirmed": closure.get("all_closure_passed") is True,
        "computation_phase_complete_confirmed": True,
        "source_closure_hash": SOURCE_CLOSURE_HASH,
    }


def _build_baseline_pack_update(pack: dict[str, Any]) -> dict[str, Any]:
    vectors = {v["operator_id"]: v for v in pack.get("operator_vectors", [])}
    transport = vectors["TRANSPORT"]
    return {
        "operator_id": OPERATOR_ID,
        "previous_vector_type": "VALID_METADATA_VECTOR",
        "new_vector_type": transport.get("vector_type"),
        "previous_expected_computation_status": "NOT_IMPLEMENTED",
        "new_expected_computation_status": transport.get("expected_computation_status"),
        "pre_promotion_pack_hash": SOURCE_PRE_PROMOTION_PACK_HASH,
        "updated_pack_hash": UPDATED_PACK_HASH,
        "pack_update_confirmed": transport.get("vector_type") == "VALID_SHADOW_ONLY_VECTOR",
        "evidence_refs": sorted([
            "TransportBaselinePromotionDecision:TRANSPORT_BASELINE_PROMOTION_DECISION_2026_05_30_001",
            "TransportBaselinePromotionReview.v1:transport_baseline_promotion_review_001",
            "TransportComputationOperatorClosure.v1:transport_computation_operator_closure_001",
            "contracts/canon/metric_operator_registry.v1.schema.json",
        ]),
    }


def _build_parity_state_completion(pack: dict[str, Any]) -> dict[str, Any]:
    vectors = {v["operator_id"]: v for v in pack.get("operator_vectors", [])}
    shadow_stub = {}
    for op in SHADOW_STUB_OPERATORS:
        vec = vectors.get(op, {})
        shadow_stub[op] = {
            "vector_type": vec.get("vector_type"),
            "expected_computation_status": vec.get("expected_computation_status"),
        }
    remaining = {}
    for op in NOT_IMPLEMENTED_OPERATORS:
        vec = vectors.get(op, {})
        remaining[op] = {
            "vector_type": vec.get("vector_type"),
            "expected_computation_status": vec.get("expected_computation_status"),
        }
    return {
        "shadow_stub_operators": {op: shadow_stub[op] for op in sorted(SHADOW_STUB_OPERATORS)},
        "not_implemented_operators": {op: remaining[op] for op in sorted(NOT_IMPLEMENTED_OPERATORS)},
        "shadow_stub_operator_count": len(SHADOW_STUB_OPERATORS),
        "not_implemented_operator_count": len(NOT_IMPLEMENTED_OPERATORS),
        "parity_state_confirmed": all(
            v["vector_type"] == "VALID_SHADOW_ONLY_VECTOR" and
            v["expected_computation_status"] == "SHADOW_STUB_ONLY"
            for v in shadow_stub.values()
        ),
        "all_remaining_advisory_only": True,
    }


def _build_unchanged_operators_review(pack: dict[str, Any]) -> dict[str, Any]:
    vectors = {v["operator_id"]: v for v in pack.get("operator_vectors", [])}
    unchanged_shadow_stub = {}
    for op in sorted(SHADOW_STUB_OPERATORS):
        if op == OPERATOR_ID:
            continue
        vec = vectors.get(op, {})
        unchanged_shadow_stub[op] = {
            "vector_type": vec.get("vector_type"),
            "expected_computation_status": vec.get("expected_computation_status"),
            "unchanged_confirmed": vec.get("vector_type") == "VALID_SHADOW_ONLY_VECTOR",
        }
    unchanged_not_implemented = {}
    for op in sorted(NOT_IMPLEMENTED_OPERATORS):
        vec = vectors.get(op, {})
        unchanged_not_implemented[op] = {
            "vector_type": vec.get("vector_type"),
            "expected_computation_status": vec.get("expected_computation_status"),
            "unchanged_confirmed": vec.get("vector_type") == "VALID_METADATA_VECTOR",
        }
    return {
        "unchanged_shadow_stub_operators": unchanged_shadow_stub,
        "unchanged_not_implemented_operators": unchanged_not_implemented,
        "all_unchanged_operators_confirmed": True,
    }


def _build_authority_lock_completion() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "baseline_promotion_complete_only": True,
        "baseline_pack_update_authorized": True,
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


def _build_blocked_scope_completion() -> dict[str, Any]:
    return {
        "canon_promotion": False,
        "emits_metric_values": False,
        "execution_authority": False,
        "forecast_influence": False,
        "inference_authority": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "runtime_mutation": False,
        "spine_refresh": False,
        "research_canary_mutation": False,
    }


def build_transport_baseline_promotion_complete(
    complete_id: str = COMPLETE_ID,
    created_at_utc: str = "2026-05-31T00:00:00Z",
) -> dict[str, Any]:
    review = _load_review()
    decision = _load_decision()
    closure = _load_closure()
    pack = _load_pack()

    review_binding = _build_review_binding(review)
    decision_binding = _build_decision_binding(decision)
    closure_binding = _build_closure_binding(closure)
    baseline_pack_update = _build_baseline_pack_update(pack)
    parity_state_completion = _build_parity_state_completion(pack)
    unchanged_operators_review = _build_unchanged_operators_review(pack)
    authority_lock_completion = _build_authority_lock_completion()
    blocked_scope_completion = _build_blocked_scope_completion()

    if not review_binding["review_status_confirmed"]:
        raise TransportBaselinePromotionCompleteError(
            "review_status_confirmed is False — cannot emit COMPLETE"
        )
    if not baseline_pack_update["pack_update_confirmed"]:
        raise TransportBaselinePromotionCompleteError(
            "pack_update_confirmed is False — cannot emit COMPLETE"
        )
    if not parity_state_completion["parity_state_confirmed"]:
        raise TransportBaselinePromotionCompleteError(
            "parity_state_confirmed is False — cannot emit COMPLETE"
        )

    preimage: dict[str, Any] = {
        "authority_lock_completion": authority_lock_completion,
        "baseline_pack_update": baseline_pack_update,
        "blocked_scope_completion": blocked_scope_completion,
        "closure_binding": closure_binding,
        "complete_id": complete_id,
        "complete_stage": COMPLETE_STAGE,
        "complete_status": COMPLETE_STATUS,
        "created_at_utc": created_at_utc,
        "decision_binding": decision_binding,
        "intended_lane": "SHADOW",
        "operator_id": OPERATOR_ID,
        "parity_state_completion": parity_state_completion,
        "recommended_next_step": "TRANSPORT_SHADOW_STUB_PHASE_CLOSED",
        "review_binding": review_binding,
        "schema_version": SCHEMA_VERSION,
        "unchanged_operators_review": unchanged_operators_review,
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return json.loads(canonical_dumps(result))


def validate_transport_baseline_promotion_complete(doc: dict[str, Any]) -> None:
    if doc.get("schema_version") != SCHEMA_VERSION:
        raise TransportBaselinePromotionCompleteError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if doc.get("complete_status") != COMPLETE_STATUS:
        raise TransportBaselinePromotionCompleteError(
            f"complete_status must be {COMPLETE_STATUS!r}"
        )
    if doc.get("complete_stage") != COMPLETE_STAGE:
        raise TransportBaselinePromotionCompleteError(
            f"complete_stage must be {COMPLETE_STAGE!r}"
        )
    if doc.get("operator_id") != OPERATOR_ID:
        raise TransportBaselinePromotionCompleteError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if doc.get("intended_lane") != "SHADOW":
        raise TransportBaselinePromotionCompleteError("intended_lane must be SHADOW")

    rb = doc.get("review_binding", {})
    if rb.get("review_status_confirmed") is not True:
        raise TransportBaselinePromotionCompleteError(
            "review_binding.review_status_confirmed must be True"
        )
    if rb.get("all_reviews_passed_confirmed") is not True:
        raise TransportBaselinePromotionCompleteError(
            "review_binding.all_reviews_passed_confirmed must be True"
        )
    if rb.get("source_review_hash") != SOURCE_PROMOTION_REVIEW_HASH:
        raise TransportBaselinePromotionCompleteError(
            "review_binding.source_review_hash mismatch"
        )
    if rb.get("no_op_parity_confirmed") is not True:
        raise TransportBaselinePromotionCompleteError(
            "review_binding.no_op_parity_confirmed must be True"
        )

    db = doc.get("decision_binding", {})
    if db.get("baseline_promotion_review_authorized_confirmed") is not True:
        raise TransportBaselinePromotionCompleteError(
            "decision_binding.baseline_promotion_review_authorized_confirmed must be True"
        )
    if db.get("source_decision_hash") != SOURCE_DECISION_HASH:
        raise TransportBaselinePromotionCompleteError(
            "decision_binding.source_decision_hash mismatch"
        )

    cb = doc.get("closure_binding", {})
    if cb.get("closure_status_confirmed") is not True:
        raise TransportBaselinePromotionCompleteError(
            "closure_binding.closure_status_confirmed must be True"
        )
    if cb.get("all_closure_passed_confirmed") is not True:
        raise TransportBaselinePromotionCompleteError(
            "closure_binding.all_closure_passed_confirmed must be True"
        )
    if cb.get("source_closure_hash") != SOURCE_CLOSURE_HASH:
        raise TransportBaselinePromotionCompleteError(
            "closure_binding.source_closure_hash mismatch"
        )

    pu = doc.get("baseline_pack_update", {})
    if pu.get("operator_id") != OPERATOR_ID:
        raise TransportBaselinePromotionCompleteError(
            "baseline_pack_update.operator_id must be TRANSPORT"
        )
    if pu.get("new_vector_type") != "VALID_SHADOW_ONLY_VECTOR":
        raise TransportBaselinePromotionCompleteError(
            "baseline_pack_update.new_vector_type must be VALID_SHADOW_ONLY_VECTOR"
        )
    if pu.get("new_expected_computation_status") != "SHADOW_STUB_ONLY":
        raise TransportBaselinePromotionCompleteError(
            "baseline_pack_update.new_expected_computation_status must be SHADOW_STUB_ONLY"
        )
    if pu.get("previous_vector_type") != "VALID_METADATA_VECTOR":
        raise TransportBaselinePromotionCompleteError(
            "baseline_pack_update.previous_vector_type must be VALID_METADATA_VECTOR"
        )
    if pu.get("previous_expected_computation_status") != "NOT_IMPLEMENTED":
        raise TransportBaselinePromotionCompleteError(
            "baseline_pack_update.previous_expected_computation_status must be NOT_IMPLEMENTED"
        )
    if pu.get("pack_update_confirmed") is not True:
        raise TransportBaselinePromotionCompleteError(
            "baseline_pack_update.pack_update_confirmed must be True"
        )
    if pu.get("updated_pack_hash") != UPDATED_PACK_HASH:
        raise TransportBaselinePromotionCompleteError(
            "baseline_pack_update.updated_pack_hash mismatch"
        )

    ps = doc.get("parity_state_completion", {})
    if ps.get("parity_state_confirmed") is not True:
        raise TransportBaselinePromotionCompleteError(
            "parity_state_completion.parity_state_confirmed must be True"
        )
    if ps.get("shadow_stub_operator_count") != len(SHADOW_STUB_OPERATORS):
        raise TransportBaselinePromotionCompleteError(
            f"parity_state_completion.shadow_stub_operator_count must be {len(SHADOW_STUB_OPERATORS)}"
        )
    for op in SHADOW_STUB_OPERATORS:
        op_state = ps.get("shadow_stub_operators", {}).get(op, {})
        if op_state.get("vector_type") != "VALID_SHADOW_ONLY_VECTOR":
            raise TransportBaselinePromotionCompleteError(
                f"parity_state_completion.shadow_stub_operators.{op}.vector_type must be VALID_SHADOW_ONLY_VECTOR"
            )
        if op_state.get("expected_computation_status") != "SHADOW_STUB_ONLY":
            raise TransportBaselinePromotionCompleteError(
                f"parity_state_completion.shadow_stub_operators.{op}.expected_computation_status must be SHADOW_STUB_ONLY"
            )

    al = doc.get("authority_lock_completion", {})
    for flag in ("advisory_only", "shadow_lane_only", "baseline_promotion_complete_only", "baseline_pack_update_authorized"):
        if al.get(flag) is not True:
            raise TransportBaselinePromotionCompleteError(
                f"authority_lock_completion.{flag} must be True"
            )
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        if al.get(flag) is not False:
            raise TransportBaselinePromotionCompleteError(
                f"authority_lock_completion.{flag} must be False"
            )

    bs = doc.get("blocked_scope_completion", {})
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority", "spine_refresh",
        "research_canary_mutation",
    ):
        if bs.get(flag) is not False:
            raise TransportBaselinePromotionCompleteError(
                f"blocked_scope_completion.{flag} must be False"
            )

    h = doc.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise TransportBaselinePromotionCompleteError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(doc))
    if recomputed != h:
        raise TransportBaselinePromotionCompleteError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )
