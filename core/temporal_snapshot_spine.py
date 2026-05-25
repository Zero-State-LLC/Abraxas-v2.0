"""Deterministic temporal snapshot spine for projection refresh surfaces."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

PATCH_ID = "PATCH-P15-PROJECTION-BUS-AND-TEMPORAL-SNAPSHOT-SPINE-001"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
BLOCKED = "BLOCKED"

_AUTHORITY_BOUNDARY: dict[str, Any] = {
    "projection_only": True,
    "advisory_only": True,
    "authority_granted": False,
    "mutation_allowed": False,
    "promotion_allowed": False,
    "inference_authority": False,
}


def _load_artifact(path: str | Path) -> dict[str, Any] | None:
    try:
        text = Path(path).read_text(encoding="utf-8")
        return json.loads(text)  # type: ignore[no-any-return]
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _cursor_for_snapshot(snapshot_id: str, ordinal: int, total: int) -> str:
    return f"cursor:{canonical_hash({'snapshot_id': snapshot_id, 'ordinal': ordinal, 'total': total})[:20]}"


def _extract_snapshot(source_path: str, payload: dict[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return {
            "source_path": source_path,
            "status": NOT_COMPUTABLE,
            "reason": "source artifact missing or unreadable",
        }

    projection_id = payload.get("projection_id")
    if not isinstance(projection_id, str) or not projection_id:
        return {
            "source_path": source_path,
            "status": NOT_COMPUTABLE,
            "reason": "projection_id missing or invalid",
        }

    deterministic_timestamp = payload.get("projection_timestamp")
    if not isinstance(deterministic_timestamp, str) or not deterministic_timestamp:
        return {
            "source_path": source_path,
            "status": NOT_COMPUTABLE,
            "reason": "deterministic projection timestamp missing",
        }

    source_hash = canonical_hash(payload)
    projection_hash = projection_id
    snapshot_id = canonical_hash(
        {
            "source_path": source_path,
            "projection_id": projection_id,
            "projection_hash": projection_hash,
            "source_hash": source_hash,
            "deterministic_timestamp": deterministic_timestamp,
        }
    )
    lineage_prev = payload.get("lineage_prev")
    lineage_next = payload.get("lineage_next")
    return {
        "schema": "TemporalSnapshotIndexEntry.v1",
        "status": "PRESENT",
        "source_path": source_path,
        "snapshot_id": snapshot_id,
        "projection_id": projection_id,
        "projection_hash": projection_hash,
        "source_hash": source_hash,
        "deterministic_timestamp": deterministic_timestamp,
        "lineage_prev": lineage_prev if isinstance(lineage_prev, str) else None,
        "lineage_next": lineage_next if isinstance(lineage_next, str) else None,
        **_AUTHORITY_BOUNDARY,
    }


def _build_windows(
    ordered_snapshots: list[dict[str, Any]],
    lineage_gaps: list[dict[str, str]],
    *,
    window_size: int,
) -> list[dict[str, Any]]:
    if not ordered_snapshots:
        return []
    gap_ids = {g["snapshot_id"] for g in lineage_gaps}
    windows: list[dict[str, Any]] = []
    for start in range(len(ordered_snapshots)):
        subset = ordered_snapshots[start : start + max(window_size, 1)]
        if not subset:
            continue
        snapshot_ids = [str(item["snapshot_id"]) for item in subset]
        blocked = any(sid in gap_ids for sid in snapshot_ids)
        windows.append(
            {
                "schema": "TemporalSnapshotWindow.v1",
                "window_id": canonical_hash(
                    {
                        "start_snapshot_id": snapshot_ids[0],
                        "end_snapshot_id": snapshot_ids[-1],
                        "snapshot_ids": snapshot_ids,
                    }
                ),
                "start_snapshot_id": snapshot_ids[0],
                "end_snapshot_id": snapshot_ids[-1],
                "snapshot_ids": snapshot_ids,
                "window_status": BLOCKED if blocked else "PRESENT",
                "blocked_reason": "lineage_gap_detected" if blocked else None,
                **_AUTHORITY_BOUNDARY,
            }
        )
    return windows


def _select_window_receipt(
    ordered_snapshots: list[dict[str, Any]],
    lineage_gaps: list[dict[str, str]],
    *,
    window_size: int,
    cursor: str | None,
) -> dict[str, Any]:
    if not ordered_snapshots:
        return {
            "schema": "ProjectionWindowReceipt.v1",
            "window_status": NOT_COMPUTABLE,
            "reason": "no indexable projection snapshots available",
            "selected_snapshot_ids": [],
            "cursor": None,
            "next_cursor": None,
            **_AUTHORITY_BOUNDARY,
        }

    cursor_to_index = {
        str(snapshot["cursor"]): idx for idx, snapshot in enumerate(ordered_snapshots)
    }
    start_index = cursor_to_index.get(cursor, max(len(ordered_snapshots) - window_size, 0))
    selected = ordered_snapshots[start_index : start_index + max(window_size, 1)]
    selected_ids = [str(snapshot["snapshot_id"]) for snapshot in selected]
    gap_ids = {g["snapshot_id"] for g in lineage_gaps}
    blocked = any(snapshot_id in gap_ids for snapshot_id in selected_ids)

    return {
        "schema": "ProjectionWindowReceipt.v1",
        "window_status": BLOCKED if blocked else "PRESENT",
        "reason": "lineage_gap_detected" if blocked else None,
        "selected_snapshot_ids": selected_ids,
        "cursor": selected[0]["cursor"] if selected else None,
        "next_cursor": selected[-1]["cursor"] if selected else None,
        **_AUTHORITY_BOUNDARY,
    }


def build_temporal_snapshot_index(
    *,
    packet_id: str = "temporal_snapshot_spine_001",
    source_paths: list[str] | None = None,
    window_size: int = 2,
    cursor: str | None = None,
) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    resolved_source_paths = source_paths or [
        paths.aal_viz_runtime_projection_latest.as_posix(),
        paths.live_projection_refresh_latest.as_posix(),
    ]

    source_entries = [
        _extract_snapshot(source_path, _load_artifact(source_path))
        for source_path in sorted(resolved_source_paths)
    ]
    ordered_snapshots = sorted(
        [entry for entry in source_entries if entry.get("status") == "PRESENT"],
        key=lambda item: (
            str(item.get("deterministic_timestamp", "")),
            str(item.get("snapshot_id", "")),
        ),
    )

    for index, snapshot in enumerate(ordered_snapshots):
        snapshot["ordinal"] = index
        snapshot["cursor"] = _cursor_for_snapshot(
            str(snapshot["snapshot_id"]), index, len(ordered_snapshots)
        )

    snapshot_ids = {str(snapshot["snapshot_id"]) for snapshot in ordered_snapshots}
    lineage_gaps: list[dict[str, str]] = []
    for snapshot in ordered_snapshots:
        snapshot_id = str(snapshot["snapshot_id"])
        lineage_prev = snapshot.get("lineage_prev")
        lineage_next = snapshot.get("lineage_next")
        if isinstance(lineage_prev, str) and lineage_prev and lineage_prev not in snapshot_ids:
            lineage_gaps.append(
                {
                    "snapshot_id": snapshot_id,
                    "lineage_ref": lineage_prev,
                    "kind": "lineage_prev_missing",
                }
            )
        if isinstance(lineage_next, str) and lineage_next and lineage_next not in snapshot_ids:
            lineage_gaps.append(
                {
                    "snapshot_id": snapshot_id,
                    "lineage_ref": lineage_next,
                    "kind": "lineage_next_missing",
                }
            )

    projection_hash_index: dict[str, list[str]] = {}
    for snapshot in ordered_snapshots:
        p_hash = str(snapshot["projection_hash"])
        projection_hash_index.setdefault(p_hash, []).append(str(snapshot["snapshot_id"]))
    projection_hash_index = {
        key: sorted(value) for key, value in sorted(projection_hash_index.items())
    }

    lineage_index = {
        str(snapshot["snapshot_id"]): {
            "lineage_prev": snapshot.get("lineage_prev"),
            "lineage_next": snapshot.get("lineage_next"),
        }
        for snapshot in ordered_snapshots
    }

    windows = _build_windows(ordered_snapshots, lineage_gaps, window_size=window_size)
    window_receipt = _select_window_receipt(
        ordered_snapshots, lineage_gaps, window_size=window_size, cursor=cursor
    )

    blockers = [
        f"missing_artifact:{entry['source_path']}"
        for entry in source_entries
        if entry.get("status") == NOT_COMPUTABLE
    ]
    blockers.extend(
        sorted(
            f"lineage_gap:{gap['kind']}:{gap['snapshot_id']}->{gap['lineage_ref']}"
            for gap in lineage_gaps
        )
    )

    if not ordered_snapshots:
        final_status = NOT_COMPUTABLE
    elif lineage_gaps:
        final_status = BLOCKED
    elif blockers:
        final_status = "ADVISORY_ONLY"
    else:
        final_status = "PASS"

    cursor_bounds = {
        "first": ordered_snapshots[0]["cursor"] if ordered_snapshots else None,
        "last": ordered_snapshots[-1]["cursor"] if ordered_snapshots else None,
    }

    index_hash = canonical_hash(
        {
            "packet_id": packet_id,
            "ordered_snapshot_ids": [snapshot["snapshot_id"] for snapshot in ordered_snapshots],
            "lineage_gaps": lineage_gaps,
            "cursor_bounds": cursor_bounds,
            "window_ids": [window["window_id"] for window in windows],
        }
    )

    return {
        "schema": "TemporalSnapshotIndex.v1",
        "patch_id": PATCH_ID,
        "packet_id": packet_id,
        "source_entries": source_entries,
        "ordered_snapshots": ordered_snapshots,
        "projection_hash_index": projection_hash_index,
        "lineage_index": lineage_index,
        "lineage_gaps": lineage_gaps,
        "lineage_gap_count": len(lineage_gaps),
        "temporal_windows": windows,
        "window_receipt": window_receipt,
        "cursor_bounds": cursor_bounds,
        "index_hash": index_hash,
        "final_status": final_status,
        "remaining_blockers": sorted(blockers),
        **_AUTHORITY_BOUNDARY,
    }


def write_temporal_snapshot_index(path: str | Path, index_payload: dict[str, Any]) -> Path:
    target = Path(path)
    write_canonical_json(target, index_payload)
    return target

