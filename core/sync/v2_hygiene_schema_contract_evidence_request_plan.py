from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_schema_contract_readiness_audit import (
    OUT_JSON as SOURCE_SCHEMA_AUDIT_JSON,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygieneSchemaContractEvidenceRequestPlan.v1"
PLAN_ID = "v2_hygiene_schema_contract_evidence_request_plan_001"
PLAN_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_schema_contract_evidence_request_plan_001.latest.json"
)
PLAN_MD_PATH = PLAN_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = "V2_HYGIENE_SCHEMA_CONTRACT_READINESS_AUDIT_HELD_FOR_OPERATOR"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _locks_all_false(value: Any) -> bool:
    return isinstance(value, Mapping) and bool(value) and all(
        item is False for item in value.values()
    )


def _field_plan(group_id: str, fields: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "step_id": f"{group_id}_{index:03d}",
            "field": field,
            "required": True,
            "attested": False,
        }
        for index, field in enumerate(fields, start=1)
    ]


def _authority_locks() -> dict[str, bool]:
    return {
        "activation": False,
        "authorization_record_creation": False,
        "auto_approval": False,
        "auto_continuation": False,
        "auto_patch_generation": False,
        "canon_mutation": False,
        "evidence_bundle_creation": False,
        "execution_authority": False,
        "github_writeback": False,
        "hygiene_code_creation": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_evidence_bundle_creation": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_file_creation": False,
        "schema_mutation": False,
        "strict_mode_enablement": False,
        "v2_module_registration": False,
    }


def _source_ready(packet: Mapping[str, Any]) -> bool:
    summary = packet.get("contract_summary", {})
    return (
        packet.get("schema_version") == "V2HygieneSchemaContractReadinessAudit.v1"
        and packet.get("status") == EXPECTED_SOURCE_STATUS
        and packet.get("source_ready") is True
        and isinstance(summary, Mapping)
        and summary.get("expected_contract_count") == 5
        and summary.get("missing_contract_count") == 5
        and summary.get("repo_observed_count") == 0
        and packet.get("operator_review_required") is True
        and packet.get("operator_input_required") is True
        and packet.get("operator_attestation_created") is False
        and packet.get("authorization_record_created") is False
        and packet.get("schema_file_creation_authorized") is False
        and packet.get("schema_mutation_authorized") is False
        and packet.get("implementation_authorized") is False
        and packet.get("hygiene_code_creation_authorized") is False
        and packet.get("v2_module_registration_authorized") is False
        and packet.get("rune_registration_authorized") is False
        and packet.get("strict_mode_enablement_authorized") is False
        and packet.get("execution_authority") is False
        and packet.get("valid_for_implementation") is False
        and packet.get("valid_for_execution") is False
        and packet.get("safe_to_prepare_patch") is False
        and packet.get("safe_to_auto_continue") is False
        and packet.get("recommended_next_lane") == NOT_COMPUTABLE
        and packet.get("recommended_next_patch") == NOT_COMPUTABLE
        and _locks_all_false(packet.get("authority_locks"))
    )


def _contract_ids(source: Mapping[str, Any]) -> list[str]:
    summary = source.get("contract_summary", {})
    if isinstance(summary, Mapping) and isinstance(summary.get("missing_contract_ids"), list):
        return [str(item) for item in summary["missing_contract_ids"]]
    return [
        str(record.get("contract_id"))
        for record in source.get("contract_records", [])
        if isinstance(record, Mapping) and record.get("repo_observed") is False
    ]


