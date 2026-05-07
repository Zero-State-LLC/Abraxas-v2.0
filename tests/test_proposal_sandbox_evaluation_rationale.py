from core.proposal_sandbox_evaluation.rationale import ProposalSandboxRationalePacket

def test_rationale_hash() -> None:
    assert ProposalSandboxRationalePacket.compute_hash("h", "r", [])
