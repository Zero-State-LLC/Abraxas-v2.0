#!/usr/bin/env python3
"""Emit the advisory stabilization-readiness foundation artifacts."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _director_module() -> Any:
    return importlib.import_module("skills.abx-stabilization-readiness.director")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-commit", required=True)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("out/audit/stabilization_readiness"),
    )
    args = parser.parse_args()
    artifacts = _director_module().emit_foundation_artifacts(
        args.output_root,
        baseline_commit=args.baseline_commit,
    )
    receipt = artifacts["stabilization_skill_foundation_receipt.latest.json"]
    print(json.dumps({"decision": receipt["decision"], "output": str(args.output_root)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
