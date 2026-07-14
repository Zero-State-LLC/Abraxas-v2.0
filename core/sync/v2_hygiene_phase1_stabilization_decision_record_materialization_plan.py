from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_materialization_gate import (
    GATE_JSON_PATH as SOURCE_MATERIALIZATION_GATE_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygienePhase1StabilizationDecisionRecordMaterializationPlan.v1"
PLAN_ID = "v2_hygiene_phase1_stabilization_decision_record_materialization_plan_001"
PLAN_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_materialization_plan_001.latest.json"
)
PLAN_MD_PATH = PLAN_JSON_PATH.with_suffix(".md")
READY_STATUS = "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_MATERIALIZATION_PLAN_READY"
BLOCKED_STATUS = "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_MATERIALIZATION_PLAN_BLOCKED"
EXPECTED_GATE_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_MATERIALIZATION_GATE_"
    "READY_FOR_SEPARATE_MATERIALIZATION_PLANNING"
)
AUTHORITY_EXPANDING_FIELDS = (
    "decision_record_created",
    "decision_record_creation_authorized",
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
        "expected_status": EXPECTED_GATE_STATUS,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "recommended_next_lane": str(packet.get("recommended_next_lane", NOT_COMPUTABLE)),
        "safe_to_auto_continue": packet.get("safe_to_auto_continue"),
        "valid_for_execution": packet.get("valid_for_execution"),
    }


def _source_blockers(gate: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if gate.get("status") != EXPECTED_GATE_STATUS:
        blockers.append("source_materialization_gate_not_ready")
    if gate.get("separate_materialization_planning_allowed") is not True:
        blockers.append("source_materialization_planning_not_allowed")
    if gate.get("decision_record_materialized") is not False:
        blockers.append("source_decision_record_materialized_not_false")
    if gate.get("decision_record_materialization_authorized") is not False:
        blockers.append("source_materialization_authorized_not_false")
    if gate.get("decision_record_created") is not False:
        blockers.append("source_decision_record_created_not_false")
    if gate.get("decision_record_creation_authorized") is not False:
        blockers.append("source_creation_authorized_not_false")
    if gate.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append("source_recommended_next_lane_not_not_computable")
    if gate.get("safe_to_auto_continue") is not False:
        blockers.append("source_safe_to_auto_continue_not_false")
    if gate.get("valid_for_execution") is not False:
        blockers.append("source_valid_for_execution_not_false")
    if gate.get("valid_for_decision_record_materialization") is not False:
        blockers.append("source_valid_for_materialization_not_false")
    if not _locks_all_false(gate.get("authority_locks")):
        blockers.append("source_authority_locks_not_all_false")
    blockers.extend(_authority_expansion_blockers("materialization_gate", gate))
    return sorted(set(blockers))


def build_v2_hygiene_phase1_stabilization_decision_record_materialization_plan(
    repo_root: str | Path = ".",
    *,
    source_materialization_gate_path: str | Path = SOURCE_MATERIALIZATION_GATE_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    gate_path = Path(source_materialization_gate_path)
    gate = _read_json(root / gate_path) or {}
    sources_observed = bool(gate)
    blockers = _source_blockers(gate)
    if not sources_observed:
        blockers = sorted(set(blockers + ["required_materialization_gate_missing"]))
    ready = sources_observed and not blockers
    status = READY_STATUS if ready else (NOT_COMPUTABLE if not sources_observed else BLOCKED_STATUS)
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "plan_id": PLAN_ID,
        "status": status,
        "sources_observed": sources_observed,
        "source_records": [
            _source_record(
                "stabilization_decision_record_materialization_gate",
                gate_path,
                gate,
            ),
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "decision_record_materialization_plan_ready": ready,
        "planned_materialization": {
            "record_id": str(
                gate.get(
                    "approved_record_id",
                    "v2_hygiene_phase1_stabilization_decision_record_001",
                )
            ),
            "record_output_path": str(
                gate.get(
                    "approved_record_output_path",
                    "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_001.latest.json",
                )
            ),
            "record_materialization_allowed": False,
            "record_materialization_authorized": False,
            "record_materialized": False,
            "requires_separate_materialization_authorization": True,
            "requires_operator_review_before_materialization": True,
            "source_materialization_gate_hash": str(gate.get("gate_hash", NOT_COMPUTABLE)),
            "source_creation_approval_payload_hash": str(
                gate.get("operator_approval_hash", NOT_COMPUTABLE)
            ),
            "operator_id": str(gate.get("operator_id", NOT_COMPUTABLE)),
            "operator_reviewed_at_source_observed": str(
                gate.get("operator_reviewed_at_source_observed", NOT_COMPUTABLE)
            ),
            "planned_materialization_steps": [
                "verify materialization gate remains ready and authority-locked",
                "verify the creation approval payload and source compression audit hashes are unchanged",
                "materialize the stabilization decision record only in a separately governed materialization lane",
                "validate the materialized record without granting implementation or execution authority",
            ],
            "authority_granted": False,
        },
        "decision_record_created": False,
        "decision_record_creation_authorized": False,
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
        "valid_for_decision_record_materialization": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_action": (
            "hold for a separate governed decision-record materialization "
            "authorization gate; this plan does not create or materialize the record"
            if ready
            else "restore the ready materialization gate before materialization planning"
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


def render_v2_hygiene_phase1_stabilization_decision_record_materialization_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    materialization = packet["planned_materialization"]
    lines = [
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Materialization Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- decision_record_materialization_plan_ready: {packet['decision_record_materialization_plan_ready']}",
        f"- record_id: {materialization['record_id']}",
        f"- record_materialization_allowed: {materialization['record_materialization_allowed']}",
        f"- requires_separate_materialization_authorization: {materialization['requires_separate_materialization_authorization']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- valid_for_decision_record_materialization: {packet['valid_for_decision_record_materialization']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Planned Materialization Steps",
    ]
    lines.extend(
        f"- {step}" for step in materialization["planned_materialization_steps"]
    )
    lines.extend(["", "## Source Blockers"])
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase1_stabilization_decision_record_materialization_plan(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_materialization_plan(
        repo_root
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / PLAN_JSON_PATH, packet)
    md_path = root / PLAN_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_stabilization_decision_record_materialization_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
