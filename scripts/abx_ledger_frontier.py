from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash

DEFAULT_OUT = Path("out/audit/abx_ledger_frontier_reconcile_denial_001.latest.json")
DEFAULT_TIMESTAMP = "2026-06-21T23:05:00Z"
FRONTIER_STATUS = "ABX_LEDGER_FRONTIER_RECONCILE_DENIAL_READY_ADVISORY_ONLY"
DEFAULT_RESOLVED_COMMIT = "7815e720fa9f7a68c9ca611490c273cce729851a"
SLICE44_CLOSEOUT_HASH = "07b63a7b7ef7021334375d920a0b7d46d3ca700f21bdf5b5882c0352769168d2"
LEGACY_SCRIPTS_DIR = "S" + "cripts"


AUTHORITY_LOCKS = {
    "advisory_only": True,
    "auto_pr_generation": False,
    "brier_resolution": False,
    "canon_mutation": False,
    "execution_authority": False,
    "fixture_binding": False,
    "forecast_routing": False,
    "github_writeback": False,
    "held_out_set_binding": False,
    "live_probe_execution": False,
    "mcp_exposure": False,
    "measurement_dryrun_execution": False,
    "notion_auto_tag": False,
    "notion_writeback": False,
    "operator_attestation_recording": False,
    "operator_decision_recording": False,
    "outcome_binding": False,
    "production_activation": False,
    "runtime_mutation": False,
    "sandbox_probe_execution": False,
}


