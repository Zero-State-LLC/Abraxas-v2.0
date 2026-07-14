from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_loop_awareness_alignment_plan import (
    OUT_JSON as SOURCE_ALIGNMENT_PLAN_JSON,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

ARTIFACT_TYPE = "V2HygieneLoopAwarenessOperatorAuthorizationGate.v1"
GATE_ID = "V2_HYGIENE_LOOP_AWARENESS_OPERATOR_AUTHORIZATION_GATE_001"
OUT_JSON = "out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.json"
OUT_MD = "out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.md"
EXPECTED_SOURCE_STATUS = "V2_HYGIENE_LOOP_AWARENESS_ALIGNMENT_PLAN_READY"

REQUIRED_OPERATOR_AUTHORIZATION_FIELDS = [
    "operator_id",
    "operator_name",
    "operator_role",
    "authorization_timestamp_utc",
    "authorization_scope_acknowledged",
    "reviewed_alignment_plan_hash",
    "approved_workstreams",
    "denied_workstreams",
    "authority_boundary_acknowledged",
    "no_auto_continuation_acknowledged",
]

ALLOWED_OPERATOR_DECISIONS = [
    "HOLD",
    "REQUEST_REVISED_ALIGNMENT_PLAN",
    "AUTHORIZE_SEPARATE_V2_HYGIENE_RECORD_PLAN",
    "REJECT_ALIGNMENT",
]


def _read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _source_hash(path: Path) -> str:
    try:
        return canonical_hash(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return NOT_COMPUTABLE


def _authority_locks() -> dict[str, bool]:
    return {
        "auto_continuation": False,
        "auto_patch_generation": False,
        "canon_mutation": False,
        "execution_authority": False,
        "forecast_routing": False,
        "github_writeback": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_authorization_record_creation": False,
        "projection_surface_mutation": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "token_minting": False,
        "v2_module_registration": False,
    }


def _alignment_ready(plan: Mapping[str, Any]) -> bool:
    return (
        plan.get("artifact_type") == "V2HygieneLoopAwarenessAlignmentPlan.v1"
        and plan.get("plan_status") == EXPECTED_SOURCE_STATUS
        and plan.get("recommended_next_patch") == NOT_COMPUTABLE
        and plan.get("safe_to_prepare_patch") is False
        and plan.get("safe_to_auto_continue") is False
        and plan.get("advisory_only") is True
        and plan.get("valid_for_execution") is False
        and plan.get("notion_writeback_allowed") is False
        and plan.get("github_writeback_allowed") is False
        and plan.get("canon_mutation") is False
        and plan.get("runtime_mutation") is False
        and plan.get("queue_mutation") is False
        and plan.get("scheduler_mutation") is False
        and plan.get("schema_mutation") is False
        and plan.get("execution_authority") is False
        and plan.get("downstream") == NOT_COMPUTABLE
    )


def _authorization_checks(source_ready: bool) -> list[dict[str, Any]]:
    return [
        {
            "check_id": "v2_hygiene_gate_001_alignment_plan_ready",
            "check_status": "PASS" if source_ready else "FAIL_CLOSED",
            "required_before": "operator authorization review",
            "grants_authority": False,
        },
        {
            "check_id": "v2_hygiene_gate_002_operator_decision_required",
            "check_status": "HELD_FOR_OPERATOR",
            "required_before": "any v2 hygiene module, rune, schema, or projection mutation",
            "grants_authority": False,
        },
        {
            "check_id": "v2_hygiene_gate_003_no_record_creation",
            "check_status": "ENFORCED",
            "required_before": "authorization record creation",
            "grants_authority": False,
        },
        {
            "check_id": "v2_hygiene_gate_004_no_writeback",
            "check_status": "ENFORCED",
            "required_before": "Notion or GitHub writeback",
            "grants_authority": False,
        },
        {
            "check_id": "v2_hygiene_gate_005_no_execution",
            "check_status": "ENFORCED",
            "required_before": "runtime, scheduler, queue, or execution work",
            "grants_authority": False,
        },
    ]


def build_v2_hygiene_loop_awareness_operator_authorization_gate(
    repo_root: str | Path = ".",
    source_alignment_plan_path: str | Path = SOURCE_ALIGNMENT_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_alignment_plan_path
    plan = _read_json(source_path)
    source_observed = bool(plan)
    source_ready = source_observed and _alignment_ready(plan)
    gate_status = (
        "V2_HYGIENE_LOOP_AWARENESS_OPERATOR_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
        if source_ready
        else NOT_COMPUTABLE
    )

    blocked_actions = list(
        dict.fromkeys(
            [
                *[
                    str(item)
                    for item in plan.get("blocked_actions", [])
                    if isinstance(item, str)
                ],
                "OPERATOR_AUTHORIZATION_RECORD_CREATION",
                "V2_HYGIENE_DIRECT_MUTATION",
            ]
        )
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "gate_id": GATE_ID,
        "gate_status": gate_status,
        "target_surface": "V2_HYGIENE_LOOP_AWARENESS_ALIGNMENT",
        "source_alignment_plan": {
            "path": Path(source_alignment_plan_path).as_posix(),
            "hash": _source_hash(source_path),
            "plan_status": str(plan.get("plan_status", NOT_COMPUTABLE)),
            "source_ready": source_ready,
        },
        "authorization_scope": "V2_HYGIENE_ALIGNMENT_OPERATOR_REVIEW_ONLY",
        "authorization_eligible": source_ready,
        "requires_operator_decision": True,
        "selected_operator_decision": "HOLD",
        "allowed_operator_decisions": list(ALLOWED_OPERATOR_DECISIONS),
        "required_operator_authorization_fields": list(REQUIRED_OPERATOR_AUTHORIZATION_FIELDS),
        "source_alignment_required_workstreams": [
            str(item) for item in plan.get("alignment_required_workstreams", [])
        ]
        if isinstance(plan.get("alignment_required_workstreams", []), list)
        else [],
        "authorization_checks": _authorization_checks(source_ready),
        "blocked_actions": blocked_actions,
        "recommended_next_action": (
            "collect explicit external operator authorization evidence before any "
            "v2 hygiene record planning, module registration, rune registration, "
            "projection update, schema mutation, writeback, or execution"
            if source_ready
            else "repair v2 hygiene alignment plan evidence before operator authorization review"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "operator_authorization_observed": False,
        "operator_authorization_record_created": False,
        "authorization_granted": False,
        "authorization_record_creation_authorized": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "projection_surface_mutation_authorized": False,
        "schema_mutation_authorized": False,
        "implementation_authorized": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "safe_to_prepare_patch": False,
        "safe_to_auto_continue": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "forecast_routing": False,
        "authority_locks": _authority_locks(),
        "downstream": NOT_COMPUTABLE,
    }
    return {**base, "gate_hash": canonical_hash(base)}


def write_v2_hygiene_loop_awareness_operator_authorization_gate(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_v2_hygiene_loop_awareness_operator_authorization_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Loop-Awareness Operator Authorization Gate",
        "",
        f"- gate_id: {packet['gate_id']}",
        f"- gate_status: {packet['gate_status']}",
        f"- authorization_scope: {packet['authorization_scope']}",
        f"- authorization_eligible: {packet['authorization_eligible']}",
        f"- selected_operator_decision: {packet['selected_operator_decision']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- recommended_next_patch: {packet['recommended_next_patch']}",
        f"- authorization_granted: {packet['authorization_granted']}",
        f"- operator_authorization_record_created: {packet['operator_authorization_record_created']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        "",
        "## Required Operator Authorization Fields",
    ]
    for field in packet["required_operator_authorization_fields"]:
        lines.append(f"- {field}")
    lines.extend(["", "## Authorization Checks"])
    for check in packet.get("authorization_checks", []):
        if isinstance(check, Mapping):
            lines.append(f"- {check['check_id']}: {check['check_status']}")
    lines.extend(["", "## Blocked Actions"])
    for action in packet["blocked_actions"]:
        lines.append(f"- {action}")
    return lines


def write_v2_hygiene_loop_awareness_operator_authorization_gate_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(render_v2_hygiene_loop_awareness_operator_authorization_gate_markdown(packet)) + "\n",
        encoding="utf-8",
    )
