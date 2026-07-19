"""WP-O: recovery drill v0 — dry-run restore of critical readiness artifacts from git."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_recovery_drill_v0"
OUT_DIR_REL = Path("out/production_readiness/ws8")

# Critical readiness artifacts that must be restorable from git when tracked.
CRITICAL_PATHS = [
    "out/production_readiness/baseline/baseline_receipt.v1.json",
    "out/production_readiness/ws1/interface_registry_snapshot.v1.json",
    "out/production_readiness/ws3/service_registry.v1.json",
    "out/production_readiness/ws5/neon_genie_capability_allowlist.v1.json",
    "out/production_readiness/ws8/threat_model.v0.json",
    "out/production_readiness/ws8/notion_readiness_mapping.v1.json",
    "out/production_readiness/ws8/threat_model_operator_decision_request.v0.json",
    "out/production_readiness/ws8/threat_model_operator_decision_record.v0.json",
    "out/production_readiness/ws8/notion_writeback_receipt.v1.json",
    "out/production_readiness/CONTINUATION_PLAN.v4.md",
    "VERSION",
    "COMPATIBILITY.md",
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


def _git_ls_files(repo_root: Path, rel: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", rel],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def _git_show_head(repo_root: Path, rel: str) -> tuple[bool, str]:
    result = subprocess.run(
        ["git", "show", f"HEAD:{rel}"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return False, (result.stderr or result.stdout or "")[:200]
    return True, result.stdout[:80]


def build_recovery_drill_v0(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    """Dry-run: verify critical paths are tracked and restorable via git show HEAD:path.

    Does not modify the worktree (no git restore executed).
    """
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    checks: list[dict[str, Any]] = []
    for rel in CRITICAL_PATHS:
        exists = (repo_root / rel).exists()
        tracked = _git_ls_files(repo_root, rel) if exists or True else False
        restorable, preview = _git_show_head(repo_root, rel) if tracked else (False, "not_tracked")
        status = "PASS" if tracked and restorable else "FAIL"
        checks.append(
            {
                "path": rel,
                "worktree_exists": exists,
                "git_tracked": tracked,
                "git_show_head_ok": restorable,
                "status": status,
                "preview_prefix": preview.replace("\n", " ")[:60] if restorable else preview[:60],
            }
        )

    passed = sum(1 for c in checks if c["status"] == "PASS")
    failed = [c for c in checks if c["status"] == "FAIL"]

    drill: dict[str, Any] = {
        "schema_version": "recovery_drill.v0",
        "artifact_type": "recovery_drill",
        "work_package": "WP-O_RECOVERY_DRILL_V0",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial" if not failed else "Partial",
        "mode": "DRY_RUN_NO_WORKTREE_MUTATION",
        "summary": {
            "paths_checked": len(checks),
            "pass_count": passed,
            "fail_count": len(failed),
            "all_critical_restorable": len(failed) == 0,
        },
        "checks": checks,
        "restore_procedure": [
            "1. Identify missing/corrupt critical path under out/production_readiness/ or root doctrine files",
            "2. git restore --source=HEAD --worktree -- <path>",
            "3. Re-run scripts/run_production_readiness_baseline.py (optional) to refresh inventories",
            "4. Re-run scripts/run_fast_ci.py to confirm green",
            "5. Do not force-push; do not rewrite historical research_canary_* without operator approval",
        ],
        "rollback_notes": [
            "Recovery from git assumes artifacts are tracked (force-added despite out/**/*.json ignore).",
            "Untracked local-only artifacts are NOT_COMPUTABLE for git restore.",
        ],
        "notes": [
            "v0 is a dry-run presence/restorability check, not a full disaster-recovery exercise.",
            "Linked plan: out/production_readiness/CONTINUATION_PLAN.v3.md",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "recovery_drill.v0.json", drill)

    return drill
