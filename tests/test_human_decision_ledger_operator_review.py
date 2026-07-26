from core.human_decision_ledger.runtime import run_human_decision_ledger


def test_operator_review_exists() -> None:
    stub = [{"evidence": "present"}]
    packet = run_human_decision_ledger(stub, stub, stub, stub)
    assert packet["operator_review"]["decision_count"] == 1
