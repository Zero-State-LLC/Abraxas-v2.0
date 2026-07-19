from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ContinuityNamespaceMigrationRunReceipt.v1"
STATUS = "CONTINUITY_NAMESPACE_MIGRATION_RUNNER_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-63"
MIGRATION_RUN_ID = "CONTINUITY_NAMESPACE_MIGRATION_RUN_001"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = "out/audit/continuity_namespace_migration_run_001.latest.json"
RUNNER_DOC_PATH = "docs/status/CONTINUITY_NAMESPACE_MIGRATION_RUNNER.md"

CONTINUITY_NAMESPACE_AUDIT_PATH = "out/continuity_namespace_audit/latest.json"
CONTINUITY_NAMESPACE_MIGRATION_PLAN_PATH = "out/continuity_namespace_migration_plan/latest.json"
CONTINUITY_NAMESPACE_STABILIZATION_RECEIPT_PATH = (
    "out/continuity_namespace_stabilization_receipt/latest.json"
)
CONTINUITY_NAMESPACE_READINESS_REVIEW_PATH = (
    "out/continuity_namespace_readiness_review/latest.json"
)
CONTINUITY_NAMESPACE_ALIAS_PLAN_PATH = "out/continuity_namespace_alias_plan/latest.json"
CONTINUITY_NAMESPACE_TOOLING_REFRESH_RECEIPT_PATH = (
    "out/audit/continuity_namespace_migration_tooling_refresh_001.latest.json"
)
CONTINUITY_NAMESPACE_STATUS_DOC_PATH = "docs/status/CONTINUITY_NAMESPACE_MIGRATION_STATUS.md"
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"

SOURCE_PATHS = (
    CONTINUITY_NAMESPACE_AUDIT_PATH,
    CONTINUITY_NAMESPACE_MIGRATION_PLAN_PATH,
    CONTINUITY_NAMESPACE_STABILIZATION_RECEIPT_PATH,
    CONTINUITY_NAMESPACE_READINESS_REVIEW_PATH,
    CONTINUITY_NAMESPACE_ALIAS_PLAN_PATH,
    CONTINUITY_NAMESPACE_TOOLING_REFRESH_RECEIPT_PATH,
    CONTINUITY_NAMESPACE_STATUS_DOC_PATH,
    CONTINUITY_SPINE_PATH,
    "core/generated_artifact_registry.py",
)

STAGE_ORDER = (
    "START",
    "INVENTORY",
    "ALIAS_BINDING_SCAFFOLD",
    "ROUTE_REWRITE_SCAFFOLD",
    "RECEIPT_REBINDING_SCAFFOLD",
    "ROLLBACK_PATH",
    "FINAL_STATUS",
)

BLOCKED_ACTIONS = (
    "RENAME_FILES",
    "MOVE_FILES",
    "REWRITE_IDS",
    "MATERIALIZE_ALIAS_MANIFEST",
    "REWRITE_HISTORICAL_RECEIPTS",
    "EXECUTE_NAMESPACE_MIGRATION",
    "AUTHORIZE_ALIAS_IMPLEMENTATION",
    "MUTATE_CANON_RUNTIME_STATE",
)

