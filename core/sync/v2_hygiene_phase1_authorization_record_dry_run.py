from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_authorization_record_plan import (
    PLAN_JSON_PATH as SOURCE_PLAN_JSON_PATH,
)

SCHEMA_VERSION = "V2HygienePhase1AuthorizationRecordDryRun.v1"
DRY_RUN_ID = "v2_hygiene_phase1_authorization_record_dry_run_001"
DRY_RUN_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase1_authorization_record_dry_run_001.latest.json"
)
DRY_RUN_MD_PATH = DRY_RUN_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = "V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_PLAN_READY"
NOT_COMPUTABLE = "NOT_COMPUTABLE"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _authority_locks() -> dict[str, bool]:
    return {
        "activation": False,
        "authorization_record_creation": False,
        "auto_approval": False,
        "auto_continuation": False,
        "canon_mutation": False,
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


def _planned_fields(plan: Mapping[str, Any]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for group in plan.get("record_field_groups", []):
        if not isinstance(group, Mapping):
            continue
        group_id = str(group.get("group_id", ""))
        fields = group.get("required_fields", [])
        if group_id and isinstance(fields, list):
            groups[group_id] = [str(field) for field in fields]
    return dict(sorted(groups.items()))


def _simulated_group(group_id: str, fields: list[str]) -> dict[str, Any]:
    return {
        "group_id": group_id,
        "fields": {
            field: {
                "required": True,
                "attested": False,
                "simulated_value": "SIMULATED_PENDING_OPERATOR_INPUT",
            }
            for field in fields
        },
        "field_count": len(fields),
        "attested_field_count": 0,
        "group_attested": False,
    }


def build_v2_hygiene_phase1_authorization_record_dry_run(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    plan = _read_json(root / SOURCE_PLAN_JSON_PATH)
    plan_observed = plan is not None
    plan = plan or {}
    source_plan_hash = str(plan.get("plan_hash", NOT_COMPUTABLE))
    source_plan_ready = (
        plan.get("schema_version") == "V2HygienePhase1AuthorizationRecordPlan.v1"
        and plan.get("status") == EXPECTED_SOURCE_STATUS
        and plan.get("source_ready") is True
        and plan.get("record_plan_only") is True
        and plan.get("operator_input_required") is True
        and plan.get("operator_attestations_present") is False
        and plan.get("authorization_record_created") is False
        and plan.get("authorization_record_creation_authorized") is False
        and plan.get("implementation_authorized") is False
        and plan.get("valid_for_authorization_record") is False
        and plan.get("valid_for_implementation") is False
        and plan.get("valid_for_execution") is False
        and plan.get("safe_to_auto_continue") is False
    )
    planned_fields = _planned_fields(plan)
    total_required_fields = sum(len(fields) for fields in planned_fields.values())

    if not plan_observed:
        status = "NOT_COMPUTABLE"
        shape_validation_passed = False
        validation_blockers = [
            "source_authorization_record_plan_missing_or_unreadable",
            f"source_path:{SOURCE_PLAN_JSON_PATH}",
        ]
    elif not source_plan_ready:
        status = "V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_DRY_RUN_BLOCKED"
        shape_validation_passed = False
        validation_blockers = ["source_authorization_record_plan_not_ready"]
    else:
        status = "V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_DRY_RUN_READY"
        shape_validation_passed = bool(planned_fields and total_required_fields)
        validation_blockers = [
            "operator_identity_not_attested",
            "scope_acknowledgement_not_attested",
            "authority_boundary_acknowledgement_not_attested",
            "phase1_workstream_disposition_not_attested",
            "record_output_controls_not_attested",
        ]

    simulated_groups = [
        _simulated_group(group_id, fields) for group_id, fields in planned_fields.items()
    ]
    simulated_record = {
        "artifact_type": "V2HygienePhase1AuthorizationRecord.v1.simulated",
        "simulated_only": True,
        "authorization_record_id": "v2_hygiene_phase1_authorization_record_001.simulated",
        "authorization_record_hash": "SIMULATED_PENDING_OPERATOR_INPUT",
        "selected_operator_decision": "HOLD_FOR_OPERATOR_REVIEW",
        "requested_follow_on_lane": NOT_COMPUTABLE,
        "terminal_no_authority_summary": "SIMULATED_NO_AUTHORITY_GRANTED",
        "field_groups": simulated_groups,
        "required_group_count": len(simulated_groups),
        "required_field_count": total_required_fields,
        "attested_group_count": 0,
        "attested_field_count": 0,
        "operator_attestations_present": False,
        "authorization_record_created": False,
        "authorization_record_creation_authorized": False,
        "implementation_authorized": False,
        "hygiene_code_creation_authorized": False,
        "schema_file_creation_authorized": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "strict_mode_enablement_authorized": False,
        "execution_authority": False,
        "valid_for_authorization_record": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
    }
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "dry_run_id": DRY_RUN_ID,
        "source_plan_path": str(SOURCE_PLAN_JSON_PATH),
        "source_plan_hash": source_plan_hash,
        "source_plan_observed": plan_observed,
        "source_plan_ready": source_plan_ready,
        "shape_validation_passed": shape_validation_passed,
        "simulated_authorization_record": simulated_record,
        "validation_blockers": validation_blockers,
        "simulated_only": True,
        "operator_input_required": True,
        "operator_attestations_present": False,
        "authorization_record_created": False,
        "authorization_record_creation_authorized": False,
        "implementation_authorized": False,
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
        "valid_for_authorization_record": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_prepare_patch": False,
        "safe_to_auto_continue": False,
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_action": (
            "hold v2 hygiene Phase 1 implementation until explicit external "
            "operator authorization fields are attested; this dry run validates "
            "only the simulated record shape and grants no authority"
        ),
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authority_locks": _authority_locks(),
    }
    packet["dry_run_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "dry_run_hash"}
    )
    return packet


def render_v2_hygiene_phase1_authorization_record_dry_run_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Phase 1 Authorization Record Dry Run",
        "",
        f"- dry_run_id: {packet['dry_run_id']}",
        f"- status: {packet['status']}",
        f"- source_plan_ready: {packet['source_plan_ready']}",
        f"- shape_validation_passed: {packet['shape_validation_passed']}",
        f"- simulated_only: {packet['simulated_only']}",
        f"- authorization_record_created: {packet['authorization_record_created']}",
        f"- implementation_authorized: {packet['implementation_authorized']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        "",
        "## Validation Blockers",
    ]
    for blocker in packet.get("validation_blockers", []):
        lines.append(f"- {blocker}")
    simulated = packet.get("simulated_authorization_record", {})
    lines.extend(["", "## Simulated Record"])
    if isinstance(simulated, Mapping):
        lines.extend(
            [
                f"- selected_operator_decision: {simulated['selected_operator_decision']}",
                f"- required_group_count: {simulated['required_group_count']}",
                f"- required_field_count: {simulated['required_field_count']}",
                f"- attested_field_count: {simulated['attested_field_count']}",
                f"- terminal_no_authority_summary: {simulated['terminal_no_authority_summary']}",
            ]
        )
    return lines


def write_v2_hygiene_phase1_authorization_record_dry_run(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_authorization_record_dry_run(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    json_path = root / DRY_RUN_JSON_PATH
    md_path = root / DRY_RUN_MD_PATH
    write_canonical_json(json_path, packet)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(render_v2_hygiene_phase1_authorization_record_dry_run_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
    return packet
