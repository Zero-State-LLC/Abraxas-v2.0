from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.grok_abx_runes_operator_decision_evidence_collection_dry_run import (
    DRY_RUN_JSON_PATH as SOURCE_DRY_RUN_JSON_PATH,
)

SCHEMA_VERSION = "GrokAbxRunesOperatorReviewChainCompressionReceipt.v1"
RECEIPT_ID = "grok_abx_runes_operator_review_chain_compression_receipt_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/grok_abx_runes_operator_review_chain_compression_receipt_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = (
    "GROK_ABX_RUNES_OPERATOR_DECISION_EVIDENCE_COLLECTION_DRY_RUN_READY"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


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
    summary = source.get("readiness_summary")
    return (
        source.get("schema_version")
        == "GrokAbxRunesOperatorDecisionEvidenceCollectionDryRun.v1"
        and source.get("status") == EXPECTED_SOURCE_STATUS
        and source.get("source_evidence_collection_plan_ready") is True
        and source.get("simulated_only") is True
        and source.get("operator_input_required") is True
        and source.get("operator_attestations_present") is False
        and source.get("operator_evidence_collected") is False
        and source.get("evidence_bundle_created") is False
        and source.get("decision_record_created") is False
        and source.get("authorization_record_created") is False
        and source.get("external_backlog_accepted") is False
        and source.get("separate_registration_planning_authorized") is False
        and source.get("catalog_mutation_authorized") is False
        and source.get("rune_registration_authorized") is False
        and source.get("yggdrasil_binding_mutation_authorized") is False
        and source.get("recommended_next_lane") == NOT_COMPUTABLE
        and source.get("safe_to_auto_continue") is False
        and source.get("valid_for_decision_record") is False
        and source.get("valid_for_execution") is False
        and source.get("valid_for_implementation") is False
        and bool(_string_list(source.get("evaluation_blockers")))
        and isinstance(summary, Mapping)
        and summary.get("groups_ready") == 0
        and summary.get("groups_total") == 5
        and summary.get("required_field_count") == 29
        and summary.get("evidence_bundle_complete") is False
        and _locks_all_false(source.get("authority_locks"))
    )


def _authority_locks() -> dict[str, bool]:
    return {
        "authorization_record_creation": False,
        "auto_approval": False,
        "auto_continuation": False,
        "backlog_acceptance": False,
        "canon_mutation": False,
        "catalog_mutation": False,
        "decision_record_creation": False,
        "evidence_bundle_creation": False,
        "execution_authority": False,
        "github_writeback": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_evidence_collection": False,
        "pr_merge_authority": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "yggdrasil_binding_mutation": False,
    }


