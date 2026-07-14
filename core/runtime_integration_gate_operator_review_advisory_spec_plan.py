from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

ARTIFACT_TYPE = "RuntimeIntegrationGateOperatorReviewAdvisorySpecPlan.v1"
PLAN_ID = "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_ADVISORY_SPEC_PLAN_001"
OUT_JSON = "out/audit/runtime_integration_gate_operator_review_advisory_spec_plan_001.latest.json"
OUT_MD = "out/audit/runtime_integration_gate_operator_review_advisory_spec_plan_001.latest.md"
SOURCE_RECEIPT = "out/audit/runtime_integration_gate_receipt_001.latest.json"

_AUTHORITY_LOCKS: dict[str, bool] = {
    "advisory_only": True,
    "projection_only": True,
    "non_authoritative": True,
    "valid_for_execution": False,
    "valid_for_runtime_wiring": False,
    "runtime_mutation_allowed": False,
    "canon_mutation_allowed": False,
    "replay_mutation_allowed": False,
    "queue_mutation_allowed": False,
    "scheduler_mutation_allowed": False,
    "forecast_routing_allowed": False,
    "notion_writeback_allowed": False,
    "github_writeback_allowed": False,
    "codegen_implementation_allowed": False,
    "activation_allowed": False,
    "auto_approval_allowed": False,
}

_REVIEW_QUESTIONS: tuple[str, ...] = (
    "Confirm the runtime spine remains advisory and is not enabled as mandatory pre-dispatch wiring.",
    "Confirm each runtime-adjacent subsystem remains bound to its existing authority owner.",
    "Confirm no operator-command authority is delegated to the runtime integration gate surface.",
    "Confirm Codegen Intelligence Spine planning does not permit code generation, file writeback, or autonomous PR action.",
    "Confirm any future behavior-changing patch requires a separate governed operator authorization record.",
)

_BLOCKED_PATCH_CLASSES: tuple[str, ...] = (
    "LIVE_RUNTIME_MUTATION",
    "MANDATORY_PRE_DISPATCH_WIRING",
    "AUTONOMOUS_ACTION",
    "OPERATOR_COMMAND_AUTHORITY",
    "CODEGEN_IMPLEMENTATION",
    "FILE_WRITEBACK_WITHOUT_OPERATOR_REVIEW",
    "CANON_PROMOTION",
    "FORECAST_ROUTING",
    "QUEUE_OR_SCHEDULER_MUTATION",
    "NOTION_OR_GITHUB_WRITEBACK",
)

_WORKSTREAMS: tuple[dict[str, Any], ...] = (
    {
        "workstream_id": "AUTHORITY_OWNER_MAPPING",
        "purpose": "review subsystem-to-owner bindings from the runtime integration gate receipt",
        "allowed_outputs": ["operator review checklist", "binding clarification notes"],
        "forbidden_outputs": ["new runtime authority", "owner reassignment without separate authorization"],
    },
    {
        "workstream_id": "NO_AUTHORITY_SEAL_REVIEW",
        "purpose": "verify each covered subsystem keeps mutation and execution booleans false",
        "allowed_outputs": ["seal consistency findings", "fail-closed blocker list"],
        "forbidden_outputs": ["authority grant", "activation record", "promotion record"],
    },
    {
        "workstream_id": "CODEGEN_BOUNDARY_REVIEW",
        "purpose": "preserve Codegen Intelligence Spine as planning-only until external operator evidence exists",
        "allowed_outputs": ["advisory codegen boundary notes", "future evidence request plan"],
        "forbidden_outputs": ["codegen harness implementation", "patch emission", "shadow replay execution"],
    },
    {
        "workstream_id": "RECEIPT_FRESHNESS_REVIEW",
        "purpose": "confirm the source receipt remains deterministic and repo-visible before any later gate",
        "allowed_outputs": ["source-hash comparison", "staleness finding"],
        "forbidden_outputs": ["artifact regeneration sweep", "research-canary artifact replay"],
    },
)

