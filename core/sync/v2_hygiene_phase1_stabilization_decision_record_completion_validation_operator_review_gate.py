from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt import (
    RECEIPT_JSON_PATH as SOURCE_EXECUTION_RECEIPT_JSON_PATH,
)

SCHEMA_VERSION = (
    "V2HygienePhase1StabilizationDecisionRecordCompletionValidationOperatorReviewGate.v1"
)
RECEIPT_ID = (
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
    "operator_review_gate_001"
)
RECEIPT_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
    "operator_review_gate_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
NOT_COMPUTABLE = "NOT_COMPUTABLE"
READY_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "OPERATOR_REVIEW_GATE_READY"
)
BLOCKED_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "OPERATOR_REVIEW_GATE_BLOCKED"
)
EXPECTED_EXECUTION_RECEIPT_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "EXECUTION_RECEIPT_READY"
)
EXPECTED_EXECUTION_RECEIPT_HASH = (
    "6ae90808a070f921c691a21437c68ff66854fcac7d988a337954ab69276fd13d"
)
NEXT_DECISION_RECORD_COMPLETION_RECEIPT_LANE = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_RECEIPT_001"
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
    "brier_resolution_authorized",
    "package_lock_mutation_authorized",
    "valid_for_execution",
    "valid_for_implementation",
    "valid_for_decision_record_creation",
    "valid_for_decision_record_completion",
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
        "decision_record_completion": False,
        "decision_record_completion_validation": False,
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
    }


def _copied_authority_locks(source: Mapping[str, Any]) -> dict[str, bool]:
    locks = source.get("authority_locks")
    if _locks_all_false(locks):
        copied = {str(key): False for key in sorted(locks)}
        copied.setdefault("brier_resolution", False)
        copied.setdefault("promotion", False)
        copied.setdefault("decision_record_materialization", False)
        return copied
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
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": path.as_posix(),
        "observed": bool(packet),
        "file_hash": _sha256(path),
        "packet_hash": str(packet.get("execution_receipt_hash", NOT_COMPUTABLE)),
        "expected_packet_hash": EXPECTED_EXECUTION_RECEIPT_HASH,
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_EXECUTION_RECEIPT_STATUS,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "claim_evaluation_count": (
            packet.get("execution_packet", {}).get("claim_evaluation_count")
            if isinstance(packet.get("execution_packet"), Mapping)
            else NOT_COMPUTABLE
        ),
        "claims_validated_count": (
            packet.get("execution_packet", {}).get("claims_validated_count")
            if isinstance(packet.get("execution_packet"), Mapping)
            else NOT_COMPUTABLE
        ),
        "recommended_next_lane": str(packet.get("recommended_next_lane", NOT_COMPUTABLE)),
        "downstream": str(packet.get("downstream", NOT_COMPUTABLE)),
        "safe_to_auto_continue": packet.get("safe_to_auto_continue"),
        "valid_for_execution": packet.get("valid_for_execution"),
        "valid_for_writeback": packet.get("valid_for_writeback"),
        "valid_for_decision_record_completion_validation": packet.get(
            "valid_for_decision_record_completion_validation"
        ),
    }


