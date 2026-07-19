"""WP-D4-R: residual package disposition for skills / abx-afe / remaining core.

Classifies residual sole-writer findings without fail-closed promotion.
Skills and package CLIs are kept as intentional writers; core residual is debt.
"""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_residual_package_disposition"
OUT_DIR_REL = Path("out/production_readiness/ws2")
REPORT_REL = Path("out/production_readiness/ws1/sole_writer_advisory_report.v1.json")


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


def build_residual_package_disposition(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)
    report: dict[str, Any] = {}
    path = repo_root / REPORT_REL
    if path.is_file():
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            report = {}

    findings = [f for f in (report.get("findings") or []) if isinstance(f, dict)]
    by_package = report.get("by_package") or Counter(
        f.get("package") or "unknown" for f in findings
    )

    dispositions = [
        {
            "package": "skills",
            "disposition": "KEEP_SKILL_SURFACE_WRITERS",
            "rationale": (
                "Skill tools intentionally emit operator/audit packets under out/. "
                "Not core kernel sole-writer debt; leave until skill-lane rewrite."
            ),
            "fail_closed_candidate": False,
        },
        {
            "package": "abx-afe",
            "disposition": "KEEP_PACKAGE_CLI_WRITERS",
            "rationale": (
                "abx-afe scripts/CLI are a separate package lane with their own "
                "publication pattern (write_text). Not Abraxas core freeze blockers."
            ),
            "fail_closed_candidate": False,
        },
        {
            "package": "scripts",
            "disposition": "KEEP_SOLE_WRITER_RUNNERS",
            "rationale": "scripts/run_* are the intended sole writers.",
            "fail_closed_candidate": False,
        },
        {
            "package": "core",
            "disposition": "CONTINUE_PURE_BUILDER_DEBT_REDUCTION",
            "rationale": (
                "Remaining core findings after D4-C1..C4; production_readiness "
                "generators allowlisted. Residual is known debt under threshold."
            ),
            "fail_closed_candidate": False,
        },
    ]

    packet: dict[str, Any] = {
        "schema_version": "residual_package_disposition.v1",
        "artifact_type": "residual_package_disposition",
        "work_package": "WP-D4_R_RESIDUAL_PACKAGE_DISPOSITION",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "source_report": REPORT_REL.as_posix(),
        "finding_count": report.get("finding_count"),
        "by_package": dict(by_package),
        "dispositions": dispositions,
        "fail_closed_enabled": False,
        "production_activation_authorized": False,
        "notes": [
            "Disposition only — no skill/afe rewrites in this WP.",
            "Do not fail-close sole-writer while residual remains.",
            "Linked plan: out/production_readiness/CONTINUATION_PLAN.v9.md",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "residual_package_disposition.v1.json", packet)

    return packet
