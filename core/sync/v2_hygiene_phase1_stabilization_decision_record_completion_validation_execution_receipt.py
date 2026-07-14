from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_completion_validation_implementation_receipt import (
    RECEIPT_JSON_PATH as SOURCE_IMPLEMENTATION_RECEIPT_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = (
    "V2HygienePhase1StabilizationDecisionRecordCompletionValidationExecutionReceipt.v1"
)
RECEIPT_ID = (
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
    "execution_receipt_001"
)
RECEIPT_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
    "execution_receipt_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
READY_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "EXECUTION_RECEIPT_READY"
)
BLOCKED_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "EXECUTION_RECEIPT_BLOCKED"
)
EXPECTED_IMPLEMENTATION_RECEIPT_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "IMPLEMENTATION_RECEIPT_READY"
)
NEXT_OPERATOR_GATE_LANE = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "OPERATOR_REVIEW_GATE_001"
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
    "operator_evidence_bundle_created",
    "operator_evidence_bundle_creation_authorized",
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
    "promotion_authorized",
    "package_lock_mutation_authorized",
    "valid_for_execution",
    "valid_for_implementation",
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


def _copied_authority_locks(source: Mapping[str, Any]) -> dict[str, bool]:
    locks = source.get("authority_locks")
    if _locks_all_false(locks):
        return {str(key): False for key in sorted(locks)}
    return _authority_locks()


def _authority_expansion_blockers(
    source_id: str,
    packet: Mapping[str, Any],
) -> list[str]:
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
    hash_key: str,
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": path.as_posix(),
        "observed": bool(packet),
        "file_hash": _sha256(path),
        "packet_hash": str(packet.get(hash_key, NOT_COMPUTABLE)),
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": expected_status,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "recommended_next_lane": str(packet.get("recommended_next_lane", NOT_COMPUTABLE)),
        "downstream": str(packet.get("downstream", NOT_COMPUTABLE)),
        "safe_to_auto_continue": packet.get("safe_to_auto_continue"),
        "valid_for_execution": packet.get("valid_for_execution"),
        "valid_for_implementation": packet.get("valid_for_implementation"),
        "valid_for_decision_record_completion_validation": packet.get(
            "valid_for_decision_record_completion_validation"
        ),
    }


def _source_chain_hash_blockers(
    root: Path,
    implementation_receipt: Mapping[str, Any],
) -> list[str]:
    records = implementation_receipt.get("source_records")
    if not isinstance(records, list):
        return ["implementation_receipt_source_records_missing"]
    blockers = []
    for record in records:
        if not isinstance(record, Mapping):
            blockers.append("implementation_receipt_source_record_malformed")
            continue
        path = str(record.get("path", ""))
        expected_file_hash = str(record.get("file_hash", NOT_COMPUTABLE))
        if not path:
            blockers.append("implementation_receipt_source_record_path_missing")
            continue
        observed_hash = _sha256(_resolve(root, path))
        if observed_hash != expected_file_hash:
            blockers.append(f"implementation_receipt_source_hash_mismatch:{path}")
    return blockers


def _approved_duplicate_manifest_paths(
    root: Path,
    implementation_receipt: Mapping[str, Any],
) -> list[str]:
    records = implementation_receipt.get("source_records")
    if not isinstance(records, list):
        return []
    repair_path = None
    for record in records:
        if (
            isinstance(record, Mapping)
            and record.get("source_id") == "duplicate_frontier_repair_execution_receipt"
        ):
            repair_path = str(record.get("path", ""))
            break
    if not repair_path:
        return []
    repair_receipt = _read_json(_resolve(root, repair_path)) or {}
    deleted_paths = repair_receipt.get("deleted_paths")
    if not isinstance(deleted_paths, list):
        return []
    return sorted(
        str(path)
        for path in deleted_paths
        if isinstance(path, str) and _resolve(root, path).exists()
    )


