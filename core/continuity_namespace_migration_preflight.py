from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ContinuityNamespaceMigrationPreflightReceipt.v1"
STATUS = "CONTINUITY_NAMESPACE_MIGRATION_PREFLIGHT_READY_ADVISORY_ONLY"
DEGRADED_STATUS = "CONTINUITY_NAMESPACE_MIGRATION_PREFLIGHT_HELD"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-PRIORITY2-MIGRATION-PREFLIGHT"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = "out/audit/continuity_namespace_migration_preflight_001.latest.json"

MIGRATION_TOOLING_REFRESH_PATH = (
    "out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json"
)
MIGRATION_RUN_RECEIPT_PATH = "out/audit/continuity_namespace_migration_run_001.latest.json"
ALIAS_IMPLEMENTATION_DESIGN_PATH = (
    "out/audit/continuity_namespace_alias_implementation_design_001.latest.json"
)
SUBSYSTEM_HEALTH_DASHBOARD_PATH = "out/audit/subsystem_health_dashboard_001.latest.json"
PRIORITY2_CLOSEOUT_PATH = "out/audit/priority2_live_console_migration_closeout_001.latest.json"
MIGRATION_STATUS_DOC_PATH = "docs/status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md"
MIGRATION_RUNNER_DOC_PATH = "docs/status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md"
ALIAS_DESIGN_DOC_PATH = "docs/status/CONTINUITY_NAMESPACE_ALIAS_IMPLEMENTATION_DESIGN.md"

SOURCE_PATHS = (
    MIGRATION_TOOLING_REFRESH_PATH,
    MIGRATION_RUN_RECEIPT_PATH,
    ALIAS_IMPLEMENTATION_DESIGN_PATH,
    SUBSYSTEM_HEALTH_DASHBOARD_PATH,
    PRIORITY2_CLOSEOUT_PATH,
    MIGRATION_STATUS_DOC_PATH,
    MIGRATION_RUNNER_DOC_PATH,
    ALIAS_DESIGN_DOC_PATH,
)

AUTHORITY_LOCKS = {
    "alias_materialization": False,
    "canon_mutation": False,
    "execution_authority": False,
    "external_calls": False,
    "github_writeback": False,
    "historical_receipt_rebinding": False,
    "mcp_exposure": False,
    "notion_writeback": False,
    "path_rename_authority": False,
    "production_activation": False,
    "runtime_activation": False,
    "runtime_mutation": False,
    "scheduler_mutation": False,
}

REQUIRED_RECEIPT_STATUSES = {
    MIGRATION_TOOLING_REFRESH_PATH: "CONTINUITY_NAMESPACE_MIGRATION_TOOLING_REFRESH_READY_ADVISORY_ONLY",
    MIGRATION_RUN_RECEIPT_PATH: "CONTINUITY_NAMESPACE_MIGRATION_RUNNER_READY_ADVISORY_ONLY",
    ALIAS_IMPLEMENTATION_DESIGN_PATH: "CONTINUITY_NAMESPACE_ALIAS_IMPLEMENTATION_DESIGN_READY_ADVISORY_ONLY",
    SUBSYSTEM_HEALTH_DASHBOARD_PATH: "SUBSYSTEM_HEALTH_DASHBOARD_READY_ADVISORY_ONLY",
    PRIORITY2_CLOSEOUT_PATH: "PRIORITY2_LIVE_CONSOLE_MIGRATION_CLOSEOUT_READY_ADVISORY_ONLY",
}


def _read_text(path: Path) -> tuple[str, str]:
    try:
        return path.read_text(encoding="utf-8"), "OBSERVED"
    except FileNotFoundError:
        return "", "MISSING"
    except OSError:
        return "", "NOT_COMPUTABLE"


def _read_json(path: Path) -> tuple[dict[str, Any], str]:
    text, status = _read_text(path)
    if status != "OBSERVED":
        return {}, status
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {}, "NOT_COMPUTABLE"
    if not isinstance(payload, dict):
        return {}, "NOT_COMPUTABLE"
    return payload, "OBSERVED"


def _source_row(root: Path, relative_path: str) -> dict[str, Any]:
    path = root / relative_path
    text, status = _read_text(path)
    row: dict[str, Any] = {
        "path": relative_path,
        "source_status": status,
        "line_count": len(text.splitlines()) if status == "OBSERVED" else 0,
        "authority_granted": False,
    }
    if relative_path.endswith(".json"):
        payload, json_status = _read_json(path)
        row["source_status"] = json_status
        row["top_level_key_count"] = len(payload) if json_status == "OBSERVED" else 0
        row["observed_status"] = payload.get("status", "NOT_COMPUTABLE")
    return row


def _authority_false(payload: dict[str, Any]) -> bool:
    locks = payload.get("authority_locks", {})
    if not isinstance(locks, dict):
        return False
    return all(value is False for value in locks.values())


