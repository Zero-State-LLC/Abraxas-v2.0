from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_promotion_closure_receipt import (
    RECEIPT_JSON_PATH as SOURCE_PROMOTION_CLOSURE_RECEIPT_JSON_PATH,
)

SCHEMA_VERSION = "V2HygienePhase2NextStabilizationSubsystemSelectionReceipt.v1"
RECEIPT_ID = "v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
NOT_COMPUTABLE = "NOT_COMPUTABLE"
READY_STATUS = "V2_HYGIENE_PHASE2_NEXT_STABILIZATION_SUBSYSTEM_SELECTION_RECEIPT_READY"
BLOCKED_STATUS = "V2_HYGIENE_PHASE2_NEXT_STABILIZATION_SUBSYSTEM_SELECTION_RECEIPT_BLOCKED"
EXPECTED_PHASE6_STATUS = "V2_HYGIENE_PHASE1_STABILIZATION_PROMOTION_CLOSURE_RECEIPT_READY"
EXPECTED_PHASE6_HASH = "f3ac209c98a7afcec10381db867fadcbd965de6cf77c01c4f964cbefbd610516"
PHASE6_CLASSIFICATION = "ADVISORY_COMPLETE_NOT_CANON_PROMOTED"
RECOMMENDED_OPERATOR_REVIEW_GATE = (
    "V2_HYGIENE_PHASE2_STABILIZATION_SUBSYSTEM_SELECTION_OPERATOR_REVIEW_GATE_001"
)

AUTHORITY_EXPANDING_FIELDS = (
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
    "activation_authorized",
    "runtime_activation_authorized",
    "canon_promotion_authorized",
    "brier_resolution_authorized",
    "package_lock_mutation_authorized",
    "v2_module_registration_authorized",
    "rune_registration_authorized",
    "authorization_record_created",
    "authorization_record_creation_authorized",
    "evidence_bundle_created",
    "evidence_bundle_creation_authorized",
    "operator_attestation_created",
    "operator_evidence_bundle_created",
    "operator_evidence_bundle_creation_authorized",
    "implementation_authorized",
    "valid_for_writeback",
    "valid_for_promotion",
    "valid_for_activation",
    "valid_for_execution",
    "valid_for_implementation",
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
        "auto_continuation": False,
        "brier_resolution": False,
        "canon_mutation": False,
        "execution_authority": False,
        "forecast_routing": False,
        "github_writeback": False,
        "notion_writeback": False,
        "package_lock_mutation": False,
        "promotion": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "v2_module_registration": False,
        "writeback": False,
    }


def _copied_authority_locks(source: Mapping[str, Any]) -> dict[str, bool]:
    locks = source.get("authority_locks")
    if _locks_all_false(locks):
        copied = {str(key): False for key in sorted(locks)}
        copied.setdefault("writeback", False)
        copied.setdefault("promotion", False)
        copied.setdefault("activation", False)
        copied.setdefault("package_lock_mutation", False)
        copied.setdefault("brier_resolution", False)
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
            if value is True
        )
    return blockers


def _source_record(source_id: str, path: Path, packet: Mapping[str, Any]) -> dict[str, Any]:
    contract = packet.get("promotion_closure_contract")
    return {
        "source_id": source_id,
        "path": path.as_posix(),
        "observed": bool(packet),
        "file_hash": _sha256(path),
        "packet_hash": str(packet.get("closure_receipt_hash", NOT_COMPUTABLE)),
        "expected_packet_hash": EXPECTED_PHASE6_HASH,
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_PHASE6_STATUS,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "source_blockers": packet.get("source_blockers", NOT_COMPUTABLE),
        "closure_claim_count": (
            contract.get("closure_claim_count", NOT_COMPUTABLE)
            if isinstance(contract, Mapping)
            else NOT_COMPUTABLE
        ),
        "closure_claims_finalized_count": (
            contract.get("closure_claims_finalized_count", NOT_COMPUTABLE)
            if isinstance(contract, Mapping)
            else NOT_COMPUTABLE
        ),
        "phase1_stabilization_advisory_complete": packet.get(
            "phase1_stabilization_advisory_complete"
        ),
        "promotion_readiness_classification": str(
            packet.get("promotion_readiness_classification", NOT_COMPUTABLE)
        ),
        "recommended_next_lane": str(packet.get("recommended_next_lane", NOT_COMPUTABLE)),
        "alternative_next_lane": str(packet.get("alternative_next_lane", NOT_COMPUTABLE)),
        "downstream": str(packet.get("downstream", NOT_COMPUTABLE)),
    }


