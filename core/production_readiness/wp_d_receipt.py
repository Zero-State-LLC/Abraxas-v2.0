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
        # batch 3
        "core/overlay_risk/runtime.py",
        "core/overlay_containment/runtime.py",
        "core/overlay_readiness/runtime.py",
        "core/overlay_governance/runtime.py",
        "core/overlay_resolution/runtime.py",
        "core/overlay_topology/runtime.py",
        "core/manual_action_custody/runtime.py",
        "core/human_decision_ledger/runtime.py",
        # batch 4 / D4-C1
        "core/manual_execution/runtime.py",
        "core/manual_execution_receipts/runtime.py",
        # batch 4 / D4-C3
        "core/observability/aggregation.py",
        "core/proposal_sandbox_routing/runtime.py",
        "core/proposal_sandbox_evaluation/runtime.py",
        "core/overlay_firewall/runtime.py",
    ]
    clean = []
    for rel in modules:
        text = (repo_root / rel).read_text(encoding="utf-8")
        # Detect real use, not comments: import or call site.
        has_writer = (
            "from core.canonical.json import" in text
            and "write_canonical_json" in text
        ) or "write_canonical_json(" in text
        clean.append(
            {
                "path": rel,
                "write_canonical_json_present": has_writer,
            }
        )

    receipt: dict[str, Any] = {
        "schema_version": "wp_d_consolidation_receipt.v1",
        "artifact_type": "wp_d_consolidation_receipt",
        "work_package": "WP-D4_C1_MANUAL_EXECUTION_PURE_BUILDERS",
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
                "scripts/run_overlay_risk_envelope.py",
                "scripts/run_overlay_containment_policy.py",
                "scripts/run_overlay_readiness_index.py",
                "scripts/run_overlay_governance_ledger.py",
                "scripts/run_overlay_resolution_ledger.py",
                "scripts/run_overlay_topology_simulation.py",
                "scripts/run_manual_action_custody.py",
                "scripts/run_human_decision_ledger.py",
                "scripts/run_manual_execution_authorization.py",
                "scripts/run_manual_execution_receipt_ledger.py",
            ],
            "pattern": "core pure builders; scripts/run_* publish via write_canonical_json",
            "batches": ["batch1", "batch2", "batch3", "batch4_d4c1"],
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
            {
                "decision_id": "CD-001-BATCH3",
                "status": "IMPLEMENTED",
                "subject": "overlay_risk/containment/readiness/governance/resolution/topology + manual_action_custody + human_decision_ledger",
                "action": "Removed disk writes from core; sole-writer scripts publish",
            },
            {
                "decision_id": "CD-001-BATCH4-D4-C1",
                "status": "IMPLEMENTED",
                "subject": "manual_execution + manual_execution_receipts runtimes",
                "action": "Removed disk writes from core; sole-writer scripts publish",
            },
            {
                "decision_id": "CD-001-BATCH4-D4-C2",
                "status": "IMPLEMENTED",
                "subject": "core/ingest/scheduler + controlled_ingest_scheduler_governance_audit writers",
                "action": "Pure builders remain in core; sole-writers under scripts/ingest/",
            },
            {
                "decision_id": "CD-001-BATCH4-D4-C3",
                "status": "IMPLEMENTED",
                "subject": "observability aggregation + proposal_sandbox_routing/evaluation + overlay_firewall",
                "action": "Removed disk writes from core; sole-writer scripts publish",
            },
        ],
        "notes": [
            "Remaining RUNTIME_PACKET_WRITER findings may remain in other core modules.",
            "fail_closed sole-writer still not ready.",
            "Linked plan: out/production_readiness/CONTINUATION_PLAN.v9.md",
            "D4-C2 runners: scripts/ingest/run_ingest_scheduler.py, "
            "scripts/ingest/run_controlled_ingest_scheduler_governance_audit.py",
            "D4-C3 runners: run_observability_pipeline, run_proposal_sandbox_*, "
            "run_overlay_execution_firewall",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "wp_d_consolidation_receipt.v1.json", receipt)

    return receipt
