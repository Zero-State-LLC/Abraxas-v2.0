#!/usr/bin/env python3
"""
Abraxas Governance Stratifier v1

Classifies engineering work into layers per GOVERNANCE_STRATIFICATION_001.md.
Default: Layer 0 (Internal Engineering) unless objective evidence shows escalation.
"""

import json
from typing import Dict, Any, List

LAYER_0_KEYWORDS = {
    "test", "schema", "validator", "receipt", "documentation", "refactor",
    "tooling", "automation", "repo_intel", "oracle", "harness", "ledger",
    "boundary", "classifier", "stratifier", "planning", "intelligence"
}

LAYER_1_KEYWORDS = {
    "shadow", "research", "simulation", "advisory", "experimental", "proposal",
    "candidate_implementation", "alternative_algorithm"
}

LAYER_2_INDICATORS = {
    "canonical_schema", "canon", "governance_definition", "operator_policy",
    "system_contract", "accepted_truth"
}

LAYER_3_INDICATORS = {
    "production", "runtime_execution", "activation", "deployment", "promotion",
    "autonomous_execution", "live_decision"
}

def classify_work(candidate: Dict[str, Any], affected_paths: List[str], operations: List[str]) -> Dict[str, Any]:
    """Returns layer classification and evidence."""
    title = (candidate.get("title", "") + " " + " ".join(affected_paths) + " " + " ".join(operations)).lower()
    evidence = []

    layer = 0
    reasons = []

    # Layer 3 check (highest first)
    for ind in LAYER_3_INDICATORS:
        if ind in title:
            layer = 3
            evidence.append(f"layer3_indicator:{ind}")
            reasons.append("modifies runtime/production/activation")
            break

    if layer < 3:
        for ind in LAYER_2_INDICATORS:
            if ind in title:
                layer = 2
                evidence.append(f"layer2_indicator:{ind}")
                reasons.append("modifies canonical semantics or governance definition")
                break

    if layer == 0:
        for kw in LAYER_1_KEYWORDS:
            if kw in title:
                layer = 1
                evidence.append(f"layer1_keyword:{kw}")
                reasons.append("advisory / experimental / research surface")
                break

    if layer == 0:
        # Default Layer 0 for typical engineering
        matched = [kw for kw in LAYER_0_KEYWORDS if kw in title]
        if matched or not any(ind in title for ind in (LAYER_2_INDICATORS | LAYER_3_INDICATORS)):
            layer = 0
            evidence.append("default_layer0_internal_engineering")
            reasons.append("routine engineering (tests, schemas, refactors, intelligence, tooling)")

    classification = {
        "layer": layer,
        "layer_name": ["Internal Engineering", "Advisory Architecture", "Canon", "Runtime"][layer],
        "automatic_under_engineering_approval": layer <= 1,
        "reasons": reasons,
        "evidence": evidence,
        "candidate_id": candidate.get("candidate_id"),
        "stratification_version": "1.0.0"
    }
    return classification

def classify_from_work_packet(work_packet: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
    affected = work_packet.get("affected_paths", [])
    ops = work_packet.get("allowed_operations", []) + work_packet.get("prohibited_operations", [])
    return classify_work(candidate, affected, ops)

def main():
    # Example usage with last executed candidate
    example_candidate = {"candidate_id": "00d0fb441ea388c2", "title": "Add tests for core/scoring/models.py"}
    example_packet = {"affected_paths": ["core/scoring/models.py"], "allowed_operations": ["ADD_TEST_FUNCTIONS"]}
    result = classify_from_work_packet(example_packet, example_candidate)
    print(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    main()
