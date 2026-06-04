from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.rune_registry_formalization_plan import OUT_JSON as RUNE_REGISTRY_FORMALIZATION_PLAN_JSON

ARTIFACT_TYPE = "NotionPatchQueueTerminalState.v1"
TERMINAL_STATE_ID = "NOTION_PATCH_QUEUE_TERMINAL_STATE_001"
OUT_JSON = "out/sync/notion_patch_queue_terminal_state/latest.json"
OUT_MD = "out/sync/notion_patch_queue_terminal_state/latest.md"

_NOT_COMPUTABLE = "NOT_COMPUTABLE"


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return _NOT_COMPUTABLE


def _load_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _formalization_plan_terminal(plan: dict[str, Any]) -> bool:
    return (
        plan.get("artifact_type") == "RuneRegistryFormalizationPlan.v1"
        and plan.get("plan_status") == "PLAN_EMITTED_ADVISORY_ONLY"
        and plan.get("recommended_next_patch") == _NOT_COMPUTABLE
        and plan.get("rune_registration_performed") is False
        and plan.get("catalog_mutation_performed") is False
        and plan.get("execution_dispatch_changed") is False
        and plan.get("valid_for_execution") is False
    )


def build_notion_patch_queue_terminal_state(
    *,
    repo_root: str | Path,
    rune_registry_formalization_plan_path: str | Path = RUNE_REGISTRY_FORMALIZATION_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    plan_target = root / rune_registry_formalization_plan_path
    formalization_plan = _load_json(plan_target)
    queue_is_terminal = _formalization_plan_terminal(formalization_plan)
    candidate_holds = sorted(str(item) for item in formalization_plan.get("candidate_holds", []))
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "terminal_state_id": TERMINAL_STATE_ID,
        "terminal_state_status": (
            "QUEUE_TERMINAL_STATE_EMITTED_ADVISORY_ONLY"
            if queue_is_terminal
            else _NOT_COMPUTABLE
        ),
        "notion_source": "ABRAXAS_PATCH_QUEUE_REVISED_001",
        "depends_on_patch": "PATCH-ABX-RUNE-REGISTRY-FORMALIZATION-PLAN-001",
        "consumed_rune_registry_formalization_plan_path": Path(
            rune_registry_formalization_plan_path
        ).as_posix(),
        "consumed_rune_registry_formalization_plan_hash": _sha256(plan_target),
        "queue_is_terminal": queue_is_terminal,
        "terminal_reason": (
            "rune registry formalization plan recommended_next_patch is NOT_COMPUTABLE"
            if queue_is_terminal
            else "terminal state cannot be proven from current queue evidence"
        ),
        "candidate_holds": candidate_holds,
        "required_operator_input": (
            "new Notion patch spec or explicit governed operator decision required"
            if queue_is_terminal
            else "repair queue evidence before continuation"
        ),
        "safe_to_auto_continue": False,
        "auto_patch_generation_allowed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "forecast_routing": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "recommended_next_patch": _NOT_COMPUTABLE,
        "recommended_next_lane": _NOT_COMPUTABLE,
        "blocked_actions": [
            "AUTO_CREATE_NEXT_PATCH",
            "LIVE_NOTION_WRITEBACK",
            "GITHUB_PUSH_OR_PR_CREATION",
            "RUNE_REGISTRATION",
            "PIPELINE_OR_ROUTE_MUTATION",
            "RUNTIME_OR_SCHEDULER_MUTATION",
            "CANON_PROMOTION",
        ],
        "authority_locks": {
            "auto_patch_generation": False,
            "canon_mutation": False,
            "execution_authority": False,
            "forecast_routing": False,
            "github_writeback": False,
            "notion_writeback": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "token_minting": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_notion_patch_queue_terminal_state(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)


def write_notion_patch_queue_terminal_state_markdown(path: str | Path, packet: dict[str, Any]) -> None:
    lines = [
        "# Notion Patch Queue Terminal State",
        "",
        f"- terminal_state_id: {packet['terminal_state_id']}",
        f"- terminal_state_status: {packet['terminal_state_status']}",
        f"- queue_is_terminal: {packet['queue_is_terminal']}",
        f"- terminal_reason: {packet['terminal_reason']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- auto_patch_generation_allowed: {packet['auto_patch_generation_allowed']}",
        f"- notion_writeback_allowed: {packet['notion_writeback_allowed']}",
        f"- github_writeback_allowed: {packet['github_writeback_allowed']}",
        f"- recommended_next_patch: {packet['recommended_next_patch']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        "",
        "## Candidate Holds",
    ]
    for rune_id in packet.get("candidate_holds", []):
        lines.append(f"- {rune_id}")
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- {action}")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
