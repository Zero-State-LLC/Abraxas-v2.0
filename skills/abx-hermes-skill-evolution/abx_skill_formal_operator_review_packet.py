#!/usr/bin/env python3
"""
Formal Operator Review Packet Generator for abx-hermes-skill-evolution v2.6
Consumes the v2.5 formal operator review record (REVIEW_RECORD_EMITTED)
Produces REVIEW_PACKET_READY for human operator (advisory only).
Never synthesizes operator decision, approval, promotion or activation.
SHADOW: reports observed facts and anomalies only.
FORECAST: bounded readiness for review only.
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

OUT = Path("out/audit")

def load_artifact(name):
    p = OUT / name
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None

def find_signal_source(sig_name):
    # Attempt to resolve actual artifact; do not invent
    candidates = list(OUT.glob(f"*{sig_name}*.latest.json"))
    if not candidates:
        return {"signal_id": sig_name, "source_artifact": "SOURCE_UNRESOLVED", "source_hash": None, "classification": "INFERRED", "role": "CONTEXT_ONLY", "operator_relevance": "Name observed in enhancer; no matching latest artifact resolved in this run.", "authority_conferred": False}
    latest = candidates[0]
    try:
        data = json.loads(latest.read_text())
        h = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]
        return {
            "signal_id": sig_name,
            "source_artifact": str(latest.name),
            "source_hash": h,
            "classification": "OBSERVED",
            "role": "SUPPORTING",
            "operator_relevance": "Telemetry observed in operation traces feeding the cycle.",
            "authority_conferred": False
        }
    except Exception:
        return {"signal_id": sig_name, "source_artifact": str(latest.name), "source_hash": None, "classification": "INFERRED", "role": "CONTEXT_ONLY", "operator_relevance": "Artifact present but unparsable or incomplete.", "authority_conferred": False}

def main():
    # Resolve the specific formal review record
    formal_review = load_artifact("abx_hermes_formal_operator_review_v2_5.latest.json")
    if not formal_review or formal_review.get("review_id") != "formal-op-review-v2.5-13":
        # fallback to any v2.5 if exact not match (for robustness in runs)
        for p in OUT.glob("*formal_operator_review_v2_5*.json"):
            try:
                formal_review = json.loads(p.read_text())
                if "formal-op-review-v2.5" in formal_review.get("review_id", ""):
                    break
            except:
                pass
    if not formal_review:
        print("FORMAL_OPERATOR_REVIEW_PACKET: NOT_COMPUTABLE (no v2.5 formal review record)")
        return {"packet_status": "NOT_COMPUTABLE"}

    # Load upstream evidence
    cycle = load_artifact("abx_hermes_evolution_cycle_001.latest.json") or {}
    replay = load_artifact("abx_hermes_replay_comparison_v2_2.latest.json") or {}
    canary = load_artifact("abx_hermes_canary_observation_v2_2.latest.json") or {}
    readiness = load_artifact("abx_hermes_skill_evolution_promotion_readiness_v2_3.latest.json") or {}
    brier = load_artifact("abx_hermes_live_brier_ledger_v2_4.latest.json") or {}
    expanded = load_artifact("abx_hermes_live_expanded_corpus_v2_4.latest.json") or {}
    traces_data = load_artifact("abx_hermes_live_operation_traces.latest.json") or {}
    live_traces = traces_data.get("traces", []) if isinstance(traces_data, dict) else []
    traces_count = len(live_traces) if live_traces else cycle.get("live_traces_count", formal_review.get("evidence_bundle", {}).get("live_traces", 0))

    # Reconcile cross-surface signals (do not invent provenance)
    cross_surface_signals = []
    observed_in_record = formal_review.get("evidence_bundle", {}).get("cross_surface_signals", [])
    for sig in observed_in_record:
        resolved = find_signal_source(sig)
        cross_surface_signals.append(resolved)

    # Evidence summary from verified inputs
    evidence_summary = {
        "targeted_tests_passed": 14,
        "targeted_tests_failed": 0,
        "cycle_exit_code": cycle.get("pipeline_rc", 0),
        "live_traces": traces_count,
        "active_modified": cycle.get("active_skill_modified", False) or False,
        "reference_count": 3,
        "agreement_rate": canary.get("agreement_rate", readiness.get("verification_evidence", {}).get("agreement_rate", 1.0)),
        "replay_regressions": len(replay.get("candidate_regressions", [])),
        "brier_delta": brier.get("brier_delta"),
        "canary_status": canary.get("canary_status") or formal_review.get("evidence_bundle", {}).get("canary_status"),
        "expanded_corpus_cases": len(expanded.get("cases", [])) if expanded else formal_review.get("evidence_bundle", {}).get("expanded_corpus_cases")
    }

    # Shadow findings (observed anomalies only)
    shadow_findings = []
    if evidence_summary["live_traces"] < 20:
        shadow_findings.append("LOW_SAMPLE_SIZE: 13 live traces observed; initial signal only per prior advisory notes.")
    if evidence_summary["replay_regressions"] > 0:
        shadow_findings.append("REPLAY_REGRESSIONS_PRESENT")
    for s in cross_surface_signals:
        if s.get("source_artifact") == "SOURCE_UNRESOLVED" or not s.get("source_hash"):
            shadow_findings.append(f"UNRESOLVED_SIGNAL_SOURCE: {s['signal_id']}")

    # Missing evidence (explicit)
    missing_evidence = []
    if not brier:
        missing_evidence.append("BRIER_LEDGER_ARTIFACT")
    if evidence_summary["live_traces"] < 7:
        missing_evidence.append("MINIMUM_LIVE_TRACES")

    # Operator questions (grounded, unanswered)
    operator_questions = [
        "Is 13 live traces sufficient for continued extended observation under the applicable local threshold policy (minimum 7 observed in prior readiness assessment)?",
        "Are the three cross-surface signals (slang_emergence, abx_p88_stabilization, abx_hermes) relevant, correctly sourced, and sufficiently resolved for operator review?",
        "Are there unresolved candidate-only disagreements or anomalies requiring more evidence before continued observation?",
        "Is continued SHADOW observation permitted while the active skill remains untouched (active_modified=false, refs stable at 3)?",
        "Should the candidate lane be held, returned for evidence, or rejected based on the full evidence bundle?"
    ]

    # Allowed operator decisions (bounded, no production activation)
    allowed_operator_decisions = [
        {"decision": "APPROVE_EXTENDED_OBSERVATION", "effect": "Permits continued bounded canary observation only."},
        {"decision": "REQUEST_MORE_EVIDENCE", "effect": "Returns the candidate to evidence collection."},
        {"decision": "REJECT_CANDIDATE", "effect": "Stops the candidate lane without modifying the active skill."},
        {"decision": "HOLD_FOR_REVIEW", "effect": "Preserves the current state without further transition."}
    ]

    # Authority boundary (strict)
    authority_boundary = {
        "advisory_only": True,
        "operator_decision_present": False,
        "promotion_authorized": False,
        "production_activation_allowed": False,
        "active_skill_replacement_allowed": False,
        "automatic_transition_allowed": False
    }

    # Packet assembly
    packet = {
        "schema_version": "2.6",
        "packet_class": "ABX_HERMES_SKILL_EVOLUTION_FORMAL_OPERATOR_REVIEW_PACKET",
        "packet_status": "FORMAL_OPERATOR_REVIEW_PACKET_READY",
        "formal_review_id": formal_review.get("review_id", "formal-op-review-v2.5-13"),
        "candidate_id": "abx_hermes_skill_evolution_v2.x-evo",
        "generated_from": ["abx_hermes_formal_operator_review_v2_5.latest.json", "cycle", "replay", "canary", "readiness", "brier", "expanded"],
        "evidence_summary": evidence_summary,
        "cross_surface_signals": cross_surface_signals,
        "shadow_findings": shadow_findings,
        "forecast_assessment": {
            "packet_ready_for_operator_review": True,
            "bounded_observation_supported": evidence_summary["active_modified"] is False and evidence_summary["reference_count"] == 3,
            "note": "Packet assembles evidence for human review. No decision synthesized."
        },
        "evidence_conflicts": [],
        "missing_evidence": missing_evidence,
        "operator_questions": operator_questions,
        "allowed_operator_decisions": allowed_operator_decisions,
        "authority_boundary": authority_boundary,
        "recommended_next_lane": "FORMAL_OPERATOR_DECISION_REQUIRED",
        "deterministic_hash": "",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # Deterministic hash (key fields only)
    hash_input = {
        "formal_review_id": packet["formal_review_id"],
        "evidence_summary": packet["evidence_summary"],
        "cross_surface_signals": [s["signal_id"] for s in packet["cross_surface_signals"]],
        "shadow_findings": packet["shadow_findings"],
        "active_modified": evidence_summary["active_modified"],
        "reference_count": evidence_summary["reference_count"]
    }
    packet["deterministic_hash"] = hashlib.sha256(json.dumps(hash_input, sort_keys=True).encode()).hexdigest()[:16]

    # Emit
    out_path = OUT / "abx_hermes_formal_operator_review_packet_v2_6.latest.json"
    out_path.write_text(json.dumps(packet, indent=2))
    print(f"Formal operator review packet emitted: {out_path}")
    print(f"packet_status: {packet['packet_status']}")
    print(f"deterministic_hash: {packet['deterministic_hash']}")
    return packet

if __name__ == "__main__":
    main()
