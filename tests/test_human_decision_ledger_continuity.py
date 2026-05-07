from core.human_decision_ledger.continuity import HumanDecisionContinuityPacket

def test_continuity_hash() -> None:
    assert HumanDecisionContinuityPacket.compute_hash("d", [], True)
