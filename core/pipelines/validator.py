"""Doctrine validator for pipeline contracts."""

from __future__ import annotations

from typing import Any

from core.pipelines.models import PipelineContractV11, PipelineLane


def _gate(name: str, passed: bool, reason: str = "") -> dict[str, Any]:
    return {"gate": name, "passed": passed, "reason": reason}


def validate_pipeline_contract(
    contract: PipelineContractV11,
    rune_catalog: dict[str, Any],
    route_graph: dict[str, Any] | None,
    continuity: dict[str, Any] | None = None,
) -> dict[str, Any]:
    gates: list[dict[str, Any]] = []
    gates.append(_gate("registry_contract_gate", True, "contract loaded"))
    try:
        contract.authority.assert_locked()
        gates.append(_gate("authority_gate", True, "authority locked"))
    except ValueError as exc:
        gates.append(_gate("authority_gate", False, str(exc)))

    missing_runes = [r for r in contract.required_runes if r not in rune_catalog]
    gates.append(_gate("rune_gate", not missing_runes, "all runes present" if not missing_runes else f"missing runes: {missing_runes}"))

    if route_graph is None:
        gates.append(_gate("yggdrasil_route_gate", False, "missing route graph"))
    else:
        graph_nodes = {n["node_id"] for n in route_graph.get("nodes", [])}
        missing_nodes = [n for n in contract.yggdrasil_nodes if n not in graph_nodes]
        gates.append(_gate("yggdrasil_route_gate", not missing_nodes, "all nodes present" if not missing_nodes else f"missing nodes: {missing_nodes}"))

    gates.append(_gate("artifact_completeness_gate", bool(contract.required_artifacts), "artifacts defined" if contract.required_artifacts else "no required_artifacts defined"))

    if contract.lane == PipelineLane.PROJECTION:
        ok = not contract.authority.aal_viz_inference_authority
        gates.append(_gate("aal_viz_projection_gate", ok, "projection-only authority ok" if ok else "PROJECTION lane must not have aal_viz_inference_authority"))

    gates.append(_gate("final_state_policy_gate", bool(contract.final_state_policy), "final_state_policy defined" if contract.final_state_policy else "no final_state_policy defined"))

    if continuity is not None:
        gates.append(_gate("milestone_continuity_gate", continuity.get("status") == "passed", continuity.get("status", "unknown")))
        gates.append(_gate("prior_script_continuity_gate", not continuity.get("missing_scripts"), "scripts present"))
        gates.append(_gate("prior_artifact_continuity_gate", not continuity.get("missing_artifacts"), "artifacts present"))
        gates.append(_gate("prior_route_continuity_gate", not continuity.get("missing_routes"), "routes present"))

    failed = [g for g in gates if not g["passed"]]
    not_computable = any((g["gate"] == "rune_gate" and not g["passed"]) or (g["gate"] == "yggdrasil_route_gate" and not g["passed"]) for g in gates)
    if not_computable:
        status = "not_computable"
    elif failed:
        status = "repair_required"
    else:
        status = "doctrine_compliant"

    return {"pipeline_id": contract.pipeline_id, "status": status, "gate_results": gates}
