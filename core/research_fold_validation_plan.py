from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchFoldValidationPlan.v1"
LANE_ID = "P96_RESEARCH_FOLD_VALIDATION_PLAN"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P95_RESEARCH_FOLD_DROP_SPEC_BUILDER"
RECOMMENDED_NEXT_LANE_ON_PASS = "P97_RESEARCH_DERIVED_SUBSYSTEM_CANDIDATE_LEDGER"

REQUIRED_P95_ARTIFACT_TYPE = "ResearchFoldDropSpecBuilder.v1"

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

DROP_006_FIXTURES: tuple[str, ...] = (
    "fixture_drop006_intent_graph_valid.json",
    "fixture_drop006_active_inference_valid.json",
    "fixture_drop006_survival_calibration_valid.json",
    "fixture_drop006_missing_source_not_computable.json",
    "fixture_drop006_authority_escalation_rejected.json",
    "fixture_drop006_forecast_weight_mutation_rejected.json",
)

DROP_007_FIXTURES: tuple[str, ...] = (
    "fixture_drop007_hidden_intent_candidate_valid.json",
    "fixture_drop007_cross_session_dependency_valid.json",
    "fixture_drop007_interleaved_intent_trace_valid.json",
    "fixture_drop007_contextual_intervention_window_valid.json",
    "fixture_drop007_coordination_threshold_valid.json",
    "fixture_drop007_hidden_intent_overclaim_rejected.json",
    "fixture_drop007_operator_bypass_rejected.json",
    "fixture_drop007_autonomous_execution_rejected.json",
)

DROP_006_SPEC_IDS: tuple[str, ...] = (
    "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_SPEC",
    "DROP006B_ACTIVE_INFERENCE_INTENTIONAL_PLANNING_SPEC",
    "DROP006C_ISOTONIC_SURVIVAL_CALIBRATION_SPEC",
)

DROP_007_SPEC_IDS: tuple[str, ...] = (
    "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_SPEC",
    "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_SPEC",
    "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_SPEC",
)


def _validate_p95_packet(p95_packet: Any) -> list[str]:
    if p95_packet is None:
        return ["p95_packet_missing"]
    if not isinstance(p95_packet, dict):
        return ["p95_packet_malformed:not_a_dict"]

    reasons: list[str] = []

    artifact_type = p95_packet.get("artifact_type")
    if artifact_type != REQUIRED_P95_ARTIFACT_TYPE:
        reasons.append(f"p95_artifact_type_mismatch:{artifact_type!r}")

    p95_status = p95_packet.get("status")
    if p95_status != "PASS":
        reasons.append(f"p95_status_not_pass:{p95_status!r}")

    authority_locks = p95_packet.get("authority_locks")
    if isinstance(authority_locks, dict):
        drifted = [key for key, value in authority_locks.items() if value is not False]
        if drifted:
            reasons.append(f"p95_authority_drift_detected:{sorted(drifted)!r}")
    else:
        reasons.append("p95_authority_locks_malformed")

    generated_drop_specs = p95_packet.get("generated_drop_specs")
    if isinstance(generated_drop_specs, list):
        drop_ids = {
            spec.get("drop_id")
            for spec in generated_drop_specs
            if isinstance(spec, dict)
        }
        if "DROP006" not in drop_ids or "DROP007" not in drop_ids:
            reasons.append("p95_generated_drop_specs_missing_required_drops")
    else:
        reasons.append("p95_generated_drop_specs_malformed")

    return reasons


def _build_fixture_plan() -> list[dict[str, Any]]:
    return [
        {
            "drop_id": "DROP006",
            "fixture_targets": list(DROP_006_FIXTURES),
        },
        {
            "drop_id": "DROP007",
            "fixture_targets": list(DROP_007_FIXTURES),
        },
    ]


def _build_positive_proof_packet_plan() -> dict[str, Any]:
    return {
        "deterministic_source_candidate_ordering": "drop_order_then_source_candidate_order",
        "canon_shadow_target_mapping": [
            {
                "drop_id": "DROP006",
                "spec_ids": list(DROP_006_SPEC_IDS),
                "canon_shadow_target": "canon_shadow_drop006_validation_target",
            },
            {
                "drop_id": "DROP007",
                "spec_ids": list(DROP_007_SPEC_IDS),
                "canon_shadow_target": "canon_shadow_drop007_validation_target",
            },
        ],
        "authority_locks_remain_false": True,
        "advisory_only_posture_preserved": True,
        "aal_viz_projection_only_posture_preserved": True,
        "next_state": "VALIDATION_PLANNING_ONLY",
    }


def _build_negative_failure_proof_packet_plan() -> dict[str, Any]:
    return {
        "rejected_conditions": [
            "hidden_intent_marked_as_known_intent",
            "proactive_suggestion_marked_autonomous",
            "intent_graph_dependency_marked_confirmed_intent",
            "endpoint_constraint_marked_known_goal",
            "calibration_candidate_mutating_forecast_weights",
            "aal_viz_claiming_inference_authority",
            "missing_provenance",
            "missing_source_identity",
            "runtime_scheduler_baseline_canon_mutation_request",
        ]
    }


def _build_operator_review_requirements() -> list[str]:
    return [
        "confirm_provenance_fields_present_and_source_identity_bound",
        "confirm_drop006_fixture_execution_order_matches_plan",
        "confirm_drop007_fixture_execution_order_matches_plan",
        "confirm_positive_proof_packet_plan_advisory_and_projection_only",
        "confirm_negative_failure_proof_packet_plan_rejections_enforced",
        "confirm_authority_locks_all_false_before_any_lane_transition",
    ]


def _build_aal_viz_projection_constraints() -> list[str]:
    return [
        "aal_viz_projection_only",
        "aal_viz_no_runtime_or_scheduler_mutation",
        "aal_viz_no_forecast_weight_mutation",
        "aal_viz_no_inference_or_execution_authority_claim",
    ]


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def build_research_fold_validation_plan(
    *,
    p95_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons = _validate_p95_packet(p95_packet)

    if not_computable_reasons:
        status = "NOT_COMPUTABLE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P95 upstream packet is missing, failed, malformed, or contains authority drift; "
            "validation planning cannot proceed."
        )
    else:
        status = "PASS"
        recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_PASS
        recommended_next_lane_reason = (
            "P96 validation planning is deterministic and advisory-only; "
            "proceed to P97 candidate ledger planning."
        )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "lane_id": LANE_ID,
        "status": status,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_drop_spec_status": p95_packet.get("status") if isinstance(p95_packet, dict) else None,
        "fixture_plan": _build_fixture_plan(),
        "positive_proof_packet_plan": _build_positive_proof_packet_plan(),
        "negative_failure_proof_packet_plan": _build_negative_failure_proof_packet_plan(),
        "operator_review_requirements": _build_operator_review_requirements(),
        "aal_viz_projection_constraints": _build_aal_viz_projection_constraints(),
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p95_research_fold_drop_spec_builder",
            "mapping_method": "deterministic_validation_planning",
            "drop_order": ["DROP006", "DROP007"],
            "fixture_ordering": "drop_order_then_static_fixture_order",
            "p95_status": p95_packet.get("status") if isinstance(p95_packet, dict) else None,
            "p95_artifact_type": p95_packet.get("artifact_type") if isinstance(p95_packet, dict) else None,
            "gated_recommendation_rule": "recommend_p97_only_when_status_pass",
        },
    }
    return _finalize(packet_base)


def write_research_fold_validation_plan(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
