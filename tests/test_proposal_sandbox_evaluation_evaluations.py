from core.proposal_sandbox_evaluation.evaluations import ProposalSandboxEvaluationPacket

def test_eval_hash_deterministic() -> None:
    assert ProposalSandboxEvaluationPacket.compute_hash("r", "evaluation_recorded") == ProposalSandboxEvaluationPacket.compute_hash("r", "evaluation_recorded")
