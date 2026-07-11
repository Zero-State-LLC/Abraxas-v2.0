#!/usr/bin/env python3
"""
v2.5 Governance Enhancer: Cross-surface signals + Formal Operator Review Decision Record
Advisory only. SHADOW. Never mutates active skill.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

OUT = Path("out/audit")

def main():
    traces_count = 0
    traces_path = OUT / "abx_hermes_live_operation_traces.latest.json"
    if traces_path.exists():
        traces_count = json.loads(traces_path.read_text()).get("count", 0)

    # Phase 2/3: Cross-surface signal ingestion (holler/oracle/slang)
    cross_signals = {}
    for sig_name in ["holler_oracle", "slang_emergence", "abx_p88_stabilization", "abx_hermes"]:
        for latest in list(OUT.glob(f"*{sig_name}*.latest.json"))[:1]:
            try:
                data = json.loads(latest.read_text())
                cross_signals[sig_name] = {
                    "path": str(latest.name),
                    "summary": str(list(data.keys())[:3] if isinstance(data, dict) else type(data))
                }
                break
            except Exception:
                pass

    # Formal operator review decision record
    formal_review = {
        "review_id": f"formal-op-review-v2.5-{traces_count}",
        "cycle_id": "ABX_HERMES_EVOLUTION_CYCLE_004_LIVE_V2_4",
        "evidence_bundle": {
            "live_traces": traces_count,
            "cross_surface_signals": list(cross_signals.keys()),
            "expanded_corpus_cases": None,
            "brier_delta": None,
            "canary_status": None,
            "recurring_lane": "abx_hermes_extended_shadow_v2_4"
        },
        "recommendation": "CONTINUE_SHADOW_COLLECTION",
        "operator_attestation_required": True,
        "false_certainty_risk": "LOW",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # Pull latest brier and canary
    brier_p = OUT / "abx_hermes_live_brier_ledger_v2_4.latest.json"
    if brier_p.exists():
        formal_review["evidence_bundle"]["brier_delta"] = json.loads(brier_p.read_text()).get("brier_delta")

    canary_p = OUT / "abx_hermes_extended_canary_observation_v2_4.latest.json"
    if canary_p.exists():
        formal_review["evidence_bundle"]["canary_status"] = json.loads(canary_p.read_text()).get("canary_status")

    expander_p = OUT / "abx_hermes_live_expanded_corpus_v2_4.latest.json"
    if expander_p.exists():
        formal_review["evidence_bundle"]["expanded_corpus_cases"] = len(json.loads(expander_p.read_text()).get("cases", []))

    formal_path = OUT / "abx_hermes_formal_operator_review_v2_5.latest.json"
    formal_path.write_text(json.dumps(formal_review, indent=2))
    print(f"Formal operator review decision record emitted: {formal_path}")
    if cross_signals:
        print(f"Cross-surface signals: {list(cross_signals.keys())}")
    return formal_review

if __name__ == "__main__":
    main()
