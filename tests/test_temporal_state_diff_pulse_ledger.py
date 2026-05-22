from __future__ import annotations

import json
from pathlib import Path

from core.temporal_state_diff_pulse_ledger import (
    build_temporal_state_diff_pulse_ledger,
    write_temporal_state_diff_pulse_ledger,
)


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_deterministic_hash_and_ordering(tmp_path: Path) -> None:
    p1 = tmp_path / "b.json"
    p2 = tmp_path / "a.json"
    _write(p1, {"packet_id": "p2", "packet_hash": "h2", "total_change_count": 2, "diff_entries": [{"source_surface": "x"}]})
    _write(p2, {"packet_id": "p1", "packet_hash": "h1", "total_change_count": 1, "diff_entries": [{"source_surface": "y"}]})
    a = build_temporal_state_diff_pulse_ledger(pulse_paths=[p1.as_posix(), p2.as_posix()])
    b = build_temporal_state_diff_pulse_ledger(pulse_paths=[p1.as_posix(), p2.as_posix()])
    assert a == b
    assert a["pulse_count"] == 2
    assert all(e["advisory_only"] is True for e in a["entries"])


def test_missing_inputs_non_breaking_and_writer(tmp_path: Path) -> None:
    packet = build_temporal_state_diff_pulse_ledger(pulse_paths=[(tmp_path / "missing.json").as_posix()])
    assert packet["pulse_count"] == 0
    out = tmp_path / "ledger.json"
    write_temporal_state_diff_pulse_ledger(out, packet)
    assert out.exists()
    assert out.with_suffix(".md").exists()
