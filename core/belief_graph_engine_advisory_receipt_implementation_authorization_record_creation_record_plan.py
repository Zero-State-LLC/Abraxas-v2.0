from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_authorization_gate import (
    OUT_JSON as BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_AUTHORIZATION_GATE_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = (
    "BeliefGraphEngineAdvisoryReceiptImplementationAuthorizationRecordCreationRecordPlan.v1"
)
PLAN_ID = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_RECORD_PLAN_001"
)
OUT_JSON = "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_record_plan_001.latest.json"
OUT_MD = "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_record_plan_001.latest.md"

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


def _record_requirements(source_ready: bool) -> list[dict[str, Any]]:
    return [
        {
            "requirement_id": "record_requirement_001_source_gate_held",
            "requirement_status": "SATISFIED" if source_ready else "FAIL_CLOSED",
            "required_before": "record creation record planning",
            "record_creation_allowed": False,
        },
        {
            "requirement_id": "record_requirement_002_operator_decision_evidence",
            "requirement_status": "HELD_FOR_OPERATOR",
            "required_before": "any authorization record creation record",
            "record_creation_allowed": False,
        },
        {
            "requirement_id": "record_requirement_003_no_implicit_grant",
            "requirement_status": "ENFORCED",
            "required_before": "authorization grant or receipt code creation",
            "record_creation_allowed": False,
        },
        {
            "requirement_id": "record_requirement_004_replay_hash_binding",
            "requirement_status": "PLANNED_ONLY",
            "required_before": "future record creation record review",
            "record_creation_allowed": False,
        },
    ]


def build_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_record_plan(
    *,
    repo_root: str | Path,
    authorization_record_creation_authorization_gate_path: str | Path = BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_AUTHORIZATION_GATE_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    creation_gate = _read_json(root / authorization_record_creation_authorization_gate_path)
    source_ready = (
        creation_gate.get("artifact_type")
        == "BeliefGraphEngineAdvisoryReceiptImplementationAuthorizationRecordCreationAuthorizationGate.v1"
        and creation_gate.get("gate_status")
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
        and creation_gate.get("recommended_next_lane")
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_RECORD_PLAN"
        and creation_gate.get("record_creation_authorization_eligible") is True
        and creation_gate.get("selected_operator_decision") == "HOLD"
        and creation_gate.get("authorization_record_creation_allowed") is False
        and creation_gate.get("authorization_record_created") is False
        and creation_gate.get("authorization_token_created") is False
        and creation_gate.get("authorization_granted") is False
        and creation_gate.get("operator_approved") is False
        and creation_gate.get("receipt_code_creation_authorized") is False
        and creation_gate.get("receipt_implementation_authorized") is False
        and creation_gate.get("execution_authority") is False
    )
    source_path = Path(authorization_record_creation_authorization_gate_path).as_posix()
    source_hash = _sha256(root / authorization_record_creation_authorization_gate_path)

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "record_plan_status": (
            "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_RECORD_PLAN_READY"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "target_surface": (
            "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_RECORD"
        ),
        "source_authorization_record_creation_authorization_gate": {
            "path": source_path,
            "hash": source_hash,
            "gate_status": str(creation_gate.get("gate_status", "NOT_COMPUTABLE")),
            "recommended_next_lane": str(
                creation_gate.get("recommended_next_lane", "NOT_COMPUTABLE")
            ),
            "selected_operator_decision": str(
                creation_gate.get("selected_operator_decision", "NOT_COMPUTABLE")
            ),
            "source_ready": source_ready,
        },
        "authorization_record_creation_record_plan_only": True,
        "authorization_record_creation_record_required": source_ready,
        "authorization_record_creation_record_allowed": False,
        "authorization_record_creation_record_created": False,
        "authorization_record_creation_allowed": False,
        "authorization_record_created": False,
        "authorization_token_created": False,
        "operator_approved": False,
        "authorization_granted": False,
        "planned_record_creation_record": {
            "artifact_type": (
                "BeliefGraphEngineAdvisoryReceiptImplementationAuthorizationRecordCreationRecord.v1"
            ),
            "record_scope": "ADVISORY_RECEIPT_AUTHORIZATION_RECORD_CREATION_DECISION_ONLY",
            "source_authorization_gate_path": source_path,
            "source_authorization_gate_hash": source_hash,
            "planned_authorization_record_output_path": str(
                creation_gate.get("planned_record_output_path", "NOT_COMPUTABLE")
            ),
            "planned_authorization_record_artifact_type": str(
                creation_gate.get("planned_record_artifact_type", "NOT_COMPUTABLE")
            ),
            "operator_approval_required": True,
            "operator_approved": False,
            "authorization_granted": False,
            "authorization_record_creation_allowed": False,
            "authorization_record_created": False,
            "authorization_token_created": False,
            "record_creation_allowed": False,
            "record_created": False,
            "execution_authority": False,
            "packet_hash_required": True,
        },
        "record_requirements": _record_requirements(source_ready),
        "recommended_next_lane": (
            "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_RECORD_CREATION_PLAN"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "recommended_next_action": (
            "prepare a separate authorization record creation record-creation plan only; "
            "do not create a record, mint a token, create receipt code, or implement the engine from this plan"
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
            "authorization_record_creation_record_creation": False,
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


def write_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_record_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_record_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Belief Graph Engine Advisory Receipt Implementation Authorization Record Creation Record Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- record_plan_status: {packet['record_plan_status']}",
        f"- target_surface: {packet['target_surface']}",
        f"- authorization_record_creation_record_plan_only: {packet['authorization_record_creation_record_plan_only']}",
        f"- authorization_record_creation_record_required: {packet['authorization_record_creation_record_required']}",
        f"- authorization_record_creation_record_allowed: {packet['authorization_record_creation_record_allowed']}",
        f"- authorization_record_creation_record_created: {packet['authorization_record_creation_record_created']}",
        f"- authorization_record_creation_allowed: {packet['authorization_record_creation_allowed']}",
        f"- authorization_record_created: {packet['authorization_record_created']}",
        f"- authorization_token_created: {packet['authorization_token_created']}",
        f"- authorization_granted: {packet['authorization_granted']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- execution_authority: {packet['execution_authority']}",
        "",
        "## Record Requirements",
    ]
    for requirement in packet.get("record_requirements", []):
        if isinstance(requirement, dict):
            lines.append(
                f"- {requirement['requirement_id']}: {requirement['requirement_status']}"
            )
    lines.extend(["", "## Denied Authority"])
    for authority in packet.get("denied_authority", []):
        lines.append(f"- {authority}")
    return lines


def write_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_record_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_record_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
