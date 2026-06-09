#!/usr/bin/env python3
"""
Script Organization Automation

Safely moves run_*.py scripts from scripts/ into logical subdirectories
based on filename prefixes.

Features:
    - Structured JSON logging + final JSON summary
    - Robust error handling around JSON output
    - Dry-run mode by default
    - Proper exit codes

Usage:
    python scripts/organize_scripts.py --dry-run
    python scripts/organize_scripts.py --execute
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
    """Custom JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if hasattr(record, "extra_data"):
            log_record.update(getattr(record, "extra_data", {}))
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record, ensure_ascii=False)


def setup_logging(verbose: bool = False) -> logging.Logger:
    logger = logging.getLogger("organize_scripts")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    return logger


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

    logger.info("Starting reorganization", extra={"mode": "dry_run" if dry_run else "execute"})

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
            skipped.append(f"{file.name} (already in {target_subdir}/)")
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
            logger.error("Move failed", extra={"file": file.name, "error": str(e)})

    status = "success" if not errors else ("partial" if moved else "failed")

    summary = {
        "status": status,
        "mode": "dry_run" if dry_run else "execute",
        "moved_count": len(moved),
        "skipped_count": len(skipped),
        "error_count": len(errors),
        "moved": [{"file": n, "target": t} for n, t in moved],
        "skipped": skipped,
        "errors": [{"file": n, "error": e} for n, e in errors],
    }

    logger.info(
        "Reorganization finished",
        extra={
            "status": status,
            "moved_count": len(moved),
            "skipped_count": len(skipped),
            "error_count": len(errors),
        },
    )

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Organize Abraxas scripts into subdirectories.")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()
    dry_run = not args.execute

    logger = setup_logging(verbose=args.verbose)

    try:
        summary = organize(dry_run=dry_run, logger=logger)
    except Exception as e:
        # Fallback: always try to output valid JSON even on unexpected failure
        error_summary = {
            "status": "failed",
            "mode": "dry_run" if dry_run else "execute",
            "moved_count": 0,
            "skipped_count": 0,
            "error_count": 1,
            "errors": [{"file": "__internal__", "error": str(e)}],
            "moved": [],
            "skipped": [],
        }
        print(json.dumps(error_summary, indent=2, ensure_ascii=False))
        sys.exit(1)

    # Print final structured JSON summary
    try:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    except Exception as json_err:
        # Last-resort fallback if JSON serialization itself fails
        fallback = {
            "status": "failed",
            "error": f"JSON serialization failed: {json_err}",
            "original_status": summary.get("status", "unknown"),
        }
        print(json.dumps(fallback, indent=2, ensure_ascii=False))
        sys.exit(1)

    # Exit code based on result
    if summary["error_count"] > 0:
        sys.exit(1)
    elif summary["moved_count"] == 0 and summary["skipped_count"] > 0:
        sys.exit(0)  # Nothing to do is not a failure
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
