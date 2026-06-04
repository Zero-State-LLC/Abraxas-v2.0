from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "NotionWritebackAuthorizationGate.v1"
GATE_ID = "NOTION_WRITEBACK_AUTHORIZATION_GATE_001"
OUT_JSON = "out/sync/notion_writeback_authorization_gate/latest.json"
OUT_MD = "out/sync/notion_writeback_authorization_gate/latest.md"
DRY_RUN_PLAN_PATH = "out/sync/notion_writeback_dry_run_plan/latest.json"
DEFAULT_OPERATOR_AUTHORIZATION_PATH = "input/notion_writeback_operator_authorization.json"

_NOT_COMPUTABLE = "NOT_COMPUTABLE"
_REQUIRED_OPERATOR_DECISION = "APPROVE_NOTION_WRITEBACK_DRY_RUN_TO_MUTATION_GATE"


def _read_json(repo_root: Path, rel_path: str) -> dict[str, Any]:
    try:
        parsed = json.loads((repo_root / rel_path).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _file_hash(repo_root: Path, rel_path: str) -> str:
    try:
        return hashlib.sha256((repo_root / rel_path).read_bytes()).hexdigest()
    except OSError:
        return _NOT_COMPUTABLE


def _dry_run_ready(dry_run_plan: dict[str, Any]) -> bool:
    return (
        dry_run_plan.get("artifact_type") == "NotionWritebackDryRunPlan.v1"
        and dry_run_plan.get("plan_status") == "DRY_RUN_PLAN_READY"
        and dry_run_plan.get("target_state") == "TARGET_CONFIGURED"
        and dry_run_plan.get("dry_run_only") is True
        and dry_run_plan.get("writeback_performed") is False
        and dry_run_plan.get("notion_writeback") is False
        and bool(dry_run_plan.get("planned_operations"))
    )


def _operator_authorization_valid(record: dict[str, Any]) -> bool:
    return (
        record.get("artifact_type") == "NotionWritebackOperatorAuthorization.v1"
        and record.get("operator_decision") == _REQUIRED_OPERATOR_DECISION
        and record.get("authorizes_live_writeback") is False
        and record.get("authorizes_mutation_gate_planning") is True
        and record.get("advisory_only") is True
    )


def _gate_status(dry_run_ready: bool, operator_authorization_valid: bool) -> str:
    if not dry_run_ready:
        return "NOT_COMPUTABLE"
    if not operator_authorization_valid:
        return "OPERATOR_AUTHORIZATION_REQUIRED"
    return "MUTATION_GATE_PLANNING_ELIGIBLE"


def build_notion_writeback_authorization_gate(
    *,
    repo_root: str | Path,
    dry_run_plan_path: str = DRY_RUN_PLAN_PATH,
    operator_authorization_path: str = DEFAULT_OPERATOR_AUTHORIZATION_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    dry_run_plan = _read_json(root, dry_run_plan_path)
    operator_record = _read_json(root, operator_authorization_path)
    dry_run_is_ready = _dry_run_ready(dry_run_plan)
    operator_record_valid = _operator_authorization_valid(operator_record)
    gate_status = _gate_status(dry_run_is_ready, operator_record_valid)

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "gate_id": GATE_ID,
        "gate_status": gate_status,
        "consumed_dry_run_plan_path": dry_run_plan_path,
        "operator_authorization_path": operator_authorization_path,
        "source_hashes": {
            dry_run_plan_path: _file_hash(root, dry_run_plan_path),
            operator_authorization_path: _file_hash(root, operator_authorization_path),
        },
        "dry_run_plan_ready": dry_run_is_ready,
        "operator_authorization_observed": bool(operator_record),
        "operator_authorization_valid": operator_record_valid,
        "required_operator_decision": _REQUIRED_OPERATOR_DECISION,
        "eligible_for_mutation_gate_planning": gate_status == "MUTATION_GATE_PLANNING_ELIGIBLE",
        "writeback_authorized": False,
        "writeback_performed": False,
        "notion_writeback": False,
        "mutation_gate_planning_only": True,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "valid_for_execution": False,
        "recommended_next_lane": (
            "NOTION_WRITEBACK_MUTATION_GATE_PLAN"
            if gate_status == "MUTATION_GATE_PLANNING_ELIGIBLE"
            else "NOT_COMPUTABLE"
        ),
        "authority_locks": {
            "canon_promotion": False,
            "execution_authority": False,
            "forecast_authority": False,
            "notion_mutation_authority": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "token_minting": False,
        },
        "blocked_actions": [
            "LIVE_NOTION_WRITEBACK",
            "CREATE_OR_UPDATE_NOTION_PAGE",
            "DELETE_NOTION_CONTENT",
            "MUTATE_DATABASE_SCHEMA",
            "AUTHORIZE_EXECUTION",
            "PROMOTE_CANON",
            "MUTATE_RUNTIME_OR_SCHEDULER",
        ],
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_notion_writeback_authorization_gate(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)


def write_notion_writeback_authorization_gate_markdown(path: str | Path, packet: dict[str, Any]) -> None:
    lines = [
        "# Notion Writeback Authorization Gate",
        "",
        f"- gate_id: {packet['gate_id']}",
        f"- gate_status: {packet['gate_status']}",
        f"- dry_run_plan_ready: {packet['dry_run_plan_ready']}",
        f"- operator_authorization_valid: {packet['operator_authorization_valid']}",
        f"- eligible_for_mutation_gate_planning: {packet['eligible_for_mutation_gate_planning']}",
        f"- writeback_authorized: {packet['writeback_authorized']}",
        f"- writeback_performed: {packet['writeback_performed']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        "",
        "## Source Hashes",
    ]
    hashes = packet.get("source_hashes", {})
    if isinstance(hashes, dict):
        for rel_path in sorted(hashes):
            lines.append(f"- {rel_path}: {hashes[rel_path]}")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
