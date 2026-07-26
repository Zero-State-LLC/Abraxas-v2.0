from __future__ import annotations

import pytest

from core.observability.aggregation import run_observability_pipeline
from core.observability.telemetry_hash import resolve_telemetry_hash
from core.sandbox.runtime import run_adaptive_sandbox
from core.state.runtime import run_state_engine


def test_resolve_nested_observability_telemetry_hash() -> None:
    obs = run_observability_pipeline(
        {"projection": {"a": 1}, "queue": {}, "validation": {}},
        {"replay_hash": "r1"},
        {"graph": {"topology_hash": "t1"}, "scheduler": {"execution_sequence": ["n1"]}},
    )
    resolved = resolve_telemetry_hash(obs)
    assert resolved == obs["projection_snapshot"]["telemetry_hash"]
    assert resolved != "unknown"


def test_resolve_execution_telemetry_id() -> None:
    packet = {
        "telemetry_id": "tele-id-1",
        "executed_node_count": 1,
    }
    assert resolve_telemetry_hash(packet) == "tele-id-1"


def test_unknown_telemetry_hash_fails_closed() -> None:
    with pytest.raises(ValueError, match="refuse unknown fallback"):
        resolve_telemetry_hash({"telemetry_hash": "unknown"})


def test_sandbox_distinct_observability_produces_distinct_payload_hashes() -> None:
    state = {"state_hash": "root"}
    replay = {"replay_hash": "none"}
    topology = {"topology_hash": "topo"}
    obs1 = run_observability_pipeline(
        {"projection": {"a": 1}, "queue": {}, "validation": {}},
        {"replay_hash": "r1"},
        {"graph": {"topology_hash": "t1"}, "scheduler": {"execution_sequence": ["n1"]}},
    )
    obs2 = run_observability_pipeline(
        {"projection": {"a": 2}, "queue": {}, "validation": {}},
        {"replay_hash": "r2"},
        {"graph": {"topology_hash": "t2"}, "scheduler": {"execution_sequence": ["n2"]}},
    )
    s1 = run_adaptive_sandbox(state, replay, topology, obs1)
    s2 = run_adaptive_sandbox(state, replay, topology, obs2)
    assert (
        s1["proposal"]["mutation_payload_hash"]
        != s2["proposal"]["mutation_payload_hash"]
    )


def test_state_distinct_telemetry_packets_produce_distinct_state_hashes() -> None:
    execution = {
        "pipeline_id": "shadow",
        "execution_hash": "exec:1",
        "prev_state_hash": "root",
    }
    replay = {"replay_hash": "replay:1"}
    topology = {"topology_hash": "topo:1"}
    tele1 = {"telemetry_id": "tele-aaa", "executed_node_count": 1}
    tele2 = {"telemetry_id": "tele-bbb", "executed_node_count": 2}
    s1 = run_state_engine(execution, replay, tele1, topology)
    s2 = run_state_engine(execution, replay, tele2, topology)
    assert s1["snapshot"]["state_hash"] != s2["snapshot"]["state_hash"]
    assert s1["snapshot"]["telemetry_hash"] == "tele-aaa"
    assert s2["snapshot"]["telemetry_hash"] == "tele-bbb"


def test_adaptive_sandbox_writer_requires_observability_artifact() -> None:
    source = (
        __import__("pathlib")
        .Path("scripts/research/run_adaptive_sandbox.py")
        .read_text(encoding="utf-8")
    )
    assert '{"telemetry_hash": "unknown"}' not in source
    assert 'out/observability/latest.json"' in source or (
        "out/observability/latest.json" in source
    )
