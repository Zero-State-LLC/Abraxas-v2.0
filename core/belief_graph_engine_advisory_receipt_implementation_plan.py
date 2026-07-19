from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.belief_graph_engine_advisory_receipt_contract_plan import (
    OUT_JSON as BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_CONTRACT_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "BeliefGraphEngineAdvisoryReceiptImplementationPlan.v1"
PLAN_ID = "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_PLAN_001"
OUT_JSON = "out/audit/belief_graph_engine_advisory_receipt_implementation_plan_001.latest.json"
OUT_MD = "out/audit/belief_graph_engine_advisory_receipt_implementation_plan_001.latest.md"

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


def _planned_implementation_steps() -> list[dict[str, Any]]:
    return [
        {
            "step_id": "implementation_plan_step_001_schema_authoring",
            "step_status": "PLANNED_ONLY",
            "planned_surface": "contracts/canon/belief_graph_engine_advisory_receipt.v1.schema.json",
            "requires_future_authorization": True,
            "creates_runtime_surface": False,
        },
        {
            "step_id": "implementation_plan_step_002_builder_authoring",
            "step_status": "PLANNED_ONLY",
            "planned_surface": "core/belief_graph_engine_advisory_receipt.py",
            "requires_future_authorization": True,
            "creates_runtime_surface": False,
        },
        {
            "step_id": "implementation_plan_step_003_runner_authoring",
            "step_status": "PLANNED_ONLY",
            "planned_surface": "scripts/run_belief_graph_engine_advisory_receipt.py",
            "requires_future_authorization": True,
            "creates_runtime_surface": False,
        },
        {
            "step_id": "implementation_plan_step_004_fixture_tests",
            "step_status": "PLANNED_ONLY",
            "planned_surface": "tests/test_belief_graph_engine_advisory_receipt.py",
            "requires_future_authorization": True,
            "creates_runtime_surface": False,
        },
        {
            "step_id": "implementation_plan_step_005_generated_receipt_outputs",
            "step_status": "PLANNED_ONLY",
            "planned_surface": "out/audit/belief_graph_engine_advisory_receipt_001.latest.json",
            "requires_future_authorization": True,
            "creates_runtime_surface": False,
        },
    ]


def _implementation_gates() -> list[dict[str, Any]]:
    return [
        {
            "gate_id": "implementation_gate_001_contract_plan_ready",
            "gate_status": "PASS_IF_SOURCE_READY",
            "required_before": "receipt implementation planning",
            "grants_authority": False,
        },
        {
            "gate_id": "implementation_gate_002_future_operator_authorization",
            "gate_status": "FUTURE_REVIEW_REQUIRED",
            "required_before": "any receipt code creation",
            "grants_authority": False,
        },
        {
            "gate_id": "implementation_gate_003_fail_closed_fixture_review",
            "gate_status": "FUTURE_REVIEW_REQUIRED",
            "required_before": "receipt implementation PR",
            "grants_authority": False,
        },
        {
            "gate_id": "implementation_gate_004_no_runtime_dispatch",
            "gate_status": "REQUIRED",
            "required_before": "receipt implementation PR",
            "grants_authority": False,
        },
        {
            "gate_id": "implementation_gate_005_no_writeback",
            "gate_status": "REQUIRED",
            "required_before": "receipt implementation PR",
            "grants_authority": False,
        },
    ]


def _planned_validation_commands() -> list[dict[str, Any]]:
    return [
        {
            "command_id": "validation_command_001_targeted_tests",
            "command": "python -m pytest tests/test_belief_graph_engine_advisory_receipt.py",
            "command_status": "PLANNED_ONLY",
        },
        {
            "command_id": "validation_command_002_fast_ci",
            "command": "python scripts/run_fast_ci.py",
            "command_status": "PLANNED_ONLY",
        },
        {
            "command_id": "validation_command_003_artifact_drift",
            "command": "python -m scripts.artifact.run_artifact_regeneration --check-drift",
            "command_status": "PLANNED_ONLY",
        },
    ]


def build_belief_graph_engine_advisory_receipt_implementation_plan(
    *,
    repo_root: str | Path,
    receipt_contract_plan_path: str | Path = BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_CONTRACT_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    contract_plan = _read_json(root / receipt_contract_plan_path)
    source_ready = (
        contract_plan.get("artifact_type")
        == "BeliefGraphEngineAdvisoryReceiptContractPlan.v1"
        and contract_plan.get("plan_status")
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_CONTRACT_PLAN_READY"
        and contract_plan.get("recommended_next_lane")
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_PLAN"
        and contract_plan.get("valid_for_implementation") is False
        and contract_plan.get("execution_authority") is False
        and contract_plan.get("receipt_implementation_performed") is False
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "plan_status": (
            "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_PLAN_READY"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "target_surface": "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION",
        "source_plan": {
            "path": Path(receipt_contract_plan_path).as_posix(),
            "hash": _sha256(root / receipt_contract_plan_path),
            "plan_status": str(contract_plan.get("plan_status", "NOT_COMPUTABLE")),
            "recommended_next_lane": str(contract_plan.get("recommended_next_lane", "NOT_COMPUTABLE")),
            "source_ready": source_ready,
        },
        "implementation_plan_scope": "ADVISORY_RECEIPT_IMPLEMENTATION_PLAN_ONLY",
        "planned_implementation_steps": _planned_implementation_steps(),
        "planned_validation_gates": _implementation_gates(),
        "planned_validation_commands": _planned_validation_commands(),
        "planned_delivery_surfaces": [
            "contracts/canon/belief_graph_engine_advisory_receipt.v1.schema.json",
            "core/belief_graph_engine_advisory_receipt.py",
            "scripts/run_belief_graph_engine_advisory_receipt.py",
            "tests/test_belief_graph_engine_advisory_receipt.py",
            "out/audit/belief_graph_engine_advisory_receipt_001.latest.json",
            "out/audit/belief_graph_engine_advisory_receipt_001.latest.md",
        ],
        "blocked_actions": list(BLOCKED_ACTIONS),
        "recommended_next_lane": "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_GATE",
        "recommended_next_action": (
            "prepare a separate operator authorization gate before any advisory receipt code creation; "
            "do not implement the receipt or engine from this plan"
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


def write_belief_graph_engine_advisory_receipt_implementation_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_belief_graph_engine_advisory_receipt_implementation_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Belief Graph Engine Advisory Receipt Implementation Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- plan_status: {packet['plan_status']}",
        f"- target_surface: {packet['target_surface']}",
        f"- implementation_plan_scope: {packet['implementation_plan_scope']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- receipt_code_creation_authorized: {packet['receipt_code_creation_authorized']}",
        f"- receipt_implementation_performed: {packet['receipt_implementation_performed']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Planned Implementation Steps",
    ]
    for step in packet.get("planned_implementation_steps", []):
        if isinstance(step, dict):
            lines.append(f"- {step['step_id']}: {step['step_status']} -> {step['planned_surface']}")
    lines.extend(["", "## Validation Gates"])
    for gate in packet.get("planned_validation_gates", []):
        if isinstance(gate, dict):
            lines.append(f"- {gate['gate_id']}: {gate['gate_status']}")
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- {action}")
    return lines


def write_belief_graph_engine_advisory_receipt_implementation_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(render_belief_graph_engine_advisory_receipt_implementation_plan_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
