from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_completion_authorization_gate import (
    GATE_JSON_PATH as SOURCE_COMPLETION_AUTHORIZATION_GATE_JSON_PATH,
)
from scripts.preflight.preflight_v2_hygiene_phase1_stabilization_decision_record_completion_approval_payload import (
    DEFAULT_COMPLETION_APPROVAL_PAYLOAD_PATH,
    preflight_payload,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = (
    "V2HygienePhase1StabilizationDecisionRecordCompletionApprovalIntakeGate.v1"
)
GATE_ID = (
    "v2_hygiene_phase1_stabilization_decision_record_completion_approval_intake_gate_001"
)
GATE_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_approval_intake_gate_001.latest.json"
)
GATE_MD_PATH = GATE_JSON_PATH.with_suffix(".md")
READY_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_APPROVAL_"
    "INTAKE_VALIDATED_FOR_FUTURE_RECORD_COMPLETION_GATE"
)
BLOCKED_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_APPROVAL_"
    "INTAKE_GATE_BLOCKED"
)
EXPECTED_AUTHORIZATION_GATE_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_AUTHORIZATION_"
    "GATE_HELD_FOR_OPERATOR"
)
AUTHORITY_EXPANDING_FIELDS = (
    "decision_record_created",
    "decision_record_creation_authorized",
    "decision_record_completed",
    "decision_record_emitted",
    "decision_record_emission_authorized",
    "decision_record_finalized",
    "decision_record_finalization_authorized",
    "decision_record_materialized",
    "decision_record_completion_authorized",
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


def _payload_blockers(preflight: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if preflight.get("payload_observed") is not True:
        blockers.append("completion_approval_payload_missing")
    if preflight.get("valid") is not True:
        blockers.append("completion_approval_payload_not_valid")
    blockers.extend(str(item) for item in preflight.get("validation_blockers", []))
    return sorted(set(blockers))


def _planned_authorization(packet: Mapping[str, Any]) -> Mapping[str, Any]:
    auth = packet.get("planned_completion_authorization")
    return auth if isinstance(auth, Mapping) else {}


def _authorization_gate_blockers(gate: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    auth = _planned_authorization(gate)
    if gate.get("status") != EXPECTED_AUTHORIZATION_GATE_STATUS:
        blockers.append("source_completion_authorization_gate_not_held")
    if gate.get("operator_review_required") is not True:
        blockers.append("source_operator_review_not_required")
    if gate.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append("source_recommended_next_lane_not_not_computable")
    if gate.get("safe_to_auto_continue") is not False:
        blockers.append("source_safe_to_auto_continue_not_false")
    if gate.get("valid_for_execution") is not False:
        blockers.append("source_valid_for_execution_not_false")
    if gate.get("valid_for_decision_record_completion", False) is not False:
        blockers.append("source_valid_for_completion_not_false")
    if gate.get("valid_for_decision_record_emission", False) is not False:
        blockers.append("source_valid_for_emission_not_false")
    if gate.get("valid_for_decision_record_finalization", False) is not False:
        blockers.append("source_valid_for_finalization_not_false")
    if not auth:
        blockers.append("source_planned_completion_authorization_missing")
    if auth.get("authorization_gate_ready") is not True:
        blockers.append("source_authorization_gate_ready_not_true")
    if auth.get("record_completion_allowed") is not False:
        blockers.append("source_completion_allowed_not_false")
    if auth.get("record_completion_authorized") is not False:
        blockers.append("source_completion_authorized_not_false")
    if auth.get("record_completed") is not False:
        blockers.append("source_record_completed_not_false")
    if auth.get("record_emitted") is not False:
        blockers.append("source_record_emitted_not_false")
    if auth.get("record_finalized") is not False:
        blockers.append("source_record_finalized_not_false")
    if auth.get("record_materialized") is not False:
        blockers.append("source_record_materialized_not_false")
    if auth.get("requires_external_operator_decision") is not True:
        blockers.append("source_external_operator_decision_not_required")
    if auth.get("authority_granted") is not False:
        blockers.append("source_authority_granted_not_false")
    if not _locks_all_false(gate.get("authority_locks")):
        blockers.append("source_authority_locks_not_all_false")
    blockers.extend(_authority_expansion_blockers("completion_authorization_gate", gate))
    return sorted(set(blockers))


def _source_record(
    source_id: str,
    path: Path,
    *,
    observed: bool,
    status: str,
    packet_hash: str,
    authority_locks_all_false: bool,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    record = {
        "source_id": source_id,
        "path": path.as_posix(),
        "observed": observed,
        "file_hash": _sha256(path),
        "packet_hash": packet_hash,
        "status": status,
        "authority_locks_all_false": authority_locks_all_false,
    }
    if extra:
        record.update(extra)
    return record


def build_v2_hygiene_phase1_stabilization_decision_record_completion_approval_intake_gate(
    repo_root: str | Path = ".",
    *,
    completion_approval_payload_path: str | Path = DEFAULT_COMPLETION_APPROVAL_PAYLOAD_PATH,
    source_completion_authorization_gate_path: str | Path = SOURCE_COMPLETION_AUTHORIZATION_GATE_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    payload_path = Path(completion_approval_payload_path)
    gate_path = Path(source_completion_authorization_gate_path)
    payload_preflight = preflight_payload(
        payload_path,
        repo_root=root,
        template_mode=False,
    )
    gate = _read_json(root / gate_path) or {}
    payload = _read_json(root / payload_path) or {}
    operator_identity = payload.get("operator_identity", {})
    auth = dict(_planned_authorization(gate))
    payload_ready = bool(payload_preflight.get("valid") is True)
    gate_observed = bool(gate)
    blockers = sorted(
        set(
            _payload_blockers(payload_preflight)
            + (
                _authorization_gate_blockers(gate)
                if gate_observed
                else ["source_completion_authorization_gate_missing"]
            )
        )
    )
    if gate_observed and payload_ready:
        if operator_identity.get("operator_id") != auth.get("operator_id"):
            blockers.append("operator_identity.operator_id_source_mismatch")
        if operator_identity.get("operator_reviewed_at_source_observed") != auth.get(
            "operator_reviewed_at_source_observed"
        ):
            blockers.append(
                "operator_identity.operator_reviewed_at_source_observed_source_mismatch"
            )
        if operator_identity.get("operator_approval_hash") != auth.get(
            "source_operator_approval_hash"
        ):
            blockers.append("operator_identity.operator_approval_hash_source_mismatch")
        blockers = sorted(set(blockers))
    ready = payload_ready and gate_observed and not blockers
    status = READY_STATUS if ready else (NOT_COMPUTABLE if not gate_observed else BLOCKED_STATUS)

    disposition = payload.get("completion_disposition", {})

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "status": status,
        "sources_observed": payload_preflight.get("payload_observed") is True
        and gate_observed,
        "source_records": [
            _source_record(
                "completion_approval_payload",
                payload_path,
                observed=payload_preflight.get("payload_observed") is True,
                status="COMPLETION_APPROVAL_PAYLOAD_VALIDATED"
                if payload_ready
                else NOT_COMPUTABLE,
                packet_hash=_sha256(root / payload_path),
                authority_locks_all_false=True,
                extra={
                    "preflight_valid": payload_preflight.get("valid") is True,
                    "validation_blockers": payload_preflight.get(
                        "validation_blockers",
                        [],
                    ),
                },
            ),
            _source_record(
                "completion_authorization_gate",
                gate_path,
                observed=gate_observed,
                status=str(gate.get("status", NOT_COMPUTABLE)),
                packet_hash=str(gate.get("gate_hash", NOT_COMPUTABLE)),
                authority_locks_all_false=_locks_all_false(gate.get("authority_locks")),
                extra={
                    "expected_status": EXPECTED_AUTHORIZATION_GATE_STATUS,
                    "recommended_next_lane": str(
                        gate.get("recommended_next_lane", NOT_COMPUTABLE)
                    ),
                    "safe_to_auto_continue": gate.get("safe_to_auto_continue"),
                    "valid_for_execution": gate.get("valid_for_execution"),
                },
            ),
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "operator_approval_observed": payload_ready,
        "operator_approval_hash": str(
            operator_identity.get("operator_approval_hash", NOT_COMPUTABLE)
        ),
        "operator_id": str(operator_identity.get("operator_id", NOT_COMPUTABLE)),
        "operator_reviewed_at_source_observed": str(
            operator_identity.get("operator_reviewed_at_source_observed", NOT_COMPUTABLE)
        ),
        "selected_operator_decision": "VALIDATE_COMPLETION_APPROVAL_FOR_FUTURE_RECORD_COMPLETION_GATE"
        if ready
        else NOT_COMPUTABLE,
        "selected_follow_on_action": "PLAN_SEPARATE_DECISION_RECORD_COMPLETION_GATE"
        if ready
        else NOT_COMPUTABLE,
        "approved_record_id": str(
            disposition.get(
                "approved_record_id",
                auth.get(
                    "record_id",
                    "v2_hygiene_phase1_stabilization_decision_record_001",
                ),
            )
        ),
        "approved_record_output_path": str(
            disposition.get("approved_record_output_path", auth.get("record_output_path", NOT_COMPUTABLE))
        ),
        "completion_approval_validated_for_future_record_completion_gate": ready,
        "separate_record_completion_gate_required": True,
        "decision_record_created": False,
        "decision_record_creation_authorized": False,
        "decision_record_completed": False,
        "decision_record_emitted": False,
        "decision_record_emission_authorized": False,
        "decision_record_finalized": False,
        "decision_record_finalization_authorized": False,
        "decision_record_materialized": False,
        "decision_record_completion_authorized": False,
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
        "valid_for_decision_record_emission": False,
        "valid_for_decision_record_finalization": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_action": (
            "plan a separate governed stabilization decision-record completion validation gate; "
            "this intake does not complete, finalize, emit, or materialize the record"
            if ready
            else "repair the completion approval payload or authorization gate before record-completion planning"
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


def render_v2_hygiene_phase1_stabilization_decision_record_completion_approval_intake_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Completion Approval Intake Gate",
        "",
        f"- gate_id: {packet['gate_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- operator_approval_observed: {packet['operator_approval_observed']}",
        f"- selected_operator_decision: {packet['selected_operator_decision']}",
        f"- selected_follow_on_action: {packet['selected_follow_on_action']}",
        f"- approved_record_id: {packet['approved_record_id']}",
        f"- completion_approval_validated_for_future_record_completion_gate: {packet['completion_approval_validated_for_future_record_completion_gate']}",
        f"- decision_record_completed: {packet['decision_record_completed']}",
        f"- decision_record_finalized: {packet['decision_record_finalized']}",
        f"- decision_record_emitted: {packet['decision_record_emitted']}",
        f"- decision_record_materialized: {packet['decision_record_materialized']}",
        f"- decision_record_completion_authorized: {packet['decision_record_completion_authorized']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- valid_for_decision_record_completion: {packet['valid_for_decision_record_completion']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Source Blockers",
    ]
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase1_stabilization_decision_record_completion_approval_intake_gate(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_approval_intake_gate(
        repo_root
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / GATE_JSON_PATH, packet)
    md_path = root / GATE_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_stabilization_decision_record_completion_approval_intake_gate_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
