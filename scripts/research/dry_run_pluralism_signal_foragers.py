#!/usr/bin/env python3
"""
P3 Pluralism Dry-Run: Multiple signal forager roles (Hermes + others) feeding one evolution cycle.

Now emits sample os_signal traces with distinct task_classes so the analyzer
and ledger see pluralism (signal_forage + hyperagent_forager).

All outputs are advisory SHADOW artifacts.
"""

import json
import random
from datetime import UTC, datetime
from pathlib import Path


def emit_sample_os_signal_trace(task_class: str, skill_id: str, observed: int = 3) -> Path:
    """Emit a minimal os_signal trace for the given forager task_class (SHADOW only)."""
    audit_dir = Path("out/audit")
    audit_dir.mkdir(parents=True, exist_ok=True)

    trace = {
        "operation_id": f"os-plural-{task_class}-{int(datetime.now(UTC).timestamp())}",
        "skill_id": skill_id,
        "task_class": task_class,
        "completion_status": "COMPLETE",
        "boundary": "ADVISORY_ONLY | SHADOW",
        "evidence_status": "OBSERVED" if observed > 0 else "INFERRED",
        "brier_score": round(random.uniform(0.05, 0.15), 3),
        "provenance": {
            "source": "pluralism_dry_run",
            "forager_role": task_class,
            "observed_count": observed,
            "density": round(observed / 5.0, 2),
            "lane": "SHADOW",
            "advisory_only": True,
        },
        "timestamp": datetime.now(UTC).isoformat(),
    }

    ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    trace_path = audit_dir / f"os_signal_plural_{task_class}_{ts}.latest.json"
    trace_path.write_text(json.dumps(trace, indent=2))
    return trace_path


def main():
    roles = [
        {"role": "hermes-native-signal-forager", "density_target": 0.7, "task_class": "signal_forage", "skill_id": "abx-familiar-signal-forager"},
        {"role": "hyperagent-long-running-forager", "cadence": "6h", "input": "Hermes traces + external", "task_class": "hyperagent_forager", "skill_id": "abx-hyperagent-forager"},
    ]

    emitted = []
    for r in roles:
        if "task_class" in r:
            p = emit_sample_os_signal_trace(r["task_class"], r["skill_id"], observed=4 if r["task_class"] == "signal_forage" else 2)
            emitted.append(str(p))

    artifact = {
        "pluralism_dry_run": "P3-Alembic-Hyperagent-2026-07",
        "timestamp": datetime.now(UTC).isoformat(),
        "roles": roles,
        "emitted_traces": emitted,
        "evolution_handoff": "OperationTrace(s) with task_class=signal_forage + hyperagent_forager",
        "authority": {"execution_authority": False, "lane": "SHADOW"},
        "notes": "Plural foragers now feed distinct task_classes into the same evolution ledger path. No promotion.",
    }

    print(json.dumps(artifact, indent=2))
    out_path = Path("out/shadow_pluralism_dry_run.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2))
    print(f"\nWrote {out_path} + sample traces for analyzer/ledger pluralism.")


if __name__ == "__main__":
    main()
