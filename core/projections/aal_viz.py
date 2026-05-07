"""AAL-Viz projection packet builder for ABRAXAS v2.0."""

from __future__ import annotations

from typing import Any

from core.governance.authority import locked_authority
from core.governance.doctrine import SCHEMA_VERSION_AAL_VIZ


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
) -> dict[str, Any]:
    projection_only = True
    inference_authority = False

    total = registry.get("pipeline_count", 0)
    compliant = sum(1 for r in validation if r.get("status") == "doctrine_compliant")
    repair = sum(1 for r in validation if r.get("status") == "repair_required")
    not_computable = sum(1 for r in validation if r.get("status") == "not_computable")

    panels = [
        {
            "pipeline_id": r["pipeline_id"],
            "status": r["status"],
            "gate_summary": [
                {
                    "gate": g.get("gate_id", g.get("gate")),
                    "status": g.get(
                        "status", "passed" if g.get("passed") else "failed"
                    ),
                }
                for g in r.get("gate_results", [])
            ],
        }
        for r in validation
    ]
    continuity = continuity or {}
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
        "continuity_summary": {
            "prior_scripts_present": not continuity.get("missing_scripts", [1]),
            "prior_artifacts_present": not continuity.get("missing_artifacts", [1]),
            "prior_routes_present": not continuity.get("missing_routes", [1]),
            "continuity_failures": len(continuity.get("missing_scripts", []))
            + len(continuity.get("missing_artifacts", []))
            + len(continuity.get("missing_routes", [])),
        },
        "doctrine_posture_summary": doctrine_posture_summary
        or {
            "doctrine_compliant": compliant,
            "repair_required": repair,
            "legacy_contract_posture": 0,
            "not_computable": not_computable,
            "failed": 0,
            "seal_recommendation": "repair" if repair else "seal",
        },
        "panels": panels,
        "sandbox_summary": sandbox_summary
        or {
            "active_branches": 0,
            "stable_branches": 0,
            "failed_branches": 0,
            "replay_matches": 0,
            "convergence_score": 0.0,
            "rollback_ready": 0,
            "pending_reviews": 0,
            "divergence_events": 0,
        },
        "oracle_summary": oracle_summary
        or {
            "intake_runs": 0,
            "stabilized_intakes": 0,
            "replay_matches": 0,
            "unresolved_conflicts": 0,
            "lineage_depth": 0,
            "replay_failures": 0,
            "pending_reviews": 0,
        },
        "forecast_summary": forecast_summary
        or {
            "candidate_forecasts": 0,
            "calibrated_forecasts": 0,
            "replay_matches": 0,
            "unresolved_bindings": 0,
            "calibration_average": 0.0,
            "stabilization_state": "unstable",
            "pending_reviews": 0,
        },
        "brier_summary": brier_summary
        or {
            "scored_forecasts": 0,
            "average_brier": 0.0,
            "calibration_average": 0.0,
            "reliability_score": 0.0,
            "replay_matches": 0,
            "replay_failures": 0,
            "stabilization_state": "unstable",
            "pending_reviews": 0,
        },
        "drift_summary": drift_summary
        or {
            "drift_proposals": 0,
            "active_overlays": 0,
            "average_overlay_weight": 0.0,
            "drift_confidence": 0.0,
            "replay_matches": 0,
            "replay_failures": 0,
            "stabilization_state": "unstable",
            "pending_reviews": 0,
        },
        "milestone_summary": milestone_summary
        or {
            "active_milestone": "unknown",
            "stabilized_milestones": [],
            "latest_stable_hash": "unknown",
            "lineage_depth": 0,
            "milestone_validator_status": "not_computable",
        },
        "canary_summary": canary_summary
        or {
            "active_canary_overlays": 0,
            "replay_matches": 0,
            "replay_failures": 0,
            "rollback_ready": 0,
            "rollback_events": 0,
            "stabilization_state": "unstable",
            "blocked_routes": 0,
            "pending_reviews": 0,
        },
        "overlay_observability_summary": overlay_observability_summary
        or {
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
        "canary_scheduler_summary": canary_scheduler_summary
        or {
            "policy_packets": 0,
            "eligible_overlays": 0,
            "blocked_overlays": 0,
            "proposed_schedules": 0,
            "replay_matches": 0,
            "replay_failures": 0,
            "pending_reviews": 0,
            "blocked_reasons": [],
        },
        "canary_promotion_summary": canary_promotion_summary
        or {
            "promotion_candidates": 0,
            "eligible_for_review": 0,
            "denied_candidates": 0,
            "replay_failures": 0,
            "critical_diagnostics": 0,
            "rollback_ready": 0,
            "pending_reviews": 0,
            "denial_reasons": [],
        },
        "overlay_governance_summary": overlay_governance_summary
        or {
            "governance_events": 0,
            "ledger_depth": 0,
            "continuity_score": 0.0,
            "missing_event_types": [],
            "replay_matches": 0,
            "replay_failures": 0,
            "critical_diagnostics": 0,
            "pending_reviews": 0,
        },
        "overlay_risk_summary": overlay_risk_summary
        or {
            "aggregate_risk": 0.0,
            "cliff_risk": 0.0,
            "saturation_risk": 0.0,
            "replay_instability": 0,
            "propagation_depth": 0,
            "pending_reviews": 0,
            "critical_diagnostics": 0,
        },
        "overlay_topology_summary": overlay_topology_summary
        or {
            "overlay_nodes": 0,
            "overlay_edges": 0,
            "graph_density": 0.0,
            "coupling_score": 0.0,
            "bottlenecks": 0,
            "rollback_path_depth": 0,
            "propagation_depth": 0,
            "critical_diagnostics": 0,
        },
        "overlay_containment_summary": overlay_containment_summary
        or {
            "containment_recommendations": 0,
            "critical_recommendations": 0,
            "active_triggers": 0,
            "affected_overlays": 0,
            "containment_scope_depth": 0,
            "replay_matches": 0,
            "critical_diagnostics": 0,
            "pending_reviews": 0,
        },
        "overlay_resolution_summary": overlay_resolution_summary
        or {
            "total_resolution_events": 0,
            "unresolved_events": 0,
            "critical_unresolved_events": 0,
            "replay_failures": 0,
            "rollback_ready_count": 0,
            "blocked_resolution_count": 0,
            "closure_ready": False,
            "pending_reviews": 0,
        },
        "overlay_readiness_summary": overlay_readiness_summary
        or {
            "aggregate_readiness_score": 0.0,
            "readiness_band": "blocked",
            "component_scores": {},
            "blocked_components": [],
            "replay_matches": 0,
            "rollback_ready": 0,
            "critical_diagnostics": 0,
            "pending_reviews": 0,
        },
        "overlay_firewall_summary": overlay_firewall_summary
        or {
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
        "operator_queue_summary": operator_queue_summary
        or {
            "pending_requests": 0,
            "deferred_requests": 0,
            "denied_requests": 0,
            "review_only_approved_requests": 0,
            "unresolved_diagnostics": 1,
            "replay_matches": False,
            "continuity_status": "not_computable",
            "authority_locked": False,
        },
        "review_continuity_summary": review_continuity_summary
        or {
            "continuity_chains": 0,
            "deferred_sequences": 0,
            "denied_sequences": 0,
            "unresolved_diagnostics": 1,
            "replay_matches": False,
            "continuity_integrity": False,
            "authority_locked": False,
        },
        "review_resolution_summary": review_resolution_summary
        or {
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
        "manual_execution_summary": manual_execution_summary
        or {
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
        "manual_execution_receipt_summary": manual_execution_receipt_summary
        or {
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
        "manual_action_custody_summary": manual_action_custody_summary
        or {
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
        "authority": locked_authority(),
    }
    return packet
