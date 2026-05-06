from core.pipelines.gate_scope import GateScope, gate_applies
from core.pipelines.models import Authority, PipelineContractV11, PipelineLane


def _contract(pipeline_id: str, owner: str) -> PipelineContractV11:
    return PipelineContractV11(
        pipeline_id=pipeline_id,
        trigger="t",
        owner_subsystem=owner,
        lane=PipelineLane.SHADOW,
        typed_ir_schema="IR.v1",
        required_runes=["RUNE.INTAKE.QUERY.NORMALIZE"],
        yggdrasil_nodes=["ingest.query.normalize"],
        required_artifacts=["a"],
        final_state_policy=["hold"],
        authority=Authority(),
    )


def test_gate_scope_sandbox_only() -> None:
    scope = GateScope("sandbox_branch_gate", "sandbox", ["AbraxasPipelineAutomationContract.v1.1"], ["sandbox"])
    assert gate_applies(scope, _contract("adaptive_sandbox", "sandbox"))
    assert not gate_applies(scope, _contract("research_intake", "research"))
