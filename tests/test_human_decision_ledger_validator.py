from core.human_decision_ledger.validators import validate_human_decision_ledger

def test_forbidden_decision_fails() -> None:
    out = validate_human_decision_ledger("approved_live", True, [], False, False, False, False, False, False)
    assert out["status"] == "failed"
