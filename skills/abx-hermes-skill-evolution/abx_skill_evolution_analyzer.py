#!/usr/bin/env python3
"""
abx-skill-evolution-analyzer v0.1 (stub)
Aggregates OperationTraces into SkillPerformanceLedger.
Detects recurring patterns.
Emits SkillEvolutionCandidate (advisory only, no mutation).
"""
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List
import sys

_SKILL_DIR = Path(__file__).resolve().parent
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

from abx_skill_stabilization_evolution_constants import (  # noqa: E402
    FAILURE_CLASSES_STABILIZATION,
    classify_failure_kind,
)

def load_traces(trace_dir: Path = Path("out/audit")) -> List[Dict]:
    traces = []
    for p in trace_dir.glob("*receipt*.json"):
        try:
            data = json.loads(p.read_text())
            if "operation_id" in data or "boundary" in data:
                traces.append({"path": str(p), "data": data})
        except Exception:
            pass
    return traces

def aggregate_ledger(traces: List[Dict]) -> Dict[str, Dict]:
    ledger: Dict[str, Dict] = {}
    for t in traces:
        skill = t["data"].get("skill_id", t["data"].get("skill", "unknown"))
        if skill not in ledger:
            ledger[skill] = {"runs": 0, "success": 0, "brier_sum": 0.0, "failures": []}
        ledger[skill]["runs"] += 1
        if t["data"].get("completion_status") == "COMPLETE" or "COMPLETE" in str(t["data"].get("boundary", "")):
            ledger[skill]["success"] += 1
        b = t["data"].get("brier_score") or t["data"].get("provenance", {}).get("brier", 0)
        if isinstance(b, (int, float)):
            ledger[skill]["brier_sum"] += b
        if "failure" in str(t["data"]).lower() or "NOT_COMPUTABLE" in str(t["data"]):
            ledger[skill]["failures"].append(t["path"])
    for s in ledger:
        r = ledger[s]["runs"]
        ledger[s]["success_rate"] = ledger[s]["success"] / r if r else 0
        ledger[s]["mean_brier"] = ledger[s]["brier_sum"] / r if r else None
    return ledger

def detect_signals(ledger: Dict) -> List[Dict]:
    candidates = []
    for skill, stats in ledger.items():
        if stats["runs"] >= 3 and (stats["success_rate"] < 0.8 or (stats.get("mean_brier") or 0) > 0.2):
            candidates.append({
                "candidate_id": f"evocand-{skill}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}",
                "skill_id": skill,
                "triggering_patterns": ["low_success" if stats["success_rate"] < 0.8 else "high_brier"],
                "evidence_window": f"{stats['runs']} runs",
                "status": "CANDIDATE_ONLY",
                "confidence": 0.7
            })
    return candidates

def main():
    traces = load_traces()
    ledger = aggregate_ledger(traces)
    signals = detect_signals(ledger)
    out = {
        "boundary": "ADVISORY_ONLY | SHADOW | SKILL_EVOLUTION_ANALYZER_STUB",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stabilization_failure_classes": FAILURE_CLASSES_STABILIZATION,
        "failure_kind_taxonomy": [
            "implementation_failure",
            "validation_failure",
            "environment_failure",
            "contract_failure",
            "evidence_failure",
        ],
        "ledger_summary": {k: {"runs": v["runs"], "success_rate": round(v["success_rate"], 2)} for k, v in ledger.items()},
        "candidates": signals,
        "failure_kind_samples": {
            skill: classify_failure_kind(" ".join(stats.get("failures", [])[:1]))
            for skill, stats in ledger.items()
            if stats.get("failures")
        },
    }
    Path("out/audit/skill_evolution_analyzer_stub_receipt.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
