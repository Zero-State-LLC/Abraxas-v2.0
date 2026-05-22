from __future__ import annotations

import subprocess

COMMANDS: list[list[str]] = [
    ["python", "scripts/run_artifact_regeneration.py", "--check-drift"],
    ["pytest", "-q", "-m", "not slow and not integration and not canon and not artifact"],
    ["ruff", "check", "."],
    ["pyright"],
]


def main() -> int:
    for command in COMMANDS:
        print("+", " ".join(command), flush=True)
        completed = subprocess.run(command, check=False)
        if completed.returncode != 0:
            return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
