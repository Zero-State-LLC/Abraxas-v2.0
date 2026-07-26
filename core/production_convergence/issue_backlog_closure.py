"""Advisory receipt for pre–Phase 10 GitHub issue backlog closure."""

from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash

CLOSED_ISSUES: tuple[dict[str, Any], ...] = (
    {
        "issue": 546,
        "title": "Sprint 1: Foundation Activation - June 2026",
        "disposition": "completed_superseded_by_governance_v3_and_convergence",
        "recommended_action": "CLOSE",
    },
    {
        "issue": 547,
        "title": "Sprint 2: Intelligence Activation & Expansion - June 2026",
        "disposition": "completed_superseded_by_governance_v3_and_convergence",
        "recommended_action": "CLOSE",
    },
    {
        "issue": 881,
        "title": "v2.7.2 - Persistent Execution + Secret Vault (sandbox-gated)",
        "disposition": "advisory_complete_gate_deferred",
        "recommended_action": "CLOSE",
        "evidence_paths": [
            "out/audit/oracle_sandbox_probe_gate_proposal_receipt_001.latest.json",
        ],
        "evidence_hashes": [
            "2117fde5249744832d5a861c459f2b00dc05ea3693704cf13ed4c729799592b8",
        ],
        "merged_prs": [886, 887, 888],
    },
    {
        "issue": 892,
        "title": "v2.7.3 - ORACLE_SANDBOX_PROBE_GATE + Persistent Execution Baseline",
        "disposition": "planning_complete_probe_deferred",
        "recommended_action": "CLOSE",
        "evidence_paths": [
            "out/audit/abx_ledger_frontier_reconcile_denial_001.latest.json",
        ],
        "evidence_hashes": [
            "0b28044325cad08cad70e89f895f4a45729b68f6240fcd7c40b2331e45d77066",
        ],
        "merged_prs": [891, 894, 895],
    },
)


def build_issue_backlog_closure_receipt() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "artifact_type": "production_convergence_issue_backlog_closure",
        "schema_version": "issue_backlog_closure.v1",
        "mode": "advisory_report_only",
        "fail_closed": False,
        "evidence_state": "Partial",
        "candidate_status": "NOT_READY",
        "external_production_authorized": False,
        "oracle_sandbox_probe_gate_confirmed": False,
        "mass_deletion_authorized": False,
        "closed_issues": list(CLOSED_ISSUES),
        "summary": {
            "closed_count": len(CLOSED_ISSUES),
            "sandbox_probe_authorized": False,
            "gate_phrase_issued": False,
        },
        "notes": [
            "GitHub issue closeout for expired sprints and advisory-complete oracle lanes.",
            "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED remains unissued; no probe execution authorized.",
            "Phase 10 handoff: residual viz *_replay.py and deferred WP-D research writers.",
        ],
        "docs_pointer": "docs/status/ISSUE_BACKLOG_CLOSURE_001.md",
    }
    payload["canonical_hash"] = canonical_hash(
        {k: v for k, v in payload.items() if k != "canonical_hash"}
    )
    return payload
