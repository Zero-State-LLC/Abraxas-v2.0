from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_operator_authorization_evidence_request_plan import (
    PLAN_JSON_PATH as SOURCE_EVIDENCE_REQUEST_JSON,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygienePhase1FoundationBacklogPlan.v1"
PLAN_ID = "v2_hygiene_phase1_foundation_backlog_plan_001"
PLAN_JSON_PATH = Path(
    "out/sync/v2_hygiene_phase1_foundation_backlog_plan/latest.json"
)
PLAN_MD_PATH = PLAN_JSON_PATH.with_suffix(".md")

SOURCE_OPERATOR_GATE_JSON = (
    "out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.json"
)
SOURCE_REGISTRATION_READINESS_JSON = "out/sync/v2_hygiene_registration_readiness_audit/latest.json"

NOTION_PHASE1_SOURCES: tuple[dict[str, str], ...] = (
    {
        "page_id": "37e3e8ba-2f5c-81b0-8bd9-fe40510f2af3",
        "title": "Phase 1: Foundations & Hygiene Layer",
        "status": "READY_FOR_WORK",
        "source_observed_at": "2026-06-13T16:41:03Z",
    },
    {
        "page_id": "37e3e8ba-2f5c-8136-9cec-c0482fd71a8e",
        "title": "v2.0 Schema Contracts",
        "status": "TECHNICAL_REFERENCE_SURFACE",
        "source_observed_at": "2026-06-13T16:27:39Z",
    },
    {
        "page_id": "37e3e8ba-2f5c-816d-a703-cabbdbf431fc",
        "title": "Versioning & Release Hygiene Policy",
        "status": "ACTIVE_POLICY",
        "source_observed_at": "2026-06-13T16:26:28Z",
    },
    {
        "page_id": "56a5b080-8f17-4392-af50-55d19c174cc0",
        "title": "Phase 1 - Implementation Checklist",
        "status": "TASKS_TO_DO",
        "source_observed_at": "2026-06-13T16:34:45Z",
    },
)

PHASE1_TASKS: tuple[dict[str, str], ...] = (
    {
        "task_id": "phase1_p0_001",
        "priority": "P0",
        "task": "Set up folder structure",
        "deliverable": "abraxas/v2/hygiene folder layout",
        "repo_path": "abraxas/v2/hygiene",
    },
    {
        "task_id": "phase1_p0_002",
        "priority": "P0",
        "task": "Implement LoopDynamics",
        "deliverable": "LoopDynamics dataclass and validation",
        "repo_path": "abraxas/v2/hygiene/loop_dynamics.py",
    },
    {
        "task_id": "phase1_p0_003",
        "priority": "P0",
        "task": "Implement V2Output",
        "deliverable": "three-register output wrapper",
        "repo_path": "abraxas/v2/hygiene/registers.py",
    },
    {
        "task_id": "phase1_p0_004",
        "priority": "P0",
        "task": "Create V2HygieneRune base class",
        "deliverable": "abstract base with apply contract",
        "repo_path": "abraxas/v2/hygiene/contracts/v2_hygiene_rune_base.py",
    },
    {
        "task_id": "phase1_p0_005",
        "priority": "P0",
        "task": "Implement HygieneMode system",
        "deliverable": "OFF / ADVISORY / STRICT mode enum",
        "repo_path": "abraxas/v2/governance/mode.py",
    },
    {
        "task_id": "phase1_p0_006",
        "priority": "P0",
        "task": "Implement LoopAwarenessRune",
        "deliverable": "loop awareness rune and tests",
        "repo_path": "abraxas/v2/hygiene/runes/loop_awareness.py",
    },
    {
        "task_id": "phase1_p1_007",
        "priority": "P1",
        "task": "Implement ProvenanceEnforceRune",
        "deliverable": "provenance enforcement rune and tests",
        "repo_path": "abraxas/v2/hygiene/runes/provenance_enforce.py",
    },
    {
        "task_id": "phase1_p1_008",
        "priority": "P1",
        "task": "Add JSON schema validation",
        "deliverable": "schema loader and validation helpers",
        "repo_path": "abraxas/v2/hygiene/contracts/schema_validator.py",
    },
    {
        "task_id": "phase1_p1_009",
        "priority": "P1",
        "task": "Write unit tests for core objects",
        "deliverable": "tests under tests/v2/hygiene",
        "repo_path": "tests/v2/hygiene",
    },
    {
        "task_id": "phase1_p1_010",
        "priority": "P1",
        "task": "Implement remaining 3 runes",
        "deliverable": "hyperstition, adversarial audit, output register runes",
        "repo_path": "abraxas/v2/hygiene/runes",
    },
    {
        "task_id": "phase1_p2_011",
        "priority": "P2",
        "task": "Add advisory integration hook",
        "deliverable": "feature-flagged advisory integration example",
        "repo_path": "abraxas/v2/hygiene/pipeline.py",
    },
    {
        "task_id": "phase1_p2_012",
        "priority": "P2",
        "task": "Create schema files",
        "deliverable": "loop_dynamics and output_register schemas",
        "repo_path": "abraxas/v2/hygiene/contracts/schemas",
    },
    {
        "task_id": "phase1_p2_013",
        "priority": "P2",
        "task": "Documentation and examples",
        "deliverable": "docstrings and minimal usage example",
        "repo_path": "examples/v2_hygiene_integration.py",
    },
    {
        "task_id": "phase1_p2_014",
        "priority": "P2",
        "task": "Final review and cleanup",
        "deliverable": "versioning and advisory-mode review",
        "repo_path": "out/operator_review/v2_hygiene_phase1_final_review_001.latest.json",
    },
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _hash_source(path: Path) -> str:
    value = _read_json(path)
    return canonical_hash(value) if value else NOT_COMPUTABLE


def _notion_source_records() -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for source in NOTION_PHASE1_SOURCES:
        record = dict(source)
        record["source_hash"] = canonical_hash(source)
        records.append(record)
    return records


def _task_records(repo_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for task in PHASE1_TASKS:
        target = repo_root / task["repo_path"]
        repo_observed = target.exists()
        records.append(
            {
                **task,
                "repo_observed": repo_observed,
                "implementation_status": (
                    "REPO_PATH_OBSERVED_HELD_FOR_OPERATOR"
                    if repo_observed
                    else "NOTION_TASK_TO_DO_HELD_FOR_OPERATOR"
                ),
                "implementation_authorized": False,
                "execution_authority": False,
            }
        )
    return records


def _authority_locks() -> dict[str, bool]:
    return {
        "activation": False,
        "advisory_integration_hook_authorized": False,
        "auto_continuation": False,
        "auto_patch_generation": False,
        "canon_mutation": False,
        "execution_authority": False,
        "github_writeback": False,
        "hygiene_code_creation": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_authorization_record_creation": False,
        "projection_surface_mutation": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_file_creation": False,
        "schema_mutation": False,
        "strict_mode_enablement": False,
        "token_minting": False,
        "v2_module_registration": False,
    }


def build_v2_hygiene_phase1_foundation_backlog_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    source_paths = {
        "operator_evidence_request_plan": str(SOURCE_EVIDENCE_REQUEST_JSON),
        "operator_authorization_gate": SOURCE_OPERATOR_GATE_JSON,
        "registration_readiness_audit": SOURCE_REGISTRATION_READINESS_JSON,
    }
    source_packets = {key: _read_json(root / path) for key, path in source_paths.items()}
    evidence_request = source_packets["operator_evidence_request_plan"] or {}
    gate = source_packets["operator_authorization_gate"] or {}
    registration = source_packets["registration_readiness_audit"] or {}
    source_ready = (
        evidence_request.get("status")
        == "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_REQUEST_PLAN_READY"
        and evidence_request.get("implementation_authorized") is False
        and evidence_request.get("v2_module_registration_authorized") is False
        and evidence_request.get("rune_registration_authorized") is False
        and gate.get("authorization_granted") is False
        and gate.get("valid_for_implementation") is False
        and registration.get("valid_for_implementation") is False
    )
    task_records = _task_records(root)
    blocked_task_count = sum(
        1 for task in task_records if task["implementation_authorized"] is False
    )
    blockers = [] if source_ready else ["v2_hygiene_operator_evidence_sources_not_ready"]

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "V2_HYGIENE_PHASE1_FOUNDATION_BACKLOG_PLAN_READY"
            if source_ready
            else "V2_HYGIENE_PHASE1_FOUNDATION_BACKLOG_PLAN_BLOCKED"
        ),
        "plan_id": PLAN_ID,
        "plan_hash": "",
        "source_paths": source_paths,
        "source_hashes": {
            key: _hash_source(root / path) for key, path in source_paths.items()
        },
        "source_ready": source_ready,
        "notion_phase1_sources": _notion_source_records(),
        "phase1_goal": (
            "Map Notion Phase 1 hygiene foundation tasks into repo-visible advisory backlog "
            "without creating v2 hygiene implementation files or granting authority."
        ),
        "task_records": task_records,
        "task_summary": {
            "total_task_count": len(task_records),
            "p0_task_count": sum(1 for task in task_records if task["priority"] == "P0"),
            "p1_task_count": sum(1 for task in task_records if task["priority"] == "P1"),
            "p2_task_count": sum(1 for task in task_records if task["priority"] == "P2"),
            "repo_observed_task_count": sum(1 for task in task_records if task["repo_observed"]),
            "blocked_task_count": blocked_task_count,
        },
        "acceptance_gate_summary": {
            "operator_authorization_required": True,
            "operator_authorization_observed": False,
            "operator_evidence_request_ready": source_ready,
            "safe_to_create_hygiene_code": False,
            "safe_to_create_schema_files": False,
            "safe_to_register_modules_or_runes": False,
            "safe_to_enable_strict_mode": False,
        },
        "recommended_next_action": (
            "keep the Phase 1 hygiene foundation as a repo-visible backlog until explicit "
            "external operator authorization evidence permits a separate implementation "
            "record lane"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "implementation_authorized": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_prepare_patch": False,
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "authority_locks": _authority_locks(),
        "blockers": blockers,
    }
    packet["plan_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "plan_hash"}
    )
    return packet


def render_v2_hygiene_phase1_foundation_backlog_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Phase 1 Foundation Backlog Plan",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `source_ready`: `{packet['source_ready']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        f"- `implementation_authorized`: `{packet['implementation_authorized']}`",
        f"- `valid_for_execution`: `{packet['valid_for_execution']}`",
        "",
        "## Task Summary",
        "",
    ]
    summary = packet["task_summary"]
    for key in [
        "total_task_count",
        "p0_task_count",
        "p1_task_count",
        "p2_task_count",
        "repo_observed_task_count",
        "blocked_task_count",
    ]:
        lines.append(f"- `{key}`: `{summary[key]}`")
    lines.extend(["", "## Phase 1 Tasks", ""])
    for task in packet["task_records"]:
        lines.append(
            f"- `{task['task_id']}` {task['task']}: "
            f"`{task['implementation_status']}`"
        )
    if packet["blockers"]:
        lines.extend(["", "## Blockers", ""])
        for blocker in packet["blockers"]:
            lines.append(f"- `{blocker}`")
    return lines


def write_v2_hygiene_phase1_foundation_backlog_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_v2_hygiene_phase1_foundation_backlog_plan(root)
    write_canonical_json(target_root / PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / PLAN_MD_PATH,
        render_v2_hygiene_phase1_foundation_backlog_plan_markdown(packet),
    )
    return packet
