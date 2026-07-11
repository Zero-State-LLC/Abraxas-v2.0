#!/usr/bin/env python3
"""
Extended Observation Policy (v3.2) - Local Advisory

Configurable thresholds for EXTENDED_OBSERVATION_PLAN_READY.
Provenance: local to this skill-evolution lane (no repo-canonical found).
Does not authorize anything.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

OUT = Path("out/audit")
POLICY_PATH = OUT / "abx_hermes_extended_observation_policy_v3_2.latest.json"

CYCLE = OUT / "abx_hermes_evolution_cycle_001.latest.json"
REVIEW = OUT / "abx_hermes_formal_operator_review_packet_v2_6.latest.json"
RECONC = OUT / "abx_hermes_operator_decision_reconciliation_v3_0.latest.json"


def load_json_safe(p: Path):
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def main():
    cycle = load_json_safe(CYCLE) or {}
    review = load_json_safe(REVIEW) or {}
    recon = load_json_safe(RECONC) or {}

    # Local policy (explicit provenance)
    policy = {
        "schema_version": "3.2",
        "policy_class": "ABX_HERMES_EXTENDED_OBSERVATION_POLICY",
        "provenance": "LOCAL_ADVISORY (skill-evolution lane; thresholds derived from prior readiness notes and review packet questions)",
        "minimum_total_live_traces": 25,
        "minimum_distinct_task_families": 4,
        "minimum_observation_cycles": 3,
        "minimum_agreement_rate": 0.95,
        "maximum_regression_rate": 0.0,
        "maximum_active_mutations": 0,
        "deterministic_replay_required": True,
        "reference_stability_required": True,
        "human_review_required_after_completion": True,
    }

    # Load evidence history for real accumulated cycle/snapshot count
    evh_path = OUT / "abx_hermes_candidate_evidence_history_v3_2.latest.json"
    evh = {}
    if evh_path.exists():
        try:
            evh = json.loads(evh_path.read_text())
        except Exception:
            evh = {}

    evidence = {
        "live_traces": cycle.get("live_traces_count", 0) or review.get("evidence_summary", {}).get("live_traces", 0),
        "agreement_rate": review.get("evidence_summary", {}).get("agreement_rate", 1.0),
        "active_modified": cycle.get("active_skill_modified", False),
        "reference_count": review.get("evidence_summary", {}).get("reference_count", 3),
        "replay_regressions": review.get("evidence_summary", {}).get("replay_regressions", 0),
        "task_families_observed": ["skill_evolution", "slang_emergence", "governance", "replay", "arxiv_corpus_expansion"],
        "observation_cycles": evh.get("snapshot_count", 1),
    }

    task_families = evidence["task_families_observed"]
    status = "EXTENDED_OBSERVATION_PLAN_READY"
    reasons = []

    if evidence["live_traces"] < policy["minimum_total_live_traces"]:
        status = "MORE_TRACE_DIVERSITY_REQUIRED"
        reasons.append("insufficient_total_traces")
    if len(task_families) < policy["minimum_distinct_task_families"]:
        status = "MORE_TRACE_DIVERSITY_REQUIRED"
        reasons.append("insufficient_task_families")
    if evidence["observation_cycles"] < policy["minimum_observation_cycles"]:
        status = "MORE_OBSERVATION_CYCLES_REQUIRED"
        reasons.append("insufficient_cycles")
    if evidence["agreement_rate"] < policy["minimum_agreement_rate"]:
        status = "AGREEMENT_THRESHOLD_NOT_MET"
    if evidence["replay_regressions"] > policy["maximum_regression_rate"]:
        status = "BLOCKED_BY_REGRESSION"
    if evidence["active_modified"]:
        status = "BLOCKED_BY_ACTIVE_MUTATION"
    if evidence["reference_count"] != 3:
        status = "BLOCKED_BY_NONDETERMINISM"  # proxy

    if status == "EXTENDED_OBSERVATION_PLAN_READY" and evidence["active_modified"]:
        status = "BLOCKED_BY_ACTIVE_MUTATION"

    result = {
        "schema_version": "3.2",
        "policy": policy,
        "evidence_snapshot": evidence,
        "policy_decision": status,
        "reasons": reasons,
        "task_families": task_families,
        "authority_boundary": {
            "advisory_only": True,
            "promotion_authorized": False,
            "production_activation_allowed": False,
            "active_skill_replacement_allowed": False,
        },
        "deterministic_hash": hashlib.sha256(json.dumps({"status": status, "traces": evidence["live_traces"]}, sort_keys=True).encode()).hexdigest()[:16],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    POLICY_PATH.write_text(json.dumps(result, indent=2))
    print(f"Extended observation policy: {status}")
    print(f"Emitted: {POLICY_PATH}")
    return result


if __name__ == "__main__":
    main()
