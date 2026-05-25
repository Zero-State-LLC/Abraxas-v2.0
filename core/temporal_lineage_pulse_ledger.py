from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

_FLAGS: dict[str, Any] = {
    "advisory_only": True,
    "projection_only": True,
    "forecast_authority": False,
    "authority_granted": False,
    "mutation_allowed": False,
}


def _load(path: str | Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _entry(
    *, pulse_ordinal: int, chronoscope_path: str, snapshot_spine_path: str, pulse_id: str
) -> dict[str, Any] | None:
    chronoscope = _load(chronoscope_path)
    snapshot_spine = _load(snapshot_spine_path)
    if not isinstance(chronoscope, dict) or not isinstance(snapshot_spine, dict):
        return None

    timeline_points = [x for x in chronoscope.get("timeline_points", []) if isinstance(x, dict)]
    ordered_snapshots = [x for x in snapshot_spine.get("ordered_snapshots", []) if isinstance(x, dict)]
    lineage_edge_count = sum(
        1 for x in timeline_points if str(x.get("lineage_prev", "")).strip() and str(x.get("snapshot_id", "")).strip()
    ) + sum(1 for x in ordered_snapshots if str(x.get("lineage_prev", "")).strip())
    lineage_gap_count = int(snapshot_spine.get("lineage_gap_count", 0))
    corrupt_lineage_count = int((chronoscope.get("lineage_evolution") or {}).get("corrupt_lineage_count", 0))
    cursors = [x for x in chronoscope.get("playback_cursors", []) if isinstance(x, dict)]
    cursor_span = {
        "first": str(cursors[0].get("cursor")) if cursors else None,
        "last": str(cursors[-1].get("cursor")) if cursors else None,
    }
    lineage_hash = canonical_hash(
        {
            "timeline_point_ids": sorted(str(x.get("timeline_point_id", "")) for x in timeline_points),
            "snapshot_ids": sorted(str(x.get("snapshot_id", "")) for x in ordered_snapshots),
            "lineage_edge_count": lineage_edge_count,
            "lineage_gap_count": lineage_gap_count,
            "corrupt_lineage_count": corrupt_lineage_count,
            "cursor_span": cursor_span,
        }
    )
    entry = {
        "schema": "TemporalLineagePulseLedgerEntry.v1",
        "pulse_id": pulse_id,
        "pulse_ordinal": pulse_ordinal,
        "source_artifact_paths": {
            "projection_chronoscope": chronoscope_path,
            "temporal_snapshot_spine": snapshot_spine_path,
        },
        "chronoscope_timeline_point_count": len(timeline_points),
        "snapshot_spine_ordered_snapshot_count": len(ordered_snapshots),
        "lineage_edge_count": lineage_edge_count,
        "lineage_gap_count": lineage_gap_count,
        "corrupt_lineage_count": corrupt_lineage_count,
        "cursor_span": cursor_span,
        "lineage_hash": lineage_hash,
        **_FLAGS,
    }
    entry["entry_hash"] = canonical_hash(entry)
    return entry


def build_temporal_lineage_pulse_ledger(
    *, ledger_id: str = "temporal_lineage_pulse_ledger_001", pulses: list[str] | None = None
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for idx, pulse_path in enumerate(sorted(pulses or []), start=1):
        payload = _load(pulse_path)
        if not isinstance(payload, dict):
            continue
        entry = _entry(
            pulse_ordinal=idx,
            chronoscope_path=str(payload.get("projection_chronoscope", "")),
            snapshot_spine_path=str(payload.get("temporal_snapshot_spine", "")),
            pulse_id=str(payload.get("pulse_id", f"pulse_{idx:04d}")),
        )
        if entry is not None:
            entries.append(entry)
    packet = {
        "schema_version": "TemporalLineagePulseLedger.v1",
        "ledger_id": ledger_id,
        "entry_count": len(entries),
        "entries": entries,
        **_FLAGS,
    }
    packet["ledger_hash"] = canonical_hash(packet)
    return packet


def build_temporal_lineage_pulse_ledger_markdown(packet: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Temporal Lineage Pulse Ledger",
            "",
            f"- ledger_id: `{packet.get('ledger_id')}`",
            f"- entry_count: `{packet.get('entry_count')}`",
            f"- ledger_hash: `{packet.get('ledger_hash')}`",
            "",
        ]
    )


def write_temporal_lineage_pulse_ledger(path: str | Path, packet: dict[str, Any]) -> Path:
    target = Path(path)
    write_canonical_json(target, packet)
    target.with_suffix(".md").write_text(
        build_temporal_lineage_pulse_ledger_markdown(packet), encoding="utf-8"
    )
    return target
