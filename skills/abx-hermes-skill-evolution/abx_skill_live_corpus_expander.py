#!/usr/bin/env python3
"""
Live Corpus Expander for abx-hermes-skill-evolution v2.4 (initial)
Advisory only. Converts recent live OperationTraces into additional ReplayCase entries.
Never mutates the frozen static corpus. Produces additive live replay cases for extended shadow observation.
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

OUT = Path("out/audit")
SKILL_DIR = Path("skills/abx-hermes-skill-evolution")
FIXTURES = SKILL_DIR / "fixtures" / "replay_cases"

def load_live_traces():
    p = OUT / "abx_hermes_live_operation_traces.latest.json"
    if not p.exists():
        return []
    data = json.loads(p.read_text())
    return data.get("traces", [])

def trace_to_replay_case(trace, idx):
    case_id = f"live-{trace.get('operation_id', idx)}"
    return {
        "case_id": case_id,
        "task_class": trace.get("task_class", "unknown"),
        "skill_id": trace.get("skill_id", "abx-hermes-skill-evolution"),
        "skill_version": "live-v2.3",
        "input_refs": trace.get("input_refs", []),
        "expected_behavior": trace.get("expected_behavior", {"outcome": "PASS"}),
        "forbidden_behavior": trace.get("forbidden_behavior", []),
        "validation_requirements": trace.get("validation_requirements", []),
        "source_commit": trace.get("repo_commit", "live"),
        "provenance_hash": hashlib.sha256(json.dumps(trace, sort_keys=True).encode()).hexdigest()[:16],
        "live_trace_id": trace.get("operation_id"),
        "source": "live_operation_trace"
    }

def main():
    traces = load_live_traces()
    if not traces:
        print("No live traces found. Nothing to expand.")
        return

    live_cases = [trace_to_replay_case(t, i) for i, t in enumerate(traces)]

    expanded = {
        "corpus_id": "abx_hermes_live_expanded_corpus_v2_4",
        "version": "0.1-live",
        "base_corpus": "abx_hermes_replay_corpus_v2_2",
        "cases": live_cases,
        "live_trace_count": len(traces),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "ADDITIVE_LIVE_ONLY",
        "deterministic_hash": hashlib.sha256(json.dumps(live_cases, sort_keys=True).encode()).hexdigest()[:16]
    }

    out_path = OUT / "abx_hermes_live_expanded_corpus_v2_4.latest.json"
    out_path.write_text(json.dumps(expanded, indent=2))

    # Also write individual cases for future use (advisory)
    FIXTURES.mkdir(parents=True, exist_ok=True)
    for case in live_cases[:5]:  # limit to first 5 for cleanliness
        case_path = FIXTURES / f"{case['case_id']}.json"
        case_path.write_text(json.dumps(case, indent=2))

    print(f"Live corpus expanded. Cases: {len(live_cases)}")
    print(f"Artifact: {out_path}")
    print(f"Deterministic hash: {expanded['deterministic_hash']}")
    return expanded

if __name__ == "__main__":
    main()
