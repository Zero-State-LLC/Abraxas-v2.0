"""WP-D consolidation receipt builder."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json
from core.production_readiness.sole_writer_check import build_sole_writer_report
from core.production_readiness.writer_debt_triage import build_writer_debt_triage

PRODUCER = "run_wp_d_consolidation_receipt"
OUT_DIR_REL = Path("out/production_readiness/ws2")


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


def build_wp_d_receipt(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)
    sole = build_sole_writer_report(repo_root, write=False, max_findings=10_000)
    triage = build_writer_debt_triage(repo_root, write=False)
    runtime_class = next(
        (
            c
            for c in triage.get("classes", [])
            if c.get("debt_class") == "RUNTIME_PACKET_WRITER"
        ),
        {"finding_count": 0},
    )

    modules = [
        # batch 1
        "core/brier/runtime.py",
        "core/canary/runtime.py",
        "core/drift/runtime.py",
        "core/canary_promotion/runtime.py",
        "core/canary_scheduler/runtime.py",
        # batch 2
        "core/forecast/runtime.py",
        "core/external_action_proposals/runtime.py",
        "core/overlay_observability/runtime.py",
        "core/oracle/runtime.py",
        "core/sandbox/runtime.py",
        "core/operator_queue/runtime.py",
        "core/state/runtime.py",
    ]
    clean = []
    for rel in modules:
        text = (repo_root / rel).read_text(encoding="utf-8")
        clean.append(
            {
                "path": rel,
                "write_canonical_json_present": "write_canonical_json" in text,
            }
        )

    receipt: dict[str, Any] = {
        "schema_version": "wp_d_consolidation_receipt.v1",
        "artifact_type": "wp_d_consolidation_receipt",
        "work_package": "WP-D_CORE_WRITER_CONSOLIDATION_BATCH1",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "PARTIAL",
        "batch": {
            "modules_migrated": modules,
            "module_checks": clean,
            "runners": [
                "scripts/run_brier_ledger.py",
                "scripts/run_canary_overlay.py",
                "scripts/run_weight_drift_simulation.py",
                "scripts/run_canary_promotion_review.py",
                "scripts/run_canary_policy_scheduler.py",
                "scripts/run_forecast_candidates.py",
                "scripts/run_external_action_proposals.py",
                "scripts/run_overlay_observability.py",
                "scripts/run_oracle_intake.py",
                "scripts/run_adaptive_sandbox.py",
                "scripts/run_operator_approval_queue.py",
                "scripts/run_state_engine.py",
            ],
            "pattern": "core pure builders; scripts/run_* publish via write_canonical_json",
            "batches": ["batch1", "batch2"],
        },
        "metrics": {
            "sole_writer_finding_count": sole.get("finding_count"),
            "runtime_packet_writer_findings": runtime_class.get("finding_count"),
            "modules_still_writing": sum(
                1 for m in clean if m["write_canonical_json_present"]
            ),
        },
        "decisions": [
            {
                "decision_id": "CD-001-BATCH1",
                "status": "IMPLEMENTED",
                "subject": "brier/canary/drift/canary_promotion/canary_scheduler runtimes",
                "action": "Removed disk writes from core; sole-writer scripts publish",
            },
            {
                "decision_id": "CD-001-BATCH2",
                "status": "IMPLEMENTED",
                "subject": "forecast/oracle/sandbox/state/operator_queue/external_action/overlay_observability",
                "action": "Removed disk writes from core; sole-writer scripts publish",
            },
        ],
        "notes": [
            "Remaining RUNTIME_PACKET_WRITER findings may remain in other core modules.",
            "fail_closed sole-writer still not ready.",
            "Linked plan: out/production_readiness/CONTINUATION_PLAN.v1.md",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "wp_d_consolidation_receipt.v1.json", receipt)

    return receipt
