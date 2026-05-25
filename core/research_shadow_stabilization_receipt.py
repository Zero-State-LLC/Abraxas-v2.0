from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchShadowStabilizationReceipt.v1"
LANE_ID = "P101_RESEARCH_SHADOW_STABILIZATION_RECEIPT"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P100_RESEARCH_OPERATOR_STABILIZATION_DECISION_RECORD"
REQUIRED_P100_ARTIFACT_TYPE = "ResearchOperatorStabilizationDecisionRecord.v1"
RECOMMENDED_NEXT_LANE_ON_PASS = "P102_RESEARCH_STABILIZATION_WINDOW_MONITOR"

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

ALLOWED_DECISIONS: frozenset[str] = frozenset(
    {"hold", "repair", "reject", "advance_to_shadow_stabilization"}
)

FORBIDDEN_DECISIONS: frozenset[str] = frozenset(
    {
        "canon_promote",
        "production_activate",
        "runtime_mutate",
        "scheduler_mutate",
        "forecast_weight_import",
        "autonomous_execute",
        "operator_bypass",
        "hidden_intent_claim_authority",
    }
)

CANDIDATE_IDS: tuple[str, ...] = (
    "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER",
    "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
    "DROP006C_SURVIVAL_CALIBRATION_GOVERNANCE_LAYER",
    "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
    "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER",
    "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER",
)

STABILIZATION_WINDOW_REQUIREMENTS: dict[str, Any] = {
    "minimum_shadow_cycles_required": 12,
    "authority_lock_invariance_required": True,
    "deterministic_replay_required": True,
    "not_computable_failure_proof_required": True,
    "aal_viz_projection_only_required": True,
    "operator_review_required": True,
    "no_runtime_mutation": True,
    "no_canon_promotion": True,
    "no_forecast_weight_mutation": True,
}


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def _validate_p100_packet(p100_packet: Any) -> list[str]:
    if p100_packet is None:
        return ["p100_packet_missing"]
    if not isinstance(p100_packet, dict):
        return ["p100_packet_malformed:not_a_dict"]

    reasons: list[str] = []

    if p100_packet.get("artifact_type") != REQUIRED_P100_ARTIFACT_TYPE:
        reasons.append(
            f"p100_artifact_type_mismatch:{p100_packet.get('artifact_type')!r}"
        )
    if p100_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p100_lane_id_mismatch:{p100_packet.get('lane_id')!r}")
    if p100_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p100_canonical_status_mismatch:{p100_packet.get('canonical_status')!r}"
        )
    if p100_packet.get("advisory_only") is not True:
        reasons.append("p100_advisory_only_not_true")
    if p100_packet.get("projection_only") is not True:
        reasons.append("p100_projection_only_not_true")

    status = p100_packet.get("status")
    operator_status = p100_packet.get("operator_decision_record_status")
    valid_statuses = {
        ("OPERATOR_DECISION_RECORD_EMITTED", "EMITTED"),
        ("REJECTED_AUTHORITY_DRIFT", "REJECTED_AUTHORITY_DRIFT"),
    }
    if (status, operator_status) not in valid_statuses:
        reasons.append(f"p100_status_not_emitted_or_rejected:{status!r}")
        reasons.append(
            f"p100_operator_decision_record_status_not_emitted_or_rejected:{operator_status!r}"
        )

    if status == "OPERATOR_DECISION_RECORD_EMITTED":
        recommended_next_lane = p100_packet.get("recommended_next_lane")
        if recommended_next_lane != LANE_ID:
            reasons.append(
                f"p100_recommendation_chain_mismatch:{recommended_next_lane!r}"
            )

    candidate_decisions = p100_packet.get("candidate_decisions")
    if not isinstance(candidate_decisions, dict):
        reasons.append("p100_candidate_decisions_malformed")
        return sorted(set(reasons))

    expected_candidates = set(CANDIDATE_IDS)
    for candidate_id in CANDIDATE_IDS:
        if candidate_id not in candidate_decisions:
            reasons.append(f"p100_candidate_decision_missing:{candidate_id}")

    extra_candidates = sorted(set(candidate_decisions) - expected_candidates)
    for candidate_id in extra_candidates:
        reasons.append(f"p100_candidate_decision_unknown_candidate:{candidate_id}")

    for candidate_id in CANDIDATE_IDS:
        decision = candidate_decisions.get(candidate_id)
        if not isinstance(decision, str):
            reasons.append(f"p100_candidate_decision_malformed:{candidate_id}")
            continue
        if decision in FORBIDDEN_DECISIONS:
            reasons.append(f"p100_forbidden_candidate_decision:{candidate_id}:{decision}")
        elif decision not in ALLOWED_DECISIONS:
            reasons.append(f"p100_candidate_decision_invalid:{candidate_id}:{decision}")

    authority_locks = p100_packet.get("authority_locks")
    if not isinstance(authority_locks, dict):
        reasons.append("p100_authority_locks_malformed")
    else:
        for key in AUTHORITY_LOCK_KEYS:
            if key not in authority_locks:
                reasons.append(f"p100_authority_lock_missing:{key}")

    return sorted(set(reasons))


