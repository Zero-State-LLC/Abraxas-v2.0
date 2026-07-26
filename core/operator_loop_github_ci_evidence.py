"""Build operator-loop GitHub/CI evidence snapshots (projection-only).

Pure builders shape evidence without network. `gather_and_write` shells out
to `gh` only when invoked (inject `gh_runner` in tests). Authority locks
always false / none. No network on import.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_PR_CAP = 15
MAIN_BRANCH = "main"

# State buckets for gh pr checks / Actions conclusions.
_FAIL_STATES = frozenset(
    {"fail", "failure", "cancelled", "timed_out", "action_required", "error"}
)
_PENDING_STATES = frozenset({"pending", "in_progress", "queued"})
# skipping/skip/neutral count as pass (non-blocking green-ish).
_PASS_STATES = frozenset({"pass", "success", "skipping", "skip", "neutral"})

GhRunner = Callable[[list[str]], tuple[int, str, str]]


def utc_now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


_DEFAULT_GH_TIMEOUT_S = 120


def _default_gh_runner(argv: list[str]) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            check=False,
            timeout=_DEFAULT_GH_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        stderr = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        if not stderr:
            stderr = f"gh subprocess timed out after {_DEFAULT_GH_TIMEOUT_S}s"
        return 124, stdout, stderr
    return int(result.returncode), result.stdout or "", result.stderr or ""


def _repo_flag(resolved_repo: str | None) -> list[str]:
    """Return ``["-R", repo]`` when repo is a known owner/name; else empty."""
    if not resolved_repo or resolved_repo == "unknown":
        return []
    return ["-R", resolved_repo]


def _write_evidence_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _is_ci_workflow_run(run: dict[str, Any]) -> bool:
    """Keep runs whose workflow is `ci`, name is `fast-ci`, or display contains `ci`."""
    name = str(run.get("name") or "")
    workflow = str(run.get("workflowName") or run.get("workflow") or "")
    name_l = name.lower()
    workflow_l = workflow.lower()
    if workflow_l == "ci" or name_l == "fast-ci":
        return True
    return "ci" in name_l or "ci" in workflow_l


def gather_and_write(
    *,
    evidence_dir: Path,
    gh_runner: GhRunner | None = None,
    gh_on_path: bool | None = None,
    max_prs: int = DEFAULT_PR_CAP,
    now_iso: str | None = None,
    repo: str | None = None,
) -> dict[str, Path]:
    """Write github.v1.json and ci.v1.json. Never grants authority.

    gh_runner(argv) -> (returncode, stdout, stderr). If None, use subprocess.
    """
    evidence_dir = Path(evidence_dir)
    github_path = evidence_dir / "github.v1.json"
    ci_path = evidence_dir / "ci.v1.json"
    gathered_at = now_iso or utc_now_iso()
    on_path = shutil.which("gh") is not None if gh_on_path is None else bool(gh_on_path)

    if not on_path:
        note = "gh CLI not found on PATH"
        _write_evidence_json(
            github_path,
            not_computable_evidence(
                surface="github", notes=[note], gathered_at=gathered_at
            ),
        )
        _write_evidence_json(
            ci_path,
            not_computable_evidence(
                surface="ci", notes=[note], gathered_at=gathered_at
            ),
        )
        return {"github": github_path, "ci": ci_path}

    run = gh_runner or _default_gh_runner
    notes: list[str] = []
    ci_notes: list[str] = []

    resolved_repo = (repo or "").strip() or None
    if not resolved_repo:
        code, stdout, stderr = run(
            ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"]
        )
        if code == 0 and stdout.strip():
            resolved_repo = stdout.strip()
        else:
            notes.append(
                "failed to resolve repo via gh repo view: "
                + (stderr.strip() or f"exit {code}")
            )
            resolved_repo = "unknown"

    main_sha: str | None = None
    code, stdout, stderr = run(
        ["gh", "api", f"repos/{resolved_repo}/commits/{MAIN_BRANCH}", "--jq", ".sha"]
    )
    if code == 0 and stdout.strip():
        main_sha = stdout.strip()[:40]
    else:
        notes.append(
            f"gh api commits/{MAIN_BRANCH} failed: "
            + (stderr.strip() or f"exit {code}")
        )
        code_g, stdout_g, stderr_g = run(["git", "rev-parse", f"origin/{MAIN_BRANCH}"])
        if code_g == 0 and stdout_g.strip():
            main_sha = stdout_g.strip()[:40]
            notes.append(f"main tip from git rev-parse origin/{MAIN_BRANCH}")
        else:
            notes.append(
                f"git rev-parse origin/{MAIN_BRANCH} failed: "
                + (stderr_g.strip() or f"exit {code_g}")
            )

    repo_flag = _repo_flag(resolved_repo)

    open_prs: list[dict[str, Any]] = []
    pr_fields = "number,title,isDraft,mergeable,headRefName,baseRefName,url"
    code, stdout, stderr = run(
        [
            "gh",
            "pr",
            "list",
            *repo_flag,
            "--state",
            "open",
            "--limit",
            str(max_prs),
            "--json",
            pr_fields,
        ]
    )
    if code == 0:
        try:
            parsed = json.loads(stdout or "[]")
            if isinstance(parsed, list):
                open_prs = [p for p in parsed if isinstance(p, dict)]
            else:
                notes.append("gh pr list returned non-list JSON")
        except json.JSONDecodeError as exc:
            notes.append(f"gh pr list JSON parse error: {exc}")
    else:
        notes.append(
            "gh pr list failed: " + (stderr.strip() or f"exit {code}")
        )

    main_runs_raw: list[dict[str, Any]] = []
    run_fields = "name,conclusion,status,headSha,url,databaseId,workflowName"
    code, stdout, stderr = run(
        [
            "gh",
            "run",
            "list",
            *repo_flag,
            "--branch",
            MAIN_BRANCH,
            "--limit",
            "5",
            "--json",
            run_fields,
        ]
    )
    if code == 0:
        try:
            parsed = json.loads(stdout or "[]")
            if isinstance(parsed, list):
                main_runs_raw = [r for r in parsed if isinstance(r, dict)]
            else:
                ci_notes.append("gh run list returned non-list JSON")
        except json.JSONDecodeError as exc:
            ci_notes.append(f"gh run list JSON parse error: {exc}")
    else:
        ci_notes.append(
            "gh run list failed: " + (stderr.strip() or f"exit {code}")
        )

    main_runs = [r for r in main_runs_raw if _is_ci_workflow_run(r)]

    pr_check_summaries: list[dict[str, Any]] = []
    for pr in sorted(
        open_prs, key=lambda p: int(p.get("number") or 0), reverse=True
    )[:max_prs]:
        try:
            pr_number = int(pr["number"])
        except (KeyError, TypeError, ValueError):
            ci_notes.append("skipping PR without valid number")
            continue
        code, stdout, stderr = run(
            ["gh", "pr", "checks", *repo_flag, str(pr_number)]
        )
        if code not in (0, 1, 8):
            # gh pr checks often exits non-zero when any check fails; still parse stdout.
            # Keep going with whatever table we got.
            ci_notes.append(
                f"gh pr checks {pr_number} exit {code}: "
                + (stderr.strip() or "see stdout")
            )
        rows = parse_gh_pr_checks_table(stdout or "")
        summary = summarize_pr_checks(rows)
        summary["pr_number"] = pr_number
        pr_check_summaries.append(summary)

    github_payload = build_github_evidence(
        repo=resolved_repo,
        main_sha=main_sha,
        main_branch=MAIN_BRANCH,
        open_prs=open_prs,
        gathered_at=gathered_at,
        notes=notes,
        cap=max_prs,
    )
    ci_payload = build_ci_evidence(
        main_runs=main_runs,
        pr_check_summaries=pr_check_summaries,
        gathered_at=gathered_at,
        notes=ci_notes,
    )
    _write_evidence_json(github_path, github_payload)
    _write_evidence_json(ci_path, ci_payload)
    return {"github": github_path, "ci": ci_path}


def not_computable_evidence(
    *,
    surface: str,
    notes: list[str],
    gathered_at: str,
) -> dict[str, Any]:
    return {
        "status": "NOT_COMPUTABLE",
        "source": "none",
        "gathered_at": gathered_at,
        "items": [],
        "notes": list(notes),
        "surface": surface,
    }


def build_github_evidence(
    *,
    repo: str,
    main_sha: str | None,
    main_branch: str,
    open_prs: list[dict[str, Any]],
    gathered_at: str,
    notes: list[str] | None = None,
    cap: int = DEFAULT_PR_CAP,
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    if main_sha:
        items.append(
            {
                "kind": "git_tip",
                "sha": main_sha[:40],
                "branch": main_branch,
                "authority_implication": "none",
            }
        )
    # newest first: assume caller sorted; still re-sort by number desc
    sorted_prs = sorted(
        open_prs,
        key=lambda p: int(p.get("number") or 0),
        reverse=True,
    )[:cap]
    for pr in sorted_prs:
        mergeable_raw = pr.get("mergeable")
        if mergeable_raw is not None:
            mergeable = str(mergeable_raw or "UNKNOWN").upper()
        else:
            mergeable = "UNKNOWN"
        items.append(
            {
                "kind": "open_pr",
                "number": int(pr["number"]),
                "title": str(pr.get("title") or ""),
                "is_draft": bool(pr.get("isDraft", pr.get("is_draft", False))),
                "mergeable": mergeable,
                "head_branch": str(
                    pr.get("headRefName") or pr.get("head_branch") or ""
                ),
                "base_branch": str(
                    pr.get("baseRefName") or pr.get("base_branch") or "main"
                ),
                "url": str(pr.get("url") or ""),
                "authority_implication": "none",
            }
        )
    status = "PRESENT" if items else "NOT_COMPUTABLE"
    return {
        "status": status,
        "source": "gh_cli",
        "gathered_at": gathered_at,
        "repo": repo,
        "cap": cap,
        "items": items,
        "notes": list(notes or []),
    }


def parse_gh_pr_checks_table(text: str) -> list[dict[str, str]]:
    """Parse `gh pr checks` default tab-separated rows: name, state, ..."""
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            parts = line.split()
        if len(parts) < 2:
            continue
        rows.append({"name": parts[0], "state": parts[1].lower()})
    return rows


def summarize_pr_checks(check_rows: list[dict[str, str]]) -> dict[str, Any]:
    """Count check states; primary is fail > mixed > pending > pass.

    Fail dominates. Skipping/skip/neutral count as pass. Unknown states
    are treated as pending.
    """
    pass_n = fail_n = pending_n = 0
    for row in check_rows:
        state = (row.get("state") or "").lower()
        if state in _FAIL_STATES:
            fail_n += 1
        elif state in _PENDING_STATES:
            pending_n += 1
        elif state in _PASS_STATES:
            pass_n += 1
        else:
            pending_n += 1

    if fail_n > 0:
        primary = "fail"
    elif pending_n > 0 and pass_n > 0:
        primary = "mixed"
    elif pending_n > 0:
        primary = "pending"
    else:
        primary = "pass"

    return {
        "pass": pass_n,
        "fail": fail_n,
        "pending": pending_n,
        "primary": primary,
        "authority_implication": "none",
    }


def build_ci_evidence(
    *,
    main_runs: list[dict[str, Any]],
    pr_check_summaries: list[dict[str, Any]],
    gathered_at: str,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for run in main_runs:
        items.append(
            {
                "kind": "main_workflow",
                "workflow": str(run.get("name") or run.get("workflow") or "ci"),
                "conclusion": str(run.get("conclusion") or ""),
                "status": str(run.get("status") or ""),
                "head_sha": str(run.get("headSha") or run.get("head_sha") or "")[:40],
                "url": str(run.get("url") or ""),
                "authority_implication": "none",
            }
        )
    for summary in pr_check_summaries:
        items.append(
            {
                "kind": "pr_checks_summary",
                "pr_number": int(summary["pr_number"]),
                "pass": int(summary.get("pass") or 0),
                "fail": int(summary.get("fail") or 0),
                "pending": int(summary.get("pending") or 0),
                "primary": str(summary.get("primary") or "pending"),
                "authority_implication": "none",
            }
        )
    status = "PRESENT" if items else "NOT_COMPUTABLE"
    return {
        "status": status,
        "source": "gh_cli",
        "gathered_at": gathered_at,
        "items": items,
        "notes": list(notes or []),
    }
