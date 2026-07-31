"""Main-scope git cleanliness receipt (advisory).

Emits ``out/audit/main_cleanliness.latest.json`` for the Notion main-scope
engineering-quality audit. Pure git-state capture; no tests, no authority grant.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Callable

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "MainCleanlinessReceipt.v0"
DEFAULT_OUT_PATH = "out/audit/main_cleanliness.latest.json"
DEFAULT_COMPARE_REF = "origin/main"

AUTHORITY = {
    "execution_authority": False,
    "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False,
    "production_activation_allowed": False,
    "notion_writeback_allowed": False,
}


def _run_git(repo_root: Path, *args: str) -> tuple[int, str, str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def collect_git_state(
    repo_root: Path,
    *,
    compare_ref: str = DEFAULT_COMPARE_REF,
    runner: Callable[[Path, tuple[str, ...]], tuple[int, str, str]] | None = None,
) -> dict[str, Any]:
    """Collect git hygiene fields. ``runner`` is injectable for tests."""
    root = Path(repo_root).resolve()
    run = runner or (lambda r, a: _run_git(r, *a))

    def need(*args: str) -> str:
        code, out, err = run(root, args)
        if code != 0:
            raise RuntimeError(f"git {' '.join(args)} failed: {err or out or code}")
        return out

    commit_sha = need("rev-parse", "HEAD")
    branch = need("branch", "--show-current") or "DETACHED"
    code_ref, origin_sha, err_ref = run(root, ("rev-parse", compare_ref))
    if code_ref != 0:
        return {
            "collect_status": "NOT_COMPUTABLE",
            "collect_reason": f"missing_compare_ref:{compare_ref}:{err_ref or 'unknown'}",
            "commit_sha": commit_sha,
            "branch": branch,
            "compare_ref": compare_ref,
            "origin_main_sha": None,
            "ahead": None,
            "behind": None,
            "worktree_clean": None,
            "tracked_dirty": None,
            "untracked_present": None,
            "dirty_tracked_paths": [],
            "untracked_paths_sample": [],
        }

    code_cnt, counts, err_cnt = run(
        root, ("rev-list", "--left-right", "--count", f"HEAD...{compare_ref}")
    )
    if code_cnt != 0:
        ahead, behind = None, None
        count_error = err_cnt or counts
    else:
        parts = counts.split()
        ahead = int(parts[0]) if len(parts) >= 1 else None
        behind = int(parts[1]) if len(parts) >= 2 else None
        count_error = None

    code_st, porcelain, err_st = run(root, ("status", "--porcelain"))
    if code_st != 0:
        return {
            "collect_status": "NOT_COMPUTABLE",
            "collect_reason": f"git_status_failed:{err_st or porcelain}",
            "commit_sha": commit_sha,
            "branch": branch,
            "compare_ref": compare_ref,
            "origin_main_sha": origin_sha,
            "ahead": ahead,
            "behind": behind,
            "worktree_clean": None,
            "tracked_dirty": None,
            "untracked_present": None,
            "dirty_tracked_paths": [],
            "untracked_paths_sample": [],
            "count_error": count_error,
        }

    dirty_tracked: list[str] = []
    untracked: list[str] = []
    for line in porcelain.splitlines():
        if not line.strip():
            continue
        # porcelain v1: XY path
        status = line[:2] if len(line) >= 2 else "??"
        path = line[3:] if len(line) > 3 else line
        if status == "??":
            untracked.append(path)
        else:
            dirty_tracked.append(path)

    return {
        "collect_status": "OBSERVED",
        "collect_reason": None,
        "commit_sha": commit_sha,
        "branch": branch,
        "compare_ref": compare_ref,
        "origin_main_sha": origin_sha,
        "ahead": ahead,
        "behind": behind,
        "worktree_clean": len(dirty_tracked) == 0,
        "tracked_dirty": len(dirty_tracked) > 0,
        "untracked_present": len(untracked) > 0,
        "dirty_tracked_paths": dirty_tracked[:50],
        "untracked_paths_sample": untracked[:20],
        "count_error": count_error,
    }


def _derive_status(state: dict[str, Any]) -> tuple[str, list[str]]:
    if state.get("collect_status") != "OBSERVED":
        return "NOT_COMPUTABLE", [str(state.get("collect_reason") or "collect_failed")]
    blockers: list[str] = []
    if state.get("ahead") is None or state.get("behind") is None:
        blockers.append("ahead_behind_not_computable")
    else:
        if int(state["ahead"]) != 0:
            blockers.append(f"ahead={state['ahead']}")
        if int(state["behind"]) != 0:
            blockers.append(f"behind={state['behind']}")
    if state.get("tracked_dirty"):
        blockers.append("tracked_worktree_dirty")
    if blockers:
        return "FAIL", blockers
    return "PASS", []


def build_main_cleanliness_receipt(
    *,
    repo_root: str | Path = ".",
    compare_ref: str = DEFAULT_COMPARE_REF,
    git_state: dict[str, Any] | None = None,
    runner: Callable[[Path, tuple[str, ...]], tuple[int, str, str]] | None = None,
) -> dict[str, Any]:
    """Build MainCleanlinessReceipt.v0 for a single repo SHA."""
    root = Path(repo_root).resolve()
    state = git_state or collect_git_state(
        root, compare_ref=compare_ref, runner=runner
    )
    status, blockers = _derive_status(state)
    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "commit_sha": state.get("commit_sha"),
        "origin_main_sha": state.get("origin_main_sha"),
        "branch": state.get("branch"),
        "compare_ref": state.get("compare_ref", compare_ref),
        "ahead": state.get("ahead"),
        "behind": state.get("behind"),
        "worktree_clean": state.get("worktree_clean"),
        "tracked_dirty": state.get("tracked_dirty"),
        "untracked_present": state.get("untracked_present"),
        "dirty_tracked_paths": list(state.get("dirty_tracked_paths") or []),
        "untracked_paths_sample": list(state.get("untracked_paths_sample") or []),
        "blockers": blockers,
        "collect_status": state.get("collect_status"),
        "authority": dict(AUTHORITY),
        "advisory_only": True,
        "projection_only": True,
        "lane": "SHADOW",
        "producer": {
            "module": "core.audit.main_cleanliness_receipt",
            "purpose": "notion_main_scope_engineering_quality_audit",
        },
    }
    body["canonical_hash"] = canonical_hash(body)
    return body


def write_main_cleanliness_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
