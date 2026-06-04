from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.notion_spec_completion_queue import OUT_JSON as COMPLETION_QUEUE_JSON

ARTIFACT_TYPE = "NotionOperatorDecisionBacklog.v1"
BACKLOG_ID = "NOTION_OPERATOR_DECISION_BACKLOG_001"
OUT_JSON = "out/sync/notion_operator_decision_backlog/latest.json"
OUT_MD = "out/sync/notion_operator_decision_backlog/latest.md"

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


def _queue_terminal(queue_packet: dict[str, Any]) -> bool:
    return (
        queue_packet.get("artifact_type") == "NotionSpecCompletionQueue.v1"
        and queue_packet.get("queue_status") == "COMPLETION_QUEUE_EMITTED_ADVISORY_ONLY"
        and queue_packet.get("recommended_next_patch") == _NOT_COMPUTABLE
        and queue_packet.get("safe_to_prepare_planning_pr") is False
        and queue_packet.get("safe_to_auto_continue") is False
        and queue_packet.get("valid_for_execution") is False
    )


def _decision_scope(required_inputs: list[str]) -> str:
    joined = " ".join(required_inputs)
    if "separate implementation spec" in joined:
        return "IMPLEMENTATION_SPEC_DECISION_REQUIRED"
    if "fresh Notion patch spec" in joined:
        return "NOTION_SPEC_REFRESH_REQUIRED"
    return "GOVERNED_OPERATOR_DECISION_REQUIRED"


def _decision_backlog(queue_packet: dict[str, Any]) -> list[dict[str, Any]]:
    backlog: list[dict[str, Any]] = []
    queue = queue_packet.get("completion_queue", [])
    if not isinstance(queue, list):
        return backlog
    blocked_items = [
        item
        for item in queue
        if isinstance(item, dict)
        and item.get("implementation_blocked") is True
        and item.get("queue_action") == "HOLD_FOR_GOVERNED_OPERATOR_DECISION"
    ]
    for rank, item in enumerate(blocked_items, start=1):
        required_inputs = [str(value) for value in item.get("required_evidence", [])]
        backlog.append(
            {
                "backlog_rank": rank,
                "queue_rank": int(item.get("queue_rank", rank)),
                "notion_surface": str(item.get("notion_surface", "")),
                "decision_scope": _decision_scope(required_inputs),
                "source_completion_status": "BLOCKED",
                "source_match_strength": str(item.get("match_strength", _NOT_COMPUTABLE)),
                "queue_action": "HOLD_FOR_GOVERNED_OPERATOR_DECISION",
                "required_inputs": required_inputs,
                "recommended_action": str(item.get("recommended_action", "")),
                "observed_paths": sorted(str(path) for path in item.get("observed_paths", [])),
                "missing_paths": sorted(str(path) for path in item.get("missing_paths", [])),
            }
        )
    return backlog


def build_notion_operator_decision_backlog(
    *,
    repo_root: str | Path,
    completion_queue_path: str | Path = COMPLETION_QUEUE_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    queue_target = root / completion_queue_path
    queue_packet = _load_json(queue_target)
    queue_observed = queue_packet.get("artifact_type") == "NotionSpecCompletionQueue.v1"
    queue_terminal = _queue_terminal(queue_packet)
    decision_backlog = _decision_backlog(queue_packet)
    top_priority_surface = (
        str(decision_backlog[0]["notion_surface"]) if decision_backlog else _NOT_COMPUTABLE
    )
    top_priority_required_inputs = (
        list(decision_backlog[0]["required_inputs"]) if decision_backlog else []
    )
    backlog_ready = queue_observed and queue_terminal and bool(decision_backlog)
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "backlog_id": BACKLOG_ID,
        "backlog_status": (
            "OPERATOR_DECISION_BACKLOG_EMITTED_ADVISORY_ONLY" if backlog_ready else _NOT_COMPUTABLE
        ),
        "notion_source": "ABRAXAS_PATCH_QUEUE_REVISED_001",
        "depends_on_artifacts": [Path(completion_queue_path).as_posix()],
        "source_artifact_hashes": {Path(completion_queue_path).as_posix(): _sha256(queue_target)},
        "queue_observed": queue_observed,
        "queue_terminal": queue_terminal,
        "blocked_surface_count": len(decision_backlog),
        "decision_backlog": decision_backlog,
        "top_priority_surface": top_priority_surface,
        "top_priority_required_inputs": top_priority_required_inputs,
        "recommended_next_patch": _NOT_COMPUTABLE,
        "recommended_next_action": (
            f"collect governed operator input for {top_priority_surface}"
            if backlog_ready
            else "repair operator decision backlog evidence"
        ),
        "safe_to_prepare_planning_pr": False,
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
        "blocked_actions": [
            "AUTO_CREATE_NEXT_PATCH",
            "LIVE_NOTION_WRITEBACK",
            "GITHUB_PUSH_OR_PR_CREATION",
            "SUBSYSTEM_IMPLEMENTATION",
            "PIPELINE_OR_ROUTE_MUTATION",
            "RUNTIME_OR_SCHEDULER_MUTATION",
            "CANON_PROMOTION",
            "EXECUTION_AUTHORITY_GRANT",
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


def write_notion_operator_decision_backlog(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)


def write_notion_operator_decision_backlog_markdown(path: str | Path, packet: dict[str, Any]) -> None:
    lines = [
        "# Notion Operator Decision Backlog",
        "",
        f"- backlog_id: {packet['backlog_id']}",
        f"- backlog_status: {packet['backlog_status']}",
        f"- queue_observed: {packet['queue_observed']}",
        f"- queue_terminal: {packet['queue_terminal']}",
        f"- blocked_surface_count: {packet['blocked_surface_count']}",
        f"- top_priority_surface: {packet['top_priority_surface']}",
        f"- recommended_next_action: {packet['recommended_next_action']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- notion_writeback_allowed: {packet['notion_writeback_allowed']}",
        f"- github_writeback_allowed: {packet['github_writeback_allowed']}",
        "",
        "## Decision Backlog",
    ]
    for item in packet.get("decision_backlog", []):
        lines.append(
            "- "
            f"{item['backlog_rank']}. {item['notion_surface']} "
            f"[{item['decision_scope']}] -> {item['recommended_action']}"
        )
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
