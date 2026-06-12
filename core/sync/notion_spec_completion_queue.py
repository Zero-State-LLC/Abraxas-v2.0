from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.repo_notion_diff import OUT_JSON as REPO_NOTION_DIFF_JSON
from core.sync.global_ingest_adapter_spine_alignment_plan import OUT_JSON as GLOBAL_INGEST_PLAN_JSON
from core.sync.notion_patch_queue_terminal_state import OUT_JSON as TERMINAL_STATE_JSON

ARTIFACT_TYPE = "NotionSpecCompletionQueue.v1"
QUEUE_ID = "NOTION_SPEC_COMPLETION_QUEUE_001"
OUT_JSON = "out/sync/notion_spec_completion_queue/latest.json"
OUT_MD = "out/sync/notion_spec_completion_queue/latest.md"
GLOBAL_INGEST_DECISION_RECORD_JSON = "out/operator_review/global_ingest_operator_decision_record_001.latest.json"
GLOBAL_INGEST_IMPLEMENTATION_SPEC_JSON = (
    "out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.json"
)

_NOT_COMPUTABLE = "NOT_COMPUTABLE"
_NEXT_PATCH = "PATCH-ABX-GLOBAL-INGEST-ADAPTER-SPINE-ALIGNMENT-PLAN-001"
_NEXT_ACTION = (
    "prepare an advisory alignment plan for Global Ingest Adapter Spine before any "
    "core/oracle_signal.py implementation"
)


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


def _completion_status(record: dict[str, Any]) -> str:
    if record.get("governed_hold") is True:
        return "GOVERNED_HOLD"
    if record.get("implementation_blocked") is True:
        return "BLOCKED"
    match_strength = record.get("match_strength")
    if match_strength == "EXACT":
        return "OBSERVED"
    if match_strength == "PARTIAL":
        return "PARTIAL"
    return "MISSING"


def _eligible_for_planning(record: dict[str, Any]) -> bool:
    return (
        record.get("implementation_blocked") is not True
        and record.get("governed_hold") is not True
        and record.get("match_strength") in {"PARTIAL", "MISSING"}
    )


def _queue_action(record: dict[str, Any]) -> str:
    surface = str(record.get("notion_surface", ""))
    if record.get("governed_hold") is True:
        return "HOLD_FOR_GOVERNED_OPERATOR_DECISION"
    if record.get("implementation_blocked") is True:
        return "HOLD_FOR_GOVERNED_OPERATOR_DECISION"
    if surface == "Global Ingest Adapter Spine" and record.get("match_strength") == "PARTIAL":
        return "PREPARE_ADVISORY_ALIGNMENT_PLAN"
    if record.get("match_strength") == "EXACT":
        return "PRESERVE_OBSERVED_SURFACE"
    return "PLAN_BEFORE_IMPLEMENTATION"


def _required_evidence(record: dict[str, Any]) -> list[str]:
    missing_paths = [str(path) for path in record.get("missing_paths", [])]
    if record.get("governed_hold") is True or record.get("implementation_blocked") is True:
        return ["explicit governed operator decision", "fresh Notion patch spec"]
    if missing_paths:
        return [f"planning evidence for {path}" for path in missing_paths]
    return ["no additional implementation evidence required"]


def _sort_key(record: dict[str, Any]) -> tuple[int, str]:
    if record.get("notion_surface") == "Global Ingest Adapter Spine":
        return (0, str(record.get("notion_surface", "")))
    if _eligible_for_planning(record):
        return (1, str(record.get("notion_surface", "")))
    if record.get("implementation_blocked") is True or record.get("governed_hold") is True:
        return (2, str(record.get("notion_surface", "")))
    return (3, str(record.get("notion_surface", "")))


def _global_ingest_plan_hold(plan: dict[str, Any]) -> bool:
    return (
        plan.get("artifact_type") == "GlobalIngestAdapterSpineAlignmentPlan.v1"
        and plan.get("patch_id") == _NEXT_PATCH
        and plan.get("plan_status") == "ALIGNMENT_PLAN_EMITTED_ADVISORY_ONLY"
        and plan.get("recommended_next_patch") == _NOT_COMPUTABLE
        and plan.get("implementation_allowed") is False
        and plan.get("valid_for_execution") is False
    )


def _global_ingest_spec_ready(decision_record: dict[str, Any], implementation_spec: dict[str, Any]) -> bool:
    return (
        decision_record.get("status") == "GLOBAL_INGEST_OPERATOR_DECISION_RECORDED"
        and decision_record.get("selected_decision") == "APPROVE_SEPARATE_IMPLEMENTATION_SPEC"
        and decision_record.get("implementation_spec_authoring_approved") is True
        and decision_record.get("implementation_authorized") is False
        and decision_record.get("execution_authority") is False
        and implementation_spec.get("status") == "GLOBAL_INGEST_ADAPTER_SPINE_IMPLEMENTATION_SPEC_READY"
        and implementation_spec.get("spec_authoring_allowed") is True
        and implementation_spec.get("implementation_authorized") is False
        and implementation_spec.get("execution_authority") is False
    )


