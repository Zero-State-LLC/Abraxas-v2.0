from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_operator_review_stabilization_decision_record_plan import (
    PLAN_JSON_PATH as SOURCE_DECISION_RECORD_PLAN_JSON_PATH,
)
from core.sync.v2_hygiene_phase1_stabilization_decision_record_gate import (
    GATE_JSON_PATH as SOURCE_DECISION_RECORD_GATE_JSON_PATH,
)
from core.sync.v2_hygiene_phase1_stabilization_operator_attestation_intake_gate import (
    GATE_JSON_PATH as SOURCE_ATTESTATION_INTAKE_GATE_JSON_PATH,
)
from core.sync.v2_hygiene_phase1_stabilization_review_chain_compression_audit import (
    AUDIT_JSON_PATH as SOURCE_COMPRESSION_AUDIT_JSON_PATH,
)

SCHEMA_VERSION = "V2HygienePhase1StabilizationDecisionRecordPlanningReceipt.v1"
PLANNING_RECEIPT_ID = (
    "v2_hygiene_phase1_stabilization_decision_record_planning_receipt_001"
)
PLANNING_RECEIPT_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_planning_receipt_001.latest.json"
)
PLANNING_RECEIPT_MD_PATH = PLANNING_RECEIPT_JSON_PATH.with_suffix(".md")
NOT_COMPUTABLE = "NOT_COMPUTABLE"
READY_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_PLANNING_RECEIPT_READY"
)
BLOCKED_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_PLANNING_RECEIPT_BLOCKED"
)
EXPECTED_GATE_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_GATE_READY_FOR_SEPARATE_RECORD_PLANNING"
)
EXPECTED_INTAKE_STATUS = "ATTESTATION_INTAKE_VALIDATED_FOR_FUTURE_DECISION_RECORD_GATE"
EXPECTED_PLAN_STATUS = (
    "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_PLAN_READY"
)
EXPECTED_COMPRESSION_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_REVIEW_CHAIN_COMPRESSION_AUDIT_HELD_FOR_OPERATOR"
)
REQUIRED_ATTESTATION_GROUPS = (
    "operator_identity",
    "strategy_scope_acknowledgement",
    "stabilization_disposition",
    "authority_boundary_acknowledgement",
    "terminal_output_controls",
)
AUTHORITY_EXPANDING_FIELDS = (
    "decision_record_created",
    "decision_record_creation_authorized",
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


def _group_records(packet: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    records = packet.get("attestation_group_records")
    if not isinstance(records, list):
        return []
    return [record for record in records if isinstance(record, Mapping)]


def _validated_group_ids(packet: Mapping[str, Any]) -> list[str]:
    return sorted(
        str(record.get("group_id"))
        for record in _group_records(packet)
        if record.get("group_validated") is True
    )


def _planned_field_groups(intake: Mapping[str, Any]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for record in sorted(_group_records(intake), key=lambda item: str(item.get("group_id"))):
        groups.append(
            {
                "group_id": str(record.get("group_id")),
                "required_fields": list(record.get("required_fields", [])),
                "source_group_validated": record.get("group_validated") is True,
                "authority_granted": False,
                "record_creation_field": False,
            }
        )
    return groups


def _source_record(
    source_id: str,
    path: Path,
    packet: Mapping[str, Any],
    *,
    expected_status: str,
    hash_field: str,
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": path.as_posix(),
        "observed": bool(packet),
        "file_hash": _sha256(path),
        "packet_hash": str(packet.get(hash_field, NOT_COMPUTABLE)),
        "status": str(
            packet.get("status")
            or packet.get("decision_record_plan_status")
            or NOT_COMPUTABLE
        ),
        "expected_status": expected_status,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "recommended_next_lane": str(packet.get("recommended_next_lane", NOT_COMPUTABLE)),
        "safe_to_auto_continue": packet.get("safe_to_auto_continue"),
        "valid_for_execution": packet.get("valid_for_execution"),
    }


def _source_blockers(
    *,
    gate: Mapping[str, Any],
    intake: Mapping[str, Any],
    plan: Mapping[str, Any],
    compression: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if gate.get("status") != EXPECTED_GATE_STATUS:
        blockers.append("source_decision_record_gate_not_ready")
    if gate.get("decision_record_gate_ready") is not True:
        blockers.append("source_decision_record_gate_ready_not_true")
    if gate.get("separate_record_planning_allowed") is not True:
        blockers.append("source_separate_record_planning_not_allowed")
    if gate.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append("source_gate_recommended_next_lane_not_not_computable")
    if gate.get("safe_to_auto_continue") is not False:
        blockers.append("source_gate_safe_to_auto_continue_not_false")
    if gate.get("valid_for_execution") is not False:
        blockers.append("source_gate_valid_for_execution_not_false")
    if gate.get("valid_for_decision_record") is not False:
        blockers.append("source_gate_valid_for_decision_record_not_false")

    if intake.get("status") != EXPECTED_INTAKE_STATUS:
        blockers.append("source_intake_gate_not_validated")
    if intake.get("payload_readiness") != "OPERATOR_ATTESTATION_PAYLOAD_VALIDATED":
        blockers.append("source_intake_payload_not_validated")
    if intake.get("attested_group_count") != len(REQUIRED_ATTESTATION_GROUPS):
        blockers.append("source_intake_attested_group_count_mismatch")
    if _validated_group_ids(intake) != sorted(REQUIRED_ATTESTATION_GROUPS):
        blockers.append("source_intake_required_groups_not_all_validated")

    if plan.get("decision_record_plan_status") != EXPECTED_PLAN_STATUS:
        blockers.append("source_decision_record_plan_not_ready")
    if plan.get("decision_record_created") is not False:
        blockers.append("source_decision_record_plan_record_created_not_false")
    if plan.get("decision_record_creation_allowed") is not False:
        blockers.append("source_decision_record_plan_creation_allowed_not_false")
    if plan.get("operator_attested") is not False:
        blockers.append("source_decision_record_plan_operator_attested_not_false")

    if compression.get("status") != EXPECTED_COMPRESSION_STATUS:
        blockers.append("source_compression_audit_not_held")

    for source_id, packet in (
        ("decision_record_gate", gate),
        ("intake_gate", intake),
        ("decision_record_plan", plan),
        ("compression_audit", compression),
    ):
        if not _locks_all_false(packet.get("authority_locks")):
            blockers.append(f"{source_id}_authority_locks_not_all_false")
        blockers.extend(_authority_expansion_blockers(source_id, packet))
    return sorted(set(blockers))


def build_v2_hygiene_phase1_stabilization_decision_record_planning_receipt(
    repo_root: str | Path = ".",
    *,
    source_decision_record_gate_path: str | Path = SOURCE_DECISION_RECORD_GATE_JSON_PATH,
    source_intake_gate_path: str | Path = SOURCE_ATTESTATION_INTAKE_GATE_JSON_PATH,
    source_decision_record_plan_path: str | Path = SOURCE_DECISION_RECORD_PLAN_JSON_PATH,
    source_compression_audit_path: str | Path = SOURCE_COMPRESSION_AUDIT_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    gate_path = Path(source_decision_record_gate_path)
    intake_path = Path(source_intake_gate_path)
    plan_path = Path(source_decision_record_plan_path)
    compression_path = Path(source_compression_audit_path)
    gate = _read_json(root / gate_path) or {}
    intake = _read_json(root / intake_path) or {}
    plan = _read_json(root / plan_path) or {}
    compression = _read_json(root / compression_path) or {}
    sources_observed = all(packet for packet in (gate, intake, plan, compression))
    blockers = _source_blockers(gate=gate, intake=intake, plan=plan, compression=compression)
    if not sources_observed:
        blockers = sorted(set(blockers + ["one_or_more_required_source_artifacts_missing"]))
    ready = sources_observed and not blockers
    status = READY_STATUS if ready else (NOT_COMPUTABLE if not sources_observed else BLOCKED_STATUS)
    field_groups = _planned_field_groups(intake)
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "planning_receipt_id": PLANNING_RECEIPT_ID,
        "status": status,
        "sources_observed": sources_observed,
        "source_records": [
            _source_record(
                "stabilization_decision_record_gate",
                gate_path,
                gate,
                expected_status=EXPECTED_GATE_STATUS,
                hash_field="gate_hash",
            ),
            _source_record(
                "stabilization_operator_attestation_intake_gate",
                intake_path,
                intake,
                expected_status=EXPECTED_INTAKE_STATUS,
                hash_field="gate_hash",
            ),
            _source_record(
                "stabilization_decision_record_plan",
                plan_path,
                plan,
                expected_status=EXPECTED_PLAN_STATUS,
                hash_field="plan_hash",
            ),
            _source_record(
                "stabilization_review_chain_compression_audit",
                compression_path,
                compression,
                expected_status=EXPECTED_COMPRESSION_STATUS,
                hash_field="audit_hash",
            ),
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "decision_record_planning_ready": ready,
        "validated_attestation_group_count": int(intake.get("attested_group_count", 0)),
        "required_attestation_groups": list(REQUIRED_ATTESTATION_GROUPS),
        "validated_attestation_group_ids": _validated_group_ids(intake),
        "planned_decision_record": {
            "record_id": "v2_hygiene_phase1_stabilization_decision_record_001",
            "record_creation_allowed": False,
            "record_creation_authorized": False,
            "record_created": False,
            "source_intake_gate_hash": str(intake.get("gate_hash", NOT_COMPUTABLE)),
            "source_attestation_payload_file_hash": str(
                intake.get("attestation_payload_file_hash", NOT_COMPUTABLE)
            ),
            "source_attestation_payload_packet_hash": str(
                intake.get("attestation_payload_packet_hash", NOT_COMPUTABLE)
            ),
            "source_decision_record_gate_hash": str(gate.get("gate_hash", NOT_COMPUTABLE)),
            "field_groups": field_groups,
            "field_group_count": len(field_groups),
            "authority_granted": False,
        },
        "future_record_creation_gate_required": True,
        "decision_record_created": False,
        "decision_record_creation_authorized": False,
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
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_action": (
            "hold for a separately governed decision-record creation gate; do not "
            "create a decision record, evidence bundle, authorization record, "
            "implementation lane, writeback, mutation, activation, promotion, "
            "registration, auto-continuation, or execution authority"
            if ready
            else "restore the validated intake and decision-record gate sources before "
            "future stabilization decision-record planning"
        ),
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authority_locks": _authority_locks(),
        "downstream": NOT_COMPUTABLE,
        "planning_receipt_hash": "",
    }
    packet["planning_receipt_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "planning_receipt_hash"}
    )
    return packet


def render_v2_hygiene_phase1_stabilization_decision_record_planning_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    planned_record = packet["planned_decision_record"]
    lines = [
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Planning Receipt",
        "",
        f"- planning_receipt_id: {packet['planning_receipt_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- decision_record_planning_ready: {packet['decision_record_planning_ready']}",
        f"- planned_record_id: {planned_record['record_id']}",
        f"- record_creation_allowed: {planned_record['record_creation_allowed']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- valid_for_decision_record_creation: {packet['valid_for_decision_record_creation']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Planned Field Groups",
    ]
    for group in planned_record["field_groups"]:
        lines.append(
            "- "
            f"{group['group_id']}: fields={len(group['required_fields'])}, "
            f"source_group_validated={group['source_group_validated']}, "
            f"authority_granted={group['authority_granted']}"
        )
    lines.extend(["", "## Source Blockers"])
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase1_stabilization_decision_record_planning_receipt(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_planning_receipt(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / PLANNING_RECEIPT_JSON_PATH, packet)
    md_path = root / PLANNING_RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_stabilization_decision_record_planning_receipt_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
