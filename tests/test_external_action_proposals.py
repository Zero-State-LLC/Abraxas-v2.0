from core.external_action_proposals.proposals import ExternalActionProposalPacket


def test_deterministic_proposal_hash() -> None:
    h1 = ExternalActionProposalPacket.compute_hash("proposed", "review_operator", "x")
    h2 = ExternalActionProposalPacket.compute_hash("proposed", "review_operator", "x")
    assert h1 == h2