def _implementation_receipt_blockers(
    root: Path,
    receipt: Mapping[str, Any],
) -> list[str]:
    blockers = []
    if receipt.get("status") != EXPECTED_IMPLEMENTATION_RECEIPT_STATUS:
        blockers.append("implementation_receipt_not_ready")
    if receipt.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("implementation_receipt_source_not_ready")
    if receipt.get("implementation_receipt_ready") is not True:
        blockers.append("implementation_receipt_ready_not_true")
    if receipt.get("valid_for_completion_validation_execution_authorization_gate") is not True:
        blockers.append("implementation_receipt_not_valid_for_execution_authorization_gate")
    if receipt.get("downstream") != NOT_COMPUTABLE:
        blockers.append("implementation_receipt_downstream_not_closed")
    if receipt.get("package_lock_mutation_authorized") is not False:
        blockers.append("implementation_receipt_package_lock_mutation_not_false")
    if not _locks_all_false(receipt.get("authority_locks")):
        blockers.append("implementation_receipt_locks_not_false")
    clean_frontier = receipt.get("clean_frontier_evidence")
    if not isinstance(clean_frontier, Mapping):
        blockers.append("implementation_receipt_clean_frontier_evidence_missing")
    else:
        if clean_frontier.get("duplicate_frontier_paths_observed_count") != 0:
            blockers.append("implementation_receipt_duplicate_frontier_not_clean")
        if clean_frontier.get("package_lock_mutation_authorized") is not False:
            blockers.append("implementation_receipt_package_lock_frontier_not_false")
    contract = receipt.get("validation_packet_contract")
    if not isinstance(contract, Mapping):
        blockers.append("implementation_receipt_validation_packet_contract_missing")
    else:
        if contract.get("completion_validation_performed") is not False:
            blockers.append("implementation_receipt_contract_completion_performed_not_false")
        if not _locks_all_false(contract.get("authority_denials")):
            blockers.append("implementation_receipt_contract_authority_denials_not_false")
        claims = contract.get("validation_claims")
        if not isinstance(claims, list) or not claims:
            blockers.append("implementation_receipt_validation_claims_missing")
        elif any(
            not isinstance(claim, Mapping) or claim.get("claim_validated") is not True
            for claim in claims
        ):
            blockers.append("implementation_receipt_validation_claims_not_all_true")
    brier_contract = receipt.get("brier_scoring_contract")
    if not isinstance(brier_contract, Mapping):
        blockers.append("implementation_receipt_brier_contract_missing")
    else:
        for field in (
            "resolution_allowed",
            "adaptive_learning_authorized",
            "forecast_routing_authorized",
            "promotion_authorized",
            "execution_authority",
        ):
            if brier_contract.get(field) is not False:
                blockers.append(f"implementation_receipt_brier_authority_not_false:{field}")
    blockers.extend(_authority_expansion_blockers("implementation_receipt", receipt))
    blockers.extend(_source_chain_hash_blockers(root, receipt))
    if _approved_duplicate_manifest_paths(root, receipt):
        blockers.append("approved_duplicate_frontier_paths_reappeared")
    return blockers


def _claim_blocker(claim: Mapping[str, Any]) -> str:
    if claim.get("claim_validated") is True:
        return ""
    claim_id = str(claim.get("claim_id", "unknown_claim"))
    return f"claim_not_validated:{claim_id}"


def _executed_validation_claims(
    implementation_receipt: Mapping[str, Any],
) -> list[dict[str, Any]]:
    contract = implementation_receipt.get("validation_packet_contract")
    source_claims = contract.get("validation_claims") if isinstance(contract, Mapping) else []
    claims = source_claims if isinstance(source_claims, list) else []
    executed = []
    for claim in claims:
        if not isinstance(claim, Mapping):
            executed.append(
                {
                    "claim_id": "malformed_claim",
                    "claim": "source claim was malformed",
                    "provenance": "implementation_receipt.validation_packet_contract.validation_claims",
                    "risk_level": "HIGH",
                    "expected_value": "well-formed validation claim",
                    "observed_value": "malformed",
                    "claim_validated": False,
                    "execution_status": "BLOCKED",
                    "fail_closed_blocker": "malformed_claim",
                }
            )
            continue
        blocker = _claim_blocker(claim)
        executed.append(
            {
                "claim_id": str(claim.get("claim_id", "unknown_claim")),
                "claim": str(claim.get("claim", "")),
                "provenance": str(claim.get("provenance", NOT_COMPUTABLE)),
                "risk_level": str(claim.get("risk_level", "HIGH")),
                "expected_value": str(claim.get("expected_value", NOT_COMPUTABLE)),
                "observed_value": str(claim.get("observed_value", NOT_COMPUTABLE)),
                "claim_validated": claim.get("claim_validated") is True,
                "execution_status": "CLAIM_VALIDATED" if not blocker else "BLOCKED",
                "fail_closed_blocker": blocker or "none",
            }
        )
    return executed


def _execution_packet(
    implementation_receipt: Mapping[str, Any],
    executed_claims: list[dict[str, Any]],
) -> dict[str, Any]:
    contract = implementation_receipt.get("validation_packet_contract")
    source_contract = contract if isinstance(contract, Mapping) else {}
    return {
        "contract_id": (
            "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
            "execution_packet_contract_001"
        ),
        "record_id": str(source_contract.get("record_id", NOT_COMPUTABLE)),
        "record_output_path": str(source_contract.get("record_output_path", NOT_COMPUTABLE)),
        "source_packet_hashes": source_contract.get("source_packet_hashes", {}),
        "executed_validation_claims": executed_claims,
        "claim_evaluation_count": len(executed_claims),
        "claims_validated_count": sum(
            1 for claim in executed_claims if claim["claim_validated"] is True
        ),
        "claim_evaluation_performed": True,
        "completion_validation_authorized": False,
        "completion_validation_performed": False,
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
        "execution_receipt_only": True,
    }


