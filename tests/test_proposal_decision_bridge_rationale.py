from core.proposal_decision_bridge.rationale import ProposalDecisionRationalePacket

def test_rationale_hash() -> None:
    assert ProposalDecisionRationalePacket.compute_hash("b", "r", [])
