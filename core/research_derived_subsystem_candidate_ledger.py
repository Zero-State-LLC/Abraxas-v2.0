from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ResearchDerivedSubsystemCandidateLedger.v1"
LANE_ID = "P97_RESEARCH_DERIVED_SUBSYSTEM_CANDIDATE_LEDGER"
CANONICAL_STATUS = "ADVISORY_ONLY"
UPSTREAM_LANE_ID = "P96_RESEARCH_FOLD_VALIDATION_PLAN"
RECOMMENDED_NEXT_LANE_ON_PASS = "P98_RESEARCH_SHADOW_STABILIZATION_PROOF_PLAN"

REQUIRED_P96_ARTIFACT_TYPE = "ResearchFoldValidationPlan.v1"
REQUIRED_P96_RECOMMENDATION = LANE_ID

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

STABILIZATION_REQUIREMENTS: tuple[str, ...] = (
    "12-run invariance proof required",
    "authority-lock invariance proof required",
    "NOT_COMPUTABLE failure proof required",
    "AAL-Viz projection-only proof required",
    "cross-drop conflict scan required",
    "operator review hold required",
)

BOUNDARY_RULES: tuple[str, ...] = (
    "hidden_intent_is_never_known_intent",
    "proactivity_is_never_autonomous_execution",
    "intent_graph_dependency_is_never_confirmed_intent",
    "endpoint_constraint_is_never_known_goal",
    "calibration_projection_is_never_forecast_weight_mutation",
    "aal_viz_is_projection_only",
    "candidate_ledger_is_not_implementation_authority",
)

_DROP_ORDER: dict[str, int] = {
    "DROP006": 0,
    "DROP007": 1,
}

_CANDIDATE_DEFINITIONS: tuple[
    tuple[str, str, tuple[str, ...], tuple[str, ...]],
    ...,
] = (
    (
        "DROP006",
        "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER",
        (
            "Skill Runtime Ontology",
            "Agent Trace",
            "Oracle Signal Layer",
            "YGGDRASIL graph runtime",
        ),
        (
            "IndirectDependencyTrace.v1",
            "BehavioralIntentGraph.v1",
            "DenoisedScenarioFrame.v1",
        ),
    ),
    (
        "DROP006",
        "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
        (
            "Recursive Cognition & Replay Governance",
            "Skill Runtime Ontology",
            "Oracle Signal Layer",
        ),
        (
            "IntendedEndpointConstraint.v1",
            "InductivePlanningTrace.v1",
            "BlindAlleyPruningSignal.v1",
        ),
    ),
    (
        "DROP006",
        "DROP006C_SURVIVAL_CALIBRATION_GOVERNANCE_LAYER",
        (
            "PSE calibration surfaces",
            "Oracle Signal Layer validation",
            "Calibration ledger extensions",
        ),
        (
            "IsotonicCalibrationProjection.v1",
            "DoubleRobustCalibrationGate.v1",
            "MonotoneRiskTimeProjection.v1",
        ),
    ),
    (
        "DROP007",
        "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
        (
            "Situation Runtime & Proactive Coordination",
            "Skill Runtime Ontology",
            "Agent Trace",
            "AAL-Viz operator projection",
        ),
        (
            "HiddenIntentCandidate.v1",
            "ProactiveResolutionTrace.v1",
            "CrossSessionDependencyGraph.v1",
            "OperatorInterruptibilityGate.v1",
        ),
    ),
    (
        "DROP007",
        "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_LAYER",
        (
            "Recursive Cognition & Replay Governance",
            "Phase Percolation Engine",
            "YGGDRASIL topology",
            "Narrative Topology & Belief-Graph Dynamics",
        ),
        (
            "CoordinationThreshold.v1",
            "NestedInformationHierarchy.v1",
            "SymbolicCompressionTransition.v1",
            "NoisyCoordinationConstraint.v1",
        ),
    ),
    (
        "DROP007",
        "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_LAYER",
        (
            "Situation Runtime & Proactive Coordination",
            "Drop 006 Intent Graph Behavioral Logic Layer",
            "Skill Runtime Ontology",
            "AAL-Viz projection",
        ),
        (
            "InterleavedIntentTrace.v1",
            "ContextualInterventionWindow.v1",
            "SituationContinuityFrame.v1",
            "TrajectoryNoiseFrame.v1",
        ),
    ),
)


