from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_creation_authorization_gate import (
    GATE_JSON_PATH as SOURCE_AUTHORIZATION_GATE_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = (
    "V2HygienePhase1StabilizationDecisionRecordCreationAuthorizationChainCompressionAudit.v1"
)
AUDIT_ID = (
    "v2_hygiene_phase1_stabilization_decision_record_creation_authorization_chain_compression_audit_001"
)
AUDIT_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_creation_authorization_chain_compression_audit_001.latest.json"
)
AUDIT_MD_PATH = AUDIT_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
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


def _locks_all_false(value: Any) -> bool:
    return isinstance(value, Mapping) and bool(value) and all(
        item is False for item in value.values()
    )


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


def _source_ready(source: Mapping[str, Any]) -> bool:
    return (
        source.get("schema_version")
        == "V2HygienePhase1StabilizationDecisionRecordCreationAuthorizationGate.v1"
        and source.get("status") == EXPECTED_SOURCE_STATUS
        and source.get("operator_review_required") is True
        and source.get("selected_operator_decision")
        == "HOLD_FOR_OPERATOR_DECISION_RECORD_CREATION"
        and source.get("selected_follow_on_action")
        == "MAINTAIN_STABILIZATION_DECISION_RECORD_CREATION_HOLD"
        and source.get("decision_record_created") is False
        and source.get("decision_record_creation_authorized") is False
        and source.get("authorization_record_created") is False
        and source.get("authorization_record_creation_authorized") is False
        and source.get("evidence_bundle_created") is False
        and source.get("operator_attestation_created") is False
        and source.get("implementation_authorized") is False
        and source.get("execution_authority") is False
        and source.get("valid_for_decision_record_creation") is False
        and source.get("valid_for_execution") is False
        and source.get("valid_for_implementation") is False
        and source.get("recommended_next_lane") == NOT_COMPUTABLE
        and source.get("recommended_next_patch") == NOT_COMPUTABLE
        and source.get("safe_to_auto_continue") is False
        and source.get("downstream") == NOT_COMPUTABLE
        and _locks_all_false(source.get("authority_locks"))
    )


