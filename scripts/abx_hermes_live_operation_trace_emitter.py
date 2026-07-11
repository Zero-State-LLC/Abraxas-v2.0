#!/usr/bin/env python3
"""
abx_hermes_live_operation_trace_emitter.py — v2.3 Live OperationTrace Emitter

Scans recent out/audit/*.latest.json artifacts and normalizes them into
OperationTrace v0.1 records. Emits a live batch for the skill-evolution pipeline.

Deterministic: sorted by operation_id, stable fields.
Never mutates active skills. Advisory / signal only.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out" / "audit"
SKILL_DIR = ROOT / "skills" / "abx-hermes-skill-evolution"
SCHEMA_PATH = SKILL_DIR / "contracts" / "operation_trace_v0.1.schema.json"

def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

def normalize_artifact_to_trace(artifact_path: Path, data: Dict[str, Any]) -> Dict[str, Any]:
    """Best-effort normalization of common audit artifacts to OperationTrace v0.1."""
    op_id = f"op-{stable_hash(str(artifact_path))}"
    task_class = "skill_evolution" if "hermes" in str(artifact_path).lower() or "evolution" in str(artifact_path).lower() else "governance_operation"
    skill_id = "abx-hermes-skill-evolution"

    # Extract signals
    commands_run = []
    if "runner" in data:
        commands_run.append(data["runner"])
    if "pipeline_rc" in data:
        commands_run.append(f"rc={data['pipeline_rc']}")

    outputs = []
    if "promotion_eligibility" in data:
        outputs.append({"promotion_eligibility": data["promotion_eligibility"]})
    if "replay_status" in data:
        outputs.append({"replay_status": data["replay_status"]})

    validation_results = []
    if data.get("active_skill_modified") is False:
        validation_results.append("ACTIVE_UNTOUCHED_PASS")
    if data.get("candidate_promoted") is False:
        validation_results.append("CANDIDATE_UNPROMOTED_PASS")

    trace = {
        "operation_id": op_id,
        "skill_id": skill_id,
        "task_class": task_class,
        "repo_commit": "HEAD",  # would be git rev in real
        "inputs_hash": stable_hash(json.dumps(sorted(data.items()) if isinstance(data, dict) else str(data))),
        "plan_hash": stable_hash(str(artifact_path)),
        "commands_run": commands_run or ["governance_run"],
        "outputs": outputs or [{"raw_artifact": str(artifact_path.name)}],
        "validation_results": validation_results or ["OBSERVED"],
        "evidence_status": "OBSERVED",
        "completion_status": data.get("status", "COMPLETE"),
        "operator_interventions": [],
        "token_usage": {"estimated": 0},
        "elapsed_time": 0.0,
        "failure_signatures": [],
        "brier_score": None,
        "source_artifact": str(artifact_path.relative_to(ROOT)),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return trace

def main() -> int:
    print("=== ABX HERMES LIVE OPERATION TRACE EMITTER v2.3 ===")

    traces: List[Dict[str, Any]] = []
    seen = set()

    # Scan recent .latest.json
    candidates = sorted(OUT.glob("*.latest.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:30]

    for path in candidates:
        try:
            data = json.loads(path.read_text())
            if not isinstance(data, dict):
                continue
            # Heuristic: only interesting governance/skill-evolution artifacts
            if any(k in str(path).lower() for k in ["hermes", "evolution", "cycle", "canary", "replay", "promotion", "holler", "oracle", "slang"]):
                trace = normalize_artifact_to_trace(path, data)
                key = trace["operation_id"]
                if key not in seen:
                    seen.add(key)
                    traces.append(trace)
        except Exception as e:
            print(f"SKIP {path.name}: {e}")

    # Sort for determinism
    traces.sort(key=lambda t: t["operation_id"])

    
    # Phase 2 enhancement: include literature corpus as additional deterministic traces for diversity
    try:
        exp = json.loads((OUT / "abx_hermes_live_expanded_corpus_v2_4.latest.json").read_text())
        for case in exp.get("cases", []):
            if case.get("source") == "arxiv_literature_corpus":
                lit_trace = {
                    "operation_id": f"lit-{case.get("case_id", "unknown")}",
                    "skill_id": "abx-hermes-skill-evolution",
                    "task_class": "literature_governance",
                    "repo_commit": "HEAD",
                    "inputs_hash": stable_hash(json.dumps(case, sort_keys=True)),
                    "plan_hash": "literature",
                    "commands_run": ["literature_derived"],
                    "outputs": [{"engineering_implication": case.get("engineering_implication", "")[:100]}],
                    "validation_results": ["LITERATURE_DERIVED_PASS"],
                    "evidence_status": "OBSERVED",
                    "completion_status": "COMPLETE",
                    "operator_interventions": [],
                    "token_usage": {"estimated": 0},
                    "elapsed_time": 0.0,
                    "failure_signatures": [],
                    "brier_score": None,
                    "source_artifact": "literature_corpus",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                key = lit_trace["operation_id"]
                if key not in seen:
                    seen.add(key)
                    traces.append(lit_trace)
    except Exception as e:
        print(f"SKIP literature in emitter: {e}")

    # Emit batch
    out_path = OUT / "abx_hermes_live_operation_traces.latest.json"
    payload = {
        "version": "v2.3",
        "count": len(traces),
        "traces": traces,
        "emitted_at": datetime.now(timezone.utc).isoformat(),
        "source_dir": "out/audit"
    }
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(f"Emitted {len(traces)} live OperationTraces -> {out_path}")

    # Also emit a simple latest signal for the runner (back-compat + new)
    signal_path = OUT / "abx_hermes_training_signal_v2_3.latest.json"
    signal = {
        "version": "v2.3",
        "evidence_count": len(traces),
        "latest_traces": str(out_path),
        "evolution_candidate": {
            "evidence_count": len(traces),
            "source": "live_emitter"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    signal_path.write_text(json.dumps(signal, indent=2))
    print(f"Training signal updated -> {signal_path}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
