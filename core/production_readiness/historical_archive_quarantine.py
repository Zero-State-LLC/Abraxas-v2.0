"""TD Wave 3: RISK-004 historical archive quarantine inventory."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_historical_archive_quarantine"
OUT_DIR_REL = Path("out/production_readiness/ws2")

# High-signal archive / historical surfaces to track (not delete).
CANDIDATE_PATHS = [
    "out/archive",
    "docs/audits",
    "docs/releases",
    "README 2.md",
]


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


def build_historical_archive_quarantine(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    entries = []
    for rel in CANDIDATE_PATHS:
        path = repo_root / rel
        entries.append(
            {
                "path": rel,
                "exists": path.exists(),
                "disposition": "QUARANTINE_KEEP_HISTORICAL",
                "notes": "Do not delete; not authority for current readiness.",
            }
        )

    packet: dict[str, Any] = {
        "schema_version": "historical_archive_quarantine.v1",
        "artifact_type": "historical_archive_quarantine",
        "work_package": "TD_WAVE3_RISK004_QUARANTINE",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "risk_id": "RISK-004",
        "status": "MITIGATING",
        "entries": entries,
        "summary": {
            "paths_tracked": len(entries),
            "present": sum(1 for e in entries if e["exists"]),
        },
        "notes": [
            "Quarantine inventory only — no destructive cleanup.",
            "Closes OPEN gap by formal tracking; full purge out of scope.",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(
            out_dir / "historical_archive_quarantine.v1.json",
            packet,
        )

    return packet
