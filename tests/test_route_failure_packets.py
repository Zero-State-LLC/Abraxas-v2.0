from core.yggdrasil.failures import build_route_failure_packet


def test_failure_packet_deterministic() -> None:
    p1 = build_route_failure_packet(graph_hash="g", failure_type="cycle_detected")
    p2 = build_route_failure_packet(graph_hash="g", failure_type="cycle_detected")
    assert p1.failure_id == p2.failure_id
