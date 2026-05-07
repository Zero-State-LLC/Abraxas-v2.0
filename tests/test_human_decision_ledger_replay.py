from core.human_decision_ledger.validators import validate_human_decision_ledger

def test_replay_mismatch_fails() -> None:
    out = validate_human_decision_ledger("review_only", False, [], False, False, False, False, False, False)
    assert out["status"] == "failed"
