from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_plan import (
    OUT_JSON as BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = (
    "BeliefGraphEngineAdvisoryReceiptImplementationAuthorizationRecordCreationAuthorizationGate.v1"
)
GATE_ID = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_AUTHORIZATION_GATE_001"
)
OUT_JSON = "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate_001.latest.json"
OUT_MD = "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate_001.latest.md"

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


def _authorization_prerequisites(source_ready: bool) -> list[dict[str, Any]]:
    return [
        {
            "check_id": "authorization_prerequisite_001_source_creation_plan_ready",
            "check_status": "PASS" if source_ready else "FAIL_CLOSED",
            "required_before": "record creation authorization review",
            "grants_authority": False,
        },
        {
            "check_id": "authorization_prerequisite_002_operator_approval_required",
            "check_status": "HELD_FOR_OPERATOR",
            "required_before": "any authorization record creation",
            "grants_authority": False,
        },
        {
            "check_id": "authorization_prerequisite_003_creation_locks_false",
            "check_status": "ENFORCED",
            "required_before": "authorization record creation",
            "grants_authority": False,
        },
        {
            "check_id": "authorization_prerequisite_004_no_runtime_or_writeback",
            "check_status": "ENFORCED",
            "required_before": "runtime, queue, scheduler, Notion, or GitHub mutation",
            "grants_authority": False,
        },
    ]


def build_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate(
    *,
    repo_root: str | Path,
    authorization_record_creation_plan_path: str | Path = BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    creation_plan = _read_json(root / authorization_record_creation_plan_path)
    planned_record_output = creation_plan.get("planned_record_output")
    output_dict = planned_record_output if isinstance(planned_record_output, dict) else {}
    source_ready = (
        creation_plan.get("artifact_type")
        == "BeliefGraphEngineAdvisoryReceiptImplementationAuthorizationRecordCreationPlan.v1"
        and creation_plan.get("creation_plan_status")
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_PLAN_READY"
        and creation_plan.get("recommended_next_lane")
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_AUTHORIZATION_GATE"
        and creation_plan.get("authorization_record_creation_required") is True
        and creation_plan.get("authorization_record_creation_allowed") is False
        and creation_plan.get("authorization_record_created") is False
        and creation_plan.get("authorization_token_created") is False
        and creation_plan.get("authorization_granted") is False
        and creation_plan.get("operator_approved") is False
        and creation_plan.get("receipt_code_creation_authorized") is False
        and creation_plan.get("receipt_implementation_authorized") is False
        and creation_plan.get("execution_authority") is False
        and isinstance(planned_record_output, dict)
        and output_dict.get("creation_allowed") is False
        and output_dict.get("creation_authority") is False
    )
    source_path = Path(authorization_record_creation_plan_path).as_posix()
    source_hash = _sha256(root / authorization_record_creation_plan_path)

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "gate_id": GATE_ID,
        "gate_status": (
            "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "target_surface": (
            "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_AUTHORIZATION"
        ),
        "source_authorization_record_creation_plan": {
            "path": source_path,
            "hash": source_hash,
            "creation_plan_status": str(
                creation_plan.get("creation_plan_status", "NOT_COMPUTABLE")
            ),
            "recommended_next_lane": str(
                creation_plan.get("recommended_next_lane", "NOT_COMPUTABLE")
            ),
            "source_ready": source_ready,
        },
        "authorization_scope": "RECORD_CREATION_ELIGIBILITY_REVIEW_ONLY",
        "record_creation_authorization_eligible": source_ready,
        "requires_operator_decision": True,
        "selected_operator_decision": "HOLD",
        "authorization_prerequisites": _authorization_prerequisites(source_ready),
        "planned_record_output_path": str(output_dict.get("path", "NOT_COMPUTABLE")),
        "planned_record_artifact_type": str(
            output_dict.get("artifact_type", "NOT_COMPUTABLE")
        ),
        "recommended_next_lane": (
            "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_RECORD_PLAN"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "recommended_next_action": (
            "prepare a separate authorization record creation record plan only; do not create "
            "an authorization record, mint a token, create receipt code, or implement the engine from this gate"
        ),
        "denied_authority": list(DENIED_AUTHORITY),
        "authorization_record_creation_allowed": False,
        "authorization_record_created": False,
        "authorization_token_created": False,
        "operator_approved": False,
        "authorization_granted": False,
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


def write_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Belief Graph Engine Advisory Receipt Implementation Authorization Record Creation Authorization Gate",
        "",
        f"- gate_id: {packet['gate_id']}",
        f"- gate_status: {packet['gate_status']}",
        f"- target_surface: {packet['target_surface']}",
        f"- authorization_scope: {packet['authorization_scope']}",
        f"- record_creation_authorization_eligible: {packet['record_creation_authorization_eligible']}",
        f"- selected_operator_decision: {packet['selected_operator_decision']}",
        f"- authorization_record_creation_allowed: {packet['authorization_record_creation_allowed']}",
        f"- authorization_record_created: {packet['authorization_record_created']}",
        f"- authorization_token_created: {packet['authorization_token_created']}",
        f"- operator_approved: {packet['operator_approved']}",
        f"- authorization_granted: {packet['authorization_granted']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- execution_authority: {packet['execution_authority']}",
        "",
        "## Authorization Prerequisites",
    ]
    for check in packet.get("authorization_prerequisites", []):
        if isinstance(check, dict):
            lines.append(f"- {check['check_id']}: {check['check_status']}")
    lines.extend(["", "## Denied Authority"])
    for authority in packet.get("denied_authority", []):
        lines.append(f"- {authority}")
    return lines


def write_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
