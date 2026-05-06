from __future__ import annotations

from dataclasses import dataclass

from core.pipelines.models import PipelineContractV11


@dataclass(frozen=True)
class GateScope:
    gate_id: str
    applies_to: str
    required_for_versions: list[str]
    required_for_pipeline_types: list[str]


def _pipeline_types(contract: PipelineContractV11) -> set[str]:
    tags = {contract.lane.value.lower(), contract.owner_subsystem.lower(), contract.pipeline_id.lower()}
    if "sandbox" in contract.pipeline_id.lower() or "sandbox" in contract.owner_subsystem.lower():
        tags.add("sandbox")
    return tags


def gate_applies(scope: GateScope, contract: PipelineContractV11) -> bool:
    if "AbraxasPipelineAutomationContract.v1.1" not in scope.required_for_versions:
        return False
    pipeline_types = _pipeline_types(contract)
    return "all" in scope.required_for_pipeline_types or bool(pipeline_types.intersection(scope.required_for_pipeline_types))
