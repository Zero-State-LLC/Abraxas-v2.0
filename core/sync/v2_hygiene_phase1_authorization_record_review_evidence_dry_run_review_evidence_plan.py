from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review import (
    REVIEW_JSON_PATH as SOURCE_REVIEW_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygienePhase1AuthorizationRecordReviewEvidenceDryRunReviewEvidencePlan.v1"
PLAN_ID = (
    "v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_plan_001"
)
PLAN_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_plan_001.latest.json"
)
PLAN_MD_PATH = PLAN_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = (
    "V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_REVIEW_EVIDENCE_DRY_RUN_REVIEW_HELD_FOR_OPERATOR"
)


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


def _source_ready(review: Mapping[str, Any]) -> bool:
    return (
        review.get("schema_version")
        == "V2HygienePhase1AuthorizationRecordReviewEvidenceDryRunReview.v1"
        and review.get("status") == EXPECTED_SOURCE_STATUS
        and review.get("source_evidence_dry_run_ready") is True
        and review.get("source_readiness") == "SOURCE_PHASE1_EVIDENCE_DRY_RUN_READY"
        and review.get("selected_operator_decision") == "HOLD_FOR_OPERATOR_REVIEW"
        and review.get("selected_follow_on_action")
        == "MAINTAIN_V2_HYGIENE_PHASE1_AUTHORIZATION_HOLD"
        and review.get("operator_review_required") is True
        and review.get("operator_input_required") is True
        and review.get("operator_attestations_present") is False
        and review.get("operator_decision_attested") is False
        and review.get("operator_attestation_created") is False
        and review.get("evidence_bundle_created") is False
        and review.get("operator_evidence_bundle_created") is False
        and review.get("authorization_record_created") is False
        and review.get("authorization_record_creation_authorized") is False
        and review.get("implementation_authorized") is False
        and review.get("hygiene_code_creation_authorized") is False
        and review.get("schema_file_creation_authorized") is False
        and review.get("v2_module_registration_authorized") is False
        and review.get("rune_registration_authorized") is False
        and review.get("strict_mode_enablement_authorized") is False
        and review.get("projection_surface_mutation_authorized") is False
        and review.get("schema_mutation_authorized") is False
        and review.get("execution_authority") is False
        and review.get("valid_for_authorization_record") is False
        and review.get("valid_for_implementation") is False
        and review.get("valid_for_execution") is False
        and review.get("recommended_next_patch") == NOT_COMPUTABLE
        and review.get("recommended_next_lane") == NOT_COMPUTABLE
        and review.get("recommended_next_state") == "hold"
        and review.get("safe_to_auto_continue") is False
        and _locks_all_false(review.get("authority_locks"))
    )