def _global_ingest_queue_item(
    record: dict[str, Any],
    plan: dict[str, Any],
    decision_record: dict[str, Any],
    implementation_spec: dict[str, Any],
) -> dict[str, Any]:
    spec_ready = _global_ingest_spec_ready(decision_record, implementation_spec)
    if spec_ready:
        return {
            "notion_surface": str(record.get("notion_surface", "")),
            "completion_status": "BLOCKED",
            "match_strength": str(record.get("match_strength", _NOT_COMPUTABLE)),
            "duplicate_risk": str(record.get("duplicate_risk", "LOW")),
            "implementation_blocked": True,
            "governed_hold": False,
            "hold_reason": "NOT_APPLICABLE",
            "eligible_for_planning": False,
            "observed_paths": sorted(str(path) for path in record.get("observed_paths", [])),
            "missing_paths": sorted(str(path) for path in record.get("missing_paths", [])),
            "recommended_action": str(
                implementation_spec.get(
                    "recommended_next_action",
                    "prepare additive shadow contracts only; keep implementation and execution denied",
                )
            ),
            "queue_action": "SPEC_AUTHORING_APPROVED_IMPLEMENTATION_HELD",
            "required_evidence": [
                str(decision_record.get("decision_record_id", "global_ingest_operator_decision_record_001")),
                str(implementation_spec.get("spec_id", "global_ingest_adapter_spine_implementation_spec_001")),
            ],
        }
    return {
        "notion_surface": str(record.get("notion_surface", "")),
        "completion_status": "BLOCKED",
        "match_strength": str(record.get("match_strength", _NOT_COMPUTABLE)),
        "duplicate_risk": str(record.get("duplicate_risk", "LOW")),
        "implementation_blocked": True,
        "governed_hold": False,
        "hold_reason": "NOT_APPLICABLE",
        "eligible_for_planning": False,
        "observed_paths": sorted(str(path) for path in record.get("observed_paths", [])),
        "missing_paths": sorted(str(path) for path in record.get("missing_paths", [])),
        "recommended_action": str(
            plan.get(
                "recommended_next_action",
                "hold for explicit governed operator decision before any Global Ingest implementation",
            )
        ),
        "queue_action": "HOLD_FOR_GOVERNED_OPERATOR_DECISION",
        "required_evidence": [str(plan.get("required_operator_input", "explicit governed operator decision"))],
    }


def _completion_queue(
    diff_packet: dict[str, Any],
    global_ingest_plan: dict[str, Any],
    decision_record: dict[str, Any],
    implementation_spec: dict[str, Any],
) -> list[dict[str, Any]]:
    records = diff_packet.get("diff_records", [])
    if not isinstance(records, list):
        records = []
    sorted_records = sorted(
        (record for record in records if isinstance(record, dict)),
        key=_sort_key,
    )
    queue: list[dict[str, Any]] = []
    global_ingest_hold = _global_ingest_plan_hold(global_ingest_plan)
    for rank, record in enumerate(sorted_records, start=1):
        if global_ingest_hold and record.get("notion_surface") == "Global Ingest Adapter Spine":
            item = _global_ingest_queue_item(record, global_ingest_plan, decision_record, implementation_spec)
        else:
            item = {
                "notion_surface": str(record.get("notion_surface", "")),
                "completion_status": _completion_status(record),
                "match_strength": str(record.get("match_strength", _NOT_COMPUTABLE)),
                "duplicate_risk": str(record.get("duplicate_risk", "LOW")),
                "implementation_blocked": bool(record.get("implementation_blocked", False)),
                "governed_hold": bool(record.get("governed_hold", False)),
                "hold_reason": str(record.get("hold_reason", "NOT_APPLICABLE")),
                "eligible_for_planning": _eligible_for_planning(record),
                "observed_paths": sorted(str(path) for path in record.get("observed_paths", [])),
                "missing_paths": sorted(str(path) for path in record.get("missing_paths", [])),
                "recommended_action": str(record.get("recommended_action", "")),
                "queue_action": _queue_action(record),
                "required_evidence": _required_evidence(record),
            }
        queue.append({"queue_rank": rank, **item})
    return queue


