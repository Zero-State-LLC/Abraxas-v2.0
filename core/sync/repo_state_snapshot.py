from __future__ import annotations

import subprocess
from pathlib import Path


from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

def _git(root: Path, *args: str) -> str:
    try:
        out = subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError):
        return NOT_COMPUTABLE
    return out.stdout.strip() or NOT_COMPUTABLE


def build_repo_state_snapshot(*, repo_root: str | Path = ".") -> dict[str, str]:
    root = Path(repo_root)
    return {
        "repo_commit": _git(root, "rev-parse", "HEAD"),
        "branch": _git(root, "rev-parse", "--abbrev-ref", "HEAD"),
    }
