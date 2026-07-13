#!/usr/bin/env python3
"""
Extended Observation Execution Plan (v3.3)

Bounded plan for evidence collection under SHADOW.
Does not authorize execution or mutate active skill.
Plan readiness != authorization.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

OUT = Path("out/audit")
PLAN_PATH = OUT / "abx_hermes_extended_observation_execution_plan_v3_3.latest.json"

POLICY = OUT / "abx_hermes_extended_observation_policy_v3_2.latest.json"
REVIEW = OUT / "abx_hermes_formal_operator_review_packet_v2_6.latest.json"
RECONC = OUT / "abx_hermes_operator_decision_reconciliation_v3_0.latest.json"
EVIDENCE_H = OUT / "abx_hermes_candidate_evidence_history_v3_2.latest.json"


def load_json_safe(p: Path):
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def main():
    policy = load_json_safe(POLICY) or {}
    review = load_json_safe(REVIEW) or {}
    recon = load_json_safe(RECONC) or {}
    _ = load_json_safe(EVIDENCE_H) or {}

    pol_dec = policy.get("policy_decision", "NOT_COMPUTABLE")
    plan_status = "EXTENDED_OBSERVATION_EXECUTION_PLAN_READY" if pol_dec == "EXTENDED_OBSERVATION_PLAN_READY" else "REQUIRES_OPERATOR_AUTHORIZATION_FOR_PLAN"

    candidate = review.get("candidate_id", "abx_hermes_skill_evolution_v2.x-evo")

    plan = {
        "schema_version": "3.3",
        "plan_class": "ABX_HERMES_EXTENDED_OBSERVATION_EXECUTION_PLAN",
        "plan_status": plan_status,
        "candidate_id": candidate,
        "candidate_hash": review.get("deterministic_hash", ""),
        "entry_requirements": {
            "reconciliation_status": recon.get("reconciliation_status"),
            "policy_decision": pol_dec,
        },
        "observation_targets": {
            "target_total_live_traces": policy.get("minimum_total_live_traces", 25),
            "target_distinct_task_families": policy.get("minimum_distinct_task_families", 4),
            "target_agreement_rate": policy.get("minimum_agreement_rate", 0.95),
        },
        "task_family_requirements": ["skill_evolution", "governance", "replay_validation", "cross_surface"],
        "cycle_limits": {"max_cycles": 5, "max_additional_traces": 20},
        "stop_conditions": [
            "target_traces_reached_and_stable",
            "agreement_below_threshold",
            "active_mutation_detected",
            "refs_drift",
        ],
        "abort_conditions": [
            "operator_decision_REJECT_CANDIDATE",
            "production_authority_detected",
            "chain_integrity_failure",
        ],
        "required_artifacts": ["updated_traces", "updated_replay", "updated_canary", "new_reconciliation", "new_history"],
        "operator_checkpoints": ["after_each_cycle", "on_policy_status_change"],
        "authority_boundary": {
            "advisory_only": True,
            "active_skill_mutation_allowed": False,
            "production_activation_allowed": False,
            "automatic_promotion_allowed": False,
        },
        "recommended_next_lane": "EXTENDED_OBSERVATION_OPERATOR_AUTHORIZATION_REQUIRED",
        "deterministic_hash": "",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    h_input = {k: plan.get(k) for k in ["plan_status", "candidate_id", "observation_targets", "authority_boundary"]}
    plan["deterministic_hash"] = hashlib.sha256(json.dumps(h_input, sort_keys=True).encode()).hexdigest()[:16]

    PLAN_PATH.write_text(json.dumps(plan, indent=2))
    print(f"Execution plan status: {plan_status}")
    print(f"Emitted: {PLAN_PATH}")
    return plan


if __name__ == "__main__":
    main()
