"""WP-A: classify sole-writer advisory findings into debt classes.

Does not modify production write behavior. Emits a triage report under
out/production_readiness/ws2/ (architecture / debt track; continues WS1.7).
"""

from __future__ import annotations

import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json
from core.production_readiness.sole_writer_check import build_sole_writer_report

PRODUCER = "run_writer_debt_triage"
OUT_DIR_REL = Path("out/production_readiness/ws2")

# Path/pattern → debt class (first match wins)
CLASS_RULES: list[tuple[str, re.Pattern[str]]] = [
    (
        "RUNTIME_PACKET_WRITER",
        re.compile(
            r"core/(brier|canary|canary_promotion|canary_scheduler|drift|"
            r"external_action_proposals|ingest|lineage|observability)/"
            r".*runtime\.py$"
        ),
    ),
    (
        "ORACLE_EXECUTION_WRITER",
        re.compile(r"core/abraxas_oracle_.*\.py$"),
    ),
    (
        "SKILL_OUT_WRITER",
        re.compile(r"^skills/"),
    ),
    (
        "ABX_AFE_WRITER",
        re.compile(r"^abx-afe/"),
    ),
    (
        "SCRIPT_NON_RUN_WRITER",
        re.compile(r"^scripts/(?!run_)"),
    ),
    (
        "CORE_BUILDER_OR_HELPER",
        re.compile(r"^core/"),
    ),
    (
        "OTHER",
        re.compile(r"."),
    ),
]

# Recommended disposition per class (documentation only)
DISPOSITION: dict[str, dict[str, str]] = {
    "RUNTIME_PACKET_WRITER": {
        "disposition": "CONSOLIDATE",
        "action": (
            "Migrate to scripts/<domain>/run_*.py sole-writer calling pure builders; "
            "or explicit allow-list with owner if runtime must publish."
        ),
        "priority": "P0",
    },
    "ORACLE_EXECUTION_WRITER": {
        "disposition": "CONSOLIDATE",
        "action": "Route oracle execution artifacts through authorized runners only.",
        "priority": "P0",
    },
    "SKILL_OUT_WRITER": {
        "disposition": "ALLOWLIST_OR_ISOLATE",
        "action": (
            "Skills writing out/audit must be allow-listed as advisory skill surfaces "
            "or write only under skill-local paths."
        ),
        "priority": "P1",
    },
    "ABX_AFE_WRITER": {
        "disposition": "BOUNDARY",
        "action": "Treat abx-afe as adapter boundary; no direct kernel governance writes.",
        "priority": "P1",
    },
    "SCRIPT_NON_RUN_WRITER": {
        "disposition": "RENAME_OR_ALLOWLIST",
        "action": "Prefer scripts/<domain>/run_*.py naming or add to WRITER_ALLOWLIST with reason.",
        "priority": "P1",
    },
    "CORE_BUILDER_OR_HELPER": {
        "disposition": "CONSOLIDATE",
        "action": "Builders should return dicts; runners write via canonical_json.",
        "priority": "P0",
    },
    "OTHER": {
        "disposition": "REVIEW",
        "action": "Manual classification required.",
        "priority": "P2",
    },
}


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


def classify_path(rel_path: str) -> str:
    for name, pattern in CLASS_RULES:
        if pattern.search(rel_path):
            return name
    return "OTHER"


def build_writer_debt_triage(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    sole = build_sole_writer_report(repo_root, write=False, max_findings=10_000)
    raw_findings = sole.get("findings", [])
    # Re-scan full set: sole report may be capped — use finding list from uncapped by
    # calling build with high max (already 10000). If still truncated, note it.
    classified: list[dict[str, Any]] = []
    class_counts: Counter[str] = Counter()
    unique_paths: set[str] = set()

    for finding in raw_findings:
        path = finding.get("path", "")
        debt_class = classify_path(path)
        class_counts[debt_class] += 1
        unique_paths.add(path)
        classified.append(
            {
                "path": path,
                "package": finding.get("package"),
                "debt_class": debt_class,
                "detail": finding.get("detail"),
                "disposition": DISPOSITION[debt_class]["disposition"],
                "priority": DISPOSITION[debt_class]["priority"],
            }
        )

    by_class: list[dict[str, Any]] = []
    for name, count in class_counts.most_common():
        sample = [c for c in classified if c["debt_class"] == name][:8]
        by_class.append(
            {
                "debt_class": name,
                "finding_count": count,
                "unique_paths": len({c["path"] for c in classified if c["debt_class"] == name}),
                "disposition": DISPOSITION[name]["disposition"],
                "recommended_action": DISPOSITION[name]["action"],
                "priority": DISPOSITION[name]["priority"],
                "sample_findings": sample,
            }
        )

    report: dict[str, Any] = {
        "schema_version": "writer_debt_triage.v1",
        "artifact_type": "writer_debt_triage",
        "work_package": "WP-A_WRITER_DEBT_TRIAGE",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "PARTIAL",
        "source": {
            "sole_writer_finding_count": sole.get("finding_count"),
            "sole_writer_truncated": sole.get("truncated"),
            "sole_writer_by_package": sole.get("by_package"),
        },
        "summary": {
            "classified_finding_count": len(classified),
            "unique_paths": len(unique_paths),
            "by_debt_class": {k: v for k, v in class_counts.most_common()},
            "fail_closed_ready": False,
        },
        "classes": by_class,
        "consolidation_decisions": [
            {
                "decision_id": "CD-001",
                "subject": "core/*/runtime.py packet publishers",
                "decision": "CONSOLIDATE_TO_RUNNERS",
                "rationale": (
                    "ARCHITECTURE.md requires runners to write out/; runtime modules "
                    "that call write_canonical_json directly create parallel write paths."
                ),
                "status": "DOCUMENTED_NOT_IMPLEMENTED",
            },
            {
                "decision_id": "CD-002",
                "subject": "skills/** out/audit writers",
                "decision": "ALLOWLIST_ADVISORY_SKILL_SURFACE",
                "rationale": (
                    "Skills are advisory; writes to out/audit must stay non-governance "
                    "and explicitly allow-listed before any fail-closed gate."
                ),
                "status": "DOCUMENTED_NOT_IMPLEMENTED",
            },
            {
                "decision_id": "CD-003",
                "subject": "abx-afe writers",
                "decision": "ADAPTER_BOUNDARY",
                "rationale": "Keep adapter-local; do not grant kernel control-plane writes.",
                "status": "DOCUMENTED_NOT_IMPLEMENTED",
            },
        ],
        "next_actions": [
            "WP-D batch 1: pick one runtime family (e.g. core/brier/runtime.py) and move write to scripts/run_*.py",
            "Do not enable sole-writer fail-closed until RUNTIME_PACKET_WRITER count is near zero or allow-listed",
            "WP-B Validation Service remains independent of this triage",
        ],
        "notes": [
            "Triage is classification evidence only — no production behavior change.",
            "Linked continuation plan: out/production_readiness/CONTINUATION_PLAN.v1.md",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "writer_debt_triage.v1.json", report)

    return report
