from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.operator_review_terminal_hold_consolidation_receipt import (
    OUT_JSON as TERMINAL_HOLD_CONSOLIDATION_JSON_PATH,
)
from core.sync.v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run import (
    DRY_RUN_JSON_PATH as SOURCE_DRY_RUN_JSON_PATH,
)
from core.sync.v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_review import (
    REVIEW_JSON_PATH as SOURCE_DRY_RUN_REVIEW_JSON_PATH,
)
from core.sync.v2_hygiene_phase1_stabilization_review_chain_compression_audit import (
    AUDIT_JSON_PATH as SOURCE_COMPRESSION_AUDIT_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygienePhase1StabilizationOperatorAttestationIntakeGate.v1"
GATE_ID = "v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_001"
GATE_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_001.latest.json"
)
GATE_MD_PATH = GATE_JSON_PATH.with_suffix(".md")
DEFAULT_ATTESTATION_PAYLOAD_PATH = Path(
    "operator_input/"
    "v2_hygiene_phase1_stabilization_operator_attestation_payload_001.json"
)
READY_STATUS = "ATTESTATION_INTAKE_VALIDATED_FOR_FUTURE_DECISION_RECORD_GATE"
BLOCKED_STATUS = "V2_HYGIENE_PHASE1_STABILIZATION_OPERATOR_ATTESTATION_INTAKE_GATE_BLOCKED"

REQUIRED_GROUPS: tuple[str, ...] = (
    "operator_identity",
    "strategy_scope_acknowledgement",
    "stabilization_disposition",
    "authority_boundary_acknowledgement",
    "terminal_output_controls",
)

REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "operator_identity": (
        "operator_id",
        "operator_reviewed_at_source_observed",
        "operator_attestation_hash",
    ),
    "strategy_scope_acknowledgement": (
        "source_strategy_plan_path",
        "source_strategy_plan_hash",
        "selected_strategy_id",
        "cycle_audit_scope_acknowledged",
    ),
    "stabilization_disposition": (
        "approved_strategy_id",
        "terminal_snapshot_allowed",
        "bulk_scan_exclusion_allowed",
        "two_phase_manifest_allowed",
        "naive_regeneration_allowed",
    ),
    "authority_boundary_acknowledgement": (
        "no_decision_record_auto_creation",
        "no_hygiene_implementation_authority",
        "no_execution_authority",
        "no_runtime_mutation",
        "no_notion_writeback",
    ),
    "terminal_output_controls": (
        "downstream_lane_disposition",
        "future_dry_run_allowed",
        "future_record_creation_gate_required",
        "rollback_or_supersession_policy",
    ),
}

TRUE_FIELDS = {
    "cycle_audit_scope_acknowledged",
    "terminal_snapshot_allowed",
    "bulk_scan_exclusion_allowed",
    "no_decision_record_auto_creation",
    "no_hygiene_implementation_authority",
    "no_execution_authority",
    "no_runtime_mutation",
    "no_notion_writeback",
    "future_record_creation_gate_required",
}
FALSE_FIELDS = {
    "two_phase_manifest_allowed",
    "naive_regeneration_allowed",
    "future_dry_run_allowed",
}
EXPECTED_LITERAL_FIELDS = {
    "selected_strategy_id": "terminal_snapshot_strategy",
    "approved_strategy_id": "terminal_snapshot_strategy",
    "source_strategy_plan_path": (
        "out/operator_review/"
        "v2_hygiene_phase1_operator_review_stabilization_strategy_plan_001.latest.json"
    ),
    "downstream_lane_disposition": "NOT_COMPUTABLE_UNTIL_GOVERNED_DECISION_RECORD_INTAKE",
    "rollback_or_supersession_policy": "fresh governed operator decision required",
}
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


def _source_readiness(
    dry_run: Mapping[str, Any],
    review: Mapping[str, Any],
    compression: Mapping[str, Any],
    consolidation: Mapping[str, Any],
) -> tuple[bool, list[str]]:
    blockers: list[str] = []
    if dry_run.get("status") != (
        "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_DRY_RUN_READY"
    ):
        blockers.append("source_stabilization_dry_run_not_ready")
    if dry_run.get("operator_attestations_present") is not False:
        blockers.append("source_stabilization_dry_run_attestation_state_not_false")
    if dry_run.get("valid_for_decision_record") is not False:
        blockers.append("source_stabilization_dry_run_decision_record_validity_not_false")
    if review.get("status") != (
        "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_DRY_RUN_REVIEW_HELD_FOR_OPERATOR"
    ):
        blockers.append("source_stabilization_dry_run_review_not_held")
    if compression.get("status") != (
        "V2_HYGIENE_PHASE1_STABILIZATION_REVIEW_CHAIN_COMPRESSION_AUDIT_HELD_FOR_OPERATOR"
    ):
        blockers.append("source_stabilization_compression_not_held")
    if consolidation.get("receipt_status") != (
        "OPERATOR_REVIEW_TERMINAL_HOLD_CONSOLIDATION_RECEIPT_READY"
    ):
        blockers.append("source_terminal_hold_consolidation_not_ready")
    for source_id, packet in (
        ("dry_run", dry_run),
        ("dry_run_review", review),
        ("compression_audit", compression),
        ("terminal_hold_consolidation", consolidation),
    ):
        if packet.get("recommended_next_lane") != NOT_COMPUTABLE:
            blockers.append(f"{source_id}_recommended_next_lane_not_not_computable")
        if packet.get("safe_to_auto_continue") is not False:
            blockers.append(f"{source_id}_safe_to_auto_continue_not_false")
        if packet.get("valid_for_execution") is not False:
            blockers.append(f"{source_id}_valid_for_execution_not_false")
        if not _locks_all_false(packet.get("authority_locks")):
            blockers.append(f"{source_id}_authority_locks_not_all_false")
    return not blockers, sorted(blockers)


