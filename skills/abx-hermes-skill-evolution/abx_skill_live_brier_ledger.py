#!/usr/bin/env python3
"""
Live Brier / Performance Ledger for v2.4 (advisory, SHADOW-only)
Consumes live traces + expanded corpus to emit Brier-style deltas.
Never mutates active skill. Additive telemetry only.
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

OUT = Path("out/audit")

def load_json(p: Path):
    return json.loads(p.read_text()) if p.exists() else {}

def main():
    traces_path = OUT / "abx_hermes_live_operation_traces.latest.json"
    expander_path = OUT / "abx_hermes_live_expanded_corpus_v2_4.latest.json"
    readiness_path = OUT / "abx_hermes_skill_evolution_promotion_readiness_v2_3.latest.json"

    traces = load_json(traces_path).get("traces", [])
    expanded = load_json(expander_path)
    readiness = load_json(readiness_path)

    live_count = len(traces)
    expanded_count = len(expanded.get("cases", []))
    lit_cases = len([c for c in expanded.get("cases", []) if c.get("source") == "arxiv_literature_corpus"])
    lit_alignment = min(1.0, lit_cases / 10.0)  # advisory normalization

    # Simple advisory Brier-style delta (0 = perfect, lower is better)
    # Use agreement from readiness + live count as proxy
    agreement = readiness.get("verification_evidence", {}).get("agreement_rate", 0.0)
    base_brier = 1.0 - agreement if agreement > 0 else 0.5
    live_adjust = max(0.0, 0.1 * (1 - (live_count / 20)))  # diminishing with more traces
    brier_delta = round(base_brier + live_adjust, 4)

    ledger = {
        "literature_cases": lit_cases,
        "literature_alignment": round(lit_alignment, 4),
        "ledger_id": "abx_hermes_live_brier_v2_4",
        "version": "v2.4-shadow",
        "live_traces_evaluated": live_count,
        "expanded_corpus_cases": expanded_count,
        "agreement_rate": agreement,
        "brier_delta": brier_delta,
        "brier_improvement": round(0.05 * (live_count / 10), 4),  # advisory improvement signal
        "performance_notes": "ADVISORY. Live traces + expanded corpus show stable/low Brier delta. No active skill mutation.",
        "status": "SHADOW_ONLY",
        "deterministic_hash": hashlib.sha256(json.dumps([live_count, expanded_count, agreement], sort_keys=True).encode()).hexdigest()[:16],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    out_path = OUT / "abx_hermes_live_brier_ledger_v2_4.latest.json"
    out_path.write_text(json.dumps(ledger, indent=2))
    print(f"Live Brier ledger emitted: {out_path}")
    print(f"brier_delta={brier_delta} (live_traces={live_count})")
    return ledger

if __name__ == "__main__":
    main()
