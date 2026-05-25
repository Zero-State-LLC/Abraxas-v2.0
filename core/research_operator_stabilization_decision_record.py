from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchOperatorStabilizationDecisionRecord.v1"
LANE_ID = "P100_RESEARCH_OPERATOR_STABILIZATION_DECISION_RECORD"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P99_RESEARCH_CROSS_DROP_CONFLICT_SCAN"
REQUIRED_P99_ARTIFACT_TYPE = "ResearchCrossDropConflictScan.v1"
RECOMMENDED_NEXT_LANE_ON_ADVANCE = "P101_RESEARCH_SHADOW_STABILIZATION_RECEIPT"

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

# Candidate IDs in deterministic order
CANDIDATE_IDS: tuple[str, ...] = (
    "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER",
    "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
    "DROP006C_SURVIVAL_CALIBRATION_GOVERNANCE_LAYER",
    "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
    "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER",
    "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER",
)

# Boundary note IDs that preserve Drop006/Drop007 overlap separation
_DROP006_DROP007_OVERLAP_BOUNDARY_IDS: frozenset[str] = frozenset(
    {
        "drop006_drop007_hidden_intent_endpoint_constraint",
        "drop006_drop007_proactive_vs_inductive_planning_trace",
        "drop006_drop007_situation_continuity_vs_behavioral_graph",
        "drop006_drop007_interleaved_intent_vs_behavioral_graph",
        "drop006_drop007_intervention_window_vs_pruning_signal",
        "drop006_drop007_coordination_threshold_vs_topology_concepts",
        "drop006_drop007_calibration_projection_vs_pse_calibration",
    }
)

_P99_PASS_STATUSES: frozenset[str] = frozenset(
    {"PASS_CLEAN", "PASS_WITH_ADVISORY_CONFLICTS"}
)


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _has_drop006_drop007_overlap_separation(p99_packet: dict[str, Any]) -> bool:
    """Return True when P99 boundary_resolution_notes preserve Drop006/Drop007 separation."""
    boundary_notes = p99_packet.get("boundary_resolution_notes")
    if not isinstance(boundary_notes, list):
        return False
    present_ids = {
        entry.get("boundary_id")
        for entry in boundary_notes
        if isinstance(entry, dict)
    }
    return _DROP006_DROP007_OVERLAP_BOUNDARY_IDS.issubset(present_ids)


def _validate_p99_packet(p99_packet: Any) -> list[str]:
    """Return a list of not-computable reasons (empty means valid for processing)."""
    if p99_packet is None:
        return ["p99_packet_missing"]
    if not isinstance(p99_packet, dict):
        return ["p99_packet_malformed:not_a_dict"]

    reasons: list[str] = []

    artifact_type = p99_packet.get("artifact_type")
    if artifact_type != REQUIRED_P99_ARTIFACT_TYPE:
        reasons.append(f"p99_artifact_type_mismatch:{artifact_type!r}")

    lane_id = p99_packet.get("lane_id")
    if lane_id != UPSTREAM_LANE_ID:
        reasons.append(f"p99_lane_id_mismatch:{lane_id!r}")

    recommended_next_lane = p99_packet.get("recommended_next_lane")
    if recommended_next_lane != LANE_ID:
        reasons.append(f"p99_recommendation_chain_mismatch:{recommended_next_lane!r}")

    status = p99_packet.get("status")
    if status not in _P99_PASS_STATUSES:
        reasons.append(f"p99_status_not_pass:{status!r}")

    # Hard conflicts make P99 not computable for P100
    for conflict_key in ("duplicate_id_conflicts", "schema_conflicts", "rune_conflicts", "metric_conflicts"):
        conflicts = p99_packet.get(conflict_key)
        if isinstance(conflicts, list) and conflicts:
            reasons.append(f"p99_has_hard_{conflict_key}")

    return reasons


def _check_authority_drift(p99_packet: dict[str, Any]) -> list[str]:
    """Return authority-drift findings from P99 (non-empty means REJECTED_AUTHORITY_DRIFT)."""
    findings: list[str] = []

    # If P99 itself reports authority drift findings
    p99_drift = p99_packet.get("authority_drift_findings")
    if isinstance(p99_drift, list) and p99_drift:
        findings.extend(f"p99_authority_drift_finding:{f}" for f in p99_drift)

    # Check P99's own authority locks
    authority_locks = p99_packet.get("authority_locks")
    if not isinstance(authority_locks, dict):
        findings.append("p99_authority_locks_malformed")
    else:
        for key in AUTHORITY_LOCK_KEYS:
            if authority_locks.get(key) is not False:
                findings.append(f"p99_authority_lock_drift:{key}")

    return sorted(set(findings))