def build_v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_plan(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    review = _read_json(root / SOURCE_REVIEW_JSON_PATH)
    review_observed = review is not None
    review = review or {}
    source_ready = review_observed and _source_ready(review)
    blockers = [] if source_ready else ["source_evidence_dry_run_review_not_ready"]
    if not review_observed:
        blockers = [
            "source_evidence_dry_run_review_missing_or_unreadable",
            f"source_path:{SOURCE_REVIEW_JSON_PATH}",
        ]

    evidence_bundle_groups = [
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
                "reviewed_evidence_dry_run_review_id",
                "reviewed_evidence_dry_run_review_hash",
                "reviewed_evidence_dry_run_hash",
                "reviewed_evidence_plan_hash",
                "reviewed_authorization_record_dry_run_review_hash",
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
                "implementation_authority_denied_acknowledged",
                "hygiene_code_creation_denied_acknowledged",
                "schema_file_creation_denied_acknowledged",
                "v2_module_registration_denied_acknowledged",
                "rune_registration_denied_acknowledged",
                "strict_mode_enablement_denied_acknowledged",
                "notion_writeback_denied_acknowledged",
                "github_writeback_denied_acknowledged",
                "runtime_mutation_denied_acknowledged",
                "canon_mutation_denied_acknowledged",
                "execution_authority_denied_acknowledged",
            ],
        },
        {
            "group_id": "phase1_evidence_disposition",
            "required_fields": [
                "approved_evidence_group_ids",
                "held_evidence_group_ids",
                "denied_evidence_group_ids",
                "disposition_rationale",
                "requested_follow_on_lane",
            ],
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
        for group in evidence_bundle_groups
    ]
    required_field_count = sum(len(group["required_fields"]) for group in planned_groups)

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_REVIEW_EVIDENCE_DRY_RUN_REVIEW_EVIDENCE_PLAN_READY"
            if source_ready
            else "V2_HYGIENE_PHASE1_AUTHORIZATION_RECORD_REVIEW_EVIDENCE_DRY_RUN_REVIEW_EVIDENCE_PLAN_BLOCKED"
        ),
        "plan_id": PLAN_ID,
        "source_review_path": str(SOURCE_REVIEW_JSON_PATH),
        "source_review_observed": review_observed,
        "source_review_ready": source_ready,
        "source_review_status": str(review.get("status", NOT_COMPUTABLE)),
        "source_review_hash": str(review.get("review_hash", NOT_COMPUTABLE)),
        "source_evidence_dry_run_packet_hash": str(
            review.get("source_evidence_dry_run_packet_hash", NOT_COMPUTABLE)
        ),
        "source_evaluation_blockers": _string_list(
            review.get("source_evaluation_blockers")
        ),
        "source_simulated_evidence_group_ids": _string_list(
            review.get("source_simulated_evidence_group_ids")
        ),
        "source_terminal_hold_reason": str(
            review.get("terminal_hold_reason", NOT_COMPUTABLE)
        ),
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
        "hygiene_code_creation_authorized": False,
        "schema_file_creation_authorized": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "strict_mode_enablement_authorized": False,
        "projection_surface_mutation_authorized": False,
        "schema_mutation_authorized": False,
        "evidence_bundle_groups": planned_groups,
        "evidence_readiness_summary": {
            "source_review_ready": source_ready,
            "required_group_count": len(planned_groups),
            "required_field_count": required_field_count,
            "attested_group_count": 0,
            "blocker_count": len(blockers),
        },
        "future_evidence_output_candidates": [
            "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_bundle_001.latest.json",
            "out/operator_review/v2_hygiene_phase1_authorization_record_review_evidence_bundle_001.latest.md",
        ],
        "future_authorization_record_candidates": [
            "out/operator_review/v2_hygiene_phase1_authorization_record_001.latest.json",
            "out/operator_review/v2_hygiene_phase1_authorization_record_001.latest.md",
        ],
        "recommended_default_decision": "HOLD_FOR_OPERATOR_REVIEW",
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_state": "hold",
        "recommended_next_action": (
            "collect explicit external operator evidence for the held v2 hygiene "
            "Phase 1 authorization-record evidence dry-run review before any "
            "future evidence bundle, authorization record, or implementation lane; "
            "do not create evidence, attestations, records, schemas, registrations, "
            "implementation patches, writeback, activation, or execution"
            if source_ready
            else "repair the source evidence dry-run review before evidence planning"
        ),
        "safe_to_auto_continue": False,
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


def render_v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Phase 1 Authorization Record Review Evidence Dry Run Review Evidence Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- status: {packet['status']}",
        f"- source_review_ready: {packet['source_review_ready']}",
        f"- evidence_plan_only: {packet['evidence_plan_only']}",
        f"- operator_input_required: {packet['operator_input_required']}",
        f"- authorization_record_created: {packet['authorization_record_created']}",
        f"- implementation_authorized: {packet['implementation_authorized']}",
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
    lines.extend(["", "## Source Evaluation Blockers"])
    if packet.get("source_evaluation_blockers"):
        for blocker in packet["source_evaluation_blockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_plan(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_plan(
        repo_root
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / PLAN_JSON_PATH, packet)
    md_path = root / PLAN_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_authorization_record_review_evidence_dry_run_review_evidence_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
