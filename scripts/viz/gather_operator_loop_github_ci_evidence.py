#!/usr/bin/env python3
"""Gather GitHub/CI evidence for operator-loop projection (explicit, offline-write).

Projection-only: writes github.v1.json and ci.v1.json under --evidence-dir.
Never assigns, approves, merges, or deploys. Exit 0 even when gh is missing
(fail-visible NOT_COMPUTABLE files).
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.operator_loop_github_ci_evidence import (
    DEFAULT_PR_CAP,
    gather_and_write,
)

DEFAULT_EVIDENCE_DIR = ROOT / "out" / "operator_loop" / "evidence"


def gh_available() -> bool:
    return shutil.which("gh") is not None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Gather GitHub/CI evidence for operator-loop status glance "
            "(projection-only; writes evidence files)"
        )
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=DEFAULT_EVIDENCE_DIR,
        help="Directory for github.v1.json and ci.v1.json",
    )
    parser.add_argument(
        "--max-prs",
        type=int,
        default=DEFAULT_PR_CAP,
        help=f"Cap open PRs (default {DEFAULT_PR_CAP})",
    )
    parser.add_argument(
        "--repo",
        type=str,
        default=None,
        help="owner/name; default: resolve via gh repo view",
    )
    args = parser.parse_args(argv)

    paths = gather_and_write(
        evidence_dir=args.evidence_dir,
        gh_on_path=gh_available(),
        max_prs=args.max_prs,
        repo=args.repo,
    )
    for key in ("github", "ci"):
        print(f"{key}: {paths[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