def build_notion_spec_completion_queue(
    *,
    repo_root: str | Path,
    terminal_state_path: str | Path = TERMINAL_STATE_JSON,
    repo_notion_diff_path: str | Path = REPO_NOTION_DIFF_JSON,
    global_ingest_plan_path: str | Path = GLOBAL_INGEST_PLAN_JSON,
    global_ingest_decision_record_path: str | Path = GLOBAL_INGEST_DECISION_RECORD_JSON,
    global_ingest_implementation_spec_path: str | Path = GLOBAL_INGEST_IMPLEMENTATION_SPEC_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    terminal_target = root / terminal_state_path
    diff_target = root / repo_notion_diff_path
    global_ingest_target = root / global_ingest_plan_path
    decision_record_target = root / global_ingest_decision_record_path
    implementation_spec_target = root / global_ingest_implementation_spec_path
    terminal_state = _load_json(terminal_target)
    diff_packet = _load_json(diff_target)
    global_ingest_plan = _load_json(global_ingest_target)
    decision_record = _load_json(decision_record_target)
    implementation_spec = _load_json(implementation_spec_target)
    terminal_observed = (
        terminal_state.get("artifact_type") == "NotionPatchQueueTerminalState.v1"
        and terminal_state.get("queue_is_terminal") is True
    )
    diff_observed = (
        diff_packet.get("artifact_type") == "RepoNotionDiffPacket.v1"
        and diff_packet.get("diff_status") == "EMITTED_ADVISORY_ONLY"
    )
    global_ingest_hold = _global_ingest_plan_hold(global_ingest_plan)
    global_ingest_spec_ready = _global_ingest_spec_ready(decision_record, implementation_spec)
    queue = _completion_queue(diff_packet, global_ingest_plan, decision_record, implementation_spec)
    planning_candidates = [item for item in queue if item["eligible_for_planning"] is True]
    recommended_next_patch = (
        _NEXT_PATCH if terminal_observed and diff_observed and planning_candidates else _NOT_COMPUTABLE
    )
    if recommended_next_patch != _NOT_COMPUTABLE:
        recommended_next_action = _NEXT_ACTION
    elif global_ingest_hold:
        if global_ingest_spec_ready:
            recommended_next_action = str(
                implementation_spec.get(
                    "recommended_next_action",
                    "prepare additive shadow contracts only; keep implementation and execution denied",
                )
            )
        else:
            recommended_next_action = str(
                global_ingest_plan.get(
                    "recommended_next_action",
                    "hold for explicit governed operator decision before any Global Ingest implementation",
                )
            )
    else:
        recommended_next_action = "repair completion queue evidence"
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "queue_id": QUEUE_ID,
        "queue_status": (
            "COMPLETION_QUEUE_EMITTED_ADVISORY_ONLY"
            if terminal_observed and diff_observed
            else _NOT_COMPUTABLE
        ),
        "notion_source": "ABRAXAS_PATCH_QUEUE_REVISED_001",
        "depends_on_artifacts": [
            Path(terminal_state_path).as_posix(),
            Path(repo_notion_diff_path).as_posix(),
            Path(global_ingest_plan_path).as_posix(),
        ],
        "source_artifact_hashes": {
            Path(terminal_state_path).as_posix(): _sha256(terminal_target),
            Path(repo_notion_diff_path).as_posix(): _sha256(diff_target),
            Path(global_ingest_plan_path).as_posix(): _sha256(global_ingest_target),
        },
        "terminal_queue_observed": terminal_observed,
        "repo_notion_diff_observed": diff_observed,
        "completion_queue": queue,
        "blocked_surfaces": sorted(
            item["notion_surface"] for item in queue if item["implementation_blocked"] is True
        ),
        "governed_hold_surfaces": sorted(
            item["notion_surface"] for item in queue if item["governed_hold"] is True
        ),
        "recommended_next_patch": recommended_next_patch,
        "recommended_next_action": recommended_next_action,
        "recommended_next_lane": _NOT_COMPUTABLE,
        "safe_to_prepare_planning_pr": recommended_next_patch != _NOT_COMPUTABLE,
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


def write_notion_spec_completion_queue(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)


def write_notion_spec_completion_queue_markdown(path: str | Path, packet: dict[str, Any]) -> None:
    lines = [
        "# Notion Spec Completion Queue",
        "",
        f"- queue_id: {packet['queue_id']}",
        f"- queue_status: {packet['queue_status']}",
        f"- terminal_queue_observed: {packet['terminal_queue_observed']}",
        f"- repo_notion_diff_observed: {packet['repo_notion_diff_observed']}",
        f"- recommended_next_patch: {packet['recommended_next_patch']}",
        f"- recommended_next_action: {packet['recommended_next_action']}",
        f"- safe_to_prepare_planning_pr: {packet['safe_to_prepare_planning_pr']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- notion_writeback_allowed: {packet['notion_writeback_allowed']}",
        f"- github_writeback_allowed: {packet['github_writeback_allowed']}",
        "",
        "## Completion Queue",
    ]
    for item in packet.get("completion_queue", []):
        lines.append(
            "- "
            f"{item['queue_rank']}. {item['notion_surface']} "
            f"[{item['completion_status']}] -> {item['queue_action']}"
        )
    lines.extend(["", "## Blocked Surfaces"])
    for surface in packet.get("blocked_surfaces", []):
        lines.append(f"- {surface}")
    lines.extend(["", "## Governed Hold Surfaces"])
    for surface in packet.get("governed_hold_surfaces", []):
        lines.append(f"- {surface}")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
