from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "V2HygienePhase1AuthorizationRecordPlan.v1"
PLAN_ID = "v2_hygiene_phase1_authorization_record_plan_001"
PLAN_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase1_authorization_record_plan_001.latest.json"
)
PLAN_MD_PATH = PLAN_JSON_PATH.with_suffix(".md")
NOT_COMPUTABLE = "NOT_COMPUTABLE"

SOURCE_PHASE1_RECONCILIATION = (
    "out/operator_review/v2_hygiene_phase1_bulk_approval_reconciliation_001.latest.json"
)
SOURCE_VALIDATION_REVIEW = (
    "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_001.latest.json"
)
SOURCE_EVIDENCE_DRY_RUN_REVIEW = (
    "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_review_001.latest.json"
)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _source_record(repo_root: Path, path: str, status_field: str, expected_status: str) -> dict[str, Any]:
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
        "authorization_record_creation": False,
        "auto_approval": False,
        "auto_continuation": False,
        "canon_mutation": False,
        "decision_record_creation": False,
        "evidence_bundle_creation": False,
        "execution_authority": False,
        "github_writeback": False,
        "hygiene_code_creation": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
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


def _field_group(group_id: str, fields: list[str]) -> dict[str, Any]:
    return {
        "group_id": group_id,
        "required_fields": fields,
        "fields_attested": False,
        "field_count": len(fields),
        "record_plan_steps": [
            {
                "step_id": f"{group_id}_{index:03d}",
                "field": field,
                "required": True,
                "attested": False,
            }
            for index, field in enumerate(fields, start=1)
        ],
    }


