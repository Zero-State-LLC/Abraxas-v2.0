from __future__ import annotations

import json
from pathlib import Path

from core.temporal_lineage_pulse_ledger import (
    build_temporal_lineage_pulse_ledger,
    write_temporal_lineage_pulse_ledger,
)


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _pulse(path: Path, *, pulse_id: str) -> None:
    _write(
        path,
        {
            "pulse_id": pulse_id,
            "projection_chronoscope": str(path.parent / f"{pulse_id}_chrono.json"),
            "temporal_snapshot_spine": str(path.parent / f"{pulse_id}_spine.json"),
        },
    )
    _write(
        path.parent / f"{pulse_id}_chrono.json",
        {
            "timeline_points": [
                {"timeline_point_id": "tp1", "snapshot_id": "s1", "lineage_prev": ""},
                {"timeline_point_id": "tp2", "snapshot_id": "s2", "lineage_prev": "s1"},
            ],
            "playback_cursors": [{"cursor": "c1"}, {"cursor": "c2"}],
            "lineage_evolution": {"corrupt_lineage_count": 0},
        },
    )
    _write(
        path.parent / f"{pulse_id}_spine.json",
        {
            "ordered_snapshots": [
                {"snapshot_id": "s1", "lineage_prev": None},
                {"snapshot_id": "s2", "lineage_prev": "s1"},
            ],
            "lineage_gap_count": 0,
        },
    )


def test_deterministic_and_flags(tmp_path: Path) -> None:
    p1 = tmp_path / "b.json"
    p2 = tmp_path / "a.json"
    _pulse(p1, pulse_id="p2")
    _pulse(p2, pulse_id="p1")
    a = build_temporal_lineage_pulse_ledger(pulses=[p1.as_posix(), p2.as_posix()])
    b = build_temporal_lineage_pulse_ledger(pulses=[p1.as_posix(), p2.as_posix()])
    assert a == b
    assert a["entry_count"] == 2
    assert all(e["advisory_only"] is True for e in a["entries"])
    assert all(e["forecast_authority"] is False for e in a["entries"])


def test_missing_inputs_non_breaking_and_write(tmp_path: Path) -> None:
    packet = build_temporal_lineage_pulse_ledger(pulses=[(tmp_path / "missing.json").as_posix()])
    assert packet["entry_count"] == 0
    out = tmp_path / "lineage_ledger.json"
    write_temporal_lineage_pulse_ledger(out, packet)
    assert out.exists()
    assert out.with_suffix(".md").exists()
