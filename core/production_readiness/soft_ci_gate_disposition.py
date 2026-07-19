"""WP-N2: soft CI gate disposition receipt (no fail-closed promotion)."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_soft_ci_gate_disposition"
OUT_DIR_REL = Path("out/production_readiness/ws6")


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


def build_soft_ci_gate_disposition(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    """Record N2 dispositions: keep soft gates; no fail-closed without operator."""
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    dispositions = [
        {
            "finding_path": ".github/workflows/ci.yml",
            "step": "Rune integrity scanner (report-only)",
            "decision": "KEEP_REPORT_ONLY",
            "rationale": "Historical scanner; not a production P0 gate for this track.",
        },
        {
            "finding_path": ".github/workflows/ci.yml",
            "step": "P64 manifest source hash gate",
            "decision": "KEEP_UNTIL_OPERATOR_RESEAL",
            "rationale": "Documented historical drift; reseal is separate operator work.",
        },
        {
            "finding_path": ".github/workflows/status-pages.yml",
            "step": "Check deterministic output",
            "decision": "KEEP_SOFT_TRACKED",
            "rationale": (
                "REVIEW_HARDEN deferred: flakiness risk remains; not remediating by "
                "fail-closing in this slice."
            ),
        },
        {
            "finding_path": "scripts/run_fast_ci.py",
            "step": "ADVISORY_REPORT_ONLY_COMMANDS",
            "decision": "KEEP_REPORT_ONLY",
            "rationale": (
                "Boundary/sole-writer/neon remain fail-open until sole-writer residual "
                "accepted and operator enables ABRAXAS_BOUNDARY_FAIL_CLOSED."
            ),
        },
    ]

    packet: dict[str, Any] = {
        "schema_version": "soft_ci_gate_disposition.v1",
        "artifact_type": "soft_ci_gate_disposition",
        "work_package": "WP-N2_SOFT_GATE_DISPOSITION",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "fail_closed_enabled": False,
        "dispositions": dispositions,
        "summary": {
            "disposition_count": len(dispositions),
            "fail_closed_promotions": 0,
            "kept_soft": len(dispositions),
        },
        "recommendations": [
            "Do not enable ABRAXAS_BOUNDARY_FAIL_CLOSED without operator approval",
            "Revisit status-pages deterministic soft gate after flakiness evidence review",
            "P64 reseal remains operator lane",
        ],
        "notes": [
            "N2 is disposition-only; no workflow fail-closed flips in this slice.",
            "Linked audit: out/production_readiness/ws6/soft_ci_gate_audit.v1.json",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "soft_ci_gate_disposition.v1.json", packet)

    return packet