def build_v2_hygiene_phase1_authorization_record_plan(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source_records = [
        _source_record(
            root,
            SOURCE_PHASE1_RECONCILIATION,
            "reconciliation_status",
            "V2_HYGIENE_PHASE1_BULK_APPROVAL_RECONCILIATION_HELD_FOR_OPERATOR_AUTHORIZATION",
        ),
        _source_record(
            root,
            SOURCE_VALIDATION_REVIEW,
            "status",
            "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_REVIEW_HELD_FOR_OPERATOR",
        ),
        _source_record(
            root,
            SOURCE_EVIDENCE_DRY_RUN_REVIEW,
            "status",
            "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_REVIEW_EVIDENCE_DRY_RUN_REVIEW_HELD_FOR_OPERATOR",
        ),
    ]
    reconciliation = _read_json(root / SOURCE_PHASE1_RECONCILIATION)
    validation_review = _read_json(root / SOURCE_VALIDATION_REVIEW)
    dry_run_review = _read_json(root / SOURCE_EVIDENCE_DRY_RUN_REVIEW)

    source_ready = all(record["status_matches_expected"] for record in source_records)
    reconciliation_hold_ready = (
        reconciliation.get("operator_decision_after_bulk_review") == "HOLD"
        and reconciliation.get("implementation_authorized") is False
        and reconciliation.get("authorization_record_created") is False
        and reconciliation.get("valid_for_implementation") is False
    )
    validation_hold_ready = (
        validation_review.get("operator_attestations_present") is False
        and validation_review.get("valid_for_authorization_record") is False
        and validation_review.get("authorization_record_created") is False
    )
    dry_run_hold_ready = (
        dry_run_review.get("operator_attestations_present") is False
        and dry_run_review.get("operator_decision_attested") is False
        and dry_run_review.get("valid_for_authorization_record") is False
        and dry_run_review.get("authorization_record_created") is False
    )
    plan_ready = (
        source_ready
        and reconciliation_hold_ready
        and validation_hold_ready
        and dry_run_hold_ready
    )
    blockers = [] if plan_ready else ["v2_hygiene_phase1_authorization_record_sources_not_ready"]

    record_field_groups = [
        _field_group(
            "operator_identity",
            [
                "operator_id",
                "operator_name",
                "operator_role",
                "authorization_timestamp_source_observed",
                "operator_signature_reference",
            ],
        ),
        _field_group(
            "scope_acknowledgement",
            [
                "authorization_scope_acknowledged",
                "phase1_backlog_hash_acknowledged",
                "bulk_reconciliation_hash_acknowledged",
                "validation_review_hash_acknowledged",
                "evidence_dry_run_review_hash_acknowledged",
            ],
        ),
        _field_group(
            "authority_boundary_acknowledgement",
            [
                "advisory_only_acknowledged",
                "implementation_authority_boundary_acknowledged",
                "no_auto_continuation_acknowledged",
                "notion_writeback_denied_acknowledged",
                "github_writeback_denied_acknowledged",
                "runtime_mutation_denied_acknowledged",
                "canon_mutation_denied_acknowledged",
                "execution_authority_denied_acknowledged",
            ],
        ),
        _field_group(
            "phase1_workstream_disposition",
            [
                "approved_phase1_task_ids",
                "denied_phase1_task_ids",
                "approved_workstreams",
                "denied_workstreams",
                "disposition_rationale",
            ],
        ),
        _field_group(
            "record_output_controls",
            [
                "selected_operator_decision",
                "requested_follow_on_lane",
                "authorization_record_creation_request_id",
                "terminal_no_authority_summary",
            ],
        ),
    ]
    required_field_count = sum(group["field_count"] for group in record_field_groups)

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_PLAN_READY"
            if plan_ready
            else "V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_PLAN_BLOCKED"
        ),
        "plan_id": PLAN_ID,
        "source_records": source_records,
        "source_ready": source_ready,
        "record_plan_only": True,
        "operator_input_required": True,
        "operator_attestations_present": False,
        "authorization_record_created": False,
        "authorization_record_creation_authorized": False,
        "authorization_record_creation_required_before_implementation": True,
        "recommended_default_decision": "HOLD_FOR_OPERATOR_REVIEW",
        "recommended_next_action": (
            "collect explicit external operator authorization fields before any future "
            "v2 hygiene Phase 1 authorization record can be created; this plan does "
            "not create records, attestations, evidence bundles, implementation "
            "patches, registrations, writeback, or execution authority"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "record_field_groups": record_field_groups,
        "record_readiness_summary": {
            "source_record_count": len(source_records),
            "required_group_count": len(record_field_groups),
            "required_field_count": required_field_count,
            "attested_group_count": 0,
            "authorization_record_ready": False,
            "blocker_count": len(blockers),
        },
        "future_authorization_record_candidates": [
            "out/operator_review/v2_hygiene_phase1_authorization_record_001.latest.json",
            "out/operator_review/v2_hygiene_phase1_authorization_record_001.latest.md",
        ],
        "disallowed_follow_on_actions": [
            "AUTHORIZATION_RECORD_CREATION",
            "OPERATOR_ATTESTATION_CREATION",
            "OPERATOR_EVIDENCE_BUNDLE_CREATION",
            "HYGIENE_CODE_CREATION",
            "SCHEMA_FILE_CREATION",
            "V2_MODULE_REGISTRATION",
            "RUNE_REGISTRATION",
            "STRICT_MODE_ENABLEMENT",
            "PROJECTION_SURFACE_MUTATION",
            "NOTION_WRITEBACK",
            "GITHUB_WRITEBACK",
            "RUNTIME_MUTATION",
            "CANON_MUTATION",
            "QUEUE_MUTATION",
            "SCHEDULER_MUTATION",
            "FORECAST_ROUTING",
            "ACTIVATION",
            "TOKEN_MINTING",
            "EXECUTION",
        ],
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "implementation_authorized": False,
        "valid_for_authorization_record": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_prepare_patch": False,
        "safe_to_auto_continue": False,
        "hygiene_code_creation_authorized": False,
        "schema_file_creation_authorized": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "strict_mode_enablement_authorized": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "canon_mutation": False,
        "schema_mutation": False,
        "execution_authority": False,
        "authority_locks": _authority_locks(),
        "blockers": blockers,
        "downstream": NOT_COMPUTABLE,
    }
    return {**packet, "plan_hash": canonical_hash(packet)}


def render_v2_hygiene_phase1_authorization_record_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Phase 1 Authorization Record Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- status: {packet['status']}",
        f"- record_plan_only: {packet['record_plan_only']}",
        f"- operator_input_required: {packet['operator_input_required']}",
        f"- authorization_record_created: {packet['authorization_record_created']}",
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
    lines.extend(["", "## Required Field Groups"])
    for group in packet.get("record_field_groups", []):
        if isinstance(group, Mapping):
            lines.append(
                "- "
                f"{group['group_id']}: {group['field_count']} required fields "
                f"(attested={group['fields_attested']})"
            )
    return lines


def write_v2_hygiene_phase1_authorization_record_plan(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_authorization_record_plan(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    json_path = root / PLAN_JSON_PATH
    md_path = root / PLAN_MD_PATH
    write_canonical_json(json_path, packet)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(render_v2_hygiene_phase1_authorization_record_plan_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
    return packet