def _phase6_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers = []
    if packet.get("status") != EXPECTED_PHASE6_STATUS:
        blockers.append("phase6_closure_receipt_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("phase6_source_not_ready")
    if packet.get("source_blockers") != []:
        blockers.append("phase6_source_blockers_not_empty")
    if packet.get("closure_receipt_ready") is not True:
        blockers.append("phase6_closure_receipt_ready_not_true")
    if packet.get("closure_receipt_hash") != EXPECTED_PHASE6_HASH:
        blockers.append("phase6_closure_receipt_hash_mismatch")
    packet_without_hash = dict(packet)
    observed_hash = packet_without_hash.pop("closure_receipt_hash", NOT_COMPUTABLE)
    if canonical_hash(packet_without_hash) != observed_hash:
        blockers.append("phase6_closure_receipt_self_hash_mismatch")
    if packet.get("phase1_stabilization_advisory_complete") is not True:
        blockers.append("phase6_advisory_complete_not_true")
    if packet.get("promotion_readiness_classification") != PHASE6_CLASSIFICATION:
        blockers.append("phase6_promotion_readiness_classification_mismatch")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("phase6_downstream_not_closed")
    if not _locks_all_false(packet.get("authority_locks")):
        blockers.append("phase6_authority_locks_not_false")

    contract = packet.get("promotion_closure_contract")
    if not isinstance(contract, Mapping):
        blockers.append("phase6_promotion_closure_contract_missing")
    else:
        if contract.get("closure_claim_count") != 5:
            blockers.append("phase6_closure_claim_count_not_five")
        if contract.get("closure_claims_finalized_count") != 5:
            blockers.append("phase6_closure_claims_not_finalized")
        if contract.get("phase1_stabilization_advisory_complete") is not True:
            blockers.append("phase6_contract_advisory_complete_not_true")
        if contract.get("promotion_readiness_classification") != PHASE6_CLASSIFICATION:
            blockers.append("phase6_contract_classification_mismatch")
        if not _locks_all_false(contract.get("authority_denials")):
            blockers.append("phase6_contract_authority_denials_not_false")
        claims = contract.get("closure_claims")
        if not isinstance(claims, list) or len(claims) != 5:
            blockers.append("phase6_closure_claims_missing")
        elif any(
            not isinstance(claim, Mapping)
            or claim.get("claim_finalized") is not True
            or claim.get("closure_status") != "CLOSURE_CLAIM_FINALIZED"
            for claim in claims
        ):
            blockers.append("phase6_closure_claim_not_finalized")

    brier_contract = packet.get("brier_scoring_contract")
    if not isinstance(brier_contract, Mapping):
        blockers.append("phase6_brier_contract_missing")
    else:
        if brier_contract.get("telemetry_only") is not True:
            blockers.append("phase6_brier_not_telemetry_only")
        for field in (
            "resolution_allowed",
            "adaptive_learning_authorized",
            "forecast_routing_authorized",
            "promotion_authorized",
            "execution_authority",
            "brier_resolution_authorized",
        ):
            if brier_contract.get(field) is not False:
                blockers.append(f"phase6_brier_authority_not_false:{field}")

    rune_mapping = packet.get("rune_governance_mapping")
    expected_runes = {"Observe", "Bind", "Hold", "Weigh", "Seal"}
    if not isinstance(rune_mapping, list):
        blockers.append("phase6_rune_mapping_missing")
    else:
        observed_runes = {
            str(mapping.get("rune"))
            for mapping in rune_mapping
            if isinstance(mapping, Mapping)
        }
        if observed_runes != expected_runes:
            blockers.append("phase6_rune_mapping_unexpected")
        if any(
            not isinstance(mapping, Mapping) or mapping.get("authority_granted") is not False
            for mapping in rune_mapping
        ):
            blockers.append("phase6_rune_authority_not_false")

    blockers.extend(_authority_expansion_blockers("phase6_closure_receipt", packet))
    return blockers


def _candidate_next_lane_matrix() -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": "writeback_authorization",
            "candidate_lane": (
                "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_"
                "WRITEBACK_AUTHORIZATION_RECEIPT_001"
            ),
            "candidate_type": "WRITEBACK_AUTHORIZATION",
            "provenance": "phase6.recommended_next_lane",
            "risk_level": "HIGH",
            "readiness": "ELIGIBLE_FOR_SEPARATE_OPERATOR_AUTHORIZATION",
            "selected_for_immediate_next_step": False,
            "authority_granted": False,
        },
        {
            "candidate_id": "canon_promotion_authorization",
            "candidate_lane": "V2_HYGIENE_PHASE1_STABILIZATION_PROMOTION_AUTHORIZATION_GATE_001",
            "candidate_type": "CANON_PROMOTION_AUTHORIZATION",
            "provenance": "phase6.alternative_next_lane",
            "risk_level": "HIGH",
            "readiness": "ELIGIBLE_FOR_SEPARATE_OPERATOR_AUTHORIZATION",
            "selected_for_immediate_next_step": False,
            "authority_granted": False,
        },
        {
            "candidate_id": "runtime_activation_planning",
            "candidate_lane": "V2_HYGIENE_PHASE2_RUNTIME_ACTIVATION_PLANNING_RECEIPT_001",
            "candidate_type": "RUNTIME_ACTIVATION_PLANNING",
            "provenance": "phase7.candidate_subsystem_map",
            "risk_level": "HIGH",
            "readiness": "REQUIRES_POST_SELECTION_OPERATOR_GATE",
            "selected_for_immediate_next_step": False,
            "authority_granted": False,
        },
        {
            "candidate_id": "package_lock_dependency_hygiene",
            "candidate_lane": "V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_RECEIPT_001",
            "candidate_type": "DEPENDENCY_HYGIENE",
            "provenance": "git.status.apps/aal-viz-live-console/package-lock.json",
            "risk_level": "MEDIUM",
            "readiness": "SEPARATE_FRONTIER_HYGIENE_RECEIPT_REQUIRED",
            "selected_for_immediate_next_step": False,
            "authority_granted": False,
        },
        {
            "candidate_id": "broader_subsystem_readiness_audit",
            "candidate_lane": "V2_HYGIENE_PHASE2_BROADER_SUBSYSTEM_READINESS_AUDIT_001",
            "candidate_type": "SUBSYSTEM_READINESS_AUDIT",
            "provenance": "README/PLANS post-phase1 advisory surfaces",
            "risk_level": "MEDIUM",
            "readiness": "ELIGIBLE_AFTER_SELECTION_OPERATOR_REVIEW",
            "selected_for_immediate_next_step": False,
            "authority_granted": False,
        },
    ]


