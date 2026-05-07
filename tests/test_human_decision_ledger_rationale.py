from core.human_decision_ledger.rationale import HumanDecisionRationalePacket

def test_rationale_hash() -> None:
    assert HumanDecisionRationalePacket.compute_hash("d", "r", [])
