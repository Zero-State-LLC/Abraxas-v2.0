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
    python scripts/organize_scripts.py status
    python scripts/organize_scripts.py cleanup

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

    # Keep stdout reserved for machine-readable command output.
    console = logging.StreamHandler(sys.stderr)
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
                time.sleep(delay * attempt)
            else:
                raise
    raise last_exception


# Domain destinations for prefix-matched runners.
# NOTE: do not add scripts/operator/__init__.py — when scripts/ is on
# sys.path (e.g. `python scripts/run_*.py`), that package name shadows the
# stdlib `operator` module and breaks argparse/re/enum. Namespace package
# (directory only) is intentional so `import scripts.operator.run_*` works.
# Prefer longest-prefix match (see resolve_target_dir).
PREFIX_MAP: Dict[str, str] = {
    # Wave 1
    "run_temporal_": "temporal",
    "run_governance_": "governance",
    "run_research_canary_": "research",
    "run_research_": "research",
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
    # Wave 2 — large remaining clusters
    "run_v2_hygiene_": "hygiene",
    "run_v2_": "hygiene",
    "run_abx_codegen_": "codegen",
    "run_abx_": "codegen",
    "run_abraxas_": "codegen",
    "run_chamfer_": "geometry",
    "run_geodesic_": "geometry",
    "run_norm_": "geometry",
    "run_overlay_": "viz",
    "run_runtime_": "runtime",
    "run_continuity_": "temporal",
    "run_notion_": "notion",
    "run_canary_": "research",
    "run_live_": "viz",
    "run_rune_": "operator",
    "run_yggdrasil_": "operator",
    "run_belief_": "belief",
    "run_hyperstition_": "belief",
    "run_production_": "readiness",
    "run_threat_": "readiness",
    "run_sole_": "readiness",
    "run_soft_": "readiness",
    "run_boundary_": "readiness",
    "run_campaign_": "campaign",
    "run_proposal_": "governance",
    # Wave 3 — residual long-tail root runners
    "run_brier_": "belief",
    "run_grok_": "codegen",
    "run_unattended_abx_": "codegen",
    "run_manual_": "operator",
    "run_human_": "operator",
    "run_coherence_field_": "operator",
    "run_fifth_operator_": "metric",
    "run_four_operator_": "metric",
    "run_fourth_operator_": "metric",
    "run_three_operator_": "metric",
    "run_five_operator_": "metric",
    "run_review_": "governance",
    "run_implementation_authorization_": "governance",
    "run_doctrine_": "governance",
    "run_motif_governance_": "governance",
    "run_pr_644_": "governance",
    "run_fusion_": "viz",
    "run_projection_": "viz",
    "run_priority2_": "viz",
    "run_viz01_": "viz",
    "run_pressure_motif_": "viz",
    "run_p64_": "viz",
    "run_forecast_": "research",
    "run_shadow_": "research",
    "run_sandbox_": "research",
    "run_drift_": "research",
    "run_graph_replay": "research",
    "run_incremental_replay": "research",
    "run_adaptive_sandbox": "research",
    "run_noctis_": "research",
    "run_weight_drift_": "research",
    "run_multi_run_": "research",
    "run_mutation_pressure_": "research",
    "run_replay_": "research",
    "run_external_": "campaign",
    "run_v3_structural_campaign": "campaign",
    "run_canon_": "readiness",
    "run_subsystem_": "readiness",
    "run_stabilization_": "readiness",
    "run_candidate_": "readiness",
    "run_freeze_": "readiness",
    "run_recovery_": "readiness",
    "run_release_": "readiness",
    "run_residual_": "readiness",
    "run_service_": "readiness",
    "run_supported_": "readiness",
    "run_writer_": "readiness",
    "run_wp_d_": "readiness",
    "run_interface_": "readiness",
    "run_package_writer_": "readiness",
    "run_historical_": "readiness",
    "run_neon_genie_": "readiness",
    "run_repo_": "readiness",
    "run_docs_": "readiness",
    "run_documentation_": "readiness",
    "run_continuation_": "readiness",
    "run_registry": "readiness",
    "run_receipt": "readiness",
    "run_heavy_": "geometry",
    "run_global_ingest_": "ingest",
    "run_intake_replay": "ingest",
    "run_phase13_": "notion",
    "run_sync_snapshot": "notion",
    "run_state_": "runtime",
    "run_observability_": "runtime",
    "run_validation_service": "runtime",
    "run_milestone_": "temporal",
    "run_lineage_": "temporal",
    "run_p102g_": "temporal",
    "run_cross_run_": "temporal",
    "run_read_only_transport": "transport",
}

# Never place an __init__.py under these domain dirs (stdlib name collision when
# scripts/ is on sys.path). Currently only operator.
NO_INIT_DOMAINS = frozenset({"operator"})

