from core.human_decision_ledger.runtime import run_human_decision_ledger

def test_operator_review_exists() -> None:
    p = run_human_decision_ledger([], [], [], [])
    assert p["operator_review"]["decision_count"] == 1
