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
) -> dict[str, Any]:
    """Validate a pipeline contract against doctrine rules.

    Returns a dict with pipeline_id, status, and gate_results.
    """
    gates: list[dict[str, Any]] = []

    # 1. Registry/contract gate – contract present
    gates.append(_gate("registry_contract_gate", True, "contract loaded"))

    # 2. Authority gate
    try:
        contract.authority.assert_locked()
        gates.append(_gate("authority_gate", True, "authority locked"))
    except ValueError as exc:
        gates.append(_gate("authority_gate", False, str(exc)))

    # 3. Rune gate – all required runes present in catalog
    missing_runes = [r for r in contract.required_runes if r not in rune_catalog]
    if missing_runes:
        gates.append(_gate("rune_gate", False, f"missing runes: {missing_runes}"))
    else:
        gates.append(_gate("rune_gate", True, "all runes present"))

    # 4. YGGDRASIL route gate
    if route_graph is None:
        gates.append(_gate("yggdrasil_route_gate", False, "missing route graph"))
    else:
        graph_nodes = {n["node_id"] for n in route_graph.get("nodes", [])}
        missing_nodes = [n for n in contract.yggdrasil_nodes if n not in graph_nodes]
        if missing_nodes:
            gates.append(
                _gate("yggdrasil_route_gate", False, f"missing nodes: {missing_nodes}")
            )
        else:
            gates.append(_gate("yggdrasil_route_gate", True, "all nodes present"))

    # 5. Artifact completeness gate
    if not contract.required_artifacts:
        gates.append(_gate("artifact_completeness_gate", False, "no required_artifacts defined"))
    else:
        gates.append(_gate("artifact_completeness_gate", True, "artifacts defined"))

    # 6. AAL-Viz projection gate (PROJECTION lane only)
    if contract.lane == PipelineLane.PROJECTION:
        if contract.authority.aal_viz_inference_authority:
            gates.append(
                _gate(
                    "aal_viz_projection_gate",
                    False,
                    "PROJECTION lane must not have aal_viz_inference_authority",
                )
            )
        else:
            gates.append(_gate("aal_viz_projection_gate", True, "projection-only authority ok"))

    # 7. Final state policy gate
    if not contract.final_state_policy:
        gates.append(_gate("final_state_policy_gate", False, "no final_state_policy defined"))
    else:
        gates.append(_gate("final_state_policy_gate", True, "final_state_policy defined"))

    # Derive overall status
    failed = [g for g in gates if not g["passed"]]
    not_computable_reasons = [
        g for g in failed if "missing rune" in g["reason"] or "missing route" in g["reason"]
    ]

    if not_computable_reasons:
        status = "not_computable"
    elif failed:
        status = "repair_required"
    else:
        status = "doctrine_compliant"

    return {
        "pipeline_id": contract.pipeline_id,
        "status": status,
        "gate_results": gates,
    }
