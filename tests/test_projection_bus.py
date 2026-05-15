from __future__ import annotations

from typing import Any

from core.projection_bus import NOT_COMPUTABLE, build_projection_bus_envelope


def _snapshot(
    *,
    snapshot_id: str,
    cursor: str,
    projection_id: str,
    source_hash: str,
    projection_hash: str,
    source_path: str,
) -> dict[str, Any]:
    return {
        "snapshot_id": snapshot_id,
        "cursor": cursor,
        "projection_id": projection_id,
        "source_hash": source_hash,
        "projection_hash": projection_hash,
        "source_path": source_path,
        "lineage_prev": None,
        "lineage_next": None,
    }


def _index(ordered_snapshots: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "index_hash": "idx_hash_001",
        "ordered_snapshots": ordered_snapshots,
        "cursor_bounds": {
            "first": ordered_snapshots[0]["cursor"] if ordered_snapshots else None,
            "last": ordered_snapshots[-1]["cursor"] if ordered_snapshots else None,
        },
        "remaining_blockers": [],
        "final_status": "PASS",
    }


def test_bus_message_ordering_stability() -> None:
    index_payload = _index(
        [
            _snapshot(
                snapshot_id="s1",
                cursor="c1",
                projection_id="p1",
                source_hash="h1",
                projection_hash="ph1",
                source_path="a.json",
            ),
            _snapshot(
                snapshot_id="s2",
                cursor="c2",
                projection_id="p2",
                source_hash="h2",
                projection_hash="ph2",
                source_path="b.json",
            ),
        ]
    )
    p1 = build_projection_bus_envelope(index_payload)
    p2 = build_projection_bus_envelope(index_payload)
    assert [m["snapshot_id"] for m in p1["messages"]] == [m["snapshot_id"] for m in p2["messages"]]
    assert [m["message_id"] for m in p1["messages"]] == [m["message_id"] for m in p2["messages"]]


def test_ledger_hash_stability() -> None:
    index_payload = _index(
        [
            _snapshot(
                snapshot_id="s1",
                cursor="c1",
                projection_id="p1",
                source_hash="h1",
                projection_hash="ph1",
                source_path="a.json",
            )
        ]
    )
    p1 = build_projection_bus_envelope(index_payload)
    p2 = build_projection_bus_envelope(index_payload)
    assert p1["ledger"]["ledger_hash"] == p2["ledger"]["ledger_hash"]


def test_missing_indexable_snapshots_not_computable() -> None:
    payload = build_projection_bus_envelope(_index([]))
    assert payload["final_status"] == NOT_COMPUTABLE
    assert "missing_indexable_snapshots" in payload["remaining_blockers"]


def test_corrupt_lineage_fail_closed_behavior_passthrough() -> None:
    index_payload = _index(
        [
            _snapshot(
                snapshot_id="s1",
                cursor="c1",
                projection_id="p1",
                source_hash="h1",
                projection_hash="ph1",
                source_path="a.json",
            )
        ]
    )
    index_payload["final_status"] = "BLOCKED"
    index_payload["remaining_blockers"] = ["lineage_gap:lineage_prev_missing:s1->unknown"]
    payload = build_projection_bus_envelope(index_payload)
    assert payload["final_status"] == "BLOCKED"
    assert payload["ledger"]["final_status"] == "BLOCKED"


def test_invariants_locked() -> None:
    payload = build_projection_bus_envelope(
        _index(
            [
                _snapshot(
                    snapshot_id="s1",
                    cursor="c1",
                    projection_id="p1",
                    source_hash="h1",
                    projection_hash="ph1",
                    source_path="a.json",
                )
            ]
        )
    )
    assert payload["projection_only"] is True
    assert payload["advisory_only"] is True
    assert payload["authority_granted"] is False
    assert payload["mutation_allowed"] is False
    assert payload["promotion_allowed"] is False
    assert payload["inference_authority"] is False
    message = payload["messages"][0]
    assert message["projection_only"] is True
    assert message["advisory_only"] is True
    assert message["authority_granted"] is False
    assert message["mutation_allowed"] is False
    assert message["promotion_allowed"] is False
    assert message["inference_authority"] is False

