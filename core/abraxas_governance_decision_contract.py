#!/usr/bin/env python3
"""
Abraxas Governance Decision Contract v1

Two-axis decision model:
- Engineering implementation permission (Layer 0/1 under approval)
- System authority (Canon, Promotion, Production, Runtime) — always false for advisory engineering

Reuses core/abraxas_governance_stratifier.py
"""

import json
import hashlib
import sys
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.abraxas_governance_stratifier import classify_from_work_packet

def compute_decision_hash(decision: Dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(decision, sort_keys=True, default=str).encode()).hexdigest()[:16]

def resolve_governance_decision(
    candidate: Dict[str, Any],
    work_packet: Dict[str, Any],
    engineering_approval_valid: bool = True
) -> Dict[str, Any]:
    classification = classify_from_work_packet(work_packet, candidate)
    layer = classification["layer"]
    automatic = classification.get("automatic_under_engineering_approval", False)

    implementation_allowed = engineering_approval_valid and layer in (0, 1) and automatic
    advisory_output_required = layer <= 1

    decision = {
        "governance_layer": layer,
        "layer_name": classification["layer_name"],
        "engineering_approval_valid": engineering_approval_valid,
        "automatic_under_engineering_approval": automatic,
        "implementation_allowed": implementation_allowed,
        "advisory_output_required": advisory_output_required,
        "canon_acceptance_allowed": False,
        "promotion_allowed": False,
        "production_activation_allowed": False,
        "runtime_transition_allowed": False,
        "operator_review_required": not implementation_allowed or layer >= 2,
        "review_reason": None if implementation_allowed else "LAYER_REQUIRES_EXPLICIT_AUTHORIZATION",
        "decision_evidence": classification.get("evidence", []),
        "decision_hash": None
    }
    decision["decision_hash"] = compute_decision_hash(decision)
    return decision

def main():
    example_candidate = {"candidate_id": "00d0fb441ea388c2", "title": "Add tests for core/scoring/models.py"}
    example_packet = {"affected_paths": ["core/scoring/models.py"], "allowed_operations": ["ADD_TEST_FUNCTIONS"]}
    result = resolve_governance_decision(example_candidate, example_packet)
    print(json.dumps(result, indent=2, sort_keys=True))
    return result

if __name__ == "__main__":
    main()