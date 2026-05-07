from core.proposal_decision_bridge.runtime import run_proposal_decision_bridge

def test_operator_review_exists() -> None:
    p = run_proposal_decision_bridge([], [], [], [])
    assert p["operator_review"]["bridge_count"] == 1
