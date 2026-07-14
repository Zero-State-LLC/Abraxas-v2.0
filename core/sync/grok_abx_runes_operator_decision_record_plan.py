from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.grok_abx_runes_reconciliation_plan import (
    PLAN_JSON_PATH as SOURCE_RECONCILIATION_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "GrokAbxRunesOperatorDecisionRecordPlan.v1"
PLAN_ID = "grok_abx_runes_operator_decision_record_plan_001"
PLAN_JSON_PATH = Path(
    "out/operator_review/grok_abx_runes_operator_decision_record_plan_001.latest.json"
)
PLAN_MD_PATH = PLAN_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = "GROK_ABX_RUNES_RECONCILIATION_HELD_FOR_OPERATOR"
EXPECTED_SOURCE_NEXT_LANE = "GROK_ABX_RUNES_OPERATOR_REVIEW_DECISION_RECORD_PLAN"

DECISION_OPTIONS = [
    "HOLD_FOR_OPERATOR_REVIEW",
    "ACCEPT_GROK_ABX_RUNES_AS_EXTERNAL_BACKLOG",
    "REJECT_GROK_ABX_RUNES_CLAIMS_AS_NON_AUTHORITATIVE",
    "REQUEST_ADDITIONAL_GROK_OR_NOTION_EVIDENCE",
    "AUTHORIZE_SEPARATE_ADVISORY_RUNE_REGISTRATION_PLANNING_LANE",
]


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _authority_locks() -> dict[str, bool]:
    return {
        "authorization_record_creation": False,
        "auto_approval": False,
        "auto_continuation": False,
        "backlog_acceptance_auto_apply": False,
        "canon_mutation": False,
        "catalog_mutation": False,
        "code_creation": False,
        "decision_record_creation": False,
        "execution_authority": False,
        "github_writeback": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "pr_merge_authority": False,
        "projection_surface_mutation": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "yggdrasil_binding_mutation": False,
    }


def _source_record(packet: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "path": SOURCE_RECONCILIATION_JSON_PATH.as_posix(),
        "source_observed": bool(packet),
        "source_hash": str(packet.get("reconciliation_hash", NOT_COMPUTABLE)),
        "source_status": str(packet.get("reconciliation_status", NOT_COMPUTABLE)),
        "source_recommended_next_lane": str(
            packet.get("recommended_next_lane", NOT_COMPUTABLE)
        ),
        "source_valid_for_execution": bool(packet.get("valid_for_execution", True)),
        "source_rune_registration_authorized": bool(
            packet.get("rune_registration_authorized", True)
        ),
        "source_operator_authorization_observed": bool(
            packet.get("operator_authorization_observed", False)
        ),
        "source_notion_family_count": int(
            packet.get("grok_claim_digest", {}).get("notion_rune_family_count", 0)
        )
        if isinstance(packet.get("grok_claim_digest"), Mapping)
        else 0,
        "source_missing_representative_rune_count": len(
            packet.get("repo_evidence", {}).get(
                "representative_grok_rune_ids_missing_from_catalog", []
            )
        )
        if isinstance(packet.get("repo_evidence"), Mapping)
        else 0,
    }


def _required_field_groups() -> list[dict[str, Any]]:
    return [
        {
            "group_id": "operator_identity",
            "required": True,
            "fields": [
                "operator_id",
                "operator_name",
                "operator_role",
                "decision_timestamp_source_observed",
            ],
        },
        {
            "group_id": "source_scope_acknowledgement",
            "required": True,
            "fields": [
                "reviewed_grok_share_url",
                "reviewed_reconciliation_plan_path",
                "reviewed_reconciliation_plan_hash",
                "external_source_non_authoritative_acknowledged",
            ],
        },
        {
            "group_id": "grok_claim_disposition",
            "required": True,
            "fields": [
                "selected_decision",
                "decision_rationale",
                "accepted_family_ids",
                "rejected_claim_classes",
                "additional_evidence_requested",
            ],
        },
        {
            "group_id": "authority_boundary_acknowledgement",
            "required": True,
            "fields": [
                "no_catalog_mutation",
                "no_rune_registration",
                "no_yggdrasil_binding_mutation",
                "no_notion_writeback",
                "no_github_writeback",
                "no_pr_merge_authority",
                "no_runtime_mutation",
                "no_execution_authority",
            ],
        },
        {
            "group_id": "terminal_output_controls",
            "required": True,
            "fields": [
                "downstream_lane_disposition",
                "future_advisory_registration_planning_allowed",
                "future_registration_authorization_gate_required",
                "rollback_or_supersession_policy",
            ],
        },
    ]


def build_grok_abx_runes_operator_decision_record_plan(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source = _read_json(root / SOURCE_RECONCILIATION_JSON_PATH)
    source_record = _source_record(source)
    source_ready = (
        source_record["source_observed"] is True
        and source_record["source_status"] == EXPECTED_SOURCE_STATUS
        and source_record["source_recommended_next_lane"] == EXPECTED_SOURCE_NEXT_LANE
        and source_record["source_valid_for_execution"] is False
        and source_record["source_rune_registration_authorized"] is False
        and source_record["source_notion_family_count"] == 19
        and source_record["source_missing_representative_rune_count"] > 0
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "decision_record_plan_id": PLAN_ID,
        "status": (
            "GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_PLAN_READY"
            if source_ready
            else "GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_PLAN_BLOCKED"
        ),
        "decision_scope": "GROK_ABX_RUNES_EXTERNAL_WORK_CLASSIFICATION_DECISION",
        "source_reconciliation_plan": source_record,
        "recommended_default_decision": "HOLD_FOR_OPERATOR_REVIEW",
        "recommended_next_lane": (
            "GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_DRY_RUN"
            if source_ready
            else NOT_COMPUTABLE
        ),
        "recommended_next_action": (
            "perform a simulated dry run of the Grok ABX-Runes operator decision "
            "record shape without attesting operator input or creating the record"
            if source_ready
            else "restore the Grok ABX-Runes reconciliation plan before decision-record planning"
        ),
        "operator_input_required": True,
        "decision_record_created": False,
        "operator_attestation_created": False,
        "authorization_record_created": False,
        "decision_options": DECISION_OPTIONS,
        "required_field_groups": _required_field_groups(),
        "allowed_follow_on_actions": [
            "MAINTAIN_GROK_ABX_RUNES_OPERATOR_REVIEW_HOLD",
            "CLASSIFY_GROK_ABX_RUNES_AS_EXTERNAL_BACKLOG_ONLY",
            "PLAN_SEPARATE_ADVISORY_RUNE_REGISTRATION_REVIEW_LANE",
            "REQUEST_ADDITIONAL_EXTERNAL_EVIDENCE",
            "REJECT_EXTERNAL_GROK_CLAIMS",
        ],
        "disallowed_follow_on_actions": [
            "REGISTER_RUNE_CATALOG_ENTRIES",
            "MUTATE_YGGDRASIL_BINDINGS",
            "CREATE_RUNTIME_CODE",
            "CREATE_IMPLEMENTATION_PATCH",
            "MERGE_GITHUB_PR",
            "WRITE_BACK_TO_NOTION",
            "AUTHORIZE_EXECUTION",
            "AUTHORIZE_CANON_PROMOTION",
        ],
        "future_record_output_candidates": [
            "out/operator_review/grok_abx_runes_operator_decision_record_001.latest.json",
            "out/operator_review/grok_abx_runes_operator_decision_record_001.latest.md",
        ],
        "required_review_artifacts": [
            SOURCE_RECONCILIATION_JSON_PATH.as_posix(),
            "contracts/runes/catalog.v1.json",
            "out/sync/v2_hygiene_registration_readiness_audit/latest.json",
            "out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.json",
        ],
        "required_operator_review_items": [
            "confirm whether Grok ABX-Runes family claims should be retained as external backlog",
            "confirm that Grok merge and authorization claims do not override repo evidence",
            "decide whether a separate advisory-only rune registration planning lane may be proposed",
            "acknowledge that any future catalog or YGGDRASIL mutation requires a separate authorization gate",
        ],
        "source_family_ids_for_review": _string_list(
            [
                family.get("family_id")
                for family in source.get("grok_claim_digest", {}).get(
                    "notion_rune_families", []
                )
                if isinstance(family, Mapping)
            ]
        )
        if isinstance(source.get("grok_claim_digest"), Mapping)
        else [],
        "source_conflicting_claim_classes": _string_list(
            source.get("grok_claim_digest", {}).get("conflicting_claim_classes", [])
        )
        if isinstance(source.get("grok_claim_digest"), Mapping)
        else [],
        "plan_findings": [
            {
                "finding_id": "source_reconciliation_ready",
                "finding_status": "PASS" if source_ready else "FAIL_CLOSED",
                "authority_granted": False,
            },
            {
                "finding_id": "operator_decision_record_required_but_not_created",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
            {
                "finding_id": "rune_registration_remains_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
        ],
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authorization_granted": False,
        "implementation_authorized": False,
        "catalog_mutation_authorized": False,
        "rune_registration_authorized": False,
        "yggdrasil_binding_mutation_authorized": False,
        "schema_mutation_authorized": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "pr_merge_authority": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "canon_mutation": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_prepare_patch": False,
        "safe_to_auto_continue": False,
        "authority_locks": _authority_locks(),
        "downstream": NOT_COMPUTABLE,
    }
    return {**packet, "decision_record_plan_hash": canonical_hash(packet)}


def render_grok_abx_runes_operator_decision_record_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Grok ABX-Runes Operator Decision Record Plan",
        "",
        f"- decision_record_plan_id: {packet['decision_record_plan_id']}",
        f"- status: {packet['status']}",
        f"- decision_scope: {packet['decision_scope']}",
        f"- recommended_default_decision: {packet['recommended_default_decision']}",
        f"- decision_record_created: {packet['decision_record_created']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Decision Options",
    ]
    for option in packet["decision_options"]:
        lines.append(f"- {option}")
    lines.extend(["", "## Required Field Groups"])
    for group in packet["required_field_groups"]:
        lines.append(f"- {group['group_id']}: required={group['required']}")
    lines.extend(["", "## Findings"])
    for finding in packet["plan_findings"]:
        lines.append(
            f"- {finding['finding_id']}: {finding['finding_status']} "
            f"(authority_granted={finding['authority_granted']})"
        )
    return lines


def write_grok_abx_runes_operator_decision_record_plan(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_grok_abx_runes_operator_decision_record_plan(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / PLAN_JSON_PATH, packet)
    md_path = root / PLAN_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(render_grok_abx_runes_operator_decision_record_plan_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
    return packet
