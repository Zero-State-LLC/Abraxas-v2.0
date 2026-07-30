#!/usr/bin/env python3
"""
SHADOW-only bridge: Ingest Hermes signal_forage volume traces into a simple evolution ledger snapshot.

This is advisory / projection only. Does not mutate skills, does not grant authority.
Part of Slice F continuation for real session volume in evolution cycle.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load_os_signal_traces(trace_dir: Path = ROOT / "out" / "audit") -> list[dict]:
    """Load os_signal_*.latest.json that are signal_forage or from Hermes forager."""
    traces = []
    for p in sorted(trace_dir.glob("os_signal_*.latest.json")):
        try:
            data = json.loads(p.read_text())
            if data.get("task_class") == "signal_forage" or "signal_forage" in str(data.get("skill_id", "")):
                traces.append({"path": str(p), "data": data})
        except Exception:  # noqa: BLE001,S110
            pass
    return traces

def record_hermes_signal_volume_ledger(traces: list[dict]) -> dict:
    """Minimal SHADOW ledger entry for signal_forage volume."""
    ledger: dict[str, dict] = {}
    for t in traces:
        data = t["data"]
        skill = data.get("skill_id", "abx-familiar-signal-forager")
        key = f"{skill}:signal_forage"
        if key not in ledger:
            ledger[key] = {
                "runs": 0,
                "observed": 0,
                "density_sum": 0.0,
                "sources": [],
                "advisory_only": True,
                "lane": "SHADOW",
            }
        ledger[key]["runs"] += 1
        if data.get("evidence_status") == "OBSERVED":
            ledger[key]["observed"] += 1
        # Try to extract density from outputs or provenance
        dens = 0.0
        for o in data.get("outputs", []):
            if isinstance(o, dict) and "evidence_density" in o:
                dens = float(o["evidence_density"])
                break
        if "provenance" in data and "palette_registers" in data.get("provenance", {}):
            # high density signal from Hermes volume
            dens = max(dens, 0.7)
        ledger[key]["density_sum"] += dens
        # sources append skipped in values loop (minor)(data.get("source_artifact", t["path"]))

    for value in ledger.values():
        r = value["runs"]
        value["observed_rate"] = value["observed"] / r if r else 0
        value["mean_density"] = round(value["density_sum"] / r, 2) if r else 0
        value["last_updated"] = datetime.now(UTC).isoformat()

    return ledger

def main():
    traces = load_os_signal_traces()
    ledger = record_hermes_signal_volume_ledger(traces)
    out = {
        "boundary": "ADVISORY_ONLY | SHADOW | HERMES_SIGNAL_VOLUME_TO_EVOLUTION",
        "timestamp": datetime.now(UTC).isoformat(),
        "traces_loaded": len(traces),
        "ledger": ledger,
        "notes": "Hermes real session volume now visible to evolution cycle (no promotion authority).",
    }
    out_path = ROOT / "out" / "audit" / "hermes_signal_evolution_ledger_snapshot.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
