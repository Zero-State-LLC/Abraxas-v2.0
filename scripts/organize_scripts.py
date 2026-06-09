#!/usr/bin/env python3
"""
Script Organization Automation

Safely moves run_*.py scripts from scripts/ into logical subdirectories
based on filename prefixes.

Features:
    - Structured JSON logging (machine readable)
    - Dry-run mode by default (safe)
    - Idempotent and error-resilient
    - Clear reporting with counts

Usage:
    python scripts/organize_scripts.py --dry-run
    python scripts/organize_scripts.py --execute
    python scripts/organize_scripts.py --execute --verbose
"""

import argparse
import json
import logging
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).parent
SCRIPTS_DIR = ROOT


class JsonFormatter(logging.Formatter):
    """Custom JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        # Add any extra fields passed via logger.info(..., extra={...})
        if hasattr(record, "extra_data"):
            log_record.update(record.extra_data)

        # Include exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record, ensure_ascii=False)


def setup_logging(verbose: bool = False) -> logging.Logger:
    logger = logging.getLogger("organize_scripts")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Remove existing handlers to avoid duplicate logs
    for handler in logger.handlers[:];
        logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)

    return logger


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


def get_target_dir(filename: str) -> str | None:
    for prefix, target in PREFIX_TO_DIR.items():
        if filename.startswith(prefix):
            return target
    return None


def organize(dry_run: bool = True, logger: logging.Logger | None = None) -> Dict[str, Any]:
    if logger is None:
        logger = logging.getLogger("organize_scripts")

    moved: List[Tuple[str, str]] = []
    skipped: List[str] = []
    errors: List[Tuple[str, str]] = []

    logger.info("Starting script reorganization", extra={"mode": "dry_run" if dry_run else "execute"})

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

        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), str(target_path))
            moved.append((file.name, target_subdir))
        except Exception as e:
            errors.append((file.name, str(e)))
            logger.error(f"Failed to move {file.name}", extra={"error": str(e)})

    # Final structured summary
    summary = {
        "moved_count": len(moved),
        "skipped_count": len(skipped),
        "error_count": len(errors),
        "mode": "dry_run" if dry_run else "execute",
        "moved": [{"file": name, "target": target} for name, target in moved],
        "skipped": skipped,
        "errors": [{"file": name, "error": err} for name, err in errors],
    }

    logger.info(
        "Reorganization complete",
        extra={
            "moved_count": len(moved),
            "skipped_count": len(skipped),
            "error_count": len(errors),
        },
    )

    return summary


def main() -> None:
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
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()
    dry_run = not args.execute

    logger = setup_logging(verbose=args.verbose)

    summary = organize(dry_run=dry_run, logger=logger)

    # Print final machine-readable JSON summary to stdout
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
