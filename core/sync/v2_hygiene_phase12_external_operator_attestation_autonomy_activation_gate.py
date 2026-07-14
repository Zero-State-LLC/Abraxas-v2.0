from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.scoring.brier import compute_brier_score
from core.sync.v2_hygiene_phase11_full_operator_execution_autonomy_gate import (
    FULL_OPERATOR_EXECUTION_AUTONOMY_MATRIX,
    RECEIPT_JSON_PATH as SOURCE_PHASE18_GATE_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygienePhase12ExternalOperatorAttestationAutonomyActivationGate.v1"
RECEIPT_ID = "v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
READY_STATUS = "V2_HYGIENE_PHASE12_EXTERNAL_OPERATOR_ATTESTATION_AUTONOMY_ACTIVATION_GATE_READY"
HELD_STATUS = (
    "V2_HYGIENE_PHASE12_EXTERNAL_OPERATOR_ATTESTATION_AUTONOMY_ACTIVATION_GATE_HELD_FOR_ATTESTATION"
)
BLOCKED_STATUS = "V2_HYGIENE_PHASE12_EXTERNAL_OPERATOR_ATTESTATION_AUTONOMY_ACTIVATION_GATE_BLOCKED"
EXPECTED_PHASE18_STATUS = "V2_HYGIENE_PHASE11_FULL_OPERATOR_EXECUTION_AUTONOMY_GATE_READY"
EXPECTED_PHASE18_HASH = "402cce6cbf0cb1abf108d79eae2047fa78bc45bb4f7da02852a184f01b53ae07"
PHASE18_HANDOFF_TEMPLATE_PATH = Path(
    "operator_input/templates/phase18_full_operator_execution_autonomy_handoff.md"
)
DEFAULT_ATTESTATION_PAYLOAD_PATH = Path(
    "operator_input/v2_hygiene_phase19_external_operator_attestation_autonomy_payload_001.json"
)
OPERATOR_PHASE_NUMBER = 19

AUTONOMY_ACTIVATION_PROMOTION_CLASSES = {
    "rune_visualization_layer": "OPERATOR_EXECUTION_AUTONOMY_RUNE_VIZ_ACTIVATION_RECORDED",
    "incarnation_core_planning_binding": (
        "OPERATOR_EXECUTION_AUTONOMY_INCARNATION_CORE_ACTIVATION_RECORDED"
    ),
    "planning_lane_outputs": "OPERATOR_EXECUTION_AUTONOMY_PLANNING_LANE_ACTIVATION_RECORDED",
    "core_oracle_shadow": "OPERATOR_EXECUTION_AUTONOMY_ORACLE_SHADOW_ACTIVATION_RECORDED",
    "brier_engine_telemetry": "OPERATOR_EXECUTION_AUTONOMY_BRIER_TELEMETRY_ACTIVATION_RECORDED",
}

REQUIRED_ATTESTATION_GROUPS = (
    "operator_identity",
    "phase18_hash_chain_acknowledgement",
    "autonomy_surface_disposition",
    "authority_boundary_acknowledgement",
    "terminal_output_controls",
)

REQUIRED_ATTESTATION_FIELDS: dict[str, tuple[str, ...]] = {
    "operator_identity": (
        "operator_id",
        "operator_reviewed_at_source_observed",
        "operator_attestation_hash",
    ),
    "phase18_hash_chain_acknowledgement": (
        "phase18_gate_path",
        "phase18_gate_hash",
        "autonomy_eligibility_acknowledged",
    ),
    "autonomy_surface_disposition": (
        "rune_visualization_layer_acknowledged",
        "incarnation_core_planning_binding_acknowledged",
        "planning_lane_outputs_acknowledged",
        "core_oracle_shadow_acknowledged",
        "brier_engine_telemetry_acknowledged",
    ),
    "authority_boundary_acknowledgement": (
        "no_execution_authority_auto_grant",
        "no_package_lock_mutation",
        "no_toolchain_provisioning",
        "no_notion_writeback",
        "brier_resolution_denied",
    ),
    "terminal_output_controls": (
        "downstream_lane_disposition",
        "rollback_or_supersession_policy",
    ),
}

TRUE_ATTESTATION_FIELDS = {
    "autonomy_eligibility_acknowledged",
    "rune_visualization_layer_acknowledged",
    "incarnation_core_planning_binding_acknowledged",
    "planning_lane_outputs_acknowledged",
    "core_oracle_shadow_acknowledged",
    "brier_engine_telemetry_acknowledged",
    "no_execution_authority_auto_grant",
    "no_package_lock_mutation",
    "no_toolchain_provisioning",
    "no_notion_writeback",
    "brier_resolution_denied",
}

EXPECTED_ATTESTATION_LITERALS = {
    "phase18_gate_path": SOURCE_PHASE18_GATE_JSON_PATH.as_posix(),
    "phase18_gate_hash": EXPECTED_PHASE18_HASH,
    "downstream_lane_disposition": NOT_COMPUTABLE,
    "rollback_or_supersession_policy": "fresh governed operator attestation required",
}

AUTHORITY_EXPANDING_FIELDS = (
    "notion_writeback_allowed",
    "github_writeback_allowed",
    "canon_promotion_authorized",
    "runtime_activation_authorized",
    "runtime_mutation",
    "queue_mutation",
    "scheduler_mutation",
    "canon_mutation",
    "execution_authority",
    "forecast_routing_authorized",
    "adaptive_learning_authorized",
    "promotion_authorized",
    "activation_authorized",
    "brier_resolution_authorized",
    "rune_registration_authorized",
    "implementation_authorized",
    "valid_for_writeback",
    "valid_for_promotion",
    "valid_for_activation",
    "valid_for_execution",
    "valid_for_implementation",
    "safe_to_auto_continue",
    "package_lock_mutation_authorized",
    "toolchain_provisioning_authorized",
    "dependency_mutation_authorized",
    "uncontrolled_writeback_authorized",
    "full_operator_execution_autonomy_authorized",
    "operator_execution_autonomy_authorized",
    "operator_attestation_created",
    "phase20_activation_authorized",
    "operator_signoff_auto_approved",
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


def _path_observed(repo_root: Path, path: str) -> bool:
    return (repo_root / path).exists()


def _locks_all_false(value: Any) -> bool:
    return isinstance(value, Mapping) and bool(value) and all(
        item is False for item in value.values()
    )


def _copied_authority_locks(source: Mapping[str, Any]) -> dict[str, bool]:
    locks = source.get("authority_locks")
    if _locks_all_false(locks):
        copied = {str(key): False for key in sorted(locks)}
    else:
        copied = {}
    for key in (
        "activation",
        "adaptive_learning",
        "auto_continuation",
        "brier_resolution",
        "canon_mutation",
        "controlled_execution_promotion",
        "controlled_writeback",
        "dependency_mutation",
        "execution_authority",
        "execution_surface_expansion",
        "external_operator_attestation",
        "forecast_routing",
        "full_operator_execution_autonomy",
        "github_writeback",
        "notion_writeback",
        "operator_execution_autonomy",
        "package_lock_mutation",
        "planning_lane_execution",
        "promotion",
        "queue_mutation",
        "rune_registration",
        "rune_viz_integration",
        "runtime_mutation",
        "scheduler_mutation",
        "toolchain_provisioning",
        "uncontrolled_writeback",
        "writeback",
    ):
        copied.setdefault(key, False)
    return copied


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
    return {
        "source_id": source_id,
        "path": path.as_posix(),
        "observed": bool(packet),
        "file_hash": _sha256(path),
        "packet_hash": str(packet.get("full_operator_execution_autonomy_gate_hash", NOT_COMPUTABLE)),
        "expected_packet_hash": EXPECTED_PHASE18_HASH,
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_PHASE18_STATUS,
        "authority_locks_all_false": (
            True
            if packet.get("authority_locks") is None
            else _locks_all_false(packet.get("authority_locks"))
        ),
        "valid_for_operator_execution_autonomy_eligibility": packet.get(
            "valid_for_operator_execution_autonomy_eligibility", NOT_COMPUTABLE
        ),
        "external_operator_attestation_required": packet.get(
            "external_operator_attestation_required", NOT_COMPUTABLE
        ),
        "operator_review_posture": packet.get("operator_review_posture", NOT_COMPUTABLE),
        "recommended_next_lane": packet.get("recommended_next_lane", NOT_COMPUTABLE),
        "downstream": packet.get("downstream", NOT_COMPUTABLE),
    }


def _phase18_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if packet.get("status") != EXPECTED_PHASE18_STATUS:
        blockers.append("phase18_full_operator_execution_autonomy_gate_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("phase18_source_not_ready")
    if packet.get("source_blockers") != []:
        blockers.append("phase18_source_blockers_not_empty")
    if packet.get("full_operator_execution_autonomy_gate_ready") is not True:
        blockers.append("phase18_full_operator_execution_autonomy_gate_ready_not_true")
    if packet.get("full_operator_execution_autonomy_gate_hash") != EXPECTED_PHASE18_HASH:
        blockers.append("phase18_full_operator_execution_autonomy_gate_hash_mismatch")
    without_hash = dict(packet)
    observed_hash = without_hash.pop("full_operator_execution_autonomy_gate_hash", NOT_COMPUTABLE)
    if canonical_hash(without_hash) != observed_hash:
        blockers.append("phase18_full_operator_execution_autonomy_gate_self_hash_mismatch")
    if packet.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append("phase18_recommended_lane_mismatch")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("phase18_downstream_not_closed")
    if packet.get("planning_lane_activated") is not True:
        blockers.append("phase18_planning_lane_not_activated")
    if packet.get("operator_review_posture") != "ACTIVE":
        blockers.append("phase18_operator_review_posture_not_active")
    if packet.get("valid_for_execution") is True:
        blockers.append("phase18_execution_authority_not_denied")
    if packet.get("valid_for_operator_execution_autonomy_eligibility") is not True:
        blockers.append("phase18_operator_execution_autonomy_not_eligible")
    if packet.get("external_operator_attestation_required") is not True:
        blockers.append("phase18_external_operator_attestation_not_required")
    locks = packet.get("authority_locks")
    if locks is not None and not _locks_all_false(locks):
        blockers.append("phase18_authority_locks_not_false")
    blockers.extend(_authority_expansion_blockers("phase18_full_operator_execution_autonomy_gate", packet))
    return blockers


def _attestation_group_blockers(group_id: str, group: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for field in REQUIRED_ATTESTATION_FIELDS[group_id]:
        if field not in group:
            blockers.append(f"{group_id}.{field}_missing")
            continue
        value = group[field]
        if field in TRUE_ATTESTATION_FIELDS and value is not True:
            blockers.append(f"{group_id}.{field}_must_be_true")
        if field in EXPECTED_ATTESTATION_LITERALS and value != EXPECTED_ATTESTATION_LITERALS[field]:
            blockers.append(f"{group_id}.{field}_unexpected_value")
        if field in {
            "operator_id",
            "operator_reviewed_at_source_observed",
            "operator_attestation_hash",
        } and not (isinstance(value, str) and value.strip()):
            blockers.append(f"{group_id}.{field}_blank")
    return blockers


def _external_operator_attestation_contract(payload: Mapping[str, Any], *, observed: bool) -> dict[str, Any]:
    group_records: list[dict[str, Any]] = []
    missing_group_blockers: list[str] = []
    field_blockers: list[str] = []
    for group_id in REQUIRED_ATTESTATION_GROUPS:
        group = payload.get(group_id)
        group_observed = isinstance(group, Mapping)
        if not group_observed:
            missing_group_blockers.append(f"{group_id}_missing")
        blockers = _attestation_group_blockers(group_id, group) if group_observed else [f"{group_id}_missing"]
        field_blockers.extend(blockers if group_observed else [])
        group_records.append(
            {
                "group_id": group_id,
                "group_observed": group_observed,
                "required_fields": list(REQUIRED_ATTESTATION_FIELDS[group_id]),
                "field_blockers": blockers,
                "group_validated": group_observed and not blockers,
                "authority_granted": False,
            }
        )
    authority_blockers = _authority_expansion_blockers("attestation_payload", payload)
    payload_complete = observed and all(record["group_validated"] is True for record in group_records)
    return {
        "contract_id": "v2_hygiene_phase12_external_operator_attestation_contract_001",
        "attestation_payload_path": DEFAULT_ATTESTATION_PAYLOAD_PATH.as_posix(),
        "attestation_payload_observed": observed,
        "required_attestation_groups": list(REQUIRED_ATTESTATION_GROUPS),
        "attestation_group_records": group_records,
        "missing_group_blockers": missing_group_blockers,
        "field_blockers": sorted(set(field_blockers)),
        "authority_expansion_blockers": authority_blockers,
        "attestation_payload_validated": payload_complete and not authority_blockers,
        "operator_attestation_created": False,
        "operator_attestation_recorded_externally": payload_complete,
    }


def _autonomy_activation_contract(
    repo_root: Path,
    *,
    activation_recorded: bool,
) -> dict[str, Any]:
    surfaces = []
    for entry in FULL_OPERATOR_EXECUTION_AUTONOMY_MATRIX:
        path_observations = [
            {
                "path": path,
                "observed": _path_observed(repo_root, path),
                "file_hash": _sha256(repo_root / path) if _path_observed(repo_root, path) else NOT_COMPUTABLE,
            }
            for path in entry["paths"]
        ]
        surface_id = entry["surface_id"]
        surfaces.append(
            {
                "surface_id": surface_id,
                "paths": list(entry["paths"]),
                "prior_promotion_class": entry["promotion_class"],
                "promotion_class": AUTONOMY_ACTIVATION_PROMOTION_CLASSES[surface_id],
                "write_posture": (
                    "operator_execution_autonomy_activation_recorded_pending_external_authority"
                    if activation_recorded
                    else "operator_execution_autonomy_activation_pending_attestation"
                ),
                "path_observations": path_observations,
                "all_paths_observed": all(item["observed"] for item in path_observations),
                "autonomy_eligible": True,
                "autonomy_activation_recorded": activation_recorded,
                "autonomy_authorized": False,
                "authority_granted": False,
                "operator_attestation_required": True,
            }
        )
    return {
        "contract_id": "v2_hygiene_phase12_autonomy_activation_contract_001",
        "autonomy_activation_matrix": surfaces,
        "surface_count": len(surfaces),
        "autonomy_activation_recorded_count": sum(
            1 for surface in surfaces if surface["autonomy_activation_recorded"] is True
        ),
        "full_operator_execution_autonomy_authorized": False,
        "operator_execution_autonomy_authorized": False,
        "execution_authority_granted": False,
    }


def _autonomy_eligibility_inheritance_contract(phase18: Mapping[str, Any]) -> dict[str, Any]:
    autonomy = phase18.get("full_operator_execution_autonomy_contract", {})
    matrix = autonomy.get("full_operator_execution_autonomy_matrix", [])
    return {
        "contract_id": "v2_hygiene_phase12_autonomy_eligibility_inheritance_contract_001",
        "inherited_from": "v2_hygiene_phase11_full_operator_execution_autonomy_gate_001",
        "inherited_autonomy_eligible_surfaces": matrix if isinstance(matrix, list) else [],
        "surface_count": len(matrix) if isinstance(matrix, list) else 0,
        "full_operator_execution_autonomy_authorized": False,
    }


def _operator_attestation_workflow_contract(*, ready: bool, attestation_validated: bool) -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase12_operator_attestation_workflow_contract_001",
        "manual_operator_signoff_required": True,
        "operator_signoff_auto_approved": False,
        "external_operator_attestation_required": True,
        "external_operator_attestation_validated": attestation_validated,
        "phase18_handoff_template_path": PHASE18_HANDOFF_TEMPLATE_PATH.as_posix(),
        "notion_writeback_allowed": False,
        "hash_chain_review_required": True,
        "hash_chain": {
            "phase18_gate_hash": EXPECTED_PHASE18_HASH if ready else NOT_COMPUTABLE,
            "phase19_gate_hash": NOT_COMPUTABLE,
        },
        "claims": [
            {
                "field": "phase18_hash_chain_reviewed",
                "classification": "OBSERVED" if ready else "INFERRED",
                "provenance": SOURCE_PHASE18_GATE_JSON_PATH.as_posix(),
                "value": ready,
            },
            {
                "field": "external_operator_attestation_payload_validated",
                "classification": "OBSERVED" if attestation_validated else "SPECULATIVE",
                "provenance": DEFAULT_ATTESTATION_PAYLOAD_PATH.as_posix(),
                "value": attestation_validated,
            },
            {
                "field": "execution_authority_remains_gate_denied",
                "classification": "OBSERVED",
                "provenance": RECEIPT_ID,
                "value": True,
            },
        ],
    }


def _dependency_denial_contract() -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase12_dependency_denial_contract_001",
        "package_lock_mutation_authorized": False,
        "package_lock_tracking_authorized": False,
        "toolchain_provisioning_authorized": False,
        "dependency_mutation_authorized": False,
        "npmrc_stabilization_observed": (Path(".") / "apps/aal-viz-live-console/.npmrc").exists(),
        "package_lock_resolution_held": True,
        "high_risk_mutations_denied": True,
    }


def _brier_scoring_contract() -> dict[str, Any]:
    hooks = [
        {
            "claim_id": surface_id,
            "forecast_probability": 0.88,
            "binary_outcome": NOT_COMPUTABLE,
            "brier_score": NOT_COMPUTABLE,
            "resolution_source": NOT_COMPUTABLE,
            "resolution_allowed": False,
        }
        for surface_id in AUTONOMY_ACTIVATION_PROMOTION_CLASSES
    ]
    hooks.append(
        {
            "claim_id": "operator_execution_autonomy_activation_without_gate_execution_authority",
            "forecast_probability": compute_brier_score(0.84, 0.0),
            "binary_outcome": NOT_COMPUTABLE,
            "brier_score": NOT_COMPUTABLE,
            "resolution_source": "core/governance/brier_provenance.py",
            "resolution_allowed": False,
        }
    )
    return {
        "contract_id": "v2_hygiene_phase12_external_operator_attestation_autonomy_brier_telemetry_contract_001",
        "telemetry_only": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "telemetry_hooks": hooks,
        "resolution_allowed": False,
        "brier_resolution_authorized": False,
    }


def _rune_governance_mapping() -> list[dict[str, Any]]:
    return [
        {
            "rune": "Observe",
            "governance_mapping": "Phase 18 autonomy gate and external attestation payload observation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": "Phase 18 hash linkage and autonomy surface activation binding",
            "authority_granted": False,
            "risk_level": "MEDIUM",
        },
        {
            "rune": "Hold",
            "governance_mapping": "package-lock, toolchain, dependency mutations, and gate execution authority held",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Weigh",
            "governance_mapping": "telemetry-only Brier posture for autonomy activation eligibility",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Seal",
            "governance_mapping": "Phase 19 attestation gate only; external operator attestation required",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate(
    repo_root: str | Path = ".",
    *,
    source_phase18_gate_path: str | Path = SOURCE_PHASE18_GATE_JSON_PATH,
    attestation_payload_path: str | Path = DEFAULT_ATTESTATION_PAYLOAD_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_phase18_gate_path)
    payload_path = Path(attestation_payload_path)
    phase18 = _read_json(_resolve(root, source_path)) or {}
    payload = _read_json(_resolve(root, payload_path))
    blockers: list[str] = []
    if not phase18:
        blockers.append("required_phase18_full_operator_execution_autonomy_gate_missing")
    else:
        blockers.extend(_phase18_blockers(phase18))
    if not (root / PHASE18_HANDOFF_TEMPLATE_PATH).exists():
        blockers.append("phase18_handoff_template_missing")
    payload_observed = payload is not None
    attestation_contract = _external_operator_attestation_contract(payload or {}, observed=payload_observed)
    if not payload_observed:
        blockers.append("external_operator_attestation_payload_missing")
    else:
        blockers.extend(attestation_contract["missing_group_blockers"])
        blockers.extend(attestation_contract["field_blockers"])
        blockers.extend(attestation_contract["authority_expansion_blockers"])
    activation_contract = _autonomy_activation_contract(
        root,
        activation_recorded=attestation_contract["attestation_payload_validated"],
    )
    for surface in activation_contract["autonomy_activation_matrix"]:
        if not surface["all_paths_observed"]:
            blockers.append(f"autonomy_activation_surface_path_missing:{surface['surface_id']}")
    blockers = sorted(set(blockers))
    phase18_ready = bool(phase18) and not any(
        blocker.startswith("phase18_")
        or blocker.startswith("required_phase18")
        or blocker == "phase18_handoff_template_missing"
        for blocker in blockers
    )
    attestation_validated = attestation_contract["attestation_payload_validated"]
    if phase18_ready and not payload_observed:
        status = HELD_STATUS
        gate_ready = False
    elif phase18_ready and attestation_validated:
        status = READY_STATUS
        gate_ready = True
    else:
        status = BLOCKED_STATUS
        gate_ready = False
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "operator_phase_number": OPERATOR_PHASE_NUMBER,
        "status": status,
        "sources_observed": bool(phase18),
        "source_records": [
            _source_record(
                "phase18_full_operator_execution_autonomy_gate",
                source_path,
                phase18,
            )
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if phase18_ready else "SOURCE_ARTIFACTS_NOT_READY",
        "external_operator_attestation_autonomy_activation_gate_ready": gate_ready,
        "phase18_full_operator_execution_autonomy_gate_hash_verified": phase18_ready,
        "planning_lane_status": phase18.get("planning_lane_status", NOT_COMPUTABLE) if phase18 else NOT_COMPUTABLE,
        "planning_lane_activated": phase18.get("planning_lane_activated", False) if phase18 else False,
        "attestation_payload_observed": payload_observed,
        "attestation_payload_validated": attestation_validated,
        "external_operator_attestation_recorded": attestation_validated,
        "external_operator_attestation_contract": attestation_contract,
        "autonomy_activation_contract": activation_contract,
        "autonomy_eligibility_inheritance_contract": _autonomy_eligibility_inheritance_contract(phase18),
        "operator_attestation_workflow_contract": _operator_attestation_workflow_contract(
            ready=phase18_ready,
            attestation_validated=attestation_validated,
        ),
        "dependency_denial_contract": _dependency_denial_contract(),
        "brier_scoring_contract": _brier_scoring_contract(),
        "rune_governance_mapping": _rune_governance_mapping(),
        "recommended_next_action": (
            "external operator attestation recorded for eligible surfaces; gate does not grant execution "
            "authority; package-lock and high-risk mutations remain fail-closed"
            if gate_ready
            else (
                "collect and validate external operator attestation payload before autonomy activation"
                if phase18_ready and not payload_observed
                else "restore the Phase 18 full operator execution autonomy gate before attestation"
            )
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "downstream": NOT_COMPUTABLE,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "promotion_authorized": False,
        "full_operator_execution_autonomy_authorized": False,
        "operator_execution_autonomy_authorized": False,
        "activation_authorized": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "canon_mutation": False,
        "execution_authority": False,
        "brier_resolution_authorized": False,
        "rune_registration_authorized": False,
        "implementation_authorized": False,
        "package_lock_mutation_authorized": False,
        "toolchain_provisioning_authorized": False,
        "dependency_mutation_authorized": False,
        "valid_for_planning_lane": phase18_ready,
        "valid_for_controlled_writeback": phase18_ready,
        "valid_for_controlled_execution": phase18_ready,
        "valid_for_rune_viz_integration": phase18_ready,
        "valid_for_operator_execution_autonomy_eligibility": phase18_ready,
        "valid_for_operator_execution_autonomy_activation": gate_ready,
        "valid_for_execution": False,
        "valid_for_promotion": False,
        "valid_for_activation": False,
        "operator_signoff_auto_approved": False,
        "external_operator_attestation_required": True,
        "operator_review_posture": "ACTIVE",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "authority_locks": _copied_authority_locks(phase18),
        "external_operator_attestation_autonomy_activation_gate_hash": "",
    }
    packet["external_operator_attestation_autonomy_activation_gate_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "external_operator_attestation_autonomy_activation_gate_hash"
        }
    )
    return packet


def render_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    activation = packet["autonomy_activation_contract"]
    denial = packet["dependency_denial_contract"]
    workflow = packet["operator_attestation_workflow_contract"]
    attestation = packet["external_operator_attestation_contract"]
    lines = [
        "# v2.0 Hygiene Phase 12 External Operator Attestation Autonomy Activation Gate (Operator Phase 19)",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- operator_phase_number: {packet['operator_phase_number']}",
        f"- status: {packet['status']}",
        f"- attestation_payload_observed: {packet['attestation_payload_observed']}",
        f"- attestation_payload_validated: {packet['attestation_payload_validated']}",
        f"- valid_for_operator_execution_autonomy_activation: {packet['valid_for_operator_execution_autonomy_activation']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- operator_review_posture: {packet['operator_review_posture']}",
        "",
        "## Hash Chain",
        f"- phase18_gate_hash: {workflow['hash_chain']['phase18_gate_hash']}",
        f"- phase19_gate_hash: {workflow['hash_chain']['phase19_gate_hash']}",
        "",
        "## Autonomy Activation Matrix",
    ]
    for surface in activation["autonomy_activation_matrix"]:
        lines.append(
            f"- {surface['surface_id']}: {surface['promotion_class']} "
            f"activation_recorded={surface['autonomy_activation_recorded']}"
        )
    lines.extend(
        [
            "",
            "## Attestation Contract",
            f"- attestation_payload_validated: {attestation['attestation_payload_validated']}",
            f"- attested_groups: {sum(1 for record in attestation['attestation_group_records'] if record['group_validated'])}",
            "",
            "## Dependency Denial Contract",
            f"- package_lock_mutation_authorized: {denial['package_lock_mutation_authorized']}",
            f"- high_risk_mutations_denied: {denial['high_risk_mutations_denied']}",
            "",
            "## Source Blockers",
        ]
    )
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
    source_phase18_gate_path: str | Path = SOURCE_PHASE18_GATE_JSON_PATH,
    attestation_payload_path: str | Path = DEFAULT_ATTESTATION_PAYLOAD_PATH,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate(
        repo_root,
        source_phase18_gate_path=source_phase18_gate_path,
        attestation_payload_path=attestation_payload_path,
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase12_external_operator_attestation_autonomy_activation_gate_markdown(packet)
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
