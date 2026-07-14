from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_intake_gate import (
    GATE_JSON_PATH as SOURCE_COMPLETION_VALIDATION_APPROVAL_INTAKE_GATE_JSON_PATH,
)
from core.sync.v2_hygiene_phase1_stabilization_decision_record_completion_validation_authorization_gate import (
    GATE_JSON_PATH as SOURCE_COMPLETION_VALIDATION_AUTHORIZATION_GATE_JSON_PATH,
)
from core.sync.v2_hygiene_phase1_stabilization_decision_record_completion_validation_plan import (
    PLAN_JSON_PATH as SOURCE_COMPLETION_VALIDATION_PLAN_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = (
    "V2HygienePhase1StabilizationDecisionRecordCompletionValidationApprovalGate.v1"
)
GATE_ID = (
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
    "approval_gate_001"
)
GATE_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
    "approval_gate_001.latest.json"
)
GATE_MD_PATH = GATE_JSON_PATH.with_suffix(".md")
READY_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "APPROVAL_GATE_READY_FOR_SEPARATE_RECORD_COMPLETION_VALIDATION_PLANNING"
)
BLOCKED_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "APPROVAL_GATE_BLOCKED"
)
EXPECTED_APPROVAL_INTAKE_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "APPROVAL_INTAKE_VALIDATED_FOR_FUTURE_RECORD_COMPLETION_VALIDATION_GATE"
)
EXPECTED_AUTHORIZATION_GATE_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
)
EXPECTED_PLAN_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "PLAN_READY"
)
AUTHORITY_EXPANDING_FIELDS = (
    "decision_record_created",
    "decision_record_creation_authorized",
    "decision_record_completed",
    "decision_record_completion_authorized",
    "decision_record_completion_validation_authorized",
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
    hash_field: str,
    expected_status: str,
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": path.as_posix(),
        "observed": bool(packet),
        "file_hash": _sha256(path),
        "packet_hash": str(packet.get(hash_field, NOT_COMPUTABLE)),
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": expected_status,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "recommended_next_lane": str(packet.get("recommended_next_lane", NOT_COMPUTABLE)),
        "safe_to_auto_continue": packet.get("safe_to_auto_continue"),
        "valid_for_execution": packet.get("valid_for_execution"),
    }


