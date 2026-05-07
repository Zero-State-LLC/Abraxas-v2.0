from core.proposal_sandbox_routing.governance import ProposalSandboxGovernancePacket

def test_governance_hash() -> None:
    assert ProposalSandboxGovernancePacket.compute_hash("r", [], [], True)
