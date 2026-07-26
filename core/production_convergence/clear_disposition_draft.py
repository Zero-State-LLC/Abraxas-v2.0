"""CLEAR engineering disposition draft — dual-control still required; no deletions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash
from core.production_convergence.clear_reference import build_clear_reference_analysis

# Engineering may accept non-delete recommendations; never authorize deletion here.
_NON_DELETE_ACTIONS = frozenset(
    {"KEEP", "DEPRECATE_DOCUMENT_ONLY", "DEFER_CLEAR", "MERGE_CANDIDATE"}
)


def build_clear_disposition_draft(repo_root: Path | None = None) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    analysis = build_clear_reference_analysis(root)
    entries_out: list[dict[str, Any]] = []
    action_counts: dict[str, int] = {}

    for entry in analysis.get("entries") or []:
        if not isinstance(entry, dict):
            continue
        recommended = str(entry.get("recommended_action") or "KEEP")
        if recommended not in _NON_DELETE_ACTIONS:
            recommended = "DEFER_CLEAR"
        action_counts[recommended] = action_counts.get(recommended, 0) + 1
        entries_out.append(
            {
                "path": entry.get("path"),
                "classification": entry.get("classification"),
                "role": entry.get("role"),
                "recommended_action": recommended,
                "engineering_disposition": recommended,
                "deletion_proposed": False,
                "execution_authorized": False,
                "deletion_blocker": list(entry.get("deletion_blocker") or []),
            }
        )

    entries_out.sort(key=lambda item: str(item.get("path") or ""))

    payload: dict[str, Any] = {
        "artifact_type": "production_convergence_clear_disposition_draft",
        "schema_version": "clear_disposition_draft.v1",
        "mode": "advisory_report_only",
        "fail_closed": False,
        "evidence_state": "Partial",
        "candidate_status": "NOT_READY",
        "external_production_authorized": False,
        "mass_deletion_authorized": False,
        "deletions_executed": False,
        "paths_deleted": [],
        "operator_disposition_status": "PENDING_OPERATOR",
        "engineering_disposition_status": "DRAFT_ISSUED",
        "dual_control_required": True,
        "dual_control": {
            "control_a_attestation": None,
            "control_b_attestation": None,
            "status": "PENDING",
        },
        "clear_analysis_schema_version": analysis.get("schema_version"),
        "clear_analysis_canonical_hash": analysis.get("canonical_hash"),
        "entries": entries_out,
        "summary": {
            "entry_count": len(entries_out),
            "engineering_disposition_counts": dict(sorted(action_counts.items())),
            "deletion_proposed_count": 0,
            "deletion_authorized": False,
            "operator_disposition_issued": False,
            "dual_control_complete": False,
        },
        "notes": [
            "Engineering draft only — accepts CLEAR recommended_action classes without deletion.",
            "Does not grant mass deletion, EXTERNAL_PRODUCTION, or dual-control completion.",
            "Operator dual-control attestations required before any removal.",
            "No paths deleted in this phase.",
        ],
    }
    payload["canonical_hash"] = canonical_hash(
        {k: v for k, v in payload.items() if k != "canonical_hash"}
    )
    return payload
