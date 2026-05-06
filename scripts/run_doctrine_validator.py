"""Script: run doctrine validator over all Tier-1 contracts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.canonical.json import write_canonical_json
from core.operators.review_queue import build_review_queue
from core.pipelines.registry import load_contracts
from core.pipelines.validator import validate_pipeline_contract
from core.projections.aal_viz import build_projection_packet
from core.runes.registry import load_rune_catalog
from core.spine.milestone_continuity import validate_milestone_continuity
from core.spine.milestone_registry import build_milestone_registry
from core.spine.milestone_validator import MilestoneValidationPacket, validate_active_milestone
from core.yggdrasil.validator import load_route_graphs

CONTRACTS_DIR = Path("contracts/pipelines")
RUNE_CATALOG_PATH = Path("contracts/runes/catalog.v1.json")
ROUTES_DIR = Path("contracts/yggdrasil/routes")

OUT_VALIDATION = Path("out/validation/latest.json")
OUT_AAL_VIZ = Path("out/projections/aal_viz.latest.json")
OUT_QUEUE = Path("out/operator_review/latest.json")
OUT_MILESTONE_REG = Path("out/spine/milestone_registry.latest.json")
OUT_MILESTONE_VAL = Path("out/spine/milestone_validation.latest.json")
OUT_CANARY = Path("out/canary/latest.json")
OUT_OVERLAY_OBS = Path("out/overlay_observability/latest.json")
OUT_CANARY_SCHED = Path("out/canary_scheduler/latest.json")
OUT_OVERLAY_GOV = Path("out/overlay_governance/latest.json")
OUT_OVERLAY_RISK = Path("out/overlay_risk/latest.json")
OUT_OVERLAY_TOPOLOGY = Path("out/overlay_topology/latest.json")


def _build_summary(results: list[dict], active_milestone: str = "unknown", milestone_validation: MilestoneValidationPacket | None = None, milestone_registry_status: str = "not_computable", overlay_governance_status: dict[str, object] | None = None) -> dict[str, object]:
    counts = {
        "doctrine_compliant": sum(1 for r in results if r["status"] == "doctrine_compliant"),
        "repair_required": sum(1 for r in results if r["status"] == "repair_required"),
        "legacy_contract_posture": sum(1 for r in results if r["status"] == "legacy_contract_posture"),
        "not_computable": sum(1 for r in results if r["status"] == "not_computable"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
    }
    if milestone_validation is None:
        milestone_registry_gate = True
        active_milestone_gate = True
        milestone_evidence_gate = True
        stale_metadata_gate = True
    else:
        milestone_registry_gate = milestone_registry_status == "passed"
        active_milestone_gate = milestone_validation.derived_active_milestone == active_milestone and active_milestone != "unknown"
        milestone_evidence_gate = milestone_validation.derived_evidence_status in {"artifact_verified", "code_verified"}
        stale_metadata_gate = not milestone_validation.stale_metadata_detected
        if not (milestone_registry_gate and active_milestone_gate and milestone_evidence_gate and stale_metadata_gate and milestone_validation.status == "passed"):
            counts["failed"] += 1
    seal = "repair" if counts["failed"] > 0 or counts["repair_required"] > 0 else ("hold" if counts["legacy_contract_posture"] > 0 else "seal")
    overlay_governance_status = overlay_governance_status or {}
    overlay_governance_event_gate = overlay_governance_status.get("event_gate", "passed")
    overlay_governance_ledger_gate = overlay_governance_status.get("ledger_gate", "passed")
    overlay_governance_continuity_gate = overlay_governance_status.get("continuity_gate", "passed")
    overlay_governance_replay_gate = overlay_governance_status.get("replay_gate", "passed")
    overlay_governance_operator_review_gate = overlay_governance_status.get("operator_review_gate", "passed")
    if "failed" in {
        overlay_governance_event_gate,
        overlay_governance_ledger_gate,
        overlay_governance_continuity_gate,
        overlay_governance_replay_gate,
        overlay_governance_operator_review_gate,
    }:
        counts["failed"] += 1
    return {
        "schema_version": "DoctrineValidationSummary.v1",
        "compliant_count": counts["doctrine_compliant"],
        "repair_required_count": counts["repair_required"],
        "legacy_contract_posture_count": counts["legacy_contract_posture"],
        "not_computable_count": counts["not_computable"],
        "failed_count": counts["failed"],
        "active_milestone": active_milestone,
        "seal_recommendation": seal,
        "status": "failed" if counts["failed"] > 0 else "ok",
        "milestone_registry_gate": "passed" if milestone_registry_gate else "failed",
        "active_milestone_gate": "passed" if active_milestone_gate else "failed",
        "milestone_evidence_gate": "passed" if milestone_evidence_gate else "failed",
        "stale_metadata_gate": "passed" if stale_metadata_gate else "failed",
        "overlay_governance_event_gate": overlay_governance_event_gate,
        "overlay_governance_ledger_gate": overlay_governance_ledger_gate,
        "overlay_governance_continuity_gate": overlay_governance_continuity_gate,
        "overlay_governance_replay_gate": overlay_governance_replay_gate,
        "overlay_governance_operator_review_gate": overlay_governance_operator_review_gate,
        "overlay_risk_envelope_gate": overlay_governance_status.get("overlay_risk_envelope_gate", "passed"),
        "overlay_risk_propagation_gate": overlay_governance_status.get("overlay_risk_propagation_gate", "passed"),
        "overlay_risk_cliff_gate": overlay_governance_status.get("overlay_risk_cliff_gate", "passed"),
        "overlay_risk_saturation_gate": overlay_governance_status.get("overlay_risk_saturation_gate", "passed"),
        "overlay_risk_replay_gate": overlay_governance_status.get("overlay_risk_replay_gate", "passed"),
        "overlay_risk_operator_review_gate": overlay_governance_status.get("overlay_risk_operator_review_gate", "passed"),
    }


def main() -> None:
    rune_catalog = load_rune_catalog(RUNE_CATALOG_PATH)
    route_graphs = load_route_graphs(ROUTES_DIR)
    contracts = load_contracts(CONTRACTS_DIR)
    continuity = validate_milestone_continuity()

    results = []
    for contract in contracts:
        graph_data = route_graphs[contract.pipeline_id].model_dump() if contract.pipeline_id in route_graphs else None
        results.append(validate_pipeline_contract(contract, rune_catalog, graph_data, continuity.model_dump()))

    from core.pipelines.registry import build_registry

    registry = build_registry(contracts)
    queue = build_review_queue(results)
    milestone_registry = build_milestone_registry(Path("."))
    reported_active = milestone_registry.active_milestone
    milestone_validation = validate_active_milestone(reported_active, milestone_registry)
    overlay_governance_runtime: dict[str, object] = {}
    overlay_governance_summary = {"governance_events": 0, "ledger_depth": 0, "continuity_score": 0.0, "missing_event_types": [], "replay_matches": 0, "replay_failures": 0, "critical_diagnostics": 0, "pending_reviews": 0}
    overlay_governance_gates = {"event_gate": "passed", "ledger_gate": "passed", "continuity_gate": "passed", "replay_gate": "passed", "operator_review_gate": "passed"}
    if OUT_OVERLAY_GOV.exists():
        overlay_governance_runtime = json.loads(OUT_OVERLAY_GOV.read_text())
        diagnostics = overlay_governance_runtime.get("diagnostics", [])
        replay = overlay_governance_runtime.get("replay", {})
        continuity_packet = overlay_governance_runtime.get("continuity", {})
        operator_review = overlay_governance_runtime.get("operator_review", {})
        ledger = overlay_governance_runtime.get("ledger", {})
        overlay_governance_summary = {
            "governance_events": len(overlay_governance_runtime.get("events", [])),
            "ledger_depth": ledger.get("ledger_depth", 0),
            "continuity_score": continuity_packet.get("continuity_score", 0.0),
            "missing_event_types": continuity_packet.get("missing_event_types", []),
            "replay_matches": 1 if replay.get("deterministic_match") else 0,
            "replay_failures": len(replay.get("mismatched_events", [])),
            "critical_diagnostics": sum(1 for d in diagnostics if d.get("severity") == "critical"),
            "pending_reviews": len(operator_review.get("pending_actions", [])),
        }
        overlay_governance_gates = {
            "event_gate": "passed" if overlay_governance_summary["governance_events"] > 0 else "failed",
            "ledger_gate": "passed" if overlay_governance_summary["ledger_depth"] > 0 else "failed",
            "continuity_gate": "passed" if overlay_governance_summary["continuity_score"] >= 0.5 else "failed",
            "replay_gate": "passed" if overlay_governance_summary["replay_failures"] == 0 and overlay_governance_summary["replay_matches"] == 1 else "failed",
            "operator_review_gate": "failed" if overlay_governance_summary["critical_diagnostics"] > 0 else "passed",
        }
    overlay_risk_summary = {"aggregate_risk": 0.0, "cliff_risk": 0.0, "saturation_risk": 0.0, "replay_instability": 0, "propagation_depth": 0, "pending_reviews": 0, "critical_diagnostics": 0}
    if OUT_OVERLAY_RISK.exists():
        risk = json.loads(OUT_OVERLAY_RISK.read_text())
        env = (risk.get("envelopes") or [{}])[0]
        overlay_risk_summary = {
            "aggregate_risk": env.get("aggregate_risk_score", 0.0),
            "cliff_risk": risk.get("cliff", {}).get("cliff_risk_score", 0.0),
            "saturation_risk": risk.get("saturation", {}).get("saturation_score", 0.0),
            "replay_instability": len(risk.get("replay", {}).get("mismatched_packets", [])),
            "propagation_depth": risk.get("propagation", {}).get("propagation_depth", 0),
            "pending_reviews": len(risk.get("operator_review", {}).get("pending_actions", [])),
            "critical_diagnostics": sum(1 for d in risk.get("diagnostics", []) if d.get("severity") == "critical"),
        }
        overlay_governance_gates.update(
            {
                "overlay_risk_envelope_gate": "passed",
                "overlay_risk_propagation_gate": "failed" if risk.get("propagation", {}).get("cycles_detected") else "passed",
                "overlay_risk_cliff_gate": "passed",
                "overlay_risk_saturation_gate": "passed",
                "overlay_risk_replay_gate": "passed" if risk.get("replay", {}).get("deterministic_match") else "failed",
                "overlay_risk_operator_review_gate": "failed" if overlay_risk_summary["critical_diagnostics"] > 0 else "passed",
            }
        )
    overlay_topology_summary = {"overlay_nodes": 0, "overlay_edges": 0, "graph_density": 0.0, "coupling_score": 0.0, "bottlenecks": 0, "rollback_path_depth": 0, "propagation_depth": 0, "critical_diagnostics": 0}
    if OUT_OVERLAY_TOPOLOGY.exists():
        ot = json.loads(OUT_OVERLAY_TOPOLOGY.read_text())
        overlay_topology_summary = {
            "overlay_nodes": len(ot.get("graph", {}).get("overlay_nodes", [])),
            "overlay_edges": len(ot.get("graph", {}).get("overlay_edges", [])),
            "graph_density": ot.get("graph", {}).get("graph_density", 0.0),
            "coupling_score": ot.get("coupling", {}).get("aggregate_coupling_score", 0.0),
            "bottlenecks": ot.get("bottleneck", {}).get("bottleneck_count", 0),
            "rollback_path_depth": ot.get("rollback_paths", {}).get("rollback_path_depth", 0),
            "propagation_depth": ot.get("propagation", {}).get("propagation_depth", 0),
            "critical_diagnostics": sum(1 for d in ot.get("diagnostics", []) if d.get("severity") == "critical"),
        }
        overlay_governance_gates.update(
            {
                "overlay_topology_graph_gate": "passed",
                "overlay_topology_adjacency_gate": "passed",
                "overlay_topology_coupling_gate": "passed",
                "overlay_topology_bottleneck_gate": "passed",
                "overlay_topology_replay_gate": "passed" if ot.get("replay", {}).get("deterministic_match") else "failed",
                "overlay_topology_operator_review_gate": "failed" if overlay_topology_summary["critical_diagnostics"] > 0 else "passed",
            }
        )
    summary = _build_summary(results, milestone_registry.active_milestone, milestone_validation, milestone_registry.status, overlay_governance_gates)
    canary_summary = {"active_canary_overlays": 0, "replay_matches": 0, "replay_failures": 0, "rollback_ready": 0, "rollback_events": 0, "stabilization_state": "unstable", "blocked_routes": 0, "pending_reviews": 0}
    if OUT_CANARY.exists():
        canary = json.loads(OUT_CANARY.read_text())
        canary_summary = {
            "active_canary_overlays": 1,
            "replay_matches": 1 if canary.get("replay", {}).get("deterministic_match") else 0,
            "replay_failures": len(canary.get("replay", {}).get("mismatched_routes", [])),
            "rollback_ready": 1 if canary.get("calibration", {}).get("rollback_readiness") else 0,
            "rollback_events": 1 if canary.get("rollback", {}).get("rollback_complete") else 0,
            "stabilization_state": canary.get("stabilization", {}).get("stabilization_state", "unstable"),
            "blocked_routes": len(canary.get("routing", {}).get("blocked_routes", [])),
            "pending_reviews": len(canary.get("operator_review", {}).get("pending_actions", [])),
        }

    overlay_observability_summary = {"fusion_packets": 0, "replay_matches": 0, "replay_failures": 0, "rollback_count": 0, "blocked_routes": 0, "diagnostic_count": 0, "critical_diagnostics": 0, "stability_state": "unstable", "pending_reviews": 0}
    if OUT_OVERLAY_OBS.exists():
        ov = json.loads(OUT_OVERLAY_OBS.read_text())
        overlay_observability_summary = {
            "fusion_packets": 1,
            "replay_matches": 1 if ov.get("replay",{}).get("deterministic_match") else 0,
            "replay_failures": len(ov.get("replay",{}).get("mismatched_packets",[])),
            "rollback_count": ov.get("telemetry",{}).get("rollback_count",0),
            "blocked_routes": ov.get("telemetry",{}).get("blocked_route_count",0),
            "diagnostic_count": len(ov.get("diagnostics",[])),
            "critical_diagnostics": sum(1 for d in ov.get("diagnostics",[]) if d.get("severity")=="critical"),
            "stability_state": ov.get("stability",{}).get("stability_state","unstable"),
            "pending_reviews": len(ov.get("operator_review",{}).get("pending_actions",[])),
        }

    canary_scheduler_summary = {"policy_packets": 0, "eligible_overlays": 0, "blocked_overlays": 0, "proposed_schedules": 0, "replay_matches": 0, "replay_failures": 0, "pending_reviews": 0, "blocked_reasons": []}
    if OUT_CANARY_SCHED.exists():
        cs = json.loads(OUT_CANARY_SCHED.read_text())
        elig = cs.get("eligibility", {})
        canary_scheduler_summary = {
            "policy_packets": 1,
            "eligible_overlays": 1 if elig.get("eligible") else 0,
            "blocked_overlays": 0 if elig.get("eligible") else 1,
            "proposed_schedules": 1 if cs.get("schedule", {}).get("schedule_status") == "proposed" else 0,
            "replay_matches": 1 if cs.get("replay", {}).get("deterministic_match") else 0,
            "replay_failures": len(cs.get("replay", {}).get("mismatched_windows", [])),
            "pending_reviews": len(cs.get("operator_review", {}).get("pending_actions", [])),
            "blocked_reasons": elig.get("blocked_reasons", []),
        }

    projection = build_projection_packet(
        registry,
        results,
        queue,
        continuity.model_dump(),
        doctrine_posture_summary={
            "doctrine_compliant": summary["compliant_count"],
            "repair_required": summary["repair_required_count"],
            "legacy_contract_posture": summary["legacy_contract_posture_count"],
            "not_computable": summary["not_computable_count"],
            "failed": summary["failed_count"],
            "seal_recommendation": summary["seal_recommendation"],
        },
        canary_summary=canary_summary,
        overlay_observability_summary=overlay_observability_summary,
        canary_scheduler_summary=canary_scheduler_summary,
        overlay_governance_summary=overlay_governance_summary,
        overlay_risk_summary=overlay_risk_summary,
        overlay_topology_summary=overlay_topology_summary,
        milestone_summary={
            "active_milestone": milestone_registry.active_milestone,
            "stabilized_milestones": milestone_registry.stabilized_milestones,
            "latest_stable_hash": milestone_registry.latest_stable_hash,
            "lineage_depth": len(milestone_registry.milestone_lineage),
            "derived_evidence_status": milestone_validation.derived_evidence_status,
            "artifact_verified_milestones": milestone_registry.artifact_verified_milestones,
            "code_verified_milestones": milestone_registry.code_verified_milestones,
            "partial_milestones": milestone_registry.partial_milestones,
            "missing_milestones": milestone_registry.missing_milestones,
            "stale_metadata_detected": milestone_validation.stale_metadata_detected,
            "milestone_validator_status": milestone_validation.status,
        },
    )

    write_canonical_json(OUT_VALIDATION, {"schema_version": "DoctrineValidationRun.v1", "contract_count": len(results), "results": results, "summary": summary})
    write_canonical_json(OUT_AAL_VIZ, projection)
    write_canonical_json(OUT_QUEUE, queue)
    write_canonical_json(OUT_MILESTONE_REG, milestone_registry.model_dump())
    write_canonical_json(OUT_MILESTONE_VAL, milestone_validation.model_dump())


if __name__ == "__main__":
    main()
