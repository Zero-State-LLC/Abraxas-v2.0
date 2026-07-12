#!/usr/bin/env python3
"""
Abraxas Engineering Oracle v1 (deterministic)

Consumes verified repo_intel artifacts → candidates → prioritized decision + work packet.
All advisory/SHADOW only. No mutation.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List

from core.abraxas_engineering_priority_model import rank_candidates
from core.abraxas_engineering_authority_resolver import resolve_authority

REPO_ROOT = Path.cwd()
CAND_FILE = REPO_ROOT / "out" / "repo_intelligence" / "engineering_oracle" / "engineering_candidates.v1.json"
DECISION_FILE = REPO_ROOT / "out" / "repo_intelligence" / "engineering_oracle" / "engineering_oracle_decision.v1.json"
PACKET_FILE = REPO_ROOT / "out" / "repo_intelligence" / "engineering_oracle" / "primary_work_packet.v1.json"
RECEIPT_FILE = REPO_ROOT / "out" / "repo_intelligence" / "engineering_oracle" / "engineering_oracle_receipt.v1.json"
MD_SUMMARY = REPO_ROOT / "out" / "repo_intelligence" / "engineering_oracle" / "ENGINEERING_ORACLE_DECISION_v1.md"

def load(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))

def stable_hash(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:16]

def select(cands: List[Dict[str, Any]]) -> Dict[str, Any]:
    ranked = rank_candidates(cands)
    primary = None
    secondaries = []
    blocked = []

    for c in ranked:
        auth = resolve_authority(c)
        if auth["authority_status"] != "PERMITTED_ADVISORY":
            blocked.append({"candidate_id": c["candidate_id"], "blocker_class": "AUTHORITY", "reason": "outside_grant_scope"})
            continue
        if primary is None:
            primary = c
        elif len(secondaries) < 4:
            secondaries.append(c)
        if len(secondaries) >= 4 and len(blocked) >= 3:
            break

    decision = {
        "schema_version": "1.0.0",
        "primary_candidate_id": primary["candidate_id"] if primary else None,
        "secondary_candidate_ids": [s["candidate_id"] for s in secondaries],
        "blocked_high_rank_candidates": blocked[:5],
        "not_computable": primary is None,
        "not_computable_reasons": ["INSUFFICIENT_EVIDENCE"] if not primary else [],
        "authority_status": "PERMITTED_ADVISORY",
        "authority_evidence": ["broad_operator_grant_all_engineering_tied_to_approval"],
        "prohibited_transitions": ["production_activation", "canon_mutation", "promotion"],
        "selected_at_observed": "from_repo_intel_artifacts",
        "repo_intel_receipt": "out/repo_intel/repo_intel_receipt.v1.json",
        "packet_hash": stable_hash({"primary": primary["candidate_id"] if primary else None})
    }
    return decision, primary

def build_work_packet(cand: Dict[str, Any]) -> Dict[str, Any]:
    path = cand["affected_paths"][0]
    return {
        "schema_version": "1.0.0",
        "objective": f"Add missing tests for high-value module: {path}",
        "observed_problem": f"Gap discovery reports missing tests for {path} (core/governance impact).",
        "supporting_evidence": [f"gap_discovery.v1.json:missing_tests:{path}"],
        "affected_paths": cand["affected_paths"],
        "dependency_chain": [],
        "implementation_phases": [
            "1. Locate or create test file",
            "2. Cover main paths and error cases",
            "3. Add to relevant test collection",
            "4. Verify with scrubbed pytest"
        ],
        "files_expected_to_change": [path, f"tests/test_{Path(path).stem}.py"],
        "schemas_required": [],
        "validators_required": ["existing pytest collection"],
        "tests_required": [f"tests for {path}"],
        "generated_artifacts_required": ["test receipt"],
        "registry_updates_required": [],
        "documentation_updates_required": [],
        "rollback_strategy": "Delete test file / revert addition",
        "regression_risks": ["none - additive tests only"],
        "prohibited_actions": ["mutating core logic", "changing authority"],
        "completion_criteria": ["tests pass in scrubbed env", "no new collection errors"],
        "exact_verification_commands": [
            "env -i ... uv run python -m pytest tests/ -q --tb=no -k 'relevant_module'"
        ],
        "receipt_schema": "test_execution_receipt.v1",
        "expected_continuation_state": "increased test coverage in high-value subsystem"
    }

def main() -> None:
    cands = load(CAND_FILE)["candidates"]
    decision, primary = select(cands)

    with open(DECISION_FILE, "w") as f:
        json.dump(decision, f, indent=2, sort_keys=True)

    if primary:
        packet = build_work_packet(primary)
        with open(PACKET_FILE, "w") as f:
            json.dump(packet, f, indent=2, sort_keys=True)

    receipt = {
        "schema_version": "1.0.0",
        "status": "DECISION_EMITTED" if primary else "NOT_COMPUTABLE",
        "primary_candidate": primary["candidate_id"] if primary else None,
        "candidates_consumed": len(cands),
        "repo_intel_receipt": "out/repo_intel/repo_intel_receipt.v1.json",
        "packet_hash": decision["packet_hash"]
    }
    with open(RECEIPT_FILE, "w") as f:
        json.dump(receipt, f, indent=2, sort_keys=True)

    # Human summary (derived only)
    md = f"""# ENGINEERING ORACLE DECISION v1

**Primary:** {primary['candidate_id'] if primary else 'NOT_COMPUTABLE'}  
**Title:** {primary['title'] if primary else 'N/A'}  
**Score:** {primary.get('priority', {}).get('final_priority_score', 'N/A') if primary else 'N/A'}

Authority: PERMITTED_ADVISORY (broad grant, all boundaries false)

See primary_work_packet.v1.json for execution details.
"""
    with open(MD_SUMMARY, "w") as f:
        f.write(md)

    print("Oracle decision emitted.")
    print("Primary:", primary["candidate_id"] if primary else None)

if __name__ == "__main__":
    main()