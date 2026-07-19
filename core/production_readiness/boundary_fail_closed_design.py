"""WP-E: boundary fail-closed design receipt (default remains advisory)."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_boundary_fail_closed_design"
OUT_DIR_REL = Path("out/production_readiness/ws2")


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


def build_boundary_fail_closed_design(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    doc: dict[str, Any] = {
        "schema_version": "boundary_fail_closed_design.v1",
        "artifact_type": "boundary_fail_closed_design",
        "work_package": "WP-E_BOUNDARY_FAIL_CLOSED_DESIGN",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "decision": "DESIGN_ONLY_DEFAULT_OFF",
        "scope": {
            "applies_to": "boundary_advisory_check only (imports + unregistered surfaces)",
            "does_not_apply_to": [
                "sole_writer_advisory_check",
                "rune integrity scanner",
                "historical continue-on-error gates",
            ],
        },
        "mechanism": {
            "env_var": "ABRAXAS_BOUNDARY_FAIL_CLOSED",
            "default": False,
            "enable_values": ["1", "true", "yes"],
            "cli_flag": "scripts/run_boundary_advisory_check.py --fail-closed",
            "fast_ci_behavior": "does_not_set_env; remains report-only",
        },
        "promotion_criteria": [
            "import allow-list stable for N consecutive green main CI days",
            "false-positive rate acceptable to operator",
            "explicit operator approval recorded",
            "sole-writer still advisory until separate threshold met",
        ],
        "rollback": [
            "Unset ABRAXAS_BOUNDARY_FAIL_CLOSED",
            "Revert any CI workflow change that sets the env (none in this WP)",
            "Boundary check returns to advisory exit 0",
        ],
        "notes": [
            "Enabling fail-closed in shared CI without approval is prohibited.",
            "Linked plan: out/production_readiness/CONTINUATION_PLAN.v2.md",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "boundary_fail_closed_design.v1.json", doc)

    return doc