def _preflight_checks(root: Path) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    payloads: dict[str, dict[str, Any]] = {}
    checks: list[dict[str, Any]] = []

    for path, expected_status in REQUIRED_RECEIPT_STATUSES.items():
        payload, source_status = _read_json(root / path)
        payloads[path] = payload
        observed_status = payload.get("status", "NOT_COMPUTABLE")
        checks.append(
            {
                "check_id": f"{Path(path).stem}_observed",
                "path": path,
                "expected_status": expected_status,
                "observed_status": observed_status,
                "result": "PASS"
                if source_status == "OBSERVED" and observed_status == expected_status
                else "HELD",
                "authority_granted": False,
            }
        )
        checks.append(
            {
                "check_id": f"{Path(path).stem}_authority_locks",
                "path": path,
                "expected": "all authority locks false",
                "result": "PASS" if source_status == "OBSERVED" and _authority_false(payload) else "HELD",
                "authority_granted": False,
            }
        )

    migration_runner = payloads.get(MIGRATION_RUN_RECEIPT_PATH, {})
    requested_posture = migration_runner.get("requested_execution_posture", {})
    checks.append(
        {
            "check_id": "migration_runner_execution_posture",
            "path": MIGRATION_RUN_RECEIPT_PATH,
            "expected": "advisory READY with authority_granted false",
            "observed_result": requested_posture.get("result", "NOT_COMPUTABLE"),
            "result": "PASS"
            if requested_posture.get("result") == "READY"
            and requested_posture.get("authority_granted") is False
            else "HELD",
            "authority_granted": False,
        }
    )

    alias_design = payloads.get(ALIAS_IMPLEMENTATION_DESIGN_PATH, {})
    implementation_posture = alias_design.get("implementation_posture", {})
    checks.append(
        {
            "check_id": "alias_design_remains_held",
            "path": ALIAS_IMPLEMENTATION_DESIGN_PATH,
            "expected": "DESIGN_ONLY_HELD and not valid for implementation",
            "observed_state": implementation_posture.get("current_state", "NOT_COMPUTABLE"),
            "result": "PASS"
            if implementation_posture.get("current_state") == "DESIGN_ONLY_HELD"
            and implementation_posture.get("valid_for_implementation") is False
            else "HELD",
            "authority_granted": False,
        }
    )
    return checks, payloads


def _overall_status(checks: list[dict[str, Any]]) -> str:
    return STATUS if all(check["result"] == "PASS" for check in checks) else DEGRADED_STATUS


def build_continuity_namespace_migration_preflight_receipt(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source_table = [_source_row(root, path) for path in SOURCE_PATHS]
    checks, payloads = _preflight_checks(root)
    status = _overall_status(checks)
    pass_count = sum(1 for check in checks if check["result"] == "PASS")
    held_count = len(checks) - pass_count
    migration_runner = payloads.get(MIGRATION_RUN_RECEIPT_PATH, {})
    alias_design = payloads.get(ALIAS_IMPLEMENTATION_DESIGN_PATH, {})

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "status": status,
        "slice_id": SLICE_ID,
        "brier_score": BRIER_SCORE,
        "advisory_only": True,
        "projection_only": True,
        "notion_board_url": NOTION_BOARD_URL,
        "authority_locks": AUTHORITY_LOCKS,
        "source_status": "READY" if status == STATUS else "READY_WITH_FINDINGS",
        "source_table": source_table,
        "preflight_summary": {
            "check_count": len(checks),
            "pass_count": pass_count,
            "held_count": held_count,
            "migration_runner_status": migration_runner.get("status", "NOT_COMPUTABLE"),
            "alias_design_state": alias_design.get("implementation_posture", {}).get(
                "current_state", "NOT_COMPUTABLE"
            ),
            "valid_for_implementation": False,
            "authority_granted": False,
        },
        "preflight_checks": checks,
        "blocked_actions": [
            "MATERIALIZE_ALIAS_MANIFEST",
            "RENAME_FILES",
            "MOVE_FILES",
            "REWRITE_IDS",
            "REWRITE_HISTORICAL_RECEIPTS",
            "EXECUTE_NAMESPACE_MIGRATION",
            "MUTATE_CANON_RUNTIME_STATE",
            "MUTATE_SCHEDULER_OR_QUEUE",
        ],
        "recommended_next_engineering_move": (
            "Use this preflight as the gate before any future migration-runner UI consumer or additive alias implementation design refresh."
            if status == STATUS
            else "Repair the held continuity namespace source/check before starting a live-console or alias implementation follow-on."
        ),
        "validation_plan": [
            "python scripts/run_continuity_namespace_migration_preflight_receipt.py",
            f"python scripts/run_artifact_regeneration.py --artifact {DEFAULT_OUT_PATH}",
            "python -m pytest tests/test_continuity_namespace_migration_preflight.py tests/test_generated_artifact_registry.py -q -k continuity_namespace_migration_preflight",
            "git diff --check",
            "python scripts/run_fast_ci.py",
        ],
        "boundary": {
            "alias_materialization": False,
            "canon_mutation": False,
            "external_calls": False,
            "github_writeback": False,
            "historical_receipt_rebinding": False,
            "mcp_exposure": False,
            "notion_writeback": False,
            "path_rename_authority": False,
            "runtime_activation": False,
            "scheduler_mutation": False,
        },
        "notion_closeout_text": (
            "Priority 2 migration preflight scaffold shipped; the continuity namespace migration runner, alias implementation design, subsystem health dashboard, and Priority 2 closeout receipts now have one deterministic advisory preflight before any future UI consumer or additive design refresh; no alias materialization, path rename, runtime activation, canon mutation, queue/scheduler mutation, external calls, or autonomous writeback authorized. Brier Score: 0.10."
        ),
        "provenance": "Notion Engineering Board Priority 2 Card 1 + Hash: canonical_hash",
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def write_continuity_namespace_migration_preflight_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
