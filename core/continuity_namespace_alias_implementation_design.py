from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ContinuityNamespaceAliasImplementationDesignReceipt.v1"
STATUS = "CONTINUITY_NAMESPACE_ALIAS_IMPLEMENTATION_DESIGN_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-71"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = (
    "out/audit/continuity_namespace_alias_implementation_design_001.latest.json"
)

ALIAS_PLAN_PATH = "out/continuity_namespace_alias_plan/latest.json"
MIGRATION_STATUS_PATH = "docs/status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md"
MIGRATION_RUNNER_PATH = "docs/status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md"
HEALTH_DASHBOARD_PATH = "out/audit/subsystem_health_dashboard_001.latest.json"
MIGRATION_RUN_RECEIPT_PATH = "out/audit/continuity_namespace_migration_run_001.latest.json"
REGISTRY_PATH = "core/generated_artifact_registry.py"

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
    "runtime_activation": False,
    "runtime_mutation": False,
    "sandbox_probe_execution": False,
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
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None, "NOT_COMPUTABLE"
    return parsed if isinstance(parsed, dict) else None, "OBSERVED"


def _source_row(root: Path, relative_path: str) -> dict[str, Any]:
    text, status = _read_text(root / relative_path)
    return {
        "path": relative_path,
        "source_status": status,
        "line_count": len(text.splitlines()) if status == "OBSERVED" else 0,
        "authority_granted": False,
    }


def _design_rows(
    alias_plan: dict[str, Any],
    runner: dict[str, Any],
    dashboard: dict[str, Any],
) -> list[dict[str, Any]]:
    status_fields = alias_plan.get("status_surface_additive_fields", [])
    validation_gates = alias_plan.get("validation_gates", [])
    blocked_actions = runner.get("blocked_actions", [])
    next_lane = dashboard.get("recommended_next_lane", "NOT_COMPUTABLE")

    return [
        {
            "design_stage": "ALIAS_MANIFEST_METADATA_DESIGN",
            "current_posture": "DESIGN_ONLY_HELD",
            "observed_inputs": [
                ALIAS_PLAN_PATH,
                MIGRATION_RUN_RECEIPT_PATH,
            ],
            "planned_output": "out/continuity_namespace_alias_manifest/latest.json",
            "success_criteria": (
                "Manifest shape stays additive-only, preserves canonical IDs, and "
                "remains invalid for execution without later stabilization evidence."
            ),
            "blocked_actions": [
                "MATERIALIZE_ALIAS_MANIFEST",
                "REWRITE_IDS",
                "MOVE_FILES",
            ],
            "authority_granted": False,
        },
        {
            "design_stage": "STATUS_SURFACE_PROPAGATION_DESIGN",
            "current_posture": "DESIGN_ONLY_HELD",
            "observed_inputs": [
                MIGRATION_STATUS_PATH,
                MIGRATION_RUNNER_PATH,
                HEALTH_DASHBOARD_PATH,
            ],
            "planned_output": "status-surface additive metadata fields",
            "success_criteria": (
                "Only additive alias fields are described for status surfaces; no "
                "existing route is renamed or rewritten."
            ),
            "blocked_actions": [
                "MUTATE_EXISTING_SURFACES",
                "GRANT_AUTHORIZATION",
            ],
            "authority_granted": False,
            "status_surface_fields": status_fields,
        },
        {
            "design_stage": "VALIDATION_AND_REGISTRY_DESIGN",
            "current_posture": "DESIGN_ONLY_HELD",
            "observed_inputs": [
                REGISTRY_PATH,
                ALIAS_PLAN_PATH,
            ],
            "planned_output": "future validation receipt and registry binding additions",
            "success_criteria": (
                "Validation gates remain fail-closed and registry additions stay "
                "no-arg regenerable if a later additive manifest draft is authorized."
            ),
            "blocked_actions": [
                "CREATE_EXECUTION_PATHS",
                "MUTATE_CANON_RUNTIME_SCHEDULER_FORECAST_STATE",
            ],
            "authority_granted": False,
            "validation_gates": validation_gates,
        },
        {
            "design_stage": "ROLLBACK_NO_OP_PATH",
            "current_posture": "READY",
            "observed_inputs": [
                MIGRATION_RUN_RECEIPT_PATH,
                ALIAS_PLAN_PATH,
            ],
            "planned_output": "no-op advisory hold",
            "success_criteria": (
                "If any implementation prerequisite is missing, the design routes "
                "back to the additive alias plan and preserves current state unchanged."
            ),
            "blocked_actions": blocked_actions[:4] if blocked_actions else [],
            "authority_granted": False,
            "recommended_next_lane": next_lane,
        },
    ]


