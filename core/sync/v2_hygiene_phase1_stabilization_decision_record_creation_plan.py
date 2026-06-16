from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_creation_gate import (
    GATE_JSON_PATH as SOURCE_CREATION_GATE_JSON_PATH,
)
from core.sync.v2_hygiene_phase1_stabilization_decision_record_planning_receipt import (
    PLANNING_RECEIPT_JSON_PATH as SOURCE_PLANNING_RECEIPT_JSON_PATH,
)

SCHEMA_VERSION = "V2HygienePhase1StabilizationDecisionRecordCreationPlan.v1"
PLAN_ID = "v2_hygiene_phase1_stabilization_decision_record_creation_plan_001"
PLAN_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_creation_plan_001.latest.json"
)
PLAN_MD_PATH = PLAN_JSON_PATH.with_suffix(".md")
NOT_COMPUTABLE = "NOT_COMPUTABLE"
READY_STATUS = "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_PLAN_READY"
BLOCKED_STATUS = "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_PLAN_BLOCKED"
EXPECTED_CREATION_GATE_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_GATE_"
    "ELIGIBLE_FOR_SEPARATE_CREATION_PLANNING"
)
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


def _planned_record_from_receipt(packet: Mapping[str, Any]) -> Mapping[str, Any]:
    record = packet.get("planned_decision_record")
    return record if isinstance(record, Mapping) else {}


def _planned_output_from_gate(packet: Mapping[str, Any]) -> Mapping[str, Any]:
    output = packet.get("planned_record_output")
    return output if isinstance(output, Mapping) else {}


def _field_group_ids(value: Mapping[str, Any]) -> list[str]:
    if isinstance(value.get("field_group_ids"), list):
        return sorted(str(item) for item in value["field_group_ids"])
    groups = value.get("field_groups")
    if isinstance(groups, list):
        return sorted(
            str(group.get("group_id"))
            for group in groups
            if isinstance(group, Mapping) and group.get("source_group_validated") is True
        )
    return []


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


