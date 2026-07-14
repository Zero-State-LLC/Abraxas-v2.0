from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.runtime_integration_gate_operator_attestation_intake_gate import (
    GATE_JSON_PATH as INTAKE_GATE_JSON_PATH,
    build_runtime_integration_gate_operator_attestation_intake_gate,
)
from core.runtime_integration_gate_operator_review_decision_record_plan import (
    PLAN_JSON_PATH as SOURCE_PLAN_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "RuntimeIntegrationGateOperatorReviewDecisionRecord.v1"
RECORD_ID = "runtime_integration_gate_operator_review_decision_record_001"
RECORD_JSON_PATH = Path(
    "out/audit/runtime_integration_gate_operator_review_decision_record_001.latest.json"
)
RECORD_MD_PATH = RECORD_JSON_PATH.with_suffix(".md")
EXPECTED_PLAN_STATUS = (
    "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_PLAN_READY"
)
DEFAULT_PAYLOAD_PATH = Path(
    "operator_input/runtime_integration_gate_operator_attestation_payload_001.json"
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _authority_locks(
    *,
    mandatory_pre_dispatch_wiring: bool,
    valid_for_runtime_wiring: bool,
) -> dict[str, bool]:
    return {
        "activation_allowed": False,
        "auto_approval_allowed": False,
        "canon_mutation_allowed": False,
        "codegen_implementation_allowed": False,
        "decision_record_creation": False,
        "execution_authority": False,
        "forecast_routing_allowed": False,
        "github_writeback_allowed": False,
        "mandatory_pre_dispatch_wiring": mandatory_pre_dispatch_wiring,
        "notion_writeback_allowed": False,
        "operator_attestation": False,
        "queue_mutation_allowed": False,
        "replay_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "valid_for_execution": False,
        "valid_for_runtime_wiring": valid_for_runtime_wiring,
    }


def _disposition_flags(selected_decision: str) -> dict[str, Any]:
    if selected_decision == "APPROVE_MANDATORY_PRE_DISPATCH_WIRING":
        return {
            "selected_decision": "APPROVE_MANDATORY_PRE_DISPATCH_WIRING",
            "decision_outcome_summary": (
                "Operator attested runtime integration gate review and approved mandatory "
                "pre-dispatch wiring while keeping execution authority denied."
            ),
            "mandatory_pre_dispatch_wiring": True,
            "valid_for_runtime_wiring": True,
            "mandatory_pre_dispatch_wiring_denied_acknowledged": False,
            "runtime_mutation_denied_acknowledged": True,
            "valid_for_runtime_wiring_denied_acknowledged": False,
            "recommended_next_lane": (
                "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_HOLD_RECEIPT_001"
            ),
            "recommended_next_action": (
                "shadow wiring approved; execution authority remains NOT_COMPUTABLE"
            ),
        }
    if selected_decision == "APPROVE_SHADOW_WIRING_ONLY":
        return {
            "selected_decision": "APPROVE_SHADOW_WIRING_ONLY",
            "decision_outcome_summary": (
                "Operator attested runtime integration gate review and approved shadow "
                "runtime wiring while keeping mandatory pre-dispatch wiring and execution "
                "authority denied."
            ),
            "mandatory_pre_dispatch_wiring": False,
            "valid_for_runtime_wiring": True,
            "mandatory_pre_dispatch_wiring_denied_acknowledged": True,
            "runtime_mutation_denied_acknowledged": True,
            "valid_for_runtime_wiring_denied_acknowledged": False,
            "recommended_next_lane": (
                "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_HOLD_RECEIPT_001"
            ),
            "recommended_next_action": (
                "shadow wiring intake validated; downstream execution remains NOT_COMPUTABLE"
            ),
        }
    return {
        "selected_decision": "HOLD_FOR_OPERATOR_RUNTIME_GATE_REVIEW",
        "decision_outcome_summary": (
            "Operator attested runtime integration gate review boundaries while keeping "
            "mandatory pre-dispatch wiring, runtime mutation, and execution authority denied."
        ),
        "mandatory_pre_dispatch_wiring": False,
        "valid_for_runtime_wiring": False,
        "mandatory_pre_dispatch_wiring_denied_acknowledged": True,
        "runtime_mutation_denied_acknowledged": True,
        "valid_for_runtime_wiring_denied_acknowledged": True,
        "recommended_next_lane": (
            "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_HOLD_RECEIPT_001"
        ),
        "recommended_next_action": "emit terminal hold receipt; downstream remains NOT_COMPUTABLE",
    }


def build_runtime_integration_gate_operator_review_decision_record(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    plan = _read_json(root / SOURCE_PLAN_JSON_PATH) or {}
    intake = build_runtime_integration_gate_operator_attestation_intake_gate(root)
    payload = _read_json(root / DEFAULT_PAYLOAD_PATH) or {}
    identity = payload.get("operator_identity", {})
    plan_ready = (
        plan.get("schema_version") == "RuntimeIntegrationGateOperatorReviewDecisionRecordPlan.v1"
        and plan.get("status") == EXPECTED_PLAN_STATUS
        and plan.get("decision_record_creation_authorized") is False
        and plan.get("mandatory_pre_dispatch_wiring") is False
        and plan.get("valid_for_runtime_wiring") is False
    )
    intake_valid = intake.get("intake_validated_for_decision_record") is True
    attestations_ready = plan_ready and intake_valid
    selected = (
        str(intake.get("operator_selected_decision", "MAINTAIN_HOLD"))
        if intake_valid
        else "MAINTAIN_HOLD"
    )
    disposition = _disposition_flags(selected if attestations_ready else "MAINTAIN_HOLD")
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "decision_record_id": RECORD_ID,
        "status": (
            "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_ATTESTED"
            if attestations_ready
            else "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_BLOCKED"
        ),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "selected_decision": disposition["selected_decision"]
        if attestations_ready
        else NOT_COMPUTABLE,
        "decision_outcome_summary": disposition["decision_outcome_summary"]
        if attestations_ready
        else NOT_COMPUTABLE,
        "operator_id": identity.get("operator_id", NOT_COMPUTABLE)
        if attestations_ready
        else NOT_COMPUTABLE,
        "operator_name": identity.get("operator_name", NOT_COMPUTABLE)
        if attestations_ready
        else NOT_COMPUTABLE,
        "operator_role": identity.get("operator_role", "governed_operator")
        if attestations_ready
        else NOT_COMPUTABLE,
        "operator_attestation_timestamp_utc": (
            identity.get("operator_reviewed_at_source_observed", NOT_COMPUTABLE)
            if attestations_ready
            else NOT_COMPUTABLE
        ),
        "authority_owner_mapping_review_attested": attestations_ready,
        "no_authority_seal_review_attested": attestations_ready,
        "codegen_boundary_review_attested": attestations_ready,
        "receipt_freshness_review_attested": attestations_ready,
        "mandatory_pre_dispatch_wiring_denied_acknowledged": disposition[
            "mandatory_pre_dispatch_wiring_denied_acknowledged"
        ],
        "runtime_mutation_denied_acknowledged": disposition[
            "runtime_mutation_denied_acknowledged"
        ],
        "valid_for_runtime_wiring_denied_acknowledged": disposition[
            "valid_for_runtime_wiring_denied_acknowledged"
        ],
        "operator_attestation_present": attestations_ready,
        "operator_input_required": not intake_valid,
        "decision_record_created": True if attestations_ready else False,
        "mandatory_pre_dispatch_wiring": disposition["mandatory_pre_dispatch_wiring"],
        "valid_for_runtime_wiring": disposition["valid_for_runtime_wiring"],
        "runtime_mutation_allowed": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "authority_locks": _authority_locks(
            mandatory_pre_dispatch_wiring=disposition["mandatory_pre_dispatch_wiring"],
            valid_for_runtime_wiring=disposition["valid_for_runtime_wiring"],
        ),
        "source_plan_path": SOURCE_PLAN_JSON_PATH.as_posix(),
        "source_plan_hash": str(plan.get("plan_hash", NOT_COMPUTABLE)),
        "source_intake_gate_path": INTAKE_GATE_JSON_PATH.as_posix(),
        "source_intake_gate_hash": str(intake.get("gate_hash", NOT_COMPUTABLE)),
        "recommended_next_lane": disposition["recommended_next_lane"]
        if attestations_ready
        else NOT_COMPUTABLE,
        "recommended_next_action": disposition["recommended_next_action"]
        if attestations_ready
        else "restore decision record plan evidence",
        "downstream": NOT_COMPUTABLE,
        "decision_record_hash": "",
    }
    packet["decision_record_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "decision_record_hash"}
    )
    return packet


def render_markdown(packet: Mapping[str, Any]) -> list[str]:
    return [
        "# Runtime Integration Gate Operator Review Decision Record 001",
        "",
        f"- decision_record_id: {packet['decision_record_id']}",
        f"- status: {packet['status']}",
        f"- selected_decision: {packet['selected_decision']}",
        f"- mandatory_pre_dispatch_wiring: {packet['mandatory_pre_dispatch_wiring']}",
        f"- valid_for_runtime_wiring: {packet['valid_for_runtime_wiring']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
    ]


def write_runtime_integration_gate_operator_review_decision_record(
    repo_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_runtime_integration_gate_operator_review_decision_record(root)
    write_canonical_json(target_root / RECORD_JSON_PATH, packet)
    target_root.joinpath(RECORD_MD_PATH).parent.mkdir(parents=True, exist_ok=True)
    target_root.joinpath(RECORD_MD_PATH).write_text(
        "\n".join(render_markdown(packet)) + "\n",
        encoding="utf-8",
    )
    return packet
