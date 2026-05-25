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


def build_temporal_state_diff_pulse_ledger(
    *, packet_id: str = "temporal_state_diff_pulse_ledger_001", pulse_paths: list[str] | None = None
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for idx, p in enumerate(sorted(pulse_paths or []), start=1):
        payload = _load(p)
        if not isinstance(payload, dict):
            continue
        diff_entries = [
            item for item in payload.get("diff_entries", []) if isinstance(item, dict)
        ]
        surface_counts: dict[str, int] = {}
        for item in diff_entries:
            key = str(item.get("source_surface", ""))
            if key:
                surface_counts[key] = surface_counts.get(key, 0) + 1
        ordered_counts = {k: surface_counts[k] for k in sorted(surface_counts)}
        entry = {
            "schema": "TemporalStateDiffPulseLedgerEntry.v1",
            "packet_id": str(payload.get("packet_id", "temporal_state_diff_001")),
            "pulse_ordinal": idx,
            "temporal_state_diff_hash": str(payload.get("packet_hash", canonical_hash(payload))),
            "total_change_count": int(payload.get("total_change_count", 0)),
            "source_surface_counts": ordered_counts,
            "sequence_cursor": f"pulse:{idx:04d}",
            **_FLAGS,
        }
        entry["entry_hash"] = canonical_hash(entry)
        entries.append(entry)

    ledger: dict[str, Any] = {
        "schema_version": "TemporalStateDiffPulseLedger.v1",
        "packet_id": packet_id,
        "pulse_count": len(entries),
        "entries": entries,
        **_FLAGS,
    }
    ledger["ledger_hash"] = canonical_hash(ledger)
    return ledger


def build_temporal_state_diff_pulse_ledger_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Temporal State Diff Pulse Ledger",
        "",
        f"- packet_id: `{packet.get('packet_id')}`",
        f"- pulse_count: `{packet.get('pulse_count')}`",
        f"- ledger_hash: `{packet.get('ledger_hash')}`",
    ]
    return "\n".join(lines) + "\n"


def write_temporal_state_diff_pulse_ledger(path: str | Path, packet: dict[str, Any]) -> Path:
    target = Path(path)
    write_canonical_json(target, packet)
    target.with_suffix(".md").write_text(
        build_temporal_state_diff_pulse_ledger_markdown(packet), encoding="utf-8"
    )
    return target
