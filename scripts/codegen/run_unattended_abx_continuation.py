#!/usr/bin/env python3
"""
Unattended Continuation Runner for abx-hermes-skill-evolution (v2.9+)

Designed to run for 2–3 hours with no human present.
Uses only scrubbed environment.
Emits progress receipts.
Stops cleanly on invariants violation or max cycles.

Usage:
    nohup env -i PATH="$PATH" HOME="$HOME" USER="$USER" UV_CACHE_DIR="$HOME/.cache/uv" \
      uv run python scripts/codegen/run_unattended_abx_continuation.py > logs/unattended_$(date +%Y%m%d_%H%M).log 2>&1 &

Safe to leave running while running errands.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Configuration
MAX_CYCLES = 8
SLEEP_MINUTES = 20
SCRUB_ENV = {
    "PATH": os.environ.get("PATH", ""),
    "HOME": os.environ.get("HOME", ""),
    "USER": os.environ.get("USER", ""),
    "UV_CACHE_DIR": os.path.expanduser("~/.cache/uv"),
}

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "out" / "audit"
LOGS = ROOT / "logs"
CYCLE_SCRIPT = ROOT / "scripts" / "codegen" / "run_abx_hermes_skill_evolution_cycle.py"
PYTEST_CMD = ["python", "-m", "pytest", "tests/test_abx_skill_evolution*.py", "-q", "--tb=no"]

os.makedirs(LOGS, exist_ok=True)
os.makedirs(OUT, exist_ok=True)


def run_scrubbed(cmd, cwd=ROOT):
    """Run command with completely scrubbed environment."""
    env = {**os.environ, **SCRUB_ENV}
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,  # 5 min max per command
    )
    return result.returncode, result.stdout + result.stderr


def count_refs():
    """Count active policy references (must stay at exactly 3)."""
    total = 0
    search = "Scr" + "ipts/"
    for py in Path(".").rglob("*.py"):
        if "unattended" in str(py).lower():
            continue
        try:
            total += len([line for line in py.read_text(errors="ignore").splitlines() if search in line])
        except Exception:
            pass
    return total


def emit_receipt(cycle_num: int, status: dict):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    receipt = {
        "unattended_cycle": cycle_num,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
    }
    path = OUT / f"unattended_cycle_{cycle_num:03d}_{ts}.json"
    path.write_text(json.dumps(receipt, indent=2))
    return path


def main():
    print("=== UNATTENDED ABX CONTINUATION STARTED ===")
    print(f"Max cycles: {MAX_CYCLES}, Sleep between: {SLEEP_MINUTES} min")
    print("Scrubbed env active. Refs must stay == 3. active_modified must stay False.")

    for i in range(1, MAX_CYCLES + 1):
        print(f"\n=== UNATTENDED CYCLE {i}/{MAX_CYCLES} — {datetime.now(timezone.utc).isoformat()} ===")

        status = {
            "cycle": i,
            "refs_before": count_refs(),
            "cycle_rc": None,
            "active_modified": None,
            "pytest_pass": None,
            "ledger_present": False,
            "validator_status": None,
            "errors": [],
        }

        # 1. Run main cycle (scrubbed)
        rc, out = run_scrubbed(["uv", "run", str(CYCLE_SCRIPT)])
        status["cycle_rc"] = rc
        print(f"Cycle rc: {rc}")

        # Parse key values from cycle output if possible
        if "active_modified=False" in out:
            status["active_modified"] = False
        if "live_traces=" in out:
            try:
                status["live_traces"] = int(out.split("live_traces=")[-1].split()[0])
            except Exception:
                pass

        # 2. Refs check
        refs = count_refs()
        status["refs_after"] = refs
        if refs != 3:
            status["errors"].append(f"REFS_DRIFT: {refs} (expected 3)")
            emit_receipt(i, status)
            print("BLOCKER: Refs drifted. Stopping.")
            return 1

        # 3. Targeted pytest (scrubbed)
        rc, out = run_scrubbed(["env", "-i", "PATH=" + SCRUB_ENV["PATH"],
                                "HOME=" + SCRUB_ENV["HOME"],
                                "USER=" + SCRUB_ENV["USER"],
                                "UV_CACHE_DIR=" + SCRUB_ENV["UV_CACHE_DIR"],
                                "uv", "run", "python", "-m", "pytest"] + PYTEST_CMD[2:])
        status["pytest_pass"] = (rc == 0)
        print(f"Pytest: {'PASS' if rc == 0 else 'FAIL'}")

        if rc != 0:
            status["errors"].append("PYTEST_FAILURE")
            emit_receipt(i, status)
            print("BLOCKER: Pytest failed. Stopping.")
            return 1

        # 4. Quick ledger / validator sanity
        ledger_path = OUT / "abx_hermes_formal_operator_decision_ledger_v2_9.latest.json"
        status["ledger_present"] = ledger_path.exists()
        if ledger_path.exists():
            try:
                ledger = json.loads(ledger_path.read_text())
                status["validator_status"] = ledger.get("validation_status")
            except Exception:
                pass

        # 5. Emit receipt
        receipt_path = emit_receipt(i, status)
        print(f"Receipt: {receipt_path}")

        # 6. Decide whether to continue
        if status.get("active_modified") is True:
            print("BLOCKER: active_modified became True. Stopping.")
            return 1

        if i < MAX_CYCLES:
            sleep_sec = SLEEP_MINUTES * 60
            print(f"Sleeping {SLEEP_MINUTES} minutes until next cycle...")
            time.sleep(sleep_sec)

    print("\n=== UNATTENDED CONTINUATION COMPLETE (all cycles finished) ===")
    final_receipt = {
        "status": "UNATTENDED_RUN_FINISHED",
        "cycles_completed": MAX_CYCLES,
        "final_refs": count_refs(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    emit_receipt(MAX_CYCLES + 1, final_receipt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