def _missing_group_blockers(payload: Mapping[str, Any]) -> list[str]:
    return [
        f"{group_id}_missing"
        for group_id in REQUIRED_GROUPS
        if not isinstance(payload.get(group_id), Mapping)
    ]


def _field_blockers(
    group_id: str,
    group: Mapping[str, Any],
    *,
    expected_source_plan_hash: str,
) -> list[str]:
    blockers: list[str] = []
    for field in REQUIRED_FIELDS[group_id]:
        if field not in group:
            blockers.append(f"{group_id}.{field}_missing")
            continue
        value = group[field]
        if field in TRUE_FIELDS and value is not True:
            blockers.append(f"{group_id}.{field}_must_be_true")
        if field in FALSE_FIELDS and value is not False:
            blockers.append(f"{group_id}.{field}_must_be_false")
        if field in EXPECTED_LITERAL_FIELDS and value != EXPECTED_LITERAL_FIELDS[field]:
            blockers.append(f"{group_id}.{field}_unexpected_value")
        if field == "source_strategy_plan_hash" and value != expected_source_plan_hash:
            blockers.append(f"{group_id}.source_strategy_plan_hash_mismatch")
        if field in {
            "operator_id",
            "operator_reviewed_at_source_observed",
            "operator_attestation_hash",
        } and not (isinstance(value, str) and value.strip()):
            blockers.append(f"{group_id}.{field}_blank")
    return blockers


def _authority_expansion_blockers(payload: Mapping[str, Any]) -> list[str]:
    blockers = [
        f"payload_authority_expanding_field:{field}"
        for field in AUTHORITY_EXPANDING_FIELDS
        if payload.get(field) is True
    ]
    locks = payload.get("authority_locks")
    if isinstance(locks, Mapping):
        blockers.extend(
            f"payload_authority_lock_true:{field}"
            for field, value in sorted(locks.items())
            if value is True
        )
    return blockers


