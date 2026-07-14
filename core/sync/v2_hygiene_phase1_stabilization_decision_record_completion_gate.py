from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_finalization_approval_intake_gate import (
    GATE_JSON_PATH as SOURCE_FINALIZATION_APPROVAL_INTAKE_GATE_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygienePhase1StabilizationDecisionRecordCompletionGate.v1"
GATE_ID = "v2_hygiene_phase1_stabilization_decision_record_completion_gate_001"
GATE_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_gate_001.latest.json"
)
GATE_MD_PATH = GATE_JSON_PATH.with_suffix(".md")
ELIGIBLE_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_GATE_"
    "ELIGIBLE_FOR_SEPARATE_RECORD_COMPLETION_PLANNING"
)
BLOCKED_STATUS = "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_GATE_BLOCKED"
EXPECTED_INTAKE_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_FINALIZATION_APPROVAL_"
    "INTAKE_VALIDATED_FOR_FUTURE_RECORD_FINALIZATION_GATE"
)
AUTHORITY_EXPANDING_FIELDS = (
    "decision_record_created",
    "decision_record_creation_authorized",
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
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": path.as_posix(),
        "observed": bool(packet),
        "file_hash": _sha256(path),
        "packet_hash": str(packet.get("gate_hash", NOT_COMPUTABLE)),
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_INTAKE_STATUS,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "recommended_next_lane": str(packet.get("recommended_next_lane", NOT_COMPUTABLE)),
        "safe_to_auto_continue": packet.get("safe_to_auto_continue"),
        "valid_for_execution": packet.get("valid_for_execution"),
    }


