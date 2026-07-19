"""WP-D4-prep: inventory next sole-writer consolidation targets (no rewrites)."""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_sole_writer_d4_target_inventory"
OUT_DIR_REL = Path("out/production_readiness/ws2")
REPORT_REL = Path("out/production_readiness/ws1/sole_writer_advisory_report.v1.json")


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git_sha(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"


def build_sole_writer_d4_target_inventory(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    report_path = repo_root / REPORT_REL
    findings: list[dict[str, Any]] = []
    finding_count = 0
    by_package: dict[str, Any] = {}
    if report_path.is_file():
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            report = {}
        findings = [f for f in (report.get("findings") or []) if isinstance(f, dict)]
        finding_count = int(report.get("finding_count") or len(findings))
        by_package = report.get("by_package") or {}

    path_counts: Counter[str] = Counter()
    package_counts: Counter[str] = Counter()
    for f in findings:
        path = str(f.get("path") or "")
        pkg = str(f.get("package") or "unknown")
        if path:
            path_counts[path] += 1
        package_counts[pkg] += 1

    # Ranked clusters for a future D4 implementation PR (not executed here).
    ranked_paths = [
        {
            "path": path,
            "finding_hits_in_sample": count,
            "recommended_action": (
                "Move writes to scripts/run_*; leave core pure builder"
                if path.startswith("core/") and "/runtime.py" in path
                else (
                    "Route skill writers through run_* or mark INTERNAL"
                    if path.startswith("skills/")
                    else "Triage / allow-list / quarantine"
                )
            ),
        }
        for path, count in path_counts.most_common(20)
    ]

    clusters = [
        {
            "cluster_id": "D4-C1",
            "name": "core manual_execution family",
            "paths": [
                p
                for p in path_counts
                if "manual_execution" in p or "manual_execution_receipts" in p
            ],
            "priority": "P1",
            "notes": "High hit runtime pair; good pure-builder candidates.",
        },
        {
            "cluster_id": "D4-C2",
            "name": "core ingest scheduler",
            "paths": [p for p in path_counts if "core/ingest" in p],
            "priority": "P1",
            "notes": "Scheduler writes; consolidate publication ownership.",
        },
        {
            "cluster_id": "D4-C3",
            "name": "observability / proposal sandbox",
            "paths": [
                p
                for p in path_counts
                if "observability" in p or "proposal_sandbox" in p
            ],
            "priority": "P2",
        },
        {
            "cluster_id": "D4-C4",
            "name": "skills out writers",
            "paths": [p for p in path_counts if p.startswith("skills/")],
            "priority": "P2",
            "notes": "Often advisory; deprioritize vs core.",
        },
        {
            "cluster_id": "D4-C5",
            "name": "abx-afe writers",
            "paths": [p for p in path_counts if p.startswith("abx-afe/")],
            "priority": "P3",
            "notes": "Separate package lane.",
        },
    ]

    inventory: dict[str, Any] = {
        "schema_version": "sole_writer_d4_target_inventory.v1",
        "artifact_type": "sole_writer_d4_target_inventory",
        "work_package": "WP-D4_PREP_TARGET_INVENTORY",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "source_report": REPORT_REL.as_posix(),
        "finding_count": finding_count,
        "by_package": by_package,
        "sample_finding_count": len(findings),
        "ranked_paths": ranked_paths,
        "clusters": clusters,
        "implementation_executed": False,
        "fail_closed_recommended": False,
        "notes": [
            "Inventory only — no modules rewritten in this WP.",
            "Do not fail-close sole-writer while CORE_BUILDER residual remains large.",
            "Linked plan: out/production_readiness/CONTINUATION_PLAN.v8.md",
        ],
        "next_pr_suggestion": (
            "Optional: implement D4-C1 manual_execution pure builders + run_* publishers"
        ),
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(
            out_dir / "sole_writer_d4_target_inventory.v1.json",
            inventory,
        )

    return inventory
