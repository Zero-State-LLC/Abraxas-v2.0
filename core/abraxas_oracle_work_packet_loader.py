#!/usr/bin/env python3
"""
Abraxas Oracle Work Packet Loader and Validator v1

Integrates governance stratification / decision contract.
Layer 0/1 valid engineering packets are accepted even when all system authority is false.
"""

import json
import hashlib
import sys
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.abraxas_governance_decision_contract import resolve_governance_decision

ORACLE_DIR = Path("out/repo_intelligence/engineering_oracle")
CANDIDATES = ORACLE_DIR / "engineering_candidates.v1.json"
DECISION = ORACLE_DIR / "engineering_oracle_decision.v1.json"
PACKET = ORACLE_DIR / "primary_work_packet.v1.json"

def stable_hash(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]

def load_json(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))

def validate_work_packet() -> Dict[str, Any]:
    result = {
        "result_class": "WORK_PACKET_INVALID", 
        "errors": [], 
        "candidate_id": None,
        "governance_decision": None
    }

    try:
        decision = load_json(DECISION)
        packet = load_json(PACKET)
        cands = load_json(CANDIDATES)["candidates"]
    except Exception as e:
        result["errors"].append(f"load_error: {e}")
        return result

    primary_id = decision.get("primary_candidate_id")
    result["candidate_id"] = primary_id

    if not primary_id:
        result["errors"].append("no_primary_in_decision")
        return result

    cand = next((c for c in cands if c["candidate_id"] == primary_id), None)
    if not cand:
        result["errors"].append("candidate_not_in_candidates_file")
        return result

    # Basic binding
    if packet.get("schema_version") != "1.0.0":
        result["errors"].append("packet_schema_mismatch")
    if decision.get("schema_version") != "1.0.0":
        result["errors"].append("decision_schema_mismatch")

    # Use the two-axis governance decision
    gov_decision = resolve_governance_decision(cand, packet, engineering_approval_valid=True)
    result["governance_decision"] = gov_decision

    if not gov_decision.get("implementation_allowed"):
        if gov_decision.get("governance_layer", 0) >= 2:
            result["result_class"] = "CANON_TRANSITION_REQUIRES_AUTHORIZATION" if gov_decision["governance_layer"] == 2 else "RUNTIME_TRANSITION_REQUIRES_AUTHORIZATION"
            result["errors"].append("protected_transition_requires_authorization")
            return result
        else:
            result["result_class"] = "ENGINEERING_APPROVAL_MISSING"
            result["errors"].append("governance_layer_requires_explicit_authorization")
            return result

    # Legacy PERMITTED_ADVISORY check (kept for compatibility)
    if decision.get("authority_status") != "PERMITTED_ADVISORY":
        result["result_class"] = "AUTHORITY_BLOCKED"
        result["errors"].append("authority_not_permitted_advisory")
        return result

    if "broad_operator_grant_all_engineering_tied_to_approval" not in cand.get("authority_observed", []):
        result["errors"].append("missing_broad_grant_evidence")

    affected = packet.get("affected_paths", [])
    if not affected:
        result["errors"].append("no_affected_paths")

    prohibited = packet.get("prohibited_actions", [])
    if not any("production" in str(p).lower() or "canon" in str(p).lower() for p in prohibited):
        result["errors"].append("insufficient_prohibited_actions")

    if result["errors"]:
        return result

    result["result_class"] = "WORK_PACKET_VALID"
    result["packet_hash"] = stable_hash(packet)
    result["decision_hash"] = stable_hash(decision)
    result["bound_to_candidate"] = primary_id
    return result

def main():
    res = validate_work_packet()
    print(json.dumps(res, indent=2, sort_keys=True))
    return res

if __name__ == "__main__":
    main()