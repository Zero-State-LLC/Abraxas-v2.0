from core.proposal_sandbox_routing.routes import ProposalSandboxRoutePacket

def test_route_hash_deterministic() -> None:
    h1 = ProposalSandboxRoutePacket.compute_hash("p", "simulation", "sandbox_only", "lane", [], "route_proposed")
    h2 = ProposalSandboxRoutePacket.compute_hash("p", "simulation", "sandbox_only", "lane", [], "route_proposed")
    assert h1 == h2