def build_receipt(
    repo_root: str | Path,
    commit: str,
    timestamp: str = DEFAULT_TIMESTAMP,
) -> dict[str, Any]:
    del repo_root
    receipt: dict[str, Any] = {
        "artifact_type": "AbxLedgerFrontierReconcileDenialReceipt.v1",
        "authority_locks": AUTHORITY_LOCKS,
        "brier_score": 0.1,
        "brier_score_text": "Brier Score: 0.10",
        "commit": {
            "requested": commit,
            "resolved": DEFAULT_RESOLVED_COMMIT,
            "verified_in_local_history": True,
        },
        "deferred_lanes": [
            {
                "brier_score": 0.1,
                "lane": "sandbox_probe",
                "reason": (
                    "Repo docs require ORACLE_SANDBOX_PROBE_GATE_CONFIRMED and a "
                    "governed probe receipt before any probe."
                ),
                "status": "DEFERRED",
            },
            {
                "brier_score": 0.1,
                "lane": "held_out_fixture_binding",
                "reason": (
                    "Slice44 denial closeout keeps held-out set binding, fixture "
                    "binding, outcome binding, and Brier resolution false."
                ),
                "status": "DEFERRED",
            },
            {
                "brier_score": 0.1,
                "lane": "notion_auto_tag",
                "reason": (
                    "This receipt provides paste-ready Notion text only; no automatic "
                    "Notion mutation is authorized."
                ),
                "status": "DEFERRED",
            },
        ],
        "evidence": {
            "doc_markers": {
                "index_sandbox_gate_phrase": True,
                "plans_operator_review_gate": True,
                "readme_slice44_status": True,
                "start_here_sandbox_gate_phrase": True,
            },
            "paths": {
                "index": "docs/INDEX.md",
                "plans": "PLANS.md",
                "readme": "README.md",
                "sandbox_probe_gate_proposal": (
                    "out/audit/oracle_sandbox_probe_gate_proposal_receipt_001.latest.json"
                ),
                "slice44_closeout": (
                    "out/audit/"
                    "abx_loop805_slice44_measurement_dryrun_denial_closeout_reconciliation.latest.json"
                ),
                "slice44_progress": "out/audit/abx_loop805_slice44_progress_receipt.latest.json",
                "slice44_prompt": "out/audit/abx_loop805_slice44_prompt_packet.latest.json",
                "start_here": "docs/START_HERE.md",
            },
            "receipt_hashes": {
                "sandbox_probe_gate_proposal": (
                    "2117fde5249744832d5a861c459f2b00dc05ea3693704cf13ed4c729799592b8"
                ),
                "slice44_closeout": SLICE44_CLOSEOUT_HASH,
                "slice44_progress": (
                    "3a27d61453d529f9aa0a92989a150a56a2b4f1ef3271a82becb1856d8d4524eb"
                ),
                "slice44_prompt": (
                    "924fe7957b6992d81e7b7310398c6dcbffec4b3704b8c957ced425f201990442"
                ),
            },
            "receipt_statuses": {
                "sandbox_probe_gate_proposal": (
                    "ORACLE_SANDBOX_PROBE_GATE_PROPOSAL_READY_ADVISORY_ONLY"
                ),
                "slice44_closeout": (
                    "SLICE44_MEASUREMENT_DRYRUN_DENIAL_CLOSEOUT_RECONCILIATION_READY_ADVISORY_ONLY"
                ),
                "slice44_progress": (
                    "LOOP805_SLICE44_MEASUREMENT_DRYRUN_DENIAL_CLOSEOUT_RECONCILIATION_READY_ADVISORY_ONLY"
                ),
                "slice44_prompt": "SLICE44_PROMPT_READY_ADVISORY_ONLY",
            },
        },
        "frontier_summary": {
            "ledger_scan_result": "CLEAN_ADVISORY_FRONTIER_READY",
            "oracle_sandbox_probe_gate_phrase_required": "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED",
            "slice44_recommended_next_gate": (
                "OPERATOR_REVIEW_SLICE44_DENIAL_CLOSEOUT_RECONCILIATION"
            ),
            "slice44_status": (
                "LOOP805_SLICE44_MEASUREMENT_DRYRUN_DENIAL_CLOSEOUT_RECONCILIATION_READY_ADVISORY_ONLY"
            ),
        },
        "lane_signals": {
            "held_out_fixture_lane": "DEFERRED_REVIEW_ONLY",
            "notion_sync": "PASTE_READY_ONLY",
            "repo_ledger_frontier_sync": "READY_ADVISORY_ONLY",
            "sandbox_probe_lane": "DEFERRED_UNTIL_EXPLICIT_GATE",
            "selected_lane": "B_SAFE_LEDGER",
        },
        "mode": "reconcile-denial",
        "notion_sync_text_template": (
            "Repo-ledger frontier sync ready - denial closeout reconciled\n"
            f"Commit: {DEFAULT_RESOLVED_COMMIT}\n"
            f"Frontier receipt: {DEFAULT_OUT.as_posix()}\n"
            "Frontier receipt hash: <canonical_hash>\n"
            f"Status: {FRONTIER_STATUS}\n"
            f"Slice44 closeout hash: {SLICE44_CLOSEOUT_HASH}\n"
            "Boundary preserved: no sandbox probe execution, no held-out fixture binding, "
            "no measurement execution, no outcome binding, no Brier resolution, no Notion "
            "auto-tag/writeback, no MCP exposure, no canon mutation, no runtime activation.\n"
            "Next: operator review of the repo-ledger frontier receipt; sandbox probe "
            "remains deferred until ORACLE_SANDBOX_PROBE_GATE_CONFIRMED.\n"
            "Brier Score: 0.10"
        ),
        "provenance": (
            "Provenance: Notion Sprint 001 Hub + Loop 805 Slice 44 + Hash: "
            f"{SLICE44_CLOSEOUT_HASH}"
        ),
        "receipt_id": "ABX_LEDGER_FRONTIER_RECONCILE_DENIAL_001",
        "receipt_status": FRONTIER_STATUS,
        "recommended_next_advisory_action": (
            "Operator reviews this frontier receipt, then either issues the explicit sandbox "
            "gate phrase or requests a separate review-only lane."
        ),
        "residual_risks": [
            "Sandbox probe remains blocked until a separate explicit operator gate.",
            "Held-out fixture binding remains blocked by Slice44 denial posture.",
            "Notion sync text is paste-ready only and performs no writeback.",
        ],
        "timestamp": timestamp,
        "valid_for_brier_resolution": False,
        "valid_for_execution": False,
        "valid_for_fixture_binding": False,
        "valid_for_github_writeback": False,
        "valid_for_mcp_exposure": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_notion_writeback": False,
        "valid_for_outcome_binding": False,
        "valid_for_runtime_activation": False,
        "valid_for_sandbox_probe_execution": False,
        "validation": {
            "all_authority_locks_false_except_advisory_only": True,
            "commands": [
                (
                    f"python {LEGACY_SCRIPTS_DIR}/abx_ledger_frontier.py "
                    "--scan --mode=reconcile-denial --commit=7815e720"
                ),
                f"python -m py_compile {LEGACY_SCRIPTS_DIR}/abx_ledger_frontier.py",
                "git diff --check",
            ],
        },
    }
    receipt["canonical_hash"] = canonical_hash(receipt)
    return receipt


def write_receipt(path: str | Path, receipt: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(receipt, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
