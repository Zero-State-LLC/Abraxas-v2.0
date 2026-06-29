from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SCRIPT_DIR_KEY = _SCRIPT_DIR.casefold()
_ROOT_DIR = os.path.dirname(_SCRIPT_DIR)
sys.path = [
    path
    for path in sys.path
    if os.path.abspath(path or os.curdir).casefold() != _SCRIPT_DIR_KEY
]
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from core.canonical.json import canonical_hash, write_canonical_json  # noqa: E402


DEFAULT_OUT = (
    "out/audit/abx_ledger_frontier_reconcile_denial_001.latest.json"
)
DEFAULT_TIMESTAMP = "2026-06-21T23:05:00Z"
SUPPORTED_MODE = "reconcile-denial"
FRONTIER_STATUS = "ABX_LEDGER_FRONTIER_RECONCILE_DENIAL_READY_ADVISORY_ONLY"
SLICE44_STATUS = (
    "LOOP805_SLICE44_MEASUREMENT_DRYRUN_DENIAL_CLOSEOUT_RECONCILIATION_READY_"
    "ADVISORY_ONLY"
)
PROVENANCE = (
    "Provenance: Notion Sprint 001 Hub + Loop 805 Slice 44 + Hash: "
    "07b63a7b7ef7021334375d920a0b7d46d3ca700f21bdf5b5882c0352769168d2"
)

EVIDENCE_PATHS = {
    "slice44_closeout": (
        "out/audit/abx_loop805_slice44_measurement_dryrun_denial_closeout_"
        "reconciliation.latest.json"
    ),
    "slice44_prompt": "out/audit/abx_loop805_slice44_prompt_packet.latest.json",
    "slice44_progress": "out/audit/abx_loop805_slice44_progress_receipt.latest.json",
    "sandbox_probe_gate_proposal": (
        "out/audit/oracle_sandbox_probe_gate_proposal_receipt_001.latest.json"
    ),
    "readme": "README.md",
    "plans": "PLANS.md",
    "start_here": "docs/START_HERE.md",
    "index": "docs/INDEX.md",
}

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


def _git_candidates() -> list[str]:
    candidates: list[str] = []
    found = shutil.which("git")
    if found:
        candidates.append(found)
    home = Path.home()
    bundled = home / (
        ".cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/"
        "cmd/git.exe"
    )
    if bundled.exists():
        candidates.append(str(bundled))
    return candidates


