from core.proposal_decision_bridge.bridge import ProposalDecisionBridgePacket

def test_bridge_hash() -> None:
    assert ProposalDecisionBridgePacket.compute_hash("e", 0.5)