def build_v2_hygiene_phase1_stabilization_decision_record_creation_authorization_chain_compression_audit(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / SOURCE_AUTHORIZATION_GATE_JSON_PATH
    source = _read_json(source_path)
    observed = source is not None
    source = source or {}
    ready = observed and _source_ready(source)

    if not observed:
        status = NOT_COMPUTABLE
        source_readiness = "SOURCE_CREATION_AUTHORIZATION_GATE_MISSING"
        compression_recommendation = "REPAIR_SOURCE_GATE_BEFORE_COMPRESSION"
        findings = [
            {
                "finding_id": "source_creation_authorization_gate_missing",
                "finding_status": "NOT_COMPUTABLE",
                "authority_granted": False,
            }
        ]
        terminal_hold_reason = (
            "source stabilization decision-record creation authorization gate is missing"
        )
    elif not ready:
        status = (
            "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_AUTHORIZATION_CHAIN_COMPRESSION_AUDIT_BLOCKED"
        )
        source_readiness = "SOURCE_CREATION_AUTHORIZATION_GATE_NOT_READY"
        compression_recommendation = "REPAIR_SOURCE_GATE_BEFORE_COMPRESSION"
        findings = [
            {
                "finding_id": "source_creation_authorization_gate_not_ready",
                "finding_status": "BLOCKED",
                "authority_granted": False,
            }
        ]
        terminal_hold_reason = (
            "source creation authorization gate is not ready for terminal compression"
        )
    else:
        status = (
            "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_AUTHORIZATION_CHAIN_COMPRESSION_AUDIT_HELD_FOR_OPERATOR"
        )
        source_readiness = "SOURCE_CREATION_AUTHORIZATION_GATE_READY"
        compression_recommendation = (
            "COMPRESS_TO_TERMINAL_OPERATOR_DECISION_RECORD_CREATION_HOLD"
        )
        findings = [
            {
                "finding_id": "source_creation_authorization_gate_held",
                "finding_status": "OBSERVED",
                "authority_granted": False,
            },
            {
                "finding_id": "recursive_creation_authorization_chain_detected",
                "finding_status": "OBSERVED",
                "authority_granted": False,
            },
            {
                "finding_id": "terminal_operator_creation_decision_required",
                "finding_status": "HELD_FOR_OPERATOR",
                "authority_granted": False,
            },
            {
                "finding_id": "decision_record_creation_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
        ]
        terminal_hold_reason = (
            "the v2 hygiene Phase 1 stabilization decision-record creation branch "
            "has reached an operator-held authorization gate; further recursive "
            "repo-side creation planning is compressed to a terminal hold until "
            "explicit external operator creation approval is supplied"
        )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "audit_id": AUDIT_ID,
        "status": status,
        "source_authorization_gate_path": str(SOURCE_AUTHORIZATION_GATE_JSON_PATH),
        "source_authorization_gate_observed": observed,
        "source_authorization_gate_file_hash": _sha256(source_path),
        "source_authorization_gate_packet_hash": str(
            source.get("gate_hash", NOT_COMPUTABLE)
        ),
        "source_authorization_gate_status": str(source.get("status", NOT_COMPUTABLE)),
        "source_authorization_gate_ready": ready,
        "source_readiness": source_readiness,
        "compression_audit_only": True,
        "recursive_creation_authorization_chain_compressed": ready,
        "compression_recommendation": compression_recommendation,
        "terminal_hold_reason": terminal_hold_reason,
        "review_findings": findings,
        "selected_operator_decision": "HOLD_FOR_OPERATOR_DECISION_RECORD_CREATION"
        if ready
        else NOT_COMPUTABLE,
        "selected_follow_on_action": "MAINTAIN_STABILIZATION_DECISION_RECORD_CREATION_HOLD"
        if ready
        else NOT_COMPUTABLE,
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_state": "hold",
        "recommended_next_action": (
            "collect explicit external operator decision-record creation approval; "
            "do not add recursive creation planning, evidence, authorization, or "
            "review lanes"
            if ready
            else "repair source creation authorization gate before compression"
        ),
        "operator_review_required": True,
        "operator_input_required": True,
        "operator_attestations_present": False,
        "operator_decision_attested": False,
        "operator_attestation_created": False,
        "evidence_bundle_created": False,
        "operator_evidence_bundle_created": False,
        "decision_record_created": False,
        "decision_record_creation_authorized": False,
        "authorization_record_created": False,
        "authorization_record_creation_authorized": False,
        "implementation_authorized": False,
        "hygiene_code_creation_authorized": False,
        "schema_file_creation_authorized": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "strict_mode_enablement_authorized": False,
        "projection_surface_mutation_authorized": False,
        "schema_mutation_authorized": False,
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_decision_record_creation": False,
        "valid_for_decision_record": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "authority_locks": _authority_locks(),
        "downstream": NOT_COMPUTABLE,
        "audit_hash": "",
    }
    packet["audit_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "audit_hash"}
    )
    return packet


def render_v2_hygiene_phase1_stabilization_decision_record_creation_authorization_chain_compression_audit_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Creation Authorization Chain Compression Audit",
        "",
        f"- audit_id: {packet['audit_id']}",
        f"- status: {packet['status']}",
        f"- source_authorization_gate_ready: {packet['source_authorization_gate_ready']}",
        f"- compression_recommendation: {packet['compression_recommendation']}",
        f"- recursive_creation_authorization_chain_compressed: {packet['recursive_creation_authorization_chain_compressed']}",
        f"- selected_operator_decision: {packet['selected_operator_decision']}",
        f"- selected_follow_on_action: {packet['selected_follow_on_action']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- valid_for_decision_record_creation: {packet['valid_for_decision_record_creation']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Terminal Hold Reason",
        "",
        str(packet["terminal_hold_reason"]),
        "",
        "## Review Findings",
    ]
    for finding in packet["review_findings"]:
        lines.append(
            f"- {finding['finding_id']}: {finding['finding_status']} "
            f"(authority_granted={finding['authority_granted']})"
        )
    return lines


def write_v2_hygiene_phase1_stabilization_decision_record_creation_authorization_chain_compression_audit(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_creation_authorization_chain_compression_audit(
        repo_root
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / AUDIT_JSON_PATH, packet)
    md_path = root / AUDIT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_stabilization_decision_record_creation_authorization_chain_compression_audit_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
