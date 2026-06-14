from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_phase1_operator_decision_record_review import (
    REVIEW_JSON_PATH as SOURCE_REVIEW_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxCodegenPhase1OperatorDecisionEvidenceCollectionPlan.v1"
PLAN_ID = "abx_codegen_phase1_operator_decision_evidence_collection_plan_001"
PLAN_JSON_PATH = Path(
    "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_plan_001.latest.json"
)
PLAN_MD_PATH = PLAN_JSON_PATH.with_suffix(".md")

EXPECTED_SOURCE_STATUS = "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_RECORD_REVIEW_HELD_FOR_OPERATOR"


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
        }
        for idx, field in enumerate(fields, start=1)
    ]


def _authority_locks() -> dict[str, bool]:
    return {
        "activation": False,
        "auto_approval": False,
        "auto_continuation": False,
        "authorization_record_creation": False,
        "authorization_record_lane_creation": False,
        "canon_mutation": False,
        "code_generation": False,
        "code_mutation": False,
        "contracts_codegen_directory_creation": False,
        "core_codegen_directory_creation": False,
        "core_harness_file_creation": False,
        "decision_record_creation": False,
        "evidence_bundle_creation": False,
        "execution": False,
        "file_writeback": False,
        "fixture_mutation": False,
        "forecast_routing": False,
        "github_writeback": False,
        "implementation_authorization": False,
        "implementation_unblock": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "patch_application": False,
        "promotion_to_canary": False,
        "queue_mutation": False,
        "recommendation_routing": False,
        "receipt_creation": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "shadow_replay_execution": False,
    }


