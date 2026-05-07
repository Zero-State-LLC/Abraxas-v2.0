from core.proposal_decision_bridge.validators import validate_proposal_decision_bridge

def test_lineage_cycle_fails() -> None:
    out = validate_proposal_decision_bridge([], True, [], True, False, False, False, False, False)
    assert out["status"] == "failed"
