from core.observability.lineage import build_lineage_trace_packet
from core.observability.validators import validate_lineage_replay


def test_lineage_chain_deterministic() -> None:
    run = {"run_id": "x", "scheduler": {"execution_sequence": ["a", "b"]}}
    t1 = build_lineage_trace_packet(run)
    t2 = build_lineage_trace_packet(run)
    assert t1.trace_id == t2.trace_id


def test_replay_mismatch_invalidates_lineage() -> None:
    run = {"run_id": "x", "scheduler": {"execution_sequence": ["a"]}}
    trace = build_lineage_trace_packet(run).model_dump(mode="json")
    result = validate_lineage_replay(trace, {"status": "failed"})
    assert result["status"] == "failed"
