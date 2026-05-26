from __future__ import annotations

import subprocess
import sys

COMMANDS: list[list[str]] = [
    ["python", "scripts/run_artifact_regeneration.py", "--check-drift"],
    [
        "python",
        "-m",
        "pytest",
        "-q",
        "-m",
        "not slow and not integration and not canon and not artifact",
    ],
    ["python", "-m", "ruff", "check", "."],
    ["pyright"],
]


def _preflight_check() -> int:
    try:
        import jsonschema  # noqa: F401
    except ModuleNotFoundError:
        print(
            "Missing test dependency: jsonschema. "
            "Install dev extras first: python -m pip install -e '.[dev]'",
            file=sys.stderr,
            flush=True,
        )
        return 1
    return 0


def main() -> int:
    preflight_status = _preflight_check()
    if preflight_status != 0:
        return preflight_status

    for command in COMMANDS:
        print("+", " ".join(command), flush=True)
        completed = subprocess.run(command, check=False)
        if completed.returncode != 0:
            return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
