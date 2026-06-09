#!/usr/bin/env python3
"""
Script Organization Automation

Safely moves run_*.py scripts from scripts/ into logical subdirectories
based on filename prefixes.

Usage:
    python scripts/organize_scripts.py --dry-run     # Preview changes (default)
    python scripts/organize_scripts.py --execute     # Perform the moves

Features:
    - Dry-run mode by default
    - Idempotent (skips files already in target)
    - Clear error handling and reporting
    - Summary of successes / failures / skipped
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# Mapping of filename prefixes to target subdirectory
PREFIX_TO_DIR: Dict[str, str] = {
    "run_temporal_": "temporal",
    "run_governance_": "governance",
    "run_research_": "research",
    "run_research_canary_": "research",
    "run_artifact_": "artifact",
    "run_ingest_": "ingest",
    "run_oracle_": "ingest",
    "run_metric_": "metric",
    "run_rank": "metric",
    "run_operator_": "operator",
    "run_aal_viz_": "viz",
    "run_geometric_": "viz",
    "run_transport_": "transport",
    "run_wasserstein_": "transport",
}

ROOT = Path(__file__).parent
SCRIPTS_DIR = ROOT


def get_target_dir(filename: str) -> str | None:
    for prefix, target in PREFIX_TO_DIR.items():
        if filename.startswith(prefix):
            return target
    return None


def organize(dry_run: bool = True) -> None:
    moved: List[Tuple[str, str]] = []
    skipped: List[str] = []
    errors: List[Tuple[str, str]] = []

    script_files = sorted(SCRIPTS_DIR.glob("run_*.py"))

    for file in script_files:
        if file.name == "organize_scripts.py":
            continue

        target_subdir = get_target_dir(file.name)
        if not target_subdir:
            skipped.append(file.name)
            continue

        target_dir = SCRIPTS_DIR / target_subdir
        target_path = target_dir / file.name

        if target_path.exists():
            skipped.append(f"{file.name} (already exists in {target_subdir}/)")
            continue

        if dry_run:
            moved.append((file.name, target_subdir))
            continue

        # --- Actual move with error handling ---
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), str(target_path))
            moved.append((file.name, target_subdir))
        except Exception as e:
            errors.append((file.name, str(e)))

    # --- Reporting ---
    print("\n" + "=" * 60)
    print("ABRAXAS SCRIPT REORGANIZATION")
    print("=" * 60)

    mode = "[DRY RUN]" if dry_run else "[EXECUTED]"
    print(f"\nMode: {mode}")

    if moved:
        print(f"\n✓ Successfully {'would move' if dry_run else 'moved'} ({len(moved)} files):")
        for name, target in moved:
            print(f"    {name}  →  scripts/{target}/")

    if skipped:
        print(f"\n▸ Skipped ({len(skipped)} files):")
        for s in skipped[:15]:
            print(f"    - {s}")
        if len(skipped) > 15:
            print(f"    ... and {len(skipped) - 15} more")

    if errors:
        print(f"\n✗ Errors ({len(errors)}):")
        for name, err in errors:
            print(f"    - {name}: {err}")

    print("\n" + "-" * 60)
    print(f"Summary: {len(moved)} moved | {len(skipped)} skipped | {len(errors)} errors")
    print("-" * 60 + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Organize Abraxas run_*.py scripts into logical subdirectories."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview changes without moving files (default)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform the file moves",
    )

    args = parser.parse_args()

    dry_run = not args.execute
    organize(dry_run=dry_run)
