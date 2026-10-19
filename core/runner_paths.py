"""Resolve sole-writer runner scripts across root and domain-organized layouts.

Runners live at ``scripts/run_<name>.py`` (root, CI entrypoints) or
``scripts/<domain>/run_<name>.py`` after scripts/organize_scripts.py moved them
into domain directories. This mirrors the layout scanned by
core/production_readiness/baseline_generator.py::_iter_run_scripts.
"""

from __future__ import annotations

from pathlib import Path

NOT_COMPUTABLE = "NOT_COMPUTABLE"

_SKIP_DOMAIN_DIRS = frozenset({"__pycache__", "common", "completions", "design"})


def resolve_runner_script(root: Path, stem: str) -> str:
    """Return the repo-relative path of ``run_<stem>.py`` or ``NOT_COMPUTABLE``.

    The root location wins; otherwise exactly one domain directory must hold the
    runner. Zero or ambiguous (multiple) matches are not computable.
    """
    if not stem:
        return NOT_COMPUTABLE
    file_name = f"run_{stem}.py"
    scripts_dir = root / "scripts"
    if (scripts_dir / file_name).is_file():
        return f"scripts/{file_name}"
    if not scripts_dir.is_dir():
        return NOT_COMPUTABLE
    matches = sorted(
        f"scripts/{child.name}/{file_name}"
        for child in scripts_dir.iterdir()
        if child.is_dir()
        and child.name not in _SKIP_DOMAIN_DIRS
        and not child.name.startswith(".")
        and (child / file_name).is_file()
    )
    return matches[0] if len(matches) == 1 else NOT_COMPUTABLE
