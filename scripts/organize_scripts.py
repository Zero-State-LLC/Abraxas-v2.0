#!/usr/bin/env python3
"""
Script Organization Automation

Moves run_*.py scripts from scripts/ into logical subdirectories
based on filename prefixes.

Usage:
    python scripts/organize_scripts.py --dry-run     # Preview changes
    python scripts/organize_scripts.py --execute     # Perform the moves
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List

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
    moved: List[tuple] = []
    skipped: List[str] = []

    for file in sorted(SCRIPTS_DIR.glob("run_*.py")):
        if file.name == "organize_scripts.py":
            continue

        target_subdir = get_target_dir(file.name)
        if not target_subdir:
            skipped.append(file.name)
            continue

        target_dir = SCRIPTS_DIR / target_subdir
        target_path = target_dir / file.name

        if target_path.exists():
            skipped.append(f"{file.name} (already exists in target)")
            continue

        if dry_run:
            moved.append((file.name, target_subdir))
        else:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), str(target_path))
            moved.append((file.name, target_subdir))

    print("\n=== Script Reorganization ===")
    if dry_run:
        print("[DRY RUN] The following moves would be performed:\n")
    else:
        print("[EXECUTED] The following moves were performed:\n")

    for name, target in moved:
        print(f"  {name}  ->  scripts/{target}/")

    if skipped:
        print(f"\nSkipped {len(skipped)} files (no matching prefix or already moved):")
        for s in skipped[:20]:  # limit output
            print(f"  - {s}")
        if len(skipped) > 20:
            print(f"  ... and {len(skipped) - 20} more")

    print(f"\nTotal to move: {len(moved)}")
    print(f"Total skipped: {len(skipped)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Organize Abraxas run_*.py scripts into subdirectories.")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Preview changes without moving files")
    parser.add_argument("--execute", action="store_true", help="Actually perform the file moves")

    args = parser.parse_args()

    dry_run = not args.execute
    organize(dry_run=dry_run)
