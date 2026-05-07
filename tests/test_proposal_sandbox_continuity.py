from core.proposal_sandbox_routing.continuity import ProposalSandboxContinuityPacket

def test_continuity_hash() -> None:
    assert ProposalSandboxContinuityPacket.compute_hash("r", ["p"], True)
