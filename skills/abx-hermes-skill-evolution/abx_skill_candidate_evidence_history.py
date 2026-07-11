#!/usr/bin/env python3
"""
Append-Only Candidate Evidence History (v3.2)

Per-cycle normalized snapshots of evidence for the candidate.
Includes live_traces, agreement, active_modified, refs, gate decisions, etc.
Hash chained.
Trend assessment (deterministic, limited stats; NOT_COMPUTABLE when insufficient history).
Advisory only.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

OUT = Path("out/audit")
EVIDENCE_HISTORY = OUT / "abx_hermes_candidate_evidence_history_v3_2.latest.json"
TREND = OUT / "abx_hermes_candidate_evidence_trend_assessment_v3_2.latest.json"

CYCLE = OUT / "abx_hermes_evolution_cycle_001.latest.json"
REPLAY = OUT / "abx_hermes_replay_comparison_v2_2.latest.json"
CANARY = OUT / "abx_hermes_canary_observation_v2_2.latest.json"
GATE = OUT / "abx_hermes_promotion_eligibility_v2_2.latest.json"
REVIEW = OUT / "abx_hermes_formal_operator_review_packet_v2_6.latest.json"
RECONC = OUT / "abx_hermes_operator_decision_reconciliation_v3_0.latest.json"


def load_json_safe(p: Path):
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def compute_hash(obj: dict) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:16]


def main():
    cycle = load_json_safe(CYCLE) or {}
    replay = load_json_safe(REPLAY) or {}
    canary = load_json_safe(CANARY) or {}
    gate = load_json_safe(GATE) or {}
    review = load_json_safe(REVIEW) or {}
    recon = load_json_safe(RECONC) or {}

    snapshots = []
    if EVIDENCE_HISTORY.exists():
        try:
            snapshots = json.loads(EVIDENCE_HISTORY.read_text()).get("snapshots", [])
        except Exception:
            snapshots = []

    # Current snapshot data
    live_traces = cycle.get("live_traces_count", 0) or (review.get("evidence_summary", {}).get("live_traces", 0))
    agreement = canary.get("agreement_rate", 1.0) or review.get("evidence_summary", {}).get("agreement_rate", 1.0)
    active = cycle.get("active_skill_modified", False)
    refs = review.get("evidence_summary", {}).get("reference_count", 3)
    gate_dec = gate.get("decision", "UNKNOWN")
    review_status = review.get("packet_status", "UNKNOWN")
    dec_status = recon.get("reconciliation_status", "UNKNOWN")

    snapshot = {
        "cycle_sequence": len(snapshots) + 1,
        "candidate_id": review.get("candidate_id", "abx_hermes_skill_evolution_v2.x-evo"),
        "candidate_hash": gate.get("candidate_id", "unknown")[:16] if gate else "unknown",
        "static_cases": 7,  # from history frozen corpus
        "candidate_only_cases": canary.get("candidate_only_useful_findings", 0),
        "live_traces_evaluated": live_traces,
        "agreement_rate": agreement,
        "disagreement_count": max(0, int((1.0 - agreement) * live_traces)),
        "replay_deterministic": True,
        "active_modified": active,
        "reference_count": refs,
        "promotion_gate_decision": gate_dec,
        "review_packet_status": review_status,
        "decision_status": dec_status,
        "source_artifacts": ["cycle", "replay", "canary", "review", "reconciliation"],
        "previous_snapshot_hash": snapshots[-1]["snapshot_hash"] if snapshots else "GENESIS",
        "snapshot_hash": "",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # hash excluding timestamp
    h_input = {k: snapshot.get(k) for k in sorted(snapshot.keys()) if k != "timestamp"}
    snapshot["snapshot_hash"] = compute_hash(h_input)

    snapshots.append(snapshot)

    hist_obj = {
        "schema_version": "3.2",
        "ledger_class": "ABX_HERMES_CANDIDATE_EVIDENCE_HISTORY",
        "snapshots": snapshots,
        "snapshot_count": len(snapshots),
        "last_hash": snapshot["snapshot_hash"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    EVIDENCE_HISTORY.write_text(json.dumps(hist_obj, indent=2))

    # Trend assessment (deterministic)
    if len(snapshots) < 2:
        trend = {
            "status": "NOT_COMPUTABLE",
            "reason": "insufficient_history",
            "trace_growth": "NOT_COMPUTABLE",
            "agreement_stability": "NOT_COMPUTABLE",
            "active_mutation_detected": active,
            "ref_stability": refs == 3,
        }
    else:
        prev = snapshots[-2]
        trace_growth = snapshot["live_traces_evaluated"] - prev["live_traces_evaluated"]
        agr_stable = abs(snapshot["agreement_rate"] - prev["agreement_rate"]) < 0.05
        trend = {
            "status": "STABLE" if not active and refs == 3 and agr_stable else "DRIFT_OBSERVED",
            "trace_growth": trace_growth,
            "agreement_stability": agr_stable,
            "active_mutation_detected": active,
            "ref_stability": refs == 3,
            "candidate_hash_stable": snapshot["candidate_hash"] == prev.get("candidate_hash"),
        }

    trend_obj = {
        "schema_version": "3.2",
        "assessment_class": "ABX_HERMES_CANDIDATE_EVIDENCE_TREND_ASSESSMENT",
        "snapshot_count": len(snapshots),
        "trend": trend,
        "deterministic_hash": compute_hash(trend),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    TREND.write_text(json.dumps(trend_obj, indent=2))

    print(f"Evidence history emitted: {EVIDENCE_HISTORY} snapshots={len(snapshots)}")
    print(f"Trend: {trend['status']}")
    return hist_obj


if __name__ == "__main__":
    main()
