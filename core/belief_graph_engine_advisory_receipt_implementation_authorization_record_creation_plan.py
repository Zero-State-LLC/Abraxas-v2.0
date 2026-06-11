from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.belief_graph_engine_advisory_receipt_implementation_authorization_record_plan import (
    OUT_JSON as BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "BeliefGraphEngineAdvisoryReceiptImplementationAuthorizationRecordCreationPlan.v1"
PLAN_ID = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_PLAN_001"
)
OUT_JSON = "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan_001.latest.json"
OUT_MD = "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan_001.latest.md"

DENIED_AUTHORITY = [
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_CODE_CREATION",
    "BELIEF_GRAPH_ENGINE_RECEIPT_IMPLEMENTATION",
    "BELIEF_GRAPH_ENGINE_IMPLEMENTATION",
    "BELIEF_GRAPH_ENGINE_RUNTIME_CREATION",
    "AUTHORIZATION_RECORD_CREATION",
    "AUTHORIZATION_GRANT",
    "AUTHORIZATION_TOKEN_CREATION",
    "TRUTH_ASSIGNMENT",
    "BELIEF_PROMOTION",
    "FORECAST_ROUTING",
    "RUNTIME_DISPATCH_MUTATION",
    "CANON_MUTATION",
    "QUEUE_MUTATION",
    "SCHEDULER_MUTATION",
    "NOTION_WRITEBACK",
    "GITHUB_WRITEBACK",
    "ACTIVATION_OR_EXECUTION",
]


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _read_json(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _creation_plan_items(
    *,
    source_record_plan_path: str,
    source_record_plan_hash: str,
    source_ready: bool,
) -> list[dict[str, Any]]:
    return [
        {
            "creation_plan_item_id": "creation_plan_item_001_authorization_record",
            "source_record_plan_path": source_record_plan_path,
            "source_record_plan_hash": source_record_plan_hash,
            "planned_record_artifact_type": (
                "BeliefGraphEngineAdvisoryReceiptImplementationAuthorizationRecord.v1"
            ),
            "planned_record_output_path": (
                "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_001.latest.json"
            ),
            "creation_plan_status": "PLANNED_ONLY" if source_ready else "NOT_COMPUTABLE",
            "operator_approval_required": True,
            "operator_approved": False,
            "authorization_record_creation_allowed": False,
            "authorization_record_created": False,
            "authorization_granted": False,
            "authorization_token_created": False,
            "receipt_code_creation_authorized": False,
            "receipt_implementation_authorized": False,
            "execution_allowed": False,
            "blocking_reason": (
                "AUTHORIZATION_RECORD_CREATION_RESERVED_FOR_SEPARATE_GOVERNED_REVIEW"
            ),
        }
    ]


def _pre_creation_checks(source_ready: bool) -> list[dict[str, Any]]:
    return [
        {
            "check_id": "pre_creation_check_001_source_record_plan_ready",
            "check_status": "PASS" if source_ready else "FAIL_CLOSED",
            "required_before": "authorization record creation planning",
            "creation_allowed": False,
        },
        {
            "check_id": "pre_creation_check_002_operator_approval_required",
            "check_status": "HELD_FOR_OPERATOR",
            "required_before": "any authorization record creation",
            "creation_allowed": False,
        },
        {
            "check_id": "pre_creation_check_003_no_implicit_receipt_authority",
            "check_status": "ENFORCED",
            "required_before": "advisory receipt code creation",
            "creation_allowed": False,
        },
        {
            "check_id": "pre_creation_check_004_no_runtime_or_writeback",
            "check_status": "ENFORCED",
            "required_before": "runtime, queue, scheduler, Notion, or GitHub mutation",
            "creation_allowed": False,
        },
    ]


def build_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan(
    *,
    repo_root: str | Path,
    authorization_record_plan_path: str | Path = BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    record_plan = _read_json(root / authorization_record_plan_path)
    source_ready = (
        record_plan.get("artifact_type")
        == "BeliefGraphEngineAdvisoryReceiptImplementationAuthorizationRecordPlan.v1"
        and record_plan.get("record_plan_status")
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_PLAN_READY"
        and record_plan.get("recommended_next_lane")
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_PLAN"
        and record_plan.get("authorization_record_required") is True
        and record_plan.get("authorization_record_creation_allowed") is False
        and record_plan.get("authorization_record_created") is False
        and record_plan.get("authorization_granted") is False
        and record_plan.get("operator_approved") is False
        and record_plan.get("receipt_code_creation_authorized") is False
        and record_plan.get("receipt_implementation_authorized") is False
        and record_plan.get("execution_authority") is False
    )
    source_path = Path(authorization_record_plan_path).as_posix()
    source_hash = _sha256(root / authorization_record_plan_path)

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "creation_plan_status": (
            "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_PLAN_READY"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "target_surface": (
            "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION"
        ),
        "source_authorization_record_plan": {
            "path": source_path,
            "hash": source_hash,
            "record_plan_status": str(record_plan.get("record_plan_status", "NOT_COMPUTABLE")),
            "recommended_next_lane": str(record_plan.get("recommended_next_lane", "NOT_COMPUTABLE")),
            "source_ready": source_ready,
        },
        "authorization_record_creation_plan_only": True,
        "authorization_record_creation_required": source_ready,
        "authorization_record_creation_allowed": False,
        "authorization_record_created": False,
        "authorization_token_created": False,
        "operator_approved": False,
        "authorization_granted": False,
        "planned_record_output": {
            "path": (
                "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_001.latest.json"
            ),
            "artifact_type": (
                "BeliefGraphEngineAdvisoryReceiptImplementationAuthorizationRecord.v1"
            ),
            "overwrite_policy": "CREATE_ONLY_AFTER_SEPARATE_GOVERNED_OPERATOR_APPROVAL",
            "creation_allowed": False,
            "creation_authority": False,
        },
        "creation_plan_items": _creation_plan_items(
            source_record_plan_path=source_path,
            source_record_plan_hash=source_hash,
            source_ready=source_ready,
        ),
        "pre_creation_checks": _pre_creation_checks(source_ready),
        "recommended_next_lane": (
            "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_AUTHORIZATION_GATE"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "recommended_next_action": (
            "prepare a separate authorization record creation authorization gate only; "
            "do not create an authorization record, receipt code, or engine implementation from this plan"
        ),
        "denied_authority": list(DENIED_AUTHORITY),
        "receipt_code_creation_authorized": False,
        "receipt_implementation_authorized": False,
        "receipt_implementation_performed": False,
        "belief_graph_engine_implementation_authorized": False,
        "belief_graph_engine_implementation_performed": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "forecast_routing_allowed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "authority_locks": {
            "authorization_grant": False,
            "authorization_record_creation": False,
            "authorization_token_creation": False,
            "belief_promotion": False,
            "canon_mutation": False,
            "execution_authority": False,
            "forecast_routing": False,
            "github_writeback": False,
            "notion_writeback": False,
            "queue_mutation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "truth_assignment": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Belief Graph Engine Advisory Receipt Implementation Authorization Record Creation Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- creation_plan_status: {packet['creation_plan_status']}",
        f"- target_surface: {packet['target_surface']}",
        f"- authorization_record_creation_plan_only: {packet['authorization_record_creation_plan_only']}",
        f"- authorization_record_creation_required: {packet['authorization_record_creation_required']}",
        f"- authorization_record_creation_allowed: {packet['authorization_record_creation_allowed']}",
        f"- authorization_record_created: {packet['authorization_record_created']}",
        f"- authorization_token_created: {packet['authorization_token_created']}",
        f"- operator_approved: {packet['operator_approved']}",
        f"- authorization_granted: {packet['authorization_granted']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- execution_authority: {packet['execution_authority']}",
        "",
        "## Creation Plan Items",
    ]
    for item in packet.get("creation_plan_items", []):
        if isinstance(item, dict):
            lines.append(f"- {item['creation_plan_item_id']}: {item['creation_plan_status']}")
    lines.extend(["", "## Pre-Creation Checks"])
    for check in packet.get("pre_creation_checks", []):
        if isinstance(check, dict):
            lines.append(f"- {check['check_id']}: {check['check_status']}")
    lines.extend(["", "## Denied Authority"])
    for authority in packet.get("denied_authority", []):
        lines.append(f"- {authority}")
    return lines


def write_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
