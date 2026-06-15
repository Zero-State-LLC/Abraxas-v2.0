from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "V2HygienePhase1OperatorReviewDependencyCycleAudit.v1"
AUDIT_ID = "v2_hygiene_phase1_operator_review_dependency_cycle_audit_001"
AUDIT_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase1_operator_review_dependency_cycle_audit_001.latest.json"
)
AUDIT_MD_PATH = AUDIT_JSON_PATH.with_suffix(".md")
NOT_COMPUTABLE = "NOT_COMPUTABLE"

BULK_DISPOSITION_PATH = (
    "out/operator_review/operator_review_required_items_bulk_disposition_001.latest.json"
)
PHASE1_RECONCILIATION_PATH = (
    "out/operator_review/v2_hygiene_phase1_bulk_approval_reconciliation_001.latest.json"
)
PHASE1_COMPRESSION_AUDIT_PATH = (
    "out/operator_review/v2_hygiene_phase1_authorization_chain_compression_audit_001.latest.json"
)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _find_surface_hash(packet: Mapping[str, Any], path: str) -> str:
    dispositions = packet.get("surface_dispositions")
    if not isinstance(dispositions, list):
        return NOT_COMPUTABLE
    for item in dispositions:
        if isinstance(item, Mapping) and item.get("path") == path:
            return str(item.get("source_hash", NOT_COMPUTABLE))
    return NOT_COMPUTABLE


def _find_source_record_hash(packet: Mapping[str, Any], path: str) -> str:
    records = packet.get("source_records")
    if not isinstance(records, list):
        return NOT_COMPUTABLE
    for item in records:
        if isinstance(item, Mapping) and item.get("path") == path:
            return str(item.get("source_hash", NOT_COMPUTABLE))
    return NOT_COMPUTABLE


def _source_status(packet: Mapping[str, Any]) -> str:
    for field in (
        "disposition_status",
        "reconciliation_status",
        "status",
        "audit_status",
    ):
        value = packet.get(field)
        if isinstance(value, str) and value:
            return value
    return NOT_COMPUTABLE


def _authority_locks() -> dict[str, bool]:
    return {
        "activation": False,
        "auto_approval": False,
        "auto_continuation": False,
        "canon_mutation": False,
        "code_creation": False,
        "evidence_bundle_creation": False,
        "execution_authority": False,
        "github_writeback": False,
        "hygiene_code_creation": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_authorization_record_creation": False,
        "operator_evidence_bundle_creation": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_file_creation": False,
        "schema_mutation": False,
        "strict_mode_enablement": False,
        "v2_module_registration": False,
    }


def _source_record(path: str, packet: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "path": path,
        "source_observed": bool(packet),
        "observed_status": _source_status(packet),
        "current_hash": canonical_hash(packet) if packet else NOT_COMPUTABLE,
        "valid_for_execution": bool(packet.get("valid_for_execution", False)),
        "implementation_authorized": bool(
            packet.get("implementation_authorized", False)
        ),
    }


