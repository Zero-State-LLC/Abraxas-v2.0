from core.proposal_sandbox_evaluation.scores import ProposalSandboxScorePacket

def test_score_hash() -> None:
    assert ProposalSandboxScorePacket.compute_hash("h", 0.5)
