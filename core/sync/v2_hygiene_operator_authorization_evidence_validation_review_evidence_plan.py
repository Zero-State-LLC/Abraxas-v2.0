from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_operator_authorization_evidence_validation_review import (
    REVIEW_JSON_PATH as SOURCE_REVIEW_JSON,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygieneOperatorAuthorizationEvidenceValidationReviewEvidencePlan.v1"
PLAN_ID = (
    "v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan_001"
)
PLAN_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan_001.latest.json"
)
PLAN_MD_PATH = PLAN_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = (
    "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_REVIEW_HELD_FOR_OPERATOR"
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


def _field_plan(group_id: str, fields: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "step_id": f"{group_id}_{idx:03d}",
            "field": field,
            "required": True,
            "attested": False,
        }
        for idx, field in enumerate(fields, start=1)
    ]


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _locks_all_false(value: Any) -> bool:
    return isinstance(value, Mapping) and bool(value) and all(
        item is False for item in value.values()
    )


def _source_ready(packet: Mapping[str, Any]) -> bool:
    return (
        packet.get("schema_version")
        == "V2HygieneOperatorAuthorizationEvidenceValidationReview.v1"
        and packet.get("status") == EXPECTED_SOURCE_STATUS
        and packet.get("source_validation_plan_ready") is True
        and packet.get("source_readiness") == "SOURCE_VALIDATION_PLAN_READY"
        and packet.get("selected_operator_decision") == "HOLD_FOR_OPERATOR_REVIEW"
        and packet.get("selected_follow_on_action")
        == "MAINTAIN_V2_HYGIENE_OPERATOR_AUTHORIZATION_HOLD"
        and packet.get("operator_review_required") is True
        and packet.get("operator_input_required") is True
        and packet.get("operator_attestations_present") is False
        and packet.get("operator_evidence_bundle_created") is False
        and packet.get("authorization_record_created") is False
        and packet.get("authorization_record_creation_authorized") is False
        and packet.get("implementation_authorized") is False
        and packet.get("v2_module_registration_authorized") is False
        and packet.get("rune_registration_authorized") is False
        and packet.get("projection_surface_mutation_authorized") is False
        and packet.get("schema_mutation_authorized") is False
        and packet.get("execution_authority") is False
        and packet.get("valid_for_authorization_record") is False
        and packet.get("valid_for_implementation") is False
        and packet.get("valid_for_execution") is False
        and packet.get("recommended_next_patch") == NOT_COMPUTABLE
        and packet.get("recommended_next_lane") == NOT_COMPUTABLE
        and packet.get("recommended_next_state") == "hold"
        and packet.get("notion_writeback_allowed") is False
        and packet.get("github_writeback_allowed") is False
        and packet.get("source_validation_blockers") == []
        and packet.get("source_blockers") == []
        and _locks_all_false(packet.get("authority_locks"))
    )