def build_abx_codegen_phase1_operator_decision_evidence_collection_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    review = _read_json(root / SOURCE_REVIEW_JSON)
    review_observed = review is not None
    review = review or {}

    source_ready = (
        review.get("schema_version") == "AbxCodegenPhase1OperatorDecisionRecordReview.v1"
        and review.get("status") == EXPECTED_SOURCE_STATUS
        and review.get("recommended_next_patch") == "NOT_COMPUTABLE"
        and review.get("safe_to_auto_continue") is False
        and review.get("operator_input_required") is True
        and review.get("operator_attestations_present") is False
        and review.get("decision_record_created") is False
        and review.get("authorization_record_lane_authorized") is False
        and review.get("implementation_unblocked") is False
        and review.get("execution_authority") is False
    )

    blockers = [] if source_ready else ["source_phase1_decision_record_review_not_ready"]
    if not review_observed:
        blockers = [
            "source_phase1_decision_record_review_missing_or_unreadable",
            f"source_path:{SOURCE_REVIEW_JSON}",
        ]

    operator_identity_fields = [
        "operator_id",
        "operator_name",
        "operator_role",
        "decision_timestamp_utc",
    ]
    decision_fields = [
        "selected_decision",
        "decision_rationale",
        "decision_scope_acknowledged",
        "phase1_scope_reviewed",
        "review_only_progression_acknowledged",
        "separate_authorization_record_lane_required_if_approved",
    ]
    acknowledgement_fields = [
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
    ]
    evidence_fields = [
        "reviewed_phase1_operator_decision_record_review_id",
        "reviewed_phase1_operator_decision_record_review_hash",
        "reviewed_phase1_operator_decision_record_dry_run_hash",
        "reviewed_phase1_operator_decision_record_plan_hash",
        "reviewed_phase1_operator_evidence_packet_hash",
        "reviewed_validation_blockers",
    ]
    output_fields = [
        "operator_evidence_bundle_id",
        "operator_evidence_bundle_hash",
        "evidence_collection_outcome_summary",
        "terminal_authority_summary",
    ]

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_PLAN_READY"
            if source_ready
            else "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_PLAN_BLOCKED"
        ),
        "plan_id": PLAN_ID,
        "plan_hash": "",
        "source_review_path": str(SOURCE_REVIEW_JSON),
        "source_review_hash": str(review.get("review_hash", "NOT_COMPUTABLE")),
        "source_review_ready": source_ready,
        "evidence_collection_only": True,
        "operator_input_required": True,
        "recommended_default_decision": "HOLD_FOR_OPERATOR_REVIEW",
        "recommended_next_patch": "NOT_COMPUTABLE",
        "recommended_next_action": (
            "collect explicit external operator evidence for the Phase 1 decision record; "
            "do not create a decision record, authorization-record lane, implementation patch, "
            "shadow replay, or Codegen execution"
        ),
        "safe_to_auto_continue": False,
        "decision_record_created": False,
        "authorization_record_created": False,
        "authorization_record_lane_authorized": False,
        "implementation_authorized": False,
        "implementation_unblocked": False,
        "shadow_replay_execution_authorized": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "evidence_bundle_groups": [
            {
                "group_id": "operator_identity",
                "required_fields": operator_identity_fields,
                "collection_steps": _field_plan("operator_identity", operator_identity_fields),
            },
            {
                "group_id": "operator_decision",
                "required_fields": decision_fields,
                "collection_steps": _field_plan("decision", decision_fields),
            },
            {
                "group_id": "authority_acknowledgements",
                "required_fields": acknowledgement_fields,
                "collection_steps": _field_plan("acknowledgement", acknowledgement_fields),
            },
            {
                "group_id": "provenance_evidence",
                "required_fields": evidence_fields,
                "collection_steps": _field_plan("evidence", evidence_fields),
            },
            {
                "group_id": "evidence_outputs",
                "required_fields": output_fields,
                "collection_steps": _field_plan("output", output_fields),
            },
        ],
        "required_review_artifacts": [
            str(SOURCE_REVIEW_JSON),
            "out/operator_review/abx_codegen_phase1_operator_decision_record_dry_run_001.latest.json",
            "out/operator_review/abx_codegen_phase1_operator_decision_record_plan_001.latest.json",
            "out/operator_review/abx_codegen_phase1_operator_review_request_001.latest.json",
            "out/audit/abx_codegen_intelligence_spine_phase1_operator_evidence_packet_001.latest.json",
        ],
        "future_evidence_output_candidates": [
            "out/operator_review/abx_codegen_phase1_operator_decision_evidence_bundle_001.latest.json",
            "out/operator_review/abx_codegen_phase1_operator_decision_evidence_bundle_001.latest.md",
        ],
        "future_record_output_candidates": [
            "out/operator_review/abx_codegen_phase1_operator_decision_record_001.latest.json",
            "out/operator_review/abx_codegen_phase1_operator_decision_record_001.latest.md",
        ],
        "disallowed_follow_on_actions": [
            "OPERATOR_DECISION_RECORD_CREATION",
            "OPERATOR_ATTESTATION_CREATION",
            "OPERATOR_EVIDENCE_BUNDLE_CREATION",
            "AUTHORIZATION_RECORD_CREATION",
            "AUTHORIZATION_RECORD_LANE_CREATION",
            "AUTO_APPROVAL",
            "AUTO_CONTINUATION",
            "CODEGEN_PHASE1_IMPLEMENTATION",
            "CORE_CODEGEN_SHADOW_REPLAY_HARNESS_CREATION",
            "SHADOW_REPLAY_EXECUTION",
            "SHADOW_IMPROVEMENT_RECEIPT_CREATION",
            "CODE_GENERATION",
            "CODE_MUTATION",
            "FILE_WRITEBACK",
            "NOTION_WRITEBACK",
            "GITHUB_WRITEBACK",
            "RUNTIME_MUTATION",
            "CANON_MUTATION",
            "QUEUE_MUTATION",
            "SCHEDULER_MUTATION",
            "FORECAST_ROUTING",
            "ACTIVATION",
            "RECOMMENDATION_ROUTING",
            "SCHEMA_MUTATION",
            "FIXTURE_MUTATION",
        ],
        "evidence_readiness_summary": {
            "source_review_observed": review_observed,
            "source_review_ready": source_ready,
            "required_group_count": 5,
            "blocker_count": len(blockers),
        },
        "blockers": blockers,
        "authority_locks": _authority_locks(),
    }
    packet["plan_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "plan_hash"}
    )
    return packet


def render_abx_codegen_phase1_operator_decision_evidence_collection_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Phase 1 Operator Decision Evidence Collection Plan",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `source_review_ready`: `{packet['source_review_ready']}`",
        f"- `recommended_default_decision`: `{packet['recommended_default_decision']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        f"- `decision_record_created`: `{packet['decision_record_created']}`",
        f"- `implementation_unblocked`: `{packet['implementation_unblocked']}`",
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


def write_abx_codegen_phase1_operator_decision_evidence_collection_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_plan(root)
    write_canonical_json(target_root / PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / PLAN_MD_PATH,
        render_abx_codegen_phase1_operator_decision_evidence_collection_plan_markdown(
            packet
        ),
    )
    return packet