def _source_blockers(
    *,
    gate: Mapping[str, Any],
    planning: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    gate_output = _planned_output_from_gate(gate)
    receipt_record = _planned_record_from_receipt(planning)

    if gate.get("status") != EXPECTED_CREATION_GATE_STATUS:
        blockers.append("source_creation_gate_not_eligible")
    if gate.get("decision_record_creation_gate_eligible") is not True:
        blockers.append("source_creation_gate_eligible_not_true")
    if gate.get("safe_to_auto_continue") is not False:
        blockers.append("source_creation_gate_safe_to_auto_continue_not_false")
    if gate.get("valid_for_execution") is not False:
        blockers.append("source_creation_gate_valid_for_execution_not_false")
    if gate.get("valid_for_decision_record_creation") is not False:
        blockers.append("source_creation_gate_valid_for_creation_not_false")

    if gate_output.get("record_created") is not False:
        blockers.append("source_creation_gate_record_created_not_false")
    if gate_output.get("record_creation_allowed") is not False:
        blockers.append("source_creation_gate_record_creation_allowed_not_false")
    if gate_output.get("record_creation_authorized") is not False:
        blockers.append("source_creation_gate_record_creation_authorized_not_false")
    if gate_output.get("field_group_count") != len(REQUIRED_ATTESTATION_GROUPS):
        blockers.append("source_creation_gate_field_group_count_mismatch")
    if _field_group_ids(gate_output) != sorted(REQUIRED_ATTESTATION_GROUPS):
        blockers.append("source_creation_gate_required_groups_not_all_validated")

    if planning.get("status") != EXPECTED_PLANNING_STATUS:
        blockers.append("source_planning_receipt_not_ready")
    if planning.get("decision_record_planning_ready") is not True:
        blockers.append("source_planning_ready_not_true")
    if planning.get("future_record_creation_gate_required") is not True:
        blockers.append("source_planning_future_creation_gate_not_required")
    if receipt_record.get("record_id") != gate_output.get("record_id"):
        blockers.append("source_record_id_mismatch")
    if _field_group_ids(receipt_record) != _field_group_ids(gate_output):
        blockers.append("source_field_group_ids_mismatch")

    for source_id, packet in (
        ("creation_gate", gate),
        ("planning_receipt", planning),
    ):
        if packet.get("recommended_next_lane") != NOT_COMPUTABLE:
            blockers.append(f"{source_id}_recommended_next_lane_not_not_computable")
        if not _locks_all_false(packet.get("authority_locks")):
            blockers.append(f"{source_id}_authority_locks_not_all_false")
        blockers.extend(_authority_expansion_blockers(source_id, packet))
    return sorted(set(blockers))


def build_v2_hygiene_phase1_stabilization_decision_record_creation_plan(
    repo_root: str | Path = ".",
    *,
    source_creation_gate_path: str | Path = SOURCE_CREATION_GATE_JSON_PATH,
    source_planning_receipt_path: str | Path = SOURCE_PLANNING_RECEIPT_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    gate_path = Path(source_creation_gate_path)
    planning_path = Path(source_planning_receipt_path)
    gate = _read_json(root / gate_path) or {}
    planning = _read_json(root / planning_path) or {}
    sources_observed = bool(gate) and bool(planning)
    blockers = _source_blockers(gate=gate, planning=planning)
    if not sources_observed:
        blockers = sorted(set(blockers + ["one_or_more_required_source_artifacts_missing"]))
    ready = sources_observed and not blockers
    status = READY_STATUS if ready else (NOT_COMPUTABLE if not sources_observed else BLOCKED_STATUS)
    gate_output = dict(_planned_output_from_gate(gate))
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "plan_id": PLAN_ID,
        "status": status,
        "sources_observed": sources_observed,
        "source_records": [
            _source_record(
                "stabilization_decision_record_creation_gate",
                gate_path,
                gate,
                expected_status=EXPECTED_CREATION_GATE_STATUS,
                hash_field="gate_hash",
            ),
            _source_record(
                "stabilization_decision_record_planning_receipt",
                planning_path,
                planning,
                expected_status=EXPECTED_PLANNING_STATUS,
                hash_field="planning_receipt_hash",
            ),
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "decision_record_creation_plan_ready": ready,
        "planned_creation": {
            "record_id": str(
                gate_output.get(
                    "record_id",
                    "v2_hygiene_phase1_stabilization_decision_record_001",
                )
            ),
            "record_output_path": (
                "out/operator_review/"
                "v2_hygiene_phase1_stabilization_decision_record_001.latest.json"
            ),
            "record_creation_allowed": False,
            "record_creation_authorized": False,
            "record_created": False,
            "requires_separate_creation_authorization": True,
            "requires_operator_review_before_creation": True,
            "source_creation_gate_hash": str(gate.get("gate_hash", NOT_COMPUTABLE)),
            "source_planning_receipt_hash": str(
                planning.get("planning_receipt_hash", NOT_COMPUTABLE)
            ),
            "source_attestation_payload_file_hash": str(
                gate_output.get("source_attestation_payload_file_hash", NOT_COMPUTABLE)
            ),
            "source_attestation_payload_packet_hash": str(
                gate_output.get("source_attestation_payload_packet_hash", NOT_COMPUTABLE)
            ),
            "field_group_count": int(gate_output.get("field_group_count", 0)),
            "field_group_ids": _field_group_ids(gate_output),
            "planned_creation_steps": [
                "verify creation gate remains eligible and authority-locked",
                "verify operator attestation payload hashes are unchanged",
                "materialize decision record only in a separately governed creation lane",
                "run validation without granting execution or implementation authority",
            ],
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
            "hold for separate operator-reviewed decision-record creation; this plan "
            "does not create the record or grant authority"
            if ready
            else "restore the eligible creation gate and planning receipt before creation planning"
        ),
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authority_locks": _authority_locks(),
        "downstream": NOT_COMPUTABLE,
        "plan_hash": "",
    }
    packet["plan_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "plan_hash"}
    )
    return packet


def render_v2_hygiene_phase1_stabilization_decision_record_creation_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    creation = packet["planned_creation"]
    lines = [
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Creation Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- decision_record_creation_plan_ready: {packet['decision_record_creation_plan_ready']}",
        f"- record_id: {creation['record_id']}",
        f"- record_creation_allowed: {creation['record_creation_allowed']}",
        f"- requires_separate_creation_authorization: {creation['requires_separate_creation_authorization']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- valid_for_decision_record_creation: {packet['valid_for_decision_record_creation']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Planned Creation Steps",
    ]
    lines.extend(f"- {step}" for step in creation["planned_creation_steps"])
    lines.extend(["", "## Source Blockers"])
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase1_stabilization_decision_record_creation_plan(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_creation_plan(
        repo_root
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / PLAN_JSON_PATH, packet)
    md_path = root / PLAN_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_stabilization_decision_record_creation_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
