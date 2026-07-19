#!/usr/bin/env python3
"""Generate Workstream 0 production-readiness baseline package.

Usage:
  python scripts/readiness/run_production_readiness_baseline.py
  python scripts/readiness/run_production_readiness_baseline.py --with-fast-ci
  python scripts/readiness/run_production_readiness_baseline.py --validation-json path.json

Never fabricates CI outcomes. Without --with-fast-ci or --validation-json,
validation artifacts remain Partial / NOT_RUN.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SCRIPT_DIR_KEY = _SCRIPT_DIR.casefold()
sys.path = [
    path
    for path in sys.path
    if os.path.abspath(path or os.curdir).casefold() != _SCRIPT_DIR_KEY
]

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.production_readiness.baseline_generator import (  # noqa: E402
    BASELINE_DIR_REL,
    build_baseline_package,
)


def _run_fast_ci(repo_root: Path) -> dict:
    cmd = [sys.executable, str(repo_root / "scripts" / "run_fast_ci.py")]
    env = os.environ.copy()
    # run_fast_ci.py spawns bare `python` / `pyright` / `ruff` on PATH.
    # Prefer the active interpreter's bin dir so venv tools resolve.
    bindir = str(Path(sys.executable).resolve().parent)
    env["PATH"] = bindir + os.pathsep + env.get("PATH", "")
    started = time.time()
    proc = subprocess.run(
        cmd,
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
    )
    duration = round(time.time() - started, 3)
    stdout_lines = (proc.stdout or "").splitlines()
    stderr_lines = (proc.stderr or "").splitlines()
    return {
        "live_execution_performed": True,
        "command": " ".join(cmd),
        "exit_code": proc.returncode,
        "duration_seconds": duration,
        "stdout_tail": stdout_lines[-80:],
        "stderr_tail": stderr_lines[-40:],
        "environment": {
            "python": sys.version.split()[0],
            "cwd": str(repo_root),
        },
        "notes": [
            "Live execution of scripts/run_fast_ci.py by run_production_readiness_baseline",
            f"exit_code={proc.returncode}",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--with-fast-ci",
        action="store_true",
        help="Execute scripts/run_fast_ci.py and attach live validation receipt",
    )
    parser.add_argument(
        "--validation-json",
        type=Path,
        default=None,
        help="Path to a JSON validation payload from a prior live run",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build package in memory without writing artifacts",
    )
    args = parser.parse_args()

    validation = None
    if args.validation_json:
        validation = json.loads(args.validation_json.read_text(encoding="utf-8"))
    elif args.with_fast_ci:
        print("Running live fast CI...", flush=True)
        validation = _run_fast_ci(REPO_ROOT)
        print(
            f"fast CI finished exit_code={validation['exit_code']} "
            f"duration={validation['duration_seconds']}s",
            flush=True,
        )

    packages = build_baseline_package(
        REPO_ROOT,
        validation=validation,
        write=not args.dry_run,
    )

    out = REPO_ROOT / BASELINE_DIR_REL
    receipt = packages["baseline_receipt.v1.json"]
    print(
        json.dumps(
            {
                "status": receipt.get("status"),
                "evidence_state": receipt.get("evidence_state"),
                "repository_sha": receipt.get("repository_sha"),
                "artifact_count": len(packages),
                "output_dir": str(out) if not args.dry_run else None,
                "validation_exit_code": (validation or {}).get("exit_code"),
            },
            indent=2,
            sort_keys=True,
        )
    )
    # Generator success is independent of fast-CI exit code; CI result is evidence.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
