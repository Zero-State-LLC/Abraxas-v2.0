from core.human_decision_ledger.blockers import HumanDecisionBlockerPacket

def test_blocker_hash() -> None:
    assert HumanDecisionBlockerPacket.compute_hash("d", [], 0)
