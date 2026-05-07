from core.proposal_sandbox_routing.validators import validate_proposal_sandbox_routing

def test_replay_mismatch_fails() -> None:
    out = validate_proposal_sandbox_routing("simulation", "route_proposed", "simulation_lane", [], False, [], False, False, False, False, False, False)
    assert out["status"] == "failed"
