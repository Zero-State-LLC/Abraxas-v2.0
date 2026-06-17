from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_review import (
    REVIEW_JSON_PATH as SOURCE_REVIEW_JSON_PATH,
)

SCHEMA_VERSION = "V2HygienePhase1StabilizationReviewChainCompressionAudit.v1"
AUDIT_ID = "v2_hygiene_phase1_stabilization_review_chain_compression_audit_001"
AUDIT_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_review_chain_compression_audit_001.latest.json"
)
AUDIT_MD_PATH = AUDIT_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = (
    "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_"
    "DRY_RUN_REVIEW_HELD_FOR_OPERATOR"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"


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


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _locks_all_false(value: Any) -> bool:
    return isinstance(value, Mapping) and bool(value) and all(
        item is False for item in value.values()
    )


def _source_ready(source: Mapping[str, Any]) -> bool:
    return (
        source.get("schema_version")
        == "V2HygienePhase1OperatorReviewStabilizationDecisionRecordDryRunReview.v1"
        and source.get("status") == EXPECTED_SOURCE_STATUS
        and source.get("source_stabilization_decision_record_dry_run_ready") is True
        and source.get("selected_operator_decision")
        == "HOLD_FOR_OPERATOR_STABILIZATION_DECISION"
        and source.get("selected_follow_on_action")
        == "MAINTAIN_V2_HYGIENE_PHASE1_STABILIZATION_HOLD"
        and source.get("operator_review_required") is True
        and source.get("operator_input_required") is True
        and source.get("operator_attestations_present") is False
        and source.get("operator_decision_attested") is False
        and source.get("operator_attestation_created") is False
        and source.get("evidence_bundle_created") is False
        and source.get("operator_evidence_bundle_created") is False
        and source.get("decision_record_created") is False
        and source.get("decision_record_creation_authorized") is False
        and source.get("authorization_record_created") is False
        and source.get("authorization_record_creation_authorized") is False
        and source.get("implementation_authorized") is False
        and source.get("hygiene_code_creation_authorized") is False
        and source.get("schema_file_creation_authorized") is False
        and source.get("v2_module_registration_authorized") is False
        and source.get("rune_registration_authorized") is False
        and source.get("strict_mode_enablement_authorized") is False
        and source.get("projection_surface_mutation_authorized") is False
        and source.get("schema_mutation_authorized") is False
        and source.get("execution_authority") is False
        and source.get("valid_for_decision_record") is False
        and source.get("valid_for_execution") is False
        and source.get("valid_for_implementation") is False
        and source.get("recommended_next_lane") == NOT_COMPUTABLE
        and source.get("recommended_next_patch") == NOT_COMPUTABLE
        and source.get("recommended_next_state") == "hold"
        and source.get("safe_to_auto_continue") is False
        and source.get("downstream") == NOT_COMPUTABLE
        and len(_string_list(source.get("source_validation_blockers"))) == 5
        and _locks_all_false(source.get("authority_locks"))
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


def build_v2_hygiene_phase1_stabilization_review_chain_compression_audit(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / SOURCE_REVIEW_JSON_PATH
    source = _read_json(source_path)
    source_observed = source is not None
    source = source or {}
    source_ready = source_observed and _source_ready(source)
    source_blockers = _string_list(source.get("source_validation_blockers"))

    if not source_observed:
        status = NOT_COMPUTABLE
        source_readiness = "SOURCE_STABILIZATION_REVIEW_MISSING"
        compression_recommendation = "REPAIR_SOURCE_REVIEW_BEFORE_COMPRESSION"
        findings = [
            {
                "finding_id": "source_stabilization_review_missing",
                "finding_status": "NOT_COMPUTABLE",
                "authority_granted": False,
            }
        ]
        terminal_hold_reason = (
            "source stabilization decision-record dry-run review artifact is "
            "missing or unreadable"
        )
    elif not source_ready:
        status = "V2_HYGIENE_PHASE1_STABILIZATION_REVIEW_CHAIN_COMPRESSION_AUDIT_BLOCKED"
        source_readiness = "SOURCE_STABILIZATION_REVIEW_NOT_READY"
        compression_recommendation = "REPAIR_SOURCE_REVIEW_BEFORE_COMPRESSION"
        findings = [
            {
                "finding_id": "source_stabilization_review_not_ready",
                "finding_status": "BLOCKED",
                "authority_granted": False,
            }
        ]
        terminal_hold_reason = (
            "source stabilization decision-record dry-run review artifact is not "
            "ready for review-chain compression"
        )
    else:
        status = (
            "V2_HYGIENE_PHASE1_STABILIZATION_REVIEW_CHAIN_COMPRESSION_AUDIT_"
            "HELD_FOR_OPERATOR"
        )
        source_readiness = "SOURCE_STABILIZATION_REVIEW_READY"
        compression_recommendation = "COMPRESS_TO_TERMINAL_OPERATOR_STABILIZATION_HOLD"
        findings = [
            {
                "finding_id": "source_stabilization_review_ready_and_held",
                "finding_status": "OBSERVED",
                "authority_granted": False,
            },
            {
                "finding_id": "recursive_review_chain_detected",
                "finding_status": "OBSERVED",
                "authority_granted": False,
            },
            {
                "finding_id": "terminal_operator_stabilization_required",
                "finding_status": "HELD_FOR_OPERATOR",
                "authority_granted": False,
            },
            {
                "finding_id": "auto_continuation_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
            {
                "finding_id": "implementation_and_execution_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
        ]
        terminal_hold_reason = (
            "v2 hygiene Phase 1 stabilization has enough repo-visible simulated "
            "review evidence to compress the recursive review chain, but it still "
            "lacks explicit external operator attestations and a governed "
            "stabilization decision record; the only valid next state is a "
            "terminal operator-stabilization hold"
        )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "audit_id": AUDIT_ID,
        "status": status,
        "source_review_path": str(SOURCE_REVIEW_JSON_PATH),
        "source_review_observed": source_observed,
        "source_review_file_hash": _sha256(source_path),
        "source_review_packet_hash": str(source.get("review_hash", NOT_COMPUTABLE)),
        "source_review_status": str(source.get("status", NOT_COMPUTABLE)),
        "source_review_ready": source_ready,
        "source_readiness": source_readiness,
        "source_validation_blockers": source_blockers,
        "compression_audit_only": True,
        "recursive_review_chain_compressed": source_ready,
        "compression_recommendation": compression_recommendation,
        "terminal_hold_reason": terminal_hold_reason,
        "review_findings": findings,
        "selected_operator_decision": "HOLD_FOR_OPERATOR_STABILIZATION_DECISION"
        if source_ready
        else NOT_COMPUTABLE,
        "selected_follow_on_action": "MAINTAIN_V2_HYGIENE_PHASE1_STABILIZATION_HOLD"
        if source_ready
        else NOT_COMPUTABLE,
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_state": "hold",
        "recommended_next_action": (
            "collect explicit external operator attestations and a governed "
            "stabilization decision record before any v2 hygiene Phase 1 "
            "stabilization or implementation lane; do not add more recursive "
            "review or evidence dry-run review lanes"
            if source_ready
            else "repair source stabilization review artifact before compression"
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


def render_v2_hygiene_phase1_stabilization_review_chain_compression_audit_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Phase 1 Stabilization Review Chain Compression Audit",
        "",
        f"- audit_id: {packet['audit_id']}",
        f"- status: {packet['status']}",
        f"- source_review_ready: {packet['source_review_ready']}",
        f"- compression_recommendation: {packet['compression_recommendation']}",
        f"- recursive_review_chain_compressed: {packet['recursive_review_chain_compressed']}",
        f"- selected_operator_decision: {packet['selected_operator_decision']}",
        f"- selected_follow_on_action: {packet['selected_follow_on_action']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- recommended_next_patch: {packet['recommended_next_patch']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- downstream: {packet['downstream']}",
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
    lines.extend(["", "## Source Validation Blockers"])
    if packet["source_validation_blockers"]:
        for blocker in packet["source_validation_blockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase1_stabilization_review_chain_compression_audit(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_stabilization_review_chain_compression_audit(
        repo_root
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / AUDIT_JSON_PATH, packet)
    md_path = root / AUDIT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_stabilization_review_chain_compression_audit_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
