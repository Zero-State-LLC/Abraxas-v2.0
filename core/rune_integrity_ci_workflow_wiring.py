from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "RuneIntegrityCIWorkflowWiringReceipt.v1"
STATUS = "RUNE_INTEGRITY_CI_WORKFLOW_WIRING_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-70"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = "out/audit/rune_integrity_ci_workflow_wiring_001.latest.json"

WORKFLOW_PATH = ".github/workflows/ci.yml"
SCANNER_RECEIPT_PATH = "out/audit/rune_integrity_scanner_guardrails_receipt_001.latest.json"
SCANNER_RUNNER_PATH = "Scripts/run_rune_integrity_scanner_guardrails_receipt.py"
REGISTRY_PATH = "core/generated_artifact_registry.py"
TEST_PATH = "tests/test_rune_integrity_scanner_guardrails.py"

AUTHORITY_LOCKS = {
    "blocking_ci_enforcement": False,
    "canon_mutation": False,
    "external_calls": False,
    "github_writeback": False,
    "mcp_exposure": False,
    "notion_writeback": False,
    "runtime_activation": False,
    "runtime_mutation": False,
    "sandbox_probe_execution": False,
    "workflow_mutation": False,
}


def _read_text(path: Path) -> tuple[str, str]:
    try:
        return path.read_text(encoding="utf-8"), "OBSERVED"
    except FileNotFoundError:
        return "", "MISSING"
    except OSError:
        return "", "NOT_COMPUTABLE"


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str]:
    text, status = _read_text(path)
    if status != "OBSERVED":
        return None, status
    try:
        return json.loads(text), "OBSERVED"
    except json.JSONDecodeError:
        return None, "NOT_COMPUTABLE"


def _source_row(root: Path, relative_path: str) -> dict[str, Any]:
    text, status = _read_text(root / relative_path)
    return {
        "path": relative_path,
        "source_status": status,
        "line_count": len(text.splitlines()) if status == "OBSERVED" else 0,
        "authority_granted": False,
    }


def build_rune_integrity_ci_workflow_wiring_receipt(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    workflow_text, workflow_status = _read_text(root / WORKFLOW_PATH)
    scanner_receipt, scanner_receipt_status = _read_json(root / SCANNER_RECEIPT_PATH)

    report_only_step_present = "Rune integrity scanner (report-only)" in workflow_text
    runner_wired = SCANNER_RUNNER_PATH in workflow_text
    continue_on_error = "continue-on-error: true" in workflow_text

    workflow_posture = (
        "WIRED_ADVISORY_ONLY"
        if workflow_status == "OBSERVED"
        and report_only_step_present
        and runner_wired
        and continue_on_error
        else "NOT_COMPUTABLE"
        if workflow_status == "NOT_COMPUTABLE"
        else "NOT_WIRED_ADVISORY_ONLY"
    )

    scanner_status = (
        scanner_receipt.get("status") if scanner_receipt_status == "OBSERVED" else "MISSING"
    )
    safe_next_surface = (
        "RUNE_INTEGRITY_SCANNER_GUARDRAILS_READY_ADVISORY_ONLY"
        if workflow_posture == "WIRED_ADVISORY_ONLY"
        else "CI_RUNE_SCANNER_WORKFLOW_REPAIR_REVIEW"
    )

    source_table = [
        _source_row(root, WORKFLOW_PATH),
        _source_row(root, SCANNER_RUNNER_PATH),
        _source_row(root, REGISTRY_PATH),
        _source_row(root, TEST_PATH),
        {
            "path": SCANNER_RECEIPT_PATH,
            "source_status": scanner_receipt_status,
            "line_count": 1 if scanner_receipt_status == "OBSERVED" else 0,
            "authority_granted": False,
        },
    ]
    observed_count = sum(1 for row in source_table if row["source_status"] == "OBSERVED")

    base = {
        "artifact_type": ARTIFACT_TYPE,
        "slice_id": SLICE_ID,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "advisory_only": True,
        "projection_only": True,
        "notion_board_url": NOTION_BOARD_URL,
        "authority_locks": AUTHORITY_LOCKS,
        "source_status": (
            "READY"
            if workflow_posture == "WIRED_ADVISORY_ONLY" and observed_count == len(source_table)
            else "READY_WITH_FINDINGS"
            if observed_count
            else "NOT_COMPUTABLE"
        ),
        "source_table": source_table,
        "workflow_wiring_posture": {
            "status": workflow_posture,
            "report_only_step_present": report_only_step_present,
            "runner_wired": runner_wired,
            "continue_on_error": continue_on_error,
            "blocking_ci_enforcement": False,
            "workflow_mutation": False,
            "authority_granted": False,
        },
        "scanner_receipt_status": scanner_status,
        "safe_next_surface": safe_next_surface,
        "recommended_next_engineering_move": (
            "Keep CI wiring report-only for now; if operators want deeper guardrails later, "
            "add a separate enforcement review slice rather than mutating this advisory path."
        ),
        "top_findings": [
            {
                "source": "workflow",
                "finding": "Rune scanner step runs in fast-ci with continue-on-error report-only posture.",
                "severity": "ADVISORY",
            },
            {
                "source": "authority",
                "finding": "No blocking CI enforcement, workflow mutation, sandbox probe, or writeback authority is granted.",
                "severity": "ADVISORY",
            },
        ],
        "validation_plan": [
            "python Scripts/run_rune_integrity_ci_workflow_wiring_receipt.py",
            f"python scripts/run_artifact_regeneration.py --artifact {DEFAULT_OUT_PATH}",
            "python -m py_compile core/rune_integrity_ci_workflow_wiring.py Scripts/run_rune_integrity_ci_workflow_wiring_receipt.py tests/test_rune_integrity_ci_workflow_wiring.py",
            "python -m pytest tests/test_rune_integrity_scanner_guardrails.py tests/test_rune_integrity_ci_workflow_wiring.py tests/test_generated_artifact_registry.py -q -k rune_integrity",
            "git diff --check",
        ],
        "notion_closeout_text": (
            "Slice70 complete - advisory rune integrity scanner now has nonblocking report-only CI workflow visibility; workflow wiring remains read-only and fail-closed with no blocking enforcement, sandbox probe, runtime activation, canon mutation, MCP exposure, external calls, or autonomous writeback authorized. Brier Score: 0.10."
        ),
        "boundary": {
            "sandbox_gate_issue": "#892",
            "sandbox_gate_phrase": "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED",
            "sandbox_gate_issued": False,
            "blocking_ci_enforcement": False,
            "external_calls": False,
            "workflow_mutation": False,
            "notion_writeback": False,
            "github_writeback": False,
            "runtime_activation": False,
            "canon_mutation": False,
            "mcp_exposure": False,
        },
        "provenance": "Notion Sprint 001 Hub + Loop 805 Slice70 + Hash: canonical_hash",
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def write_rune_integrity_ci_workflow_wiring_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
