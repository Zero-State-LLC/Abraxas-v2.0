"""Local CI stopgap: run the CI commands on a clean commit and record the result.

Hosted GitHub Actions do not run for this private repository (no Actions
billing). Until they do, a pull request carries a *local verification record*:

    python -m scripts.governance.local_ci_record run      # on a clean checkout
    python -m scripts.governance.local_ci_record check    # is the newest record still valid?

``run`` refuses a dirty tree, runs each command, and writes
``docs/status/local-ci/<commit>.json`` with the tested commit, the
environment, the commands, their exit codes and result lines, and whether
tracked files changed during the run. The record names the commit it tested,
so it is committed *afterwards* in a separate docs commit; it never hashes
itself.

``check`` fails when the newest record is missing, failed, or older than a
change to anything other than documentation: code changes invalidate the
sign-off. A record is LOCAL_VERIFICATION evidence. It is never a GitHub
Actions result and must not be reported as one.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

RECORD_DIR = Path("docs/status/local-ci")
RECORD_SCHEMA = "LocalCIRecord.v1"
# Paths whose changes do not invalidate a sign-off (documentation only).
DOC_ONLY = re.compile(r"^(docs/|[^/]+\.md$)")
_SUMMARY = re.compile(r"(\d+ (passed|failed|skipped|deselected|errors?|xfailed|xpassed))")


def ci_commands(python: str) -> list[dict[str, object]]:
    return [
        {"name": "fast_ci", "argv": [python, "scripts/run_fast_ci.py"]},
        {
            "name": "full_pytest",
            "argv": [python, "-m", "pytest", "-p", "no:cacheprovider", "-o", "addopts=",
                     "-q", "--maxfail=100000", "tests"],
        },
    ]


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()


def _tracked_changes() -> list[str]:
    out = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        capture_output=True, text=True, check=True,
    ).stdout  # not stripped: porcelain lines start with a status column
    return sorted(line[3:] for line in out.splitlines() if line.strip())


def _environment(python: str) -> dict[str, str]:
    packages = subprocess.run(
        [python, "-m", "pip", "freeze", "--exclude-editable"], capture_output=True, text=True, check=False
    ).stdout
    return {
        "python": subprocess.run([python, "--version"], capture_output=True, text=True, check=False).stdout.strip(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "pip_freeze_sha256": hashlib.sha256(packages.encode()).hexdigest(),
    }


def run(python: str) -> int:
    if _tracked_changes():
        print("refusing: tracked files are modified; commit or stash first", file=sys.stderr)
        return 2
    commit = _git("rev-parse", "HEAD")
    results = []
    for command in ci_commands(python):
        started = time.monotonic()
        proc = subprocess.run(command["argv"], capture_output=True, text=True, check=False)
        output = proc.stdout + proc.stderr
        results.append(
            {
                "name": command["name"],
                "argv": [Path(a).name if a == python else a for a in command["argv"]],
                "exit_code": proc.returncode,
                "duration_seconds": round(time.monotonic() - started, 1),
                "summary": sorted({m[0] for m in _SUMMARY.findall(output)}),
                "failed_tests": sorted(set(re.findall(r"^FAILED (\S+)", output, re.MULTILINE))),
            }
        )
    changed = _tracked_changes()
    record = {
        "schema_version": RECORD_SCHEMA,
        "kind": "LOCAL_VERIFICATION",
        "not_github_actions": True,
        "tested_commit": commit,
        "recorded_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "environment": _environment(python),
        "commands": results,
        "tracked_files_changed_by_run": changed,
        "status": "PASS" if all(r["exit_code"] == 0 for r in results) and not changed else "FAIL",
    }
    RECORD_DIR.mkdir(parents=True, exist_ok=True)
    path = RECORD_DIR / f"{commit}.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"record": str(path), "status": record["status"]}))
    return 0 if record["status"] == "PASS" else 1


def check() -> int:
    records = sorted(RECORD_DIR.glob("*.json"), key=lambda p: json.loads(p.read_text())["recorded_at"])
    if not records:
        print("NO_LOCAL_CI_RECORD")
        return 1
    record = json.loads(records[-1].read_text())
    tested = record["tested_commit"]
    changed = _git("diff", "--name-only", f"{tested}..HEAD").splitlines()
    code_changes = [p for p in changed if not DOC_ONLY.match(p)]
    verdict = {
        "record": str(records[-1]),
        "tested_commit": tested,
        "record_status": record["status"],
        "code_changed_since": code_changes,
        "valid": record["status"] == "PASS" and not code_changes,
        "kind": record["kind"],
    }
    print(json.dumps(verdict, indent=2))
    return 0 if verdict["valid"] else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local CI record (stopgap; not GitHub Actions)")
    parser.add_argument("action", choices=["run", "check"])
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args(argv)
    return run(args.python) if args.action == "run" else check()


if __name__ == "__main__":
    sys.exit(main())
