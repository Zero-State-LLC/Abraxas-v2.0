from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt import (
    RECEIPT_JSON_PATH as SOURCE_DUPLICATE_REPAIR_RECEIPT_JSON_PATH,
)
from core.sync.v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate import (
    GATE_JSON_PATH as SOURCE_COMPLETION_VALIDATION_APPROVAL_GATE_JSON_PATH,
)
from core.sync.v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan import (
    PLAN_JSON_PATH as SOURCE_COMPLETION_VALIDATION_RECEIPT_PLAN_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = (
    "V2HygienePhase1StabilizationDecisionRecordCompletionValidationImplementationReceipt.v1"
)
RECEIPT_ID = (
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
    "implementation_receipt_001"
)
RECEIPT_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
    "implementation_receipt_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
READY_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "IMPLEMENTATION_RECEIPT_READY"
)
BLOCKED_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "IMPLEMENTATION_RECEIPT_BLOCKED"
)
EXPECTED_APPROVAL_GATE_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "APPROVAL_GATE_READY_FOR_SEPARATE_RECORD_COMPLETION_VALIDATION_PLANNING"
)
EXPECTED_RECEIPT_PLAN_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "RECEIPT_PLAN_READY"
)
EXPECTED_REPAIR_RECEIPT_STATUS = (
    "V2_HYGIENE_PHASE1_DUPLICATE_FRONTIER_QUARANTINE_REPAIR_EXECUTION_RECEIPT_READY"
)
NEXT_AUTHORIZATION_GATE_LANE = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "EXECUTION_AUTHORIZATION_GATE_001"
)

AUTHORITY_EXPANDING_FIELDS = (
    "decision_record_created",
    "decision_record_creation_authorized",
    "decision_record_completed",
    "decision_record_completion_authorized",
    "decision_record_completion_validation_authorized",
    "decision_record_completion_validation_performed",
    "decision_record_emitted",
    "decision_record_emission_authorized",
    "decision_record_finalized",
    "decision_record_finalization_authorized",
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
    "forecast_routing_authorized",
    "adaptive_learning_authorized",
    "valid_for_execution",
    "valid_for_decision_record_creation",
    "valid_for_decision_record_completion",
    "valid_for_decision_record_completion_validation",
    "valid_for_decision_record_emission",
    "valid_for_decision_record_finalization",
    "valid_for_decision_record_materialization",
    "safe_to_auto_continue",
)