def _common_closed_source_blockers(source_id: str, packet: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if packet.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append(f"{source_id}_recommended_next_lane_not_not_computable")
    if packet.get("safe_to_auto_continue") is not False:
        blockers.append(f"{source_id}_safe_to_auto_continue_not_false")
    if packet.get("valid_for_execution") is not False:
        blockers.append(f"{source_id}_valid_for_execution_not_false")
    if not _locks_all_false(packet.get("authority_locks")):
        blockers.append(f"{source_id}_authority_locks_not_all_false")
    blockers.extend(_authority_expansion_blockers(source_id, packet))
    return blockers


def _plan_blockers(plan: Mapping[str, Any]) -> list[str]:
    blockers = _common_closed_source_blockers("completion_validation_plan", plan)
    if plan.get("status") != EXPECTED_PLAN_STATUS:
        blockers.append("source_completion_validation_plan_not_ready")
    if plan.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("source_completion_validation_plan_not_source_ready")
    if plan.get("valid_for_decision_record_completion_validation") is not False:
        blockers.append("source_plan_valid_for_completion_validation_not_false")
    if plan.get("decision_record_materialized") is not False:
        blockers.append("source_plan_record_materialized_not_false")
    return blockers


def _authorization_gate_blockers(gate: Mapping[str, Any]) -> list[str]:
    blockers = _common_closed_source_blockers("completion_validation_authorization_gate", gate)
    if gate.get("status") != EXPECTED_AUTHORIZATION_GATE_STATUS:
        blockers.append("source_completion_validation_authorization_gate_not_held")
    if gate.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("source_completion_validation_authorization_gate_not_source_ready")
    if gate.get("operator_review_required") is not True:
        blockers.append("source_authorization_gate_operator_review_not_required")
    if gate.get("valid_for_decision_record_completion_validation") is not False:
        blockers.append("source_authorization_gate_valid_for_validation_not_false")
    if gate.get("decision_record_completion_validation_authorized") is not False:
        blockers.append("source_completion_validation_authorized_not_false")
    if gate.get("decision_record_materialized") is not False:
        blockers.append("source_authorization_gate_record_materialized_not_false")
    return blockers


def _approval_intake_blockers(intake: Mapping[str, Any]) -> list[str]:
    blockers = _common_closed_source_blockers("completion_validation_approval_intake", intake)
    if intake.get("status") != EXPECTED_APPROVAL_INTAKE_STATUS:
        blockers.append("source_completion_validation_approval_intake_not_validated")
    if intake.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("source_completion_validation_approval_intake_not_source_ready")
    if intake.get("operator_approval_observed") is not True:
        blockers.append("source_operator_approval_not_observed")
    if (
        intake.get(
            "completion_validation_approval_validated_for_future_record_completion_validation_gate"
        )
        is not True
    ):
        blockers.append("source_completion_validation_approval_not_validated")
    if intake.get("separate_record_completion_validation_gate_required") is not True:
        blockers.append("source_separate_record_completion_validation_gate_not_required")
    if intake.get("valid_for_decision_record_completion_validation") is not False:
        blockers.append("source_intake_valid_for_validation_not_false")
    if intake.get("decision_record_completion_validation_authorized") is not False:
        blockers.append("source_intake_completion_validation_authorized_not_false")
    if intake.get("decision_record_materialized") is not False:
        blockers.append("source_intake_record_materialized_not_false")
    return blockers


def build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate(
    repo_root: str | Path = ".",
    *,
    source_completion_validation_plan_path: str | Path = SOURCE_COMPLETION_VALIDATION_PLAN_JSON_PATH,
    source_completion_validation_authorization_gate_path: str | Path = SOURCE_COMPLETION_VALIDATION_AUTHORIZATION_GATE_JSON_PATH,
    source_completion_validation_approval_intake_gate_path: str | Path = SOURCE_COMPLETION_VALIDATION_APPROVAL_INTAKE_GATE_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    plan_path = Path(source_completion_validation_plan_path)
    authorization_gate_path = Path(source_completion_validation_authorization_gate_path)
    intake_path = Path(source_completion_validation_approval_intake_gate_path)
    plan = _read_json(root / plan_path) or {}
    authorization_gate = _read_json(root / authorization_gate_path) or {}
    intake = _read_json(root / intake_path) or {}
    sources_observed = bool(plan) and bool(authorization_gate) and bool(intake)
    blockers = sorted(
        set(
            _plan_blockers(plan)
            + _authorization_gate_blockers(authorization_gate)
            + _approval_intake_blockers(intake)
        )
    )
    if not plan:
        blockers.append("required_completion_validation_plan_missing")
    if not authorization_gate:
        blockers.append("required_completion_validation_authorization_gate_missing")
    if not intake:
        blockers.append("required_completion_validation_approval_intake_missing")
    blockers = sorted(set(blockers))
    ready = sources_observed and not blockers
    status = READY_STATUS if ready else (NOT_COMPUTABLE if not sources_observed else BLOCKED_STATUS)
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "status": status,
        "sources_observed": sources_observed,
        "source_records": [
            _source_record(
                "completion_validation_plan",
                plan_path,
                plan,
                hash_field="plan_hash",
                expected_status=EXPECTED_PLAN_STATUS,
            ),
            _source_record(
                "completion_validation_authorization_gate",
                authorization_gate_path,
                authorization_gate,
                hash_field="gate_hash",
                expected_status=EXPECTED_AUTHORIZATION_GATE_STATUS,
            ),
            _source_record(
                "completion_validation_approval_intake_gate",
                intake_path,
                intake,
                hash_field="gate_hash",
                expected_status=EXPECTED_APPROVAL_INTAKE_STATUS,
            ),
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "completion_validation_approval_gate_ready": ready,
        "selected_operator_decision": (
            "ACCEPT_COMPLETION_VALIDATION_APPROVAL_FOR_SEPARATE_GOVERNED_"
            "RECORD_COMPLETION_VALIDATION_PLANNING"
            if ready
            else NOT_COMPUTABLE
        ),
        "selected_follow_on_action": (
            "PLAN_SEPARATE_GOVERNED_RECORD_COMPLETION_VALIDATION"
            if ready
            else "RESTORE_VALIDATED_COMPLETION_VALIDATION_APPROVAL_INTAKE"
        ),
        "planned_record_completion_validation": {
            "record_id": str(
                intake.get(
                    "approved_record_id",
                    "v2_hygiene_phase1_stabilization_decision_record_001",
                )
            ),
            "record_output_path": str(
                intake.get(
                    "approved_record_output_path",
                    "out/operator_review/"
                    "v2_hygiene_phase1_stabilization_decision_record_001.latest.json",
                )
            ),
            "operator_id": str(intake.get("operator_id", NOT_COMPUTABLE)),
            "operator_reviewed_at_source_observed": str(
                intake.get("operator_reviewed_at_source_observed", NOT_COMPUTABLE)
            ),
            "source_operator_approval_hash": str(
                intake.get("operator_approval_hash", NOT_COMPUTABLE)
            ),
            "source_completion_validation_plan_hash": str(
                plan.get("plan_hash", NOT_COMPUTABLE)
            ),
            "source_completion_validation_authorization_gate_hash": str(
                authorization_gate.get("gate_hash", NOT_COMPUTABLE)
            ),
            "source_completion_validation_approval_intake_hash": str(
                intake.get("gate_hash", NOT_COMPUTABLE)
            ),
            "record_completion_validation_allowed": False,
            "record_completion_validation_authorized": False,
            "record_completion_validation_performed": False,
            "record_completion_allowed": False,
            "record_completion_authorized": False,
            "record_completed": False,
            "record_finalization_allowed": False,
            "record_finalization_authorized": False,
            "record_finalized": False,
            "record_emission_allowed": False,
            "record_emission_authorized": False,
            "record_emitted": False,
            "record_materialized": False,
            "requires_separate_record_completion_validation_planning": True,
            "requires_operator_review_before_record_completion_validation": True,
            "approval_gate_only": True,
            "authority_granted": False,
        },
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
        "valid_for_decision_record_creation": False,
        "valid_for_decision_record_completion": False,
        "valid_for_decision_record_completion_validation": False,
        "valid_for_decision_record_emission": False,
        "valid_for_decision_record_finalization": False,
        "valid_for_decision_record_materialization": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_action": (
            "record completion-validation approval is ready only for separate governed "
            "record-completion-validation planning; this gate does not complete, validate, "
            "finalize, emit, or materialize the decision record"
            if ready
            else "restore validated completion-validation approval intake before planning "
            "record completion validation"
        ),
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authority_locks": _authority_locks(),
        "downstream": NOT_COMPUTABLE,
        "gate_hash": "",
    }
    packet["gate_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "gate_hash"}
    )
    return packet


def render_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    planned_validation = packet["planned_record_completion_validation"]
    lines = [
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Completion Validation Approval Gate",
        "",
        f"- gate_id: {packet['gate_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- completion_validation_approval_gate_ready: {packet['completion_validation_approval_gate_ready']}",
        f"- selected_operator_decision: {packet['selected_operator_decision']}",
        f"- selected_follow_on_action: {packet['selected_follow_on_action']}",
        f"- record_id: {planned_validation['record_id']}",
        f"- record_completion_validation_allowed: {planned_validation['record_completion_validation_allowed']}",
        f"- record_completion_validation_authorized: {planned_validation['record_completion_validation_authorized']}",
        f"- record_completion_validation_performed: {planned_validation['record_completion_validation_performed']}",
        f"- record_completed: {planned_validation['record_completed']}",
        f"- record_finalized: {planned_validation['record_finalized']}",
        f"- record_emitted: {planned_validation['record_emitted']}",
        f"- record_materialized: {planned_validation['record_materialized']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- valid_for_decision_record_completion_validation: {packet['valid_for_decision_record_completion_validation']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Planned Record Completion Validation",
        f"- record_output_path: {planned_validation['record_output_path']}",
        f"- source_completion_validation_approval_intake_hash: {planned_validation['source_completion_validation_approval_intake_hash']}",
        f"- requires_separate_record_completion_validation_planning: {planned_validation['requires_separate_record_completion_validation_planning']}",
        f"- authority_granted: {planned_validation['authority_granted']}",
        "",
        "## Source Blockers",
    ]
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate(
        repo_root
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / GATE_JSON_PATH, packet)
    md_path = root / GATE_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
