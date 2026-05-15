"""Script: run doctrine validator over all Tier-1 contracts."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.canonical.json import write_canonical_json
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id
from core.operators.review_queue import build_review_queue
from core.performance import RuntimeProfiler
from core.pipelines.registry import load_contracts
from core.pipelines.validator import validate_pipeline_contract
from core.projections.aal_viz import build_projection_packet
from core.runes.registry import load_rune_catalog
from core.spine.milestone_continuity import validate_milestone_continuity
from core.spine.milestone_registry import build_milestone_registry
from core.spine.milestone_validator import (
    MilestoneValidationPacket,
    validate_active_milestone,
)
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
OUT_OVERLAY_CONTAINMENT = Path("out/overlay_containment/latest.json")
OUT_OVERLAY_RESOLUTION = Path("out/overlay_resolution/latest.json")
OUT_OVERLAY_READINESS = Path("out/overlay_readiness/latest.json")
OUT_OVERLAY_FIREWALL = Path("out/overlay_firewall/latest.json")
OUT_OVERLAY_FIREWALL_REPLAY = Path("out/overlay_firewall_replay/latest.json")
OUT_OVERLAY_FIREWALL_LINEAGE = Path("out/overlay_firewall_lineage/latest.json")
OUT_OVERLAY_FIREWALL_DIAGNOSTICS = Path("out/overlay_firewall_diagnostics/latest.json")
OUT_OPERATOR_QUEUE = Path("out/operator_queue/latest.json")
OUT_OPERATOR_QUEUE_REPLAY = Path("out/operator_queue_replay/latest.json")
OUT_OPERATOR_QUEUE_LINEAGE = Path("out/operator_queue_lineage/latest.json")
OUT_OPERATOR_QUEUE_DIAGNOSTICS = Path("out/operator_queue_diagnostics/latest.json")
OUT_REVIEW_CONTINUITY = Path("out/review_continuity/latest.json")
OUT_REVIEW_CONTINUITY_REPLAY = Path("out/review_continuity_replay/latest.json")
OUT_REVIEW_CONTINUITY_LINEAGE = Path("out/review_continuity_lineage/latest.json")
OUT_REVIEW_CONTINUITY_DIAGNOSTICS = Path("out/review_continuity_diagnostics/latest.json")
OUT_REVIEW_RESOLUTION = Path("out/review_resolution/latest.json")
OUT_REVIEW_RESOLUTION_REPLAY = Path("out/review_resolution_replay/latest.json")
OUT_REVIEW_RESOLUTION_LINEAGE = Path("out/review_resolution_lineage/latest.json")
OUT_REVIEW_RESOLUTION_DIAGNOSTICS = Path("out/review_resolution_diagnostics/latest.json")
OUT_MANUAL_EXECUTION = Path("out/manual_execution/latest.json")
OUT_MANUAL_EXECUTION_REPLAY = Path("out/manual_execution_replay/latest.json")
OUT_MANUAL_EXECUTION_LINEAGE = Path("out/manual_execution_lineage/latest.json")
OUT_MANUAL_EXECUTION_DIAGNOSTICS = Path("out/manual_execution_diagnostics/latest.json")
OUT_MANUAL_EXECUTION_RECEIPTS = Path("out/manual_execution_receipts/latest.json")
OUT_MANUAL_EXECUTION_RECEIPTS_REPLAY = Path("out/manual_execution_receipts_replay/latest.json")
OUT_MANUAL_EXECUTION_RECEIPTS_LINEAGE = Path("out/manual_execution_receipts_lineage/latest.json")
OUT_MANUAL_EXECUTION_RECEIPTS_DIAGNOSTICS = Path("out/manual_execution_receipts_diagnostics/latest.json")
OUT_MANUAL_ACTION_CUSTODY = Path("out/manual_action_custody/latest.json")
OUT_MANUAL_ACTION_CUSTODY_REPLAY = Path("out/manual_action_custody_replay/latest.json")
OUT_MANUAL_ACTION_CUSTODY_LINEAGE = Path("out/manual_action_custody_lineage/latest.json")
OUT_MANUAL_ACTION_CUSTODY_DIAGNOSTICS = Path("out/manual_action_custody_diagnostics/latest.json")
OUT_EXTERNAL_ACTION_PROPOSALS = Path("out/external_action_proposals/latest.json")
OUT_PROPOSAL_SANDBOX_ROUTING = Path("out/proposal_sandbox_routing/latest.json")
OUT_PROPOSAL_SANDBOX_ROUTING_REPLAY = Path("out/proposal_sandbox_routing_replay/latest.json")
OUT_PROPOSAL_SANDBOX_ROUTING_LINEAGE = Path("out/proposal_sandbox_routing_lineage/latest.json")
OUT_PROPOSAL_SANDBOX_ROUTING_DIAGNOSTICS = Path("out/proposal_sandbox_routing_diagnostics/latest.json")
OUT_PROPOSAL_SANDBOX_EVALUATION = Path("out/proposal_sandbox_evaluation/latest.json")
OUT_PROPOSAL_SANDBOX_EVALUATION_REPLAY = Path("out/proposal_sandbox_evaluation_replay/latest.json")
OUT_PROPOSAL_SANDBOX_EVALUATION_LINEAGE = Path("out/proposal_sandbox_evaluation_lineage/latest.json")
OUT_PROPOSAL_SANDBOX_EVALUATION_DIAGNOSTICS = Path("out/proposal_sandbox_evaluation_diagnostics/latest.json")
OUT_PROPOSAL_DECISION_BRIDGE = Path("out/proposal_decision_bridge/latest.json")
OUT_PROPOSAL_DECISION_BRIDGE_REPLAY = Path("out/proposal_decision_bridge_replay/latest.json")
OUT_PROPOSAL_DECISION_BRIDGE_LINEAGE = Path("out/proposal_decision_bridge_lineage/latest.json")
OUT_PROPOSAL_DECISION_BRIDGE_DIAGNOSTICS = Path("out/proposal_decision_bridge_diagnostics/latest.json")
OUT_HUMAN_DECISION_LEDGER = Path("out/human_decision_ledger/latest.json")
OUT_HUMAN_DECISION_LEDGER_REPLAY = Path("out/human_decision_ledger_replay/latest.json")
OUT_HUMAN_DECISION_LEDGER_LINEAGE = Path("out/human_decision_ledger_lineage/latest.json")
OUT_HUMAN_DECISION_LEDGER_DIAGNOSTICS = Path("out/human_decision_ledger_diagnostics/latest.json")
OUT_HUMAN_DECISION_CONTINUITY = Path("out/human_decision_continuity/latest.json")
OUT_HUMAN_DECISION_CONTINUITY_REPLAY = Path("out/human_decision_continuity_replay/latest.json")
OUT_HUMAN_DECISION_CONTINUITY_LINEAGE = Path("out/human_decision_continuity_lineage/latest.json")
OUT_HUMAN_DECISION_CONTINUITY_DIAGNOSTICS = Path("out/human_decision_continuity_diagnostics/latest.json")
logger = logging.getLogger(__name__)




def _overlay_gate_status(overlay_governance_status: dict[str, object], key: str, default: str) -> object:
    return overlay_governance_status.get(key, default)


def _build_summary(
    results: list[dict],
    active_milestone: str = "unknown",
    milestone_validation: MilestoneValidationPacket | None = None,
    milestone_registry_status: str = "not_computable",
    overlay_governance_status: dict[str, object] | None = None,
) -> dict[str, object]:
    counts = {
        "doctrine_compliant": sum(
            1 for r in results if r["status"] == "doctrine_compliant"
        ),
        "repair_required": sum(1 for r in results if r["status"] == "repair_required"),
        "legacy_contract_posture": sum(
            1 for r in results if r["status"] == "legacy_contract_posture"
        ),
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
        active_milestone_gate = (
            milestone_validation.derived_active_milestone == active_milestone
            and active_milestone != "unknown"
        )
        milestone_evidence_gate = milestone_validation.derived_evidence_status in {
            "artifact_verified",
            "code_verified",
        }
        stale_metadata_gate = not milestone_validation.stale_metadata_detected
        if not (
            milestone_registry_gate
            and active_milestone_gate
            and milestone_evidence_gate
            and stale_metadata_gate
            and milestone_validation.status == "passed"
        ):
            counts["failed"] += 1
    seal = (
        "repair"
        if counts["failed"] > 0 or counts["repair_required"] > 0
        else ("hold" if counts["legacy_contract_posture"] > 0 else "seal")
    )
    overlay_governance_status = overlay_governance_status or {}
    overlay_governance_event_gate = _overlay_gate_status(overlay_governance_status, "event_gate", "passed")
    overlay_governance_ledger_gate = _overlay_gate_status(overlay_governance_status, "ledger_gate", "passed")
    overlay_governance_continuity_gate = _overlay_gate_status(overlay_governance_status, "continuity_gate", "passed")
    overlay_governance_replay_gate = _overlay_gate_status(overlay_governance_status, "replay_gate", "passed")
    overlay_governance_operator_review_gate = _overlay_gate_status(overlay_governance_status, "operator_review_gate", "passed")
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
        "overlay_risk_envelope_gate": overlay_governance_status.get(
            "overlay_risk_envelope_gate", "passed"
        ),
        "overlay_risk_propagation_gate": overlay_governance_status.get(
            "overlay_risk_propagation_gate", "passed"
        ),
        "overlay_risk_cliff_gate": overlay_governance_status.get(
            "overlay_risk_cliff_gate", "passed"
        ),
        "overlay_risk_saturation_gate": overlay_governance_status.get(
            "overlay_risk_saturation_gate", "passed"
        ),
        "overlay_risk_replay_gate": overlay_governance_status.get(
            "overlay_risk_replay_gate", "passed"
        ),
        "overlay_risk_operator_review_gate": overlay_governance_status.get(
            "overlay_risk_operator_review_gate", "passed"
        ),
        "overlay_containment_policy_gate": overlay_governance_status.get(
            "overlay_containment_policy_gate", "passed"
        ),
        "overlay_containment_recommendation_gate": overlay_governance_status.get(
            "overlay_containment_recommendation_gate", "passed"
        ),
        "overlay_containment_trigger_gate": overlay_governance_status.get(
            "overlay_containment_trigger_gate", "passed"
        ),
        "overlay_containment_scope_gate": overlay_governance_status.get(
            "overlay_containment_scope_gate", "passed"
        ),
        "overlay_containment_replay_gate": overlay_governance_status.get(
            "overlay_containment_replay_gate", "passed"
        ),
        "overlay_containment_operator_review_gate": overlay_governance_status.get(
            "overlay_containment_operator_review_gate", "passed"
        ),
        "overlay_resolution_event_gate": overlay_governance_status.get(
            "overlay_resolution_event_gate", "passed"
        ),
        "overlay_resolution_ledger_gate": overlay_governance_status.get(
            "overlay_resolution_ledger_gate", "passed"
        ),
        "overlay_resolution_outcome_gate": overlay_governance_status.get(
            "overlay_resolution_outcome_gate", "passed"
        ),
        "overlay_resolution_closure_gate": overlay_governance_status.get(
            "overlay_resolution_closure_gate", "passed"
        ),
        "overlay_resolution_replay_gate": overlay_governance_status.get(
            "overlay_resolution_replay_gate", "passed"
        ),
        "overlay_resolution_operator_review_gate": overlay_governance_status.get(
            "overlay_resolution_operator_review_gate", "passed"
        ),
        "overlay_readiness_index_gate": overlay_governance_status.get(
            "overlay_readiness_index_gate", "passed"
        ),
        "overlay_readiness_component_gate": overlay_governance_status.get(
            "overlay_readiness_component_gate", "passed"
        ),
        "overlay_readiness_threshold_gate": overlay_governance_status.get(
            "overlay_readiness_threshold_gate", "passed"
        ),
        "overlay_readiness_replay_gate": overlay_governance_status.get(
            "overlay_readiness_replay_gate", "passed"
        ),
        "overlay_readiness_operator_review_gate": overlay_governance_status.get(
            "overlay_readiness_operator_review_gate", "passed"
        ),
        "overlay_firewall_readiness_gate": overlay_governance_status.get(
            "overlay_firewall_readiness_gate", "not_computable"
        ),
        "overlay_firewall_governance_gate": overlay_governance_status.get(
            "overlay_firewall_governance_gate", "not_computable"
        ),
        "overlay_firewall_containment_gate": overlay_governance_status.get(
            "overlay_firewall_containment_gate", "not_computable"
        ),
        "overlay_firewall_rollback_gate": overlay_governance_status.get(
            "overlay_firewall_rollback_gate", "not_computable"
        ),
        "overlay_firewall_continuity_gate": overlay_governance_status.get(
            "overlay_firewall_continuity_gate", "not_computable"
        ),
        "overlay_firewall_eligibility_gate": overlay_governance_status.get(
            "overlay_firewall_eligibility_gate", "not_computable"
        ),
        "overlay_firewall_replay_gate": overlay_governance_status.get(
            "overlay_firewall_replay_gate", "not_computable"
        ),
        "overlay_firewall_operator_review_gate": overlay_governance_status.get(
            "overlay_firewall_operator_review_gate", "not_computable"
        ),
        "operator_queue_request_gate": overlay_governance_status.get(
            "operator_queue_request_gate", "not_computable"
        ),
        "operator_queue_decision_gate": overlay_governance_status.get(
            "operator_queue_decision_gate", "not_computable"
        ),
        "operator_queue_rationale_gate": overlay_governance_status.get(
            "operator_queue_rationale_gate", "not_computable"
        ),
        "operator_queue_continuity_gate": overlay_governance_status.get(
            "operator_queue_continuity_gate", "not_computable"
        ),
        "operator_queue_replay_gate": overlay_governance_status.get(
            "operator_queue_replay_gate", "not_computable"
        ),
        "operator_queue_operator_review_gate": overlay_governance_status.get(
            "operator_queue_operator_review_gate", "not_computable"
        ),
        "review_continuity_chain_gate": overlay_governance_status.get(
            "review_continuity_chain_gate", "not_computable"
        ),
        "review_continuity_inheritance_gate": overlay_governance_status.get(
            "review_continuity_inheritance_gate", "not_computable"
        ),
        "review_continuity_deferral_gate": overlay_governance_status.get(
            "review_continuity_deferral_gate", "not_computable"
        ),
        "review_continuity_denial_gate": overlay_governance_status.get(
            "review_continuity_denial_gate", "not_computable"
        ),
        "review_continuity_replay_gate": overlay_governance_status.get(
            "review_continuity_replay_gate", "not_computable"
        ),
        "review_continuity_operator_review_gate": overlay_governance_status.get(
            "review_continuity_operator_review_gate", "not_computable"
        ),
        "review_resolution_posture_gate": overlay_governance_status.get("review_resolution_posture_gate", "not_computable"),
        "review_resolution_blocker_gate": overlay_governance_status.get("review_resolution_blocker_gate", "not_computable"),
        "review_resolution_outcome_gate": overlay_governance_status.get("review_resolution_outcome_gate", "not_computable"),
        "review_resolution_closure_gate": overlay_governance_status.get("review_resolution_closure_gate", "not_computable"),
        "review_resolution_replay_gate": overlay_governance_status.get("review_resolution_replay_gate", "not_computable"),
        "review_resolution_operator_review_gate": overlay_governance_status.get("review_resolution_operator_review_gate", "not_computable"),
        "manual_execution_authorization_gate": overlay_governance_status.get("manual_execution_authorization_gate", "not_computable"),
        "manual_execution_envelope_gate": overlay_governance_status.get("manual_execution_envelope_gate", "not_computable"),
        "manual_execution_eligibility_gate": overlay_governance_status.get("manual_execution_eligibility_gate", "not_computable"),
        "manual_execution_scope_gate": overlay_governance_status.get("manual_execution_scope_gate", "not_computable"),
        "manual_execution_acknowledgement_gate": overlay_governance_status.get("manual_execution_acknowledgement_gate", "not_computable"),
        "manual_execution_replay_gate": overlay_governance_status.get("manual_execution_replay_gate", "not_computable"),
        "manual_execution_operator_review_gate": overlay_governance_status.get("manual_execution_operator_review_gate", "not_computable"),
        "manual_execution_receipt_gate": overlay_governance_status.get("manual_execution_receipt_gate", "not_computable"),
        "manual_execution_receipt_ledger_gate": overlay_governance_status.get("manual_execution_receipt_ledger_gate", "not_computable"),
        "manual_execution_receipt_scope_gate": overlay_governance_status.get("manual_execution_receipt_scope_gate", "not_computable"),
        "manual_execution_receipt_acknowledgement_gate": overlay_governance_status.get("manual_execution_receipt_acknowledgement_gate", "not_computable"),
        "manual_execution_receipt_replay_gate": overlay_governance_status.get("manual_execution_receipt_replay_gate", "not_computable"),
        "manual_execution_receipt_operator_review_gate": overlay_governance_status.get("manual_execution_receipt_operator_review_gate", "not_computable"),
        "manual_action_custody_gate": overlay_governance_status.get("manual_action_custody_gate", "not_computable"),
        "manual_action_handoff_gate": overlay_governance_status.get("manual_action_handoff_gate", "not_computable"),
        "manual_action_acknowledgement_gate": overlay_governance_status.get("manual_action_acknowledgement_gate", "not_computable"),
        "manual_action_escalation_gate": overlay_governance_status.get("manual_action_escalation_gate", "not_computable"),
        "manual_action_replay_gate": overlay_governance_status.get("manual_action_replay_gate", "not_computable"),
        "manual_action_operator_review_gate": overlay_governance_status.get("manual_action_operator_review_gate", "not_computable"),
        "external_action_proposal_gate": overlay_governance_status.get("external_action_proposal_gate", "not_computable"),
        "external_action_category_gate": overlay_governance_status.get("external_action_category_gate", "not_computable"),
        "external_action_constraint_gate": overlay_governance_status.get("external_action_constraint_gate", "not_computable"),
        "external_action_readiness_gate": overlay_governance_status.get("external_action_readiness_gate", "not_computable"),
        "external_action_governance_gate": overlay_governance_status.get("external_action_governance_gate", "not_computable"),
        "external_action_replay_gate": overlay_governance_status.get("external_action_replay_gate", "not_computable"),
        "external_action_operator_review_gate": overlay_governance_status.get("external_action_operator_review_gate", "not_computable"),
        "proposal_sandbox_route_gate": overlay_governance_status.get("proposal_sandbox_route_gate", "not_computable"),
        "proposal_sandbox_lane_gate": overlay_governance_status.get("proposal_sandbox_lane_gate", "not_computable"),
        "proposal_sandbox_constraint_gate": overlay_governance_status.get("proposal_sandbox_constraint_gate", "not_computable"),
        "proposal_sandbox_eligibility_gate": overlay_governance_status.get("proposal_sandbox_eligibility_gate", "not_computable"),
        "proposal_sandbox_governance_gate": overlay_governance_status.get("proposal_sandbox_governance_gate", "not_computable"),
        "proposal_sandbox_evaluation_gate": overlay_governance_status.get("proposal_sandbox_evaluation_gate", "not_computable"),
        "proposal_sandbox_score_gate": overlay_governance_status.get("proposal_sandbox_score_gate", "not_computable"),
        "proposal_sandbox_rationale_gate": overlay_governance_status.get("proposal_sandbox_rationale_gate", "not_computable"),
        "proposal_sandbox_restriction_gate": overlay_governance_status.get("proposal_sandbox_restriction_gate", "not_computable"),
        "proposal_sandbox_replay_gate": overlay_governance_status.get("proposal_sandbox_replay_gate", "not_computable"),
        "proposal_sandbox_operator_review_gate": overlay_governance_status.get("proposal_sandbox_operator_review_gate", "not_computable"),
        "proposal_decision_bridge_gate": overlay_governance_status.get("proposal_decision_bridge_gate", "not_computable"),
        "proposal_decision_input_gate": overlay_governance_status.get("proposal_decision_input_gate", "not_computable"),
        "proposal_decision_rationale_gate": overlay_governance_status.get("proposal_decision_rationale_gate", "not_computable"),
        "proposal_decision_restriction_gate": overlay_governance_status.get("proposal_decision_restriction_gate", "not_computable"),
        "proposal_decision_replay_gate": overlay_governance_status.get("proposal_decision_replay_gate", "not_computable"),
        "proposal_decision_operator_review_gate": overlay_governance_status.get("proposal_decision_operator_review_gate", "not_computable"),
        "human_decision_ledger_gate": overlay_governance_status.get("human_decision_ledger_gate", "not_computable"),
        "human_decision_rationale_gate": overlay_governance_status.get("human_decision_rationale_gate", "not_computable"),
        "human_decision_blocker_gate": overlay_governance_status.get("human_decision_blocker_gate", "not_computable"),
        "human_decision_deferral_gate": overlay_governance_status.get("human_decision_deferral_gate", "not_computable"),
        "human_decision_replay_gate": overlay_governance_status.get("human_decision_replay_gate", "not_computable"),
        "human_decision_operator_review_gate": overlay_governance_status.get("human_decision_operator_review_gate", "not_computable"),
        "human_decision_continuity_chain_gate": overlay_governance_status.get("human_decision_continuity_chain_gate", "not_computable"),
        "human_decision_continuity_inheritance_gate": overlay_governance_status.get("human_decision_continuity_inheritance_gate", "not_computable"),
        "human_decision_continuity_deferral_gate": overlay_governance_status.get("human_decision_continuity_deferral_gate", "not_computable"),
        "human_decision_continuity_blocker_gate": overlay_governance_status.get("human_decision_continuity_blocker_gate", "not_computable"),
        "human_decision_continuity_replay_gate": overlay_governance_status.get("human_decision_continuity_replay_gate", "not_computable"),
        "human_decision_continuity_operator_review_gate": overlay_governance_status.get("human_decision_continuity_operator_review_gate", "not_computable"),
    }


def main() -> None:
    diagnostics_logger = get_structured_logger(__name__)
    profiler = RuntimeProfiler(RuntimePaths.from_env().runtime_performance_profile_latest)
    profiler.record_artifact("contracts_dir", CONTRACTS_DIR)
    profiler.record_artifact("rune_catalog_input", RUNE_CATALOG_PATH)
    profiler.record_artifact("routes_dir", ROUTES_DIR)
    profiler.record_artifact("validation_output", OUT_VALIDATION)
    profiler.record_artifact("projection_output", OUT_AAL_VIZ)
    profiler.record_artifact("review_queue_output", OUT_QUEUE)
    profiler.record_artifact("milestone_registry_output", OUT_MILESTONE_REG)
    profiler.record_artifact("milestone_validation_output", OUT_MILESTONE_VAL)
    with profiler.measure("validation_generation", "load_rune_catalog"):
        rune_catalog = load_rune_catalog(RUNE_CATALOG_PATH)
    with profiler.measure("validation_generation", "load_route_graphs"):
        route_graphs = load_route_graphs(ROUTES_DIR)
    with profiler.measure("validation_generation", "load_contracts"):
        contracts = load_contracts(CONTRACTS_DIR)
    with profiler.measure("validation_generation", "validate_milestone_continuity"):
        continuity = validate_milestone_continuity()

    results = []
    with profiler.measure("validation_generation", "validate_pipeline_contracts"):
        for contract in contracts:
            graph_data = (
                route_graphs[contract.pipeline_id].model_dump()
                if contract.pipeline_id in route_graphs
                else None
            )
            results.append(
                validate_pipeline_contract(
                    contract, rune_catalog, graph_data, continuity.model_dump()
                )
            )

    from core.pipelines.registry import build_registry

    with profiler.measure("validation_generation", "build_registry"):
        registry = build_registry(contracts)
    with profiler.measure("validation_generation", "build_review_queue"):
        queue = build_review_queue(results)
    with profiler.measure("validation_generation", "build_milestone_registry"):
        milestone_registry = build_milestone_registry(Path("."))
    reported_active = milestone_registry.active_milestone
    with profiler.measure("validation_generation", "validate_active_milestone"):
        milestone_validation = validate_active_milestone(
            reported_active, milestone_registry
        )
    overlay_governance_runtime: dict[str, object] = {}
    overlay_governance_summary = {
        "governance_events": 0,
        "ledger_depth": 0,
        "continuity_score": 0.0,
        "missing_event_types": [],
        "replay_matches": 0,
        "replay_failures": 0,
        "critical_diagnostics": 0,
        "pending_reviews": 0,
    }
    overlay_governance_gates = {
        "event_gate": "passed",
        "ledger_gate": "passed",
        "continuity_gate": "passed",
        "replay_gate": "passed",
        "operator_review_gate": "passed",
    }
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
            "critical_diagnostics": sum(
                1 for d in diagnostics if d.get("severity") == "critical"
            ),
            "pending_reviews": len(operator_review.get("pending_actions", [])),
        }
        overlay_governance_gates = {
            "event_gate": "passed"
            if overlay_governance_summary["governance_events"] > 0
            else "failed",
            "ledger_gate": "passed"
            if overlay_governance_summary["ledger_depth"] > 0
            else "failed",
            "continuity_gate": "passed"
            if overlay_governance_summary["continuity_score"] >= 0.5
            else "failed",
            "replay_gate": "passed"
            if overlay_governance_summary["replay_failures"] == 0
            and overlay_governance_summary["replay_matches"] == 1
            else "failed",
            "operator_review_gate": "failed"
            if overlay_governance_summary["critical_diagnostics"] > 0
            else "passed",
        }
    overlay_risk_summary = {
        "aggregate_risk": 0.0,
        "cliff_risk": 0.0,
        "saturation_risk": 0.0,
        "replay_instability": 0,
        "propagation_depth": 0,
        "pending_reviews": 0,
        "critical_diagnostics": 0,
    }
    if OUT_OVERLAY_RISK.exists():
        risk = json.loads(OUT_OVERLAY_RISK.read_text())
        env = (risk.get("envelopes") or [{}])[0]
        overlay_risk_summary = {
            "aggregate_risk": env.get("aggregate_risk_score", 0.0),
            "cliff_risk": risk.get("cliff", {}).get("cliff_risk_score", 0.0),
            "saturation_risk": risk.get("saturation", {}).get("saturation_score", 0.0),
            "replay_instability": len(
                risk.get("replay", {}).get("mismatched_packets", [])
            ),
            "propagation_depth": risk.get("propagation", {}).get(
                "propagation_depth", 0
            ),
            "pending_reviews": len(
                risk.get("operator_review", {}).get("pending_actions", [])
            ),
            "critical_diagnostics": sum(
                1
                for d in risk.get("diagnostics", [])
                if d.get("severity") == "critical"
            ),
        }
        overlay_governance_gates.update(
            {
                "overlay_risk_envelope_gate": "passed",
                "overlay_risk_propagation_gate": "failed"
                if risk.get("propagation", {}).get("cycles_detected")
                else "passed",
                "overlay_risk_cliff_gate": "passed",
                "overlay_risk_saturation_gate": "passed",
                "overlay_risk_replay_gate": "passed"
                if risk.get("replay", {}).get("deterministic_match")
                else "failed",
                "overlay_risk_operator_review_gate": "failed"
                if overlay_risk_summary["critical_diagnostics"] > 0
                else "passed",
            }
        )
    overlay_topology_summary = {
        "overlay_nodes": 0,
        "overlay_edges": 0,
        "graph_density": 0.0,
        "coupling_score": 0.0,
        "bottlenecks": 0,
        "rollback_path_depth": 0,
        "propagation_depth": 0,
        "critical_diagnostics": 0,
    }
    if OUT_OVERLAY_TOPOLOGY.exists():
        ot = json.loads(OUT_OVERLAY_TOPOLOGY.read_text())
        overlay_topology_summary = {
            "overlay_nodes": len(ot.get("graph", {}).get("overlay_nodes", [])),
            "overlay_edges": len(ot.get("graph", {}).get("overlay_edges", [])),
            "graph_density": ot.get("graph", {}).get("graph_density", 0.0),
            "coupling_score": ot.get("coupling", {}).get(
                "aggregate_coupling_score", 0.0
            ),
            "bottlenecks": ot.get("bottleneck", {}).get("bottleneck_count", 0),
            "rollback_path_depth": ot.get("rollback_paths", {}).get(
                "rollback_path_depth", 0
            ),
            "propagation_depth": ot.get("propagation", {}).get("propagation_depth", 0),
            "critical_diagnostics": sum(
                1 for d in ot.get("diagnostics", []) if d.get("severity") == "critical"
            ),
        }
        overlay_governance_gates.update(
            {
                "overlay_topology_graph_gate": "passed",
                "overlay_topology_adjacency_gate": "passed",
                "overlay_topology_coupling_gate": "passed",
                "overlay_topology_bottleneck_gate": "passed",
                "overlay_topology_replay_gate": "passed"
                if ot.get("replay", {}).get("deterministic_match")
                else "failed",
                "overlay_topology_operator_review_gate": "failed"
                if overlay_topology_summary["critical_diagnostics"] > 0
                else "passed",
            }
        )

    overlay_containment_summary = {
        "containment_recommendations": 0,
        "critical_recommendations": 0,
        "active_triggers": 0,
        "affected_overlays": 0,
        "containment_scope_depth": 0,
        "replay_matches": 0,
        "critical_diagnostics": 0,
        "pending_reviews": 0,
    }
    if OUT_OVERLAY_CONTAINMENT.exists():
        oc = json.loads(OUT_OVERLAY_CONTAINMENT.read_text())
        overlay_containment_summary = {
            "containment_recommendations": len(oc.get("recommendations", [])),
            "critical_recommendations": sum(
                1
                for r in oc.get("recommendations", [])
                if r.get("advisory_severity") == "critical"
            ),
            "active_triggers": len(oc.get("triggers", {}).get("active_triggers", [])),
            "affected_overlays": len(oc.get("scope", {}).get("affected_overlays", [])),
            "containment_scope_depth": oc.get("scope", {}).get(
                "containment_scope_depth", 0
            ),
            "replay_matches": 1
            if oc.get("replay", {}).get("deterministic_match")
            else 0,
            "critical_diagnostics": sum(
                1 for d in oc.get("diagnostics", []) if d.get("severity") == "critical"
            ),
            "pending_reviews": len(
                oc.get("operator_review", {}).get("pending_actions", [])
            ),
        }
        overlay_governance_gates.update(
            {
                "overlay_containment_policy_gate": "passed"
                if bool(oc.get("policy"))
                else "failed",
                "overlay_containment_recommendation_gate": "passed"
                if overlay_containment_summary["containment_recommendations"] >= 0
                else "failed",
                "overlay_containment_trigger_gate": "passed"
                if "active_triggers" in oc.get("triggers", {})
                else "failed",
                "overlay_containment_scope_gate": "passed"
                if bool(oc.get("scope"))
                else "failed",
                "overlay_containment_replay_gate": "passed"
                if oc.get("replay", {}).get("deterministic_match")
                else "failed",
                "overlay_containment_operator_review_gate": "failed"
                if overlay_containment_summary["critical_diagnostics"] > 0
                else "passed",
            }
        )

    overlay_resolution_summary = {
        "total_resolution_events": 0,
        "unresolved_events": 0,
        "critical_unresolved_events": 0,
        "replay_failures": 0,
        "rollback_ready_count": 0,
        "blocked_resolution_count": 0,
        "closure_ready": False,
        "pending_reviews": 0,
    }
    if OUT_OVERLAY_RESOLUTION.exists():
        ors = json.loads(OUT_OVERLAY_RESOLUTION.read_text())
        outcomes = ors.get("outcomes", [])
        overlay_resolution_summary = {
            "total_resolution_events": len(ors.get("events", [])),
            "unresolved_events": ors.get("ledger", {}).get("unresolved_events", 0),
            "critical_unresolved_events": ors.get("ledger", {}).get(
                "critical_unresolved_events", 0
            ),
            "replay_failures": len(
                ors.get("replay", {}).get("mismatched_components", [])
            ),
            "rollback_ready_count": sum(1 for o in outcomes if o.get("rollback_ready")),
            "blocked_resolution_count": sum(
                1 for o in outcomes if o.get("resolution_status") == "blocked"
            ),
            "closure_ready": ors.get("closure", {}).get("closure_ready", False),
            "pending_reviews": len(
                ors.get("operator_review", {}).get("pending_actions", [])
            ),
        }
        overlay_governance_gates.update(
            {
                "overlay_resolution_event_gate": "passed"
                if overlay_resolution_summary["total_resolution_events"] >= 1
                else "failed",
                "overlay_resolution_ledger_gate": "passed"
                if bool(ors.get("ledger"))
                else "failed",
                "overlay_resolution_outcome_gate": "passed"
                if len(outcomes) >= 1
                else "failed",
                "overlay_resolution_closure_gate": "passed"
                if isinstance(ors.get("closure", {}).get("closure_ready"), bool)
                else "failed",
                "overlay_resolution_replay_gate": "passed"
                if ors.get("replay", {}).get("deterministic_match")
                else "failed",
                "overlay_resolution_operator_review_gate": "failed"
                if overlay_resolution_summary["critical_unresolved_events"] > 0
                else "passed",
            }
        )

    overlay_readiness_summary = {
        "aggregate_readiness_score": 0.0,
        "readiness_band": "blocked",
        "component_scores": {},
        "blocked_components": [],
        "replay_matches": 0,
        "rollback_ready": 0,
        "critical_diagnostics": 0,
        "pending_reviews": 0,
    }
    if OUT_OVERLAY_READINESS.exists():
        ordy = json.loads(OUT_OVERLAY_READINESS.read_text())
        idx = ordy.get("index", {})
        comps = ordy.get("components", [])
        comp_scores = {
            c.get("component_type"): c.get("component_score", 0.0) for c in comps
        }
        blocked = [
            k for k, v in comp_scores.items() if isinstance(v, (int, float)) and v < 0.5
        ]
        overlay_readiness_summary = {
            "aggregate_readiness_score": idx.get("aggregate_readiness_score", 0.0),
            "readiness_band": idx.get("readiness_band", "blocked"),
            "component_scores": comp_scores,
            "blocked_components": blocked,
            "replay_matches": 1
            if ordy.get("replay", {}).get("deterministic_match")
            else 0,
            "rollback_ready": 1 if idx.get("rollback_score", 0.0) >= 0.5 else 0,
            "critical_diagnostics": sum(
                1
                for d in ordy.get("diagnostics", [])
                if d.get("severity") == "critical"
            ),
            "pending_reviews": len(
                ordy.get("operator_review", {}).get("pending_actions", [])
            ),
        }
        overlay_governance_gates.update(
            {
                "overlay_readiness_index_gate": "passed" if bool(idx) else "failed",
                "overlay_readiness_component_gate": "passed"
                if len(comps) > 0
                else "failed",
                "overlay_readiness_threshold_gate": "passed"
                if bool(ordy.get("threshold"))
                else "failed",
                "overlay_readiness_replay_gate": "passed"
                if ordy.get("replay", {}).get("deterministic_match")
                else "failed",
                "overlay_readiness_operator_review_gate": "failed"
                if overlay_readiness_summary["critical_diagnostics"] > 0
                else "passed",
            }
        )
    overlay_firewall_summary = {
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
    }
    firewall_gate_keys = [
        "overlay_firewall_readiness_gate",
        "overlay_firewall_governance_gate",
        "overlay_firewall_containment_gate",
        "overlay_firewall_rollback_gate",
        "overlay_firewall_continuity_gate",
        "overlay_firewall_eligibility_gate",
        "overlay_firewall_replay_gate",
        "overlay_firewall_operator_review_gate",
    ]
    if OUT_OVERLAY_FIREWALL.exists():
        ofw = json.loads(OUT_OVERLAY_FIREWALL.read_text())
        forbidden = {"approved", "activated", "live", "executing", "production_ready"}
        firewall_status = str(
            ofw.get("firewall", {}).get("firewall_status", "not_computable")
        )
        replay_match = bool(ofw.get("replay", {}).get("deterministic_match"))
        authority = ofw.get("firewall", {}).get("authority", {})
        authority_violation = (
            any(bool(v) for v in authority.values())
            if isinstance(authority, dict)
            else True
        )
        critical_unresolved = any(
            d.get("severity") == "critical" and not d.get("resolved", False)
            for d in ofw.get("diagnostics", [])
        )
        base_failed = (
            ofw.get("status") != "passed"
            or firewall_status in forbidden
            or not replay_match
            or authority_violation
            or critical_unresolved
            or not OUT_OVERLAY_FIREWALL_REPLAY.exists()
            or not OUT_OVERLAY_FIREWALL_LINEAGE.exists()
            or not OUT_OVERLAY_FIREWALL_DIAGNOSTICS.exists()
        )
        overlay_governance_gates.update(
            {
                gate: ("failed" if base_failed else str(ofw.get(gate, "passed")))
                for gate in firewall_gate_keys
            }
        )
        overlay_firewall_summary = {
            "firewall_status": firewall_status,
            "blocked_reasons": ofw.get("firewall", {}).get("blocked_reasons", []),
            "rollback_ready": bool(
                ofw.get("rollback", {}).get("rollback_ready", False)
            ),
            "replay_matches": replay_match,
            "critical_diagnostics": sum(
                1 for d in ofw.get("diagnostics", []) if d.get("severity") == "critical"
            ),
            "containment_restrictions": ofw.get("containment", {}).get(
                "containment_restrictions", []
            ),
            "governance_continuity": ofw.get("governance", {}).get(
                "governance_continuity_score", 0.0
            ),
            "operator_review_required": bool(
                ofw.get("operator_review", {}).get("operator_review_required", True)
            ),
            "projection_only": True,
            "inference_authority": False,
        }
    else:
        overlay_governance_gates.update(
            {gate: "not_computable" for gate in firewall_gate_keys}
        )
    operator_queue_summary = {
        "pending_requests": 0,
        "deferred_requests": 0,
        "denied_requests": 0,
        "review_only_approved_requests": 0,
        "unresolved_diagnostics": 1,
        "replay_matches": False,
        "continuity_status": "not_computable",
        "authority_locked": False,
    }
    operator_queue_gate_keys = [
        "operator_queue_request_gate",
        "operator_queue_decision_gate",
        "operator_queue_rationale_gate",
        "operator_queue_continuity_gate",
        "operator_queue_replay_gate",
        "operator_queue_operator_review_gate",
    ]
    if (
        OUT_OPERATOR_QUEUE.exists()
        and OUT_OPERATOR_QUEUE_REPLAY.exists()
        and OUT_OPERATOR_QUEUE_LINEAGE.exists()
        and OUT_OPERATOR_QUEUE_DIAGNOSTICS.exists()
    ):
        oq = json.loads(OUT_OPERATOR_QUEUE.read_text())
        oq_replay = json.loads(OUT_OPERATOR_QUEUE_REPLAY.read_text())
        oq_diag = json.loads(OUT_OPERATOR_QUEUE_DIAGNOSTICS.read_text())
        oq_validator = oq.get("validator", {})
        oq_request = oq.get("request", {})
        oq_decision = oq.get("decision", {})
        oq_review = oq.get("operator_review", {})
        oq_continuity = oq.get("continuity", {})
        forbidden_statuses = {"activated", "executing", "live", "production_ready"}
        forbidden_decisions = {"execute", "activate", "deploy", "promote_live"}
        authority = oq_request.get("authority", {})
        authority_mutation = (
            any(bool(v) for v in authority.values()) if isinstance(authority, dict) else True
        )
        replay_match = bool(oq_replay.get("deterministic_match"))
        critical_unresolved = any(
            d.get("severity") == "critical" and not d.get("resolved", False)
            for d in oq_diag
        )
        base_failed = (
            oq.get("status") != "passed"
            or oq_validator.get("status") == "failed"
            or oq_request.get("request_status") in forbidden_statuses
            or oq_decision.get("decision") in forbidden_decisions
            or not replay_match
            or critical_unresolved
            or authority_mutation
        )
        gate_results = {
            g.get("gate"): g.get("passed")
            for g in oq_validator.get("gate_results", [])
            if g.get("gate")
        }
        overlay_governance_gates.update(
            {
                gate: "failed"
                if base_failed or gate_results.get(gate) is False
                else ("passed" if gate_results.get(gate) is True else "governed_runtime_delegated")
                for gate in operator_queue_gate_keys
            }
        )
        operator_queue_summary = {
            "pending_requests": oq_review.get("pending_requests", 0),
            "deferred_requests": oq_review.get("deferred_requests", 0),
            "denied_requests": oq_review.get("denied_requests", 0),
            "review_only_approved_requests": oq_review.get(
                "review_only_approved_requests", 0
            ),
            "unresolved_diagnostics": oq_review.get("unresolved_diagnostics", 0),
            "replay_matches": replay_match,
            "continuity_status": oq_continuity.get("status", "not_computable"),
            "authority_locked": not authority_mutation,
        }
    else:
        overlay_governance_gates.update(
            {gate: "not_computable" for gate in operator_queue_gate_keys}
        )
    review_continuity_summary = {
        "continuity_chains": 0,
        "deferred_sequences": 0,
        "denied_sequences": 0,
        "unresolved_diagnostics": 1,
        "replay_matches": False,
        "continuity_integrity": False,
        "authority_locked": False,
    }
    review_continuity_gate_keys = [
        "review_continuity_chain_gate",
        "review_continuity_inheritance_gate",
        "review_continuity_deferral_gate",
        "review_continuity_denial_gate",
        "review_continuity_replay_gate",
        "review_continuity_operator_review_gate",
    ]
    if OUT_REVIEW_CONTINUITY.exists() and OUT_REVIEW_CONTINUITY_REPLAY.exists() and OUT_REVIEW_CONTINUITY_LINEAGE.exists() and OUT_REVIEW_CONTINUITY_DIAGNOSTICS.exists():
        rc = json.loads(OUT_REVIEW_CONTINUITY.read_text())
        rc_replay = json.loads(OUT_REVIEW_CONTINUITY_REPLAY.read_text())
        rc_diag = json.loads(OUT_REVIEW_CONTINUITY_DIAGNOSTICS.read_text())
        rc_validator = rc.get("validator", {})
        replay_match = bool(rc_replay.get("deterministic_match"))
        authority = rc.get("chain", {}).get("authority", {})
        authority_mutation = any(bool(v) for v in authority.values()) if isinstance(authority, dict) else True
        forbidden = {"executing", "activated", "deployed", "production_live"}
        forbidden_status = rc.get("chain", {}).get("chain_status") in forbidden
        critical_unresolved = any(d.get("severity") == "critical" and not d.get("resolved", False) for d in rc_diag)
        base_failed = rc.get("status") != "passed" or rc_validator.get("status") == "failed" or not replay_match or forbidden_status or critical_unresolved or authority_mutation
        gate_results = {g.get("gate"): g.get("passed") for g in rc_validator.get("gate_results", []) if g.get("gate")}
        overlay_governance_gates.update({gate: "failed" if base_failed or gate_results.get(gate) is False else ("passed" if gate_results.get(gate) is True else "governed_runtime_delegated") for gate in review_continuity_gate_keys})
        review = rc.get("operator_review", {})
        continuity = rc.get("continuity", {})
        review_continuity_summary = {
            "continuity_chains": review.get("continuity_chains", 0),
            "deferred_sequences": review.get("deferred_sequences", 0),
            "denied_sequences": review.get("denied_sequences", 0),
            "unresolved_diagnostics": review.get("unresolved_diagnostics", 0),
            "replay_matches": replay_match,
            "continuity_integrity": continuity.get("continuity_integrity", False),
            "authority_locked": not authority_mutation,
        }
    else:
        overlay_governance_gates.update({gate: "not_computable" for gate in review_continuity_gate_keys})


    review_resolution_summary = {"resolution_posture": "unresolved", "unresolved_blockers": 1, "critical_blockers": 1, "closure_ready": False, "replay_matches": False, "pending_reviews": 1, "authority_locked": False}
    review_resolution_gate_keys = ["review_resolution_posture_gate", "review_resolution_blocker_gate", "review_resolution_outcome_gate", "review_resolution_closure_gate", "review_resolution_replay_gate", "review_resolution_operator_review_gate"]
    if OUT_REVIEW_RESOLUTION.exists() and OUT_REVIEW_RESOLUTION_REPLAY.exists() and OUT_REVIEW_RESOLUTION_LINEAGE.exists() and OUT_REVIEW_RESOLUTION_DIAGNOSTICS.exists():
        rr = json.loads(OUT_REVIEW_RESOLUTION.read_text())
        rr_replay = json.loads(OUT_REVIEW_RESOLUTION_REPLAY.read_text())
        rr_diag = json.loads(OUT_REVIEW_RESOLUTION_DIAGNOSTICS.read_text())
        rr_validator = rr.get("validator", {})
        replay_match = bool(rr_replay.get("deterministic_match"))
        authority = rr.get("posture", {}).get("authority", {})
        authority_mutation = any(bool(v) for v in authority.values()) if isinstance(authority, dict) else True
        critical_unresolved = any(d.get("severity") == "critical" and not d.get("resolved", False) for d in rr_diag)
        base_failed = rr.get("status") != "passed" or rr_validator.get("status") == "failed" or not replay_match or critical_unresolved or authority_mutation
        gate_results = {g.get("gate"): g.get("passed") for g in rr_validator.get("gate_results", []) if g.get("gate")}
        overlay_governance_gates.update({gate: "failed" if base_failed or gate_results.get(gate) is False else ("passed" if gate_results.get(gate) is True else "governed_runtime_delegated") for gate in review_resolution_gate_keys})
        rr_summary = rr.get("review_resolution_summary", {})
        review_resolution_summary = {**review_resolution_summary, **rr_summary, "replay_matches": replay_match, "authority_locked": not authority_mutation}
    else:
        overlay_governance_gates.update({gate: "not_computable" for gate in review_resolution_gate_keys})


    manual_execution_summary = {"authorization_status": "not_authorized", "envelope_status": "not_computable", "eligible_for_manual_review": False, "unresolved_blockers": 1, "forbidden_actions": ["execute"], "replay_matches": False, "acknowledgement_present": False, "authority_locked": False}
    manual_execution_gate_keys = ["manual_execution_authorization_gate", "manual_execution_envelope_gate", "manual_execution_eligibility_gate", "manual_execution_scope_gate", "manual_execution_acknowledgement_gate", "manual_execution_replay_gate", "manual_execution_operator_review_gate"]
    if OUT_MANUAL_EXECUTION.exists() and OUT_MANUAL_EXECUTION_REPLAY.exists() and OUT_MANUAL_EXECUTION_LINEAGE.exists() and OUT_MANUAL_EXECUTION_DIAGNOSTICS.exists():
        me = json.loads(OUT_MANUAL_EXECUTION.read_text())
        me_replay = json.loads(OUT_MANUAL_EXECUTION_REPLAY.read_text())
        me_diag = json.loads(OUT_MANUAL_EXECUTION_DIAGNOSTICS.read_text())
        me_validator = me.get("validator", {})
        replay_match = bool(me_replay.get("deterministic_match"))
        authority = me.get("authorization", {}).get("authority", {})
        authority_mutation = any(bool(v) for v in authority.values()) if isinstance(authority, dict) else True
        critical_unresolved = any(d.get("severity") == "critical" and not d.get("resolved", False) for d in me_diag)
        base_failed = me.get("status") != "passed" or me_validator.get("status") == "failed" or not replay_match or critical_unresolved or authority_mutation
        gate_results = {g.get("gate"): g.get("passed") for g in me_validator.get("gate_results", []) if g.get("gate")}
        overlay_governance_gates.update({gate: "failed" if base_failed or gate_results.get(gate) is False else ("passed" if gate_results.get(gate) is True else "governed_runtime_delegated") for gate in manual_execution_gate_keys})
        me_summary = me.get("manual_execution_summary", {})
        manual_execution_summary = {**manual_execution_summary, **me_summary, "replay_matches": replay_match, "authority_locked": not authority_mutation}
    else:
        overlay_governance_gates.update({gate: "not_computable" for gate in manual_execution_gate_keys})


    manual_execution_receipt_summary = {"total_receipts": 0, "pending_receipts": 1, "blocked_receipts": 0, "invalid_receipts": 0, "replay_matches": False, "unresolved_diagnostics": 1, "authority_locked": False}
    manual_execution_receipt_gate_keys = ["manual_execution_receipt_gate", "manual_execution_receipt_ledger_gate", "manual_execution_receipt_scope_gate", "manual_execution_receipt_acknowledgement_gate", "manual_execution_receipt_replay_gate", "manual_execution_receipt_operator_review_gate"]
    if OUT_MANUAL_EXECUTION_RECEIPTS.exists() and OUT_MANUAL_EXECUTION_RECEIPTS_REPLAY.exists() and OUT_MANUAL_EXECUTION_RECEIPTS_LINEAGE.exists() and OUT_MANUAL_EXECUTION_RECEIPTS_DIAGNOSTICS.exists():
        mer = json.loads(OUT_MANUAL_EXECUTION_RECEIPTS.read_text())
        mer_replay = json.loads(OUT_MANUAL_EXECUTION_RECEIPTS_REPLAY.read_text())
        mer_diag = json.loads(OUT_MANUAL_EXECUTION_RECEIPTS_DIAGNOSTICS.read_text())
        mer_validator = mer.get("validator", {})
        replay_match = bool(mer_replay.get("deterministic_match"))
        authority = mer.get("receipt", {}).get("authority", {})
        authority_mutation = any(bool(v) for v in authority.values()) if isinstance(authority, dict) else True
        critical_unresolved = any(d.get("severity") == "critical" and not d.get("resolved", False) for d in mer_diag)
        base_failed = mer.get("status") != "passed" or mer_validator.get("status") == "failed" or not replay_match or critical_unresolved or authority_mutation
        gate_results = {g.get("gate"): g.get("passed") for g in mer_validator.get("gate_results", []) if g.get("gate")}
        overlay_governance_gates.update({gate: "failed" if base_failed or gate_results.get(gate) is False else ("passed" if gate_results.get(gate) is True else "governed_runtime_delegated") for gate in manual_execution_receipt_gate_keys})
        ms = mer.get("manual_execution_receipt_summary", {})
        manual_execution_receipt_summary = {**manual_execution_receipt_summary, **ms, "replay_matches": replay_match, "authority_locked": not authority_mutation}
    else:
        overlay_governance_gates.update({gate: "not_computable" for gate in manual_execution_receipt_gate_keys})


    external_action_proposal_summary = {"proposal_count": 0, "blocked_proposals": 0, "readiness_posture": 0.0, "unresolved_diagnostics": 0, "replay_matches": False, "governance_restricted": True, "authority_locked": True, "projection_only": True, "inference_authority": False}
    manual_action_custody_summary = {"custody_status": "custody_pending", "handoff_count": 0, "acknowledgement_count": 0, "escalation_required": True, "unresolved_diagnostics": 1, "replay_matches": False, "authority_locked": False}
    manual_action_custody_gate_keys = ["manual_action_custody_gate", "manual_action_handoff_gate", "manual_action_acknowledgement_gate", "manual_action_escalation_gate", "manual_action_replay_gate", "manual_action_operator_review_gate"]
    external_action_gate_keys = ["external_action_proposal_gate", "external_action_category_gate", "external_action_constraint_gate", "external_action_readiness_gate", "external_action_governance_gate", "external_action_replay_gate", "external_action_operator_review_gate"]
    if OUT_MANUAL_ACTION_CUSTODY.exists() and OUT_MANUAL_ACTION_CUSTODY_REPLAY.exists() and OUT_MANUAL_ACTION_CUSTODY_LINEAGE.exists() and OUT_MANUAL_ACTION_CUSTODY_DIAGNOSTICS.exists():
        mac = json.loads(OUT_MANUAL_ACTION_CUSTODY.read_text())
        mac_replay = json.loads(OUT_MANUAL_ACTION_CUSTODY_REPLAY.read_text())
        mac_diag = json.loads(OUT_MANUAL_ACTION_CUSTODY_DIAGNOSTICS.read_text())
        mac_validator = mac.get("validator", {})
        replay_match = bool(mac_replay.get("deterministic_match"))
        authority = mac.get("custody", {}).get("authority", {})
        authority_mutation = any(bool(v) for v in authority.values()) if isinstance(authority, dict) else True
        critical_unresolved = any(d.get("severity") == "critical" and not d.get("resolved", False) for d in mac_diag)
        base_failed = mac.get("status") != "passed" or mac_validator.get("status") == "failed" or not replay_match or critical_unresolved or authority_mutation
        gate_results = {g.get("gate"): g.get("passed") for g in mac_validator.get("gate_results", []) if g.get("gate")}
        overlay_governance_gates.update({gate: "failed" if base_failed or gate_results.get(gate) is False else ("passed" if gate_results.get(gate) is True else "governed_runtime_delegated") for gate in manual_action_custody_gate_keys})
        ms = mac.get("manual_action_custody_summary", {})
        manual_action_custody_summary = {**manual_action_custody_summary, **ms, "replay_matches": replay_match, "authority_locked": not authority_mutation}
    if OUT_EXTERNAL_ACTION_PROPOSALS.exists():
        eap = json.loads(OUT_EXTERNAL_ACTION_PROPOSALS.read_text())
        external_action_proposal_summary = {**external_action_proposal_summary, **eap.get("external_action_proposal_summary", {})}
        overlay_governance_gates["external_action_proposal_gate"] = eap.get("proposal", {}).get("status", "not_computable")
        overlay_governance_gates["external_action_category_gate"] = eap.get("category", {}).get("status", "not_computable")
        overlay_governance_gates["external_action_constraint_gate"] = eap.get("constraint", {}).get("status", "not_computable")
        overlay_governance_gates["external_action_readiness_gate"] = eap.get("readiness", {}).get("status", "not_computable")
        overlay_governance_gates["external_action_governance_gate"] = eap.get("governance", {}).get("status", "not_computable")
        overlay_governance_gates["external_action_replay_gate"] = eap.get("replay", {}).get("status", "not_computable")
        overlay_governance_gates["external_action_operator_review_gate"] = eap.get("operator_review", {}).get("status", "not_computable")
    else:
        overlay_governance_gates.update({gate: "not_computable" for gate in manual_action_custody_gate_keys})
    if not OUT_EXTERNAL_ACTION_PROPOSALS.exists():
        overlay_governance_gates.update({gate: "not_computable" for gate in external_action_gate_keys})

    proposal_sandbox_routing_summary = {"route_count": 0, "blocked_routes": 0, "eligible_routes": 0, "lane_type": "not_computable", "unresolved_diagnostics": 0, "replay_matches": False, "governance_restricted": True, "authority_locked": True}
    proposal_sandbox_gate_keys = ["proposal_sandbox_route_gate", "proposal_sandbox_lane_gate", "proposal_sandbox_constraint_gate", "proposal_sandbox_eligibility_gate", "proposal_sandbox_governance_gate", "proposal_sandbox_replay_gate", "proposal_sandbox_operator_review_gate"]
    if OUT_PROPOSAL_SANDBOX_ROUTING.exists() and OUT_PROPOSAL_SANDBOX_ROUTING_REPLAY.exists() and OUT_PROPOSAL_SANDBOX_ROUTING_LINEAGE.exists() and OUT_PROPOSAL_SANDBOX_ROUTING_DIAGNOSTICS.exists():
        psr = json.loads(OUT_PROPOSAL_SANDBOX_ROUTING.read_text())
        psr_replay = json.loads(OUT_PROPOSAL_SANDBOX_ROUTING_REPLAY.read_text())
        psr_diag = json.loads(OUT_PROPOSAL_SANDBOX_ROUTING_DIAGNOSTICS.read_text())
        proposal_sandbox_routing_summary = {**proposal_sandbox_routing_summary, **psr.get("proposal_sandbox_routing_summary", {})}
        proposal_sandbox_routing_summary["lane_type"] = psr.get("lane", {}).get("lane_type", "not_computable")
        replay_match = bool(psr_replay.get("deterministic_match"))
        critical_unresolved = any(d.get("severity") == "critical" and not d.get("resolved", False) for d in psr_diag)
        authority = psr.get("route", {}).get("authority", {})
        authority_mutation = any(bool(v) for v in authority.values()) if isinstance(authority, dict) else True
        base_failed = psr.get("status") != "passed" or not replay_match or critical_unresolved or authority_mutation
        overlay_governance_gates.update({
            "proposal_sandbox_route_gate": "failed" if base_failed else psr.get("route", {}).get("status", "passed"),
            "proposal_sandbox_lane_gate": "failed" if base_failed else psr.get("lane", {}).get("status", "passed"),
            "proposal_sandbox_constraint_gate": "failed" if base_failed else psr.get("constraint", {}).get("status", "passed"),
            "proposal_sandbox_eligibility_gate": "failed" if base_failed else psr.get("eligibility", {}).get("status", "passed"),
            "proposal_sandbox_governance_gate": "failed" if base_failed else psr.get("governance", {}).get("status", "passed"),
            "proposal_sandbox_replay_gate": "failed" if base_failed else psr.get("replay", {}).get("status", "passed"),
            "proposal_sandbox_operator_review_gate": "failed" if base_failed else psr.get("operator_review", {}).get("status", "passed"),
        })
    else:
        overlay_governance_gates.update({gate: "not_computable" for gate in proposal_sandbox_gate_keys})

    proposal_sandbox_evaluation_summary = {"evaluation_count": 0, "blocked_evaluations": 0, "evaluation_score": 0.0, "unresolved_diagnostics": 0, "replay_matches": False, "governance_restricted": True, "authority_locked": True}
    proposal_sandbox_evaluation_gate_keys = ["proposal_sandbox_evaluation_gate", "proposal_sandbox_score_gate", "proposal_sandbox_rationale_gate", "proposal_sandbox_restriction_gate", "proposal_sandbox_replay_gate", "proposal_sandbox_operator_review_gate"]
    if OUT_PROPOSAL_SANDBOX_EVALUATION.exists() and OUT_PROPOSAL_SANDBOX_EVALUATION_REPLAY.exists() and OUT_PROPOSAL_SANDBOX_EVALUATION_LINEAGE.exists() and OUT_PROPOSAL_SANDBOX_EVALUATION_DIAGNOSTICS.exists():
        pse = json.loads(OUT_PROPOSAL_SANDBOX_EVALUATION.read_text())
        pse_replay = json.loads(OUT_PROPOSAL_SANDBOX_EVALUATION_REPLAY.read_text())
        pse_diag = json.loads(OUT_PROPOSAL_SANDBOX_EVALUATION_DIAGNOSTICS.read_text())
        proposal_sandbox_evaluation_summary = {**proposal_sandbox_evaluation_summary, **pse.get("proposal_sandbox_evaluation_summary", {})}
        replay_match = bool(pse_replay.get("deterministic_match"))
        critical_unresolved = any(d.get("severity") == "critical" and not d.get("resolved", False) for d in pse_diag)
        authority = pse.get("evaluation", {}).get("authority", {})
        authority_mutation = any(bool(v) for v in authority.values()) if isinstance(authority, dict) else True
        base_failed = pse.get("status") != "passed" or not replay_match or critical_unresolved or authority_mutation
        overlay_governance_gates.update({
            "proposal_sandbox_evaluation_gate": "failed" if base_failed else pse.get("evaluation", {}).get("status", "passed"),
            "proposal_sandbox_score_gate": "failed" if base_failed else pse.get("score", {}).get("status", "passed"),
            "proposal_sandbox_rationale_gate": "failed" if base_failed else pse.get("rationale", {}).get("status", "passed"),
            "proposal_sandbox_restriction_gate": "failed" if base_failed else pse.get("restriction", {}).get("status", "passed"),
            "proposal_sandbox_replay_gate": "failed" if base_failed else pse.get("replay", {}).get("status", "passed"),
            "proposal_sandbox_operator_review_gate": "failed" if base_failed else pse.get("operator_review", {}).get("status", "passed"),
        })
    else:
        overlay_governance_gates.update({gate: "not_computable" for gate in proposal_sandbox_evaluation_gate_keys})

    proposal_decision_bridge_summary = {"bridge_count": 0, "blocked_bridges": 0, "decision_readiness": 0.0, "unresolved_diagnostics": 0, "replay_matches": False, "governance_restricted": True, "authority_locked": True}
    proposal_decision_bridge_gate_keys = ["proposal_decision_bridge_gate", "proposal_decision_input_gate", "proposal_decision_rationale_gate", "proposal_decision_restriction_gate", "proposal_decision_replay_gate", "proposal_decision_operator_review_gate"]
    if OUT_PROPOSAL_DECISION_BRIDGE.exists() and OUT_PROPOSAL_DECISION_BRIDGE_REPLAY.exists() and OUT_PROPOSAL_DECISION_BRIDGE_LINEAGE.exists() and OUT_PROPOSAL_DECISION_BRIDGE_DIAGNOSTICS.exists():
        pdb = json.loads(OUT_PROPOSAL_DECISION_BRIDGE.read_text())
        pdb_replay = json.loads(OUT_PROPOSAL_DECISION_BRIDGE_REPLAY.read_text())
        pdb_diag = json.loads(OUT_PROPOSAL_DECISION_BRIDGE_DIAGNOSTICS.read_text())
        proposal_decision_bridge_summary = {**proposal_decision_bridge_summary, **pdb.get("proposal_decision_bridge_summary", {})}
        replay_match = bool(pdb_replay.get("deterministic_match"))
        critical_unresolved = any(d.get("severity") == "critical" and not d.get("resolved", False) for d in pdb_diag)
        authority = pdb.get("bridge", {}).get("authority", {})
        authority_mutation = any(bool(v) for v in authority.values()) if isinstance(authority, dict) else True
        base_failed = pdb.get("status") != "passed" or not replay_match or critical_unresolved or authority_mutation
        overlay_governance_gates.update({
            "proposal_decision_bridge_gate": "failed" if base_failed else pdb.get("bridge", {}).get("status", "passed"),
            "proposal_decision_input_gate": "failed" if base_failed else pdb.get("decision_input", {}).get("status", "passed"),
            "proposal_decision_rationale_gate": "failed" if base_failed else pdb.get("rationale", {}).get("status", "passed"),
            "proposal_decision_restriction_gate": "failed" if base_failed else pdb.get("restriction", {}).get("status", "passed"),
            "proposal_decision_replay_gate": "failed" if base_failed else pdb.get("replay", {}).get("status", "passed"),
            "proposal_decision_operator_review_gate": "failed" if base_failed else pdb.get("operator_review", {}).get("status", "passed"),
        })
    else:
        overlay_governance_gates.update({gate: "not_computable" for gate in proposal_decision_bridge_gate_keys})

    human_decision_ledger_summary = {"decision_count": 0, "deferred_decisions": 0, "blocked_decisions": 0, "unresolved_diagnostics": 0, "replay_matches": False, "governance_restricted": True, "authority_locked": True}
    human_decision_gate_keys = ["human_decision_ledger_gate", "human_decision_rationale_gate", "human_decision_blocker_gate", "human_decision_deferral_gate", "human_decision_replay_gate", "human_decision_operator_review_gate"]
    if OUT_HUMAN_DECISION_LEDGER.exists() and OUT_HUMAN_DECISION_LEDGER_REPLAY.exists() and OUT_HUMAN_DECISION_LEDGER_LINEAGE.exists() and OUT_HUMAN_DECISION_LEDGER_DIAGNOSTICS.exists():
        hdl = json.loads(OUT_HUMAN_DECISION_LEDGER.read_text())
        hdl_replay = json.loads(OUT_HUMAN_DECISION_LEDGER_REPLAY.read_text())
        hdl_diag = json.loads(OUT_HUMAN_DECISION_LEDGER_DIAGNOSTICS.read_text())
        human_decision_ledger_summary = {**human_decision_ledger_summary, **hdl.get("human_decision_ledger_summary", {})}
        replay_match = bool(hdl_replay.get("deterministic_match"))
        critical_unresolved = any(d.get("severity") == "critical" and not d.get("resolved", False) for d in hdl_diag)
        authority = hdl.get("decision", {}).get("authority", {})
        authority_mutation = any(bool(v) for v in authority.values()) if isinstance(authority, dict) else True
        base_failed = hdl.get("status") != "passed" or not replay_match or critical_unresolved or authority_mutation
        overlay_governance_gates.update({
            "human_decision_ledger_gate": "failed" if base_failed else hdl.get("decision", {}).get("status", "passed"),
            "human_decision_rationale_gate": "failed" if base_failed else hdl.get("rationale", {}).get("status", "passed"),
            "human_decision_blocker_gate": "failed" if base_failed else hdl.get("blocker", {}).get("status", "passed"),
            "human_decision_deferral_gate": "failed" if base_failed else hdl.get("deferral", {}).get("status", "passed"),
            "human_decision_replay_gate": "failed" if base_failed else hdl.get("replay", {}).get("status", "passed"),
            "human_decision_operator_review_gate": "failed" if base_failed else hdl.get("operator_review", {}).get("status", "passed"),
        })
    else:
        overlay_governance_gates.update({gate: "not_computable" for gate in human_decision_gate_keys})

    human_decision_continuity_summary = {"continuity_chain_count": 0, "deferred_chains": 0, "blocked_chains": 0, "unresolved_diagnostics": 0, "replay_matches": False, "governance_restricted": True, "authority_locked": True}
    human_decision_continuity_gate_keys = ["human_decision_continuity_chain_gate", "human_decision_continuity_inheritance_gate", "human_decision_continuity_deferral_gate", "human_decision_continuity_blocker_gate", "human_decision_continuity_replay_gate", "human_decision_continuity_operator_review_gate"]
    if OUT_HUMAN_DECISION_CONTINUITY.exists() and OUT_HUMAN_DECISION_CONTINUITY_REPLAY.exists() and OUT_HUMAN_DECISION_CONTINUITY_LINEAGE.exists() and OUT_HUMAN_DECISION_CONTINUITY_DIAGNOSTICS.exists():
        hdc = json.loads(OUT_HUMAN_DECISION_CONTINUITY.read_text())
        hdc_replay = json.loads(OUT_HUMAN_DECISION_CONTINUITY_REPLAY.read_text())
        hdc_diag = json.loads(OUT_HUMAN_DECISION_CONTINUITY_DIAGNOSTICS.read_text())
        human_decision_continuity_summary = {**human_decision_continuity_summary, **hdc.get("human_decision_continuity_summary", {})}
        replay_match = bool(hdc_replay.get("deterministic_match"))
        critical_unresolved = any(d.get("severity") == "critical" and not d.get("resolved", False) for d in hdc_diag)
        authority = hdc.get("chain", {}).get("authority", {})
        authority_mutation = any(bool(v) for v in authority.values()) if isinstance(authority, dict) else True
        base_failed = hdc.get("status") != "passed" or not replay_match or critical_unresolved or authority_mutation
        overlay_governance_gates.update({
            "human_decision_continuity_chain_gate": "failed" if base_failed else hdc.get("chain", {}).get("status", "passed"),
            "human_decision_continuity_inheritance_gate": "failed" if base_failed else hdc.get("inheritance", {}).get("status", "passed"),
            "human_decision_continuity_deferral_gate": "failed" if base_failed else hdc.get("deferral", {}).get("status", "passed"),
            "human_decision_continuity_blocker_gate": "failed" if base_failed else hdc.get("blocker", {}).get("status", "passed"),
            "human_decision_continuity_replay_gate": "failed" if base_failed else hdc.get("replay", {}).get("status", "passed"),
            "human_decision_continuity_operator_review_gate": "failed" if base_failed else hdc.get("operator_review", {}).get("status", "passed"),
        })
    else:
        overlay_governance_gates.update({gate: "not_computable" for gate in human_decision_continuity_gate_keys})

    summary = _build_summary(
        results,
        milestone_registry.active_milestone,
        milestone_validation,
        milestone_registry.status,
        overlay_governance_gates,
    )
    canary_summary = {
        "active_canary_overlays": 0,
        "replay_matches": 0,
        "replay_failures": 0,
        "rollback_ready": 0,
        "rollback_events": 0,
        "stabilization_state": "unstable",
        "blocked_routes": 0,
        "pending_reviews": 0,
    }
    if OUT_CANARY.exists():
        canary = json.loads(OUT_CANARY.read_text())
        canary_summary = {
            "active_canary_overlays": 1,
            "replay_matches": 1
            if canary.get("replay", {}).get("deterministic_match")
            else 0,
            "replay_failures": len(
                canary.get("replay", {}).get("mismatched_routes", [])
            ),
            "rollback_ready": 1
            if canary.get("calibration", {}).get("rollback_readiness")
            else 0,
            "rollback_events": 1
            if canary.get("rollback", {}).get("rollback_complete")
            else 0,
            "stabilization_state": canary.get("stabilization", {}).get(
                "stabilization_state", "unstable"
            ),
            "blocked_routes": len(canary.get("routing", {}).get("blocked_routes", [])),
            "pending_reviews": len(
                canary.get("operator_review", {}).get("pending_actions", [])
            ),
        }

    overlay_observability_summary = {
        "fusion_packets": 0,
        "replay_matches": 0,
        "replay_failures": 0,
        "rollback_count": 0,
        "blocked_routes": 0,
        "diagnostic_count": 0,
        "critical_diagnostics": 0,
        "stability_state": "unstable",
        "pending_reviews": 0,
    }
    if OUT_OVERLAY_OBS.exists():
        ov = json.loads(OUT_OVERLAY_OBS.read_text())
        overlay_observability_summary = {
            "fusion_packets": 1,
            "replay_matches": 1
            if ov.get("replay", {}).get("deterministic_match")
            else 0,
            "replay_failures": len(ov.get("replay", {}).get("mismatched_packets", [])),
            "rollback_count": ov.get("telemetry", {}).get("rollback_count", 0),
            "blocked_routes": ov.get("telemetry", {}).get("blocked_route_count", 0),
            "diagnostic_count": len(ov.get("diagnostics", [])),
            "critical_diagnostics": sum(
                1 for d in ov.get("diagnostics", []) if d.get("severity") == "critical"
            ),
            "stability_state": ov.get("stability", {}).get(
                "stability_state", "unstable"
            ),
            "pending_reviews": len(
                ov.get("operator_review", {}).get("pending_actions", [])
            ),
        }

    canary_scheduler_summary = {
        "policy_packets": 0,
        "eligible_overlays": 0,
        "blocked_overlays": 0,
        "proposed_schedules": 0,
        "replay_matches": 0,
        "replay_failures": 0,
        "pending_reviews": 0,
        "blocked_reasons": [],
    }
    if OUT_CANARY_SCHED.exists():
        cs = json.loads(OUT_CANARY_SCHED.read_text())
        elig = cs.get("eligibility", {})
        canary_scheduler_summary = {
            "policy_packets": 1,
            "eligible_overlays": 1 if elig.get("eligible") else 0,
            "blocked_overlays": 0 if elig.get("eligible") else 1,
            "proposed_schedules": 1
            if cs.get("schedule", {}).get("schedule_status") == "proposed"
            else 0,
            "replay_matches": 1
            if cs.get("replay", {}).get("deterministic_match")
            else 0,
            "replay_failures": len(cs.get("replay", {}).get("mismatched_windows", [])),
            "pending_reviews": len(
                cs.get("operator_review", {}).get("pending_actions", [])
            ),
            "blocked_reasons": elig.get("blocked_reasons", []),
        }

    with profiler.measure("projection_generation", "build_projection_packet"):
        projection = build_projection_packet(
            registry,
            results,
            queue,
            continuity if isinstance(continuity, dict) else continuity.model_dump(),
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
            overlay_containment_summary=overlay_containment_summary,
            overlay_resolution_summary=overlay_resolution_summary,
            overlay_readiness_summary=overlay_readiness_summary,
            overlay_firewall_summary=overlay_firewall_summary,
            operator_queue_summary=operator_queue_summary,
            review_continuity_summary=review_continuity_summary,
            review_resolution_summary=review_resolution_summary,
            manual_execution_summary=manual_execution_summary,
            manual_execution_receipt_summary=manual_execution_receipt_summary,
            manual_action_custody_summary=manual_action_custody_summary,
            external_action_proposal_summary=external_action_proposal_summary,
            proposal_sandbox_routing_summary=proposal_sandbox_routing_summary,
            proposal_sandbox_evaluation_summary=proposal_sandbox_evaluation_summary,
            proposal_decision_bridge_summary=proposal_decision_bridge_summary,
            human_decision_ledger_summary=human_decision_ledger_summary,
            human_decision_continuity_summary=human_decision_continuity_summary,
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

    with profiler.measure("validation_generation", "write_validation_outputs"):
        write_canonical_json(
            OUT_VALIDATION,
            {
                "schema_version": "DoctrineValidationRun.v1",
                "contract_count": len(results),
                "results": results,
                "summary": summary,
            },
        )
        write_canonical_json(OUT_QUEUE, queue)
        write_canonical_json(OUT_MILESTONE_REG, milestone_registry.model_dump())
        write_canonical_json(OUT_MILESTONE_VAL, milestone_validation.model_dump())
    with profiler.measure("projection_generation", "write_projection_output"):
        write_canonical_json(OUT_AAL_VIZ, projection)
    validation_correlation_id = stable_correlation_id(
        "validation_generation",
        artifact_path=OUT_VALIDATION,
        context={
            "contracts_dir": CONTRACTS_DIR.as_posix(),
            "rune_catalog_path": RUNE_CATALOG_PATH.as_posix(),
            "routes_dir": ROUTES_DIR.as_posix(),
        },
    )
    profiler.record_correlation("validation_generation", validation_correlation_id)
    log_event(
        diagnostics_logger,
        "INFO",
        "validation_generation_completed",
        artifact_path=OUT_VALIDATION.as_posix(),
        correlation_id=validation_correlation_id,
        contract_count=len(results),
        summary_status=summary["status"],
        seal_recommendation=summary["seal_recommendation"],
    )
    projection_correlation_id = stable_correlation_id(
        "projection_generation",
        artifact_path=OUT_AAL_VIZ,
        context={"validation_artifact_path": OUT_VALIDATION.as_posix()},
    )
    profiler.record_correlation("projection_generation", projection_correlation_id)
    log_event(
        diagnostics_logger,
        "INFO",
        "projection_generation_completed",
        artifact_path=OUT_AAL_VIZ.as_posix(),
        correlation_id=projection_correlation_id,
        projection_only=projection.get("projection_only"),
        inference_authority=projection.get("inference_authority"),
        validation_artifact_path=OUT_VALIDATION.as_posix(),
    )
    profiler.write()


if __name__ == "__main__":
    main()
