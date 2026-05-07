from core.proposal_sandbox_routing.eligibility import ProposalSandboxEligibilityPacket

def test_eligibility_hash() -> None:
    assert ProposalSandboxEligibilityPacket.compute_hash("r", "p", "l", True, [])
