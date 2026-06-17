from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_phase1_operator_review_request import (
    REQUEST_JSON_PATH as SOURCE_REVIEW_REQUEST_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxCodegenPhase1OperatorDecisionRecordPlan.v1"
PLAN_ID = "abx_codegen_phase1_operator_decision_record_plan_001"
PLAN_JSON_PATH = Path(
    "out/operator_review/abx_codegen_phase1_operator_decision_record_plan_001.latest.json"
)
PLAN_MD_PATH = PLAN_JSON_PATH.with_suffix(".md")

EXPECTED_SOURCE_STATUS = "ABX_CODEGEN_PHASE1_OPERATOR_REVIEW_REQUEST_HELD"

DECISION_OPTIONS = [
    "HOLD_FOR_OPERATOR_REVIEW",
    "APPROVE_PHASE1_IMPLEMENTATION_REVIEW_ONLY",
    "REQUEST_ADDITIONAL_EVIDENCE",
    "REJECT_PHASE1_IMPLEMENTATION_SCOPE",
]


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _authority_locks() -> dict[str, bool]:
    return {
        "authorization_record_creation": False,
        "authorization_record_lane_creation": False,
        "canon_mutation": False,
        "code_generation": False,
        "code_mutation": False,
        "contracts_codegen_directory_creation": False,
        "core_codegen_directory_creation": False,
        "core_harness_file_creation": False,
        "decision_record_creation": False,
        "execution": False,
        "file_writeback": False,
        "forecast_routing": False,
        "github_writeback": False,
        "implementation_authorization": False,
        "implementation_unblock": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "patch_application": False,
        "promotion_to_canary": False,
        "receipt_creation": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "shadow_replay_execution": False,
    }


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def build_abx_codegen_phase1_operator_decision_record_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    request = _read_json(root / SOURCE_REVIEW_REQUEST_JSON)
    source_ready = (
        request.get("schema_version") == "AbxCodegenPhase1OperatorReviewRequest.v1"
        and request.get("status") == EXPECTED_SOURCE_STATUS
        and request.get("recommended_next_patch") == "NOT_COMPUTABLE"
        and request.get("recommended_decision") == "HOLD_FOR_OPERATOR_REVIEW"
        and request.get("evidence_packet_ready_for_review") is True
        and request.get("safe_to_auto_continue") is False
        and request.get("implementation_authorized") is False
        and request.get("execution_authority") is False
        and request.get("valid_for_implementation") is False
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_RECORD_PLAN_READY"
            if source_ready
            else "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_RECORD_PLAN_BLOCKED"
        ),
        "decision_record_plan_id": PLAN_ID,
        "decision_record_plan_hash": "",
        "decision_scope": "PHASE1_CODEGEN_IMPLEMENTATION_REVIEW_DECISION_RECORD_REQUIRED",
        "source_review_request_path": str(SOURCE_REVIEW_REQUEST_JSON),
        "source_review_request_hash": str(request.get("request_hash", "NOT_COMPUTABLE")),
        "source_review_request_ready": source_ready,
        "source_decision_question": str(request.get("decision_question", "NOT_COMPUTABLE")),
        "recommended_default_decision": "HOLD_FOR_OPERATOR_REVIEW",
        "recommended_next_patch": "NOT_COMPUTABLE",
        "recommended_next_action": (
            "collect explicit external operator decision evidence before any future "
            "Phase 1 decision-record lane; keep implementation and authorization "
            "record creation denied unless a later governed record explicitly allows "
            "review-only progression"
        ),
        "safe_to_auto_continue": False,
        "operator_input_required": True,
        "decision_record_created": False,
        "authorization_record_created": False,
        "authorization_record_lane_authorized": False,
        "implementation_authorized": False,
        "implementation_unblocked": False,
        "decision_options": DECISION_OPTIONS,
        "required_operator_identity_fields": [
            "operator_id",
            "operator_name",
            "operator_role",
            "decision_timestamp_utc",
        ],
        "required_decision_fields": [
            "selected_decision",
            "decision_rationale",
            "decision_scope_acknowledged",
            "phase1_scope_reviewed",
            "review_only_progression_acknowledged",
            "separate_authorization_record_lane_required_if_approved",
        ],
        "required_acknowledgement_fields": [
            "advisory_only_acknowledged",
            "projection_only_acknowledged",
            "non_authoritative_acknowledged",
            "implementation_authority_denied_acknowledged",
            "execution_authority_denied_acknowledged",
            "shadow_replay_execution_denied_acknowledged",
            "authorization_record_creation_denied_acknowledged",
            "notion_writeback_denied_acknowledged",
            "github_writeback_denied_acknowledged",
            "runtime_mutation_denied_acknowledged",
            "canon_mutation_denied_acknowledged",
        ],
        "required_evidence_fields": [
            "reviewed_phase1_operator_review_request_id",
            "reviewed_phase1_operator_review_request_hash",
            "reviewed_phase1_operator_evidence_packet_hash",
            "reviewed_required_operator_review_items",
            "reviewed_blocked_actions",
        ],
        "required_output_fields": [
            "decision_record_id",
            "decision_record_hash",
            "decision_outcome_summary",
            "selected_follow_on_action",
            "terminal_authority_summary",
        ],
        "allowed_follow_on_actions": [
            "MAINTAIN_PHASE1_OPERATOR_REVIEW_HOLD",
            "PLAN_SEPARATE_AUTHORIZATION_RECORD_LANE_IF_APPROVED_REVIEW_ONLY",
            "REQUEST_ADDITIONAL_PHASE1_EVIDENCE",
            "REJECT_PHASE1_IMPLEMENTATION_SCOPE",
        ],
        "disallowed_follow_on_actions": _string_list(request.get("blocked_actions")),
        "future_record_output_candidates": [
            "out/operator_review/abx_codegen_phase1_operator_decision_record_001.latest.json",
            "out/operator_review/abx_codegen_phase1_operator_decision_record_001.latest.md",
        ],
        "required_review_artifacts": [
            str(SOURCE_REVIEW_REQUEST_JSON),
            str(request.get("source_evidence_packet_path", "NOT_COMPUTABLE")),
        ],
        "required_operator_review_items": _string_list(
            request.get("required_operator_review_items")
        ),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "authority_locks": _authority_locks(),
    }
    packet["decision_record_plan_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "decision_record_plan_hash"
        }
    )
    return packet


def render_abx_codegen_phase1_operator_decision_record_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Phase 1 Operator Decision Record Plan",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `decision_scope`: `{packet['decision_scope']}`",
        f"- `source_review_request_ready`: `{packet['source_review_request_ready']}`",
        f"- `recommended_default_decision`: `{packet['recommended_default_decision']}`",
        f"- `decision_record_created`: `{packet['decision_record_created']}`",
        f"- `authorization_record_lane_authorized`: `{packet['authorization_record_lane_authorized']}`",
        f"- `implementation_authorized`: `{packet['implementation_authorized']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Required Decision Fields",
        "",
    ]
    for item in packet["required_decision_fields"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Allowed Follow-on Actions", ""])
    for item in packet["allowed_follow_on_actions"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Required Review Artifacts", ""])
    for item in packet["required_review_artifacts"]:
        lines.append(f"- `{item}`")
    return lines


def write_abx_codegen_phase1_operator_decision_record_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_codegen_phase1_operator_decision_record_plan(root)
    write_canonical_json(target_root / PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / PLAN_MD_PATH,
        render_abx_codegen_phase1_operator_decision_record_plan_markdown(packet),
    )
    return packet
