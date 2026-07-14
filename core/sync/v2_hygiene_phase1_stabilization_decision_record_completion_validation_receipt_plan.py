from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate import (
    GATE_JSON_PATH as SOURCE_COMPLETION_VALIDATION_APPROVAL_GATE_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = (
    "V2HygienePhase1StabilizationDecisionRecordCompletionValidationReceiptPlan.v1"
)
PLAN_ID = (
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
    "receipt_plan_001"
)
PLAN_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
    "receipt_plan_001.latest.json"
)
PLAN_MD_PATH = PLAN_JSON_PATH.with_suffix(".md")
READY_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "RECEIPT_PLAN_READY"
)
BLOCKED_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "RECEIPT_PLAN_BLOCKED"
)
EXPECTED_APPROVAL_GATE_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "APPROVAL_GATE_READY_FOR_SEPARATE_RECORD_COMPLETION_VALIDATION_PLANNING"
)
AUTHORITY_EXPANDING_FIELDS = (
    "decision_record_created",
    "decision_record_creation_authorized",
    "decision_record_completed",
    "decision_record_completion_authorized",
    "decision_record_completion_validation_authorized",
    "decision_record_completion_validation_performed",
    "decision_record_emitted",
    "decision_record_emission_authorized",
    "decision_record_finalized",
    "decision_record_finalization_authorized",
    "decision_record_materialized",
    "decision_record_materialization_authorized",
    "authorization_record_created",
    "authorization_record_creation_authorized",
    "evidence_bundle_created",
    "evidence_bundle_creation_authorized",
    "operator_attestation_created",
    "implementation_authorized",
    "hygiene_code_creation_authorized",
    "schema_file_creation_authorized",
    "v2_module_registration_authorized",
    "rune_registration_authorized",
    "strict_mode_enablement_authorized",
    "notion_writeback_allowed",
    "github_writeback_allowed",
    "runtime_mutation",
    "queue_mutation",
    "scheduler_mutation",
    "canon_mutation",
    "schema_mutation",
    "execution_authority",
    "valid_for_execution",
    "valid_for_implementation",
    "valid_for_decision_record_creation",
    "valid_for_decision_record_completion",
    "valid_for_decision_record_completion_validation",
    "valid_for_decision_record_emission",
    "valid_for_decision_record_finalization",
    "valid_for_decision_record_materialization",
    "safe_to_auto_continue",
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return NOT_COMPUTABLE


def _authority_locks() -> dict[str, bool]:
    return {
        "activation": False,
        "authorization_record_creation": False,
        "auto_approval": False,
        "auto_continuation": False,
        "canon_mutation": False,
        "decision_record_completion": False,
        "decision_record_completion_validation": False,
        "decision_record_creation": False,
        "decision_record_emission": False,
        "decision_record_finalization": False,
        "evidence_bundle_creation": False,
        "execution_authority": False,
        "github_writeback": False,
        "hygiene_code_creation": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_evidence_bundle_creation": False,
        "projection_surface_mutation": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_file_creation": False,
        "schema_mutation": False,
        "strict_mode_enablement": False,
        "token_minting": False,
        "v2_module_registration": False,
    }


def _locks_all_false(value: Any) -> bool:
    return isinstance(value, Mapping) and bool(value) and all(
        item is False for item in value.values()
    )


def _copied_authority_locks(source: Mapping[str, Any]) -> dict[str, bool]:
    locks = source.get("authority_locks")
    if _locks_all_false(locks):
        return {str(key): False for key in sorted(locks)}
    return _authority_locks()


def _authority_expansion_blockers(source_id: str, packet: Mapping[str, Any]) -> list[str]:
    blockers = [
        f"{source_id}_authority_expanding_field:{field}"
        for field in AUTHORITY_EXPANDING_FIELDS
        if packet.get(field) is True
    ]
    locks = packet.get("authority_locks")
    if isinstance(locks, Mapping):
        blockers.extend(
            f"{source_id}_authority_lock_true:{field}"
            for field, value in sorted(locks.items())
            if value is True
        )
    return blockers


def _source_record(
    source_id: str,
    path: Path,
    packet: Mapping[str, Any],
    *,
    expected_status: str,
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": path.as_posix(),
        "observed": bool(packet),
        "file_hash": _sha256(path),
        "packet_hash": str(packet.get("gate_hash", NOT_COMPUTABLE)),
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": expected_status,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "recommended_next_lane": str(packet.get("recommended_next_lane", NOT_COMPUTABLE)),
        "safe_to_auto_continue": packet.get("safe_to_auto_continue"),
        "valid_for_execution": packet.get("valid_for_execution"),
        "valid_for_implementation": packet.get("valid_for_implementation"),
        "valid_for_decision_record_completion_validation": packet.get(
            "valid_for_decision_record_completion_validation"
        ),
    }


def _approval_gate_blockers(gate: Mapping[str, Any]) -> list[str]:
    blockers = []
    if gate.get("status") != EXPECTED_APPROVAL_GATE_STATUS:
        blockers.append("source_completion_validation_approval_gate_not_ready")
    if gate.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("source_completion_validation_approval_gate_not_source_ready")
    if gate.get("completion_validation_approval_gate_ready") is not True:
        blockers.append("source_completion_validation_approval_gate_ready_not_true")
    if gate.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append("source_completion_validation_approval_gate_lane_not_closed")
    if gate.get("safe_to_auto_continue") is not False:
        blockers.append("source_completion_validation_approval_gate_auto_continue_not_false")
    if gate.get("valid_for_execution") is not False:
        blockers.append("source_completion_validation_approval_gate_execution_not_false")
    if gate.get("valid_for_implementation") is not False:
        blockers.append("source_completion_validation_approval_gate_implementation_not_false")
    if gate.get("valid_for_decision_record_completion_validation") is not False:
        blockers.append("source_completion_validation_approval_gate_validation_not_false")
    if gate.get("decision_record_completion_validation_authorized") is not False:
        blockers.append("source_completion_validation_authorized_not_false")
    if gate.get("decision_record_completion_validation_performed") is not False:
        blockers.append("source_completion_validation_performed_not_false")
    if not _locks_all_false(gate.get("authority_locks")):
        blockers.append("source_completion_validation_approval_gate_locks_not_all_false")
    planned = gate.get("planned_record_completion_validation")
    if not isinstance(planned, Mapping):
        blockers.append("source_planned_record_completion_validation_missing")
    else:
        required_hash_fields = (
            "source_completion_validation_plan_hash",
            "source_completion_validation_authorization_gate_hash",
            "source_completion_validation_approval_intake_hash",
            "source_operator_approval_hash",
        )
        blockers.extend(
            f"source_planned_record_completion_validation_missing:{field}"
            for field in required_hash_fields
            if planned.get(field) in (None, "", NOT_COMPUTABLE)
        )
        if planned.get("requires_separate_record_completion_validation_planning") is not True:
            blockers.append("source_separate_record_completion_validation_planning_not_true")
        if planned.get("record_completion_validation_performed") is not False:
            blockers.append("source_planned_completion_validation_performed_not_false")
        if planned.get("authority_granted") is not False:
            blockers.append("source_planned_authority_granted_not_false")
    blockers.extend(_authority_expansion_blockers("completion_validation_approval_gate", gate))
    return blockers


def _planned_validation_packet_contract(
    approval_gate: Mapping[str, Any],
) -> dict[str, Any]:
    planned = approval_gate.get("planned_record_completion_validation")
    planned_record = planned if isinstance(planned, Mapping) else {}
    source_packet_hashes = {
        "completion_validation_plan_hash": str(
            planned_record.get("source_completion_validation_plan_hash", NOT_COMPUTABLE)
        ),
        "completion_validation_authorization_gate_hash": str(
            planned_record.get(
                "source_completion_validation_authorization_gate_hash",
                NOT_COMPUTABLE,
            )
        ),
        "completion_validation_approval_intake_hash": str(
            planned_record.get(
                "source_completion_validation_approval_intake_hash",
                NOT_COMPUTABLE,
            )
        ),
        "operator_approval_hash": str(
            planned_record.get("source_operator_approval_hash", NOT_COMPUTABLE)
        ),
    }
    return {
        "contract_id": (
            "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
            "packet_contract_001"
        ),
        "record_id": str(
            planned_record.get(
                "record_id",
                "v2_hygiene_phase1_stabilization_decision_record_001",
            )
        ),
        "record_output_path": str(
            planned_record.get(
                "record_output_path",
                "out/operator_review/"
                "v2_hygiene_phase1_stabilization_decision_record_001.latest.json",
            )
        ),
        "source_packet_hashes": source_packet_hashes,
        "required_fields": [
            "record_id",
            "record_output_path",
            "source_packet_hashes",
            "validation_claims",
            "authority_denials",
            "recommended_next_lane",
            "downstream",
        ],
        "validation_claims_required_structure": {
            "claim_id": "stable string identifier",
            "claim": "plain-language validation claim",
            "provenance": "source artifact path or packet field",
            "risk_level": "LOW | MEDIUM | HIGH",
            "expected_value": "deterministic expected value",
            "observed_value": "deterministic observed value",
            "claim_validated": False,
        },
        "planned_validation_claims": [
            {
                "claim_id": "source_approval_gate_ready",
                "provenance": SOURCE_COMPLETION_VALIDATION_APPROVAL_GATE_JSON_PATH.as_posix(),
                "risk_level": "LOW",
                "expected_value": EXPECTED_APPROVAL_GATE_STATUS,
            },
            {
                "claim_id": "authority_locks_preserved_false",
                "provenance": "approval_gate.authority_locks",
                "risk_level": "HIGH",
                "expected_value": "all authority locks false",
            },
            {
                "claim_id": "downstream_remains_not_computable",
                "provenance": "approval_gate.downstream",
                "risk_level": "MEDIUM",
                "expected_value": NOT_COMPUTABLE,
            },
        ],
        "authority_denials": {
            "record_completion_validation_performed": False,
            "record_completion_authorized": False,
            "record_finalization_authorized": False,
            "record_emission_authorized": False,
            "record_materialization_authorized": False,
            "implementation_authorized": False,
            "execution_authority": False,
            "notion_writeback_allowed": False,
            "github_writeback_allowed": False,
            "v2_module_registration_authorized": False,
            "rune_registration_authorized": False,
            "runtime_mutation": False,
            "canon_mutation": False,
            "queue_mutation": False,
            "scheduler_mutation": False,
        },
        "completion_validation_authorized": False,
        "completion_validation_performed": False,
        "receipt_plan_only": True,
    }


def _planned_brier_scoring_contract() -> dict[str, Any]:
    return {
        "contract_id": (
            "v2_hygiene_phase1_stabilization_completion_validation_brier_"
            "telemetry_contract_001"
        ),
        "telemetry_only": True,
        "required_fields": [
            "claim_id",
            "forecast_probability",
            "binary_outcome",
            "brier_score",
            "resolution_source",
        ],
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "field_constraints": {
            "forecast_probability": "number in [0.0, 1.0]",
            "binary_outcome": "0 or 1 when externally resolved; otherwise NOT_COMPUTABLE",
            "brier_score": "computed only after externally governed resolution",
            "resolution_source": "explicit governed source path or NOT_COMPUTABLE",
        },
        "resolution_allowed": False,
        "adaptive_learning_authorized": False,
        "forecast_routing_authorized": False,
        "promotion_authorized": False,
        "execution_authority": False,
    }


def _planned_rune_governance_mapping() -> list[dict[str, Any]]:
    return [
        {
            "rune": "Observe",
            "governance_mapping": "source readiness and source blocker observation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": "source hash and schema linkage planning",
            "authority_granted": False,
            "risk_level": "MEDIUM",
        },
        {
            "rune": "Hold",
            "governance_mapping": "approval-gate and downstream NOT_COMPUTABLE preservation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Seal",
            "governance_mapping": "future planned state only; no current seal authority",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan(
    repo_root: str | Path = ".",
    *,
    source_completion_validation_approval_gate_path: str | Path = (
        SOURCE_COMPLETION_VALIDATION_APPROVAL_GATE_JSON_PATH
    ),
) -> dict[str, Any]:
    root = Path(repo_root)
    approval_gate_path = Path(source_completion_validation_approval_gate_path)
    approval_gate = _read_json(root / approval_gate_path) or {}
    sources_observed = bool(approval_gate)
    blockers = _approval_gate_blockers(approval_gate) if approval_gate else []
    if not approval_gate:
        blockers.append("required_completion_validation_approval_gate_missing")
    blockers = sorted(set(blockers))
    ready = sources_observed and not blockers
    status = READY_STATUS if ready else (NOT_COMPUTABLE if not sources_observed else BLOCKED_STATUS)
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "plan_id": PLAN_ID,
        "status": status,
        "sources_observed": sources_observed,
        "source_records": [
            _source_record(
                "completion_validation_approval_gate",
                approval_gate_path,
                approval_gate,
                expected_status=EXPECTED_APPROVAL_GATE_STATUS,
            )
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "receipt_plan_ready": ready,
        "planned_validation_packet_contract": _planned_validation_packet_contract(
            approval_gate
        ),
        "planned_brier_scoring_contract": _planned_brier_scoring_contract(),
        "planned_rune_governance_mapping": _planned_rune_governance_mapping(),
        "selected_follow_on_action": (
            "PLAN_SEPARATE_ADVISORY_COMPLETION_VALIDATION_RECEIPT"
            if ready
            else "RESTORE_COMPLETION_VALIDATION_APPROVAL_GATE"
        ),
        "recommended_next_action": (
            "plan the future advisory-only completion-validation receipt packet; "
            "do not perform completion validation, complete records, create evidence "
            "bundles, write back, register modules or runes, mutate runtime/canon/"
            "queue/scheduler state, auto-continue, or execute"
            if ready
            else "restore the completion-validation approval gate before planning a "
            "completion-validation receipt"
        ),
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_lane": NOT_COMPUTABLE,
        "downstream": NOT_COMPUTABLE,
        "decision_record_created": False,
        "decision_record_creation_authorized": False,
        "decision_record_completed": False,
        "decision_record_completion_authorized": False,
        "decision_record_completion_validation_authorized": False,
        "decision_record_completion_validation_performed": False,
        "decision_record_emitted": False,
        "decision_record_emission_authorized": False,
        "decision_record_finalized": False,
        "decision_record_finalization_authorized": False,
        "decision_record_materialized": False,
        "decision_record_materialization_authorized": False,
        "authorization_record_created": False,
        "authorization_record_creation_authorized": False,
        "evidence_bundle_created": False,
        "evidence_bundle_creation_authorized": False,
        "operator_attestation_created": False,
        "operator_evidence_bundle_created": False,
        "operator_evidence_bundle_creation_authorized": False,
        "implementation_authorized": False,
        "hygiene_code_creation_authorized": False,
        "schema_file_creation_authorized": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "strict_mode_enablement_authorized": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "canon_mutation": False,
        "schema_mutation": False,
        "execution_authority": False,
        "forecast_routing_authorized": False,
        "adaptive_learning_authorized": False,
        "valid_for_decision_record_creation": False,
        "valid_for_decision_record_completion": False,
        "valid_for_decision_record_completion_validation": False,
        "valid_for_decision_record_emission": False,
        "valid_for_decision_record_finalization": False,
        "valid_for_decision_record_materialization": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authority_locks": _copied_authority_locks(approval_gate),
        "receipt_plan_hash": "",
    }
    packet["receipt_plan_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "receipt_plan_hash"}
    )
    return packet


def render_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    validation_contract = packet["planned_validation_packet_contract"]
    brier_contract = packet["planned_brier_scoring_contract"]
    lines = [
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Completion Validation Receipt Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- receipt_plan_ready: {packet['receipt_plan_ready']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- downstream: {packet['downstream']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- valid_for_decision_record_completion_validation: {packet['valid_for_decision_record_completion_validation']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Planned Validation Packet Contract",
        f"- contract_id: {validation_contract['contract_id']}",
        f"- record_id: {validation_contract['record_id']}",
        f"- record_output_path: {validation_contract['record_output_path']}",
        f"- completion_validation_authorized: {validation_contract['completion_validation_authorized']}",
        f"- completion_validation_performed: {validation_contract['completion_validation_performed']}",
        "",
        "## Brier Scoring Contract",
        f"- contract_id: {brier_contract['contract_id']}",
        f"- telemetry_only: {brier_contract['telemetry_only']}",
        f"- brier_score_formula: {brier_contract['brier_score_formula']}",
        f"- resolution_allowed: {brier_contract['resolution_allowed']}",
        f"- adaptive_learning_authorized: {brier_contract['adaptive_learning_authorized']}",
        f"- forecast_routing_authorized: {brier_contract['forecast_routing_authorized']}",
        "",
        "## Rune Governance Mapping",
    ]
    lines.extend(
        f"- {mapping['rune']}: {mapping['governance_mapping']} "
        f"(authority_granted={mapping['authority_granted']}, risk={mapping['risk_level']})"
        for mapping in packet["planned_rune_governance_mapping"]
    )
    lines.extend(["", "## Source Blockers"])
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan(
        repo_root
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / PLAN_JSON_PATH, packet)
    md_path = root / PLAN_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
