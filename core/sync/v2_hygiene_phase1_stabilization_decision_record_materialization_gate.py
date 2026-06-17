from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_creation_authorization_chain_compression_audit import (
    AUDIT_JSON_PATH as SOURCE_COMPRESSION_AUDIT_JSON_PATH,
)
from scripts.preflight_v2_hygiene_phase1_stabilization_decision_record_creation_approval_payload import (
    DEFAULT_CREATION_APPROVAL_PAYLOAD_PATH,
    preflight_payload,
)

SCHEMA_VERSION = "V2HygienePhase1StabilizationDecisionRecordMaterializationGate.v1"
GATE_ID = "v2_hygiene_phase1_stabilization_decision_record_materialization_gate_001"
GATE_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_materialization_gate_001.latest.json"
)
GATE_MD_PATH = GATE_JSON_PATH.with_suffix(".md")
NOT_COMPUTABLE = "NOT_COMPUTABLE"
READY_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_MATERIALIZATION_GATE_"
    "READY_FOR_SEPARATE_MATERIALIZATION_PLANNING"
)
BLOCKED_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_MATERIALIZATION_GATE_BLOCKED"
)
EXPECTED_COMPRESSION_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_AUTHORIZATION_CHAIN_"
    "COMPRESSION_AUDIT_HELD_FOR_OPERATOR"
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


def _compression_audit_blockers(audit: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if audit.get("status") != EXPECTED_COMPRESSION_STATUS:
        blockers.append("source_compression_audit_not_held_for_operator")
    if audit.get("compression_recommendation") != (
        "COMPRESS_TO_TERMINAL_OPERATOR_DECISION_RECORD_CREATION_HOLD"
    ):
        blockers.append("source_compression_recommendation_not_terminal_hold")
    if audit.get("decision_record_created") is not False:
        blockers.append("source_compression_decision_record_created_not_false")
    if audit.get("decision_record_creation_authorized") is not False:
        blockers.append("source_compression_creation_authorized_not_false")
    if audit.get("valid_for_decision_record_creation") is not False:
        blockers.append("source_compression_valid_for_creation_not_false")
    if audit.get("valid_for_execution") is not False:
        blockers.append("source_compression_valid_for_execution_not_false")
    if audit.get("safe_to_auto_continue") is not False:
        blockers.append("source_compression_safe_to_auto_continue_not_false")
    if audit.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append("source_compression_recommended_next_lane_not_not_computable")
    if not _locks_all_false(audit.get("authority_locks")):
        blockers.append("source_compression_authority_locks_not_all_false")
    return blockers


def _payload_blockers(preflight: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if preflight.get("payload_observed") is not True:
        blockers.append("creation_approval_payload_missing")
    if preflight.get("valid") is not True:
        blockers.append("creation_approval_payload_not_valid")
    blockers.extend(str(item) for item in preflight.get("validation_blockers", []))
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


def build_v2_hygiene_phase1_stabilization_decision_record_materialization_gate(
    repo_root: str | Path = ".",
    *,
    creation_approval_payload_path: str | Path = DEFAULT_CREATION_APPROVAL_PAYLOAD_PATH,
    source_compression_audit_path: str | Path = SOURCE_COMPRESSION_AUDIT_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    payload_path = Path(creation_approval_payload_path)
    audit_path = Path(source_compression_audit_path)
    payload_preflight = preflight_payload(
        payload_path,
        repo_root=root,
        template_mode=False,
    )
    audit = _read_json(root / audit_path) or {}
    payload_ready = bool(payload_preflight.get("valid") is True)
    audit_observed = bool(audit)
    blockers = sorted(
        set(
            _payload_blockers(payload_preflight)
            + (
                _compression_audit_blockers(audit)
                if audit_observed
                else ["source_compression_audit_missing"]
            )
        )
    )
    ready = payload_ready and audit_observed and not blockers
    status = READY_STATUS if ready else (NOT_COMPUTABLE if not audit_observed else BLOCKED_STATUS)

    payload = _read_json(root / payload_path) or {}
    creation_disposition = payload.get("creation_disposition", {})
    operator_identity = payload.get("operator_identity", {})

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "status": status,
        "sources_observed": payload_preflight.get("payload_observed") is True
        and audit_observed,
        "source_records": [
            _source_record(
                "creation_approval_payload",
                payload_path,
                observed=payload_preflight.get("payload_observed") is True,
                status="CREATION_APPROVAL_PAYLOAD_VALIDATED"
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
                "creation_authorization_chain_compression_audit",
                audit_path,
                observed=audit_observed,
                status=str(audit.get("status", NOT_COMPUTABLE)),
                packet_hash=str(audit.get("audit_hash", NOT_COMPUTABLE)),
                authority_locks_all_false=_locks_all_false(audit.get("authority_locks")),
                extra={
                    "expected_status": EXPECTED_COMPRESSION_STATUS,
                    "recommended_next_lane": str(
                        audit.get("recommended_next_lane", NOT_COMPUTABLE)
                    ),
                    "safe_to_auto_continue": audit.get("safe_to_auto_continue"),
                    "valid_for_execution": audit.get("valid_for_execution"),
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
        "selected_operator_decision": "APPROVE_SEPARATE_GOVERNED_MATERIALIZATION_PLANNING"
        if ready
        else NOT_COMPUTABLE,
        "selected_follow_on_action": "PLAN_SEPARATE_DECISION_RECORD_MATERIALIZATION_GATE"
        if ready
        else NOT_COMPUTABLE,
        "approved_record_id": str(
            creation_disposition.get(
                "approved_record_id",
                "v2_hygiene_phase1_stabilization_decision_record_001",
            )
        ),
        "approved_record_output_path": str(
            creation_disposition.get("approved_record_output_path", NOT_COMPUTABLE)
        ),
        "separate_materialization_planning_allowed": ready,
        "separate_materialization_lane_required": True,
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
            "plan a separate governed stabilization decision-record materialization "
            "lane without creating the record, evidence bundle, authorization record, "
            "implementation lane, writeback, mutation, activation, promotion, "
            "registration, auto-continuation, or execution authority"
            if ready
            else "repair the creation approval payload or compression audit before materialization planning"
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


def render_v2_hygiene_phase1_stabilization_decision_record_materialization_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Materialization Gate",
        "",
        f"- gate_id: {packet['gate_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- operator_approval_observed: {packet['operator_approval_observed']}",
        f"- selected_operator_decision: {packet['selected_operator_decision']}",
        f"- selected_follow_on_action: {packet['selected_follow_on_action']}",
        f"- approved_record_id: {packet['approved_record_id']}",
        f"- decision_record_materialized: {packet['decision_record_materialized']}",
        f"- decision_record_materialization_authorized: {packet['decision_record_materialization_authorized']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- valid_for_decision_record_materialization: {packet['valid_for_decision_record_materialization']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Source Blockers",
    ]
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase1_stabilization_decision_record_materialization_gate(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_materialization_gate(
        repo_root
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / GATE_JSON_PATH, packet)
    md_path = root / GATE_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_stabilization_decision_record_materialization_gate_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