def _execution_claims(packet: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    execution_packet = packet.get("execution_packet")
    if not isinstance(execution_packet, Mapping):
        return []
    claims = execution_packet.get("executed_validation_claims")
    return [claim for claim in claims if isinstance(claim, Mapping)] if isinstance(claims, list) else []


def _execution_receipt_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers = []
    if packet.get("status") != EXPECTED_EXECUTION_RECEIPT_STATUS:
        blockers.append("execution_receipt_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("execution_receipt_source_not_ready")
    if packet.get("execution_receipt_ready") is not True:
        blockers.append("execution_receipt_ready_not_true")
    if packet.get("execution_receipt_hash") != EXPECTED_EXECUTION_RECEIPT_HASH:
        blockers.append("execution_receipt_hash_mismatch")
    packet_without_hash = dict(packet)
    observed_hash = packet_without_hash.pop("execution_receipt_hash", NOT_COMPUTABLE)
    if canonical_hash(packet_without_hash) != observed_hash:
        blockers.append("execution_receipt_self_hash_mismatch")
    if packet.get("source_blockers") != []:
        blockers.append("execution_receipt_source_blockers_not_empty")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("execution_receipt_downstream_not_closed")
    for field in (
        "valid_for_decision_record_completion_validation",
        "valid_for_writeback",
        "valid_for_execution",
        "safe_to_auto_continue",
        "brier_resolution_authorized",
        "promotion_authorized",
        "package_lock_mutation_authorized",
    ):
        if packet.get(field) is not False:
            blockers.append(f"execution_receipt_authority_not_false:{field}")
    if not _locks_all_false(packet.get("authority_locks")):
        blockers.append("execution_receipt_locks_not_false")

    execution_packet = packet.get("execution_packet")
    if not isinstance(execution_packet, Mapping):
        blockers.append("execution_packet_missing")
    else:
        if execution_packet.get("claim_evaluation_count") != 5:
            blockers.append("execution_packet_claim_count_not_five")
        if execution_packet.get("claims_validated_count") != 5:
            blockers.append("execution_packet_validated_count_not_five")
        if execution_packet.get("completion_validation_authorized") is not False:
            blockers.append("execution_packet_completion_validation_authority_not_false")
        if execution_packet.get("completion_validation_performed") is not False:
            blockers.append("execution_packet_completion_validation_performed_not_false")
        if not _locks_all_false(execution_packet.get("authority_denials")):
            blockers.append("execution_packet_authority_denials_not_false")
        claims = _execution_claims(packet)
        if len(claims) != 5:
            blockers.append("execution_packet_claims_missing")
        for claim in claims:
            claim_id = str(claim.get("claim_id", "unknown_claim"))
            if claim.get("claim_validated") is not True:
                blockers.append(f"execution_packet_claim_not_validated:{claim_id}")
            if claim.get("execution_status") != "CLAIM_VALIDATED":
                blockers.append(f"execution_packet_claim_status_not_validated:{claim_id}")
            if claim.get("risk_level") not in {"LOW", "MEDIUM", "HIGH"}:
                blockers.append(f"execution_packet_claim_risk_invalid:{claim_id}")
            if not claim.get("provenance"):
                blockers.append(f"execution_packet_claim_provenance_missing:{claim_id}")

    brier_contract = packet.get("brier_scoring_contract")
    if not isinstance(brier_contract, Mapping):
        blockers.append("execution_receipt_brier_contract_missing")
    else:
        if brier_contract.get("telemetry_only") is not True:
            blockers.append("execution_receipt_brier_not_telemetry_only")
        for field in (
            "resolution_allowed",
            "adaptive_learning_authorized",
            "forecast_routing_authorized",
            "promotion_authorized",
            "execution_authority",
        ):
            if brier_contract.get(field) is not False:
                blockers.append(f"execution_receipt_brier_authority_not_false:{field}")
        hooks = brier_contract.get("telemetry_hooks")
        if not isinstance(hooks, list) or len(hooks) != 5:
            blockers.append("execution_receipt_brier_hooks_missing")
        elif any(
            not isinstance(hook, Mapping)
            or hook.get("resolution_allowed") is not False
            or hook.get("binary_outcome") != NOT_COMPUTABLE
            or hook.get("brier_score") != NOT_COMPUTABLE
            for hook in hooks
        ):
            blockers.append("execution_receipt_brier_hook_authority_or_resolution_present")

    rune_mapping = packet.get("rune_governance_mapping")
    expected_runes = {"Observe", "Bind", "Hold", "Weigh", "Seal"}
    if not isinstance(rune_mapping, list):
        blockers.append("execution_receipt_rune_mapping_missing")
    else:
        observed_runes = {
            str(mapping.get("rune"))
            for mapping in rune_mapping
            if isinstance(mapping, Mapping)
        }
        if observed_runes != expected_runes:
            blockers.append("execution_receipt_rune_mapping_unexpected")
        if any(
            not isinstance(mapping, Mapping) or mapping.get("authority_granted") is not False
            for mapping in rune_mapping
        ):
            blockers.append("execution_receipt_rune_authority_not_false")

    blockers.extend(_authority_expansion_blockers("execution_receipt", packet))
    return blockers


def _operator_disposition_contract(ready: bool) -> dict[str, Any]:
    return {
        "contract_id": (
            "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
            "operator_disposition_contract_001"
        ),
        "source_execution_receipt_hash": EXPECTED_EXECUTION_RECEIPT_HASH,
        "operator_review_gate_ready": ready,
        "operator_decision_required": True,
        "recommended_operator_decision": (
            "AUTHORIZE_SEPARATE_DECISION_RECORD_COMPLETION_RECEIPT"
            if ready
            else "HOLD_FOR_SOURCE_REPAIR"
        ),
        "authorized_future_lane": (
            NEXT_DECISION_RECORD_COMPLETION_RECEIPT_LANE if ready else NOT_COMPUTABLE
        ),
        "future_lane_authorization_only": ready,
        "decision_record_completion_performed": False,
        "decision_record_finalization_performed": False,
        "decision_record_emission_performed": False,
        "decision_record_materialization_performed": False,
        "writeback_performed": False,
        "package_lock_mutation_performed": False,
        "authority_denials": {
            "decision_record_completion_authorized_in_this_gate": False,
            "decision_record_completion_performed": False,
            "decision_record_finalization_authorized": False,
            "decision_record_emission_authorized": False,
            "decision_record_materialization_authorized": False,
            "notion_writeback_allowed": False,
            "github_writeback_allowed": False,
            "runtime_mutation": False,
            "canon_mutation": False,
            "queue_mutation": False,
            "scheduler_mutation": False,
            "v2_module_registration_authorized": False,
            "rune_registration_authorized": False,
            "brier_resolution_authorized": False,
            "forecast_routing_authorized": False,
            "adaptive_learning_authorized": False,
            "promotion_authorized": False,
            "package_lock_mutation_authorized": False,
            "execution_authority": False,
        },
    }


def _brier_scoring_contract(source: Mapping[str, Any]) -> dict[str, Any]:
    source_contract = source.get("brier_scoring_contract")
    hooks = (
        source_contract.get("telemetry_hooks")
        if isinstance(source_contract, Mapping)
        else []
    )
    return {
        "contract_id": (
            "v2_hygiene_phase1_stabilization_completion_validation_brier_"
            "telemetry_contract_operator_review_gate_001"
        ),
        "source_contract_id": (
            source_contract.get("contract_id", NOT_COMPUTABLE)
            if isinstance(source_contract, Mapping)
            else NOT_COMPUTABLE
        ),
        "telemetry_only": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "telemetry_hooks_observed_count": len(hooks) if isinstance(hooks, list) else 0,
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
            "governance_mapping": "Phase 3 execution receipt source state observation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": "execution receipt hash, schema, claim, and source linkage",
            "authority_granted": False,
            "risk_level": "MEDIUM",
        },
        {
            "rune": "Hold",
            "governance_mapping": "existing completion, writeback, promotion, and execution locks",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Weigh",
            "governance_mapping": "telemetry-only Brier review without resolution authority",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Seal",
            "governance_mapping": "future operator-approved decision-record completion receipt only",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate(
    repo_root: str | Path = ".",
    *,
    source_completion_validation_execution_receipt_path: str | Path = (
        SOURCE_EXECUTION_RECEIPT_JSON_PATH
    ),
) -> dict[str, Any]:
    root = Path(repo_root)
    execution_path = Path(source_completion_validation_execution_receipt_path)
    execution_receipt = _read_json(_resolve(root, execution_path)) or {}
    blockers = []
    if not execution_receipt:
        blockers.append("required_completion_validation_execution_receipt_missing")
    else:
        blockers.extend(_execution_receipt_blockers(execution_receipt))
    blockers = sorted(set(blockers))
    ready = bool(execution_receipt) and not blockers
    disposition_contract = _operator_disposition_contract(ready)
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": READY_STATUS if ready else BLOCKED_STATUS,
        "sources_observed": bool(execution_receipt),
        "source_records": [
            _source_record(
                "completion_validation_execution_receipt",
                execution_path,
                execution_receipt,
            )
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "operator_review_gate_ready": ready,
        "phase3_execution_receipt_hash_verified": ready,
        "phase3_claims_validated": ready,
        "operator_disposition_contract": disposition_contract,
        "brier_scoring_contract": _brier_scoring_contract(execution_receipt),
        "rune_governance_mapping": _rune_governance_mapping(),
        "selected_follow_on_action": (
            "AUTHORIZE_SEPARATE_DECISION_RECORD_COMPLETION_RECEIPT"
            if ready
            else "HOLD_FOR_PHASE3_EXECUTION_RECEIPT_REPAIR"
        ),
        "recommended_next_action": (
            "create a separate decision-record completion receipt lane; do not "
            "complete, finalize, emit, materialize, write back, register, activate, "
            "promote, resolve Brier outcomes, mutate package-lock, auto-continue, "
            "or execute in this gate"
            if ready
            else "restore the Phase 3 execution receipt before operator review"
        ),
        "recommended_next_lane": (
            NEXT_DECISION_RECORD_COMPLETION_RECEIPT_LANE if ready else NOT_COMPUTABLE
        ),
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
        "authority_locks": _copied_authority_locks(execution_receipt),
        "operator_review_gate_hash": "",
    }
    packet["operator_review_gate_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "operator_review_gate_hash"}
    )
    return packet


def render_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    disposition = packet["operator_disposition_contract"]
    brier_contract = packet["brier_scoring_contract"]
    lines = [
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Completion Validation Operator Review Gate",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- operator_review_gate_ready: {packet['operator_review_gate_ready']}",
        f"- phase3_execution_receipt_hash_verified: {packet['phase3_execution_receipt_hash_verified']}",
        f"- phase3_claims_validated: {packet['phase3_claims_validated']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- downstream: {packet['downstream']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- valid_for_decision_record_completion: {packet['valid_for_decision_record_completion']}",
        f"- valid_for_writeback: {packet['valid_for_writeback']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Operator Disposition Contract",
        f"- contract_id: {disposition['contract_id']}",
        f"- operator_decision_required: {disposition['operator_decision_required']}",
        f"- recommended_operator_decision: {disposition['recommended_operator_decision']}",
        f"- authorized_future_lane: {disposition['authorized_future_lane']}",
        f"- future_lane_authorization_only: {disposition['future_lane_authorization_only']}",
        f"- decision_record_completion_performed: {disposition['decision_record_completion_performed']}",
        f"- writeback_performed: {disposition['writeback_performed']}",
        "",
        "## Brier Scoring Contract",
        f"- contract_id: {brier_contract['contract_id']}",
        f"- telemetry_only: {brier_contract['telemetry_only']}",
        f"- telemetry_hooks_observed_count: {brier_contract['telemetry_hooks_observed_count']}",
        f"- resolution_allowed: {brier_contract['resolution_allowed']}",
        f"- adaptive_learning_authorized: {brier_contract['adaptive_learning_authorized']}",
        f"- forecast_routing_authorized: {brier_contract['forecast_routing_authorized']}",
        f"- promotion_authorized: {brier_contract['promotion_authorized']}",
        f"- brier_resolution_authorized: {brier_contract['brier_resolution_authorized']}",
        "",
        "## Rune Governance Mapping",
    ]
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


def write_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate(
        repo_root
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
