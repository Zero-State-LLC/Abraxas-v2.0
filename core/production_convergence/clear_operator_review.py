"""Advisory CLEAR operator-review packet — disposition pending; no deletions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash
from core.production_convergence.clear_reference import build_clear_reference_analysis


def build_clear_operator_review_packet(repo_root: Path | None = None) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    analysis = build_clear_reference_analysis(root)
    action_counts: dict[str, int] = {}
    for entry in analysis.get("entries") or []:
        action = str(entry.get("recommended_action") or "KEEP")
        action_counts[action] = action_counts.get(action, 0) + 1

    payload: dict[str, Any] = {
        "artifact_type": "production_convergence_clear_operator_review",
        "schema_version": "clear_operator_review.v1",
        "mode": "advisory_report_only",
        "fail_closed": False,
        "evidence_state": "Partial",
        "candidate_status": "NOT_READY",
        "external_production_authorized": False,
        "mass_deletion_authorized": False,
        "operator_disposition_status": "PENDING_OPERATOR",
        "dual_control_required": True,
        "clear_analysis_schema_version": analysis.get("schema_version"),
        "clear_analysis_canonical_hash": analysis.get("canonical_hash"),
        "summary": {
            "entry_count": analysis.get("summary", {}).get("entry_count", 0),
            "recommended_action_counts": dict(sorted(action_counts.items())),
            "deletion_authorized": False,
            "operator_disposition_issued": False,
        },
        "recommended_disposition_classes": sorted(action_counts),
        "notes": [
            "Engineering packet only — does not grant deletion or EXTERNAL_PRODUCTION.",
            "Operator must explicitly disposition KEEP / archive / delete classes.",
            "No mass deletion without dual-control mandate.",
        ],
    }
    payload["canonical_hash"] = canonical_hash(
        {k: v for k, v in payload.items() if k != "canonical_hash"}
    )
    return payload
