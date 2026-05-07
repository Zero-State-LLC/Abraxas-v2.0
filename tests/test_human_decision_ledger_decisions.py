from core.human_decision_ledger.decisions import HumanDecisionLedgerPacket

def test_decision_hash() -> None:
    assert HumanDecisionLedgerPacket.compute_hash("b", "review_only")
