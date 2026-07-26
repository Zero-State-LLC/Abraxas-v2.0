"""Build operator-loop GitHub/CI evidence snapshots (projection-only).

Pure helpers: no network, no gh subprocess. The gatherer script shells out
to gh and calls these builders. Authority locks always false / none.
"""

from __future__ import annotations

from typing import Any

DEFAULT_PR_CAP = 15

# State buckets for gh pr checks / Actions conclusions.
_FAIL_STATES = frozenset(
    {"fail", "failure", "cancelled", "timed_out", "action_required", "error"}
)
_PENDING_STATES = frozenset({"pending", "in_progress", "queued"})
# skipping/skip/neutral count as pass (non-blocking green-ish).
_PASS_STATES = frozenset({"pass", "success", "skipping", "skip", "neutral"})


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
