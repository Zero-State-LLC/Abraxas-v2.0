from __future__ import annotations

from typing import Any
from unittest.mock import patch

from core.temporal_snapshot_spine import (
    NOT_COMPUTABLE,
    build_temporal_snapshot_index,
)


def _make_snapshot(
    *,
    projection_id: str,
    projection_timestamp: str,
    lineage_prev: str | None = None,
    lineage_next: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "projection_id": projection_id,
        "projection_timestamp": projection_timestamp,
        "projection_only": True,
        "advisory_only": True,
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
        "inference_authority": False,
    }
    if lineage_prev is not None:
        payload["lineage_prev"] = lineage_prev
    if lineage_next is not None:
        payload["lineage_next"] = lineage_next
    return payload


def test_snapshot_index_ordering_stability() -> None:
    mapping = {
        "snap_a.json": _make_snapshot(projection_id="p-a", projection_timestamp="t:002"),
        "snap_b.json": _make_snapshot(projection_id="p-b", projection_timestamp="t:001"),
    }
    with patch(
        "core.temporal_snapshot_spine._load_artifact",
        side_effect=lambda path: mapping.get(str(path)),
    ):
        p1 = build_temporal_snapshot_index(source_paths=["snap_a.json", "snap_b.json"])
        p2 = build_temporal_snapshot_index(source_paths=["snap_a.json", "snap_b.json"])
    assert [s["snapshot_id"] for s in p1["ordered_snapshots"]] == [
        s["snapshot_id"] for s in p2["ordered_snapshots"]
    ]
    assert [s["deterministic_timestamp"] for s in p1["ordered_snapshots"]] == ["t:001", "t:002"]


def test_cursor_stability() -> None:
    mapping = {
        "snap_a.json": _make_snapshot(projection_id="p-a", projection_timestamp="t:001"),
    }
    with patch(
        "core.temporal_snapshot_spine._load_artifact",
        side_effect=lambda path: mapping.get(str(path)),
    ):
        p1 = build_temporal_snapshot_index(source_paths=["snap_a.json"])
        p2 = build_temporal_snapshot_index(source_paths=["snap_a.json"])
    assert p1["ordered_snapshots"][0]["cursor"] == p2["ordered_snapshots"][0]["cursor"]


def test_window_selection_stability() -> None:
    mapping = {
        "snap_1.json": _make_snapshot(projection_id="p-1", projection_timestamp="t:001"),
        "snap_2.json": _make_snapshot(projection_id="p-2", projection_timestamp="t:002"),
        "snap_3.json": _make_snapshot(projection_id="p-3", projection_timestamp="t:003"),
    }
    with patch(
        "core.temporal_snapshot_spine._load_artifact",
        side_effect=lambda path: mapping.get(str(path)),
    ):
        p1 = build_temporal_snapshot_index(source_paths=list(mapping), window_size=2)
        p2 = build_temporal_snapshot_index(source_paths=list(mapping), window_size=2)
    assert p1["window_receipt"] == p2["window_receipt"]
    assert p1["window_receipt"]["window_status"] == "PRESENT"


def test_missing_artifact_not_computable() -> None:
    with patch("core.temporal_snapshot_spine._load_artifact", return_value=None):
        payload = build_temporal_snapshot_index(source_paths=["missing.json"])
    assert payload["final_status"] == NOT_COMPUTABLE
    assert payload["ordered_snapshots"] == []
    assert payload["remaining_blockers"] == ["missing_artifact:missing.json"]


def test_corrupt_lineage_blocks_window() -> None:
    mapping = {
        "snap_a.json": _make_snapshot(
            projection_id="p-a",
            projection_timestamp="t:001",
            lineage_prev="unknown_snapshot",
        )
    }
    with patch(
        "core.temporal_snapshot_spine._load_artifact",
        side_effect=lambda path: mapping.get(str(path)),
    ):
        payload = build_temporal_snapshot_index(source_paths=["snap_a.json"])
    assert payload["final_status"] == "BLOCKED"
    assert payload["lineage_gap_count"] == 1
    assert payload["window_receipt"]["window_status"] == "BLOCKED"


def test_invariants_locked() -> None:
    mapping = {
        "snap_a.json": _make_snapshot(projection_id="p-a", projection_timestamp="t:001"),
    }
    with patch(
        "core.temporal_snapshot_spine._load_artifact",
        side_effect=lambda path: mapping.get(str(path)),
    ):
        payload = build_temporal_snapshot_index(source_paths=["snap_a.json"])
    assert payload["projection_only"] is True
    assert payload["advisory_only"] is True
    assert payload["authority_granted"] is False
    assert payload["mutation_allowed"] is False
    assert payload["promotion_allowed"] is False
    assert payload["inference_authority"] is False

