#!/usr/bin/env python3
"""
Abraxas Script Organization Tool

Moves run_*.py scripts into logical subdirectories based on naming conventions.

Structured JSON logging + robust error handling + proper exit codes.

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
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).parent


class StructuredJsonFormatter(logging.Formatter):
    """Produces clean, structured JSON logs."""

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "msg": record.getMessage(),
            "logger": record.name,
        }

        # Merge any extra structured data
        extra = getattr(record, "extra", {})
        if isinstance(extra, dict):
            payload.update(extra)

        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def get_logger(verbose: bool = False) -> logging.Logger:
    logger = logging.getLogger("abraxas.organize")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.propagate = False

    # Clear existing handlers
    for h in logger.handlers[:]:
        logger.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredJsonFormatter())
    logger.addHandler(handler)
    return logger


# Prefix → target directory mapping
PREFIX_MAP: Dict[str, str] = {
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


def resolve_target_dir(name: str) -> Optional[str]:
    for prefix, directory in PREFIX_MAP.items():
        if name.startswith(prefix):
            return directory
    return None


def run_organization(dry_run: bool = True, logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    if logger is None:
        logger = get_logger()

    moved: List[Dict[str, str]] = []
    skipped: List[str] = []
    errors: List[Dict[str, str]] = []

    logger.info("organization.started", extra={"dry_run": dry_run})

    for path in sorted(ROOT.glob("run_*.py")):
        if path.name == "organize_scripts.py":
            continue

        target_dir = resolve_target_dir(path.name)
        if target_dir is None:
            skipped.append(path.name)
            continue

        dest_dir = ROOT / target_dir
        dest_path = dest_dir / path.name

        if dest_path.exists():
            skipped.append(path.name)
            continue

        if dry_run:
            moved.append({"file": path.name, "target": target_dir})
            continue

        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(dest_path))
            moved.append({"file": path.name, "target": target_dir})
            logger.debug("file.moved", extra={"file": path.name, "target": target_dir})
        except Exception as exc:
            errors.append({"file": path.name, "error": str(exc)})
            logger.error("file.move_failed", extra={"file": path.name, "error": str(exc)})

    status = "success" if not errors else ("partial" if moved else "failed")

    summary = {
        "status": status,
        "dry_run": dry_run,
        "moved_count": len(moved),
        "skipped_count": len(skipped),
        "error_count": len(errors),
        "moved": moved,
        "skipped": skipped,
        "errors": errors,
    }

    logger.info(
        "organization.completed",
        extra={
            "status": status,
            "moved_count": len(moved),
            "skipped_count": len(skipped),
            "error_count": len(errors),
        },
    )

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Organize Abraxas runner scripts into subdirectories.")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Preview only (default)")
    parser.add_argument("--execute", action="store_true", help="Perform the moves")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logs")

    args = parser.parse_args()
    dry_run = not args.execute

    logger = get_logger(verbose=args.verbose)

    try:
        result = run_organization(dry_run=dry_run, logger=logger)
    except Exception as exc:
        error_result = {
            "status": "failed",
            "dry_run": dry_run,
            "error": str(exc),
            "moved_count": 0,
            "skipped_count": 0,
            "error_count": 1,
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)

    # Always output final structured JSON summary
    try:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as json_exc:
        fallback = {"status": "failed", "error": f"JSON output failed: {json_exc}"}
        print(json.dumps(fallback, indent=2))
        sys.exit(1)

    # Exit code policy
    if result["error_count"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
