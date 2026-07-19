"""WP-P+: operator decision record for Threat Model v0.

Records an explicit human decision against the WP-P request.
Never auto-accepts without caller-supplied decision_code.
Does not authorize production activation.
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_threat_model_operator_decision_record"
OUT_DIR_REL = Path("out/production_readiness/ws8")
RECORD_ID = "THREAT_MODEL_V0_OPERATOR_DECISION_RECORD_001"
REQUEST_REL = Path("out/production_readiness/ws8/threat_model_operator_decision_request.v0.json")
MODEL_REL = Path("out/production_readiness/ws8/threat_model.v0.json")

ALLOWED_CODES = frozenset(
    {"ACCEPT_PARTIAL_BASELINE", "REQUEST_REVISIONS", "REJECT", "DEFER"}
)
DEFAULT_RESIDUALS = ["RR-01", "RR-02", "RR-03", "RR-04", "RR-05"]


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


def build_threat_model_operator_decision_record(
    repo_root: Path,
    *,
    decision_code: str,
    operator_id_or_role: str,
    notes: str,
    acknowledged_residual_risk_ids: list[str] | None = None,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    """Build decision record. Requires explicit decision_code from operator."""
    repo_root = Path(repo_root).resolve()
    if decision_code not in ALLOWED_CODES:
        raise ValueError(
            f"decision_code must be one of {sorted(ALLOWED_CODES)}, got {decision_code!r}"
        )
    if not operator_id_or_role.strip():
        raise ValueError("operator_id_or_role is required")
    if not notes.strip():
        raise ValueError("notes are required for auditability")

    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)
    residuals = list(acknowledged_residual_risk_ids or DEFAULT_RESIDUALS)

    production_activation_authorized = False
    readiness_state = "NOT_READY"
    risk_014_status = "MITIGATING"
    if decision_code == "ACCEPT_PARTIAL_BASELINE":
        operator_review_state = "ACCEPTED_PARTIAL"
    elif decision_code == "REQUEST_REVISIONS":
        operator_review_state = "REVISIONS_REQUESTED"
    elif decision_code == "REJECT":
        operator_review_state = "REJECTED"
    else:
        operator_review_state = "DEFERRED"

    record: dict[str, Any] = {
        "schema_version": "threat_model_operator_decision_record.v0",
        "record_id": RECORD_ID,
        "artifact_type": "operator_decision_record",
        "work_package": "WP-P_PLUS_THREAT_MODEL_OPERATOR_DECISION",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "request_ref": str(REQUEST_REL).replace("\\", "/"),
        "subject_ref": str(MODEL_REL).replace("\\", "/"),
        "decision_code": decision_code,
        "operator_id_or_role": operator_id_or_role,
        "decided_at": produced_at,
        "acknowledged_residual_risk_ids": residuals,
        "operator_review_state": operator_review_state,
        "production_activation_authorized": production_activation_authorized,
        "readiness_state": readiness_state,
        "risk_014_status": risk_014_status,
        "notes": notes,
        "constraints_honored": [
            "No production activation from this decision",
            "Threat model remains Partial (not Verified pen-test quality)",
            "Fail-closed authority locks remain binding",
            "Neon Genie remains non-control-plane",
        ],
        "linked_artifacts": [
            str(REQUEST_REL).replace("\\", "/"),
            str(MODEL_REL).replace("\\", "/"),
            "out/production_readiness/ws8/notion_readiness_mapping.v1.json",
            "out/production_readiness/CONTINUATION_PLAN.v4.md",
            "https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/971",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(
            out_dir / "threat_model_operator_decision_record.v0.json",
            record,
        )

    return record
