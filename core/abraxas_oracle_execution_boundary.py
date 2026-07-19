#!/usr/bin/env python3
"""
Abraxas Oracle Execution Boundary v1

Immutable boundary for advisory execution.
Integrates Governance Stratification v1 (Layer 0 default).
"""

import json
import hashlib
import sys
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.abraxas_governance_stratifier import classify_from_work_packet

def compute_boundary_hash(boundary: Dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(boundary, sort_keys=True, default=str).encode()).hexdigest()[:16]

def create_execution_boundary(candidate_id: str = "00d0fb441ea388c2",
                               work_packet: Dict[str, Any] | None = None,
                               candidate: Dict[str, Any] | None = None) -> Dict[str, Any]:

    if work_packet is None:
        work_packet = {"affected_paths": ["core/scoring/models.py"],
                       "allowed_operations": ["ADD_TEST_FUNCTIONS", "CREATE_TEST_FILE"]}

    if candidate is None:
        candidate = {"candidate_id": candidate_id, "title": "Add tests for core/scoring/models.py"}

    classification = classify_from_work_packet(work_packet, candidate)

    affected = work_packet.get("affected_paths", [f"core/{candidate_id[:8]}.py"])
    test_paths = [f"tests/test_{Path(p).stem}.py" for p in affected]

    boundary = {
        "candidate_id": candidate_id,
        "governance_layer": classification["layer"],
        "governance_layer_name": classification["layer_name"],
        "automatic_under_engineering_approval": classification["automatic_under_engineering_approval"],
        "execution_mode": "ADVISORY_ENGINEERING" if classification["layer"] <= 1 else "REQUIRES_REVIEW",
        "allowed_paths": affected,
        "conditionally_allowed_paths": test_paths,
        "prohibited_paths": ["*"],
        "allowed_operations": work_packet.get("allowed_operations", ["ADD_TEST_FUNCTIONS", "CREATE_TEST_FILE"]),
        "prohibited_operations": [
            "production_activation",
            "canon_mutation",
            "runtime_execution",
            "authority_field_mutation",
            "operator_grant_broadening",
            "governance_hold_removal",
            "shadow_promotion",
            "historical_receipt_deletion",
            "unrelated_surface_mutation",
            "validator_bypass",
            "test_weakening"
        ],
        "authority_status": "PERMITTED_ADVISORY",
        "all_authority_false": True,
        "production_activation_allowed": False,
        "canon_mutation_allowed": False,
        "promotion_allowed": False,
        "runtime_execution_allowed": False,
        "shadow_to_active_transition_allowed": False,
        "stratification_evidence": classification,
        "boundary_hash": None
    }
    boundary["boundary_hash"] = compute_boundary_hash(boundary)
    return boundary

def main():
    # TD Wave 1: pure library; publish via scripts/run_oracle_execution_boundary.py
    b = create_execution_boundary()
    print(json.dumps(b, indent=2, sort_keys=True))
    print("Governance Layer:", b["governance_layer"], "-", b["governance_layer_name"])
    print("Note: not writing out/; use scripts/run_oracle_execution_boundary.py to publish.")

if __name__ == "__main__":
    main()
