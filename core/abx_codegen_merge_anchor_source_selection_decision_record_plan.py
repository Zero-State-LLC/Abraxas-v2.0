from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_merge_anchor_source_selection_request import (
    REQUEST_JSON_PATH as SOURCE_REQUEST_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxCodegenMergeAnchorSourceSelectionDecisionRecordPlan.v1"
PLAN_ID = "abx_codegen_merge_anchor_source_selection_decision_record_plan_001"
PLAN_JSON_PATH = Path(
    "out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_plan_001.latest.json"
)
PLAN_MD_PATH = PLAN_JSON_PATH.with_suffix(".md")

EXPECTED_SOURCE_STATUS = "ABX_CODEGEN_MERGE_ANCHOR_SOURCE_SELECTION_REQUEST_HELD"

ALLOWED_DECISION_VALUES = [
    "MAINTAIN_HOLD",
    "SELECT_CANONICAL_SOURCE",
    "REQUEST_ADDITIONAL_NOTION_EVIDENCE",
    "REJECT_CANDIDATE_SOURCE",
    "CONFIRM_ALIAS_RELATIONSHIP",
    "CONFIRM_NO_IMPLEMENTATION_UNBLOCK",
]

DISALLOWED_DECISION_VALUES = [
    "AUTHORIZE_CODEGEN_IMPLEMENTATION",
    "AUTHORIZE_CONTRACTS_CODEGEN_CREATION",
    "AUTHORIZE_CORE_CODEGEN_CREATION",
    "AUTHORIZE_SCHEMA_CREATION",
    "AUTHORIZE_MODULE_CREATION",
    "AUTHORIZE_IMPLEMENTATION_PROMPT_EMISSION",
    "AUTHORIZE_SOURCE_SELECTION_BY_AGENT",
    "AUTHORIZE_NOTION_WRITEBACK",
    "AUTHORIZE_GITHUB_WRITEBACK",
    "AUTHORIZE_RUNTIME_MUTATION",
    "AUTHORIZE_CANON_MUTATION",
    "AUTHORIZE_FORECAST_ROUTING",
]

BLOCKED_ACTIONS = [
    "OPERATOR_DECISION_RECORD_CREATION",
    "OPERATOR_ATTESTATION_CREATION",
    "AUTHORIZATION_RECORD_CREATION",
    "CANONICAL_SOURCE_SELECTION_BY_AGENT",
    "CODEGEN_IMPLEMENTATION_UNBLOCK",
    "CONTRACTS_CODEGEN_DIRECTORY_CREATION",
    "CORE_CODEGEN_DIRECTORY_CREATION",
    "SCHEMA_CREATION_FROM_SOURCE_SELECTION",
    "MODULE_CREATION",
    "IMPLEMENTATION_PROMPT_EMISSION",
    "PATCH_APPLICATION",
    "NOTION_WRITEBACK",
    "GITHUB_WRITEBACK",
    "FORECAST_ROUTING",
    "RUNTIME_MUTATION",
    "CANON_MUTATION",
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
        "canon_mutation": False,
        "canonical_source_selection": False,
        "code_generation": False,
        "code_mutation": False,
        "contracts_codegen_directory_creation": False,
        "core_codegen_directory_creation": False,
        "decision_record_creation": False,
        "execution": False,
        "file_writeback": False,
        "forecast_routing": False,
        "github_writeback": False,
        "implementation_authorization": False,
        "implementation_unblock": False,
        "merge_anchor_mutation": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "patch_application": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "source_promotion": False,
    }


def _source_selection_requirements(
    request: Mapping[str, Any],
    *,
    source_ready: bool,
) -> list[dict[str, Any]]:
    if not source_ready:
        return []
    source_requests = request.get("source_selection_requests", [])
    if not isinstance(source_requests, list):
        return []
    requirements: list[dict[str, Any]] = []
    for item in source_requests:
        if not isinstance(item, Mapping):
            continue
        requirements.append(
            {
                "decision": str(item.get("decision", "NOT_COMPUTABLE")),
                "applies_to_anchor_id": str(
                    item.get("applies_to_anchor_id", "NOT_COMPUTABLE")
                ),
                "candidate_page_id_or_url": str(
                    item.get("candidate_page_id_or_url", "NOT_COMPUTABLE")
                ),
                "candidate_source_title": str(
                    item.get("candidate_source_title", "NOT_COMPUTABLE")
                ),
                "source_evidence_hash": str(
                    item.get("source_evidence_hash", "NOT_COMPUTABLE")
                ),
                "required_record_fields": [
                    "selected_decision",
                    "operator_rationale",
                    "canonical_source_page_id_or_url",
                    "canonical_source_title",
                    "selection_confidence",
                    "authority_boundary_acknowledgement",
                ],
                "allowed_decision_values": ALLOWED_DECISION_VALUES,
                "implementation_unblocked_by_record": False,
                "selection_authorized_by_plan": False,
            }
        )
    return requirements


def build_abx_codegen_merge_anchor_source_selection_decision_record_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    request = _read_json(root / SOURCE_REQUEST_JSON)
    source_ready = (
        request.get("schema_version")
        == "AbxCodegenMergeAnchorSourceSelectionRequest.v1"
        and request.get("status") == EXPECTED_SOURCE_STATUS
        and request.get("recommended_next_patch") == "NOT_COMPUTABLE"
        and request.get("safe_to_auto_continue") is False
        and request.get("execution_authority") is False
        and request.get("valid_for_implementation") is False
        and request.get("implementation_authorized") is False
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "ABX_CODEGEN_MERGE_ANCHOR_SOURCE_SELECTION_DECISION_RECORD_PLAN_READY"
            if source_ready
            else "ABX_CODEGEN_MERGE_ANCHOR_SOURCE_SELECTION_DECISION_RECORD_PLAN_BLOCKED"
        ),
        "decision_record_plan_id": PLAN_ID,
        "decision_record_plan_hash": "",
        "decision_scope": "CODEGEN_MERGE_ANCHOR_CANONICAL_SOURCE_SELECTION_DECISION_RECORD_REQUIRED",
        "source_request_path": str(SOURCE_REQUEST_JSON),
        "source_request_hash": str(request.get("request_hash", "NOT_COMPUTABLE")),
        "source_request_ready": source_ready,
        "recommended_default_decision": "MAINTAIN_HOLD",
        "recommended_next_patch": "NOT_COMPUTABLE",
        "safe_to_auto_continue": False,
        "operator_input_required": True,
        "decision_record_created": False,
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
            "source_selection_request_hash_acknowledged",
            "normalization_plan_hash_acknowledged",
            "no_implementation_unblock_acknowledged",
        ],
        "required_acknowledgement_fields": [
            "advisory_only_acknowledged",
            "projection_only_acknowledged",
            "non_authoritative_acknowledged",
            "agent_source_selection_denied_acknowledged",
            "implementation_authority_denied_acknowledged",
            "execution_authority_denied_acknowledged",
            "notion_writeback_denied_acknowledged",
            "github_writeback_denied_acknowledged",
            "runtime_mutation_denied_acknowledged",
            "canon_mutation_denied_acknowledged",
        ],
        "required_evidence_fields": [
            "reviewed_source_selection_request_id",
            "reviewed_source_selection_request_hash",
            "reviewed_normalization_plan_hash",
            "reviewed_source_selection_requests",
        ],
        "required_per_anchor_decision_fields": [
            "anchor_id",
            "selected_decision",
            "canonical_source_page_id_or_url",
            "canonical_source_title",
            "operator_rationale",
            "authority_boundary_acknowledgement",
            "implementation_unblocked",
        ],
        "source_selection_requirements": _source_selection_requirements(
            request,
            source_ready=source_ready,
        ),
        "allowed_decision_values": ALLOWED_DECISION_VALUES,
        "disallowed_decision_values": DISALLOWED_DECISION_VALUES,
        "future_record_output_candidates": [
            "out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_001.latest.json",
            "out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_001.latest.md",
        ],
        "required_review_artifacts": [
            str(SOURCE_REQUEST_JSON),
            str(request.get("source_normalization_plan_path", "NOT_COMPUTABLE")),
        ],
        "blocked_actions": BLOCKED_ACTIONS,
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "implementation_authorized": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
    }
    packet["decision_record_plan_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "decision_record_plan_hash"}
    )
    return packet


def render_abx_codegen_merge_anchor_source_selection_decision_record_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Merge Anchor Source Selection Decision Record Plan",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `decision_scope`: `{packet['decision_scope']}`",
        f"- `recommended_default_decision`: `{packet['recommended_default_decision']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        f"- `decision_record_created`: `{packet['decision_record_created']}`",
        f"- `implementation_authorized`: `{packet['implementation_authorized']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        "",
        "## Required Decision Fields",
        "",
    ]
    for item in packet["required_decision_fields"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Source Selection Requirements", ""])
    for item in packet["source_selection_requirements"]:
        lines.append(
            f"- `{item['applies_to_anchor_id']}`: `{item['decision']}` "
            f"({item['candidate_page_id_or_url']})"
        )
    lines.extend(["", "## Blocked Actions", ""])
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    return lines


def write_abx_codegen_merge_anchor_source_selection_decision_record_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_codegen_merge_anchor_source_selection_decision_record_plan(root)
    write_canonical_json(target_root / PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / PLAN_MD_PATH,
        render_abx_codegen_merge_anchor_source_selection_decision_record_plan_markdown(
            packet
        ),
    )
    return packet