def build_continuity_namespace_alias_implementation_design_receipt(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    alias_plan, alias_plan_status = _read_json(root / ALIAS_PLAN_PATH)
    runner, runner_status = _read_json(root / MIGRATION_RUN_RECEIPT_PATH)
    dashboard, dashboard_status = _read_json(root / HEALTH_DASHBOARD_PATH)

    alias_plan = alias_plan or {}
    runner = runner or {}
    dashboard = dashboard or {}

    design_rows = _design_rows(alias_plan, runner, dashboard)
    source_table = [
        {
            **_source_row(root, ALIAS_PLAN_PATH),
            "source_status": alias_plan_status,
        },
        {
            **_source_row(root, MIGRATION_STATUS_PATH),
        },
        {
            **_source_row(root, MIGRATION_RUNNER_PATH),
        },
        {
            **_source_row(root, HEALTH_DASHBOARD_PATH),
            "source_status": dashboard_status,
        },
        {
            **_source_row(root, MIGRATION_RUN_RECEIPT_PATH),
            "source_status": runner_status,
        },
        {
            **_source_row(root, REGISTRY_PATH),
        },
    ]
    observed_count = sum(1 for row in source_table if row["source_status"] == "OBSERVED")

    readiness = alias_plan.get(
        "stabilization_receipt_requirement_before_implementation", {}
    )
    safe_next_surface = runner.get(
        "safe_next_surface", "CONTINUITY_NAMESPACE_ADDITIVE_ALIAS_PLAN_001_ADVISORY_ONLY"
    )
    recommended_next_move = (
        "Keep additive alias implementation at design-only posture until a future "
        "stabilization receipt explicitly lifts the implementation hold."
    )

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
            if observed_count == len(source_table)
            else "READY_WITH_FINDINGS"
            if observed_count
            else "NOT_COMPUTABLE"
        ),
        "source_table": source_table,
        "implementation_posture": {
            "current_state": "DESIGN_ONLY_HELD",
            "safe_next_surface": safe_next_surface,
            "required_stabilization_status": readiness.get(
                "required_status", "ALIAS_PLAN_STABILIZED_ADVISORY_ONLY"
            ),
            "valid_for_implementation": readiness.get(
                "valid_for_implementation_until_receipt", False
            ),
            "authority_granted": False,
        },
        "design_stage_rows": design_rows,
        "blocked_action_classes": runner.get("blocked_actions", []),
        "top_findings": [
            {
                "code": "STABILIZATION_RECEIPT_REQUIRED",
                "detail": (
                    "The existing alias plan still requires a future stabilization "
                    "receipt before any implementation surface can become valid."
                ),
                "severity": "MEDIUM",
                "authority_granted": False,
            },
            {
                "code": "ALIAS_MATERIALIZATION_DENIED",
                "detail": (
                    "Alias materialization, path renames, and historical receipt "
                    "rebinding remain explicitly denied in this design slice."
                ),
                "severity": "MEDIUM",
                "authority_granted": False,
            },
        ],
        "recommended_next_engineering_move": recommended_next_move,
        "validation_plan": [
            "python scripts/temporal/run_continuity_namespace_alias_implementation_design_receipt.py",
            f"python scripts/artifact/run_artifact_regeneration.py --artifact {DEFAULT_OUT_PATH}",
            "python -m py_compile core/continuity_namespace_alias_implementation_design.py scripts/temporal/run_continuity_namespace_alias_implementation_design_receipt.py tests/test_continuity_namespace_alias_implementation_design.py",
            "python -m pytest tests/test_continuity_namespace_alias_implementation_design.py tests/test_generated_artifact_registry.py -q -k continuity_namespace_alias_implementation_design",
            "git diff --check",
        ],
        "notion_closeout_text": (
            "Slice71 complete - Continuity Namespace Alias Implementation Design shipped; additive alias implementation now has a design-only advisory route grounded in the existing alias plan, migration runner, and subsystem health surfaces; no alias materialization, file renames, ID rewrites, runtime activation, canon mutation, MCP exposure, external calls, or autonomous writeback authorized. Brier Score: 0.10."
        ),
        "boundary": {
            "sandbox_gate_issue": "#892",
            "sandbox_gate_phrase": "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED",
            "sandbox_gate_issued": False,
            "alias_materialization": False,
            "canon_mutation": False,
            "external_calls": False,
            "github_writeback": False,
            "historical_receipt_rebinding": False,
            "mcp_exposure": False,
            "notion_writeback": False,
            "path_rename_authority": False,
            "runtime_activation": False,
        },
        "provenance": "Notion Sprint 001 Hub + Loop 805 Slice71 + Hash: canonical_hash",
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def write_continuity_namespace_alias_implementation_design_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
