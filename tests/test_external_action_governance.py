from core.external_action_proposals.governance import ProposalGovernancePacket

def test_governance_hash_deterministic() -> None:
    h = ProposalGovernancePacket.compute_hash("a", True, True)
    assert h == ProposalGovernancePacket.compute_hash("a", True, True)
