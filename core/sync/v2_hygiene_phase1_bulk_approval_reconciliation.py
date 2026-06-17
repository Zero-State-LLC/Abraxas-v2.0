from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "V2HygienePhase1BulkApprovalReconciliation.v1"
RECONCILIATION_ID = "V2_HYGIENE_PHASE1_BULK_APPROVAL_RECONCILIATION_001"
OUT_JSON = Path(
    "out/operator_review/v2_hygiene_phase1_bulk_approval_reconciliation_001.latest.json"
)
OUT_MD = OUT_JSON.with_suffix(".md")
NOT_COMPUTABLE = "NOT_COMPUTABLE"

SOURCE_PHASE1_BACKLOG = "out/sync/v2_hygiene_phase1_foundation_backlog_plan/latest.json"
SOURCE_OPERATOR_GATE = (
    "out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.json"
)
SOURCE_BULK_DISPOSITION = (
    "out/operator_review/operator_review_required_items_bulk_disposition_001.latest.json"
)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _source_record(repo_root: Path, path: str, expected_status: str, status_field: str) -> dict[str, Any]:
    packet = _read_json(repo_root / path)
    observed_status = str(packet.get(status_field, NOT_COMPUTABLE))
    return {
        "path": path,
        "status_field": status_field,
        "expected_status": expected_status,
        "observed_status": observed_status,
        "source_observed": bool(packet),
        "status_matches_expected": observed_status == expected_status,
        "source_hash": canonical_hash(packet) if packet else NOT_COMPUTABLE,
    }


