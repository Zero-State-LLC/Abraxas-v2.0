from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_planning_receipt import (
    PLANNING_RECEIPT_JSON_PATH as SOURCE_PLANNING_RECEIPT_JSON_PATH,
)

SCHEMA_VERSION = "V2HygienePhase1StabilizationDecisionRecordCreationGate.v1"
GATE_ID = "v2_hygiene_phase1_stabilization_decision_record_creation_gate_001"
GATE_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_creation_gate_001.latest.json"
)
GATE_MD_PATH = GATE_JSON_PATH.with_suffix(".md")
NOT_COMPUTABLE = "NOT_COMPUTABLE"
ELIGIBLE_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_GATE_"
    "ELIGIBLE_FOR_SEPARATE_CREATION_PLANNING"
)
BLOCKED_STATUS = "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_GATE_BLOCKED"
EXPECTED_PLANNING_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_PLANNING_RECEIPT_READY"
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
    "valid_for_decision_record_creation",
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


def _planned_record(packet: Mapping[str, Any]) -> Mapping[str, Any]:
    record = packet.get("planned_decision_record")
    return record if isinstance(record, Mapping) else {}


def _planned_field_group_ids(record: Mapping[str, Any]) -> list[str]:
    groups = record.get("field_groups")
    if not isinstance(groups, list):
        return []
    return sorted(
        str(group.get("group_id"))
        for group in groups
        if isinstance(group, Mapping) and group.get("source_group_validated") is True
    )


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
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": expected_status,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "recommended_next_lane": str(packet.get("recommended_next_lane", NOT_COMPUTABLE)),
        "safe_to_auto_continue": packet.get("safe_to_auto_continue"),
        "valid_for_execution": packet.get("valid_for_execution"),
    }


def _source_blockers(planning: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    planned_record = _planned_record(planning)
    if planning.get("status") != EXPECTED_PLANNING_STATUS:
        blockers.append("source_planning_receipt_not_ready")
    if planning.get("decision_record_planning_ready") is not True:
        blockers.append("source_decision_record_planning_ready_not_true")
    if planning.get("future_record_creation_gate_required") is not True:
        blockers.append("source_future_record_creation_gate_not_required")
    if planning.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append("source_planning_recommended_next_lane_not_not_computable")
    if planning.get("safe_to_auto_continue") is not False:
        blockers.append("source_planning_safe_to_auto_continue_not_false")
    if planning.get("valid_for_execution") is not False:
        blockers.append("source_planning_valid_for_execution_not_false")
    if planning.get("valid_for_decision_record_creation") is not False:
        blockers.append("source_planning_valid_for_creation_not_false")

    if not planned_record:
        blockers.append("source_planned_decision_record_missing")
    if planned_record.get("record_created") is not False:
        blockers.append("source_planned_record_created_not_false")
    if planned_record.get("record_creation_allowed") is not False:
        blockers.append("source_planned_record_creation_allowed_not_false")
    if planned_record.get("record_creation_authorized") is not False:
        blockers.append("source_planned_record_creation_authorized_not_false")
    if planned_record.get("field_group_count") != len(REQUIRED_ATTESTATION_GROUPS):
        blockers.append("source_planned_record_field_group_count_mismatch")
    if _planned_field_group_ids(planned_record) != sorted(REQUIRED_ATTESTATION_GROUPS):
        blockers.append("source_planned_record_required_groups_not_all_validated")
    if planned_record.get("authority_granted") is not False:
        blockers.append("source_planned_record_authority_granted_not_false")

    if not _locks_all_false(planning.get("authority_locks")):
        blockers.append("planning_receipt_authority_locks_not_all_false")
    blockers.extend(_authority_expansion_blockers("planning_receipt", planning))
    return sorted(set(blockers))


def build_v2_hygiene_phase1_stabilization_decision_record_creation_gate(
    repo_root: str | Path = ".",
    *,
    source_planning_receipt_path: str | Path = SOURCE_PLANNING_RECEIPT_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    planning_path = Path(source_planning_receipt_path)
    planning = _read_json(root / planning_path) or {}
    sources_observed = bool(planning)
    blockers = _source_blockers(planning)
    if not sources_observed:
        blockers = sorted(set(blockers + ["required_planning_receipt_missing"]))
    eligible = sources_observed and not blockers
    status = ELIGIBLE_STATUS if eligible else (NOT_COMPUTABLE if not sources_observed else BLOCKED_STATUS)
    planned_record = dict(_planned_record(planning))
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "status": status,
        "sources_observed": sources_observed,
        "source_records": [
            _source_record(
                "stabilization_decision_record_planning_receipt",
                planning_path,
                planning,
                expected_status=EXPECTED_PLANNING_STATUS,
                hash_field="planning_receipt_hash",
            ),
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if eligible else "SOURCE_ARTIFACTS_NOT_READY",
        "decision_record_creation_gate_eligible": eligible,
        "planned_record_output": {
            "record_id": str(
                planned_record.get(
                    "record_id",
                    "v2_hygiene_phase1_stabilization_decision_record_001",
                )
            ),
            "record_creation_allowed": False,
            "record_creation_authorized": False,
            "record_created": False,
            "source_planning_receipt_hash": str(
                planning.get("planning_receipt_hash", NOT_COMPUTABLE)
            ),
            "source_attestation_payload_file_hash": str(
                planned_record.get("source_attestation_payload_file_hash", NOT_COMPUTABLE)
            ),
            "source_attestation_payload_packet_hash": str(
                planned_record.get("source_attestation_payload_packet_hash", NOT_COMPUTABLE)
            ),
            "field_group_count": int(planned_record.get("field_group_count", 0)),
            "field_group_ids": _planned_field_group_ids(planned_record),
            "creation_gate_only": True,
            "authority_granted": False,
        },
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
            "prepare a separately governed creation plan or operator review for the "
            "planned stabilization decision record; this gate does not create records "
            "or grant authority"
            if eligible
            else "restore the ready planning receipt before any future record-creation gate"
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


def render_v2_hygiene_phase1_stabilization_decision_record_creation_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    planned_output = packet["planned_record_output"]
    lines = [
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Creation Gate",
        "",
        f"- gate_id: {packet['gate_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- decision_record_creation_gate_eligible: {packet['decision_record_creation_gate_eligible']}",
        f"- planned_record_id: {planned_output['record_id']}",
        f"- record_creation_allowed: {planned_output['record_creation_allowed']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- valid_for_decision_record_creation: {packet['valid_for_decision_record_creation']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Planned Record Output",
        f"- field_group_count: {planned_output['field_group_count']}",
        f"- field_group_ids: {', '.join(planned_output['field_group_ids'])}",
        f"- authority_granted: {planned_output['authority_granted']}",
        "",
        "## Source Blockers",
    ]
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase1_stabilization_decision_record_creation_gate(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_creation_gate(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / GATE_JSON_PATH, packet)
    md_path = root / GATE_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_stabilization_decision_record_creation_gate_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