# Intentionally remain at scripts/ root (CI entrypoints, operator-review queue).
ROOT_RUNNER_PREFIXES = (
    "run_operator_review_",
    "run_fast_ci",
)


def resolve_target_dir(name: str) -> Optional[str]:
    if name.startswith(ROOT_RUNNER_PREFIXES):
        return None
    # Longest prefix first so run_abx_codegen_ beats run_abx_, etc.
    for prefix, directory in sorted(PREFIX_MAP.items(), key=lambda kv: len(kv[0]), reverse=True):
        if name.startswith(prefix):
            return directory
    return None


def get_organization_status(logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """Return current organization status of run_*.py scripts."""
    if logger is None:
        logger = get_logger()

    try:
        all_scripts = sorted(ROOT.glob("run_*.py"))
    except OSError as exc:
        logger.error("status.scan_failed", extra={"error": str(exc)})
        return {
            "status": "error",
            "error": f"Failed to scan scripts directory: {exc}",
            "total_run_scripts": 0,
            "organized": 0,
            "unorganized": 0,
            "by_directory": {},
            "unorganized_files": []
        }

    organized = 0
    unorganized = 0
    by_directory: Dict[str, int] = {}
    unorganized_files: List[str] = []

    for path in all_scripts:
        if path.name == "organize_scripts.py":
            continue

        target_dir = resolve_target_dir(path.name)
        if target_dir is None:
            unorganized += 1
            unorganized_files.append(path.name)
            continue

        dest_dir = (ROOT / target_dir).resolve()
        dest_path = dest_dir / path.name

        if dest_path.exists():
            organized += 1
            by_directory[target_dir] = by_directory.get(target_dir, 0) + 1
        else:
            unorganized += 1
            unorganized_files.append(path.name)

    return {
        "status": "success",
        "total_run_scripts": len(all_scripts) - 1,
        "organized": organized,
        "unorganized": unorganized,
        "by_directory": by_directory,
        "unorganized_files": sorted(unorganized_files)
    }


def cleanup_duplicates(dry_run: bool = True, logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """Remove duplicate run_*.py scripts from root if they already exist in target subdirectories."""
    if logger is None:
        logger = get_logger()

    removed = []
    skipped = []
    errors = []

    logger.info("cleanup.started", extra={"dry_run": dry_run})

    try:
        scripts = sorted(ROOT.glob("run_*.py"))
    except OSError as exc:
        logger.error("cleanup.scan_failed", extra={"error": str(exc)})
        return {
            "status": "error",
            "error": str(exc),
            "removed_count": 0,
            "skipped_count": 0,
            "error_count": 1
        }

    for path in scripts:
        if path.name == "organize_scripts.py":
            continue

        target_dir = resolve_target_dir(path.name)
        if target_dir is None:
            skipped.append(path.name)
            continue

        dest_dir = (ROOT / target_dir).resolve()
        dest_path = dest_dir / path.name

        if not dest_path.exists():
            skipped.append(path.name)
            continue

        if dry_run:
            removed.append({"file": path.name, "target": str(dest_path)})
            continue

        try:
            path.unlink()
            removed.append({"file": path.name, "target": str(dest_path)})
            logger.info("cleanup.removed_duplicate", extra={"file": path.name, "target": str(dest_path)})
        except Exception as exc:
            errors.append({"file": path.name, "error": str(exc)})
            logger.error("cleanup.remove_failed", extra={"file": path.name, "error": str(exc)})

    status = "success" if not errors else ("partial" if removed else "failed")

    return {
        "status": status,
        "dry_run": dry_run,
        "removed_count": len(removed),
        "skipped_count": len(skipped),
        "error_count": len(errors),
        "removed": removed,
        "skipped": skipped,
        "errors": errors
    }


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

    subparsers = parser.add_subparsers(dest="command", required=True, help="dry-run, execute, status, or cleanup")

    subparsers.add_parser("dry-run", help="Preview moves without changing anything")
    subparsers.add_parser("execute", help="Actually move the files")
    subparsers.add_parser("status", help="Show current organization status")
    subparsers.add_parser("cleanup", help="Remove duplicate scripts from root if they exist in target directories")

    args = parser.parse_args()

    dry_run = args.command == "dry-run"
    logger = get_logger(verbose=args.verbose, log_file=args.log_file)

    if args.command == "status":
        try:
            status_result = get_organization_status(logger=logger)
            print(json.dumps(status_result, indent=2, ensure_ascii=False))
            sys.exit(0 if status_result.get("status") == "success" else 1)
        except Exception as exc:
            print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
            sys.exit(1)

    if args.command == "cleanup":
        try:
            cleanup_result = cleanup_duplicates(dry_run=dry_run, logger=logger)
            print(json.dumps(cleanup_result, indent=2, ensure_ascii=False))
            sys.exit(0 if cleanup_result.get("status") in ("success", "partial") else 1)
        except Exception as exc:
            print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
            sys.exit(1)

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