def _brier_scoring_contract(executed_claims: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "contract_id": (
            "v2_hygiene_phase1_stabilization_completion_validation_brier_"
            "telemetry_contract_execution_001"
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
            for claim in executed_claims
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
            "governance_mapping": "source-chain, frontier, and validation claim observation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": "source hash, record path, schema, and claim linkage",
            "authority_granted": False,
            "risk_level": "MEDIUM",
        },
        {
            "rune": "Hold",
            "governance_mapping": "decision-record completion and execution authority denial preservation",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Weigh",
            "governance_mapping": "telemetry-only Brier hooks without resolution or routing authority",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Seal",
            "governance_mapping": "future operator-approved completion state only",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt(
    repo_root: str | Path = ".",
    *,
    source_completion_validation_implementation_receipt_path: str | Path = (
        SOURCE_IMPLEMENTATION_RECEIPT_JSON_PATH
    ),
) -> dict[str, Any]:
    root = Path(repo_root)
    implementation_path = Path(source_completion_validation_implementation_receipt_path)
    implementation_receipt = _read_json(_resolve(root, implementation_path)) or {}
    blockers = []
    if not implementation_receipt:
        blockers.append("required_completion_validation_implementation_receipt_missing")
    else:
        blockers.extend(_implementation_receipt_blockers(root, implementation_receipt))
    blockers = sorted(set(blockers))
    executed_claims = _executed_validation_claims(implementation_receipt)
    all_claims_validated = bool(executed_claims) and all(
        claim["claim_validated"] is True for claim in executed_claims
    )
    ready = bool(implementation_receipt) and not blockers and all_claims_validated
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": READY_STATUS if ready else BLOCKED_STATUS,
        "sources_observed": bool(implementation_receipt),
        "source_records": [
            _source_record(
                "completion_validation_implementation_receipt",
                implementation_path,
                implementation_receipt,
                expected_status=EXPECTED_IMPLEMENTATION_RECEIPT_STATUS,
                hash_key="implementation_receipt_hash",
            )
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "execution_receipt_ready": ready,
        "completion_validation_claim_evaluation_performed": bool(executed_claims),
        "execution_packet": _execution_packet(implementation_receipt, executed_claims),
        "brier_scoring_contract": _brier_scoring_contract(executed_claims),
        "rune_governance_mapping": _rune_governance_mapping(),
        "selected_follow_on_action": (
            "HOLD_FOR_OPERATOR_REVIEW_OF_COMPLETION_VALIDATION_EXECUTION_RECEIPT"
            if ready
            else "RESTORE_IMPLEMENTATION_RECEIPT_BEFORE_COMPLETION_VALIDATION_EXECUTION"
        ),
        "recommended_next_action": (
            "review the non-authoritative completion-validation execution receipt; "
            "create a separate operator gate before any decision-record completion, "
            "writeback, registration, activation, promotion, or execution authority"
            if ready
            else "restore the implementation receipt source chain before rerunning "
            "completion-validation claim evaluation"
        ),
        "recommended_next_lane": NEXT_OPERATOR_GATE_LANE if ready else NOT_COMPUTABLE,
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
        "brier_resolution_authorized": False,
        "valid_for_decision_record_creation": False,
        "valid_for_decision_record_completion": False,
        "valid_for_decision_record_completion_validation": False,
        "valid_for_decision_record_emission": False,
        "valid_for_decision_record_finalization": False,
        "valid_for_decision_record_materialization": False,
        "valid_for_writeback": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authority_locks": _copied_authority_locks(implementation_receipt),
        "execution_receipt_hash": "",
    }
    packet["execution_receipt_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "execution_receipt_hash"}
    )
    return packet


def render_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    execution_packet = packet["execution_packet"]
    brier_contract = packet["brier_scoring_contract"]
    lines = [
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Completion Validation Execution Receipt",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- execution_receipt_ready: {packet['execution_receipt_ready']}",
        f"- completion_validation_claim_evaluation_performed: {packet['completion_validation_claim_evaluation_performed']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- downstream: {packet['downstream']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- valid_for_decision_record_completion_validation: {packet['valid_for_decision_record_completion_validation']}",
        f"- valid_for_writeback: {packet['valid_for_writeback']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Execution Packet",
        f"- contract_id: {execution_packet['contract_id']}",
        f"- record_id: {execution_packet['record_id']}",
        f"- record_output_path: {execution_packet['record_output_path']}",
        f"- claim_evaluation_count: {execution_packet['claim_evaluation_count']}",
        f"- claims_validated_count: {execution_packet['claims_validated_count']}",
        f"- completion_validation_authorized: {execution_packet['completion_validation_authorized']}",
        f"- completion_validation_performed: {execution_packet['completion_validation_performed']}",
        "",
        "## Executed Validation Claims",
    ]
    lines.extend(
        f"- {claim['claim_id']}: {claim['execution_status']} "
        f"(risk={claim['risk_level']}, provenance={claim['provenance']}, "
        f"blocker={claim['fail_closed_blocker']})"
        for claim in execution_packet["executed_validation_claims"]
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


def write_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt(
        repo_root
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