def build_v2_hygiene_schema_contract_evidence_request_plan(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source = _read_json(root / SOURCE_SCHEMA_AUDIT_JSON)
    source_observed = source is not None
    source = source or {}
    source_ready = source_observed and _source_ready(source)
    blockers = [] if source_ready else ["source_schema_contract_audit_not_ready"]
    if not source_observed:
        blockers = [
            "source_schema_contract_audit_missing_or_unreadable",
            f"source_path:{SOURCE_SCHEMA_AUDIT_JSON}",
        ]

    missing_contract_ids = _contract_ids(source)
    contract_records = [
        {
            "contract_id": str(record.get("contract_id", NOT_COMPUTABLE)),
            "notion_status": str(record.get("notion_status", NOT_COMPUTABLE)),
            "repo_path": str(record.get("repo_path", NOT_COMPUTABLE)),
            "required_fields": str(record.get("required_fields", NOT_COMPUTABLE)),
            "repo_observed": bool(record.get("repo_observed", False)),
            "authority_granted": False,
        }
        for record in source.get("contract_records", [])
        if isinstance(record, Mapping)
    ]

    evidence_groups = [
        {
            "group_id": "operator_identity",
            "required_fields": [
                "operator_id",
                "operator_name",
                "operator_role",
                "attestation_timestamp_source_observed",
                "operator_signature_reference",
            ],
        },
        {
            "group_id": "review_scope_acknowledgement",
            "required_fields": [
                "reviewed_schema_contract_audit_id",
                "reviewed_schema_contract_audit_hash",
                "reviewed_phase1_backlog_hash",
                "reviewed_phase1_authorization_hold_hash",
                "reviewed_notion_schema_contract_source_hash",
            ],
        },
        {
            "group_id": "authority_acknowledgements",
            "required_fields": [
                "advisory_only_acknowledged",
                "projection_only_acknowledged",
                "non_authoritative_acknowledged",
                "operator_attestation_creation_denied_acknowledged",
                "evidence_bundle_creation_denied_acknowledged",
                "authorization_record_creation_denied_acknowledged",
                "schema_file_creation_denied_acknowledged",
                "schema_mutation_denied_acknowledged",
                "hygiene_code_creation_denied_acknowledged",
                "implementation_authorization_denied_acknowledged",
                "v2_module_registration_denied_acknowledged",
                "rune_registration_denied_acknowledged",
                "strict_mode_enablement_denied_acknowledged",
                "notion_writeback_denied_acknowledged",
                "github_writeback_denied_acknowledged",
                "runtime_mutation_denied_acknowledged",
                "execution_authority_denied_acknowledged",
            ],
        },
        {
            "group_id": "schema_contract_disposition",
            "required_fields": [
                "approved_schema_contract_ids",
                "held_schema_contract_ids",
                "denied_schema_contract_ids",
                "missing_contract_rationale",
                "requested_follow_on_lane",
            ],
            "source_contract_ids": missing_contract_ids,
        },
        {
            "group_id": "terminal_output_controls",
            "required_fields": [
                "selected_operator_decision",
                "evidence_bundle_output_id",
                "authorization_record_creation_request_id",
                "terminal_no_authority_summary",
            ],
        },
    ]
    planned_groups = [
        {
            **group,
            "collection_steps": _field_plan(group["group_id"], group["required_fields"]),
            "fields_attested": False,
        }
        for group in evidence_groups
    ]
    required_field_count = sum(len(group["required_fields"]) for group in planned_groups)

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "V2_HYGIENE_SCHEMA_CONTRACT_EVIDENCE_REQUEST_PLAN_READY"
            if source_ready
            else "V2_HYGIENE_SCHEMA_CONTRACT_EVIDENCE_REQUEST_PLAN_BLOCKED"
        ),
        "plan_id": PLAN_ID,
        "source_schema_contract_audit_path": str(SOURCE_SCHEMA_AUDIT_JSON),
        "source_schema_contract_audit_observed": source_observed,
        "source_schema_contract_audit_ready": source_ready,
        "source_schema_contract_audit_status": str(source.get("status", NOT_COMPUTABLE)),
        "source_schema_contract_audit_hash": str(source.get("audit_hash", NOT_COMPUTABLE)),
        "source_missing_schema_contract_ids": missing_contract_ids,
        "source_contract_records": contract_records,
        "evidence_plan_only": True,
        "operator_input_required": True,
        "operator_attestations_present": False,
        "operator_decision_attested": False,
        "operator_attestation_created": False,
        "evidence_bundle_created": False,
        "operator_evidence_bundle_created": False,
        "authorization_record_created": False,
        "authorization_record_creation_authorized": False,
        "implementation_authorized": False,
        "schema_file_creation_authorized": False,
        "schema_mutation_authorized": False,
        "hygiene_code_creation_authorized": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "strict_mode_enablement_authorized": False,
        "evidence_bundle_groups": planned_groups,
        "evidence_readiness_summary": {
            "source_schema_contract_audit_ready": source_ready,
            "required_group_count": len(planned_groups),
            "required_field_count": required_field_count,
            "attested_group_count": 0,
            "source_missing_contract_count": len(missing_contract_ids),
            "blocker_count": len(blockers),
        },
        "required_review_artifacts": [
            str(SOURCE_SCHEMA_AUDIT_JSON),
            "out/sync/v2_hygiene_phase1_foundation_backlog_plan/latest.json",
            "out/operator_review/v2_hygiene_phase1_authorization_chain_compression_audit_001.latest.json",
        ],
        "future_evidence_output_candidates": [
            "out/operator_review/v2_hygiene_schema_contract_evidence_bundle_001.latest.json",
            "out/operator_review/v2_hygiene_schema_contract_evidence_bundle_001.latest.md",
        ],
        "future_authorization_record_candidates": [
            "out/operator_review/v2_hygiene_schema_contract_authorization_record_001.latest.json",
            "out/operator_review/v2_hygiene_schema_contract_authorization_record_001.latest.md",
        ],
        "recommended_default_decision": "HOLD_FOR_OPERATOR_REVIEW",
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_state": "hold",
        "recommended_next_action": (
            "collect explicit external operator evidence for the held v2 hygiene "
            "schema-contract readiness audit before any future evidence bundle, "
            "authorization record, schema file creation, hygiene code creation, "
            "registration, strict-mode enablement, writeback, activation, or execution"
            if source_ready
            else "repair the v2 hygiene schema-contract readiness audit before evidence planning"
        ),
        "safe_to_auto_continue": False,
        "safe_to_prepare_patch": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_authorization_record": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "authority_locks": _authority_locks(),
        "blockers": blockers,
    }
    return {**packet, "plan_hash": canonical_hash(packet)}


