from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.belief_graph_engine_advisory_receipt_implementation_plan import (
    OUT_JSON as BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "BeliefGraphEngineAdvisoryReceiptImplementationAuthorizationGate.v1"
GATE_ID = "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_GATE_001"
OUT_JSON = "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_gate_001.latest.json"
OUT_MD = "out/audit/belief_graph_engine_advisory_receipt_implementation_authorization_gate_001.latest.md"

BLOCKED_ACTIONS = [
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_CODE_CREATION",
    "BELIEF_GRAPH_ENGINE_RECEIPT_IMPLEMENTATION",
    "BELIEF_GRAPH_ENGINE_IMPLEMENTATION",
    "BELIEF_GRAPH_ENGINE_RUNTIME_CREATION",
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

ALLOWED_OPERATOR_DECISIONS = [
    "HOLD",
    "REQUEST_REVISED_IMPLEMENTATION_PLAN",
    "AUTHORIZE_SEPARATE_ADVISORY_RECEIPT_IMPLEMENTATION_RECORD_PLAN",
    "REJECT_IMPLEMENTATION",
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


def _authorization_checks(source_ready: bool) -> list[dict[str, Any]]:
    return [
        {
            "check_id": "authorization_check_001_source_plan_ready",
            "check_status": "PASS" if source_ready else "FAIL_CLOSED",
            "required_before": "operator authorization review",
            "grants_authority": False,
        },
        {
            "check_id": "authorization_check_002_operator_decision_required",
            "check_status": "HELD_FOR_OPERATOR",
            "required_before": "any advisory receipt code creation",
            "grants_authority": False,
        },
        {
            "check_id": "authorization_check_003_no_receipt_implementation",
            "check_status": "ENFORCED",
            "required_before": "receipt implementation PR",
            "grants_authority": False,
        },
        {
            "check_id": "authorization_check_004_no_runtime_dispatch",
            "check_status": "ENFORCED",
            "required_before": "belief graph engine runtime work",
            "grants_authority": False,
        },
        {
            "check_id": "authorization_check_005_no_writeback",
            "check_status": "ENFORCED",
            "required_before": "Notion or GitHub automation",
            "grants_authority": False,
        },
    ]


def build_belief_graph_engine_advisory_receipt_implementation_authorization_gate(
    *,
    repo_root: str | Path,
    implementation_plan_path: str | Path = BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    implementation_plan = _read_json(root / implementation_plan_path)
    source_ready = (
        implementation_plan.get("artifact_type")
        == "BeliefGraphEngineAdvisoryReceiptImplementationPlan.v1"
        and implementation_plan.get("plan_status")
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_PLAN_READY"
        and implementation_plan.get("recommended_next_lane")
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_GATE"
        and implementation_plan.get("valid_for_implementation") is False
        and implementation_plan.get("execution_authority") is False
        and implementation_plan.get("receipt_code_creation_authorized") is False
        and implementation_plan.get("receipt_implementation_authorized") is False
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "gate_id": GATE_ID,
        "gate_status": (
            "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "target_surface": "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION",
        "source_plan": {
            "path": Path(implementation_plan_path).as_posix(),
            "hash": _sha256(root / implementation_plan_path),
            "plan_status": str(implementation_plan.get("plan_status", "NOT_COMPUTABLE")),
            "recommended_next_lane": str(
                implementation_plan.get("recommended_next_lane", "NOT_COMPUTABLE")
            ),
            "source_ready": source_ready,
        },
        "authorization_scope": "ELIGIBILITY_REVIEW_ONLY",
        "authorization_eligible": source_ready,
        "requires_operator_decision": True,
        "selected_operator_decision": "HOLD",
        "allowed_operator_decisions": list(ALLOWED_OPERATOR_DECISIONS),
        "authorization_checks": _authorization_checks(source_ready),
        "blocked_actions": list(BLOCKED_ACTIONS),
        "recommended_next_lane": (
            "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_PLAN"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "recommended_next_action": (
            "prepare a separate operator authorization record plan; do not create receipt code "
            "or implement the Belief Graph Engine from this gate"
        ),
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


def write_belief_graph_engine_advisory_receipt_implementation_authorization_gate(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_belief_graph_engine_advisory_receipt_implementation_authorization_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Belief Graph Engine Advisory Receipt Implementation Authorization Gate",
        "",
        f"- gate_id: {packet['gate_id']}",
        f"- gate_status: {packet['gate_status']}",
        f"- target_surface: {packet['target_surface']}",
        f"- authorization_scope: {packet['authorization_scope']}",
        f"- authorization_eligible: {packet['authorization_eligible']}",
        f"- selected_operator_decision: {packet['selected_operator_decision']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- receipt_code_creation_authorized: {packet['receipt_code_creation_authorized']}",
        f"- receipt_implementation_authorized: {packet['receipt_implementation_authorized']}",
        f"- receipt_implementation_performed: {packet['receipt_implementation_performed']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Authorization Checks",
    ]
    for check in packet.get("authorization_checks", []):
        if isinstance(check, dict):
            lines.append(f"- {check['check_id']}: {check['check_status']}")
    lines.extend(["", "## Allowed Operator Decisions"])
    for decision in packet.get("allowed_operator_decisions", []):
        lines.append(f"- {decision}")
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- {action}")
    return lines


def write_belief_graph_engine_advisory_receipt_implementation_authorization_gate_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_belief_graph_engine_advisory_receipt_implementation_authorization_gate_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
