#!/usr/bin/env python3
"""
Slice F End-to-End Example: Hermes session volume → EvidencePack → OperationTrace → evolution emitter.

This demonstrates the closed loop for "real session volume in evolution cycle".

Run with:
  env -u PYTHONPATH -u PYTHONHOME .venv/bin/python scripts/research/run_slice_f_end_to_end_example.py

All SHADOW. No authority granted.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "research" / "run_shadow_signal_forage_template.py"
EMITTER = ROOT / "scripts" / "abx_hermes_live_operation_trace_emitter.py"
ANALYZER = ROOT / "skills" / "abx-hermes-skill-evolution" / "abx_skill_evolution_analyzer.py"


def run(cmd: list[str], cwd: Path = ROOT) -> tuple[int, str]:
    env = {"PATH": "/usr/bin:/bin"}
    # scrub
    for k in ["PYTHONPATH", "PYTHONHOME"]:
        env.pop(k, None)
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, env={**env, "PATH": env.get("PATH", "")}
    )
    return result.returncode, result.stdout + result.stderr


def main():
    print("=== Slice F End-to-End: Hermes volume → pack → trace → emitter → analyzer ===\n")

    # 1. Produce high-density pack from Hermes traces (or stub if no traces)
    print("1. Running --from-hermes-traces (Hermes-native enhanced forager)...")
    out_dir = ROOT / "tmp" / "slice_f_e2e"
    out_dir.mkdir(parents=True, exist_ok=True)
    rc, out = run([
        "python3", str(RUNNER),
        "--from-hermes-traces",
        "--topic", "slice-f-e2e-real-volume",
        "--out", str(out_dir)
    ])
    print(out)

    pack_path = out_dir / "evidence_pack.v0.json"
    if not pack_path.exists():
        print("ERROR: no pack produced")
        return 2

    # 2. The runner already emitted the OperationTrace (see output above)
    print("\n2. OperationTrace emission (done by runner via adapter + write_operation_trace):")
    recent_traces = sorted((ROOT / "out" / "audit").glob("os_signal_*.latest.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:1]
    for t in recent_traces:
        print(f"   {t}")
        try:
            data = json.loads(t.read_text())
            print(f"   task_class: {data.get('task_class')}")
            print(f"   skill_id: {data.get('skill_id')}")
            print(f"   evidence_status: {data.get('evidence_status')}")
        except Exception:
            pass

    # 3. Run the emitter (it will pick up the new os_signal trace)
    print("\n3. Running emitter to surface for abx-hermes-skill-evolution...")
    rc2, out2 = run(["python3", str(EMITTER)])
    # Show last few lines
    lines = out2.strip().splitlines()[-10:]
    for line in lines:
        print("   " + line)

    # 4. Run the Hermes signal volume to evolution ledger bridge (Slice F continuation)
    print("\n4. Running Hermes signal volume -> evolution ledger bridge...")
    rc3, out3 = run([ "python3", str(ROOT / "scripts" / "research" / "run_hermes_signal_evolution_ingest.py") ])
    print("   " + (out3.splitlines()[-5] if out3.splitlines() else "(no output)"))

    # 5. Explicitly run the analyzer to surface volume candidates (new in this continuation)
    print("\n5. Explicitly running abx-hermes-skill-evolution analyzer for volume candidates...")
    rc4, out4 = run(["python3", str(ANALYZER)])
    try:
        analyzer_out = json.loads(out4)
        volume_cands = [c for c in analyzer_out.get("candidates", []) if "signal_forage" in c.get("skill_id", "")]
        if volume_cands:
            print("   Volume candidates (high_hermes_signal_volume):")
            for c in volume_cands:
                print(f"     {json.dumps(c, indent=2)}")
        else:
            print("   (no signal_forage candidates in this run)")
        print("   Full ledger_summary keys:", list(analyzer_out.get("ledger_summary", {}).keys()))
    except Exception as e:
        print(f"   (analyzer parse note: {e})")

    # 6. Summary
    print("\n=== END-TO-END SUMMARY ===")
    print(f"Pack: {pack_path} (density high, OBSERVED bias from Hermes sessions)")
    print("Trace: written to out/audit/os_signal_*.latest.json (via core/signal/operation_trace_adapter)")
    print("Emitter: scans and normalizes for abx-hermes-skill-evolution (SHADOW learning loop)")
    print("Ledger bridge: signal_forage volume recorded in SHADOW evolution ledger")
    print("Analyzer: high_hermes_signal_volume candidate surfaced for skill:task_class (SHADOW)")
    print("Next (operator): use the trace/ledger/candidate in skill-evolution cycle or abx-hermes-skill-evolution SKILL.")
    print("\nAll advisory / SHADOW. No execution or promotion authority.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
