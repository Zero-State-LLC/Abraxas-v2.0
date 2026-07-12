#!/usr/bin/env python3
"""
Abraxas Oracle Completion Gate v1

Separates engineering completion from system authority.
Layer 0/1 can complete as ENGINEERING_TASK_COMPLETE_ADVISORY while all authority remains false.
"""

import json
from pathlib import Path
from typing import Dict, Any

def evaluate_completion() -> Dict[str, Any]:
    EXEC_DIR = Path("out/oracle_execution")
    validation = {}
    vpath = EXEC_DIR / "validation_results.v1.json"
    if vpath.exists():
        validation = json.loads(vpath.read_text())

    overall = validation.get("overall_passed", False)

    # Two-axis status
    engineering_complete = overall
    canon_unchanged = True
    production_inactive = True
    promotion_unauthorized = True

    if engineering_complete:
        status = "ENGINEERING_TASK_COMPLETE_ADVISORY"
    else:
        status = "ENGINEERING_TASK_INCOMPLETE"

    gate = {
        "candidate_id": "00d0fb441ea388c2",
        "status": status,
        "engineering_implementation_complete": engineering_complete,
        "canon_accepted": False,
        "production_active": False,
        "promoted": False,
        "runtime_transitioned": False,
        "all_system_authority_false": True,
        "criteria_checked": [
            "work_packet_valid",
            "boundary_respected",
            "candidate_tests_pass",
            "regression_pass",
            "replay_pass",
            "governance_invariants",
            "no_authority_change",
            "no_protected_transition"
        ],
        "all_criteria_met": overall
    }

    EXEC_DIR.mkdir(parents=True, exist_ok=True)
    (EXEC_DIR / "completion_gate.v1.json").write_text(json.dumps(gate, indent=2, sort_keys=True))
    return gate

if __name__ == "__main__":
    print(json.dumps(evaluate_completion(), indent=2))