def _authority_locks() -> dict[str, bool]:
    return {
        "activation": False,
        "auto_continuation": False,
        "auto_patch_generation": False,
        "canon_mutation": False,
        "code_creation": False,
        "execution_authority": False,
        "github_writeback": False,
        "hygiene_code_creation": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_authorization_record_creation": False,
        "operator_evidence_bundle_creation": False,
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


def _phase1_task_effects(backlog: Mapping[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    task_records = backlog.get("task_records")
    if not isinstance(task_records, list):
        return records
    for task in task_records:
        if not isinstance(task, Mapping):
            continue
        records.append(
            {
                "task_id": str(task.get("task_id", NOT_COMPUTABLE)),
                "priority": str(task.get("priority", NOT_COMPUTABLE)),
                "task": str(task.get("task", NOT_COMPUTABLE)),
                "notion_status": "READY_FOR_WORK",
                "bulk_review_disposition": "REVIEW_ONLY_APPROVED",
                "post_reconciliation_status": "HELD_FOR_EXPLICIT_OPERATOR_AUTHORIZATION",
                "repo_path": str(task.get("repo_path", NOT_COMPUTABLE)),
                "repo_observed": bool(task.get("repo_observed", False)),
                "implementation_authorized": False,
                "code_creation_authorized": False,
                "schema_file_creation_authorized": False,
                "execution_authority": False,
            }
        )
    return records


def build_v2_hygiene_phase1_bulk_approval_reconciliation(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source_records = [
        _source_record(
            root,
            SOURCE_PHASE1_BACKLOG,
            "V2_HYGIENE_PHASE1_FOUNDATION_BACKLOG_PLAN_READY",
            "status",
        ),
        _source_record(
            root,
            SOURCE_OPERATOR_GATE,
            "V2_HYGIENE_LOOP_AWARENESS_OPERATOR_AUTHORIZATION_GATE_HELD_FOR_OPERATOR",
            "gate_status",
        ),
        _source_record(
            root,
            SOURCE_BULK_DISPOSITION,
            "OPERATOR_REVIEW_REQUIRED_ITEMS_BULK_DISPOSITION_REVIEW_ONLY_APPROVED_WITH_HOLDS",
            "disposition_status",
        ),
    ]
    backlog = _read_json(root / SOURCE_PHASE1_BACKLOG)
    gate = _read_json(root / SOURCE_OPERATOR_GATE)
    bulk = _read_json(root / SOURCE_BULK_DISPOSITION)
    source_ready = all(record["status_matches_expected"] for record in source_records)
    bulk_review_only = (
        bulk.get("review_only_approval_recorded") is True
        and bulk.get("bulk_authority_approval_granted") is False
        and bulk.get("implementation_authorized") is False
        and bulk.get("authorization_record_created") is False
        and bulk.get("authority_grant_count") == 0
    )
    gate_still_held = (
        gate.get("operator_authorization_observed") is False
        and gate.get("authorization_granted") is False
        and gate.get("selected_operator_decision") == "HOLD"
        and gate.get("valid_for_implementation") is False
    )
    phase1_ready_but_blocked = (
        backlog.get("status") == "V2_HYGIENE_PHASE1_FOUNDATION_BACKLOG_PLAN_READY"
        and backlog.get("task_summary", {}).get("blocked_task_count") == 14
        and backlog.get("valid_for_implementation") is False
    )
    task_effects = _phase1_task_effects(backlog)
    reconciliation_passed = (
        source_ready
        and bulk_review_only
        and gate_still_held
        and phase1_ready_but_blocked
        and len(task_effects) == 14
    )
    blockers = [] if reconciliation_passed else ["phase1_bulk_approval_sources_not_reconciled"]

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "reconciliation_id": RECONCILIATION_ID,
        "reconciliation_status": (
            "V2_HYGIENE_PHASE1_BULK_APPROVAL_RECONCILIATION_HELD_FOR_OPERATOR_AUTHORIZATION"
            if reconciliation_passed
            else "V2_HYGIENE_PHASE1_BULK_APPROVAL_RECONCILIATION_BLOCKED"
        ),
        "source_records": source_records,
        "source_ready": source_ready,
        "notion_phase1_status": "READY_TO_BEGIN_IMPLEMENTATION",
        "bulk_review_status": str(bulk.get("disposition_status", NOT_COMPUTABLE)),
        "bulk_review_only_approval_recorded": bool(bulk.get("review_only_approval_recorded", False)),
        "bulk_authority_approval_granted": False,
        "operator_gate_status": str(gate.get("gate_status", NOT_COMPUTABLE)),
        "operator_authorization_observed": False,
        "operator_authorization_required": True,
        "operator_decision_after_bulk_review": "HOLD",
        "phase1_task_effects": task_effects,
        "effect_summary": {
            "phase1_task_count": len(task_effects),
            "review_only_approved_task_count": len(task_effects),
            "implementation_authorized_task_count": 0,
            "held_task_count": len(task_effects),
            "repo_observed_task_count": sum(1 for task in task_effects if task["repo_observed"]),
        },
        "reconciliation_findings": [
            {
                "finding_id": "notion_phase1_ready_for_work_observed",
                "finding_status": "PASS" if phase1_ready_but_blocked else "FAIL_CLOSED",
                "authority_granted": False,
            },
            {
                "finding_id": "bulk_approval_is_review_only",
                "finding_status": "PASS" if bulk_review_only else "FAIL_CLOSED",
                "authority_granted": False,
            },
            {
                "finding_id": "operator_authorization_gate_remains_hold",
                "finding_status": "PASS" if gate_still_held else "FAIL_CLOSED",
                "authority_granted": False,
            },
            {
                "finding_id": "phase1_implementation_remains_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
        ],
        "recommended_next_action": (
            "treat the bulk approval as review-only evidence; collect explicit external "
            "operator authorization fields before any v2 hygiene code, schema, rune, "
            "module, integration hook, strict-mode, writeback, or execution lane"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "implementation_authorized": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_prepare_patch": False,
        "safe_to_auto_continue": False,
        "authorization_granted": False,
        "authorization_record_created": False,
        "operator_attestation_created": False,
        "operator_evidence_bundle_created": False,
        "hygiene_code_creation_authorized": False,
        "schema_file_creation_authorized": False,
        "rune_registration_authorized": False,
        "v2_module_registration_authorized": False,
        "strict_mode_enablement_authorized": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "canon_mutation": False,
        "schema_mutation": False,
        "authority_locks": _authority_locks(),
        "blockers": blockers,
        "downstream": NOT_COMPUTABLE,
    }
    return {**packet, "reconciliation_hash": canonical_hash(packet)}


def render_v2_hygiene_phase1_bulk_approval_reconciliation_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Phase 1 Bulk Approval Reconciliation",
        "",
        f"- reconciliation_id: {packet['reconciliation_id']}",
        f"- reconciliation_status: {packet['reconciliation_status']}",
        f"- notion_phase1_status: {packet['notion_phase1_status']}",
        f"- bulk_review_status: {packet['bulk_review_status']}",
        f"- operator_decision_after_bulk_review: {packet['operator_decision_after_bulk_review']}",
        f"- implementation_authorized: {packet['implementation_authorized']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        "",
        "## Source Records",
    ]
    for record in packet.get("source_records", []):
        if isinstance(record, Mapping):
            lines.append(
                "- "
                f"{record['path']}: {record['observed_status']} "
                f"(matched={record['status_matches_expected']})"
            )
    lines.extend(["", "## Findings"])
    for finding in packet.get("reconciliation_findings", []):
        if isinstance(finding, Mapping):
            lines.append(f"- {finding['finding_id']}: {finding['finding_status']}")
    lines.extend(["", "## Phase 1 Task Effects"])
    for task in packet.get("phase1_task_effects", []):
        if isinstance(task, Mapping):
            lines.append(
                "- "
                f"{task['task_id']}: {task['post_reconciliation_status']} "
                f"(implementation_authorized={task['implementation_authorized']})"
            )
    return lines


def write_v2_hygiene_phase1_bulk_approval_reconciliation(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_bulk_approval_reconciliation(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    json_path = root / OUT_JSON
    md_path = root / OUT_MD
    write_canonical_json(json_path, packet)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(render_v2_hygiene_phase1_bulk_approval_reconciliation_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
    return packet
