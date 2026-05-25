from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchFoldDropSpecBuilder.v1"
LANE_ID = "P95_RESEARCH_FOLD_DROP_SPEC_BUILDER"
CANONICAL_STATUS = "ADVISORY_ONLY"
RECOMMENDED_NEXT_LANE_ON_PASS = "P96_RESEARCH_FOLD_VALIDATION_PLAN"

REQUIRED_P94_ARTIFACT_TYPE = "ResearchFoldCanonAlignmentPlan.v1"

AUTHORITY_LOCK_KEYS: tuple[str, ...] = (
    "production_activation",
    "canon_promotion",
    "runtime_mutation",
    "forecast_influence",
    "forecast_weight_allowed",
    "shadow_to_forecast_leakage",
    "scheduler_mutation",
    "autonomous_execution",
    "operator_bypass",
    "hidden_intent_claim_authority",
)

# Static drop-spec definitions derived from canon Drop 006 and Drop 007.
# Each entry: (drop_id, spec_id, source_candidate_id)
DROP_SPEC_DEFINITIONS: tuple[tuple[str, str, str], ...] = (
    (
        "DROP006",
        "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_SPEC",
        "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER",
    ),
    (
        "DROP006",
        "DROP006B_ACTIVE_INFERENCE_INTENTIONAL_PLANNING_SPEC",
        "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
    ),
    (
        "DROP006",
        "DROP006C_ISOTONIC_SURVIVAL_CALIBRATION_SPEC",
        "DROP006C_SURVIVAL_CALIBRATION_GOVERNANCE_LAYER",
    ),
    (
        "DROP007",
        "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_SPEC",
        "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
    ),
    (
        "DROP007",
        "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_SPEC",
        "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER",
    ),
    (
        "DROP007",
        "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_SPEC",
        "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER",
    ),
)

_BOUNDARY_RULES: tuple[str, ...] = (
    "hidden_intent_is_never_known_intent",
    "proactivity_is_never_autonomous_execution",
    "spec_is_never_executable_module",
    "advisory_spec_is_never_canon_active",
    "drop_spec_builder_is_projection_only",
)


def _validate_p94_packet(
    p94_packet: Any,
) -> list[str]:
    """Return a list of not-computable reasons; empty list means valid."""
    if p94_packet is None:
        return ["p94_packet_missing"]
    if not isinstance(p94_packet, dict):
        return ["p94_packet_malformed:not_a_dict"]

    reasons: list[str] = []

    artifact_type = p94_packet.get("artifact_type")
    if artifact_type != REQUIRED_P94_ARTIFACT_TYPE:
        reasons.append(f"p94_artifact_type_mismatch:{artifact_type!r}")

    p94_status = p94_packet.get("status")
    if p94_status != "PASS":
        reasons.append(f"p94_status_not_pass:{p94_status!r}")

    p94_alignment = p94_packet.get("canon_alignment_status")
    if p94_alignment != "ALIGNED":
        reasons.append(f"p94_canon_alignment_not_aligned:{p94_alignment!r}")

    authority_locks = p94_packet.get("authority_locks")
    if isinstance(authority_locks, dict):
        drifted = [k for k, v in authority_locks.items() if v is not False]
        if drifted:
            reasons.append(f"p94_authority_drift_detected:{sorted(drifted)!r}")
    elif authority_locks is not None:
        reasons.append("p94_authority_locks_malformed")

    return reasons


def _build_generated_drop_specs() -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for drop_id, spec_id, source_candidate_id in DROP_SPEC_DEFINITIONS:
        specs.append(
            {
                "drop_id": drop_id,
                "spec_id": spec_id,
                "source_candidate_id": source_candidate_id,
                "spec_mode": "ADVISORY_SPEC_ONLY",
                "executable": False,
            }
        )
    return specs


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def build_research_fold_drop_spec_builder(
    *,
    p94_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons = _validate_p94_packet(p94_packet)

    if not_computable_reasons:
        status = "NOT_COMPUTABLE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P94 upstream packet is missing, failed, malformed, or contains authority drift; "
            "drop-spec generation cannot proceed."
        )
        generated_drop_specs: list[dict[str, Any]] = []
    else:
        status = "PASS"
        recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_PASS
        recommended_next_lane_reason = (
            "P95 drop-spec generation is advisory-only and complete; "
            "proceed to governed validation in P96."
        )
        generated_drop_specs = _build_generated_drop_specs()

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "lane_id": LANE_ID,
        "status": status,
        "generated_drop_specs": generated_drop_specs,
        "authority_locks": {lock_key: False for lock_key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p94_research_fold_canon_alignment_plan",
            "mapping_method": "deterministic_static_spec_generation",
            "drop_order": ["DROP006", "DROP007"],
            "spec_ordering": "drop_order_then_static_definition_order",
            "p94_status": p94_packet.get("status") if isinstance(p94_packet, dict) else None,
            "p94_canon_alignment_status": (
                p94_packet.get("canon_alignment_status") if isinstance(p94_packet, dict) else None
            ),
            "boundary_rules": list(_BOUNDARY_RULES),
            "gated_recommendation_rule": "recommend_p96_only_when_status_pass",
        },
    }
    return _finalize(packet_base)


def write_research_fold_drop_spec_builder(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
