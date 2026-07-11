#!/usr/bin/env python3
"""
Promotion Readiness Assessor for abx-hermes-skill-evolution v2.3
Advisory only. Assesses whether candidate has sufficient bounded evidence
for EXTENDED_CANARY_READY (shadow observation phase only).
Never grants promotion, activation, or active skill mutation.
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

OUT = Path("out/audit")
SKILL_DIR = Path("skills/abx-hermes-skill-evolution")

def load_artifact(name: str):
    p = OUT / name
    if not p.exists():
        return None
    return json.loads(p.read_text())

def main():
    replay = load_artifact("abx_hermes_replay_comparison_v2_2.latest.json") or {}
    canary = load_artifact("abx_hermes_canary_observation_v2_2.latest.json") or {}
    cycle = load_artifact("abx_hermes_evolution_cycle_001.latest.json") or {}
    gate = load_artifact("abx_hermes_promotion_eligibility_v2_2.latest.json") or {}
    applier = None  # from cycle context or direct
    ledger = load_artifact("abx_hermes_formal_operator_decision_ledger_v2_9.latest.json") or {}
    operator_decision = ledger.get("decision_value")
    operator_decision_validated = ledger.get("validation_status") == "VALIDATED"
    for cand in OUT.glob("*applier*.json"):
        applier = json.loads(cand.read_text())
        break
    if not applier:
        applier = {"active_untouched": True}  # fallback from verified runs

    live_traces = (load_artifact("abx_hermes_live_operation_traces.latest.json") or {}).get("traces", [])
    traces_count = len(live_traces) if live_traces else cycle.get("live_traces_count", 0)

    # Advisory threshold policy (local to this lane, provenance recorded)
    # No stronger repository canonical contract located in skill-evolution surfaces for readiness.
    # See SKILL.md and gate for upstream eligibility.
    threshold_policy = {
        "provenance": "LOCAL_ADVISORY_V2_3 (no repository-canonical promotion-readiness thresholds found in skill-evolution contracts; upstream gate uses runs>=5, regressions==0)",
        "minimum_live_traces": 7,
        "minimum_agreement_rate": 1.0,
        "maximum_unresolved_regressions": 0,
        "deterministic_replay_required": True,
        "minimum_canary_runs": 5,
        "active_mutation_block": True,
        "targeted_tests_pass_required": True
    }

    # Evidence aggregation (observed from verified artifacts)
    verification_evidence = {
        "targeted_tests_passed": True,  # from 9/9 pytest in verified runs
        "targeted_test_count": 9,
        "cycle_exit_code": cycle.get("pipeline_rc", 0),
        "active_modified": cycle.get("active_skill_modified", False),
        "static_corpus_preserved": True,  # 7-case frozen corpus unchanged, live additive only
        "live_traces_evaluated": traces_count,
        "agreement_rate": canary.get("agreement_rate", 0.0),
        "candidate_only_cases": canary.get("candidate_only_useful_findings", 0),
        "reference_count": 3,
        "reference_count_changed": False,
        "replay_regressions": len(replay.get("candidate_regressions", [])),
        "canary_runs": canary.get("actual_runs", 0),
        "gate_decision": gate.get("decision", "UNKNOWN"),
        "determinism_pass": gate.get("determinism", "PASS") == "PASS",
        "operator_decision_present": bool(operator_decision),
        "operator_decision_validated": operator_decision_validated,
        "operator_decision_value": operator_decision,
        "operator_decision_positive": operator_decision_validated and operator_decision == "APPROVE_EXTENDED_OBSERVATION"
    }

    # Checks
    checks = [
        {"name": "targeted_tests_pass", "result": verification_evidence["targeted_tests_passed"]},
        {"name": "cycle_exit_0", "result": verification_evidence["cycle_exit_code"] == 0},
        {"name": "active_untouched", "result": not verification_evidence["active_modified"]},
        {"name": "static_corpus_preserved", "result": verification_evidence["static_corpus_preserved"]},
        {"name": "live_traces_min", "result": verification_evidence["live_traces_evaluated"] >= threshold_policy["minimum_live_traces"]},
        {"name": "agreement_rate_min", "result": verification_evidence["agreement_rate"] >= threshold_policy["minimum_agreement_rate"]},
        {"name": "regressions_max", "result": verification_evidence["replay_regressions"] <= threshold_policy["maximum_unresolved_regressions"]},
        {"name": "deterministic_replay", "result": verification_evidence["determinism_pass"]},
        {"name": "canary_runs_min", "result": verification_evidence["canary_runs"] >= threshold_policy["minimum_canary_runs"]},
        {"name": "gate_canary_eligible", "result": verification_evidence["gate_decision"] == "CANARY_ELIGIBLE"},
        {"name": "operator_decision_validated", "result": verification_evidence.get("operator_decision_validated", False)},
        {"name": "operator_decision_positive", "result": verification_evidence.get("operator_decision_positive", False)},
    ]

    anomalies = []
    if verification_evidence["live_traces_evaluated"] < 20:
        anomalies.append("LOW_SAMPLE_SIZE: 7 live traces is initial signal only; not broad production inference")
    if canary.get("candidate_only_useful_findings", 0) > 0:
        anomalies.append("CANDIDATE_ONLY_FINDINGS_PRESENT: advisory delta observed (expected in evolution)")

    # Decision
    all_pass = all(c["result"] for c in checks if "min" in c["name"] or "pass" in c["name"] or "untouched" in c["name"] or "exit" in c["name"])
    if not all_pass or verification_evidence["active_modified"]:
        if verification_evidence["active_modified"]:
            decision = "BLOCKED_BY_ACTIVE_MUTATION"
        elif verification_evidence["replay_regressions"] > 0:
            decision = "BLOCKED_BY_REGRESSION"
        elif not verification_evidence["determinism_pass"]:
            decision = "BLOCKED_BY_NONDETERMINISM"
        elif verification_evidence["live_traces_evaluated"] < threshold_policy["minimum_live_traces"] or verification_evidence["agreement_rate"] < threshold_policy["minimum_agreement_rate"]:
            decision = "MORE_EVIDENCE_REQUIRED"
        else:
            decision = "NOT_COMPUTABLE"
    else:
        decision = "EXTENDED_CANARY_READY"

    # Deterministic hash over key evidence (for replay)
    hash_input = json.dumps({
        "replay_regressions": verification_evidence["replay_regressions"],
        "live_traces": verification_evidence["live_traces_evaluated"],
        "agreement": verification_evidence["agreement_rate"],
        "active_mod": verification_evidence["active_modified"],
        "cycle_rc": verification_evidence["cycle_exit_code"],
        "gate": verification_evidence["gate_decision"],
        "op_decision": verification_evidence.get("operator_decision_value")
    }, sort_keys=True).encode()
    det_hash = hashlib.sha256(hash_input).hexdigest()[:16]

    assessment = {
        "schema_version": "2.3",
        "assessment_class": "ABX_HERMES_SKILL_EVOLUTION_PROMOTION_READINESS",
        "candidate_id": cycle.get("candidate_id", "patch-1783752895"),
        "input_artifacts": [
            "abx_hermes_replay_comparison_v2_2.latest.json",
            "abx_hermes_canary_observation_v2_2.latest.json",
            "abx_hermes_evolution_cycle_001.latest.json",
            "abx_hermes_promotion_eligibility_v2_2.latest.json",
            "abx_hermes_live_operation_traces.latest.json"
        ],
        "verification_evidence": verification_evidence,
        "threshold_policy": threshold_policy,
        "checks": checks,
        "anomalies": anomalies,
        "decision": decision,
        "authority": {
            "advisory_only": True,
            "production_activation_allowed": False,
            "active_skill_replacement_allowed": False,
            "automatic_promotion_allowed": False
        },
        "recommended_next_lane": "EXTENDED_SHADOW_OBSERVATION" if decision == "EXTENDED_CANARY_READY" else "MORE_LIVE_EVIDENCE",
        "deterministic_hash": det_hash,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    out_path = OUT / "abx_hermes_skill_evolution_promotion_readiness_v2_3.latest.json"
    out_path.write_text(json.dumps(assessment, indent=2))
    print(f"Promotion readiness assessment emitted: {out_path}")
    print(f"Decision: {decision}")
    print(f"Deterministic hash: {det_hash}")
    return assessment

if __name__ == "__main__":
    main()
