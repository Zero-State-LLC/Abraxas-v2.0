from core.observability.telemetry import build_execution_telemetry_packet


def test_telemetry_deterministic_hash() -> None:
    run = {"run_id": "x", "graph": {"topology_hash": "g"}, "traversal": {"traversal_id": "t"}, "scheduler": {"scheduler_id": "s", "execution_sequence": [], "blocked_nodes": []}, "receipt": {"receipt_id": "r"}, "failures": []}
    p1 = build_execution_telemetry_packet(run)
    p2 = build_execution_telemetry_packet(run)
    assert p1.telemetry_id == p2.telemetry_id