def _classify_candidate_decisions(
    candidate_decisions: dict[str, str],
) -> tuple[list[str], list[str], list[str], list[str]]:
    stabilized_candidates: list[str] = []
    held_candidates: list[str] = []
    repair_candidates: list[str] = []
    rejected_candidates: list[str] = []

    for candidate_id in CANDIDATE_IDS:
        decision = candidate_decisions[candidate_id]
        if decision == "advance_to_shadow_stabilization":
            stabilized_candidates.append(candidate_id)
        elif decision == "hold":
            held_candidates.append(candidate_id)
        elif decision == "repair":
            repair_candidates.append(candidate_id)
        elif decision == "reject":
            rejected_candidates.append(candidate_id)

    return (
        stabilized_candidates,
        held_candidates,
        repair_candidates,
        rejected_candidates,
    )


def _detect_authority_drift(p100_packet: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    if p100_packet.get("status") == "REJECTED_AUTHORITY_DRIFT":
        findings.append("p100_reports_authority_drift")

    authority_locks = p100_packet.get("authority_locks")
    if isinstance(authority_locks, dict):
        for key in AUTHORITY_LOCK_KEYS:
            if authority_locks.get(key) is not False:
                findings.append(f"p100_authority_lock_drift:{key}")

    return sorted(set(findings))


def build_research_shadow_stabilization_receipt(
    *,
    p100_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons = _validate_p100_packet(p100_packet)
    normalized_p100 = p100_packet if isinstance(p100_packet, dict) else None

    candidate_decisions: dict[str, str] = {}
    advanced_candidates: list[str] = []
    held_candidates: list[str] = []
    repair_candidates: list[str] = []
    rejected_candidates: list[str] = []
    authority_drift_findings: list[str] = []

    if not not_computable_reasons and normalized_p100 is not None:
        candidate_decisions = {
            candidate_id: normalized_p100["candidate_decisions"][candidate_id]
            for candidate_id in CANDIDATE_IDS
        }
        (
            advanced_candidates,
            held_candidates,
            repair_candidates,
            rejected_candidates,
        ) = _classify_candidate_decisions(candidate_decisions)
        authority_drift_findings = _detect_authority_drift(normalized_p100)
        if not advanced_candidates:
            not_computable_reasons = ["p100_no_shadow_stabilization_candidates"]

    if not_computable_reasons:
        status = "NOT_COMPUTABLE"
        stabilization_receipt_status = "NOT_COMPUTABLE"
        stabilized_candidates: list[str] = []
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P100 must be a valid emitted advisory-only packet on the P100→P101 chain "
            "with at least one shadow-stabilization candidate."
        )
    elif authority_drift_findings:
        status = "REJECTED_AUTHORITY_DRIFT"
        stabilization_receipt_status = "REJECTED_AUTHORITY_DRIFT"
        stabilized_candidates = []
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "Authority drift must be cleared before any shadow stabilization receipt "
            "can recommend P102."
        )
    else:
        status = "SHADOW_STABILIZATION_RECEIPT_EMITTED"
        stabilization_receipt_status = "EMITTED"
        stabilized_candidates = advanced_candidates
        recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_PASS
        recommended_next_lane_reason = (
            "At least one candidate entered advisory-only SHADOW stabilization with no "
            "authority drift; proceed to P102 research stabilization window monitor."
        )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "lane_id": LANE_ID,
        "status": status,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_operator_decision_status": (
            normalized_p100.get("status") if normalized_p100 is not None else None
        ),
        "stabilization_receipt_status": stabilization_receipt_status,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "stabilization_window_requirements": dict(STABILIZATION_WINDOW_REQUIREMENTS),
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p100_research_operator_stabilization_decision_record",
            "mapping_method": "deterministic_shadow_stabilization_receipt",
            "candidate_ids": list(CANDIDATE_IDS),
            "allowed_decisions": sorted(ALLOWED_DECISIONS),
            "forbidden_decisions": sorted(FORBIDDEN_DECISIONS),
            "boundary_rules": [
                "shadow_stabilization_receipt_is_not_implementation_authority",
                "shadow_stabilization_receipt_is_not_canon_promotion",
                "shadow_stabilization_receipt_is_not_production_activation",
                "shadow_stabilization_receipt_is_not_runtime_mutation",
                "shadow_stabilization_receipt_is_not_autonomous_execution",
                "aal_viz_remains_projection_only",
            ],
            "gated_recommendation_rule": (
                "recommend_p102_only_when_at_least_one_candidate_is_stabilized_and_no_authority_drift_exists"
            ),
            "p100_status": normalized_p100.get("status") if normalized_p100 else None,
            "p100_artifact_type": (
                normalized_p100.get("artifact_type") if normalized_p100 else None
            ),
        },
    }
    return _finalize(packet_base)


def write_research_shadow_stabilization_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
