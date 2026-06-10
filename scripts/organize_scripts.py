#!/usr/bin/env python3
"""
Abraxas Script Organization Tool

Moves run_*.py scripts into logical subdirectories.

Structured JSON logging (stdout + optional .jsonl file) ready for ELK stack ingestion.

ELK Integration:
    - Logs are emitted as structured JSON (ideal for Filebeat/Logstash)
    - Use --log-file to write JSON Lines (.jsonl) for easy shipping to Elasticsearch
    - Recommended: Filebeat → Logstash → Elasticsearch → Kibana

Usage:
    python scripts/organize_scripts.py dry-run
    python scripts/organize_scripts.py execute --log-file logs/organization.jsonl
    python scripts/organize_scripts.py execute --verbose

Shell Completion:
    Bash:  source scripts/completions/organize_scripts.bash
    Zsh:   Add scripts/completions to your fpath and run compinit
    Fish:  Copy scripts/completions/organize_scripts.fish to ~/.config/fish/completions/
"""

import argparse
import json
import logging
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

ROOT = Path(__file__).parent


class StructuredJsonFormatter(logging.Formatter):
    """Compact structured JSON formatter."""

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "msg": record.getMessage(),
            "logger": record.name,
        }
        extra = getattr(record, "extra", {})
        if isinstance(extra, dict):
            payload.update(extra)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def get_logger(verbose: bool = False, log_file: Optional[Path] = None) -> logging.Logger:
    logger = logging.getLogger("abraxas.organize")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.propagate = False

    for h in logger.handlers[:]:
        logger.removeHandler(h)

    # Console handler (stdout)
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(StructuredJsonFormatter())
    logger.addHandler(console)

    # Optional file handler (JSON Lines - perfect for ELK/Filebeat)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setFormatter(StructuredJsonFormatter())
        logger.addHandler(file_handler)

    return logger


def _retry_operation(
    operation: Callable[[], Any],
    max_attempts: int = 3,
    delay: float = 0.5,
    logger: Optional[logging.Logger] = None,
    operation_name: str = "operation",
) -> Any:
    """Retry an operation with exponential backoff on transient errors."""
    last_exception = None
    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except (OSError, PermissionError, shutil.Error) as exc:
            last_exception = exc
            if logger:
                logger.warning(
                    f"{operation_name}.retry",
                    extra={
                        "attempt": attempt,
                        "max_attempts": max_attempts,
                        "error": str(exc)
                    },
                )
            if attempt < max_attempts:
                time.sleep(delay * attempt)  # Simple backoff
            else:
                raise
    raise last_exception


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


def run_organization(
    dry_run: bool = True,
    logger: Optional[logging.Logger] = None,
    log_file: Optional[Path] = None,
) -> Dict[str, Any]:
    if logger is None:
        logger = get_logger(log_file=log_file)

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

        dest_dir = (ROOT / target_dir).resolve()
        dest_path = dest_dir / path.name

        if dest_path.exists():
            skipped.append(path.name)
            continue

        if dry_run:
            moved.append({"file": path.name, "target": target_dir})
            continue

        # Defensive check for existing non-directory
        if dest_dir.exists() and not dest_dir.is_dir():
            errors.append({
                "file": path.name,
                "error": f"Target path exists but is not a directory: {dest_dir}"
            })
            logger.error(
                "directory.not_a_directory",
                extra={"file": path.name, "target_dir": str(dest_dir)}
            )
            continue

        def _create_dir():
            dest_dir.mkdir(parents=True, exist_ok=True)

        try:
            _retry_operation(
                _create_dir,
                max_attempts=3,
                delay=0.3,
                logger=logger,
                operation_name="directory.create"
            )
        except (OSError, PermissionError) as exc:
            errors.append({
                "file": path.name,
                "error": f"Failed to create directory {dest_dir} after retries: {exc}"
            })
            logger.error(
                "directory.create_failed_after_retries",
                extra={
                    "file": path.name,
                    "target_dir": str(dest_dir),
                    "error": str(exc)
                }
            )
            continue

        def _move_file():
            shutil.move(str(path), str(dest_path))

        try:
            _retry_operation(
                _move_file,
                max_attempts=3,
                delay=0.3,
                logger=logger,
                operation_name="file.move"
            )
            moved.append({"file": path.name, "target": target_dir})
            logger.debug("file.moved", extra={"file": path.name, "target": target_dir})
        except Exception as exc:
            errors.append({"file": path.name, "error": str(exc)})
            logger.error("file.move_failed_after_retries", extra={"file": path.name, "error": str(exc)})

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
    parser = argparse.ArgumentParser(
        description="Organize Abraxas runner scripts into subdirectories (ELK-ready logging)."
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Write structured JSON logs to this file (JSON Lines format, ideal for ELK/Filebeat)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="dry-run or execute")

    # dry-run subcommand
    dry_parser = subparsers.add_parser("dry-run", help="Preview moves without changing anything (default behavior)")

    # execute subcommand
    exec_parser = subparsers.add_parser("execute", help="Actually move the files")

    args = parser.parse_args()

    dry_run = args.command == "dry-run"

    logger = get_logger(verbose=args.verbose, log_file=args.log_file)

    try:
        result = run_organization(dry_run=dry_run, logger=logger, log_file=args.log_file)
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

    try:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as json_exc:
        print(json.dumps({"status": "failed", "error": str(json_exc)}))
        sys.exit(1)

    sys.exit(1 if result["error_count"] > 0 else 0)


if __name__ == "__main__":
    main()