AUTHORITY_LOCKS = {
    "canon_mutation": False,
    "external_calls": False,
    "github_writeback": False,
    "mcp_exposure": False,
    "notion_writeback": False,
    "production_activation": False,
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


def _load_json(path: Path) -> tuple[dict[str, Any], str]:
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


def _source_row(repo_root: Path, relative_path: str) -> dict[str, Any]:
    path = repo_root / relative_path
    text, status = _read_text(path)
    row: dict[str, Any] = {
        "path": relative_path,
        "source_status": status,
        "line_count": len(text.splitlines()) if status == "OBSERVED" else 0,
        "authority_granted": False,
    }
    if relative_path.endswith(".json"):
        payload, json_status = _load_json(path)
        row["source_status"] = json_status
        row["top_level_key_count"] = len(payload) if json_status == "OBSERVED" else 0
    return row


def _payloads_and_statuses(
    root: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    payloads: dict[str, dict[str, Any]] = {}
    statuses: dict[str, str] = {}
    for label, relative_path in (
        ("audit", CONTINUITY_NAMESPACE_AUDIT_PATH),
        ("migration_plan", CONTINUITY_NAMESPACE_MIGRATION_PLAN_PATH),
        ("stabilization_receipt", CONTINUITY_NAMESPACE_STABILIZATION_RECEIPT_PATH),
        ("readiness_review", CONTINUITY_NAMESPACE_READINESS_REVIEW_PATH),
        ("alias_plan", CONTINUITY_NAMESPACE_ALIAS_PLAN_PATH),
        ("tooling_refresh_receipt", CONTINUITY_NAMESPACE_TOOLING_REFRESH_RECEIPT_PATH),
        ("continuity_spine", CONTINUITY_SPINE_PATH),
    ):
        payloads[label], statuses[label] = _load_json(root / relative_path)
    return payloads, statuses


def _stack_ready(payloads: dict[str, dict[str, Any]], statuses: dict[str, str]) -> bool:
    required = (
        "audit",
        "migration_plan",
        "stabilization_receipt",
        "readiness_review",
        "alias_plan",
        "tooling_refresh_receipt",
    )
    if any(statuses.get(label) != "OBSERVED" for label in required):
        return False
    return (
        payloads["readiness_review"].get("readiness_status") == "READY_FOR_ADDITIVE_ALIAS_PLAN"
        and payloads["readiness_review"].get("safe_next_surface_recommendation")
        == "CONTINUITY_NAMESPACE_ADDITIVE_ALIAS_PLAN_001_ADVISORY_ONLY"
        and payloads["alias_plan"].get("plan_status") == "ADDITIVE_ALIAS_PLAN_EMITTED"
        and payloads["tooling_refresh_receipt"].get("current_route_class")
        == "ACTIVE MIGRATION ROUTE"
    )


def _source_invariants(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    state = payloads.get("readiness_review", {}).get("source_state", {})
    spine = payloads.get("continuity_spine", {})
    return {
        "highest_observed_lane": state.get(
            "highest_observed_lane", spine.get("highest_lane", "NOT_COMPUTABLE")
        ),
        "lane_count": state.get("lane_count", spine.get("lane_count", 0)),
        "governance": state.get("governance", "NOT_COMPUTABLE"),
        "canon": state.get("canon", "NOT_COMPUTABLE"),
        "downstream": state.get("downstream", "NOT_COMPUTABLE"),
        "authority_granted": False,
    }


def _blocked_execution_posture(requested_mode: str, stack_ready: bool) -> dict[str, Any]:
    if requested_mode == "execute-like":
        return {
            "requested_mode": requested_mode,
            "effective_mode": "advisory",
            "result": "HELD",
            "reason": (
                "Execution-style requests remain blocked because continuity namespace implementation authority is still closed."
            ),
            "authority_granted": False,
        }
    if not stack_ready:
        return {
            "requested_mode": requested_mode,
            "effective_mode": "advisory",
            "result": "HELD",
            "reason": (
                "One or more required continuity namespace source surfaces are missing or degraded."
            ),
            "authority_granted": False,
        }
    return {
        "requested_mode": requested_mode,
        "effective_mode": "advisory",
        "result": "READY",
        "reason": "Runner is operating as a deterministic advisory migration simulation only.",
        "authority_granted": False,
    }


def _stage_rows(
    payloads: dict[str, dict[str, Any]],
    statuses: dict[str, str],
    *,
    requested_mode: str,
    stack_ready: bool,
) -> list[dict[str, Any]]:
    readiness = payloads.get("readiness_review", {})
    alias_plan = payloads.get("alias_plan", {})
    migration_plan = payloads.get("migration_plan", {})
    blocked_posture = _blocked_execution_posture(requested_mode, stack_ready)
    stages: list[dict[str, Any]] = []

    stages.append(
        {
            "stage_id": "START",
            "observed_inputs": [
                CONTINUITY_NAMESPACE_TOOLING_REFRESH_RECEIPT_PATH,
                CONTINUITY_NAMESPACE_STATUS_DOC_PATH,
            ],
            "intended_operation_class": "run_initialization",
            "blocked_authority": list(BLOCKED_ACTIONS),
            "success_criteria": "Migration runner begins in advisory mode with source stack fully enumerated.",
            "rollback_note": "No mutation occurs, so rollback is a no-op.",
            "resulting_advisory_posture": blocked_posture["result"],
            "authority_granted": False,
        }
    )
    stages.append(
        {
            "stage_id": "INVENTORY",
            "observed_inputs": list(SOURCE_PATHS[:6]),
            "intended_operation_class": "source_inventory_and_validation",
            "blocked_authority": list(BLOCKED_ACTIONS),
            "success_criteria": "Required continuity namespace audit/plan/stabilization/readiness/alias/tooling-refresh inputs are observed and structurally usable.",
            "rollback_note": "If any source is missing or malformed, hold the run and emit degraded findings only.",
            "resulting_advisory_posture": "READY" if stack_ready else "NOT_COMPUTABLE / HELD",
            "authority_granted": False,
        }
    )
    stages.append(
        {
            "stage_id": "ALIAS_BINDING_SCAFFOLD",
            "observed_inputs": [
                CONTINUITY_NAMESPACE_ALIAS_PLAN_PATH,
                CONTINUITY_NAMESPACE_READINESS_REVIEW_PATH,
            ],
            "intended_operation_class": "namespace_aliasing_and_rebinding_scaffold",
            "blocked_authority": [
                "MATERIALIZE_ALIAS_MANIFEST",
                "REWRITE_IDS",
                "AUTHORIZE_ALIAS_IMPLEMENTATION",
            ],
            "success_criteria": (
                f"Preserve `{alias_plan.get('selected_policy', 'NOT_COMPUTABLE')}` and route only to `{readiness.get('safe_next_surface_recommendation', 'NOT_COMPUTABLE')}`."
            ),
            "rollback_note": "Keep alias work at metadata-planning level only; do not touch existing surfaces or IDs.",
            "resulting_advisory_posture": "SCAFFOLD_ONLY",
            "authority_granted": False,
        }
    )
    stages.append(
        {
            "stage_id": "ROUTE_REWRITE_SCAFFOLD",
            "observed_inputs": [
                CONTINUITY_NAMESPACE_MIGRATION_PLAN_PATH,
                CONTINUITY_SPINE_PATH,
            ],
            "intended_operation_class": "route_rewrite_planning_scaffold",
            "blocked_authority": ["RENAME_FILES", "MOVE_FILES", "EXECUTE_NAMESPACE_MIGRATION"],
            "success_criteria": (
                f"Maintain migration plan posture `{migration_plan.get('selected_policy', 'NOT_COMPUTABLE')}` while preserving `P102G`, `58`, `FROZEN`, and `ADVISORY_ONLY` invariants."
            ),
            "rollback_note": "Route rewrites remain planned steps only; no path changes or lane rewrites occur.",
            "resulting_advisory_posture": "SCAFFOLD_ONLY",
            "authority_granted": False,
        }
    )
    stages.append(
        {
            "stage_id": "RECEIPT_REBINDING_SCAFFOLD",
            "observed_inputs": [
                CONTINUITY_NAMESPACE_AUDIT_PATH,
                CONTINUITY_NAMESPACE_TOOLING_REFRESH_RECEIPT_PATH,
                "core/generated_artifact_registry.py",
            ],
            "intended_operation_class": "historical_receipt_rebinding_scaffold",
            "blocked_authority": [
                "REWRITE_HISTORICAL_RECEIPTS",
                "MUTATE_CANON_RUNTIME_STATE",
            ],
            "success_criteria": "Historical receipt rebinding is described as a future additive-metadata exercise only, with registry-backed provenance preserved.",
            "rollback_note": "If receipt rebinding cannot stay additive-only, keep it fully blocked and route back to design work.",
            "resulting_advisory_posture": "SCAFFOLD_ONLY",
            "authority_granted": False,
        }
    )
    stages.append(
        {
            "stage_id": "ROLLBACK_PATH",
            "observed_inputs": [
                CONTINUITY_NAMESPACE_STABILIZATION_RECEIPT_PATH,
                CONTINUITY_NAMESPACE_STATUS_DOC_PATH,
            ],
            "intended_operation_class": "rollback_definition",
            "blocked_authority": list(BLOCKED_ACTIONS),
            "success_criteria": "Rollback path is explicit: no-op for advisory runs, hold if any execution-style request or source degradation appears.",
            "rollback_note": "Primary rollback is to preserve the current continuity namespace stack unchanged and emit a held advisory receipt.",
            "resulting_advisory_posture": "ROLLBACK_DEFINED",
            "authority_granted": False,
        }
    )
    stages.append(
        {
            "stage_id": "FINAL_STATUS",
            "observed_inputs": [
                CONTINUITY_NAMESPACE_ALIAS_PLAN_PATH,
                CONTINUITY_NAMESPACE_TOOLING_REFRESH_RECEIPT_PATH,
            ],
            "intended_operation_class": "final_advisory_disposition",
            "blocked_authority": list(BLOCKED_ACTIONS),
            "success_criteria": "Runner ends with a deterministic advisory receipt and no mutation side effects.",
            "rollback_note": blocked_posture["reason"],
            "resulting_advisory_posture": blocked_posture["result"],
            "authority_granted": False,
        }
    )
    return stages


def build_continuity_namespace_migration_run_receipt(
    *,
    repo_root: str | Path = ".",
    requested_mode: str = "advisory",
) -> dict[str, Any]:
    root = Path(repo_root)
    source_status_table = [_source_row(root, path) for path in SOURCE_PATHS]
    payloads, statuses = _payloads_and_statuses(root)
    stack_ready = _stack_ready(payloads, statuses)
    blocked_posture = _blocked_execution_posture(requested_mode, stack_ready)
    run_stage_rows = _stage_rows(
        payloads,
        statuses,
        requested_mode=requested_mode,
        stack_ready=stack_ready,
    )

    source_status = (
        "NOT_COMPUTABLE"
        if not any(row.get("source_status") == "OBSERVED" for row in source_status_table)
        else "READY_WITH_FINDINGS"
        if not stack_ready or blocked_posture["result"] == "HELD"
        else "READY"
    )

    packet: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "slice_id": SLICE_ID,
        "migration_run_id": MIGRATION_RUN_ID,
        "advisory_only": True,
        "projection_only": True,
        "notion_board_url": NOTION_BOARD_URL,
        "authority_locks": AUTHORITY_LOCKS,
        "boundary": {
            "sandbox_gate_issue": "#892",
            "sandbox_gate_phrase": "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED",
            "sandbox_gate_issued": False,
            "canon_mutation": False,
            "external_calls": False,
            "github_writeback": False,
            "mcp_exposure": False,
            "notion_writeback": False,
            "runtime_activation": False,
        },
        "source_status": source_status,
        "source_status_table": source_status_table,
        "source_invariants": _source_invariants(payloads),
        "requested_mode": requested_mode,
        "requested_execution_posture": blocked_posture,
        "run_stage_rows": run_stage_rows,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "safe_next_surface": payloads.get("readiness_review", {}).get(
            "safe_next_surface_recommendation", "NOT_COMPUTABLE"
        ),
        "recommended_next_engineering_move": (
            "Additive alias implementation design slice"
            if stack_ready
            else "Continuity namespace source repair or packaging follow-up"
        ),
        "recommended_next_engineering_reason": (
            "The continuity namespace stack is present and deterministic, but implementation authority is still closed so the next safe move remains design-only."
            if stack_ready
            else "One or more required continuity namespace sources are degraded or missing, so additional source/package repair is safer than new migration design."
        ),
        "run_summary": {
            "stack_ready": stack_ready,
            "execution_request_held": blocked_posture["result"] == "HELD",
            "selected_policy": payloads.get("alias_plan", {}).get(
                "selected_policy", "NOT_COMPUTABLE"
            ),
            "safe_next_surface": payloads.get("readiness_review", {}).get(
                "safe_next_surface_recommendation", "NOT_COMPUTABLE"
            ),
            "authority_granted": False,
        },
        "doc_path": RUNNER_DOC_PATH,
        "touched_docs": [
            "README.md",
            "PLANS.md",
            "docs/START_HERE.md",
            "docs/INDEX.md",
            "docs/artifacts/ARTIFACT_INDEX.md",
            RUNNER_DOC_PATH,
        ],
        "validation_plan": [
            "python scripts/temporal/run_continuity_namespace_migration_runner.py",
            "python scripts/artifact/run_artifact_regeneration.py --artifact out/audit/continuity_namespace_migration_run_001.latest.json",
            "python -m py_compile core/continuity_namespace_migration_runner.py scripts/temporal/run_continuity_namespace_migration_runner.py tests/test_continuity_namespace_migration_runner.py",
            "python -m pytest tests/test_continuity_namespace_migration_runner.py tests/test_generated_artifact_registry.py -q -k continuity_namespace_migration_runner",
            "git diff --check",
        ],
        "notion_closeout_text": (
            "Slice63 complete - Receipt-driven continuity namespace migration runner shipped as an advisory simulation layer; stack inventory, alias scaffolding, route rewrite scaffolding, receipt rebinding scaffolding, and rollback posture now route through one deterministic run receipt; no sandbox probe, runtime activation, canon mutation, MCP exposure, external calls, or autonomous writeback authorized. Brier Score: 0.10."
        ),
        "provenance": "Notion Sprint 001 Hub + Loop 805 Slice63 + Hash: canonical_hash",
    }
    packet["canonical_hash"] = canonical_hash(packet)
    return packet


def write_continuity_namespace_migration_run_receipt(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
