"""WP-Q: sole-writer residual acceptance for freeze evaluation.

Records a residual threshold and known-debt acceptance.
Does NOT enable fail-closed sole-writer enforcement.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_sole_writer_residual_acceptance"
OUT_DIR_REL = Path("out/production_readiness/ws1")
REPORT_REL = Path("out/production_readiness/ws1/sole_writer_advisory_report.v1.json")
TRIAGE_REL = Path("out/production_readiness/ws2/writer_debt_triage.v1.json")

# Advisory residual ceiling for known-debt acceptance on this track.
# Fail-closed remains forbidden while CORE_BUILDER_OR_HELPER dominates.
DEFAULT_THRESHOLD = {
    "max_finding_count": 100,
    "require_truncated_report": True,
    "fail_closed_allowed": False,
    "notes": (
        "Threshold is for residual acceptance bookkeeping only. "
        "Does not authorize fail-closed sole-writer CI."
    ),
}


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


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def build_sole_writer_residual_acceptance(
    repo_root: Path,
    *,
    operator_id_or_role: str,
    decision: str = "ACCEPT_KNOWN_RESIDUAL",
    notes: str = "",
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    """Build residual acceptance record against latest advisory report."""
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    allowed = {
        "ACCEPT_KNOWN_RESIDUAL",
        "REJECT_THRESHOLD_EXCEEDED",
        "DEFER",
    }
    if decision not in allowed:
        raise ValueError(f"decision must be one of {sorted(allowed)}")

    report = _load_json(repo_root / REPORT_REL) or {}
    triage = _load_json(repo_root / TRIAGE_REL) or {}
    finding_count = int(report.get("finding_count") or 0)
    truncated = bool(report.get("truncated"))
    by_package = report.get("by_package") or {}
    triage_summary = triage.get("summary") or {}
    by_class = triage_summary.get("by_debt_class") or {}

    under_threshold = finding_count <= DEFAULT_THRESHOLD["max_finding_count"]
    fail_closed_ready = bool(triage_summary.get("fail_closed_ready")) is True

    if decision == "ACCEPT_KNOWN_RESIDUAL" and not under_threshold:
        decision_effective = "REJECT_THRESHOLD_EXCEEDED"
        acceptance_status = "REJECTED"
    elif decision == "ACCEPT_KNOWN_RESIDUAL":
        decision_effective = decision
        acceptance_status = "ACCEPTED_KNOWN_RESIDUAL"
    elif decision == "REJECT_THRESHOLD_EXCEEDED":
        decision_effective = decision
        acceptance_status = "REJECTED"
    else:
        decision_effective = decision
        acceptance_status = "DEFERRED"

    packet: dict[str, Any] = {
        "schema_version": "sole_writer_residual_acceptance.v1",
        "artifact_type": "sole_writer_residual_acceptance",
        "work_package": "WP-Q_SOLE_WRITER_RESIDUAL_ACCEPTANCE",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "operator_id_or_role": operator_id_or_role,
        "decision": decision_effective,
        "acceptance_status": acceptance_status,
        "threshold": DEFAULT_THRESHOLD,
        "observed": {
            "finding_count": finding_count,
            "truncated": truncated,
            "by_package": by_package,
            "by_debt_class": by_class,
            "fail_closed_ready": fail_closed_ready,
            "source_report": str(REPORT_REL).replace("\\", "/"),
            "source_triage": str(TRIAGE_REL).replace("\\", "/"),
        },
        "under_threshold": under_threshold,
        "fail_closed_enabled": False,
        "production_activation_authorized": False,
        "gate_4_satisfied": acceptance_status == "ACCEPTED_KNOWN_RESIDUAL",
        "notes": notes
        or (
            "Residual sole-writer findings accepted as known debt for freeze "
            "evaluation only. Fail-closed sole-writer remains disabled."
        ),
        "constraints": [
            "Does not enable sole-writer fail-closed in CI",
            "Does not authorize production activation",
            "CORE_BUILDER_OR_HELPER residual remains debt, not silence",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(
            out_dir / "sole_writer_residual_acceptance.v1.json",
            packet,
        )

    return packet