def _selection_contract(ready: bool) -> dict[str, Any]:
    candidates = _candidate_next_lane_matrix()
    return {
        "contract_id": "v2_hygiene_phase2_next_stabilization_subsystem_selection_contract_001",
        "selection_receipt_authorized": ready,
        "selection_receipt_emitted": ready,
        "phase1_source_hash": EXPECTED_PHASE6_HASH if ready else NOT_COMPUTABLE,
        "phase1_stabilization_advisory_complete": ready,
        "phase1_promotion_readiness_classification": (
            PHASE6_CLASSIFICATION if ready else NOT_COMPUTABLE
        ),
        "candidate_next_lane_matrix": candidates if ready else [],
        "candidate_count": len(candidates) if ready else 0,
        "recommended_operator_review_gate": (
            RECOMMENDED_OPERATOR_REVIEW_GATE if ready else NOT_COMPUTABLE
        ),
        "selection_status": (
            "SELECTION_READY_FOR_SEPARATE_OPERATOR_REVIEW_GATE"
            if ready
            else "SELECTION_BLOCKED_BY_SOURCE"
        ),
        "authority_denials": {
            "notion_writeback_allowed": False,
            "github_writeback_allowed": False,
            "canon_promotion_authorized": False,
            "runtime_activation_authorized": False,
            "runtime_mutation": False,
            "canon_mutation": False,
            "queue_mutation": False,
            "scheduler_mutation": False,
            "v2_module_registration_authorized": False,
            "rune_registration_authorized": False,
            "brier_resolution_authorized": False,
            "forecast_routing_authorized": False,
            "adaptive_learning_authorized": False,
            "package_lock_mutation_authorized": False,
            "execution_authority": False,
            "auto_continuation_authorized": False,
        },
    }


