from core.observability.timelines import build_runtime_timeline_packet


def test_runtime_timeline_deterministic() -> None:
    run = {"run_id": "x", "scheduler": {"execution_sequence": ["a", "b"]}}
    t1 = build_runtime_timeline_packet(run)
    t2 = build_runtime_timeline_packet(run)
    assert t1.timeline_hash == t2.timeline_hash
