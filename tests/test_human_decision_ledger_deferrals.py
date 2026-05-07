from core.human_decision_ledger.deferrals import HumanDecisionDeferralPacket

def test_deferral_hash() -> None:
    assert HumanDecisionDeferralPacket.compute_hash("d", True, "x")
