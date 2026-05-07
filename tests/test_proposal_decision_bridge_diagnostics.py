from core.proposal_decision_bridge.validators import validate_proposal_decision_bridge

def test_critical_diag_fails() -> None:
    out = validate_proposal_decision_bridge([], True, [{"severity":"critical","resolved":False}], False, False, False, False, False, False)
    assert out["status"] == "failed"
