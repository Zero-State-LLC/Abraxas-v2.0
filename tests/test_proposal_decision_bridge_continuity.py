from core.proposal_decision_bridge.continuity import ProposalDecisionContinuityPacket

def test_continuity_hash() -> None:
    assert ProposalDecisionContinuityPacket.compute_hash("b", [], True)
