from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.generated_artifact_registry import (
    build_generated_artifact_registry,
    detect_ci_artifact_drift_paths,
    execute_artifact_regeneration,
    list_ci_drift_artifact_paths,
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
        dest="validation_only",
        help="Validate drift without regenerating artifacts; defaults to the full CI target set when no --artifact is provided.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        dest="validation_only",
        help="Validate drift without regenerating artifacts; defaults to the full CI target set when no --artifact is provided.",
    )
    parser.add_argument(
        "--print-ci-drift-paths",
        action="store_true",
        help="Print registry-declared deterministic CI drift paths.",
    )
    parser.add_argument(
        "--check-drift",
        action="store_true",
        help="Fail if deterministic CI drift paths differ from the tracked baseline.",
    )
    return parser.parse_args(argv)


def _resolve_selection(args: argparse.Namespace) -> tuple[bool, list[str] | None]:
    full = args.full or (args.validation_only and not args.artifact)
    selected_artifacts = args.artifact or None
    if not full and selected_artifacts is None:
        raise SystemExit("select --full or at least one --artifact target")
    return full, selected_artifacts


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    repo_root = Path(__file__).resolve().parent.parent.parent
    registry = build_generated_artifact_registry(repo_root)
    if args.print_ci_drift_paths:
        for artifact_path in list_ci_drift_artifact_paths(registry):
            print(artifact_path)
        return
    if args.check_drift:
        drift_paths = detect_ci_artifact_drift_paths(registry, repo_root=repo_root)
        if drift_paths:
            for artifact_path in drift_paths:
                print(artifact_path)
            raise SystemExit(1)
        return

    full, selected_artifacts = _resolve_selection(args)
    plan = execute_artifact_regeneration(
        registry,
        repo_root=repo_root,
        selected_artifacts=selected_artifacts,
        full=full,
        validation_only=args.validation_only,
    )
    write_artifact_regeneration_outputs(registry, plan, repo_root=repo_root)
    for status in plan.statuses:
        print(status.artifact_path)
    if plan.final_status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