def _source_blockers(intake: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if intake.get("status") != EXPECTED_INTAKE_STATUS:
        blockers.append("source_finalization_approval_intake_not_validated")
    if (
        intake.get("finalization_approval_validated_for_future_record_finalization_gate")
        is not True
    ):
        blockers.append("source_finalization_approval_not_validated")
    if intake.get("operator_approval_observed") is not True:
        blockers.append("source_operator_approval_not_observed")
    if intake.get("separate_record_finalization_gate_required") is not True:
        blockers.append("source_record_finalization_gate_not_required")
    if intake.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append("source_recommended_next_lane_not_not_computable")
    if intake.get("safe_to_auto_continue") is not False:
        blockers.append("source_safe_to_auto_continue_not_false")
    if intake.get("valid_for_execution") is not False:
        blockers.append("source_valid_for_execution_not_false")
    if intake.get("valid_for_decision_record_emission", False) is not False:
        blockers.append("source_valid_for_emission_not_false")
    if intake.get("valid_for_decision_record_finalization") is not False:
        blockers.append("source_valid_for_finalization_not_false")
    if intake.get("decision_record_emitted", False) is not False:
        blockers.append("source_decision_record_emitted_not_false")
    if intake.get("decision_record_emission_authorized", False) is not False:
        blockers.append("source_emission_authorized_not_false")
    if intake.get("decision_record_finalized") is not False:
        blockers.append("source_decision_record_finalized_not_false")
    if intake.get("decision_record_finalization_authorized") is not False:
        blockers.append("source_finalization_authorized_not_false")
    if intake.get("decision_record_materialized") is not False:
        blockers.append("source_decision_record_materialized_not_false")
    if intake.get("decision_record_created") is not False:
        blockers.append("source_decision_record_created_not_false")
    if intake.get("decision_record_creation_authorized") is not False:
        blockers.append("source_creation_authorized_not_false")
    if not _locks_all_false(intake.get("authority_locks")):
        blockers.append("source_authority_locks_not_all_false")
    blockers.extend(_authority_expansion_blockers("finalization_approval_intake", intake))
    return sorted(set(blockers))


def build_v2_hygiene_phase1_stabilization_decision_record_completion_gate(
    repo_root: str | Path = ".",
    *,
    source_finalization_approval_intake_gate_path: str | Path = SOURCE_FINALIZATION_APPROVAL_INTAKE_GATE_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    intake_path = Path(source_finalization_approval_intake_gate_path)
    intake = _read_json(root / intake_path) or {}
    sources_observed = bool(intake)
    blockers = _source_blockers(intake)
    if not sources_observed:
        blockers = sorted(set(blockers + ["required_finalization_approval_intake_missing"]))
    eligible = sources_observed and not blockers
    status = ELIGIBLE_STATUS if eligible else (NOT_COMPUTABLE if not sources_observed else BLOCKED_STATUS)
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "status": status,
        "sources_observed": sources_observed,
        "source_records": [
            _source_record(
                "finalization_approval_intake_gate",
                intake_path,
                intake,
            ),
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if eligible else "SOURCE_ARTIFACTS_NOT_READY",
        "decision_record_completion_gate_eligible": eligible,
        "planned_record_completion": {
            "record_id": str(
                intake.get(
                    "approved_record_id",
                    "v2_hygiene_phase1_stabilization_decision_record_001",
                )
            ),
            "record_output_path": str(
                intake.get(
                    "approved_record_output_path",
                    "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_001.latest.json",
                )
            ),
            "record_finalization_allowed": False,
            "record_finalization_authorized": False,
            "record_finalized": False,
            "record_completion_allowed": False,
            "record_completion_authorized": False,
            "record_completed": False,
            "record_emission_allowed": False,
            "record_emission_authorized": False,
            "record_emitted": False,
            "record_materialized": False,
            "requires_separate_record_completion_plan": True,
            "requires_operator_review_before_completion": True,
            "source_finalization_approval_intake_hash": str(
                intake.get("gate_hash", NOT_COMPUTABLE)
            ),
            "source_operator_approval_hash": str(
                intake.get("operator_approval_hash", NOT_COMPUTABLE)
            ),
            "operator_id": str(intake.get("operator_id", NOT_COMPUTABLE)),
            "operator_reviewed_at_source_observed": str(
                intake.get("operator_reviewed_at_source_observed", NOT_COMPUTABLE)
            ),
            "completion_gate_only": True,
            "authority_granted": False,
        },
        "decision_record_created": False,
        "decision_record_creation_authorized": False,
        "decision_record_emitted": False,
        "decision_record_emission_authorized": False,
        "decision_record_finalized": False,
        "decision_record_finalization_authorized": False,
        "decision_record_completed": False,
        "decision_record_completion_authorized": False,
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
        "valid_for_decision_record_emission": False,
        "valid_for_decision_record_finalization": False,
        "valid_for_decision_record_completion": False,
        "valid_for_decision_record_materialization": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_action": (
            "prepare a separate governed stabilization decision-record completion plan; "
            "this gate does not finalize, emit, or materialize the decision record"
            if eligible
            else "restore the validated finalization approval intake before record-completion planning"
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


def render_v2_hygiene_phase1_stabilization_decision_record_completion_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    planned_completion = packet["planned_record_completion"]
    lines = [
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Completion Gate",
        "",
        f"- gate_id: {packet['gate_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- decision_record_completion_gate_eligible: {packet['decision_record_completion_gate_eligible']}",
        f"- record_id: {planned_completion['record_id']}",
        f"- record_completion_allowed: {planned_completion['record_completion_allowed']}",
        f"- record_completed: {planned_completion['record_completed']}",
        f"- record_finalization_allowed: {planned_completion['record_finalization_allowed']}",
        f"- record_finalized: {planned_completion['record_finalized']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- valid_for_decision_record_emission: {packet['valid_for_decision_record_emission']}",
        f"- valid_for_decision_record_finalization: {packet['valid_for_decision_record_finalization']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Planned Record Completion",
        f"- record_output_path: {planned_completion['record_output_path']}",
        f"- requires_separate_record_completion_plan: {planned_completion['requires_separate_record_completion_plan']}",
        f"- authority_granted: {planned_completion['authority_granted']}",
        "",
        "## Source Blockers",
    ]
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase1_stabilization_decision_record_completion_gate(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_gate(
        repo_root
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / GATE_JSON_PATH, packet)
    md_path = root / GATE_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_stabilization_decision_record_completion_gate_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
