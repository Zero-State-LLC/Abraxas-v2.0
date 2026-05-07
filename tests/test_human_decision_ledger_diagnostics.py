from core.human_decision_ledger.validators import validate_human_decision_ledger

def test_critical_diag_fails() -> None:
    out = validate_human_decision_ledger("review_only", True, [{"severity":"critical","resolved":False}], False, False, False, False, False, False)
    assert out["status"] == "failed"
