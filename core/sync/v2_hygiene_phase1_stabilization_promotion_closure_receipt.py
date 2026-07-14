from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_completion_receipt import (
    RECEIPT_JSON_PATH as SOURCE_COMPLETION_RECEIPT_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygienePhase1StabilizationPromotionClosureReceipt.v1"
RECEIPT_ID = "v2_hygiene_phase1_stabilization_promotion_closure_receipt_001"
RECORD_ID = "v2_hygiene_phase1_stabilization_decision_record_001"
RECORD_OUTPUT_PATH = "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_001.latest.json"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase1_stabilization_promotion_closure_receipt_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
READY_STATUS = "V2_HYGIENE_PHASE1_STABILIZATION_PROMOTION_CLOSURE_RECEIPT_READY"
BLOCKED_STATUS = "V2_HYGIENE_PHASE1_STABILIZATION_PROMOTION_CLOSURE_RECEIPT_BLOCKED"
EXPECTED_COMPLETION_RECEIPT_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_RECEIPT_READY"
)
EXPECTED_COMPLETION_RECEIPT_HASH = (
    "a0eb709dc8ad24c72f8df28bbeaa7742c253f0463d61cec473a6a10af27a7a97"
)
EXPECTED_PHASE4_GATE_HASH = (
    "499532b0b4937fd0aece57f337fc830e03dae65a8fd9cc05b8c54bfbffd34edb"
)
NEXT_WRITEBACK_AUTHORIZATION_LANE = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_WRITEBACK_AUTHORIZATION_RECEIPT_001"
)
NEXT_PROMOTION_AUTHORIZATION_GATE = (
    "V2_HYGIENE_PHASE1_STABILIZATION_PROMOTION_AUTHORIZATION_GATE_001"
)

AUTHORITY_EXPANDING_FIELDS = (
    "decision_record_created",
    "decision_record_creation_authorized",
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
    "brier_resolution_authorized",
    "package_lock_mutation_authorized",
    "valid_for_execution",
    "valid_for_implementation",
    "valid_for_decision_record_creation",
    "valid_for_decision_record_completion_validation",
    "valid_for_decision_record_emission",
    "valid_for_decision_record_finalization",
    "valid_for_decision_record_materialization",
    "valid_for_writeback",
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
        "brier_resolution": False,
        "canon_mutation": False,
        "decision_record_creation": False,
        "decision_record_emission": False,
        "decision_record_finalization": False,
        "decision_record_materialization": False,
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
        "promotion": False,
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
        "writeback": False,
    }


def _copied_authority_locks(source: Mapping[str, Any]) -> dict[str, bool]:
    locks = source.get("authority_locks")
    if _locks_all_false(locks):
        copied = {str(key): False for key in sorted(locks)}
        copied.pop("decision_record_completion", None)
        copied.setdefault("promotion", False)
        copied.setdefault("brier_resolution", False)
        copied.setdefault("writeback", False)
        return copied
    return _authority_locks()


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
            if field != "decision_record_completion" and value is True
        )
    return blockers


def _source_record(source_id: str, path: Path, packet: Mapping[str, Any]) -> dict[str, Any]:
    contract = packet.get("decision_record_completion_contract")
    return {
        "source_id": source_id,
        "path": path.as_posix(),
        "observed": bool(packet),
        "file_hash": _sha256(path),
        "packet_hash": str(packet.get("completion_receipt_hash", NOT_COMPUTABLE)),
        "expected_packet_hash": EXPECTED_COMPLETION_RECEIPT_HASH,
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_COMPLETION_RECEIPT_STATUS,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "phase4_gate_hash_verified": packet.get("source_records", [{}])[0].get(
            "packet_hash", NOT_COMPUTABLE
        )
        == EXPECTED_PHASE4_GATE_HASH
        if isinstance(packet.get("source_records"), list) and packet.get("source_records")
        else False,
        "record_id": str(packet.get("record_id", NOT_COMPUTABLE)),
        "record_output_path": str(packet.get("record_output_path", NOT_COMPUTABLE)),
        "decision_record_completed": packet.get("decision_record_completed"),
        "completion_claims_finalized": packet.get("completion_claims_finalized"),
        "completion_claim_count": (
            contract.get("completion_claim_count", NOT_COMPUTABLE)
            if isinstance(contract, Mapping)
            else NOT_COMPUTABLE
        ),
        "completion_claims_finalized_count": (
            contract.get("completion_claims_finalized_count", NOT_COMPUTABLE)
            if isinstance(contract, Mapping)
            else NOT_COMPUTABLE
        ),
        "recommended_next_lane": str(packet.get("recommended_next_lane", NOT_COMPUTABLE)),
        "downstream": str(packet.get("downstream", NOT_COMPUTABLE)),
    }


