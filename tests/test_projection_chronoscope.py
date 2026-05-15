from __future__ import annotations

from copy import deepcopy
from typing import Any
from unittest.mock import patch

from core.projection_chronoscope import (
    BLOCKED,
    NOT_COMPUTABLE,
    build_projection_chronoscope_packet,
    build_projection_chronoscope_packet_from_artifacts,
)


def _snapshot(
    *,
    snapshot_id: str,
    timestamp: str,
    cursor: str,
    projection_id: str,
    topic_hash: str,
    lineage_prev: str | None = None,
    lineage_next: str | None = None,
) -> dict[str, Any]:
    return {
        "snapshot_id": snapshot_id,
        "deterministic_timestamp": timestamp,
        "cursor": cursor,
        "projection_id": projection_id,
        "projection_hash": topic_hash,
        "source_hash": f"src-{snapshot_id}",
        "lineage_prev": lineage_prev,
        "lineage_next": lineage_next,
    }


def _snapshot_index() -> dict[str, Any]:
    snapshots = [
        _snapshot(
            snapshot_id="s2",
            timestamp="t:002",
            cursor="c2",
            projection_id="p2",
            topic_hash="h2",
            lineage_prev="s1",
        ),
        _snapshot(
            snapshot_id="s1",
            timestamp="t:001",
            cursor="c1",
            projection_id="p1",
            topic_hash="h1",
            lineage_next="s2",
        ),
    ]
    return {
        "index_hash": "idx-1",
        "ordered_snapshots": snapshots,
        "source_entries": [
            {"source_path": "a.json", "status": "PRESENT"},
            {"source_path": "b.json", "status": "NOT_COMPUTABLE"},
        ],
        "lineage_gap_count": 0,
        "lineage_gaps": [],
        "remaining_blockers": [],
    }


def _projection_bus() -> dict[str, Any]:
    return {
        "messages": [
            {"snapshot_id": "s1", "message_id": "m1", "topic": "aal_viz.projection.refresh"},
            {"snapshot_id": "s2", "message_id": "m2", "topic": "aal_viz.projection.refresh"},
        ],
        "ledger": {"ledger_hash": "ledger-1"},
        "remaining_blockers": [],
    }


def _supplemental_payload() -> dict[str, Any]:
    return {
        "optimization_drift_summary": {
            "detections": ["variance_spike", "cache_contamination"],
            "performance_delta": {"delta_pct": -10.0},
        },
        "replay_topology": {
            "replay_equivalence_status": {"equivalence_verified": True},
        },
    }


def test_timeline_ordering_stability() -> None:
    p1 = build_projection_chronoscope_packet(_snapshot_index(), _projection_bus())
    p2 = build_projection_chronoscope_packet(_snapshot_index(), _projection_bus())
    assert [t["snapshot_id"] for t in p1["timeline_points"]] == ["s1", "s2"]
    assert [t["timeline_point_id"] for t in p1["timeline_points"]] == [
        t["timeline_point_id"] for t in p2["timeline_points"]
    ]


def test_playback_cursor_generation_stability() -> None:
    p1 = build_projection_chronoscope_packet(_snapshot_index(), _projection_bus())
    p2 = build_projection_chronoscope_packet(_snapshot_index(), _projection_bus())
    assert p1["playback_cursors"] == p2["playback_cursors"]
    assert p1["playback_cursor_bounds"] == {"first": "c1", "last": "c2"}


def test_window_extraction_stability() -> None:
    p1 = build_projection_chronoscope_packet(
        _snapshot_index(), _projection_bus(), window_size=1, start_cursor="c2", end_cursor="c2"
    )
    p2 = build_projection_chronoscope_packet(
        _snapshot_index(), _projection_bus(), window_size=1, start_cursor="c2", end_cursor="c2"
    )
    assert p1["timeline_windows"] == p2["timeline_windows"]
    assert len(p1["timeline_windows"]) == 1
    assert p1["timeline_windows"][0]["snapshot_ids"] == ["s2"]


def test_packet_hash_stability() -> None:
    p1 = build_projection_chronoscope_packet(
        _snapshot_index(), _projection_bus(), supplemental_source_payloads=[_supplemental_payload()]
    )
    p2 = build_projection_chronoscope_packet(
        _snapshot_index(), _projection_bus(), supplemental_source_payloads=[_supplemental_payload()]
    )
    assert p1["packet_hash"] == p2["packet_hash"]


def test_topic_filtering_determinism() -> None:
    bus = _projection_bus()
    bus["messages"][1]["topic"] = "other.topic"
    p1 = build_projection_chronoscope_packet(
        _snapshot_index(), bus, topic_filter=["aal_viz.projection.refresh"]
    )
    p2 = build_projection_chronoscope_packet(
        _snapshot_index(), bus, topic_filter=["aal_viz.projection.refresh"]
    )
    assert [point["snapshot_id"] for point in p1["timeline_points"]] == ["s1"]
    assert p1["timeline_points"] == p2["timeline_points"]


def test_missing_source_handling_fails_closed() -> None:
    with patch("core.projection_chronoscope._load_artifact", return_value=None):
        packet = build_projection_chronoscope_packet_from_artifacts()
    assert packet["final_status"] == NOT_COMPUTABLE
    assert packet["timeline_points"] == []
    assert packet["playback_cursor_bounds"] == {"first": None, "last": None}
    assert packet["remaining_blockers"]


def test_corrupt_lineage_fail_closed_behavior() -> None:
    index_payload = _snapshot_index()
    index_payload["ordered_snapshots"][0]["lineage_prev"] = "missing_snapshot"
    packet = build_projection_chronoscope_packet(index_payload, _projection_bus())
    assert packet["final_status"] == BLOCKED
    assert packet["lineage_evolution"]["lineage_status"] == BLOCKED
    assert packet["lineage_evolution"]["corrupt_lineage_count"] == 1


def test_invariants_locked() -> None:
    packet = build_projection_chronoscope_packet(_snapshot_index(), _projection_bus())
    assert packet["projection_only"] is True
    assert packet["advisory_only"] is True
    assert packet["authority_granted"] is False
    assert packet["mutation_allowed"] is False
    assert packet["promotion_allowed"] is False
    assert packet["inference_authority"] is False


def test_timeline_contract_invariants_locked() -> None:
    packet = build_projection_chronoscope_packet(_snapshot_index(), _projection_bus())
    point = packet["timeline_points"][0]
    window = packet["timeline_windows"][0]
    cursor = packet["playback_cursors"][0]
    drift = packet["drift_timeline"]
    lineage = packet["lineage_evolution"]
    for item in [point, window, cursor, drift, lineage]:
        assert item["projection_only"] is True
        assert item["advisory_only"] is True
        assert item["authority_granted"] is False
        assert item["mutation_allowed"] is False
        assert item["promotion_allowed"] is False
        assert item["inference_authority"] is False


def test_no_runtime_replay_canon_mutation() -> None:
    snapshot_index = _snapshot_index()
    projection_bus = _projection_bus()
    snapshot_before = deepcopy(snapshot_index)
    bus_before = deepcopy(projection_bus)
    build_projection_chronoscope_packet(snapshot_index, projection_bus)
    assert snapshot_index == snapshot_before
    assert projection_bus == bus_before
