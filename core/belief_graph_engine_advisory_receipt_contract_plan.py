from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.belief_graph_engine_advisory_spec_plan import (
    OUT_JSON as BELIEF_GRAPH_ENGINE_ADVISORY_SPEC_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "BeliefGraphEngineAdvisoryReceiptContractPlan.v1"
PLAN_ID = "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_CONTRACT_PLAN_001"
OUT_JSON = "out/audit/belief_graph_engine_advisory_receipt_contract_plan_001.latest.json"
OUT_MD = "out/audit/belief_graph_engine_advisory_receipt_contract_plan_001.latest.md"

BLOCKED_ACTIONS = [
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


def _planned_receipt_fields() -> list[dict[str, Any]]:
    return [
        {
            "field_name": "receipt_id",
            "field_status": "PLANNED_ONLY",
            "required": True,
            "semantics": "stable receipt identifier for the future advisory receipt",
        },
        {
            "field_name": "source_packet_hashes",
            "field_status": "PLANNED_ONLY",
            "required": True,
            "semantics": "canonical hashes of consumed Belief Graph primitive packets or fixtures",
        },
        {
            "field_name": "advisory_findings",
            "field_status": "PLANNED_ONLY",
            "required": True,
            "semantics": "deterministic validation findings without truth assignment",
        },
        {
            "field_name": "authority_locks",
            "field_status": "PLANNED_ONLY",
            "required": True,
            "semantics": "explicit false authority booleans for promotion, forecast, runtime, canon, queue, scheduler, and writeback",
        },
        {
            "field_name": "operator_gate_references",
            "field_status": "PLANNED_ONLY",
            "required": True,
            "semantics": "future operator gates required before implementation or activation",
        },
        {
            "field_name": "recommended_next_lane",
            "field_status": "PLANNED_ONLY",
            "required": True,
            "semantics": "next advisory planning lane only; no execution route",
        },
    ]


def _validation_gates() -> list[dict[str, Any]]:
    return [
        {
            "gate_id": "source_spec_plan_ready",
            "gate_status": "PASS_IF_SOURCE_READY",
            "required_before": "receipt contract authoring",
            "grants_authority": False,
        },
        {
            "gate_id": "no_truth_assignment_fields",
            "gate_status": "REQUIRED",
            "required_before": "receipt schema approval",
            "grants_authority": False,
        },
        {
            "gate_id": "authority_locks_required",
            "gate_status": "REQUIRED",
            "required_before": "receipt schema approval",
            "grants_authority": False,
        },
        {
            "gate_id": "fixture_fail_closed_cases_required",
            "gate_status": "REQUIRED",
            "required_before": "future receipt implementation",
            "grants_authority": False,
        },
        {
            "gate_id": "operator_authorization_required_for_implementation",
            "gate_status": "FUTURE_REVIEW_REQUIRED",
            "required_before": "any receipt implementation or engine implementation",
            "grants_authority": False,
        },
    ]


def _planned_fixtures() -> list[dict[str, Any]]:
    return [
        {
            "fixture_id": "receipt_fixture_001_minimal_valid_packet",
            "fixture_status": "PLANNED_ONLY",
            "expected_receipt_status": "ADVISORY_RECEIPT_READY",
            "truth_assignment_allowed": False,
        },
        {
            "fixture_id": "receipt_fixture_002_conflicting_packet",
            "fixture_status": "PLANNED_ONLY",
            "expected_receipt_status": "ADVISORY_RECEIPT_CONFLICT_RECORDED",
            "truth_assignment_allowed": False,
        },
        {
            "fixture_id": "receipt_fixture_003_missing_hash",
            "fixture_status": "PLANNED_ONLY",
            "expected_receipt_status": "NOT_COMPUTABLE",
            "truth_assignment_allowed": False,
        },
    ]


def build_belief_graph_engine_advisory_receipt_contract_plan(
    *,
    repo_root: str | Path,
    advisory_spec_plan_path: str | Path = BELIEF_GRAPH_ENGINE_ADVISORY_SPEC_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    spec_plan = _read_json(root / advisory_spec_plan_path)
    source_ready = (
        spec_plan.get("artifact_type") == "BeliefGraphEngineAdvisorySpecPlan.v1"
        and spec_plan.get("plan_status") == "BELIEF_GRAPH_ENGINE_ADVISORY_SPEC_PLAN_READY"
        and spec_plan.get("recommended_next_lane")
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_CONTRACT_PLAN"
        and spec_plan.get("valid_for_implementation") is False
        and spec_plan.get("execution_authority") is False
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "plan_status": (
            "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_CONTRACT_PLAN_READY"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "target_surface": "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT",
        "source_plan": {
            "path": Path(advisory_spec_plan_path).as_posix(),
            "hash": _sha256(root / advisory_spec_plan_path),
            "plan_status": str(spec_plan.get("plan_status", "NOT_COMPUTABLE")),
            "recommended_next_lane": str(spec_plan.get("recommended_next_lane", "NOT_COMPUTABLE")),
            "source_ready": source_ready,
        },
        "contract_plan_scope": "ADVISORY_RECEIPT_CONTRACT_PLAN_ONLY",
        "planned_receipt_schema": {
            "schema_path": "contracts/canon/belief_graph_engine_advisory_receipt.v1.schema.json",
            "artifact_type": "BeliefGraphEngineAdvisoryReceipt.v1",
            "status_values": [
                "ADVISORY_RECEIPT_READY",
                "ADVISORY_RECEIPT_CONFLICT_RECORDED",
                "NOT_COMPUTABLE",
            ],
            "planned_fields": _planned_receipt_fields(),
        },
        "planned_delivery_surfaces": [
            "contracts/canon/belief_graph_engine_advisory_receipt.v1.schema.json",
            "core/belief_graph_engine_advisory_receipt.py",
            "Scripts/run_belief_graph_engine_advisory_receipt.py",
            "tests/test_belief_graph_engine_advisory_receipt.py",
            "out/audit/belief_graph_engine_advisory_receipt_001.latest.json",
            "out/audit/belief_graph_engine_advisory_receipt_001.latest.md",
        ],
        "planned_validation_gates": _validation_gates(),
        "planned_fixtures": _planned_fixtures(),
        "blocked_actions": list(BLOCKED_ACTIONS),
        "recommended_next_lane": "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_PLAN",
        "recommended_next_action": (
            "prepare a separate advisory receipt implementation plan; do not implement the receipt "
            "or engine without a future explicit operator gate"
        ),
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


def write_belief_graph_engine_advisory_receipt_contract_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_belief_graph_engine_advisory_receipt_contract_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Belief Graph Engine Advisory Receipt Contract Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- plan_status: {packet['plan_status']}",
        f"- target_surface: {packet['target_surface']}",
        f"- contract_plan_scope: {packet['contract_plan_scope']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- receipt_implementation_authorized: {packet['receipt_implementation_authorized']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Planned Receipt Fields",
    ]
    schema = packet.get("planned_receipt_schema", {})
    if isinstance(schema, dict):
        for field in schema.get("planned_fields", []):
            if isinstance(field, dict):
                lines.append(f"- {field['field_name']}: {field['field_status']}")
    lines.extend(["", "## Validation Gates"])
    for gate in packet.get("planned_validation_gates", []):
        if isinstance(gate, dict):
            lines.append(f"- {gate['gate_id']}: {gate['gate_status']}")
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- {action}")
    return lines


def write_belief_graph_engine_advisory_receipt_contract_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(render_belief_graph_engine_advisory_receipt_contract_plan_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