def build_v2_hygiene_phase1_operator_review_dependency_cycle_audit(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    bulk = _read_json(root / BULK_DISPOSITION_PATH)
    reconciliation = _read_json(root / PHASE1_RECONCILIATION_PATH)
    compression = _read_json(root / PHASE1_COMPRESSION_AUDIT_PATH)

    reconciliation_current_hash = canonical_hash(reconciliation) if reconciliation else NOT_COMPUTABLE
    compression_current_hash = canonical_hash(compression) if compression else NOT_COMPUTABLE
    bulk_current_hash = canonical_hash(bulk) if bulk else NOT_COMPUTABLE

    bulk_recorded_reconciliation_hash = _find_surface_hash(
        bulk,
        PHASE1_RECONCILIATION_PATH,
    )
    bulk_recorded_compression_hash = _find_surface_hash(
        bulk,
        PHASE1_COMPRESSION_AUDIT_PATH,
    )
    reconciliation_recorded_bulk_hash = _find_source_record_hash(
        reconciliation,
        BULK_DISPOSITION_PATH,
    )

    bulk_reconciliation_hash_current = (
        bulk_recorded_reconciliation_hash == reconciliation_current_hash
    )
    bulk_compression_hash_current = (
        bulk_recorded_compression_hash == compression_current_hash
    )
    reconciliation_bulk_hash_current = (
        reconciliation_recorded_bulk_hash == bulk_current_hash
    )

    cycle_observed = (
        bool(bulk)
        and bool(reconciliation)
        and bool(compression)
        and not bulk_reconciliation_hash_current
        and reconciliation_bulk_hash_current
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "audit_id": AUDIT_ID,
        "audit_status": (
            "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_DEPENDENCY_CYCLE_AUDIT_HELD_FOR_OPERATOR"
            if cycle_observed
            else "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_DEPENDENCY_CYCLE_AUDIT_BLOCKED"
        ),
        "source_records": [
            _source_record(BULK_DISPOSITION_PATH, bulk),
            _source_record(PHASE1_RECONCILIATION_PATH, reconciliation),
            _source_record(PHASE1_COMPRESSION_AUDIT_PATH, compression),
        ],
        "cycle_observed": cycle_observed,
        "cycle_edges": [
            {
                "edge_id": "bulk_disposition_scans_phase1_reconciliation",
                "from_path": BULK_DISPOSITION_PATH,
                "to_path": PHASE1_RECONCILIATION_PATH,
                "recorded_hash": bulk_recorded_reconciliation_hash,
                "current_hash": reconciliation_current_hash,
                "hash_current": bulk_reconciliation_hash_current,
            },
            {
                "edge_id": "bulk_disposition_scans_phase1_compression_audit",
                "from_path": BULK_DISPOSITION_PATH,
                "to_path": PHASE1_COMPRESSION_AUDIT_PATH,
                "recorded_hash": bulk_recorded_compression_hash,
                "current_hash": compression_current_hash,
                "hash_current": bulk_compression_hash_current,
            },
            {
                "edge_id": "phase1_reconciliation_consumes_bulk_disposition",
                "from_path": PHASE1_RECONCILIATION_PATH,
                "to_path": BULK_DISPOSITION_PATH,
                "recorded_hash": reconciliation_recorded_bulk_hash,
                "current_hash": bulk_current_hash,
                "hash_current": reconciliation_bulk_hash_current,
            },
        ],
        "stabilization_decision": "HOLD_FOR_OPERATOR_STABILIZATION_STRATEGY",
        "naive_regeneration_safe": False,
        "recommended_next_action": (
            "do not continue alternating bulk-disposition and Phase 1 chain "
            "regeneration; choose an explicit operator-reviewed stabilization "
            "strategy, such as excluding the bulk disposition from its own "
            "downstream closure set or emitting a separate terminal snapshot"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "audit_findings": [
            {
                "finding_id": "operator_review_dependency_cycle_observed",
                "finding_status": "PASS" if cycle_observed else "FAIL_CLOSED",
                "authority_granted": False,
            },
            {
                "finding_id": "bulk_disposition_phase1_hashes_stale",
                "finding_status": "OBSERVED"
                if not bulk_reconciliation_hash_current
                else "NOT_OBSERVED",
                "authority_granted": False,
            },
            {
                "finding_id": "phase1_reconciliation_bulk_hash_current",
                "finding_status": "OBSERVED"
                if reconciliation_bulk_hash_current
                else "NOT_OBSERVED",
                "authority_granted": False,
            },
            {
                "finding_id": "implementation_and_execution_remain_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
        ],
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authorization_granted": False,
        "authorization_record_created": False,
        "operator_attestation_created": False,
        "operator_evidence_bundle_created": False,
        "implementation_authorized": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_prepare_patch": False,
        "safe_to_auto_continue": False,
        "hygiene_code_creation_authorized": False,
        "schema_file_creation_authorized": False,
        "rune_registration_authorized": False,
        "v2_module_registration_authorized": False,
        "strict_mode_enablement_authorized": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "canon_mutation": False,
        "schema_mutation": False,
        "authority_locks": _authority_locks(),
        "downstream": NOT_COMPUTABLE,
    }
    return {**packet, "audit_hash": canonical_hash(packet)}


def render_v2_hygiene_phase1_operator_review_dependency_cycle_audit_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Phase 1 Operator Review Dependency Cycle Audit",
        "",
        f"- audit_id: {packet['audit_id']}",
        f"- audit_status: {packet['audit_status']}",
        f"- cycle_observed: {packet['cycle_observed']}",
        f"- naive_regeneration_safe: {packet['naive_regeneration_safe']}",
        f"- stabilization_decision: {packet['stabilization_decision']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Cycle Edges",
    ]
    for edge in packet.get("cycle_edges", []):
        if isinstance(edge, Mapping):
            lines.append(
                "- "
                f"{edge['edge_id']}: hash_current={edge['hash_current']}"
            )
    lines.extend(["", "## Findings"])
    for finding in packet.get("audit_findings", []):
        if isinstance(finding, Mapping):
            lines.append(
                f"- {finding['finding_id']}: {finding['finding_status']} "
                f"(authority_granted={finding['authority_granted']})"
            )
    return lines


def write_v2_hygiene_phase1_operator_review_dependency_cycle_audit(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_operator_review_dependency_cycle_audit(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / AUDIT_JSON_PATH, packet)
    md_path = root / AUDIT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_operator_review_dependency_cycle_audit_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
