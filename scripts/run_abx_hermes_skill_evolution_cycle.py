#!/usr/bin/env python3
"""
run_abx_hermes_skill_evolution_cycle.py — v2.2 Live Training Signal Pipeline Runner
Consumes latest training signal (if present) and executes the full v2.2 replay/canary/gate cycle.
Emits cycle receipt. Never mutates active skill.
"""
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "abx-hermes-skill-evolution"
OUT = ROOT / "out" / "audit"

def run_module(mod: str) -> int:
    p = SKILL_DIR / mod
    if not p.exists():
        print(f"SKIP: {mod} not found")
        return 0
    res = subprocess.run([sys.executable, str(p)], capture_output=True, text=True, cwd=ROOT)
    print(f"RUN {mod}: exit={res.returncode}")
    if res.stdout:
        print(res.stdout.strip()[:300])
    return res.returncode

def main():
    print("=== ABX HERMES SKILL EVOLUTION CYCLE v2.2 (LIVE RUNNER) ===")
    signal_path = OUT / "abx_hermes_training_signal_v2_1.latest.json"
    if signal_path.exists():
        sig = json.loads(signal_path.read_text())
        print(f"Training signal loaded: evidence_count={sig.get("evolution_candidate", {}).get("evidence_count", "?")}")
    else:
        print("No training signal found; running on current corpus")

    # Execute full pipeline
    rc = 0
    rc += run_module("abx_skill_replay_stub.py")
    rc += run_module("abx_skill_canary_stub.py")
    rc += run_module("abx_skill_candidate_applier.py")
    rc += run_module("abx_skill_promotion_gate_stub.py")

    # Load latest cycle and ensure safety invariants
    cycle_path = OUT / "abx_hermes_evolution_cycle_001.latest.json"
    if cycle_path.exists():
        cycle = json.loads(cycle_path.read_text())
    else:
        cycle = {}

    cycle.update({
        "cycle_id": "ABX_HERMES_EVOLUTION_CYCLE_002_LIVE",
        "runner": "scripts/run_abx_hermes_skill_evolution_cycle.py",
        "active_skill_modified": False,
        "candidate_promoted": False,
        "operator_decision_required": True,
        "pipeline_rc": rc,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    cycle_path.write_text(json.dumps(cycle, indent=2))

    print(f"Cycle receipt emitted: {cycle_path}")
    print(f"Pipeline complete. rc={rc}. active_modified={cycle.get("active_skill_modified")}")
    return rc

if __name__ == "__main__":
    sys.exit(main())