def _resolve(root: Path, path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate


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
        "adaptive_learning": False,
        "authorization_record_creation": False,
        "auto_approval": False,
        "auto_continuation": False,
        "canon_mutation": False,
        "decision_record_completion": False,
        "decision_record_completion_validation": False,
        "decision_record_creation": False,
        "decision_record_emission": False,
        "decision_record_finalization": False,
        "evidence_bundle_creation": False,
        "execution_authority": False,
        "forecast_routing": False,
        "github_writeback": False,
        "hygiene_code_creation": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_evidence_bundle_creation": False,
        "package_lock_mutation": False,
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


def _copied_authority_locks(*sources: Mapping[str, Any]) -> dict[str, bool]:
    for source in sources:
        locks = source.get("authority_locks")
        if _locks_all_false(locks):
            return {str(key): False for key in sorted(locks)}
    return _authority_locks()


def _packet_hash(packet: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = packet.get(key)
        if isinstance(value, str) and value and value != NOT_COMPUTABLE:
            return value
    return canonical_hash(packet) if packet else NOT_COMPUTABLE


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
    *,
    expected_status: str,
    hash_keys: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": path.as_posix(),
        "observed": bool(packet),
        "file_hash": _sha256(path),
        "packet_hash": _packet_hash(packet, *hash_keys),
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": expected_status,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "recommended_next_lane": str(packet.get("recommended_next_lane", NOT_COMPUTABLE)),
        "downstream": str(packet.get("downstream", NOT_COMPUTABLE)),
        "safe_to_auto_continue": packet.get("safe_to_auto_continue"),
        "valid_for_execution": packet.get("valid_for_execution"),
        "valid_for_implementation": packet.get("valid_for_implementation"),
    }


def _frontier_duplicate_paths(root: Path, repair_receipt: Mapping[str, Any]) -> list[str]:
    deleted_paths = repair_receipt.get("deleted_paths")
    if not isinstance(deleted_paths, list):
        return []
    paths = [
        str(path)
        for path in deleted_paths
        if isinstance(path, str) and _resolve(root, path).exists()
    ]
    return sorted(paths)


def _approval_gate_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers = []
    if packet.get("status") != EXPECTED_APPROVAL_GATE_STATUS:
        blockers.append("completion_validation_approval_gate_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("completion_validation_approval_gate_source_not_ready")
    if packet.get("completion_validation_approval_gate_ready") is not True:
        blockers.append("completion_validation_approval_gate_ready_not_true")
    if packet.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append("completion_validation_approval_gate_lane_not_closed")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("completion_validation_approval_gate_downstream_not_closed")
    if not _locks_all_false(packet.get("authority_locks")):
        blockers.append("completion_validation_approval_gate_locks_not_false")
    blockers.extend(_authority_expansion_blockers("completion_validation_approval_gate", packet))
    return blockers


def _receipt_plan_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers = []
    if packet.get("status") != EXPECTED_RECEIPT_PLAN_STATUS:
        blockers.append("completion_validation_receipt_plan_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("completion_validation_receipt_plan_source_not_ready")
    if packet.get("receipt_plan_ready") is not True:
        blockers.append("completion_validation_receipt_plan_ready_not_true")
    if packet.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append("completion_validation_receipt_plan_lane_not_closed")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("completion_validation_receipt_plan_downstream_not_closed")
    if not _locks_all_false(packet.get("authority_locks")):
        blockers.append("completion_validation_receipt_plan_locks_not_false")
    contract = packet.get("planned_validation_packet_contract")
    if not isinstance(contract, Mapping):
        blockers.append("completion_validation_receipt_plan_contract_missing")
    else:
        for field in (
            "record_id",
            "record_output_path",
            "source_packet_hashes",
            "planned_validation_claims",
            "authority_denials",
        ):
            if field not in contract:
                blockers.append(f"completion_validation_receipt_plan_contract_missing:{field}")
        if contract.get("completion_validation_performed") is not False:
            blockers.append("completion_validation_receipt_plan_contract_performed_not_false")
        denials = contract.get("authority_denials")
        if not _locks_all_false(denials):
            blockers.append("completion_validation_receipt_plan_contract_denials_not_false")
    blockers.extend(_authority_expansion_blockers("completion_validation_receipt_plan", packet))
    return blockers


def _repair_receipt_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers = []
    if packet.get("status") != EXPECTED_REPAIR_RECEIPT_STATUS:
        blockers.append("duplicate_frontier_repair_receipt_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("duplicate_frontier_repair_receipt_source_not_ready")
    summary = packet.get("repair_summary")
    if not isinstance(summary, Mapping):
        blockers.append("duplicate_frontier_repair_summary_missing")
    else:
        expected = {
            "source_manifest_count": 466,
            "preflight_eligible_count": 466,
            "preflight_blocked_count": 0,
            "deleted_path_count": 466,
            "held_path_count": 0,
            "post_duplicate_remaining_count": 0,
            "canonical_counterparts_remaining_count": 466,
        }
        blockers.extend(
            f"duplicate_frontier_repair_summary_unexpected:{field}"
            for field, expected_value in expected.items()
            if summary.get(field) != expected_value
        )
    if packet.get("repair_performed") is not True:
        blockers.append("duplicate_frontier_repair_not_performed")
    if packet.get("scoped_duplicate_deletion_performed") is not True:
        blockers.append("duplicate_frontier_scoped_deletion_not_performed")
    if not _locks_all_false(packet.get("authority_locks")):
        blockers.append("duplicate_frontier_repair_locks_not_false")
    for field in (
        "subsystem_implementation_authorized",
        "completion_validation_execution_authorized",
        "decision_record_completion_authorized",
        "valid_for_execution",
        "valid_for_implementation",
        "safe_to_auto_continue",
    ):
        if packet.get(field) is not False:
            blockers.append(f"duplicate_frontier_repair_authority_field_not_false:{field}")
    return blockers


def _validation_claims(
    approval_gate: Mapping[str, Any],
    receipt_plan: Mapping[str, Any],
    repair_receipt: Mapping[str, Any],
    duplicate_paths: list[str],
) -> list[dict[str, Any]]:
    repair_summary = repair_receipt.get("repair_summary")
    summary = repair_summary if isinstance(repair_summary, Mapping) else {}
    return [
        {
            "claim_id": "source_approval_gate_ready",
            "claim": "completion-validation approval gate is ready for separate governed planning",
            "provenance": SOURCE_COMPLETION_VALIDATION_APPROVAL_GATE_JSON_PATH.as_posix(),
            "risk_level": "LOW",
            "expected_value": EXPECTED_APPROVAL_GATE_STATUS,
            "observed_value": str(approval_gate.get("status", NOT_COMPUTABLE)),
            "claim_validated": approval_gate.get("status") == EXPECTED_APPROVAL_GATE_STATUS,
        },
        {
            "claim_id": "receipt_plan_ready",
            "claim": "Phase 1 receipt plan finalized the future validation packet contract",
            "provenance": SOURCE_COMPLETION_VALIDATION_RECEIPT_PLAN_JSON_PATH.as_posix(),
            "risk_level": "LOW",
            "expected_value": EXPECTED_RECEIPT_PLAN_STATUS,
            "observed_value": str(receipt_plan.get("status", NOT_COMPUTABLE)),
            "claim_validated": receipt_plan.get("status") == EXPECTED_RECEIPT_PLAN_STATUS,
        },
        {
            "claim_id": "duplicate_frontier_clean",
            "claim": "duplicate frontier repair removed the known 466 byte-equal duplicate paths",
            "provenance": SOURCE_DUPLICATE_REPAIR_RECEIPT_JSON_PATH.as_posix(),
            "risk_level": "MEDIUM",
            "expected_value": "post_duplicate_remaining_count=0",
            "observed_value": f"post_duplicate_remaining_count={summary.get('post_duplicate_remaining_count', NOT_COMPUTABLE)}",
            "claim_validated": summary.get("post_duplicate_remaining_count") == 0
            and duplicate_paths == [],
        },
        {
            "claim_id": "authority_locks_preserved_false",
            "claim": "all source authority locks remain false",
            "provenance": "source_records.authority_locks_all_false",
            "risk_level": "HIGH",
            "expected_value": "all authority locks false",
            "observed_value": str(
                all(
                    _locks_all_false(packet.get("authority_locks"))
                    for packet in (approval_gate, receipt_plan, repair_receipt)
                )
            ),
            "claim_validated": all(
                _locks_all_false(packet.get("authority_locks"))
                for packet in (approval_gate, receipt_plan, repair_receipt)
            ),
        },
        {
            "claim_id": "downstream_remains_not_computable",
            "claim": "the implementation receipt does not itself authorize downstream execution",
            "provenance": "implementation_receipt.downstream",
            "risk_level": "HIGH",
            "expected_value": NOT_COMPUTABLE,
            "observed_value": NOT_COMPUTABLE,
            "claim_validated": True,
        },
    ]


def _validation_packet_contract(
    receipt_plan: Mapping[str, Any],
    validation_claims: list[dict[str, Any]],
) -> dict[str, Any]:
    planned_contract = receipt_plan.get("planned_validation_packet_contract")
    contract = planned_contract if isinstance(planned_contract, Mapping) else {}
    source_hashes = contract.get("source_packet_hashes")
    packet_hashes = source_hashes if isinstance(source_hashes, Mapping) else {}
    return {
        "contract_id": (
            "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
            "implementation_packet_contract_001"
        ),
        "record_id": str(
            contract.get(
                "record_id",
                "v2_hygiene_phase1_stabilization_decision_record_001",
            )
        ),
        "record_output_path": str(
            contract.get(
                "record_output_path",
                "out/operator_review/"
                "v2_hygiene_phase1_stabilization_decision_record_001.latest.json",
            )
        ),
        "source_packet_hashes": {str(key): str(value) for key, value in sorted(packet_hashes.items())},
        "required_fields": [
            "record_id",
            "record_output_path",
            "source_packet_hashes",
            "validation_claims",
            "authority_denials",
            "recommended_next_lane",
            "downstream",
        ],
        "validation_claims": validation_claims,
        "validation_claims_required_structure": {
            "claim_id": "stable string identifier",
            "claim": "plain-language validation claim",
            "provenance": "source artifact path or packet field",
            "risk_level": "LOW | MEDIUM | HIGH",
            "expected_value": "deterministic expected value",
            "observed_value": "deterministic observed value",
            "claim_validated": True,
        },
        "authority_denials": {
            "record_completion_validation_performed": False,
            "record_completion_authorized": False,
            "record_finalization_authorized": False,
            "record_emission_authorized": False,
            "record_materialization_authorized": False,
            "implementation_authorized": False,
            "execution_authority": False,
            "notion_writeback_allowed": False,
            "github_writeback_allowed": False,
            "v2_module_registration_authorized": False,
            "rune_registration_authorized": False,
            "runtime_mutation": False,
            "canon_mutation": False,
            "queue_mutation": False,
            "scheduler_mutation": False,
            "package_lock_mutation_authorized": False,
        },
        "completion_validation_authorized": False,
        "completion_validation_performed": False,
        "implementation_receipt_only": True,
    }


def _brier_scoring_contract(validation_claims: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "contract_id": (
            "v2_hygiene_phase1_stabilization_completion_validation_brier_"
            "telemetry_contract_implementation_001"
        ),
        "telemetry_only": True,
        "required_fields": [
            "claim_id",
            "forecast_probability",
            "binary_outcome",
            "brier_score",
            "resolution_source",
        ],
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "telemetry_hooks": [
            {
                "claim_id": claim["claim_id"],
                "forecast_probability": 0.95,
                "binary_outcome": NOT_COMPUTABLE,
                "brier_score": NOT_COMPUTABLE,
                "resolution_source": NOT_COMPUTABLE,
                "resolution_allowed": False,
            }
            for claim in validation_claims
        ],
        "resolution_allowed": False,
        "adaptive_learning_authorized": False,
        "forecast_routing_authorized": False,
        "promotion_authorized": False,
        "execution_authority": False,
    }


def _rune_governance_mapping() -> list[dict[str, Any]]:
    return [
        {
            "rune": "Observe",
            "governance_mapping": "source readiness, repair evidence, and duplicate frontier observation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": "source packet hash, schema, and validation-claim linkage",
            "authority_granted": False,
            "risk_level": "MEDIUM",
        },
        {
            "rune": "Hold",
            "governance_mapping": "authority locks, downstream NOT_COMPUTABLE, and execution denial preservation",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Weigh",
            "governance_mapping": "telemetry-only Brier claim scoring without routing or adaptive authority",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Seal",
            "governance_mapping": "future operator-approved completion-validation execution state only",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_implementation_receipt(
    repo_root: str | Path = ".",
    *,
    source_completion_validation_approval_gate_path: str | Path = (
        SOURCE_COMPLETION_VALIDATION_APPROVAL_GATE_JSON_PATH
    ),
    source_completion_validation_receipt_plan_path: str | Path = (
        SOURCE_COMPLETION_VALIDATION_RECEIPT_PLAN_JSON_PATH
    ),
    source_duplicate_repair_receipt_path: str | Path = (
        SOURCE_DUPLICATE_REPAIR_RECEIPT_JSON_PATH
    ),
) -> dict[str, Any]:
    root = Path(repo_root)
    approval_gate_path = Path(source_completion_validation_approval_gate_path)
    receipt_plan_path = Path(source_completion_validation_receipt_plan_path)
    repair_receipt_path = Path(source_duplicate_repair_receipt_path)
    approval_gate = _read_json(_resolve(root, approval_gate_path)) or {}
    receipt_plan = _read_json(_resolve(root, receipt_plan_path)) or {}
    repair_receipt = _read_json(_resolve(root, repair_receipt_path)) or {}
    duplicate_paths = _frontier_duplicate_paths(root, repair_receipt)
    blockers: list[str] = []
    if not approval_gate:
        blockers.append("required_completion_validation_approval_gate_missing")
    else:
        blockers.extend(_approval_gate_blockers(approval_gate))
    if not receipt_plan:
        blockers.append("required_completion_validation_receipt_plan_missing")
    else:
        blockers.extend(_receipt_plan_blockers(receipt_plan))
    if not repair_receipt:
        blockers.append("required_duplicate_frontier_repair_receipt_missing")
    else:
        blockers.extend(_repair_receipt_blockers(repair_receipt))
    if duplicate_paths:
        blockers.append("duplicate_frontier_paths_observed")
    blockers = sorted(set(blockers))
    ready = bool(approval_gate and receipt_plan and repair_receipt) and not blockers
    validation_claims = _validation_claims(
        approval_gate,
        receipt_plan,
        repair_receipt,
        duplicate_paths,
    )
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": READY_STATUS if ready else (BLOCKED_STATUS if blockers else NOT_COMPUTABLE),
        "sources_observed": bool(approval_gate and receipt_plan and repair_receipt),
        "source_records": [
            _source_record(
                "completion_validation_approval_gate",
                approval_gate_path,
                approval_gate,
                expected_status=EXPECTED_APPROVAL_GATE_STATUS,
                hash_keys=("gate_hash",),
            ),
            _source_record(
                "completion_validation_receipt_plan",
                receipt_plan_path,
                receipt_plan,
                expected_status=EXPECTED_RECEIPT_PLAN_STATUS,
                hash_keys=("receipt_plan_hash",),
            ),
            _source_record(
                "duplicate_frontier_repair_execution_receipt",
                repair_receipt_path,
                repair_receipt,
                expected_status=EXPECTED_REPAIR_RECEIPT_STATUS,
                hash_keys=("repair_execution_receipt_hash",),
            ),
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "implementation_receipt_ready": ready,
        "clean_frontier_evidence": {
            "duplicate_frontier_paths_observed_count": len(duplicate_paths),
            "duplicate_frontier_paths_observed": duplicate_paths,
            "source_repair_deleted_path_count": (
                repair_receipt.get("repair_summary", {}).get("deleted_path_count")
                if isinstance(repair_receipt.get("repair_summary"), Mapping)
                else NOT_COMPUTABLE
            ),
            "package_lock_path": "apps/aal-viz-live-console/package-lock.json",
            "package_lock_mutation_authorized": False,
        },
        "validation_packet_contract": _validation_packet_contract(
            receipt_plan,
            validation_claims,
        ),
        "brier_scoring_contract": _brier_scoring_contract(validation_claims),
        "rune_governance_mapping": _rune_governance_mapping(),
        "selected_follow_on_action": (
            "PLAN_SEPARATE_COMPLETION_VALIDATION_EXECUTION_AUTHORIZATION_GATE"
            if ready
            else "RESTORE_SOURCE_CHAIN_BEFORE_COMPLETION_VALIDATION_IMPLEMENTATION"
        ),
        "recommended_next_action": (
            "prepare a separate governed completion-validation execution authorization "
            "gate; do not complete, finalize, emit, materialize, write back, register, "
            "activate, promote, auto-continue, or execute"
            if ready
            else "restore the source chain and clean frontier before requesting any "
            "completion-validation execution authorization gate"
        ),
        "recommended_next_lane": NEXT_AUTHORIZATION_GATE_LANE if ready else NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "downstream": NOT_COMPUTABLE,
        "decision_record_created": False,
        "decision_record_creation_authorized": False,
        "decision_record_completed": False,
        "decision_record_completion_authorized": False,
        "decision_record_completion_validation_authorized": False,
        "decision_record_completion_validation_performed": False,
        "decision_record_emitted": False,
        "decision_record_emission_authorized": False,
        "decision_record_finalized": False,
        "decision_record_finalization_authorized": False,
        "decision_record_materialized": False,
        "decision_record_materialization_authorized": False,
        "authorization_record_created": False,
        "authorization_record_creation_authorized": False,
        "evidence_bundle_created": False,
        "evidence_bundle_creation_authorized": False,
        "operator_attestation_created": False,
        "operator_evidence_bundle_created": False,
        "operator_evidence_bundle_creation_authorized": False,
        "implementation_authorized": False,
        "hygiene_code_creation_authorized": False,
        "schema_file_creation_authorized": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "strict_mode_enablement_authorized": False,
        "package_lock_mutation_authorized": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "canon_mutation": False,
        "schema_mutation": False,
        "execution_authority": False,
        "forecast_routing_authorized": False,
        "adaptive_learning_authorized": False,
        "promotion_authorized": False,
        "valid_for_decision_record_creation": False,
        "valid_for_decision_record_completion": False,
        "valid_for_decision_record_completion_validation": False,
        "valid_for_decision_record_emission": False,
        "valid_for_decision_record_finalization": False,
        "valid_for_decision_record_materialization": False,
        "valid_for_completion_validation_execution_authorization_gate": ready,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authority_locks": _copied_authority_locks(
            approval_gate,
            receipt_plan,
            repair_receipt,
        ),
        "implementation_receipt_hash": "",
    }
    packet["implementation_receipt_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "implementation_receipt_hash"
        }
    )
    return packet


def render_v2_hygiene_phase1_stabilization_decision_record_completion_validation_implementation_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    validation_contract = packet["validation_packet_contract"]
    brier_contract = packet["brier_scoring_contract"]
    clean_frontier = packet["clean_frontier_evidence"]
    lines = [
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Completion Validation Implementation Receipt",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- implementation_receipt_ready: {packet['implementation_receipt_ready']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- downstream: {packet['downstream']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- valid_for_completion_validation_execution_authorization_gate: {packet['valid_for_completion_validation_execution_authorization_gate']}",
        f"- valid_for_decision_record_completion_validation: {packet['valid_for_decision_record_completion_validation']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Clean Frontier Evidence",
        f"- duplicate_frontier_paths_observed_count: {clean_frontier['duplicate_frontier_paths_observed_count']}",
        f"- source_repair_deleted_path_count: {clean_frontier['source_repair_deleted_path_count']}",
        f"- package_lock_mutation_authorized: {clean_frontier['package_lock_mutation_authorized']}",
        "",
        "## Validation Packet Contract",
        f"- contract_id: {validation_contract['contract_id']}",
        f"- record_id: {validation_contract['record_id']}",
        f"- record_output_path: {validation_contract['record_output_path']}",
        f"- completion_validation_authorized: {validation_contract['completion_validation_authorized']}",
        f"- completion_validation_performed: {validation_contract['completion_validation_performed']}",
        "",
        "## Validation Claims",
    ]
    lines.extend(
        f"- {claim['claim_id']}: {claim['claim_validated']} "
        f"(risk={claim['risk_level']}, provenance={claim['provenance']})"
        for claim in validation_contract["validation_claims"]
    )
    lines.extend(
        [
            "",
            "## Brier Scoring Contract",
            f"- contract_id: {brier_contract['contract_id']}",
            f"- telemetry_only: {brier_contract['telemetry_only']}",
            f"- brier_score_formula: {brier_contract['brier_score_formula']}",
            f"- resolution_allowed: {brier_contract['resolution_allowed']}",
            f"- adaptive_learning_authorized: {brier_contract['adaptive_learning_authorized']}",
            f"- forecast_routing_authorized: {brier_contract['forecast_routing_authorized']}",
            f"- promotion_authorized: {brier_contract['promotion_authorized']}",
            "",
            "## Rune Governance Mapping",
        ]
    )
    lines.extend(
        f"- {mapping['rune']}: {mapping['governance_mapping']} "
        f"(authority_granted={mapping['authority_granted']}, risk={mapping['risk_level']})"
        for mapping in packet["rune_governance_mapping"]
    )
    lines.extend(["", "## Source Blockers"])
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase1_stabilization_decision_record_completion_validation_implementation_receipt(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_implementation_receipt(
        repo_root
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_stabilization_decision_record_completion_validation_implementation_receipt_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
