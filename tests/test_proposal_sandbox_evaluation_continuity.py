from core.proposal_sandbox_evaluation.continuity import ProposalSandboxEvaluationContinuityPacket

def test_continuity_hash() -> None:
    assert ProposalSandboxEvaluationContinuityPacket.compute_hash("h", [], True)