def _validate_p96_packet(p96_packet: Any) -> list[str]:
    if p96_packet is None:
        return ["p96_packet_missing"]
    if not isinstance(p96_packet, dict):
        return ["p96_packet_malformed:not_a_dict"]

    reasons: list[str] = []

    if p96_packet.get("artifact_type") != REQUIRED_P96_ARTIFACT_TYPE:
        reasons.append(f"p96_artifact_type_mismatch:{p96_packet.get('artifact_type')!r}")
    if p96_packet.get("lane_id") != UPSTREAM_LANE_ID:
        reasons.append(f"p96_lane_id_mismatch:{p96_packet.get('lane_id')!r}")
    if p96_packet.get("canonical_status") != CANONICAL_STATUS:
        reasons.append(
            f"p96_canonical_status_mismatch:{p96_packet.get('canonical_status')!r}"
        )
    if p96_packet.get("advisory_only") is not True:
        reasons.append("p96_advisory_only_not_true")
    if p96_packet.get("projection_only") is not True:
        reasons.append("p96_projection_only_not_true")

    p96_status = p96_packet.get("status")
    if p96_status != "PASS":
        reasons.append(f"p96_status_not_pass:{p96_status!r}")
    elif p96_packet.get("recommended_next_lane") != REQUIRED_P96_RECOMMENDATION:
        reasons.append(
            "p96_recommended_next_lane_invalid:"
            f"{p96_packet.get('recommended_next_lane')!r}"
        )

    structured_fields: tuple[tuple[str, type[Any]], ...] = (
        ("fixture_plan", list),
        ("positive_proof_packet_plan", dict),
        ("negative_failure_proof_packet_plan", dict),
        ("operator_review_requirements", list),
        ("aal_viz_projection_constraints", list),
        ("provenance", dict),
    )
    for field_name, expected_type in structured_fields:
        if not isinstance(p96_packet.get(field_name), expected_type):
            reasons.append(f"p96_{field_name}_malformed")

    authority_locks = p96_packet.get("authority_locks")
    if not isinstance(authority_locks, dict):
        reasons.append("p96_authority_locks_malformed")
    else:
        drifted = [
            key
            for key in AUTHORITY_LOCK_KEYS
            if authority_locks.get(key) is not False
        ]
        if drifted:
            reasons.append(f"p96_authority_drift_detected:{sorted(drifted)!r}")

    return reasons


def _build_subsystem_candidates() -> list[dict[str, Any]]:
    candidates = [
        {
            "drop_id": drop_id,
            "candidate_id": candidate_id,
            "status": "SHADOW_CANDIDATE_ONLY",
            "primary_targets": list(primary_targets),
            "candidate_contracts": list(candidate_contracts),
        }
        for drop_id, candidate_id, primary_targets, candidate_contracts in _CANDIDATE_DEFINITIONS
    ]
    return sorted(
        candidates,
        key=lambda candidate: (
            _DROP_ORDER[candidate["drop_id"]],
            candidate["candidate_id"],
        ),
    )


def _build_target_subsystems(
    subsystem_candidates: list[dict[str, Any]],
) -> list[str]:
    seen: set[str] = set()
    targets: list[str] = []
    for candidate in subsystem_candidates:
        for target in candidate["primary_targets"]:
            if target not in seen:
                seen.add(target)
                targets.append(target)
    return targets


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def build_research_derived_subsystem_candidate_ledger(
    *,
    p96_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    not_computable_reasons = _validate_p96_packet(p96_packet)

    if not_computable_reasons:
        status = "NOT_COMPUTABLE"
        candidate_ledger_status = "NOT_COMPUTABLE"
        subsystem_candidates: list[dict[str, Any]] = []
        target_subsystems: list[str] = []
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_next_lane_reason = (
            "P96 upstream validation planning is missing, malformed, non-pass, "
            "structurally invalid, or contains authority drift; candidate ledger "
            "generation cannot proceed."
        )
    else:
        status = "PASS"
        candidate_ledger_status = "READY"
        subsystem_candidates = _build_subsystem_candidates()
        target_subsystems = _build_target_subsystems(subsystem_candidates)
        recommended_next_lane = RECOMMENDED_NEXT_LANE_ON_PASS
        recommended_next_lane_reason = (
            "P97 candidate ledger is deterministic, advisory-only, and projection-only; "
            "proceed to P98 research shadow stabilization proof planning."
        )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "lane_id": LANE_ID,
        "status": status,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_validation_plan_status": (
            p96_packet.get("status") if isinstance(p96_packet, dict) else None
        ),
        "candidate_ledger_status": candidate_ledger_status,
        "subsystem_candidates": subsystem_candidates,
        "target_subsystems": target_subsystems,
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "stabilization_requirements": list(STABILIZATION_REQUIREMENTS),
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "not_computable_reasons": not_computable_reasons,
        "provenance": {
            "source": "p96_research_fold_validation_plan",
            "mapping_method": "deterministic_candidate_ledger_projection",
            "drop_order": ["DROP006", "DROP007"],
            "candidate_ordering": "drop_order_then_lexicographic_candidate_id",
            "p96_status": p96_packet.get("status") if isinstance(p96_packet, dict) else None,
            "p96_artifact_type": (
                p96_packet.get("artifact_type") if isinstance(p96_packet, dict) else None
            ),
            "boundary_rules": list(BOUNDARY_RULES),
            "gated_recommendation_rule": "recommend_p98_only_when_status_pass",
        },
    }
    return _finalize(packet_base)


def write_research_derived_subsystem_candidate_ledger(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
