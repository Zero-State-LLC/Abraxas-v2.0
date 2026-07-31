"""Branch hygiene inventory — classify remote heads (read-only; no deletes)."""

from __future__ import annotations

import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash

SCHEMA_VERSION = "BranchHygieneInventory.v0"
DETERMINISTIC_TIMESTAMP = "branch_hygiene_inventory_v0_ts_0"
POLICY_DOC = "docs/status/BRANCH_HYGIENE_INVENTORY_001.md"

DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "remote_delete_authorized": False,
    "force_push_authorized": False,
}

PRODUCER = {
    "module": "core.engineering.branch_hygiene_inventory",
    "policy_doc": POLICY_DOC,
}

AGENT_PREFIXES = frozenset(
    {"codex", "copilot", "cursor", "replit", "loop", "nw", "geodesic", "wasserstein"}
)


def _prefix(name: str) -> str:
    if "/" in name:
        return name.split("/", 1)[0]
    if "-" in name:
        return name.split("-", 1)[0]
    return name


def _classify(name: str, open_pr_heads: set[str], default_branch: str) -> str:
    if name == default_branch or name in {"main", "master"}:
        return "KEEP"
    if name in open_pr_heads:
        return "OPEN_PR"
    pref = _prefix(name)
    if pref in AGENT_PREFIXES or name.startswith(("codex/", "copilot/", "cursor/")):
        return "CANDIDATE_STALE"
    if name.startswith(("feat/", "feature/", "docs/", "shadow/", "fix/")):
        return "REVIEW"
    return "UNKNOWN"


def _list_remote_heads(repo_root: Path, remote: str = "origin") -> list[str]:
    try:
        out = subprocess.check_output(
            ["git", "ls-remote", "--heads", remote],
            cwd=str(repo_root),
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return []
    names: list[str] = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        ref = parts[-1]
        if ref.startswith("refs/heads/"):
            names.append(ref[len("refs/heads/") :])
    return sorted(names)


def _list_open_pr_heads(repo_root: Path) -> list[str]:
    """Best-effort open PR head list via gh (optional)."""
    try:
        out = subprocess.check_output(
            [
                "gh",
                "pr",
                "list",
                "--state",
                "open",
                "--json",
                "headRefName",
                "--jq",
                ".[].headRefName",
            ],
            cwd=str(repo_root),
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return []
    return sorted({ln.strip() for ln in out.splitlines() if ln.strip()})


def build_branch_hygiene_inventory(
    *,
    repo_root: Path | None = None,
    remote: str = "origin",
    default_branch: str = "main",
    sample_limit: int = 40,
    branch_names: list[str] | None = None,
    open_pr_heads: list[str] | None = None,
) -> dict[str, Any]:
    """Classify remote heads. Pure when branch_names/open_pr_heads injected."""
    root = Path(repo_root or Path.cwd()).resolve()
    heads = (
        sorted(branch_names)
        if branch_names is not None
        else _list_remote_heads(root, remote=remote)
    )
    pr_heads = (
        sorted(open_pr_heads)
        if open_pr_heads is not None
        else _list_open_pr_heads(root)
    )
    pr_set = set(pr_heads)

    prefix_counts: Counter[str] = Counter()
    class_counts: Counter[str] = Counter()
    candidates: list[dict[str, str]] = []

    for name in heads:
        pref = _prefix(name)
        prefix_counts[pref] += 1
        cls = _classify(name, pr_set, default_branch)
        class_counts[cls] += 1
        if cls in {"CANDIDATE_STALE", "MERGED_SAFE"} and len(candidates) < sample_limit:
            candidates.append({"branch": name, "class": cls, "prefix": pref})

    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "inventory_id": "bhi_"
        + canonical_hash(
            {"heads": heads, "pr": pr_heads, "remote": remote}
        )[:16],
        "remote": remote,
        "default_branch": default_branch,
        "total_heads": len(heads),
        "prefix_counts": dict(sorted(prefix_counts.items(), key=lambda kv: (-kv[1], kv[0]))),
        "class_counts": dict(sorted(class_counts.items())),
        "candidates_sample": candidates,
        "open_pr_heads": pr_heads,
        "delete_authorized": False,
        "policy_doc": POLICY_DOC,
        "authority": dict(DEFAULT_AUTHORITY),
        "advisory_only": True,
        "producer": dict(PRODUCER),
        "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
        "note": (
            "Advisory inventory only. Operator must explicitly authorize any "
            "git push origin --delete. Never bulk-delete from automation."
        ),
    }
    body["canonical_hash"] = canonical_hash(body)
    return body
