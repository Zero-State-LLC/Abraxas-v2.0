#!/usr/bin/env python3
"""Emit Production Convergence Phase 0–2 audit package under out/production_convergence/."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.production_convergence.phase0_2 import build_phase0_2_package


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Build package in memory only (no out/ writes).",
    )
    parser.add_argument(
        "--with-fast-ci",
        action="store_true",
        help="Embed live fast-CI result into baseline (slow).",
    )
    args = parser.parse_args(argv)
    result = build_phase0_2_package(
        REPO_ROOT,
        write=not args.no_write,
        run_validation=args.with_fast_ci,
    )
    summary = {
        "output_dir": result["output_dir"],
        "artifacts": result["artifacts"],
        "entrypoint_count": result["package"]["entrypoint_inventory.v1.json"]["summary"][
            "entry_count"
        ],
        "supported_interfaces": result["package"]["interface_inventory.v1.json"]["summary"][
            "supported_count"
        ],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
