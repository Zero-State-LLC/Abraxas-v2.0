from core.human_decision_ledger.escalations import HumanDecisionEscalationPacket

def test_escalation_hash() -> None:
    assert HumanDecisionEscalationPacket.compute_hash("d", False, "x")