def _build_candidate_decisions(
    *,
    has_overlap_separation: bool,
) -> dict[str, str]:
    """Return deterministic per-candidate decisions."""
    decisions: dict[str, str] = {
        "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER": "hold",
        "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER": "advance_to_shadow_stabilization",
        "DROP006C_SURVIVAL_CALIBRATION_GOVERNANCE_LAYER": "hold",
        "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER": "advance_to_shadow_stabilization",
        "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER": "hold",
        "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER": (
            "advance_to_shadow_stabilization" if has_overlap_separation else "repair"
        ),
    }
    return decisions


def build_research_operator_stabilization_decision_record(
    *,
    p99_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons = _validate_p99_packet(p99_packet)
    normalized_p99 = p99_packet if isinstance(p99_packet, dict) else None

    authority_drift_findings: list[str] = []
    candidate_decisions: dict[str, str] = {}
    has_overlap_separation = False

    if not not_computable_reasons and normalized_p99 is not None:
        authority_drift_findings = _check_authority_drift(normalized_p99)

        if not authority_drift_findings:
            has_overlap_separation = _has_drop006_drop007_overlap_separation(normalized_p99)
            candidate_decisions = _build_candidate_decisions(
                has_overlap_separation=has_overlap_separation,
            )

    # Classify candidates
    stabilized_candidates: list[str] = []  # always empty — P100 does not stabilize
    held_candidates: list[str] = []
    repair_candidates: list[str] = []
    rejected_candidates: list[str] = []
    advanced_candidates: list[str] = []

    for cid in CANDIDATE_IDS:
        decision = candidate_decisions.get(cid)
        if decision == "advance_to_shadow_stabilization":
            advanced_candidates.append(cid)
        elif decision == "hold":
            held_candidates.append(cid)
        elif decision == "repair":
            repair_candidates.append(cid)
        elif decision == "reject":
            rejected_candidates.append(cid)

    if not_computable_reasons:
        status = "NOT_COMPUTABLE"
        operator_decision_record_status = "NOT_COMPUTABLE"
        operator_decision = "NOT_COMPUTABLE"
        decision_reason = (
            "Upstream P99 packet is missing, malformed, non-pass, structurally invalid, "
            "has unresolved hard conflicts, or is on the wrong recommendation chain."
        )
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P99 must be a valid PASS packet before operator decisions can be recorded."
        )
        unresolved_conflicts = not_computable_reasons
    elif authority_drift_findings:
        status = "REJECTED_AUTHORITY_DRIFT"
        operator_decision_record_status = "REJECTED_AUTHORITY_DRIFT"
        operator_decision = "REJECTED_AUTHORITY_DRIFT"
        decision_reason = (
            "P99 reports authority drift or one or more authority locks are true; "
            "operator decision record cannot be emitted."
        )
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "Authority drift must be cleared before any operator decision record can proceed."
        )
        unresolved_conflicts = authority_drift_findings
    else:
        status = "OPERATOR_DECISION_RECORD_EMITTED"
        operator_decision_record_status = "EMITTED"
        operator_decision = "advisory_operator_record"
        decision_reason = (
            "Deterministic operator decision record emitted from valid P99 pass; "
            "no candidates stabilized or promoted; operator review required."
        )
        unresolved_conflicts = []

        if advanced_candidates:
            recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_ADVANCE
            recommended_next_lane_reason = (
                "At least one candidate is recommended for shadow stabilization "
                "and no authority drift exists; operator must review before proceeding."
            )
        else:
            recommended_next_lane = "NOT_COMPUTABLE"
            recommended_next_lane_reason = (
                "No candidates are advancing to shadow stabilization; "
                "P101 cannot be recommended."
            )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "lane_id": LANE_ID,
        "status": status,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_conflict_scan_status": (
            normalized_p99.get("status") if normalized_p99 is not None else None
        ),
        "operator_decision_record_status": operator_decision_record_status,
        "operator_decision": operator_decision,
        "decision_reason": decision_reason,
        "candidate_decisions": candidate_decisions,
        "stabilized_candidates": stabilized_candidates,
        "held_candidates": held_candidates,
        "repair_candidates": repair_candidates,
        "rejected_candidates": rejected_candidates,
        "unresolved_conflicts": unresolved_conflicts,
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p99_research_cross_drop_conflict_scan",
            "mapping_method": "deterministic_operator_decision_record",
            "candidate_ids": list(CANDIDATE_IDS),
            "allowed_decisions": sorted(ALLOWED_DECISIONS),
            "forbidden_decisions": sorted(FORBIDDEN_DECISIONS),
            "boundary_rules": [
                "hidden_intent_is_never_known_intent",
                "proactivity_is_never_autonomous_execution",
                "intent_graph_dependency_is_never_confirmed_intent",
                "endpoint_constraint_is_never_known_goal",
                "calibration_projection_is_never_forecast_weight_mutation",
                "aal_viz_is_projection_only",
                "operator_decision_record_is_not_stabilization_authority",
            ],
            "gated_recommendation_rule": (
                "recommend_p101_only_when_at_least_one_candidate_advances_and_no_authority_drift"
            ),
        },
    }
    return _finalize(packet_base)


def write_research_operator_stabilization_decision_record(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
