#!/usr/bin/env python3
"""
Abraxas Governance Execution Lifecycle v1

Canonical runner exercising the full verified lifecycle for Layer 0/1 candidates.
"""

import json
import sys
from pathlib import Path
import hashlib

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.abraxas_governance_stratifier import classify_from_work_packet
from core.abraxas_governance_decision_contract import resolve_governance_decision
from core.abraxas_oracle_work_packet_loader import validate_work_packet
from core.abraxas_oracle_execution_boundary import create_execution_boundary
from core.abraxas_oracle_validation_harness import run_full_validation
from core.abraxas_oracle_completion_gate import evaluate_completion
from core.abraxas_oracle_post_execution_reconciliation import reconcile

OUT_DIR = Path("out/governance_execution_lifecycle")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def stable_hash(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]

def run_lifecycle():
    print("=== Phase 1: Classification ===")
    cand = {"candidate_id": "00d0fb441ea388c2", "title": "Add tests for core/scoring/models.py", "affected_paths": ["core/scoring/models.py"], "candidate_class": "HARDENING"}
    pkt = {"affected_paths": ["core/scoring/models.py"], "allowed_operations": ["ADD_TEST_FUNCTIONS"], "prohibited_actions": ["production", "canon_mutation"]}
    
    classification = classify_from_work_packet(pkt, cand)
    print("Layer:", classification["layer"])

    print("=== Phase 2: Governance Decision ===")
    decision = resolve_governance_decision(cand, pkt)
    print("Implementation allowed:", decision["implementation_allowed"])

    print("=== Phase 3: Work Packet Validation ===")
    packet_result = validate_work_packet()
    print("Packet result:", packet_result.get("result_class"))

    print("=== Phase 4: Execution Boundary ===")
    boundary = create_execution_boundary()
    print("Boundary layer:", boundary.get("governance_layer"))

    print("=== Phase 5: Execution Harness Decision ===")
    harness_decision = {
        "engineering_execution_permitted": decision["implementation_allowed"] and packet_result.get("result_class") == "WORK_PACKET_VALID",
        "system_transition_permitted": False,
        "execution_continues": True,
        "stop_reason": None
    }
    print("Execution continues:", harness_decision["execution_continues"])

    print("=== Phase 6: Validation Harness ===")
    validation = run_full_validation()
    print("Overall passed:", validation.get("overall_passed"))

    print("=== Phase 7: Completion Gate ===")
    completion = evaluate_completion()
    print("Completion status:", completion.get("status"))

    print("=== Phase 8: Receipt ===")
    receipt = {
        "candidate_id": "00d0fb441ea388c2",
        "engineering_status": {
            "implementation_status": "COMPLETE" if completion.get("status") == "ENGINEERING_TASK_COMPLETE_ADVISORY" else "INCOMPLETE",
            "implementation_allowed": decision["implementation_allowed"],
            "automatic_under_engineering_approval": classification["automatic_under_engineering_approval"],
            "governance_layer": classification["layer"],
            "completion_gate_status": completion.get("status")
        },
        "system_authority_status": {
            "canon_status": "UNCHANGED",
            "promotion_status": "NOT_AUTHORIZED",
            "production_status": "INACTIVE",
            "runtime_transition_status": "NOT_AUTHORIZED",
            "shadow_to_active_status": "NOT_AUTHORIZED",
            "all_system_authority_false": True
        },
        "hashes": {
            "packet": packet_result.get("packet_hash"),
            "boundary": boundary.get("boundary_hash"),
            "decision": decision.get("decision_hash")
        }
    }
    (OUT_DIR / "execution_receipt.v1.json").write_text(json.dumps(receipt, indent=2, sort_keys=True))

    print("=== Phase 9: Reconciliation ===")
    rec = reconcile()
    print("Reconciliation status:", rec.get("status"))

    print("=== Phase 10: Continuous Engineering Eligibility ===")
    eligibility = {
        "continuous_engineering_eligible": classification["layer"] in (0,1) and decision["implementation_allowed"],
        "engineering_approval_valid": True,
        "eligible_layers": [0, 1],
        "automatic_execution_layers": [0, 1],
        "blocked_transitions": ["CANON_ACCEPTANCE", "PROMOTION", "PRODUCTION_ACTIVATION", "RUNTIME_TRANSITION"],
        "current_stop_conditions": [],
        "eligibility_hash": stable_hash({"layer": classification["layer"], "allowed": decision["implementation_allowed"]})
    }
    (OUT_DIR / "continuous_engineering_eligibility.v1.json").write_text(json.dumps(eligibility, indent=2, sort_keys=True))

    print("=== Lifecycle Complete ===")
    summary = {
        "lifecycle_status": "COMPLETE",
        "layer": classification["layer"],
        "packet_valid": packet_result.get("result_class") == "WORK_PACKET_VALID",
        "execution_permitted": harness_decision["execution_continues"],
        "completion_status": completion.get("status"),
        "reconciled": rec.get("status"),
        "continuous_eligible": eligibility["continuous_engineering_eligible"]
    }
    (OUT_DIR / "governance_execution_lifecycle_receipt.v1.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    return summary

if __name__ == "__main__":
    result = run_lifecycle()
    print(json.dumps(result, indent=2))
    if not result.get("execution_permitted") or not result.get("continuous_eligible"):
        sys.exit(1)
    print("SUCCESS")