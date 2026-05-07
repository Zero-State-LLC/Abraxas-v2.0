from core.proposal_decision_bridge.validators import validate_proposal_decision_bridge

def test_forbidden_action_fails() -> None:
    out = validate_proposal_decision_bridge(["approve"], True, [], False, False, False, False, False, False)
    assert out["status"] == "failed"
