"""Disposable copy of the working tree for tests that run in-repo generators.

Some tests exercise generators whose output location is derived from the
script's own location (``Path(__file__).parents[n]``) or from the current
working directory. Running them against a mirror keeps the tracked ``out/``
and ``apps/`` files untouched while the generators still see the same inputs.
"""
from __future__ import annotations

import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

_IGNORED_NAMES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".hypothesis",
    ".benchmarks",
    ".codebase-memory",
    ".tmp",
}


def _ignore(directory: str, names: list[str]) -> set[str]:
    return {name for name in names if name in _IGNORED_NAMES}


def make_repo_mirror(destination: Path) -> Path:
    """Copy the working tree (minus VCS/env/cache dirs) to ``destination``/repo."""
    mirror = destination / "repo"
    shutil.copytree(REPO_ROOT, mirror, ignore=_ignore, symlinks=True)
    return mirror
