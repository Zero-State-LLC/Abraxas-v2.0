from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_creation_plan import (
    PLAN_JSON_PATH as SOURCE_CREATION_PLAN_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = (
    "V2HygienePhase1StabilizationDecisionRecordCreationAuthorizationGate.v1"
)
GATE_ID = (
    "v2_hygiene_phase1_stabilization_decision_record_creation_authorization_gate_001"
)
GATE_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_creation_authorization_gate_001.latest.json"
)
GATE_MD_PATH = GATE_JSON_PATH.with_suffix(".md")
HELD_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_AUTHORIZATION_GATE_"
    "HELD_FOR_OPERATOR"
)
BLOCKED_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_AUTHORIZATION_GATE_BLOCKED"
)
EXPECTED_PLAN_STATUS = "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_PLAN_READY"
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


def _planned_creation(packet: Mapping[str, Any]) -> Mapping[str, Any]:
    creation = packet.get("planned_creation")
    return creation if isinstance(creation, Mapping) else {}


def _field_group_ids(creation: Mapping[str, Any]) -> list[str]:
    values = creation.get("field_group_ids")
    if not isinstance(values, list):
        return []
    return sorted(str(value) for value in values)


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


def _source_blockers(plan: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    creation = _planned_creation(plan)
    if plan.get("status") != EXPECTED_PLAN_STATUS:
        blockers.append("source_creation_plan_not_ready")
    if plan.get("decision_record_creation_plan_ready") is not True:
        blockers.append("source_creation_plan_ready_not_true")
    if plan.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append("source_creation_plan_recommended_next_lane_not_not_computable")
    if plan.get("safe_to_auto_continue") is not False:
        blockers.append("source_creation_plan_safe_to_auto_continue_not_false")
    if plan.get("valid_for_execution") is not False:
        blockers.append("source_creation_plan_valid_for_execution_not_false")
    if plan.get("valid_for_decision_record_creation") is not False:
        blockers.append("source_creation_plan_valid_for_creation_not_false")

    if not creation:
        blockers.append("source_planned_creation_missing")
    if creation.get("record_created") is not False:
        blockers.append("source_planned_creation_record_created_not_false")
    if creation.get("record_creation_allowed") is not False:
        blockers.append("source_planned_creation_allowed_not_false")
    if creation.get("record_creation_authorized") is not False:
        blockers.append("source_planned_creation_authorized_not_false")
    if creation.get("requires_separate_creation_authorization") is not True:
        blockers.append("source_planned_creation_separate_authorization_not_required")
    if creation.get("requires_operator_review_before_creation") is not True:
        blockers.append("source_planned_creation_operator_review_not_required")
    if creation.get("field_group_count") != len(REQUIRED_ATTESTATION_GROUPS):
        blockers.append("source_planned_creation_field_group_count_mismatch")
    if _field_group_ids(creation) != sorted(REQUIRED_ATTESTATION_GROUPS):
        blockers.append("source_planned_creation_required_groups_not_all_present")
    if creation.get("authority_granted") is not False:
        blockers.append("source_planned_creation_authority_granted_not_false")
    if not _locks_all_false(plan.get("authority_locks")):
        blockers.append("creation_plan_authority_locks_not_all_false")
    blockers.extend(_authority_expansion_blockers("creation_plan", plan))
    return sorted(set(blockers))


def build_v2_hygiene_phase1_stabilization_decision_record_creation_authorization_gate(
    repo_root: str | Path = ".",
    *,
    source_creation_plan_path: str | Path = SOURCE_CREATION_PLAN_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    plan_path = Path(source_creation_plan_path)
    plan = _read_json(root / plan_path) or {}
    sources_observed = bool(plan)
    blockers = _source_blockers(plan)
    if not sources_observed:
        blockers = sorted(set(blockers + ["required_creation_plan_missing"]))
    ready = sources_observed and not blockers
    status = HELD_STATUS if ready else (NOT_COMPUTABLE if not sources_observed else BLOCKED_STATUS)
    creation = dict(_planned_creation(plan))
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "status": status,
        "sources_observed": sources_observed,
        "source_records": [
            _source_record(
                "stabilization_decision_record_creation_plan",
                plan_path,
                plan,
                expected_status=EXPECTED_PLAN_STATUS,
                hash_field="plan_hash",
            ),
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "operator_review_required": True,
        "selected_operator_decision": "HOLD_FOR_OPERATOR_DECISION_RECORD_CREATION",
        "selected_follow_on_action": "MAINTAIN_STABILIZATION_DECISION_RECORD_CREATION_HOLD",
        "planned_creation_authorization": {
            "record_id": str(
                creation.get(
                    "record_id",
                    "v2_hygiene_phase1_stabilization_decision_record_001",
                )
            ),
            "record_output_path": str(creation.get("record_output_path", NOT_COMPUTABLE)),
            "authorization_gate_ready": ready,
            "record_creation_allowed": False,
            "record_creation_authorized": False,
            "record_created": False,
            "requires_external_operator_decision": True,
            "source_creation_plan_hash": str(plan.get("plan_hash", NOT_COMPUTABLE)),
            "source_creation_gate_hash": str(
                creation.get("source_creation_gate_hash", NOT_COMPUTABLE)
            ),
            "field_group_count": int(creation.get("field_group_count", 0)),
            "field_group_ids": _field_group_ids(creation),
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
            "hold for explicit external operator decision-record creation approval; "
            "do not create records, evidence bundles, authorization records, "
            "implementation lanes, writeback, mutation, activation, promotion, "
            "registration, auto-continuation, or execution authority"
            if ready
            else "restore the ready creation plan before operator creation authorization review"
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


def render_v2_hygiene_phase1_stabilization_decision_record_creation_authorization_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    auth = packet["planned_creation_authorization"]
    lines = [
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Creation Authorization Gate",
        "",
        f"- gate_id: {packet['gate_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- operator_review_required: {packet['operator_review_required']}",
        f"- selected_operator_decision: {packet['selected_operator_decision']}",
        f"- selected_follow_on_action: {packet['selected_follow_on_action']}",
        f"- record_id: {auth['record_id']}",
        f"- record_creation_authorized: {auth['record_creation_authorized']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- valid_for_decision_record_creation: {packet['valid_for_decision_record_creation']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Source Blockers",
    ]
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase1_stabilization_decision_record_creation_authorization_gate(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = (
        build_v2_hygiene_phase1_stabilization_decision_record_creation_authorization_gate(
            repo_root
        )
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / GATE_JSON_PATH, packet)
    md_path = root / GATE_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_stabilization_decision_record_creation_authorization_gate_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
