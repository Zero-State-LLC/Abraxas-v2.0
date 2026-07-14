from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygienePhase1OperatorReviewStabilizationDecisionRecordPlan.v1"
PLAN_ID = "v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_001"
PLAN_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_001.latest.json"
)
PLAN_MD_PATH = PLAN_JSON_PATH.with_suffix(".md")

SOURCE_STRATEGY_PLAN_PATH = (
    "out/operator_review/"
    "v2_hygiene_phase1_operator_review_stabilization_strategy_plan_001.latest.json"
)
EXPECTED_SOURCE_STATUS = (
    "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_STRATEGY_PLAN_READY"
)
EXPECTED_SOURCE_NEXT_LANE = (
    "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_PLAN"
)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _authority_locks() -> dict[str, bool]:
    return {
        "activation": False,
        "auto_approval": False,
        "auto_continuation": False,
        "canon_mutation": False,
        "code_creation": False,
        "decision_record_creation": False,
        "evidence_bundle_creation": False,
        "execution_authority": False,
        "github_writeback": False,
        "hygiene_code_creation": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_authorization_record_creation": False,
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


def _source_record(packet: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "path": SOURCE_STRATEGY_PLAN_PATH,
        "source_observed": bool(packet),
        "source_hash": canonical_hash(packet) if packet else NOT_COMPUTABLE,
        "source_status": str(
            packet.get("strategy_plan_status", NOT_COMPUTABLE)
        ),
        "source_recommended_next_lane": str(
            packet.get("recommended_next_lane", NOT_COMPUTABLE)
        ),
        "selected_strategy_id": str(
            packet.get("selected_strategy_id", NOT_COMPUTABLE)
        ),
        "operator_decision_required": bool(
            packet.get("operator_decision_required", False)
        ),
        "operator_decision_record_created": bool(
            packet.get("operator_decision_record_created", True)
        ),
        "implementation_authorized": bool(
            packet.get("implementation_authorized", False)
        ),
        "valid_for_execution": bool(packet.get("valid_for_execution", False)),
    }


def _required_field_groups() -> list[dict[str, Any]]:
    return [
        {
            "group_id": "operator_identity",
            "required": True,
            "fields": [
                "operator_id",
                "operator_reviewed_at_source_observed",
                "operator_attestation_hash",
            ],
        },
        {
            "group_id": "strategy_scope_acknowledgement",
            "required": True,
            "fields": [
                "source_strategy_plan_path",
                "source_strategy_plan_hash",
                "selected_strategy_id",
                "cycle_audit_scope_acknowledged",
            ],
        },
        {
            "group_id": "stabilization_disposition",
            "required": True,
            "fields": [
                "approved_strategy_id",
                "terminal_snapshot_allowed",
                "bulk_scan_exclusion_allowed",
                "two_phase_manifest_allowed",
                "naive_regeneration_allowed",
            ],
        },
        {
            "group_id": "authority_boundary_acknowledgement",
            "required": True,
            "fields": [
                "no_hygiene_implementation_authority",
                "no_decision_record_auto_creation",
                "no_runtime_mutation",
                "no_notion_writeback",
                "no_execution_authority",
            ],
        },
        {
            "group_id": "terminal_output_controls",
            "required": True,
            "fields": [
                "downstream_lane_disposition",
                "future_dry_run_allowed",
                "future_record_creation_gate_required",
                "rollback_or_supersession_policy",
            ],
        },
    ]


def _planned_decision_record(source_record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "record_type": "V2HygienePhase1OperatorReviewStabilizationDecisionRecord.v1",
        "record_creation_allowed": False,
        "record_created": False,
        "operator_attestation_required": True,
        "operator_attested": False,
        "source_strategy_plan_path": source_record["path"],
        "source_strategy_plan_hash": source_record["source_hash"],
        "selected_strategy_id": source_record["selected_strategy_id"],
        "default_disposition": "HOLD_FOR_OPERATOR_STABILIZATION_DECISION",
        "allowed_dispositions": [
            "APPROVE_TERMINAL_SNAPSHOT_STRATEGY",
            "APPROVE_SCAN_EXCLUSION_STRATEGY",
            "APPROVE_TWO_PHASE_MANIFEST_STRATEGY",
            "REJECT_STABILIZATION_STRATEGY",
            "HOLD_FOR_OPERATOR_STABILIZATION_DECISION",
        ],
        "forbidden_dispositions": [
            "APPROVE_NAIVE_REGENERATION_LOOP",
            "AUTHORIZE_PHASE1_IMPLEMENTATION",
            "AUTHORIZE_RUNTIME_MUTATION",
            "AUTHORIZE_NOTION_WRITEBACK",
            "AUTHORIZE_GITHUB_WRITEBACK",
            "AUTHORIZE_EXECUTION",
        ],
        "required_field_groups": _required_field_groups(),
    }


def build_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source = _read_json(root / SOURCE_STRATEGY_PLAN_PATH)
    source_record = _source_record(source)
    source_ready = (
        source_record["source_observed"] is True
        and source_record["source_status"] == EXPECTED_SOURCE_STATUS
        and source_record["source_recommended_next_lane"]
        == EXPECTED_SOURCE_NEXT_LANE
        and source_record["selected_strategy_id"] == "terminal_snapshot_strategy"
        and source_record["operator_decision_required"] is True
        and source_record["operator_decision_record_created"] is False
        and source_record["implementation_authorized"] is False
        and source_record["valid_for_execution"] is False
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "plan_id": PLAN_ID,
        "decision_record_plan_status": (
            "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_PLAN_READY"
            if source_ready
            else "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_PLAN_BLOCKED"
        ),
        "source_strategy_plan": source_record,
        "decision_record_required": True,
        "decision_record_creation_allowed": False,
        "decision_record_created": False,
        "operator_attestation_required": True,
        "operator_attested": False,
        "planned_decision_record": _planned_decision_record(source_record),
        "recommended_next_lane": (
            "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_DRY_RUN"
            if source_ready
            else NOT_COMPUTABLE
        ),
        "recommended_next_action": (
            "perform a simulated dry run of the planned stabilization decision "
            "record shape without attesting operator input or creating the record"
            if source_ready
            else "restore the stabilization strategy plan before decision-record planning"
        ),
        "plan_findings": [
            {
                "finding_id": "source_strategy_plan_ready",
                "finding_status": "PASS" if source_ready else "FAIL_CLOSED",
                "authority_granted": False,
            },
            {
                "finding_id": "decision_record_required_but_not_created",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
            {
                "finding_id": "phase1_implementation_remains_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
        ],
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authorization_granted": False,
        "authorization_record_created": False,
        "operator_attestation_created": False,
        "operator_evidence_bundle_created": False,
        "implementation_authorized": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_prepare_patch": False,
        "safe_to_auto_continue": False,
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
        "downstream": NOT_COMPUTABLE,
    }
    return {**packet, "decision_record_plan_hash": canonical_hash(packet)}


def render_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Phase 1 Operator Review Stabilization Decision Record Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- decision_record_plan_status: {packet['decision_record_plan_status']}",
        f"- decision_record_required: {packet['decision_record_required']}",
        f"- decision_record_created: {packet['decision_record_created']}",
        f"- operator_attestation_required: {packet['operator_attestation_required']}",
        f"- operator_attested: {packet['operator_attested']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Required Field Groups",
    ]
    planned = packet.get("planned_decision_record", {})
    if isinstance(planned, Mapping):
        groups = planned.get("required_field_groups", [])
        for group in groups:
            if isinstance(group, Mapping):
                lines.append(
                    f"- {group['group_id']}: required={group['required']}"
                )
    lines.extend(["", "## Findings"])
    for finding in packet.get("plan_findings", []):
        if isinstance(finding, Mapping):
            lines.append(
                f"- {finding['finding_id']}: {finding['finding_status']} "
                f"(authority_granted={finding['authority_granted']})"
            )
    return lines


def write_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = (
        build_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan(
            repo_root
        )
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / PLAN_JSON_PATH, packet)
    md_path = root / PLAN_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