def build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    review = _read_json(root / SOURCE_REVIEW_JSON)
    review_observed = review is not None
    review = review or {}
    source_ready = review_observed and _source_ready(review)

    blockers = [] if source_ready else ["source_validation_review_not_ready"]
    if not review_observed:
        blockers = [
            "source_validation_review_missing_or_unreadable",
            f"source_path:{SOURCE_REVIEW_JSON}",
        ]

    operator_identity_fields = [
        "operator_id",
        "operator_name",
        "operator_role",
        "attestation_timestamp_source_observed",
        "operator_signature_reference",
    ]
    review_scope_fields = [
        "reviewed_validation_review_id",
        "reviewed_validation_review_hash",
        "reviewed_validation_plan_hash",
        "reviewed_source_status",
        "reviewed_terminal_hold_reason",
    ]
    authority_acknowledgement_fields = [
        "advisory_only_acknowledged",
        "projection_only_acknowledged",
        "non_authoritative_acknowledged",
        "evidence_bundle_creation_denied_acknowledged",
        "operator_attestation_creation_denied_acknowledged",
        "authorization_record_creation_denied_acknowledged",
        "implementation_authority_denied_acknowledged",
        "v2_module_registration_denied_acknowledged",
        "rune_registration_denied_acknowledged",
        "schema_mutation_denied_acknowledged",
        "projection_surface_mutation_denied_acknowledged",
        "notion_writeback_denied_acknowledged",
        "github_writeback_denied_acknowledged",
        "runtime_mutation_denied_acknowledged",
        "canon_mutation_denied_acknowledged",
        "execution_authority_denied_acknowledged",
    ]
    source_packet_confirmation_fields = [
        "validation_review_status_confirmed",
        "validation_plan_status_confirmed",
        "evidence_dry_run_status_confirmed",
        "evidence_request_status_confirmed",
        "operator_gate_status_confirmed",
        "p102g_plus_surface_status_confirmed",
    ]
    operator_disposition_fields = [
        "selected_disposition",
        "disposition_rationale",
        "hold_or_more_evidence_decision",
        "requested_follow_on_lane",
        "terminal_no_authority_summary",
    ]

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_REVIEW_EVIDENCE_PLAN_READY"
            if source_ready
            else "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_REVIEW_EVIDENCE_PLAN_BLOCKED"
        ),
        "plan_id": PLAN_ID,
        "plan_hash": "",
        "source_review_path": str(SOURCE_REVIEW_JSON),
        "source_review_observed": review_observed,
        "source_review_ready": source_ready,
        "source_review_status": str(review.get("status", NOT_COMPUTABLE)),
        "source_review_hash": str(review.get("review_hash", NOT_COMPUTABLE)),
        "source_review_terminal_hold_reason": str(
            review.get("terminal_hold_reason", NOT_COMPUTABLE)
        ),
        "source_validation_plan_hash": str(
            review.get("source_validation_plan_packet_hash", NOT_COMPUTABLE)
        ),
        "source_validation_blockers": _string_list(
            review.get("source_validation_blockers")
        ),
        "source_blockers": _string_list(review.get("source_blockers")),
        "evidence_plan_only": True,
        "operator_input_required": True,
        "recommended_default_disposition": "HOLD_FOR_OPERATOR_REVIEW",
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_state": "hold",
        "recommended_next_action": (
            "collect explicit external operator evidence for the held v2 hygiene "
            "validation review before any future evidence bundle or authorization "
            "record planning lane; do not create evidence, attestations, records, "
            "registrations, implementation patches, writeback, or execution"
        )
        if source_ready
        else "repair the source validation review before evidence planning",
        "safe_to_auto_continue": False,
        "operator_attestations_present": False,
        "operator_decision_attested": False,
        "evidence_bundle_created": False,
        "operator_evidence_bundle_created": False,
        "operator_attestation_created": False,
        "authorization_record_created": False,
        "authorization_record_creation_authorized": False,
        "implementation_authorized": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "projection_surface_mutation_authorized": False,
        "schema_mutation_authorized": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_authorization_record": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "evidence_bundle_groups": [
            {
                "group_id": "operator_identity",
                "required_fields": operator_identity_fields,
                "collection_steps": _field_plan(
                    "operator_identity", operator_identity_fields
                ),
            },
            {
                "group_id": "review_scope_acknowledgement",
                "required_fields": review_scope_fields,
                "collection_steps": _field_plan(
                    "review_scope_acknowledgement", review_scope_fields
                ),
            },
            {
                "group_id": "authority_acknowledgements",
                "required_fields": authority_acknowledgement_fields,
                "collection_steps": _field_plan(
                    "authority_acknowledgements",
                    authority_acknowledgement_fields,
                ),
            },
            {
                "group_id": "source_packet_confirmation",
                "required_fields": source_packet_confirmation_fields,
                "collection_steps": _field_plan(
                    "source_packet_confirmation",
                    source_packet_confirmation_fields,
                ),
            },
            {
                "group_id": "operator_disposition",
                "required_fields": operator_disposition_fields,
                "collection_steps": _field_plan(
                    "operator_disposition", operator_disposition_fields
                ),
            },
        ],
        "required_review_artifacts": [
            str(SOURCE_REVIEW_JSON),
            "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_plan_001.latest.json",
            "out/operator_review/v2_hygiene_operator_authorization_evidence_dry_run_001.latest.json",
            "out/operator_review/v2_hygiene_operator_authorization_evidence_request_plan_001.latest.json",
            "out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.json",
            "out/operator_review/p102g_plus_operator_decision_surface_audit_001.latest.json",
        ],
        "future_evidence_output_candidates": [
            "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_evidence_bundle_001.latest.json",
            "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_evidence_bundle_001.latest.md",
        ],
        "future_record_output_candidates": [
            "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_operator_decision_record_001.latest.json",
            "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_operator_decision_record_001.latest.md",
        ],
        "disallowed_follow_on_actions": [
            "OPERATOR_EVIDENCE_BUNDLE_CREATION",
            "OPERATOR_ATTESTATION_CREATION",
            "OPERATOR_DECISION_RECORD_CREATION",
            "AUTHORIZATION_RECORD_CREATION",
            "V2_MODULE_REGISTRATION",
            "RUNE_REGISTRATION",
            "HYGIENE_CODE_CREATION",
            "SCHEMA_FILE_CREATION",
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
        "evidence_readiness_summary": {
            "source_review_observed": review_observed,
            "source_review_ready": source_ready,
            "required_group_count": 5,
            "source_validation_blocker_count": len(
                _string_list(review.get("source_validation_blockers"))
            ),
            "blocker_count": len(blockers),
        },
        "blockers": blockers,
        "authority_locks": {
            "activation": False,
            "authorization_record_creation": False,
            "auto_approval": False,
            "auto_continuation": False,
            "canon_mutation": False,
            "decision_record_creation": False,
            "evidence_bundle_creation": False,
            "execution_authority": False,
            "forecast_routing": False,
            "github_writeback": False,
            "implementation_authorization": False,
            "notion_writeback": False,
            "operator_attestation": False,
            "projection_surface_mutation": False,
            "queue_mutation": False,
            "rune_registration": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "schema_mutation": False,
            "strict_mode_enablement": False,
            "token_minting": False,
            "v2_module_registration": False,
        },
    }
    packet["plan_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "plan_hash"}
    )
    return packet


def render_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Operator Authorization Evidence Validation Review Evidence Plan",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `source_review_ready`: `{packet['source_review_ready']}`",
        f"- `recommended_default_disposition`: `{packet['recommended_default_disposition']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        f"- `evidence_bundle_created`: `{packet['evidence_bundle_created']}`",
        f"- `authorization_record_created`: `{packet['authorization_record_created']}`",
        f"- `safe_to_auto_continue`: `{packet['safe_to_auto_continue']}`",
        "",
        "## Required Review Artifacts",
        "",
    ]
    for item in packet["required_review_artifacts"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Evidence Bundle Groups", ""])
    for group in packet["evidence_bundle_groups"]:
        lines.append(f"- `{group['group_id']}`")
        for field in group["required_fields"]:
            lines.append(f"  - `{field}`")
    if packet["blockers"]:
        lines.extend(["", "## Blockers", ""])
        for blocker in packet["blockers"]:
            lines.append(f"- `{blocker}`")
    return lines


def write_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = (
        build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan(
            root
        )
    )
    write_canonical_json(target_root / PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / PLAN_MD_PATH,
        render_v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan_markdown(
            packet
        ),
    )
    return packet