def render_v2_hygiene_schema_contract_evidence_request_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Schema Contract Evidence Request Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- status: {packet['status']}",
        f"- source_schema_contract_audit_ready: {packet['source_schema_contract_audit_ready']}",
        f"- evidence_plan_only: {packet['evidence_plan_only']}",
        f"- operator_input_required: {packet['operator_input_required']}",
        f"- authorization_record_created: {packet['authorization_record_created']}",
        f"- implementation_authorized: {packet['implementation_authorized']}",
        f"- schema_file_creation_authorized: {packet['schema_file_creation_authorized']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        "",
        "## Required Evidence Groups",
    ]
    for group in packet.get("evidence_bundle_groups", []):
        if isinstance(group, Mapping):
            lines.append(
                f"- {group['group_id']}: {len(group['required_fields'])} required fields "
                f"(attested={group['fields_attested']})"
            )
    lines.extend(["", "## Source Missing Schema Contracts"])
    for contract_id in packet.get("source_missing_schema_contract_ids", []):
        lines.append(f"- {contract_id}")
    if packet.get("blockers"):
        lines.extend(["", "## Blockers"])
        for blocker in packet["blockers"]:
            lines.append(f"- {blocker}")
    return lines


def write_v2_hygiene_schema_contract_evidence_request_plan(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_schema_contract_evidence_request_plan(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / PLAN_JSON_PATH, packet)
    md_path = root / PLAN_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(render_v2_hygiene_schema_contract_evidence_request_plan_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
    return packet
