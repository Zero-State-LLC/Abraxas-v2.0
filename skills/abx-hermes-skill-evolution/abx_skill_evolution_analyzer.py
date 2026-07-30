#!/usr/bin/env python3
"""
abx-skill-evolution-analyzer v0.2 (extended for Hermes signal volume)

Aggregates OperationTraces into SkillPerformanceLedger.
Keys by skill_id + task_class when present (e.g. "abx-familiar-signal-forager:signal_forage").
Supports legacy *receipt*.json and new os_signal_*.latest.json.

Detects recurring patterns (advisory only).
Emits SkillEvolutionCandidate (SHADOW, no mutation).
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any  # keep for now, will clean on next pass


def load_traces(trace_dir: Path = Path("out/audit")) -> list[dict]:
    traces: list[dict] = []

    # Legacy receipt traces
    for p in trace_dir.glob("*receipt*.json"):
        try:
            data = json.loads(p.read_text())
            if "operation_id" in data or "boundary" in data:
                traces.append({"path": str(p), "data": data})
        except Exception:  # noqa: BLE001,S110
            pass  # resilient stub (intentional for advisory surface)

    # New: os_signal traces carrying Hermes signal volume (signal_forage etc.)
    for p in trace_dir.glob("os_signal_*.latest.json"):
        try:
            data = json.loads(p.read_text())
            if data.get("task_class") or "signal_forage" in str(data.get("skill_id", "")):
                traces.append({"path": str(p), "data": data})
        except Exception:  # noqa: BLE001,S110
            pass  # resilient stub

    return traces


def _ledger_key(skill: str, task_class: str | None) -> str:
    return f"{skill}:{task_class}" if task_class else skill


def aggregate_ledger(traces: list[dict]) -> dict[str, dict]:
    ledger: dict[str, dict] = {}
    for t in traces:
        d = t["data"]
        skill = d.get("skill_id", d.get("skill", "unknown"))
        tc = d.get("task_class")
        key = _ledger_key(skill, tc)

        if key not in ledger:
            ledger[key] = {"runs": 0, "success": 0, "brier_sum": 0.0, "failures": []}

        ledger[key]["runs"] += 1

        if d.get("completion_status") == "COMPLETE" or "COMPLETE" in str(d.get("boundary", "")):
            ledger[key]["success"] += 1

        b = d.get("brier_score") or d.get("provenance", {}).get("brier", 0)
        if isinstance(b, (int, float)):
            ledger[key]["brier_sum"] += b

        if "failure" in str(d).lower() or "NOT_COMPUTABLE" in str(d):
            ledger[key]["failures"].append(t["path"])

    for key, stats in ledger.items():
        r = stats["runs"]
        stats["success_rate"] = stats["success"] / r if r else 0
        stats["mean_brier"] = stats["brier_sum"] / r if r else None

    return ledger


def detect_signals(ledger: dict) -> list[dict]:
    candidates = []
    for key, stats in ledger.items():
        if stats["runs"] >= 3 and (stats["success_rate"] < 0.8 or (stats.get("mean_brier") or 0) > 0.2):
            candidates.append({
                "candidate_id": f"evocand-{key}-{datetime.now(UTC).strftime('%Y%m%d%H%M')}",
                "skill_id": key,
                "triggering_patterns": ["low_success" if stats["success_rate"] < 0.8 else "high_brier"],
                "evidence_window": f"{stats['runs']} runs",
                "status": "CANDIDATE_ONLY",
                "confidence": 0.7,
            })
        if "signal_forage" in key and stats["runs"] >= 2:
            # Hermes real-session volume is itself a signal (high observed density from live traces)
            candidates.append({
                "candidate_id": f"evocand-{key}-{datetime.now(UTC).strftime('%Y%m%d%H%M')}",
                "skill_id": key,
                "triggering_patterns": ["high_hermes_signal_volume"],
                "evidence_window": f"{stats['runs']} runs (Hermes sessions)",
                "status": "CANDIDATE_ONLY",
                "confidence": 0.6,
            })
    return candidates


def main() -> None:
    traces = load_traces()
    ledger = aggregate_ledger(traces)
    signals = detect_signals(ledger)

    out: dict[str, Any] = {
        "boundary": "ADVISORY_ONLY | SHADOW | SKILL_EVOLUTION_ANALYZER_V0.2",
        "timestamp": datetime.now(UTC).isoformat(),
        "ledger_summary": {
            k: {"runs": v["runs"], "success_rate": round(v["success_rate"], 2)}
            for k, v in ledger.items()
        },
        "candidates": signals,
    }
    Path("out/audit/skill_evolution_analyzer_stub_receipt.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
