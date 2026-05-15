"""Deterministic projection bus over temporal snapshot spine artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

PATCH_ID = "PATCH-P15-PROJECTION-BUS-AND-TEMPORAL-SNAPSHOT-SPINE-001"
NOT_COMPUTABLE = "NOT_COMPUTABLE"

_AUTHORITY_BOUNDARY: dict[str, Any] = {
    "projection_only": True,
    "advisory_only": True,
    "authority_granted": False,
    "mutation_allowed": False,
    "promotion_allowed": False,
    "inference_authority": False,
}


def build_projection_bus_envelope(
    temporal_snapshot_index: dict[str, Any],
    *,
    packet_id: str = "projection_bus_001",
) -> dict[str, Any]:
    ordered_snapshots = temporal_snapshot_index.get("ordered_snapshots", [])

    messages: list[dict[str, Any]] = []
    for snapshot in ordered_snapshots:
        topic = "aal_viz.projection.refresh"
        snapshot_id = str(snapshot["snapshot_id"])
        cursor = str(snapshot["cursor"])
        projection_id = str(snapshot["projection_id"])
        message_id = canonical_hash(
            {
                "packet_id": packet_id,
                "snapshot_id": snapshot_id,
                "cursor": cursor,
                "topic": topic,
            }
        )
        messages.append(
            {
                "schema": "ProjectionBusMessage.v1",
                "message_id": message_id,
                "projection_id": projection_id,
                "snapshot_id": snapshot_id,
                "source_hash": snapshot["source_hash"],
                "projection_hash": snapshot["projection_hash"],
                "lineage_prev": snapshot.get("lineage_prev"),
                "lineage_next": snapshot.get("lineage_next"),
                "cursor": cursor,
                "topic": topic,
                "payload_kind": "projection_snapshot_ref",
                "payload_ref": snapshot["source_path"],
                "advisory_flags": [
                    "projection_only",
                    "advisory_only",
                    "deterministic_ordering",
                ],
                **_AUTHORITY_BOUNDARY,
            }
        )

    topic_index: dict[str, list[str]] = {}
    for message in messages:
        topic = str(message["topic"])
        topic_index.setdefault(topic, []).append(str(message["message_id"]))
    topic_index = {key: sorted(value) for key, value in sorted(topic_index.items())}

    blockers = sorted(
        [
            *temporal_snapshot_index.get("remaining_blockers", []),
            *(
                ["missing_indexable_snapshots"]
                if not messages
                else []
            ),
        ]
    )
    if not messages:
        final_status = NOT_COMPUTABLE
    elif temporal_snapshot_index.get("final_status") == "BLOCKED":
        final_status = "BLOCKED"
    elif blockers:
        final_status = "ADVISORY_ONLY"
    else:
        final_status = "PASS"

    cursor_bounds = temporal_snapshot_index.get("cursor_bounds", {"first": None, "last": None})
    ledger_hash = canonical_hash(
        {
            "packet_id": packet_id,
            "message_ids": [message["message_id"] for message in messages],
            "topic_index": topic_index,
            "snapshot_index_hash": temporal_snapshot_index.get("index_hash"),
            "cursor_bounds": cursor_bounds,
        }
    )

    ledger = {
        "schema": "ProjectionBusLedger.v1",
        "ordered_messages": messages,
        "topic_index": topic_index,
        "snapshot_index_ref": temporal_snapshot_index.get("index_hash"),
        "cursor_bounds": cursor_bounds,
        "ledger_hash": ledger_hash,
        "final_status": final_status,
        "remaining_blockers": blockers,
        **_AUTHORITY_BOUNDARY,
    }

    return {
        "schema": "ProjectionBusEnvelope.v1",
        "patch_id": PATCH_ID,
        "packet_id": packet_id,
        "message_schema": "ProjectionBusMessage.v1",
        "ledger_schema": "ProjectionBusLedger.v1",
        "messages": messages,
        "ledger": ledger,
        "snapshot_index_ref": temporal_snapshot_index.get("index_hash"),
        "advisory_flags": [
            "projection_only",
            "advisory_only",
            "no_runtime_authority",
            "deterministic_bus",
        ],
        "final_status": final_status,
        "remaining_blockers": blockers,
        **_AUTHORITY_BOUNDARY,
    }


def write_projection_bus_envelope(path: str | Path, envelope: dict[str, Any]) -> Path:
    target = Path(path)
    write_canonical_json(target, envelope)
    return target


def build_projection_bus_markdown(
    envelope: dict[str, Any], snapshot_index: dict[str, Any]
) -> str:
    lines = [
        f"# Projection Bus — {envelope.get('packet_id', '')}",
        "",
        f"**Patch:** `{envelope.get('patch_id', '')}`",
        f"**Final Status:** `{envelope.get('final_status', '')}`",
        f"**Messages:** `{len(envelope.get('messages', []))}`",
        f"**Snapshot Index Status:** `{snapshot_index.get('final_status', '')}`",
        f"**Lineage Gap Count:** `{snapshot_index.get('lineage_gap_count', 0)}`",
        "",
        "## Cursor Bounds",
        f"- First: `{snapshot_index.get('cursor_bounds', {}).get('first')}`",
        f"- Last: `{snapshot_index.get('cursor_bounds', {}).get('last')}`",
        "",
        "## Remaining Blockers",
    ]
    blockers = envelope.get("remaining_blockers", [])
    if blockers:
        for blocker in blockers:
            lines.append(f"- `{blocker}`")
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)

