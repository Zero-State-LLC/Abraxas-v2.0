from core.observability.validators import validate_lineage_replay


def test_cyclic_lineage_fail_closed() -> None:
    trace = {"nodes": [{"source_hash": "a", "parent_hash": None}, {"source_hash": "a", "parent_hash": "a"}]}
    out = validate_lineage_replay(trace, {"status": "passed"})
    assert out["status"] == "failed"
