from core.proposal_decision_bridge.validators import validate_proposal_decision_bridge

def test_replay_mismatch_fails() -> None:
    out = validate_proposal_decision_bridge([], False, [], False, False, False, False, False, False)
    assert out["status"] == "failed"
