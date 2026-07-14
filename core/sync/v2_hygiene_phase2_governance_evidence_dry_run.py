from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase2_governance_evidence_request_plan import (
    PLAN_JSON_PATH as SOURCE_PLAN_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygienePhase2GovernanceEvidenceDryRun.v1"
DRY_RUN_ID = "v2_hygiene_phase2_governance_evidence_dry_run_001"
DRY_RUN_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase2_governance_evidence_dry_run_001.latest.json"
)
DRY_RUN_MD_PATH = DRY_RUN_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = "V2_HYGIENE_PHASE2_GOVERNANCE_EVIDENCE_REQUEST_PLAN_READY"
SIMULATED_PENDING_OPERATOR_INPUT = "SIMULATED_PENDING_OPERATOR_INPUT"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _locks_all_false(value: Any) -> bool:
    return isinstance(value, Mapping) and bool(value) and all(
        item is False for item in value.values()
    )


def _source_ready(plan: Mapping[str, Any]) -> bool:
    summary = plan.get("evidence_readiness_summary", {})
    return (
        plan.get("schema_version")
        == "V2HygienePhase2GovernanceEvidenceRequestPlan.v1"
        and plan.get("status") == EXPECTED_SOURCE_STATUS
        and plan.get("source_governance_audit_ready") is True
        and isinstance(summary, Mapping)
        and summary.get("required_group_count") == 5
        and summary.get("source_missing_control_count") == 6
        and summary.get("attested_group_count") == 0
        and plan.get("evidence_plan_only") is True
        and plan.get("operator_input_required") is True
        and plan.get("operator_attestations_present") is False
        and plan.get("operator_decision_attested") is False
        and plan.get("operator_attestation_created") is False
        and plan.get("evidence_bundle_created") is False
        and plan.get("operator_evidence_bundle_created") is False
        and plan.get("authorization_record_created") is False
        and plan.get("authorization_record_creation_authorized") is False
        and plan.get("implementation_authorized") is False
        and plan.get("module_code_creation_authorized") is False
        and plan.get("module_test_creation_authorized") is False
        and plan.get("module_registration_authorized") is False
        and plan.get("hygiene_pipeline_integration_authorized") is False
        and plan.get("promotion_authorized") is False
        and plan.get("strict_mode_enablement_authorized") is False
        and plan.get("schema_mutation_authorized") is False
        and plan.get("execution_authority") is False
        and plan.get("valid_for_authorization_record") is False
        and plan.get("valid_for_implementation") is False
        and plan.get("valid_for_execution") is False
        and plan.get("recommended_next_lane") == NOT_COMPUTABLE
        and plan.get("recommended_next_patch") == NOT_COMPUTABLE
        and plan.get("recommended_next_state") == "hold"
        and plan.get("safe_to_prepare_patch") is False
        and plan.get("safe_to_auto_continue") is False
        and _locks_all_false(plan.get("authority_locks"))
    )


def _simulated_field_groups(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    groups = plan.get("evidence_bundle_groups", [])
    if not isinstance(groups, list):
        return []

    simulated_groups: list[dict[str, Any]] = []
    for group in groups:
        if not isinstance(group, Mapping):
            continue
        required_fields = _string_list(group.get("required_fields"))
        record: dict[str, Any] = {
            "group_id": str(group.get("group_id", NOT_COMPUTABLE)),
            "attested": False,
            "field_count": len(required_fields),
            "fields": [
                {
                    "field": field,
                    "required": True,
                    "attested": False,
                    "simulated_value": SIMULATED_PENDING_OPERATOR_INPUT,
                }
                for field in required_fields
            ],
            "missing_fields": required_fields,
        }
        source_control_ids = _string_list(group.get("source_control_ids"))
        if source_control_ids:
            record["source_control_ids"] = source_control_ids
        simulated_groups.append(record)
    return simulated_groups


def _evaluation_blockers(groups: list[Mapping[str, Any]]) -> list[str]:
    blocker_by_group = {
        "operator_identity": "operator_identity_not_attested",
        "review_scope_acknowledgement": "review_scope_acknowledgement_not_attested",
        "authority_acknowledgements": "authority_acknowledgements_not_attested",
        "phase2_governance_control_disposition": (
            "phase2_governance_control_disposition_not_attested"
        ),
        "terminal_output_controls": "terminal_output_controls_not_attested",
    }
    blockers: list[str] = []
    for group in groups:
        blocker = blocker_by_group.get(str(group.get("group_id", "")))
        if blocker is not None:
            blockers.append(blocker)
    return blockers


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
        "hygiene_pipeline_integration": False,
        "implementation_authorization": False,
        "module_code_creation": False,
        "module_registration": False,
        "module_test_creation": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_evidence_bundle_creation": False,
        "promotion": False,
        "queue_mutation": False,
        "rune_binding_mutation": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "strict_mode_enablement": False,
        "v2_module_registration": False,
    }


