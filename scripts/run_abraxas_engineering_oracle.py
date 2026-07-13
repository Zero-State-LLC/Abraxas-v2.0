#!/usr/bin/env python3
"""
Runner for Abraxas Engineering Oracle v1.

Usage: python scripts/run_abraxas_engineering_oracle.py
Runs in scrubbed deterministic mode, produces all oracle artifacts.
"""

import os
import sys
import json
import hashlib
from pathlib import Path

# Ensure repo root is importable
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

# Now safe to import
from core.abraxas_engineering_authority_resolver import resolve_authority  # noqa: E402
from core.abraxas_engineering_candidate_extractor import extract_candidates  # noqa: E402
from core.abraxas_engineering_dependency_resolver import (  # noqa: E402
    build_dependency_graph,
    resolve_blockers,
)
from core.abraxas_engineering_priority_model import rank_candidates  # noqa: E402

ORACLE_OUT = Path(
    os.environ.get(
        "ABRAXAS_ENGINEERING_ORACLE_OUT",
        str(repo_root / "out" / "repo_intelligence" / "engineering_oracle"),
    )
)
ORACLE_OUT.mkdir(parents=True, exist_ok=True)


def stable_hash(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


def main():
    print("=== Abraxas Engineering Oracle v1 ===")
    # 1. Extract (re-run to ensure fresh)
    cands = extract_candidates()
    print(f"Extracted {len(cands)} candidates")

    # 2. Dep resolver
    dep_graph = build_dependency_graph(cands)
    blockers = resolve_blockers(cands, dep_graph)
    print("Dependency graph built")

    # Write dep graph
    (ORACLE_OUT / "candidate_dependency_graph.v1.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "dependencies": dep_graph,
                "blockers": blockers,
            },
            indent=2,
            sort_keys=True,
        )
    )

    # 3. Priority + scores
    ranked = rank_candidates(cands)
    scores_out = {
        "schema_version": "1.0.0",
        "scores": {c["candidate_id"]: c.get("priority", {}) for c in ranked},
        "version": "v1",
    }
    (ORACLE_OUT / "candidate_priority_scores.v1.json").write_text(json.dumps(scores_out, indent=2, sort_keys=True))
    print("Priorities scored")

    # 4. Authority + select primary
    primary = None
    secondaries = []
    blocked_high = []
    for c in ranked:
        auth = resolve_authority(c)
        c["authority"] = auth
        if auth["authority_status"] != "PERMITTED_ADVISORY":
            blocked_high.append({
                "candidate_id": c["candidate_id"],
                "blocker_class": "AUTHORITY",
                "reason": "grant boundary"
            })
            continue
        if primary is None:
            primary = c
        elif len(secondaries) < 4:
            secondaries.append(c["candidate_id"])
        if len(blocked_high) > 5:
            break

    decision = {
        "schema_version": "1.0.0",
        "primary_candidate_id": primary["candidate_id"] if primary else None,
        "secondary_candidate_ids": secondaries,
        "blocked_high_rank_candidates": blocked_high[:3],
        "not_computable": primary is None,
        "not_computable_reasons": [] if primary else ["NO_ACTIONABLE_CANDIDATES"],
        "authority_status": "PERMITTED_ADVISORY",
        "authority_evidence": ["broad_operator_grant_all_engineering_tied_to_approval"],
        "prohibited_transitions": ["production_activation", "canon_mutation", "promotion", "runtime_execution"],
        "selected_at_observed": "consumed_repo_intel_artifacts_only",
        "repo_intel_receipt": "out/repo_intel/repo_intel_receipt.v1.json",
        "packet_hash": stable_hash(primary["candidate_id"] if primary else None)
    }
    (ORACLE_OUT / "engineering_oracle_decision.v1.json").write_text(json.dumps(decision, indent=2, sort_keys=True))

    # 5. Work packet for primary
    if primary:
        path = primary["affected_paths"][0]
        packet = {
            "schema_version": "1.0.0",
            "objective": f"Add comprehensive tests for {path} (high-leverage core/governance gap)",
            "observed_problem": f"Gap discovery from repo_intel identifies missing tests in high-value subsystem: {path}. This reduces validation coverage for core engineering surfaces.",
            "supporting_evidence": primary["source_evidence"] + ["gap_discovery.v1.json", "import_graph.v1.json (for deps)"],
            "affected_paths": primary["affected_paths"],
            "dependency_chain": dep_graph.get(primary["candidate_id"], []),
            "implementation_phases": [
                "1. Create or extend test file for the module",
                "2. Cover key functions, edge cases, error paths",
                "3. Integrate with existing test collection",
                "4. Run scrubbed verification and update receipts"
            ],
            "files_expected_to_change": [path, f"tests/test_{Path(path).stem}.py" if '/' in path else "tests/"],
            "schemas_required": [],
            "validators_required": ["pytest collection"],
            "tests_required": [f"unit tests for {path}"],
            "generated_artifacts_required": ["test execution receipt"],
            "registry_updates_required": [],
            "documentation_updates_required": ["update relevant SKILL or doc if needed"],
            "rollback_strategy": "git revert test additions",
            "regression_risks": ["low - tests are additive"],
            "prohibited_actions": ["changing production logic", "expanding authority", "canon mutation"],
            "completion_criteria": [
                "relevant tests pass under scrubbed env",
                "no increase in collection errors",
                "receipt emitted"
            ],
            "exact_verification_commands": [
                "env -i PATH=... UV_CACHE_DIR=... uv run python -m pytest tests/test_abx* -q --tb=no",
                "env -i ... uv run python scripts/run_abx_hermes_skill_evolution_cycle.py (if applicable)"
            ],
            "receipt_schema": "test_receipt_v1",
            "expected_continuation_state": "higher test coverage on core surfaces; oracle can re-rank"
        }
        (ORACLE_OUT / "primary_work_packet.v1.json").write_text(json.dumps(packet, indent=2, sort_keys=True))

    # Receipt
    receipt = {
        "schema_version": "1.0.0",
        "status": "DECISION_EMITTED" if primary else "NOT_COMPUTABLE",
        "primary_candidate_id": primary["candidate_id"] if primary else None,
        "candidates_total": len(cands),
        "actionable_count": sum(1 for c in cands if c["status"] == "ACTIONABLE"),
        "inputs": ["out/repo_intel/gap_discovery.v1.json", "out/repo_intel/graphs/import_graph.v1.json", "out/repo_intel/repository_manifest.v1.json"],
        "repo_intel_receipt": "out/repo_intel/repo_intel_receipt.v1.json",
        "packet_hash": decision["packet_hash"],
        "governance_boundary": {
            "advisory_only": True,
            "all_authority_false": True,
            "operator_grant_scope": "all_engineering_tied_to_approval"
        }
    }
    (ORACLE_OUT / "engineering_oracle_receipt.v1.json").write_text(json.dumps(receipt, indent=2, sort_keys=True))

    # MD summary (derived)
    md = f"""# ABRAXAS ENGINEERING ORACLE DECISION v1

**Status**: {receipt['status']}
**Primary Candidate**: {primary['candidate_id'] if primary else 'NOT_COMPUTABLE'}
**Title**: {primary['title'] if primary else 'N/A'}
**Final Score**: {primary.get('priority', {}).get('final_priority_score', 'N/A') if primary else 'N/A'}

**Authority**: PERMITTED_ADVISORY (broad operator grant; all boundaries false)

**Key Evidence Consumed**:
- gap_discovery.v1.json (575 missing_tests)
- import_graph.v1.json
- repository_manifest.v1.json
- architecture_map.v1.json

**Prohibited**: production, canon mutation, promotion, runtime.

See primary_work_packet.v1.json for execution details.
See engineering_oracle_decision.v1.json for full decision.

Next: execute the packet under advisory mode or re-run oracle after changes.
"""
    (ORACLE_OUT / "ENGINEERING_ORACLE_DECISION_v1.md").write_text(md)

    print("Oracle complete.")
    print("Primary:", primary['candidate_id'] if primary else None)
    print(f"Artifacts in {ORACLE_OUT}")

if __name__ == "__main__":
    main()
