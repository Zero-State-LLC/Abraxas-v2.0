from core.proposal_sandbox_routing.validators import validate_proposal_sandbox_routing

def test_forbidden_action_fails() -> None:
    out = validate_proposal_sandbox_routing("simulation", "route_proposed", "simulation_lane", ["execute"], True, [], False, False, False, False, False, False)
    assert out["status"] == "failed"