def _brier_scoring_contract(candidates: list[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "contract_id": (
            "v2_hygiene_phase2_next_stabilization_subsystem_selection_"
            "brier_telemetry_contract_001"
        ),
        "telemetry_only": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "telemetry_hooks": [
            {
                "claim_id": f"{candidate['candidate_id']}_selection_readiness",
                "forecast_probability": 0.9,
                "binary_outcome": NOT_COMPUTABLE,
                "brier_score": NOT_COMPUTABLE,
                "resolution_source": NOT_COMPUTABLE,
                "resolution_allowed": False,
            }
            for candidate in candidates
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
            "governance_mapping": "Phase 6 closure receipt and next-lane candidate observation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": "Phase 6 hash, schema, and subsystem-selection lineage binding",
            "authority_granted": False,
            "risk_level": "MEDIUM",
        },
        {
            "rune": "Hold",
            "governance_mapping": "writeback, promotion, activation, mutation, package-lock, and execution locks",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Weigh",
            "governance_mapping": "telemetry-only Brier scoring for candidate readiness",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Seal",
            "governance_mapping": "advisory selection receipt only, not subsystem activation or canon promotion",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt(
    repo_root: str | Path = ".",
    *,
    source_phase6_promotion_closure_receipt_path: str | Path = (
        SOURCE_PROMOTION_CLOSURE_RECEIPT_JSON_PATH
    ),
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_phase6_promotion_closure_receipt_path)
    phase6 = _read_json(_resolve(root, source_path)) or {}
    blockers = []
    if not phase6:
        blockers.append("required_phase6_promotion_closure_receipt_missing")
    else:
        blockers.extend(_phase6_blockers(phase6))
    blockers = sorted(set(blockers))
    ready = bool(phase6) and not blockers
    selection_contract = _selection_contract(ready)
    candidates = selection_contract["candidate_next_lane_matrix"]
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": READY_STATUS if ready else BLOCKED_STATUS,
        "sources_observed": bool(phase6),
        "source_records": [
            _source_record("phase6_promotion_closure_receipt", source_path, phase6)
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "selection_receipt_ready": ready,
        "phase1_stabilization_advisory_complete_observed": ready,
        "phase1_promotion_readiness_classification": (
            PHASE6_CLASSIFICATION if ready else NOT_COMPUTABLE
        ),
        "next_stabilization_subsystem_selection_contract": selection_contract,
        "candidate_next_lane_matrix": candidates,
        "candidate_next_lane_count": len(candidates),
        "brier_scoring_contract": _brier_scoring_contract(candidates),
        "rune_governance_mapping": _rune_governance_mapping(),
        "selected_follow_on_action": (
            "HOLD_FOR_SEPARATE_SUBSYSTEM_SELECTION_OPERATOR_REVIEW_GATE"
            if ready
            else "HOLD_FOR_PHASE6_CLOSURE_RECEIPT_REPAIR"
        ),
        "recommended_next_action": (
            "create the separate Phase 7 subsystem-selection operator review gate; "
            "do not perform writeback, promotion, activation, dependency cleanup, "
            "Brier resolution, auto-continuation, or execution in this receipt"
            if ready
            else "restore the Phase 6 stabilization promotion closure receipt before selecting a next lane"
        ),
        "recommended_next_lane": RECOMMENDED_OPERATOR_REVIEW_GATE if ready else NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "downstream": NOT_COMPUTABLE,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "canon_promotion_authorized": False,
        "runtime_activation_authorized": False,
        "promotion_authorized": False,
        "activation_authorized": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "canon_mutation": False,
        "schema_mutation": False,
        "execution_authority": False,
        "forecast_routing_authorized": False,
        "adaptive_learning_authorized": False,
        "brier_resolution_authorized": False,
        "package_lock_mutation_authorized": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "authorization_record_created": False,
        "authorization_record_creation_authorized": False,
        "evidence_bundle_created": False,
        "evidence_bundle_creation_authorized": False,
        "operator_attestation_created": False,
        "operator_evidence_bundle_created": False,
        "operator_evidence_bundle_creation_authorized": False,
        "implementation_authorized": False,
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
        "authority_locks": _copied_authority_locks(phase6),
        "selection_receipt_hash": "",
    }
    packet["selection_receipt_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "selection_receipt_hash"}
    )
    return packet


def render_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    contract = packet["next_stabilization_subsystem_selection_contract"]
    brier_contract = packet["brier_scoring_contract"]
    lines = [
        "# v2.0 Hygiene Phase 2 Next Stabilization Subsystem Selection Receipt",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- selection_receipt_ready: {packet['selection_receipt_ready']}",
        f"- phase1_stabilization_advisory_complete_observed: {packet['phase1_stabilization_advisory_complete_observed']}",
        f"- phase1_promotion_readiness_classification: {packet['phase1_promotion_readiness_classification']}",
        f"- candidate_next_lane_count: {packet['candidate_next_lane_count']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- downstream: {packet['downstream']}",
        f"- valid_for_writeback: {packet['valid_for_writeback']}",
        f"- valid_for_promotion: {packet['valid_for_promotion']}",
        f"- valid_for_activation: {packet['valid_for_activation']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Selection Contract",
        f"- contract_id: {contract['contract_id']}",
        f"- selection_status: {contract['selection_status']}",
        f"- recommended_operator_review_gate: {contract['recommended_operator_review_gate']}",
        f"- candidate_count: {contract['candidate_count']}",
        "",
        "## Candidate Next-Lane Matrix",
    ]
    lines.extend(
        f"- {candidate['candidate_id']}: {candidate['candidate_lane']} "
        f"(type={candidate['candidate_type']}, risk={candidate['risk_level']}, "
        f"readiness={candidate['readiness']}, authority_granted={candidate['authority_granted']})"
        for candidate in packet["candidate_next_lane_matrix"]
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


def write_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
