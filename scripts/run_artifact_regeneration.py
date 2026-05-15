from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.generated_artifact_registry import (
    build_generated_artifact_registry,
    execute_artifact_regeneration,
    write_artifact_regeneration_outputs,
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic generated artifact regeneration.")
    parser.add_argument(
        "--artifact",
        action="append",
        default=[],
        help="Selective artifact path to regenerate or validate. May be passed multiple times.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Regenerate or validate every managed generated artifact.",
    )
    parser.add_argument(
        "--validation-only",
        action="store_true",
        help="Validate drift without regenerating artifacts.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    if not args.full and not args.artifact:
        raise SystemExit("select --full or at least one --artifact target")

    repo_root = Path(__file__).resolve().parent.parent
    registry = build_generated_artifact_registry(repo_root)
    plan = execute_artifact_regeneration(
        registry,
        repo_root=repo_root,
        selected_artifacts=args.artifact or None,
        full=args.full,
        validation_only=args.validation_only,
    )
    write_artifact_regeneration_outputs(registry, plan, repo_root=repo_root)
    if plan.final_status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