def build_grok_abx_runes_operator_review_chain_compression_receipt(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / SOURCE_DRY_RUN_JSON_PATH
    source = _read_json(source_path)
    source_observed = source is not None
    source = source or {}
    source_ready = source_observed and _source_ready(source)
    source_blockers = _string_list(source.get("evaluation_blockers"))

    if not source_observed:
        status = NOT_COMPUTABLE
        source_readiness = "SOURCE_DRY_RUN_MISSING"
        compression_recommendation = "REPAIR_SOURCE_DRY_RUN_BEFORE_COMPRESSION"
        terminal_hold_reason = "source Grok ABX-Runes evidence dry run is missing"
        findings = [
            {
                "finding_id": "source_dry_run_missing",
                "finding_status": NOT_COMPUTABLE,
                "authority_granted": False,
            }
        ]
    elif not source_ready:
        status = "GROK_ABX_RUNES_OPERATOR_REVIEW_CHAIN_COMPRESSION_RECEIPT_BLOCKED"
        source_readiness = "SOURCE_DRY_RUN_NOT_READY"
        compression_recommendation = "REPAIR_SOURCE_DRY_RUN_BEFORE_COMPRESSION"
        terminal_hold_reason = (
            "source Grok ABX-Runes evidence dry run is not ready for terminal "
            "compression"
        )
        findings = [
            {
                "finding_id": "source_dry_run_not_ready",
                "finding_status": "BLOCKED",
                "authority_granted": False,
            }
        ]
    else:
        status = "GROK_ABX_RUNES_OPERATOR_REVIEW_CHAIN_COMPRESSED_TO_TERMINAL_HOLD"
        source_readiness = "SOURCE_DRY_RUN_READY"
        compression_recommendation = "COMPRESS_TO_TERMINAL_EXTERNAL_OPERATOR_HOLD"
        terminal_hold_reason = (
            "Grok ABX-Runes has enough repo-visible advisory evidence to stop "
            "recursive planning: the external work claims are reconciled, the "
            "decision-record shape is simulated and reviewed, and the evidence "
            "bundle dry run shows all 29 operator fields still pending. No further "
            "Grok ABX-Runes repo lane is computable until explicit external operator "
            "attestations are provided."
        )
        findings = [
            {
                "finding_id": "external_grok_claims_reconciled_as_non_authoritative",
                "finding_status": "OBSERVED",
                "authority_granted": False,
            },
            {
                "finding_id": "simulated_decision_record_review_held",
                "finding_status": "OBSERVED",
                "authority_granted": False,
            },
            {
                "finding_id": "simulated_evidence_bundle_missing_all_operator_fields",
                "finding_status": "HELD_FOR_OPERATOR",
                "authority_granted": False,
            },
            {
                "finding_id": "recursive_operator_review_chain_compressed",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
            {
                "finding_id": "auto_continuation_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
            {
                "finding_id": "registration_mutation_and_execution_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
        ]

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": status,
        "source_dry_run_path": SOURCE_DRY_RUN_JSON_PATH.as_posix(),
        "source_dry_run_observed": source_observed,
        "source_dry_run_file_hash": _sha256(source_path),
        "source_dry_run_packet_hash": str(source.get("dry_run_hash", NOT_COMPUTABLE)),
        "source_dry_run_status": str(source.get("status", NOT_COMPUTABLE)),
        "source_dry_run_ready": source_ready,
        "source_readiness": source_readiness,
        "source_evaluation_blockers": source_blockers,
        "source_required_field_count": int(
            source.get("readiness_summary", {}).get("required_field_count", 0)
            if isinstance(source.get("readiness_summary"), Mapping)
            else 0
        ),
        "compression_receipt_only": True,
        "recursive_review_chain_compressed": source_ready,
        "compression_recommendation": compression_recommendation,
        "terminal_hold_reason": terminal_hold_reason,
        "review_findings": findings,
        "selected_operator_decision": "HOLD_FOR_EXTERNAL_OPERATOR_ATTESTATIONS"
        if source_ready
        else NOT_COMPUTABLE,
        "selected_follow_on_action": "STOP_GROK_ABX_RUNES_RECURSIVE_REPO_LANES"
        if source_ready
        else NOT_COMPUTABLE,
        "resume_condition": (
            "explicit external operator attestations for the 29 planned fields"
            if source_ready
            else "source dry run repaired and ready"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_action": (
            "package the Grok ABX-Runes advisory stack; do not add more recursive "
            "repo-side Grok lanes until external operator attestations are supplied"
            if source_ready
            else "repair the source Grok ABX-Runes evidence dry run before compression"
        ),
        "operator_review_required": True,
        "operator_input_required": True,
        "operator_attestations_present": False,
        "operator_evidence_collected": False,
        "operator_attestation_created": False,
        "evidence_bundle_created": False,
        "decision_record_created": False,
        "authorization_record_created": False,
        "external_backlog_accepted": False,
        "separate_registration_planning_authorized": False,
        "catalog_mutation_authorized": False,
        "rune_registration_authorized": False,
        "yggdrasil_binding_mutation_authorized": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "pr_merge_authority": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "canon_mutation": False,
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authorization_granted": False,
        "implementation_authorized": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "valid_for_decision_record": False,
        "authority_locks": _authority_locks(),
        "downstream": NOT_COMPUTABLE,
        "receipt_hash": "",
    }
    packet["receipt_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "receipt_hash"}
    )
    return packet


def render_grok_abx_runes_operator_review_chain_compression_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Grok ABX-Runes Operator Review Chain Compression Receipt",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- status: {packet['status']}",
        f"- source_dry_run_ready: {packet['source_dry_run_ready']}",
        f"- compression_recommendation: {packet['compression_recommendation']}",
        f"- recursive_review_chain_compressed: {packet['recursive_review_chain_compressed']}",
        f"- selected_operator_decision: {packet['selected_operator_decision']}",
        f"- selected_follow_on_action: {packet['selected_follow_on_action']}",
        f"- resume_condition: {packet['resume_condition']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
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
    lines.extend(["", "## Source Evaluation Blockers"])
    if packet["source_evaluation_blockers"]:
        for blocker in packet["source_evaluation_blockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- none")
    return lines


def write_grok_abx_runes_operator_review_chain_compression_receipt(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_grok_abx_runes_operator_review_chain_compression_receipt(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_grok_abx_runes_operator_review_chain_compression_receipt_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
