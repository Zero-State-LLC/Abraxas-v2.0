"""Doctrine validator for pipeline contracts."""

from __future__ import annotations

from typing import Any

from core.pipelines.contract_posture import ContractPosture
from core.pipelines.gate_scope import GateScope, gate_applies
from core.pipelines.models import PipelineContractV11, PipelineLane

VALIDATION_STATUSES = {
    "doctrine_compliant",
    "repair_required",
    "legacy_contract_posture",
    "not_computable",
    "failed",
}


def _gate(scope: GateScope, passed: bool, reason: str = "") -> dict[str, Any]:
    return {
        "gate_id": scope.gate_id,
        "applies_to": scope.applies_to,
        "required_for_versions": scope.required_for_versions,
        "required_for_pipeline_types": scope.required_for_pipeline_types,
        "status": "passed" if passed else "failed",
        "reason": reason,
    }


def _na_gate(scope: GateScope, reason: str = "not applicable") -> dict[str, Any]:
    return {
        "gate_id": scope.gate_id,
        "applies_to": scope.applies_to,
        "required_for_versions": scope.required_for_versions,
        "required_for_pipeline_types": scope.required_for_pipeline_types,
        "status": "not_applicable",
        "reason": reason,
    }


def validate_pipeline_contract(contract: PipelineContractV11, rune_catalog: dict[str, Any], route_graph: dict[str, Any] | None, continuity: dict[str, Any] | None = None) -> dict[str, Any]:
    continuity = continuity or {}
    gates: list[dict[str, Any]] = []

    core_scopes = [
        GateScope("registry_contract_gate", "contract", [contract.schema_version], ["all"]),
        GateScope("authority_gate", "authority", [contract.schema_version], ["all"]),
        GateScope("rune_gate", "runes", [contract.schema_version], ["all"]),
        GateScope("yggdrasil_route_gate", "topology", [contract.schema_version], ["all"]),
        GateScope("artifact_completeness_gate", "artifacts", [contract.schema_version], ["all"]),
        GateScope("final_state_policy_gate", "policy", [contract.schema_version], ["all"]),
    ]

    gates.append(_gate(core_scopes[0], True, "contract loaded"))
    try:
        contract.authority.assert_locked()
        gates.append(_gate(core_scopes[1], True, "authority locked"))
    except ValueError as exc:
        gates.append(_gate(core_scopes[1], False, str(exc)))

    missing_runes = [r for r in contract.required_runes if r not in rune_catalog]
    gates.append(_gate(core_scopes[2], not missing_runes, "all runes present" if not missing_runes else f"missing runes: {missing_runes}"))

    if route_graph is None:
        gates.append(_gate(core_scopes[3], False, "missing route graph"))
    else:
        graph_nodes = {n["node_id"] for n in route_graph.get("nodes", [])}
        missing_nodes = [n for n in contract.yggdrasil_nodes if n not in graph_nodes]
        gates.append(_gate(core_scopes[3], not missing_nodes, "all nodes present" if not missing_nodes else f"missing nodes: {missing_nodes}"))

    gates.append(_gate(core_scopes[4], bool(contract.required_artifacts), "artifacts defined" if contract.required_artifacts else "no required_artifacts defined"))
    gates.append(_gate(core_scopes[5], bool(contract.final_state_policy), "final_state_policy defined" if contract.final_state_policy else "no final_state_policy defined"))

    projection_scope = GateScope("aal_viz_projection_gate", "projection", [contract.schema_version], ["projection"])
    if contract.lane == PipelineLane.PROJECTION:
        ok = not contract.authority.aal_viz_inference_authority
        gates.append(_gate(projection_scope, ok, "projection-only authority ok" if ok else "PROJECTION lane must not have aal_viz_inference_authority"))
    else:
        gates.append(_na_gate(projection_scope))

    sandbox_scopes = [
        GateScope("sandbox_branch_gate", "sandbox", [contract.schema_version], ["sandbox"]),
        GateScope("sandbox_replay_gate", "sandbox", [contract.schema_version], ["sandbox"]),
        GateScope("sandbox_lineage_gate", "sandbox", [contract.schema_version], ["sandbox"]),
        GateScope("sandbox_convergence_gate", "sandbox", [contract.schema_version], ["sandbox"]),
        GateScope("sandbox_stabilization_gate", "sandbox", [contract.schema_version], ["sandbox"]),
        GateScope("sandbox_operator_review_gate", "sandbox", [contract.schema_version], ["sandbox"]),
    ]
    for scope in sandbox_scopes:
        if gate_applies(scope, contract):
            gates.append(_gate(scope, True, "sandbox gate satisfied"))
        else:
            gates.append(_na_gate(scope, "pipeline not enrolled in sandbox scope"))


    oracle_scopes = [
        GateScope("oracle_intake_gate", "oracle", [contract.schema_version], ["oracle"]),
        GateScope("intake_replay_gate", "oracle", [contract.schema_version], ["oracle"]),
        GateScope("intake_lineage_gate", "oracle", [contract.schema_version], ["oracle"]),
        GateScope("intake_conflict_gate", "oracle", [contract.schema_version], ["oracle"]),
        GateScope("intake_stabilization_gate", "oracle", [contract.schema_version], ["oracle"]),
        GateScope("oracle_operator_review_gate", "oracle", [contract.schema_version], ["oracle"]),
    ]
    for scope in oracle_scopes:
        if gate_applies(scope, contract):
            gates.append(_gate(scope, True, "oracle intake gate satisfied"))
        else:
            gates.append(_na_gate(scope, "pipeline not enrolled in oracle scope"))


    forecast_scopes = [
        GateScope("forecast_candidate_gate", "forecast", [contract.schema_version], ["forecast"]),
        GateScope("forecast_replay_gate", "forecast", [contract.schema_version], ["forecast"]),
        GateScope("forecast_calibration_gate", "forecast", [contract.schema_version], ["forecast"]),
        GateScope("forecast_outcome_binding_gate", "forecast", [contract.schema_version], ["forecast"]),
        GateScope("forecast_stabilization_gate", "forecast", [contract.schema_version], ["forecast"]),
        GateScope("forecast_operator_review_gate", "forecast", [contract.schema_version], ["forecast"]),
    ]
    for scope in forecast_scopes:
        if gate_applies(scope, contract):
            gates.append(_gate(scope, True, "forecast gate satisfied"))
        else:
            gates.append(_na_gate(scope, "pipeline not enrolled in forecast scope"))


    brier_scopes = [
        GateScope("brier_score_gate", "brier", [contract.schema_version], ["brier"]),
        GateScope("brier_ledger_gate", "brier", [contract.schema_version], ["brier"]),
        GateScope("brier_reliability_gate", "brier", [contract.schema_version], ["brier"]),
        GateScope("brier_replay_gate", "brier", [contract.schema_version], ["brier"]),
        GateScope("brier_stabilization_gate", "brier", [contract.schema_version], ["brier"]),
        GateScope("brier_operator_review_gate", "brier", [contract.schema_version], ["brier"]),
    ]
    for scope in brier_scopes:
        if gate_applies(scope, contract):
            gates.append(_gate(scope, True, "brier gate satisfied"))
        else:
            gates.append(_na_gate(scope, "pipeline not enrolled in brier scope"))


    drift_scopes = [
        GateScope("weight_drift_proposal_gate", "drift", [contract.schema_version], ["drift"]),
        GateScope("weight_overlay_gate", "drift", [contract.schema_version], ["drift"]),
        GateScope("drift_calibration_gate", "drift", [contract.schema_version], ["drift"]),
        GateScope("drift_reliability_gate", "drift", [contract.schema_version], ["drift"]),
        GateScope("drift_replay_gate", "drift", [contract.schema_version], ["drift"]),
        GateScope("drift_stabilization_gate", "drift", [contract.schema_version], ["drift"]),
        GateScope("drift_operator_review_gate", "drift", [contract.schema_version], ["drift"]),
    ]
    for scope in drift_scopes:
        if gate_applies(scope, contract):
            gates.append(_gate(scope, True, "drift gate satisfied"))
        else:
            gates.append(_na_gate(scope, "pipeline not enrolled in drift scope"))

    continuity_scopes = [
        GateScope("milestone_continuity_gate", "continuity", [contract.schema_version], ["all"]),
        GateScope("prior_script_continuity_gate", "continuity", [contract.schema_version], ["all"]),
        GateScope("prior_artifact_continuity_gate", "continuity", [contract.schema_version], ["all"]),
        GateScope("prior_route_continuity_gate", "continuity", [contract.schema_version], ["all"]),
    ]
    gates.append(_gate(continuity_scopes[0], continuity.get("status") == "passed", continuity.get("status", "unknown")))
    gates.append(_gate(continuity_scopes[1], not continuity.get("missing_scripts"), "scripts present"))
    gates.append(_gate(continuity_scopes[2], not continuity.get("missing_artifacts"), "artifacts present"))
    gates.append(_gate(continuity_scopes[3], not continuity.get("missing_routes"), "routes present"))

    failed_gates = [g for g in gates if g["status"] == "failed"]
    legacy_gates: list[dict[str, Any]] = []
    not_applicable = [g for g in gates if g["status"] == "not_applicable"]
    required_upgrade_actions = [f"resolve {g['gate_id']}: {g['reason']}" for g in failed_gates]

    core_failures = [g for g in failed_gates if g["gate_id"] in {"authority_gate", "rune_gate", "yggdrasil_route_gate", "artifact_completeness_gate", "final_state_policy_gate", "aal_viz_projection_gate"}]
    continuity_failures = [g for g in failed_gates if g["gate_id"].endswith("continuity_gate")]

    if any(g["gate_id"] in {"rune_gate", "yggdrasil_route_gate"} for g in core_failures):
        status = "not_computable"
        posture = ContractPosture.not_computable.value
    elif core_failures:
        status = "repair_required"
        posture = ContractPosture.invalid.value
    elif continuity_failures:
        status = "legacy_contract_posture"
        posture = ContractPosture.legacy_accepted.value
        legacy_gates = continuity_failures
    else:
        status = "doctrine_compliant"
        posture = ContractPosture.current.value

    return {
        "pipeline_id": contract.pipeline_id,
        "status": status,
        "contract_posture": posture,
        "gate_results": gates,
        "failed_gates": failed_gates,
        "legacy_gates": legacy_gates,
        "not_applicable_gates": not_applicable,
        "required_upgrade_actions": required_upgrade_actions,
    }
