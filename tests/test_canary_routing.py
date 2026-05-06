from core.canary.routing import CanaryRoutingPacket


def test_deterministic_routing() -> None:
    h = CanaryRoutingPacket.compute_hash(["a"], ["r"], ["s"], ["b"])
    pkt = CanaryRoutingPacket(routing_id="r1", overlay_hashes=["a"], replay_routes=["r"], sandbox_routes=["s"], blocked_routes=["b"], deterministic_routing_hash=h, status="passed")
    assert pkt.deterministic_routing_hash == h
