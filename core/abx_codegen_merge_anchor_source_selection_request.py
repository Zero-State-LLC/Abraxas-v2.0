from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan import (
    OUT_JSON as SOURCE_NORMALIZATION_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxCodegenMergeAnchorSourceSelectionRequest.v1"
REQUEST_ID = "abx_codegen_merge_anchor_source_selection_request_001"
REQUEST_JSON_PATH = Path(
    "out/operator_review/abx_codegen_merge_anchor_source_selection_request_001.latest.json"
)
REQUEST_MD_PATH = REQUEST_JSON_PATH.with_suffix(".md")

EXPECTED_NORMALIZATION_STATUS = (
    "ABX_CODEGEN_MERGE_ANCHOR_EVIDENCE_NORMALIZATION_PLAN_HELD_FOR_OPERATOR"
)

DECISION_OPTIONS = [
    "HOLD_FOR_OPERATOR_REVIEW",
    "SELECT_CANONICAL_SOURCE",
    "REQUEST_ADDITIONAL_NOTION_EVIDENCE",
    "REJECT_CANDIDATE_SOURCE",
    "CONFIRM_NO_IMPLEMENTATION_UNBLOCK",
]

REQUESTED_DECISION_IDS = [
    "select_canonical_prompting_upgrade_stack_source",
    "confirm_global_code_drop_envelope_rule_source",
    "confirm_subsystem_merge_map_002_candidate_mapping",
    "confirm_system_state_snapshot_alias_relationship",
    "confirm_no_implementation_unblock_from_normalization",
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
        "execution": False,
        "file_writeback": False,
        "forecast_routing": False,
        "github_writeback": False,
        "implementation_authorization": False,
        "implementation_unblock": False,
        "merge_anchor_mutation": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_decision_record_creation": False,
        "patch_application": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "source_promotion": False,
    }


def _decision_lookup(packet: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    decisions = packet.get("operator_required_decisions", [])
    if not isinstance(decisions, list):
        return {}
    return {
        str(decision.get("decision")): decision
        for decision in decisions
        if isinstance(decision, Mapping)
    }


def _anchor_lookup(packet: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    anchors = packet.get("normalized_anchor_evidence", [])
    if not isinstance(anchors, list):
        return {}
    return {
        str(anchor.get("anchor_id")): anchor
        for anchor in anchors
        if isinstance(anchor, Mapping)
    }


def _source_selection_requests(
    packet: Mapping[str, Any],
    *,
    source_ready: bool,
) -> list[dict[str, Any]]:
    if not source_ready:
        return []
    decisions = _decision_lookup(packet)
    anchors = _anchor_lookup(packet)
    requests: list[dict[str, Any]] = []
    for decision_id in REQUESTED_DECISION_IDS:
        decision = decisions.get(decision_id, {})
        anchor_id = str(decision.get("applies_to_anchor_id", "NOT_COMPUTABLE"))
        anchor = anchors.get(anchor_id, {}) if anchor_id != "all" else {}
        requests.append(
            {
                "decision": decision_id,
                "applies_to_anchor_id": anchor_id,
                "decision_status": str(decision.get("decision_status", "HELD_FOR_OPERATOR")),
                "candidate_page_id_or_url": str(anchor.get("notion_page_id_or_url", "NOT_APPLICABLE")),
                "candidate_source_title": str(anchor.get("source_observed_title", "NOT_APPLICABLE")),
                "normalization_status": str(anchor.get("normalization_status", "NOT_APPLICABLE")),
                "source_evidence_hash": str(anchor.get("source_evidence_hash", "NOT_APPLICABLE")),
                "requested_operator_action": _requested_operator_action(decision_id),
                "selection_authorized_by_request": False,
                "implementation_unblocked_by_request": False,
            }
        )
    return requests


def _requested_operator_action(decision_id: str) -> str:
    actions = {
        "select_canonical_prompting_upgrade_stack_source": (
            "provide_or_select_the_canonical_prompting_stack_page_or_hold"
        ),
        "confirm_global_code_drop_envelope_rule_source": (
            "confirm_candidate_code_drop_page_or_request_different_source"
        ),
        "confirm_subsystem_merge_map_002_candidate_mapping": (
            "confirm_candidate_merge_map_page_maps_to_requested_anchor_or_reject"
        ),
        "confirm_system_state_snapshot_alias_relationship": (
            "confirm_content_page_and_registry_alias_relationship_or_request_repair"
        ),
        "confirm_no_implementation_unblock_from_normalization": (
            "confirm_normalization_is_evidence_only_and_does_not_authorize_implementation"
        ),
    }
    return actions[decision_id]


def build_abx_codegen_merge_anchor_source_selection_request(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    source = _read_json(root / SOURCE_NORMALIZATION_PLAN_JSON)
    source_ready = (
        source.get("artifact_type")
        == "AbxCodegenIntelligenceSpineMergeAnchorEvidenceNormalizationPlan.v1"
        and source.get("merge_anchor_evidence_normalization_plan_status")
        == EXPECTED_NORMALIZATION_STATUS
        and source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and source.get("safe_to_auto_continue") is False
        and source.get("execution_authority") is False
        and source.get("valid_for_implementation") is False
        and source.get("normalization_summary", {}).get("operator_decision_required")
        is True
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "request_id": REQUEST_ID,
        "status": (
            "ABX_CODEGEN_MERGE_ANCHOR_SOURCE_SELECTION_REQUEST_HELD"
            if source_ready
            else "ABX_CODEGEN_MERGE_ANCHOR_SOURCE_SELECTION_REQUEST_BLOCKED"
        ),
        "decision_scope": "CODEGEN_MERGE_ANCHOR_CANONICAL_SOURCE_SELECTION_REQUIRED",
        "decision_question": (
            "Which Notion sources should be accepted as canonical Codegen merge "
            "anchors, which candidate sources should remain held, and should "
            "normalization remain evidence-only without implementation unblock?"
        ),
        "source_normalization_plan_path": SOURCE_NORMALIZATION_PLAN_JSON,
        "source_normalization_plan_hash": str(source.get("packet_hash", "NOT_COMPUTABLE")),
        "normalization_plan_ready_for_review": source_ready,
        "source_selection_requests": _source_selection_requests(
            source,
            source_ready=source_ready,
        ),
        "decision_options": DECISION_OPTIONS,
        "recommended_decision": "HOLD_FOR_OPERATOR_REVIEW",
        "recommended_next_patch": "NOT_COMPUTABLE",
        "required_operator_review_items": [
            "select or provide the canonical ABX Prompting Upgrade Stack source",
            "confirm or reject the candidate ABX Code Drop Envelope source",
            "confirm or reject the candidate Subsystem Merge Map source",
            "confirm the System State Snapshot source/registry alias relationship",
            "confirm normalization does not unblock Codegen implementation",
            "confirm no Notion writeback, GitHub writeback, or source mutation is authorized",
        ],
        "blocked_actions": [
            "CANONICAL_SOURCE_SELECTION_BY_AGENT",
            "NOTION_WRITEBACK",
            "NOTION_ANCHOR_MUTATION",
            "OPERATOR_DECISION_RECORD_CREATION",
            "OPERATOR_ATTESTATION_CREATION",
            "AUTHORIZATION_RECORD_CREATION",
            "CODEGEN_IMPLEMENTATION_UNBLOCK",
            "CONTRACTS_CODEGEN_DIRECTORY_CREATION",
            "CORE_CODEGEN_DIRECTORY_CREATION",
            "SCHEMA_CREATION_FROM_SOURCE_SELECTION",
            "MODULE_CREATION",
            "IMPLEMENTATION_PROMPT_EMISSION",
            "PATCH_APPLICATION",
            "FORECAST_ROUTING",
            "RUNTIME_MUTATION",
            "CANON_MUTATION",
            "GITHUB_WRITEBACK",
        ],
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "implementation_authorized": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "safe_to_auto_continue": False,
    }
    packet["request_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "request_hash"}
    )
    return packet


def render_abx_codegen_merge_anchor_source_selection_request_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Merge Anchor Source Selection Request",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `decision_scope`: `{packet['decision_scope']}`",
        f"- `recommended_decision`: `{packet['recommended_decision']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        f"- `implementation_authorized`: `{packet['implementation_authorized']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        f"- `valid_for_implementation`: `{packet['valid_for_implementation']}`",
        "",
        "## Source Selection Requests",
        "",
    ]
    for request in packet["source_selection_requests"]:
        lines.append(
            f"- `{request['decision']}` -> `{request['applies_to_anchor_id']}`: "
            f"`{request['decision_status']}`"
        )
    lines.extend(["", "## Decision Options", ""])
    for item in packet["decision_options"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Blocked Actions", ""])
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    return lines


def write_abx_codegen_merge_anchor_source_selection_request(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_codegen_merge_anchor_source_selection_request(root)
    write_canonical_json(target_root / REQUEST_JSON_PATH, packet)
    _write_markdown(
        target_root / REQUEST_MD_PATH,
        render_abx_codegen_merge_anchor_source_selection_request_markdown(packet),
    )
    return packet
