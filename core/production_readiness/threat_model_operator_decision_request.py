"""WP-P: operator decision request for Threat Model v0 acceptance.

Emits a PENDING request only. Never auto-accepts threat model or production.
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_threat_model_operator_decision_request"
OUT_DIR_REL = Path("out/production_readiness/ws8")
REQUEST_ID = "THREAT_MODEL_V0_OPERATOR_DECISION_REQUEST_001"
THREAT_MODEL_REL = Path("out/production_readiness/ws8/threat_model.v0.json")


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git_sha(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"


def build_threat_model_operator_decision_request(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    """Build PENDING operator decision request for ThreatModel.v0 review."""
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)
    model_path = repo_root / THREAT_MODEL_REL
    model_present = model_path.is_file()

    request: dict[str, Any] = {
        "schema_version": "threat_model_operator_decision_request.v0",
        "request_id": REQUEST_ID,
        "artifact_type": "operator_decision_request",
        "work_package": "WP-P_THREAT_MODEL_OPERATOR_REVIEW",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "decision_status": "PENDING_OPERATOR",
        "auto_accepted": False,
        "subject": {
            "artifact": str(THREAT_MODEL_REL).replace("\\", "/"),
            "model_id": "THREAT_MODEL_V0_PRODUCTION_CANDIDATE_001",
            "worktree_present": model_present,
            "declared_evidence_state": "Partial",
        },
        "question": (
            "Does the operator accept ThreatModel.v0 as the Partial security "
            "baseline for the bounded production candidate track, with residual "
            "risks RR-01..RR-04 explicitly acknowledged?"
        ),
        "allowed_decisions": [
            {
                "code": "ACCEPT_PARTIAL_BASELINE",
                "effect": (
                    "Marks threat model operator-reviewed at Partial. Does NOT "
                    "authorize production activation. RISK-014 remains MITIGATING "
                    "until Verified controls land."
                ),
            },
            {
                "code": "REQUEST_REVISIONS",
                "effect": "Return for threat/control edits; keep PENDING.",
            },
            {
                "code": "REJECT",
                "effect": "Block freeze/candidate until a revised model is proposed.",
            },
            {
                "code": "DEFER",
                "effect": "Explicit hold; freeze remains blocked.",
            },
        ],
        "constraints": [
            "No autonomous ACCEPT without human-authored decision record",
            "ACCEPT_PARTIAL_BASELINE does not grant production activation",
            "Fail-closed authority locks remain binding",
            "Neon Genie remains non-control-plane",
        ],
        "required_decision_record_fields": [
            "decision_code",
            "operator_id_or_role",
            "decided_at",
            "acknowledged_residual_risk_ids",
            "repository_sha",
            "notes",
        ],
        "decision_record_path_hint": (
            "out/production_readiness/ws8/threat_model_operator_decision_record.v0.json"
        ),
        "linked_artifacts": [
            str(THREAT_MODEL_REL).replace("\\", "/"),
            "out/production_readiness/ws8/recovery_drill.v0.json",
            "out/production_readiness/ws8/notion_readiness_mapping.v1.json",
            "out/production_readiness/CONTINUATION_PLAN.v3.md",
            "https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/971",
        ],
        "operator_actions": [
            "Read threat_model.v0.json assets, threats, controls, residual_risks",
            "Choose one allowed decision_code",
            "Emit human-authored decision record at path hint (not this request)",
            "If ACCEPT_PARTIAL_BASELINE: link decision in Notion tracker (RISK-012 residual)",
            "Do not flip production readiness to READY from this request alone",
        ],
        "notes": [
            "This is a request, not a decision. decision_status stays PENDING_OPERATOR.",
            "WP-P exit for operator acceptance is a separate decision record artifact.",
            "Does not authorize production activation.",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(
            out_dir / "threat_model_operator_decision_request.v0.json",
            request,
        )

    return request