def build_v2_hygiene_phase2_governance_evidence_dry_run(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    plan = _read_json(root / SOURCE_PLAN_JSON_PATH)
    source_observed = plan is not None
    plan = plan or {}
    source_ready = source_observed and _source_ready(plan)

    if source_ready:
        status = "V2_HYGIENE_PHASE2_GOVERNANCE_EVIDENCE_DRY_RUN_READY"
        simulated_groups = _simulated_field_groups(plan)
        blockers = _evaluation_blockers(simulated_groups)
    else:
        status = "V2_HYGIENE_PHASE2_GOVERNANCE_EVIDENCE_DRY_RUN_BLOCKED"
        simulated_groups = []
        blockers = [
            "source_phase2_governance_evidence_request_plan_missing_or_not_ready",
            f"source_path:{SOURCE_PLAN_JSON_PATH}",
        ]

    required_field_count = sum(
        int(group.get("field_count", 0)) for group in simulated_groups
    )
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "dry_run_id": DRY_RUN_ID,
        "source_evidence_plan_path": str(SOURCE_PLAN_JSON_PATH),
        "source_evidence_plan_observed": source_observed,
        "source_evidence_plan_ready": source_ready,
        "source_evidence_plan_hash": str(plan.get("plan_hash", NOT_COMPUTABLE)),
        "source_evidence_plan_status": str(plan.get("status", NOT_COMPUTABLE)),
        "source_missing_governance_control_ids": _string_list(
            plan.get("source_missing_governance_control_ids")
        ),
        "simulated_evidence_bundle": {
            "artifact_type": "V2HygienePhase2GovernanceEvidenceBundle.v1.simulated",
            "evidence_bundle_id": "v2_hygiene_phase2_governance_evidence_bundle_001.simulated",
            "evidence_bundle_hash": SIMULATED_PENDING_OPERATOR_INPUT,
            "simulated_only": True,
            "operator_input_required": True,
            "groups": simulated_groups,
        },
        "readiness_summary": {
            "simulated_only": True,
            "operator_input_required": True,
            "required_group_count": len(simulated_groups),
            "required_field_count": required_field_count,
            "attested_group_count": 0,
            "attested_field_count": 0,
            "source_missing_control_count": len(
                _string_list(plan.get("source_missing_governance_control_ids"))
            ),
            "evidence_bundle_complete": False,
            "valid_for_authorization_record": False,
            "evaluation_blockers": blockers,
        },
        "evaluation_blockers": blockers,
        "simulated_only": True,
        "operator_input_required": True,
        "operator_attestations_present": False,
        "operator_decision_attested": False,
        "operator_attestation_created": False,
        "evidence_bundle_created": False,
        "operator_evidence_bundle_created": False,
        "authorization_record_created": False,
        "authorization_record_creation_authorized": False,
        "implementation_authorized": False,
        "module_code_creation_authorized": False,
        "module_test_creation_authorized": False,
        "module_registration_authorized": False,
        "hygiene_pipeline_integration_authorized": False,
        "promotion_authorized": False,
        "strict_mode_enablement_authorized": False,
        "schema_mutation_authorized": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_authorization_record": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "recommended_next_action": (
            "preserve the v2 hygiene Phase 2 governance evidence hold; use this "
            "simulated missing-evidence bundle to guide external operator evidence "
            "collection before any evidence bundle, authorization record, module "
            "implementation, registration, HygienePipeline integration, promotion, "
            "writeback, activation, or execution"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_state": "hold",
        "safe_to_auto_continue": False,
        "safe_to_prepare_patch": False,
        "authority_locks": _authority_locks(),
        "dry_run_hash": "",
    }
    packet["dry_run_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "dry_run_hash"}
    )
    return packet


def render_v2_hygiene_phase2_governance_evidence_dry_run_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    summary = packet["readiness_summary"]
    bundle = packet["simulated_evidence_bundle"]
    lines = [
        "# v2.0 Hygiene Phase 2 Governance Evidence Dry Run",
        "",
        f"- dry_run_id: {packet['dry_run_id']}",
        f"- status: {packet['status']}",
        f"- source_evidence_plan_ready: {packet['source_evidence_plan_ready']}",
        f"- simulated_only: {packet['simulated_only']}",
        f"- required_group_count: {summary['required_group_count']}",
        f"- required_field_count: {summary['required_field_count']}",
        f"- attested_group_count: {summary['attested_group_count']}",
        f"- source_missing_control_count: {summary['source_missing_control_count']}",
        f"- valid_for_authorization_record: {packet['valid_for_authorization_record']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        "",
        "## Evaluation Blockers",
    ]
    for blocker in packet["evaluation_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Simulated Evidence Bundle"])
    lines.append(f"- artifact_type: {bundle['artifact_type']}")
    lines.append(f"- evidence_bundle_id: {bundle['evidence_bundle_id']}")
    for group in bundle["groups"]:
        lines.append(
            f"- {group['group_id']}: {group['field_count']} required fields "
            f"(attested={group['attested']})"
        )
    lines.extend(["", "## Source Missing Governance Controls"])
    for control_id in packet.get("source_missing_governance_control_ids", []):
        lines.append(f"- {control_id}")
    return lines


def write_v2_hygiene_phase2_governance_evidence_dry_run(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase2_governance_evidence_dry_run(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / DRY_RUN_JSON_PATH, packet)
    md_path = root / DRY_RUN_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(render_v2_hygiene_phase2_governance_evidence_dry_run_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
    return packet
