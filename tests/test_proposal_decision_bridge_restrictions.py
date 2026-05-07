from core.proposal_decision_bridge.restrictions import FORBIDDEN_ACTIONS

def test_restrictions_set() -> None:
    assert "approve" in FORBIDDEN_ACTIONS
