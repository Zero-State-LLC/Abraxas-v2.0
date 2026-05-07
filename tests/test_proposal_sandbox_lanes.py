import pytest
from core.proposal_sandbox_routing.lanes import ProposalSandboxLanePacket

def test_lane_forbidden_overlap() -> None:
    with pytest.raises(ValueError):
        ProposalSandboxLanePacket(lane_id="x", lane_type="simulation_lane", allowed_route_types=["simulation"], forbidden_route_types=["simulation"], deterministic_lane_hash="h", status="failed")
