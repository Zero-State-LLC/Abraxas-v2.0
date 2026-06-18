from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_completion_validation_operator_review_gate import (
    RECEIPT_JSON_PATH as SOURCE_OPERATOR_REVIEW_GATE_JSON_PATH,
)

SCHEMA_VERSION = "V2HygienePhase1StabilizationDecisionRecordCompletionReceipt.v1"
RECEIPT_ID = "v2_hygiene_phase1_stabilization_decision_record_completion_receipt_001"
RECORD_ID = "v2_hygiene_phase1_stabilization_decision_record_001"
RECORD_OUTPUT_PATH = "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_001.latest.json"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_receipt_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
NOT_COMPUTABLE = "NOT_COMPUTABLE"
READY_STATUS = "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_RECEIPT_READY"
BLOCKED_STATUS = "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_RECEIPT_BLOCKED"
EXPECTED_OPERATOR_REVIEW_GATE_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "OPERATOR_REVIEW_GATE_READY"
)
EXPECTED_OPERATOR_REVIEW_GATE_HASH = (
    "499532b0b4937fd0aece57f337fc830e03dae65a8fd9cc05b8c54bfbffd34edb"
)
EXPECTED_PHASE3_EXECUTION_RECEIPT_HASH = (
    "6ae90808a070f921c691a21437c68ff66854fcac7d988a337954ab69276fd13d"
)
EXPECTED_FUTURE_LANE = "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_RECEIPT_001"
NEXT_WRITEBACK_AUTHORIZATION_LANE = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_WRITEBACK_AUTHORIZATION_RECEIPT_001"
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
        copied.pop("decision_record_completion", None)
        copied.setdefault("brier_resolution", False)
        copied.setdefault("promotion", False)
        copied.setdefault("decision_record_materialization", False)
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
    disposition = packet.get("operator_disposition_contract")
    return {
        "source_id": source_id,
        "path": path.as_posix(),
        "observed": bool(packet),
        "file_hash": _sha256(path),
        "packet_hash": str(packet.get("operator_review_gate_hash", NOT_COMPUTABLE)),
        "expected_packet_hash": EXPECTED_OPERATOR_REVIEW_GATE_HASH,
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_OPERATOR_REVIEW_GATE_STATUS,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "phase3_execution_receipt_hash_verified": packet.get(
            "phase3_execution_receipt_hash_verified"
        ),
        "phase3_claims_validated": packet.get("phase3_claims_validated"),
        "recommended_next_lane": str(packet.get("recommended_next_lane", NOT_COMPUTABLE)),
        "downstream": str(packet.get("downstream", NOT_COMPUTABLE)),
        "operator_disposition_contract_observed": isinstance(disposition, Mapping),
        "recommended_operator_decision": (
            disposition.get("recommended_operator_decision", NOT_COMPUTABLE)
            if isinstance(disposition, Mapping)
            else NOT_COMPUTABLE
        ),
        "authorized_future_lane": (
            disposition.get("authorized_future_lane", NOT_COMPUTABLE)
            if isinstance(disposition, Mapping)
            else NOT_COMPUTABLE
        ),
    }