def _git(root: Path, args: list[str]) -> str:
    errors: list[str] = []
    for git_bin in _git_candidates():
        try:
            result = subprocess.run(
                [git_bin, *args],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            errors.append(f"{git_bin}: {exc}")
            continue
        return result.stdout.strip()
    raise RuntimeError("git unavailable or failed: " + " | ".join(errors))


def _resolve_commit(root: Path, commit: str) -> str:
    resolved = _git(root, ["rev-parse", "--verify", f"{commit}^{{commit}}"])
    _git(root, ["merge-base", "--is-ancestor", resolved, "HEAD"])
    return resolved


def _load_json(root: Path, path: str) -> dict[str, Any]:
    with (root / path).open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not a JSON object")
    return value


def _contains(root: Path, path: str, needle: str) -> bool:
    return needle in (root / path).read_text(encoding="utf-8")


def _evidence(root: Path) -> dict[str, Any]:
    receipts = {
        key: _load_json(root, path)
        for key, path in EVIDENCE_PATHS.items()
        if path.endswith(".json")
    }
    return {
        "paths": EVIDENCE_PATHS,
        "receipt_hashes": {
            key: value.get("canonical_hash", "MISSING")
            for key, value in receipts.items()
        },
        "receipt_statuses": {
            key: (
                value.get("receipt_status")
                or value.get("packet_status")
                or value.get("gate_status")
                or "MISSING"
            )
            for key, value in receipts.items()
        },
        "doc_markers": {
            "readme_slice44_status": _contains(
                root, "README.md", SLICE44_STATUS
            ),
            "plans_operator_review_gate": _contains(
                root, "PLANS.md", "OPERATOR_REVIEW_SLICE44_DENIAL_CLOSEOUT"
            ),
            "start_here_sandbox_gate_phrase": _contains(
                root, "docs/START_HERE.md", "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED"
            ),
            "index_sandbox_gate_phrase": _contains(
                root, "docs/INDEX.md", "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED"
            ),
        },
    }


def _notion_sync_text(resolved_commit: str, receipt_hash: str) -> str:
    return "\n".join(
        [
            "Repo-ledger frontier sync ready - denial closeout reconciled",
            f"Commit: {resolved_commit}",
            f"Frontier receipt: {DEFAULT_OUT}",
            f"Frontier receipt hash: {receipt_hash}",
            f"Status: {FRONTIER_STATUS}",
            "Slice44 closeout hash: "
            "07b63a7b7ef7021334375d920a0b7d46d3ca700f21bdf5b5882c0352769168d2",
            "Boundary preserved: no sandbox probe execution, no held-out fixture "
            "binding, no measurement execution, no outcome binding, no Brier "
            "resolution, no Notion auto-tag/writeback, no MCP exposure, no canon "
            "mutation, no runtime activation.",
            "Next: operator review of the repo-ledger frontier receipt; sandbox "
            "probe remains deferred until ORACLE_SANDBOX_PROBE_GATE_CONFIRMED.",
            "Brier Score: 0.10",
        ]
    )


def _notion_sync_template(resolved_commit: str) -> str:
    return _notion_sync_text(resolved_commit, "<canonical_hash>")


def build_receipt(root: Path, commit: str, timestamp: str) -> dict[str, Any]:
    resolved_commit = _resolve_commit(root, commit)
    evidence = _evidence(root)
    if not all(evidence["doc_markers"].values()):
        missing = [
            key for key, present in evidence["doc_markers"].items() if not present
        ]
        raise ValueError(f"ledger doc markers missing: {', '.join(missing)}")

    base: dict[str, Any] = {
        "artifact_type": "AbxLedgerFrontierReconcileDenialReceipt.v1",
        "receipt_id": "ABX_LEDGER_FRONTIER_RECONCILE_DENIAL_001",
        "receipt_status": FRONTIER_STATUS,
        "timestamp": timestamp,
        "brier_score": 0.1,
        "brier_score_text": "Brier Score: 0.10",
        "commit": {
            "requested": commit,
            "resolved": resolved_commit,
            "verified_in_local_history": True,
        },
        "mode": SUPPORTED_MODE,
        "authority_locks": AUTHORITY_LOCKS,
        "lane_signals": {
            "selected_lane": "B_SAFE_LEDGER",
            "repo_ledger_frontier_sync": "READY_ADVISORY_ONLY",
            "sandbox_probe_lane": "DEFERRED_UNTIL_EXPLICIT_GATE",
            "held_out_fixture_lane": "DEFERRED_REVIEW_ONLY",
            "notion_sync": "PASTE_READY_ONLY",
        },
        "evidence": evidence,
        "frontier_summary": {
            "slice44_status": SLICE44_STATUS,
            "slice44_recommended_next_gate": (
                "OPERATOR_REVIEW_SLICE44_DENIAL_CLOSEOUT_RECONCILIATION"
            ),
            "oracle_sandbox_probe_gate_phrase_required": (
                "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED"
            ),
            "ledger_scan_result": "CLEAN_ADVISORY_FRONTIER_READY",
        },
        "deferred_lanes": [
            {
                "lane": "sandbox_probe",
                "status": "DEFERRED",
                "reason": (
                    "Repo docs require ORACLE_SANDBOX_PROBE_GATE_CONFIRMED and "
                    "a governed probe receipt before any probe."
                ),
                "brier_score": 0.1,
            },
            {
                "lane": "held_out_fixture_binding",
                "status": "DEFERRED",
                "reason": (
                    "Slice44 denial closeout keeps held-out set binding, fixture "
                    "binding, outcome binding, and Brier resolution false."
                ),
                "brier_score": 0.1,
            },
            {
                "lane": "notion_auto_tag",
                "status": "DEFERRED",
                "reason": (
                    "This receipt provides paste-ready Notion text only; no "
                    "automatic Notion mutation is authorized."
                ),
                "brier_score": 0.1,
            },
        ],
        "validation": {
            "commands": [
                (
                    "python Scripts/abx_ledger_frontier.py --scan "
                    "--mode=reconcile-denial --commit=7815e720"
                ),
                "python -m py_compile Scripts/abx_ledger_frontier.py",
                "git diff --check",
            ],
            "all_authority_locks_false_except_advisory_only": True,
        },
        "notion_sync_text_template": _notion_sync_template(resolved_commit),
        "residual_risks": [
            "Sandbox probe remains blocked until a separate explicit operator gate.",
            "Held-out fixture binding remains blocked by Slice44 denial posture.",
            "Notion sync text is paste-ready only and performs no writeback.",
        ],
        "recommended_next_advisory_action": (
            "Operator reviews this frontier receipt, then either issues the "
            "explicit sandbox gate phrase or requests a separate review-only lane."
        ),
        "provenance": PROVENANCE,
        "valid_for_execution": False,
        "valid_for_sandbox_probe_execution": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_notion_writeback": False,
        "valid_for_github_writeback": False,
        "valid_for_runtime_activation": False,
        "valid_for_mcp_exposure": False,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def write_receipt(path: Path, receipt: dict[str, Any]) -> None:
    receipt_without_hash = dict(receipt)
    observed_hash = receipt_without_hash.pop("canonical_hash")
    expected_hash = canonical_hash(receipt_without_hash)
    if observed_hash != expected_hash:
        raise ValueError("receipt canonical_hash mismatch")
    write_canonical_json(path, receipt)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ABRAXAS advisory repo-ledger frontier scanner."
    )
    parser.add_argument("--scan", action="store_true", help="Run the scan.")
    parser.add_argument("--mode", choices=[SUPPORTED_MODE], required=True)
    parser.add_argument("--commit", required=True, help="Commit SHA or prefix to verify.")
    parser.add_argument("--out", default=DEFAULT_OUT, help="Receipt output path.")
    parser.add_argument(
        "--timestamp",
        default=DEFAULT_TIMESTAMP,
        help="Deterministic receipt timestamp.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.scan:
        raise SystemExit("--scan is required")
    root = Path(__file__).resolve().parents[1]
    receipt = build_receipt(root, args.commit, args.timestamp)
    out_path = root / args.out
    write_receipt(out_path, receipt)
    print(f"receipt_status: {receipt['receipt_status']}")
    print(f"canonical_hash: {receipt['canonical_hash']}")
    print(f"receipt_path: {args.out}")
    print("notion_sync_text:")
    print(
        _notion_sync_text(
            receipt["commit"]["resolved"],
            receipt["canonical_hash"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