def _attestation_group_records(
    payload: Mapping[str, Any],
    *,
    expected_source_plan_hash: str,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    records: list[dict[str, Any]] = []
    missing_group_blockers = _missing_group_blockers(payload)
    field_blockers: list[str] = []
    for group_id in REQUIRED_GROUPS:
        group = payload.get(group_id)
        observed = isinstance(group, Mapping)
        blockers = (
            _field_blockers(
                group_id,
                group,
                expected_source_plan_hash=expected_source_plan_hash,
            )
            if observed
            else [f"{group_id}_missing"]
        )
        field_blockers.extend(blockers if observed else [])
        records.append(
            {
                "group_id": group_id,
                "group_observed": observed,
                "required_fields": list(REQUIRED_FIELDS[group_id]),
                "field_count": len(REQUIRED_FIELDS[group_id]),
                "field_blockers": blockers,
                "group_validated": observed and not blockers,
                "authority_granted": False,
            }
        )
    return records, missing_group_blockers, sorted(field_blockers)


def build_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate(
    repo_root: str | Path = ".",
    *,
    attestation_payload_path: str | Path = DEFAULT_ATTESTATION_PAYLOAD_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    payload_rel = Path(attestation_payload_path)
    dry_run = _read_json(root / SOURCE_DRY_RUN_JSON_PATH)
    review = _read_json(root / SOURCE_DRY_RUN_REVIEW_JSON_PATH)
    compression = _read_json(root / SOURCE_COMPRESSION_AUDIT_JSON_PATH)
    consolidation = _read_json(root / TERMINAL_HOLD_CONSOLIDATION_JSON_PATH)
    payload = _read_json(root / payload_rel)

    sources_observed = all(
        source is not None for source in (dry_run, review, compression, consolidation)
    )
    dry_run = dry_run or {}
    review = review or {}
    compression = compression or {}
    consolidation = consolidation or {}
    payload_observed = payload is not None
    payload = payload or {}

    source_ready, source_blockers = _source_readiness(
        dry_run, review, compression, consolidation
    )
    if not sources_observed:
        source_blockers = sorted(
            set(source_blockers + ["one_or_more_required_source_artifacts_missing"])
        )
    expected_source_plan_hash = str(dry_run.get("source_plan_hash", NOT_COMPUTABLE))
    group_records, missing_group_blockers, field_blockers = _attestation_group_records(
        payload,
        expected_source_plan_hash=expected_source_plan_hash,
    )
    authority_blockers = _authority_expansion_blockers(payload)
    blockers = sorted(
        set(
            source_blockers
            + ([] if payload_observed else ["operator_attestation_payload_missing"])
            + missing_group_blockers
            + field_blockers
            + authority_blockers
        )
    )
    payload_complete = payload_observed and all(
        record["group_validated"] is True for record in group_records
    )
    validated = source_ready and payload_complete and not authority_blockers
    status = READY_STATUS if validated else (NOT_COMPUTABLE if not payload_observed else BLOCKED_STATUS)
    source_readiness = (
        "SOURCE_ARTIFACTS_READY"
        if source_ready
        else "SOURCE_ARTIFACTS_NOT_READY"
    )
    payload_readiness = (
        "OPERATOR_ATTESTATION_PAYLOAD_VALIDATED"
        if validated
        else (
            "OPERATOR_ATTESTATION_PAYLOAD_MISSING"
            if not payload_observed
            else "OPERATOR_ATTESTATION_PAYLOAD_NOT_VALIDATED"
        )
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "status": status,
        "source_stabilization_dry_run_path": str(SOURCE_DRY_RUN_JSON_PATH),
        "source_stabilization_dry_run_hash": str(
            dry_run.get("dry_run_hash", NOT_COMPUTABLE)
        ),
        "source_stabilization_dry_run_review_path": str(SOURCE_DRY_RUN_REVIEW_JSON_PATH),
        "source_stabilization_dry_run_review_hash": str(
            review.get("review_hash", NOT_COMPUTABLE)
        ),
        "source_stabilization_compression_audit_path": str(
            SOURCE_COMPRESSION_AUDIT_JSON_PATH
        ),
        "source_stabilization_compression_audit_hash": str(
            compression.get("audit_hash", NOT_COMPUTABLE)
        ),
        "source_terminal_hold_consolidation_path": str(
            TERMINAL_HOLD_CONSOLIDATION_JSON_PATH
        ),
        "source_terminal_hold_consolidation_hash": str(
            consolidation.get("receipt_hash", NOT_COMPUTABLE)
        ),
        "sources_observed": sources_observed,
        "source_readiness": source_readiness,
        "source_blockers": source_blockers,
        "attestation_payload_path": payload_rel.as_posix(),
        "attestation_payload_observed": payload_observed,
        "attestation_payload_file_hash": _sha256(root / payload_rel),
        "attestation_payload_packet_hash": canonical_hash(payload)
        if payload_observed
        else NOT_COMPUTABLE,
        "payload_readiness": payload_readiness,
        "required_attestation_groups": list(REQUIRED_GROUPS),
        "attestation_group_records": group_records,
        "missing_group_blockers": missing_group_blockers,
        "field_blockers": field_blockers,
        "authority_expansion_blockers": authority_blockers,
        "validation_blockers": blockers,
        "attested_group_count": sum(
            1 for record in group_records if record["group_validated"] is True
        ),
        "required_group_count": len(REQUIRED_GROUPS),
        "intake_validated_for_future_decision_record_gate": validated,
        "future_decision_record_gate_required": True,
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
        "valid_for_decision_record": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_action": (
            "use validated operator attestation intake only as a prerequisite for a "
            "separate governed decision-record gate; do not create records, "
            "evidence bundles, implementation lanes, writeback, mutation, "
            "activation, promotion, registration, or execution authority"
            if validated
            else "collect complete conservative external operator attestations before "
            "any future governed decision-record gate"
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


def render_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Phase 1 Stabilization Operator Attestation Intake Gate",
        "",
        f"- gate_id: {packet['gate_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- payload_readiness: {packet['payload_readiness']}",
        f"- attestation_payload_observed: {packet['attestation_payload_observed']}",
        f"- attested_group_count: {packet['attested_group_count']}",
        f"- required_group_count: {packet['required_group_count']}",
        f"- intake_validated_for_future_decision_record_gate: {packet['intake_validated_for_future_decision_record_gate']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Attestation Groups",
    ]
    for record in packet["attestation_group_records"]:
        lines.append(
            "- "
            f"{record['group_id']}: observed={record['group_observed']}, "
            f"validated={record['group_validated']}, "
            f"blockers={len(record['field_blockers'])}"
        )
    lines.extend(["", "## Validation Blockers"])
    if packet["validation_blockers"]:
        for blocker in packet["validation_blockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
    attestation_payload_path: str | Path = DEFAULT_ATTESTATION_PAYLOAD_PATH,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate(
        repo_root,
        attestation_payload_path=attestation_payload_path,
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / GATE_JSON_PATH, packet)
    md_path = root / GATE_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
