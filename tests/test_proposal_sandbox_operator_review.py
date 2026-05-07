from core.proposal_sandbox_routing.runtime import run_proposal_sandbox_routing

def test_operator_review_exists() -> None:
    packet = run_proposal_sandbox_routing([], [], [], [])
    assert packet["operator_review"]["route_count"] == 1
