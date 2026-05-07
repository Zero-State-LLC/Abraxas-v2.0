from core.proposal_sandbox_routing.validators import validate_proposal_sandbox_routing

def test_critical_diagnostics_fail() -> None:
    out = validate_proposal_sandbox_routing("simulation", "route_proposed", "simulation_lane", [], True, [{"severity": "critical", "resolved": False}], False, False, False, False, False, False)
    assert out["status"] == "failed"
