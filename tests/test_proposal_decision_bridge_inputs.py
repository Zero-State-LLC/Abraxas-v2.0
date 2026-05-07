from core.proposal_decision_bridge.decision_inputs import ProposalDecisionInputPacket

def test_input_hash() -> None:
    assert ProposalDecisionInputPacket.compute_hash("b", [], 0)