def _operator_review_gate_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers = []
    if packet.get("status") != EXPECTED_OPERATOR_REVIEW_GATE_STATUS:
        blockers.append("operator_review_gate_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("operator_review_gate_source_not_ready")
    if packet.get("operator_review_gate_ready") is not True:
        blockers.append("operator_review_gate_ready_not_true")
    if packet.get("operator_review_gate_hash") != EXPECTED_OPERATOR_REVIEW_GATE_HASH:
        blockers.append("operator_review_gate_hash_mismatch")
    packet_without_hash = dict(packet)
    observed_hash = packet_without_hash.pop("operator_review_gate_hash", NOT_COMPUTABLE)
    if canonical_hash(packet_without_hash) != observed_hash:
        blockers.append("operator_review_gate_self_hash_mismatch")
    if packet.get("source_blockers") != []:
        blockers.append("operator_review_gate_source_blockers_not_empty")
    if packet.get("phase3_execution_receipt_hash_verified") is not True:
        blockers.append("operator_review_gate_phase3_hash_not_verified")
    if packet.get("phase3_claims_validated") is not True:
        blockers.append("operator_review_gate_phase3_claims_not_validated")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("operator_review_gate_downstream_not_closed")
    if not _locks_all_false(packet.get("authority_locks")):
        blockers.append("operator_review_gate_locks_not_false")

    disposition = packet.get("operator_disposition_contract")
    if not isinstance(disposition, Mapping):
        blockers.append("operator_disposition_contract_missing")
    else:
        if disposition.get("recommended_operator_decision") != (
            "AUTHORIZE_SEPARATE_DECISION_RECORD_COMPLETION_RECEIPT"
        ):
            blockers.append("operator_disposition_not_authorizing_completion_receipt")
        if disposition.get("authorized_future_lane") != EXPECTED_FUTURE_LANE:
            blockers.append("operator_disposition_future_lane_mismatch")
        if disposition.get("future_lane_authorization_only") is not True:
            blockers.append("operator_disposition_future_lane_authorization_not_true")
        if disposition.get("decision_record_completion_performed") is not False:
            blockers.append("operator_disposition_completion_already_performed")
        if disposition.get("writeback_performed") is not False:
            blockers.append("operator_disposition_writeback_performed")
        if disposition.get("package_lock_mutation_performed") is not False:
            blockers.append("operator_disposition_package_lock_mutation_performed")
        if not _locks_all_false(disposition.get("authority_denials")):
            blockers.append("operator_disposition_authority_denials_not_false")

    brier_contract = packet.get("brier_scoring_contract")
    if not isinstance(brier_contract, Mapping):
        blockers.append("operator_review_gate_brier_contract_missing")
    else:
        if brier_contract.get("telemetry_only") is not True:
            blockers.append("operator_review_gate_brier_not_telemetry_only")
        if brier_contract.get("telemetry_hooks_observed_count") != 5:
            blockers.append("operator_review_gate_brier_hook_count_not_five")
        for field in (
            "resolution_allowed",
            "adaptive_learning_authorized",
            "forecast_routing_authorized",
            "promotion_authorized",
            "execution_authority",
            "brier_resolution_authorized",
        ):
            if brier_contract.get(field) is not False:
                blockers.append(f"operator_review_gate_brier_authority_not_false:{field}")

    rune_mapping = packet.get("rune_governance_mapping")
    expected_runes = {"Observe", "Bind", "Hold", "Weigh", "Seal"}
    if not isinstance(rune_mapping, list):
        blockers.append("operator_review_gate_rune_mapping_missing")
    else:
        observed_runes = {
            str(mapping.get("rune"))
            for mapping in rune_mapping
            if isinstance(mapping, Mapping)
        }
        if observed_runes != expected_runes:
            blockers.append("operator_review_gate_rune_mapping_unexpected")
        if any(
            not isinstance(mapping, Mapping) or mapping.get("authority_granted") is not False
            for mapping in rune_mapping
        ):
            blockers.append("operator_review_gate_rune_authority_not_false")

    for field in (
        "valid_for_writeback",
        "valid_for_execution",
        "safe_to_auto_continue",
        "brier_resolution_authorized",
        "promotion_authorized",
        "package_lock_mutation_authorized",
    ):
        if packet.get(field) is not False:
            blockers.append(f"operator_review_gate_authority_not_false:{field}")
    blockers.extend(_authority_expansion_blockers("operator_review_gate", packet))
    return blockers


def _completion_claims(ready: bool) -> list[dict[str, Any]]:
    base_claims = [
        {
            "claim_id": "operator_review_gate_ready",
            "claim": "Phase 4 operator-review gate is ready",
            "provenance": (
                "out/operator_review/"
                "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
                "operator_review_gate_001.latest.json#status"
            ),
            "risk_level": "LOW",
            "expected_value": EXPECTED_OPERATOR_REVIEW_GATE_STATUS,
            "observed_value": EXPECTED_OPERATOR_REVIEW_GATE_STATUS if ready else NOT_COMPUTABLE,
        },
        {
            "claim_id": "operator_review_gate_hash_pinned",
            "claim": "Phase 4 operator-review gate hash is pinned and verified",
            "provenance": "source_records.completion_validation_operator_review_gate.packet_hash",
            "risk_level": "LOW",
            "expected_value": EXPECTED_OPERATOR_REVIEW_GATE_HASH,
            "observed_value": EXPECTED_OPERATOR_REVIEW_GATE_HASH if ready else NOT_COMPUTABLE,
        },
        {
            "claim_id": "phase3_claims_validated",
            "claim": "Phase 3 execution receipt hash and five validation claims remain observed",
            "provenance": "operator_review_gate.source_records",
            "risk_level": "MEDIUM",
            "expected_value": "phase3_hash_verified=true; phase3_claims_validated=true",
            "observed_value": (
                "phase3_hash_verified=true; phase3_claims_validated=true"
                if ready
                else NOT_COMPUTABLE
            ),
        },
        {
            "claim_id": "operator_disposition_authorizes_completion_receipt",
            "claim": "Operator disposition authorizes only a separate completion receipt lane",
            "provenance": "operator_review_gate.operator_disposition_contract",
            "risk_level": "HIGH",
            "expected_value": "AUTHORIZE_SEPARATE_DECISION_RECORD_COMPLETION_RECEIPT",
            "observed_value": (
                "AUTHORIZE_SEPARATE_DECISION_RECORD_COMPLETION_RECEIPT"
                if ready
                else NOT_COMPUTABLE
            ),
        },
        {
            "claim_id": "non_completion_authorities_remain_denied",
            "claim": "Finalization, emission, materialization, writeback, promotion, Brier resolution, package-lock mutation, and execution remain denied",
            "provenance": "completion_receipt.authority_locks",
            "risk_level": "HIGH",
            "expected_value": "all non-completion authorities false",
            "observed_value": "all non-completion authorities false" if ready else NOT_COMPUTABLE,
        },
    ]
    return [
        {
            **claim,
            "claim_finalized": ready,
            "completion_status": "COMPLETION_CLAIM_FINALIZED" if ready else "BLOCKED",
            "fail_closed_blocker": "none" if ready else "source_not_ready",
        }
        for claim in base_claims
    ]


def _decision_record_completion_contract(ready: bool) -> dict[str, Any]:
    claims = _completion_claims(ready)
    return {
        "contract_id": "v2_hygiene_phase1_stabilization_decision_record_completion_contract_001",
        "record_id": RECORD_ID,
        "record_output_path": RECORD_OUTPUT_PATH,
        "completion_receipt_authorized": ready,
        "completion_receipt_emitted": ready,
        "decision_record_completed": ready,
        "completion_claims": claims,
        "completion_claim_count": len(claims),
        "completion_claims_finalized_count": sum(
            1 for claim in claims if claim["claim_finalized"] is True
        ),
        "completion_receipt_only": True,
        "authority_denials": {
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


def _brier_scoring_contract(claims: list[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "contract_id": (
            "v2_hygiene_phase1_stabilization_decision_record_completion_"
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
            "governance_mapping": "Phase 4 operator-review gate and source-chain observation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": "decision-record id, output path, schema, and source hash linkage",
            "authority_granted": False,
            "risk_level": "MEDIUM",
        },
        {
            "rune": "Hold",
            "governance_mapping": "finalization, emission, materialization, writeback, promotion, and execution locks",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Weigh",
            "governance_mapping": "telemetry-only Brier scoring without resolution authority",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Seal",
            "governance_mapping": "advisory decision-record completion receipt only",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase1_stabilization_decision_record_completion_receipt(
    repo_root: str | Path = ".",
    *,
    source_completion_validation_operator_review_gate_path: str | Path = (
        SOURCE_OPERATOR_REVIEW_GATE_JSON_PATH
    ),
) -> dict[str, Any]:
    root = Path(repo_root)
    gate_path = Path(source_completion_validation_operator_review_gate_path)
    gate = _read_json(_resolve(root, gate_path)) or {}
    blockers = []
    if not gate:
        blockers.append("required_completion_validation_operator_review_gate_missing")
    else:
        blockers.extend(_operator_review_gate_blockers(gate))
    blockers = sorted(set(blockers))
    ready = bool(gate) and not blockers
    completion_contract = _decision_record_completion_contract(ready)
    claims = completion_contract["completion_claims"]
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": READY_STATUS if ready else BLOCKED_STATUS,
        "sources_observed": bool(gate),
        "source_records": [
            _source_record(
                "completion_validation_operator_review_gate",
                gate_path,
                gate,
            )
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "completion_receipt_ready": ready,
        "record_id": RECORD_ID,
        "record_output_path": RECORD_OUTPUT_PATH,
        "decision_record_completion_contract": completion_contract,
        "completion_claims_finalized": ready,
        "brier_scoring_contract": _brier_scoring_contract(claims),
        "rune_governance_mapping": _rune_governance_mapping(),
        "selected_follow_on_action": (
            "HOLD_FOR_SEPARATE_WRITEBACK_AUTHORIZATION_RECEIPT"
            if ready
            else "HOLD_FOR_OPERATOR_REVIEW_GATE_REPAIR"
        ),
        "recommended_next_action": (
            "create a separate writeback authorization receipt only if operator wants "
            "Notion or GitHub status propagation; keep finalization, emission, "
            "materialization, runtime/canon/queue/scheduler mutation, registration, "
            "activation, promotion, Brier resolution, package-lock mutation, "
            "auto-continuation, and execution denied"
            if ready
            else "restore the Phase 4 operator-review gate before completing the decision record"
        ),
        "recommended_next_lane": NEXT_WRITEBACK_AUTHORIZATION_LANE if ready else NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "downstream": NOT_COMPUTABLE,
        "decision_record_created": False,
        "decision_record_creation_authorized": False,
        "decision_record_completed": ready,
        "decision_record_completion_authorized": ready,
        "decision_record_completion_receipt_emitted": ready,
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
        "valid_for_decision_record_completion": ready,
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
        "authority_locks": _copied_authority_locks(gate),
        "completion_receipt_hash": "",
    }
    packet["completion_receipt_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "completion_receipt_hash"}
    )
    return packet


def render_v2_hygiene_phase1_stabilization_decision_record_completion_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    completion_contract = packet["decision_record_completion_contract"]
    brier_contract = packet["brier_scoring_contract"]
    lines = [
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Completion Receipt",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- completion_receipt_ready: {packet['completion_receipt_ready']}",
        f"- record_id: {packet['record_id']}",
        f"- record_output_path: {packet['record_output_path']}",
        f"- decision_record_completed: {packet['decision_record_completed']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- downstream: {packet['downstream']}",
        f"- valid_for_decision_record_completion: {packet['valid_for_decision_record_completion']}",
        f"- valid_for_writeback: {packet['valid_for_writeback']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Completion Contract",
        f"- contract_id: {completion_contract['contract_id']}",
        f"- completion_receipt_authorized: {completion_contract['completion_receipt_authorized']}",
        f"- completion_receipt_emitted: {completion_contract['completion_receipt_emitted']}",
        f"- completion_claim_count: {completion_contract['completion_claim_count']}",
        f"- completion_claims_finalized_count: {completion_contract['completion_claims_finalized_count']}",
        f"- completion_receipt_only: {completion_contract['completion_receipt_only']}",
        "",
        "## Completion Claims",
    ]
    lines.extend(
        f"- {claim['claim_id']}: {claim['completion_status']} "
        f"(risk={claim['risk_level']}, provenance={claim['provenance']}, "
        f"blocker={claim['fail_closed_blocker']})"
        for claim in completion_contract["completion_claims"]
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


def write_v2_hygiene_phase1_stabilization_decision_record_completion_receipt(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_receipt(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_stabilization_decision_record_completion_receipt_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