def _completion_receipt_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers = []
    if packet.get("status") != EXPECTED_COMPLETION_RECEIPT_STATUS:
        blockers.append("completion_receipt_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("completion_receipt_source_not_ready")
    if packet.get("completion_receipt_ready") is not True:
        blockers.append("completion_receipt_ready_not_true")
    if packet.get("completion_receipt_hash") != EXPECTED_COMPLETION_RECEIPT_HASH:
        blockers.append("completion_receipt_hash_mismatch")
    packet_without_hash = dict(packet)
    observed_hash = packet_without_hash.pop("completion_receipt_hash", NOT_COMPUTABLE)
    if canonical_hash(packet_without_hash) != observed_hash:
        blockers.append("completion_receipt_self_hash_mismatch")
    if packet.get("source_blockers") != []:
        blockers.append("completion_receipt_source_blockers_not_empty")
    if packet.get("record_id") != RECORD_ID:
        blockers.append("completion_receipt_record_id_mismatch")
    if packet.get("record_output_path") != RECORD_OUTPUT_PATH:
        blockers.append("completion_receipt_record_output_path_mismatch")
    if packet.get("decision_record_completed") is not True:
        blockers.append("completion_receipt_decision_record_not_completed")
    if packet.get("decision_record_completion_authorized") is not True:
        blockers.append("completion_receipt_completion_not_authorized")
    if packet.get("decision_record_completion_receipt_emitted") is not True:
        blockers.append("completion_receipt_not_emitted")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("completion_receipt_downstream_not_closed")
    if not _locks_all_false(packet.get("authority_locks")):
        blockers.append("completion_receipt_locks_not_false")

    source_records = packet.get("source_records")
    if not isinstance(source_records, list) or not source_records:
        blockers.append("completion_receipt_source_records_missing")
    else:
        phase4_record = source_records[0]
        if not isinstance(phase4_record, Mapping):
            blockers.append("completion_receipt_phase4_source_record_malformed")
        elif phase4_record.get("packet_hash") != EXPECTED_PHASE4_GATE_HASH:
            blockers.append("completion_receipt_phase4_gate_hash_mismatch")

    contract = packet.get("decision_record_completion_contract")
    if not isinstance(contract, Mapping):
        blockers.append("completion_contract_missing")
    else:
        if contract.get("record_id") != RECORD_ID:
            blockers.append("completion_contract_record_id_mismatch")
        if contract.get("record_output_path") != RECORD_OUTPUT_PATH:
            blockers.append("completion_contract_record_output_path_mismatch")
        if contract.get("completion_receipt_authorized") is not True:
            blockers.append("completion_contract_receipt_not_authorized")
        if contract.get("completion_receipt_emitted") is not True:
            blockers.append("completion_contract_receipt_not_emitted")
        if contract.get("decision_record_completed") is not True:
            blockers.append("completion_contract_record_not_completed")
        if contract.get("completion_claim_count") != 5:
            blockers.append("completion_contract_claim_count_not_five")
        if contract.get("completion_claims_finalized_count") != 5:
            blockers.append("completion_contract_claims_not_finalized")
        claims = contract.get("completion_claims")
        if not isinstance(claims, list) or len(claims) != 5:
            blockers.append("completion_contract_claims_missing")
        elif any(
            not isinstance(claim, Mapping)
            or claim.get("claim_finalized") is not True
            or claim.get("completion_status") != "COMPLETION_CLAIM_FINALIZED"
            for claim in claims
        ):
            blockers.append("completion_contract_claim_not_finalized")
        if not _locks_all_false(contract.get("authority_denials")):
            blockers.append("completion_contract_authority_denials_not_false")

    brier_contract = packet.get("brier_scoring_contract")
    if not isinstance(brier_contract, Mapping):
        blockers.append("completion_receipt_brier_contract_missing")
    else:
        if brier_contract.get("telemetry_only") is not True:
            blockers.append("completion_receipt_brier_not_telemetry_only")
        for field in (
            "resolution_allowed",
            "adaptive_learning_authorized",
            "forecast_routing_authorized",
            "promotion_authorized",
            "execution_authority",
            "brier_resolution_authorized",
        ):
            if brier_contract.get(field) is not False:
                blockers.append(f"completion_receipt_brier_authority_not_false:{field}")
        hooks = brier_contract.get("telemetry_hooks")
        if not isinstance(hooks, list) or len(hooks) != 5:
            blockers.append("completion_receipt_brier_hook_count_not_five")
        elif any(
            not isinstance(hook, Mapping)
            or hook.get("binary_outcome") != NOT_COMPUTABLE
            or hook.get("resolution_allowed") is not False
            for hook in hooks
        ):
            blockers.append("completion_receipt_brier_hook_authority_or_resolution")

    rune_mapping = packet.get("rune_governance_mapping")
    expected_runes = {"Observe", "Bind", "Hold", "Weigh", "Seal"}
    if not isinstance(rune_mapping, list):
        blockers.append("completion_receipt_rune_mapping_missing")
    else:
        observed_runes = {
            str(mapping.get("rune"))
            for mapping in rune_mapping
            if isinstance(mapping, Mapping)
        }
        if observed_runes != expected_runes:
            blockers.append("completion_receipt_rune_mapping_unexpected")
        if any(
            not isinstance(mapping, Mapping) or mapping.get("authority_granted") is not False
            for mapping in rune_mapping
        ):
            blockers.append("completion_receipt_rune_authority_not_false")

    for field in (
        "valid_for_writeback",
        "valid_for_execution",
        "safe_to_auto_continue",
        "brier_resolution_authorized",
        "promotion_authorized",
        "package_lock_mutation_authorized",
    ):
        if packet.get(field) is not False:
            blockers.append(f"completion_receipt_authority_not_false:{field}")
    blockers.extend(_authority_expansion_blockers("completion_receipt", packet))
    return blockers


def _closure_claims(ready: bool) -> list[dict[str, Any]]:
    base_claims = [
        {
            "claim_id": "phase5_completion_receipt_ready",
            "claim": "Phase 5 decision-record completion receipt is ready",
            "provenance": (
                "out/operator_review/"
                "v2_hygiene_phase1_stabilization_decision_record_completion_receipt_001.latest.json#status"
            ),
            "risk_level": "LOW",
            "expected_value": EXPECTED_COMPLETION_RECEIPT_STATUS,
            "observed_value": EXPECTED_COMPLETION_RECEIPT_STATUS if ready else NOT_COMPUTABLE,
        },
        {
            "claim_id": "phase5_completion_receipt_hash_pinned",
            "claim": "Phase 5 completion receipt hash is pinned and verified",
            "provenance": "source_records.decision_record_completion_receipt.packet_hash",
            "risk_level": "LOW",
            "expected_value": EXPECTED_COMPLETION_RECEIPT_HASH,
            "observed_value": EXPECTED_COMPLETION_RECEIPT_HASH if ready else NOT_COMPUTABLE,
        },
        {
            "claim_id": "decision_record_completion_observed",
            "claim": "Scoped advisory decision-record completion is observed for the stabilization record",
            "provenance": "decision_record_completion_receipt.decision_record_completion_contract",
            "risk_level": "MEDIUM",
            "expected_value": "decision_record_completed=true; completion_claims_finalized_count=5",
            "observed_value": (
                "decision_record_completed=true; completion_claims_finalized_count=5"
                if ready
                else NOT_COMPUTABLE
            ),
        },
        {
            "claim_id": "phase1_stabilization_advisory_complete_not_promoted",
            "claim": "Phase 1 stabilization is advisory-complete but not canon-promoted",
            "provenance": "promotion_closure_contract.promotion_readiness_classification",
            "risk_level": "HIGH",
            "expected_value": "ADVISORY_COMPLETE_NOT_CANON_PROMOTED",
            "observed_value": "ADVISORY_COMPLETE_NOT_CANON_PROMOTED" if ready else NOT_COMPUTABLE,
        },
        {
            "claim_id": "post_closure_authorities_remain_denied",
            "claim": "Writeback, promotion, activation, runtime/canon mutation, Brier resolution, package-lock mutation, auto-continuation, and execution remain denied",
            "provenance": "promotion_closure_receipt.authority_locks",
            "risk_level": "HIGH",
            "expected_value": "all post-closure authorities false",
            "observed_value": "all post-closure authorities false" if ready else NOT_COMPUTABLE,
        },
    ]
    return [
        {
            **claim,
            "claim_finalized": ready,
            "closure_status": "CLOSURE_CLAIM_FINALIZED" if ready else "BLOCKED",
            "fail_closed_blocker": "none" if ready else "source_not_ready",
        }
        for claim in base_claims
    ]


def _promotion_closure_contract(ready: bool) -> dict[str, Any]:
    claims = _closure_claims(ready)
    return {
        "contract_id": "v2_hygiene_phase1_stabilization_promotion_closure_contract_001",
        "record_id": RECORD_ID,
        "record_output_path": RECORD_OUTPUT_PATH,
        "phase1_stabilization_advisory_complete": ready,
        "promotion_readiness_classification": (
            "ADVISORY_COMPLETE_NOT_CANON_PROMOTED" if ready else NOT_COMPUTABLE
        ),
        "closure_receipt_authorized": ready,
        "closure_receipt_emitted": ready,
        "closure_claims": claims,
        "closure_claim_count": len(claims),
        "closure_claims_finalized_count": sum(
            1 for claim in claims if claim["claim_finalized"] is True
        ),
        "recommended_follow_on_gates": [
            NEXT_WRITEBACK_AUTHORIZATION_LANE,
            NEXT_PROMOTION_AUTHORIZATION_GATE,
        ]
        if ready
        else [],
        "writeback_performed": False,
        "canon_promotion_performed": False,
        "runtime_activation_performed": False,
        "package_lock_mutation_performed": False,
        "authority_denials": {
            "notion_writeback_allowed": False,
            "github_writeback_allowed": False,
            "runtime_mutation": False,
            "canon_mutation": False,
            "queue_mutation": False,
            "scheduler_mutation": False,
            "v2_module_registration_authorized": False,
            "rune_registration_authorized": False,
            "activation_authorized": False,
            "promotion_authorized": False,
            "brier_resolution_authorized": False,
            "forecast_routing_authorized": False,
            "adaptive_learning_authorized": False,
            "package_lock_mutation_authorized": False,
            "execution_authority": False,
            "auto_continuation_authorized": False,
        },
    }


def _brier_scoring_contract(claims: list[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "contract_id": (
            "v2_hygiene_phase1_stabilization_promotion_closure_"
            "brier_telemetry_contract_001"
        ),
        "telemetry_only": True,
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
            for claim in claims
        ],
        "resolution_allowed": False,
        "adaptive_learning_authorized": False,
        "forecast_routing_authorized": False,
        "promotion_authorized": False,
        "execution_authority": False,
        "brier_resolution_authorized": False,
    }


def _rune_governance_mapping() -> list[dict[str, Any]]:
    return [
        {
            "rune": "Observe",
            "governance_mapping": "Phase 5 completion receipt and clean frontier observation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": "completion receipt hash, record path, schema, and lineage linkage",
            "authority_granted": False,
            "risk_level": "MEDIUM",
        },
        {
            "rune": "Hold",
            "governance_mapping": "writeback, promotion, activation, runtime/canon, and execution locks",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Weigh",
            "governance_mapping": "telemetry-only Brier posture without resolution authority",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Seal",
            "governance_mapping": "advisory Phase 1 stabilization closure only, not canon or runtime activation",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase1_stabilization_promotion_closure_receipt(
    repo_root: str | Path = ".",
    *,
    source_decision_record_completion_receipt_path: str | Path = (
        SOURCE_COMPLETION_RECEIPT_JSON_PATH
    ),
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_decision_record_completion_receipt_path)
    completion_receipt = _read_json(_resolve(root, source_path)) or {}
    blockers = []
    if not completion_receipt:
        blockers.append("required_decision_record_completion_receipt_missing")
    else:
        blockers.extend(_completion_receipt_blockers(completion_receipt))
    blockers = sorted(set(blockers))
    ready = bool(completion_receipt) and not blockers
    closure_contract = _promotion_closure_contract(ready)
    claims = closure_contract["closure_claims"]
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": READY_STATUS if ready else BLOCKED_STATUS,
        "sources_observed": bool(completion_receipt),
        "source_records": [
            _source_record(
                "decision_record_completion_receipt",
                source_path,
                completion_receipt,
            )
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "closure_receipt_ready": ready,
        "record_id": RECORD_ID,
        "record_output_path": RECORD_OUTPUT_PATH,
        "promotion_closure_contract": closure_contract,
        "closure_claims_finalized": ready,
        "phase1_stabilization_advisory_complete": ready,
        "promotion_readiness_classification": (
            "ADVISORY_COMPLETE_NOT_CANON_PROMOTED" if ready else NOT_COMPUTABLE
        ),
        "brier_scoring_contract": _brier_scoring_contract(claims),
        "rune_governance_mapping": _rune_governance_mapping(),
        "selected_follow_on_action": (
            "HOLD_FOR_SEPARATE_WRITEBACK_OR_PROMOTION_AUTHORIZATION_GATE"
            if ready
            else "HOLD_FOR_DECISION_RECORD_COMPLETION_RECEIPT_REPAIR"
        ),
        "recommended_next_action": (
            "create a separate writeback authorization receipt or promotion authorization gate "
            "only if the operator wants propagation or canon promotion; keep activation, "
            "runtime/canon/queue/scheduler mutation, registration, Brier resolution, "
            "package-lock mutation, auto-continuation, and execution denied"
            if ready
            else "restore the Phase 5 decision-record completion receipt before closure"
        ),
        "recommended_next_lane": NEXT_WRITEBACK_AUTHORIZATION_LANE if ready else NOT_COMPUTABLE,
        "alternative_next_lane": NEXT_PROMOTION_AUTHORIZATION_GATE if ready else NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "downstream": NOT_COMPUTABLE,
        "decision_record_completed": ready,
        "decision_record_completion_observed": ready,
        "decision_record_created": False,
        "decision_record_creation_authorized": False,
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
        "activation_authorized": False,
        "brier_resolution_authorized": False,
        "valid_for_decision_record_creation": False,
        "valid_for_decision_record_completion": False,
        "valid_for_decision_record_completion_validation": False,
        "valid_for_decision_record_emission": False,
        "valid_for_decision_record_finalization": False,
        "valid_for_decision_record_materialization": False,
        "valid_for_writeback": False,
        "valid_for_promotion": False,
        "valid_for_activation": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authority_locks": _copied_authority_locks(completion_receipt),
        "closure_receipt_hash": "",
    }
    packet["closure_receipt_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "closure_receipt_hash"}
    )
    return packet


def render_v2_hygiene_phase1_stabilization_promotion_closure_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    closure_contract = packet["promotion_closure_contract"]
    brier_contract = packet["brier_scoring_contract"]
    lines = [
        "# v2.0 Hygiene Phase 1 Stabilization Promotion Closure Receipt",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- closure_receipt_ready: {packet['closure_receipt_ready']}",
        f"- record_id: {packet['record_id']}",
        f"- record_output_path: {packet['record_output_path']}",
        f"- phase1_stabilization_advisory_complete: {packet['phase1_stabilization_advisory_complete']}",
        f"- promotion_readiness_classification: {packet['promotion_readiness_classification']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- alternative_next_lane: {packet['alternative_next_lane']}",
        f"- downstream: {packet['downstream']}",
        f"- valid_for_writeback: {packet['valid_for_writeback']}",
        f"- valid_for_promotion: {packet['valid_for_promotion']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Promotion Closure Contract",
        f"- contract_id: {closure_contract['contract_id']}",
        f"- phase1_stabilization_advisory_complete: {closure_contract['phase1_stabilization_advisory_complete']}",
        f"- promotion_readiness_classification: {closure_contract['promotion_readiness_classification']}",
        f"- closure_receipt_authorized: {closure_contract['closure_receipt_authorized']}",
        f"- closure_receipt_emitted: {closure_contract['closure_receipt_emitted']}",
        f"- closure_claim_count: {closure_contract['closure_claim_count']}",
        f"- closure_claims_finalized_count: {closure_contract['closure_claims_finalized_count']}",
        f"- writeback_performed: {closure_contract['writeback_performed']}",
        f"- canon_promotion_performed: {closure_contract['canon_promotion_performed']}",
        f"- runtime_activation_performed: {closure_contract['runtime_activation_performed']}",
        "",
        "## Closure Claims",
    ]
    lines.extend(
        f"- {claim['claim_id']}: {claim['closure_status']} "
        f"(risk={claim['risk_level']}, provenance={claim['provenance']}, "
        f"blocker={claim['fail_closed_blocker']})"
        for claim in closure_contract["closure_claims"]
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
            f"- brier_resolution_authorized: {brier_contract['brier_resolution_authorized']}",
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


def write_v2_hygiene_phase1_stabilization_promotion_closure_receipt(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_stabilization_promotion_closure_receipt(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_stabilization_promotion_closure_receipt_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
