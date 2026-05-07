"""AAL-Viz projection packet builder for ABRAXAS v2.0."""

from __future__ import annotations

from typing import Any

from core.governance.authority import locked_authority
from core.governance.doctrine import SCHEMA_VERSION_AAL_VIZ


def _with_fallback(summary: dict[str, Any] | None, fallback: dict[str, Any]) -> dict[str, Any]:
    return summary if summary is not None else fallback


def _build_gate_summary(validation: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "pipeline_id": result["pipeline_id"],
            "status": result["status"],
            "gate_summary": [
                {
                    "gate": gate.get("gate_id", gate.get("gate")),
                    "status": gate.get(
                        "status",
                        "passed" if gate.get("passed") else "failed",
                    ),
                }
                for gate in result.get("gate_results", [])
            ],
        }
        for result in validation
    ]


def build_projection_packet(
    registry: dict[str, Any],
    validation: list[dict[str, Any]],
    queue: dict[str, Any],
    continuity: dict[str, Any] | None = None,
    sandbox_summary: dict[str, Any] | None = None,
    doctrine_posture_summary: dict[str, Any] | None = None,
    oracle_summary: dict[str, Any] | None = None,
    forecast_summary: dict[str, Any] | None = None,
    brier_summary: dict[str, Any] | None = None,
    drift_summary: dict[str, Any] | None = None,
    milestone_summary: dict[str, Any] | None = None,
    canary_summary: dict[str, Any] | None = None,
    overlay_observability_summary: dict[str, Any] | None = None,
    canary_scheduler_summary: dict[str, Any] | None = None,
    canary_promotion_summary: dict[str, Any] | None = None,
    overlay_governance_summary: dict[str, Any] | None = None,
    overlay_risk_summary: dict[str, Any] | None = None,
    overlay_topology_summary: dict[str, Any] | None = None,
    overlay_containment_summary: dict[str, Any] | None = None,
    overlay_resolution_summary: dict[str, Any] | None = None,
    overlay_readiness_summary: dict[str, Any] | None = None,
    overlay_firewall_summary: dict[str, Any] | None = None,
    operator_queue_summary: dict[str, Any] | None = None,
    review_continuity_summary: dict[str, Any] | None = None,
    review_resolution_summary: dict[str, Any] | None = None,
    manual_execution_summary: dict[str, Any] | None = None,
    manual_execution_receipt_summary: dict[str, Any] | None = None,
    manual_action_custody_summary: dict[str, Any] | None = None,
    external_action_proposal_summary: dict[str, Any] | None = None,
    proposal_sandbox_routing_summary: dict[str, Any] | None = None,
    proposal_sandbox_evaluation_summary: dict[str, Any] | None = None,
    proposal_decision_bridge_summary: dict[str, Any] | None = None,
    human_decision_ledger_summary: dict[str, Any] | None = None,
    human_decision_continuity_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    projection_only = True
    inference_authority = False

    total = registry.get("pipeline_count", 0)
    compliant = sum(1 for result in validation if result.get("status") == "doctrine_compliant")
    repair = sum(1 for result in validation if result.get("status") == "repair_required")
    not_computable = sum(1 for result in validation if result.get("status") == "not_computable")

    continuity = continuity or {}
    continuity_summary = {
        "prior_scripts_present": not continuity.get("missing_scripts", [1]),
        "prior_artifacts_present": not continuity.get("missing_artifacts", [1]),
        "prior_routes_present": not continuity.get("missing_routes", [1]),
        "continuity_failures": len(continuity.get("missing_scripts", []))
        + len(continuity.get("missing_artifacts", []))
        + len(continuity.get("missing_routes", [])),
    }

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION_AAL_VIZ,
        "projection_only": projection_only,
        "inference_authority": inference_authority,
        "summary": {
            "total_pipelines": total,
            "doctrine_compliant": compliant,
            "repair_required": repair,
            "not_computable": not_computable,
            "queue_items": queue.get("queue_item_count", 0),
        },
        "continuity_summary": continuity_summary,
        "doctrine_posture_summary": _with_fallback(
            doctrine_posture_summary,
            {
                "doctrine_compliant": compliant,
                "repair_required": repair,
                "legacy_contract_posture": 0,
                "not_computable": not_computable,
                "failed": 0,
                "seal_recommendation": "repair" if repair else "seal",
            },
        ),
        "panels": _build_gate_summary(validation),
        "sandbox_summary": _with_fallback(
            sandbox_summary,
            {
                "active_branches": 0,
                "stable_branches": 0,
                "failed_branches": 0,
                "replay_matches": 0,
                "convergence_score": 0.0,
                "rollback_ready": 0,
                "pending_reviews": 0,
                "divergence_events": 0,
            },
        ),
        "oracle_summary": _with_fallback(
            oracle_summary,
            {
                "intake_runs": 0,
                "stabilized_intakes": 0,
                "replay_matches": 0,
                "unresolved_conflicts": 0,
                "lineage_depth": 0,
                "replay_failures": 0,
                "pending_reviews": 0,
            },
        ),
        "forecast_summary": _with_fallback(
            forecast_summary,
            {
                "candidate_forecasts": 0,
                "calibrated_forecasts": 0,
                "replay_matches": 0,
                "unresolved_bindings": 0,
                "calibration_average": 0.0,
                "stabilization_state": "unstable",
                "pending_reviews": 0,
            },
        ),
        "brier_summary": _with_fallback(
            brier_summary,
            {
                "scored_forecasts": 0,
                "average_brier": 0.0,
                "calibration_average": 0.0,
                "reliability_score": 0.0,
                "replay_matches": 0,
                "replay_failures": 0,
                "stabilization_state": "unstable",
                "pending_reviews": 0,
            },
        ),
        "drift_summary": _with_fallback(
            drift_summary,
            {
                "drift_proposals": 0,
                "active_overlays": 0,
                "average_overlay_weight": 0.0,
                "drift_confidence": 0.0,
                "replay_matches": 0,
                "replay_failures": 0,
                "stabilization_state": "unstable",
                "pending_reviews": 0,
            },
        ),
        "milestone_summary": _with_fallback(
            milestone_summary,
            {
                "active_milestone": "unknown",
                "stabilized_milestones": [],
                "latest_stable_hash": "unknown",
                "lineage_depth": 0,
                "milestone_validator_status": "not_computable",
            },
        ),
        "canary_summary": _with_fallback(
            canary_summary,
            {
                "active_canary_overlays": 0,
                "replay_matches": 0,
                "replay_failures": 0,
                "rollback_ready": 0,
                "rollback_events": 0,
                "stabilization_state": "unstable",
                "blocked_routes": 0,
                "pending_reviews": 0,
            },
        ),
        "overlay_observability_summary": _with_fallback(
            overlay_observability_summary,
            {
                "fusion_packets": 0,
                "replay_matches": 0,
                "replay_failures": 0,
                "rollback_count": 0,
                "blocked_routes": 0,
                "diagnostic_count": 0,
                "critical_diagnostics": 0,
                "stability_state": "unstable",
                "pending_reviews": 0,
            },
        ),
        "canary_scheduler_summary": _with_fallback(
            canary_scheduler_summary,
            {
                "policy_packets": 0,
                "eligible_overlays": 0,
                "blocked_overlays": 0,
                "proposed_schedules": 0,
                "replay_matches": 0,
                "replay_failures": 0,
                "pending_reviews": 0,
                "blocked_reasons": [],
            },
        ),
        "canary_promotion_summary": _with_fallback(
            canary_promotion_summary,
            {
                "promotion_candidates": 0,
                "eligible_for_review": 0,
                "denied_candidates": 0,
                "replay_failures": 0,
                "critical_diagnostics": 0,
                "rollback_ready": 0,
                "pending_reviews": 0,
                "denial_reasons": [],
            },
        ),
        "overlay_governance_summary": _with_fallback(
            overlay_governance_summary,
            {
                "governance_events": 0,
                "ledger_depth": 0,
                "continuity_score": 0.0,
                "missing_event_types": [],
                "replay_matches": 0,
                "replay_failures": 0,
                "critical_diagnostics": 0,
                "pending_reviews": 0,
            },
        ),
        "overlay_risk_summary": _with_fallback(
            overlay_risk_summary,
            {
                "aggregate_risk": 0.0,
                "cliff_risk": 0.0,
                "saturation_risk": 0.0,
                "replay_instability": 0,
                "propagation_depth": 0,
                "pending_reviews": 0,
                "critical_diagnostics": 0,
            },
        ),
        "overlay_topology_summary": _with_fallback(
            overlay_topology_summary,
            {
                "overlay_nodes": 0,
                "overlay_edges": 0,
                "graph_density": 0.0,
                "coupling_score": 0.0,
                "bottlenecks": 0,
                "rollback_path_depth": 0,
                "propagation_depth": 0,
                "critical_diagnostics": 0,
            },
        ),
        "overlay_containment_summary": _with_fallback(
            overlay_containment_summary,
            {
                "containment_recommendations": 0,
                "critical_recommendations": 0,
                "active_triggers": 0,
                "affected_overlays": 0,
                "containment_scope_depth": 0,
                "replay_matches": 0,
                "critical_diagnostics": 0,
                "pending_reviews": 0,
            },
        ),
        "overlay_resolution_summary": _with_fallback(
            overlay_resolution_summary,
            {
                "total_resolution_events": 0,
                "unresolved_events": 0,
                "critical_unresolved_events": 0,
                "replay_failures": 0,
                "rollback_ready_count": 0,
                "blocked_resolution_count": 0,
                "closure_ready": False,
                "pending_reviews": 0,
            },
        ),
        "overlay_readiness_summary": _with_fallback(
            overlay_readiness_summary,
            {
                "aggregate_readiness_score": 0.0,
                "readiness_band": "blocked",
                "component_scores": {},
                "blocked_components": [],
                "replay_matches": 0,
                "rollback_ready": 0,
                "critical_diagnostics": 0,
                "pending_reviews": 0,
            },
        ),
        "overlay_firewall_summary": _with_fallback(
            overlay_firewall_summary,
            {
                "firewall_status": "not_computable",
                "blocked_reasons": ["missing_firewall_artifact"],
                "rollback_ready": False,
                "replay_matches": False,
                "critical_diagnostics": 1,
                "containment_restrictions": [],
                "governance_continuity": 0.0,
                "operator_review_required": True,
                "projection_only": True,
                "inference_authority": False,
            },
        ),
        "operator_queue_summary": _with_fallback(
            operator_queue_summary,
            {
                "pending_requests": 0,
                "deferred_requests": 0,
                "denied_requests": 0,
                "review_only_approved_requests": 0,
                "unresolved_diagnostics": 1,
                "replay_matches": False,
                "continuity_status": "not_computable",
                "authority_locked": False,
            },
        ),
        "external_action_proposal_summary": _with_fallback(
            external_action_proposal_summary,
            {
                "proposal_count": 0,
                "blocked_proposals": 0,
                "readiness_posture": 0.0,
                "unresolved_diagnostics": 0,
                "replay_matches": False,
                "governance_restricted": True,
                "authority_locked": True,
                "projection_only": True,
                "inference_authority": False,
            },
        ),
        "proposal_sandbox_routing_summary": _with_fallback(
            proposal_sandbox_routing_summary,
            {
                "route_count": 0,
                "blocked_routes": 0,
                "eligible_routes": 0,
                "lane_type": "not_computable",
                "unresolved_diagnostics": 0,
                "replay_matches": False,
                "governance_restricted": True,
                "authority_locked": True,
            },
        ),
        "proposal_sandbox_evaluation_summary": _with_fallback(
            proposal_sandbox_evaluation_summary,
            {
                "evaluation_count": 0,
                "blocked_evaluations": 0,
                "evaluation_score": 0.0,
                "unresolved_diagnostics": 0,
                "replay_matches": False,
                "governance_restricted": True,
                "authority_locked": True,
            },
        ),
        "proposal_decision_bridge_summary": _with_fallback(
            proposal_decision_bridge_summary,
            {
                "bridge_count": 0,
                "blocked_bridges": 0,
                "decision_readiness": 0.0,
                "unresolved_diagnostics": 0,
                "replay_matches": False,
                "governance_restricted": True,
                "authority_locked": True,
            },
        ),
        "human_decision_ledger_summary": _with_fallback(
            human_decision_ledger_summary,
            {
                "decision_count": 0,
                "deferred_decisions": 0,
                "blocked_decisions": 0,
                "unresolved_diagnostics": 0,
                "replay_matches": False,
                "governance_restricted": True,
                "authority_locked": True,
            },
        ),
        "human_decision_continuity_summary": _with_fallback(
            human_decision_continuity_summary,
            {
                "continuity_chain_count": 0,
                "deferred_chains": 0,
                "blocked_chains": 0,
                "unresolved_diagnostics": 0,
                "replay_matches": False,
                "governance_restricted": True,
                "authority_locked": True,
            },
        ),
        "review_continuity_summary": _with_fallback(
            review_continuity_summary,
            {
                "continuity_chains": 0,
                "deferred_sequences": 0,
                "denied_sequences": 0,
                "unresolved_diagnostics": 1,
                "replay_matches": False,
                "continuity_integrity": False,
                "authority_locked": False,
            },
        ),
        "review_resolution_summary": _with_fallback(
            review_resolution_summary,
            {
                "resolution_posture": "unresolved",
                "unresolved_blockers": 1,
                "critical_blockers": 1,
                "closure_ready": False,
                "replay_matches": False,
                "pending_reviews": 1,
                "authority_locked": False,
                "projection_only": True,
                "inference_authority": False,
            },
        ),
        "manual_execution_summary": _with_fallback(
            manual_execution_summary,
            {
                "authorization_status": "not_authorized",
                "envelope_status": "not_computable",
                "eligible_for_manual_review": False,
                "unresolved_blockers": 1,
                "forbidden_actions": ["execute", "activate", "deploy"],
                "replay_matches": False,
                "acknowledgement_present": False,
                "authority_locked": False,
                "projection_only": True,
                "inference_authority": False,
            },
        ),
        "manual_execution_receipt_summary": _with_fallback(
            manual_execution_receipt_summary,
            {
                "total_receipts": 0,
                "pending_receipts": 1,
                "blocked_receipts": 0,
                "invalid_receipts": 0,
                "replay_matches": False,
                "unresolved_diagnostics": 1,
                "authority_locked": False,
                "projection_only": True,
                "inference_authority": False,
            },
        ),
        "manual_action_custody_summary": _with_fallback(
            manual_action_custody_summary,
            {
                "custody_status": "custody_pending",
                "handoff_count": 0,
                "acknowledgement_count": 0,
                "escalation_required": True,
                "unresolved_diagnostics": 1,
                "replay_matches": False,
                "authority_locked": False,
                "projection_only": True,
                "inference_authority": False,
            },
        ),
        "authority": locked_authority(),
    }
    return packet