_ACCEPTANCE_GATES: tuple[dict[str, Any], ...] = (
    {
        "gate_id": "SOURCE_RECEIPT_OBSERVED",
        "required_evidence": [SOURCE_RECEIPT],
        "pass_condition": "source receipt is present and remains advisory-only with runtime wiring disabled",
        "failure_route": "NOT_COMPUTABLE",
    },
    {
        "gate_id": "OPERATOR_ATTESTATION_REQUIRED",
        "required_evidence": ["external governed operator review decision"],
        "pass_condition": "operator attestation is present before any future behavior-changing lane",
        "failure_route": "HOLD_FOR_OPERATOR",
    },
    {
        "gate_id": "NO_AUTHORITY_ESCALATION",
        "required_evidence": ["all authority-lock fields remain false except advisory/projection/non-authoritative"],
        "pass_condition": "no execution, runtime wiring, writeback, activation, or auto-approval authority is granted",
        "failure_route": "DENY_AND_HOLD",
    },
)


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


def _source_ready(receipt: Mapping[str, Any]) -> bool:
    return (
        receipt.get("receipt_status") == "RUNTIME_INTEGRATION_GATE_RECEIPT_READY_ADVISORY_ONLY"
        and receipt.get("recommended_next_lane")
        == "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_OR_ADVISORY_SPEC_PLAN"
        and receipt.get("valid_for_execution") is False
        and receipt.get("valid_for_runtime_wiring") is False
        and receipt.get("mandatory_pre_dispatch_gate_enabled") is False
    )


def build_runtime_integration_gate_operator_review_advisory_spec_plan(
    *,
    repo_root: str | Path,
    source_receipt_path: str | Path = SOURCE_RECEIPT,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_receipt_path)
    receipt = _read_json(root / source_path)
    plan_status = (
        "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_ADVISORY_SPEC_PLAN_READY"
        if _source_ready(receipt)
        else "NOT_COMPUTABLE"
    )
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "plan_status": plan_status,
        "target_surface": "ABRAXAS_RUNTIME_INTEGRATION_GATE_001",
        "source_receipt_path": source_path.as_posix(),
        "source_receipt_hash": _sha256(root / source_path),
        "source_receipt_status": str(receipt.get("receipt_status", "NOT_COMPUTABLE")),
        "source_recommended_next_lane": str(receipt.get("recommended_next_lane", "NOT_COMPUTABLE")),
        "operator_review_required": True,
        "operator_attestation_present": False,
        "review_questions": list(_REVIEW_QUESTIONS),
        "planned_workstreams": sorted(
            (dict(workstream) for workstream in _WORKSTREAMS),
            key=lambda item: str(item["workstream_id"]),
        ),
        "acceptance_gates": sorted(
            (dict(gate) for gate in _ACCEPTANCE_GATES),
            key=lambda item: str(item["gate_id"]),
        ),
        "blocked_patch_classes": sorted(_BLOCKED_PATCH_CLASSES),
        "authority_locks": dict(_AUTHORITY_LOCKS),
        "recommended_next_lane": (
            "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DRY_RUN"
            if plan_status == "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_ADVISORY_SPEC_PLAN_READY"
            else NOT_COMPUTABLE
        ),
        "safe_to_auto_continue": False,
        **_AUTHORITY_LOCKS,
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_runtime_integration_gate_operator_review_advisory_spec_plan(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    write_canonical_json(path, packet)


def write_runtime_integration_gate_operator_review_advisory_spec_plan_markdown(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    lines = [
        "# Runtime Integration Gate Operator Review Advisory Spec Plan 001",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- plan_status: {packet['plan_status']}",
        f"- source_receipt_path: {packet['source_receipt_path']}",
        f"- source_receipt_status: {packet['source_receipt_status']}",
        f"- operator_review_required: {packet['operator_review_required']}",
        f"- operator_attestation_present: {packet['operator_attestation_present']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- valid_for_runtime_wiring: {packet['valid_for_runtime_wiring']}",
        f"- codegen_implementation_allowed: {packet['codegen_implementation_allowed']}",
        "",
        "## Review Questions",
    ]
    for question in packet.get("review_questions", []):
        lines.append(f"- {question}")
    lines.extend(["", "## Planned Workstreams"])
    for workstream in packet.get("planned_workstreams", []):
        if isinstance(workstream, dict):
            lines.append(f"- {workstream['workstream_id']}: {workstream['purpose']}")
    lines.extend(["", "## Acceptance Gates"])
    for gate in packet.get("acceptance_gates", []):
        if isinstance(gate, dict):
            lines.append(
                "- "
                f"{gate['gate_id']}: {gate['pass_condition']} "
                f"(failure_route={gate['failure_route']})"
            )
    lines.extend(["", "## Blocked Patch Classes"])
    for patch_class in packet.get("blocked_patch_classes", []):
        lines.append(f"- {patch_class}")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
