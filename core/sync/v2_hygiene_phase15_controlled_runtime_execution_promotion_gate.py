from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.governance.brier_provenance import (
    build_brier_controlled_runtime_promotion_packet,
    build_brier_decomposition_fixture,
    validate_adversarial_calibration,
)
from core.governance.signal_forager_brier_hook import build_signal_forager_brier_contract
from core.scoring.brier import DECOMPOSITION_MODE, NOT_COMPUTABLE, compute_brier_score, compute_full_decomposition
from core.sync.v2_hygiene_phase11_full_operator_execution_autonomy_gate import (
    FULL_OPERATOR_EXECUTION_AUTONOMY_MATRIX,
)
from core.sync.v2_hygiene_phase14_runtime_execution_surface_activation_gate import (
    RECEIPT_JSON_PATH as SOURCE_PHASE21_GATE_JSON_PATH,
    RUNTIME_EXECUTION_ACTIVATION_PROMOTION_CLASSES,
)

SCHEMA_VERSION = "V2HygienePhase15ControlledRuntimeExecutionPromotionGate.v1"
RECEIPT_ID = "v2_hygiene_phase15_controlled_runtime_execution_promotion_gate_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase15_controlled_runtime_execution_promotion_gate_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
READY_STATUS = "V2_HYGIENE_PHASE15_CONTROLLED_RUNTIME_EXECUTION_PROMOTION_GATE_READY"
BLOCKED_STATUS = "V2_HYGIENE_PHASE15_CONTROLLED_RUNTIME_EXECUTION_PROMOTION_GATE_BLOCKED"
EXPECTED_PHASE21_STATUS = "V2_HYGIENE_PHASE14_RUNTIME_EXECUTION_SURFACE_ACTIVATION_GATE_READY"
EXPECTED_PHASE21_HASH = "f805bebd123170457e1bcacad2584eb5988882392be9c0742c74aad6b1f71d98"
PHASE21_HANDOFF_TEMPLATE_PATH = Path(
    "operator_input/templates/phase21_runtime_execution_surface_activation_handoff.md"
)
OPERATOR_PHASE_NUMBER = 22

CONTROLLED_RUNTIME_EXECUTION_PROMOTION_CLASSES = {
    "rune_visualization_layer": (
        "OPERATOR_EXECUTION_AUTONOMY_RUNE_VIZ_CONTROLLED_RUNTIME_EXECUTION_PROMOTION_RECORDED"
    ),
    "incarnation_core_planning_binding": (
        "OPERATOR_EXECUTION_AUTONOMY_INCARNATION_CORE_CONTROLLED_RUNTIME_EXECUTION_PROMOTION_RECORDED"
    ),
    "planning_lane_outputs": (
        "OPERATOR_EXECUTION_AUTONOMY_PLANNING_LANE_CONTROLLED_RUNTIME_EXECUTION_PROMOTION_RECORDED"
    ),
    "core_oracle_shadow": (
        "OPERATOR_EXECUTION_AUTONOMY_ORACLE_SHADOW_CONTROLLED_RUNTIME_EXECUTION_PROMOTION_RECORDED"
    ),
    "brier_engine_telemetry": (
        "OPERATOR_EXECUTION_AUTONOMY_BRIER_TELEMETRY_CONTROLLED_RUNTIME_EXECUTION_PROMOTION_RECORDED"
    ),
}

LIMITED_WRITE_ALLOWED_BY_SURFACE = {
    "rune_visualization_layer": True,
    "incarnation_core_planning_binding": True,
    "planning_lane_outputs": True,
    "core_oracle_shadow": True,
    "brier_engine_telemetry": False,
}

RUNTIME_GUARD_FIELDS = (
    "execution_authority_denied",
    "brier_resolution_denied",
    "package_lock_mutation_denied",
    "toolchain_provisioning_denied",
    "notion_writeback_denied",
    "uncontrolled_runtime_mutation_denied",
    "operator_signoff_required",
    "controlled_runtime_write_only",
    "uncontrolled_execution_denied",
)

BRIER_CONTROLLED_RUNTIME_FIXTURE_PREDICTIONS = [0.7, 0.8, 0.6]
BRIER_CONTROLLED_RUNTIME_FIXTURE_TARGETS = [1.0, 0.0, 1.0]

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
    "controlled_runtime_execution_promotion_authorized",
    "phase23_activation_authorized",
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


def _runtime_guards() -> dict[str, bool]:
    return {field: True for field in RUNTIME_GUARD_FIELDS}


def _source_record(source_id: str, path: Path, packet: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": path.as_posix(),
        "observed": bool(packet),
        "file_hash": _sha256(path),
        "packet_hash": str(packet.get("runtime_execution_surface_activation_gate_hash", NOT_COMPUTABLE)),
        "expected_packet_hash": EXPECTED_PHASE21_HASH,
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_PHASE21_STATUS,
        "authority_locks_all_false": (
            True
            if packet.get("authority_locks") is None
            else _locks_all_false(packet.get("authority_locks"))
        ),
        "valid_for_runtime_execution_activation": packet.get(
            "valid_for_runtime_execution_activation", NOT_COMPUTABLE
        ),
        "operator_review_posture": packet.get("operator_review_posture", NOT_COMPUTABLE),
        "recommended_next_lane": packet.get("recommended_next_lane", NOT_COMPUTABLE),
        "downstream": packet.get("downstream", NOT_COMPUTABLE),
    }


def _phase21_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if packet.get("status") != EXPECTED_PHASE21_STATUS:
        blockers.append("phase21_runtime_execution_surface_activation_gate_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("phase21_source_not_ready")
    if packet.get("source_blockers") != []:
        blockers.append("phase21_source_blockers_not_empty")
    if packet.get("runtime_execution_surface_activation_gate_ready") is not True:
        blockers.append("phase21_runtime_execution_surface_activation_gate_ready_not_true")
    if packet.get("runtime_execution_surface_activation_gate_hash") != EXPECTED_PHASE21_HASH:
        blockers.append("phase21_runtime_execution_surface_activation_gate_hash_mismatch")
    without_hash = dict(packet)
    observed_hash = without_hash.pop("runtime_execution_surface_activation_gate_hash", NOT_COMPUTABLE)
    if canonical_hash(without_hash) != observed_hash:
        blockers.append("phase21_runtime_execution_surface_activation_gate_self_hash_mismatch")
    if packet.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append("phase21_recommended_lane_mismatch")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("phase21_downstream_not_closed")
    if packet.get("planning_lane_activated") is not True:
        blockers.append("phase21_planning_lane_not_activated")
    if packet.get("operator_review_posture") != "ACTIVE":
        blockers.append("phase21_operator_review_posture_not_active")
    if packet.get("valid_for_execution") is True:
        blockers.append("phase21_execution_authority_not_denied")
    if packet.get("valid_for_runtime_execution_activation") is not True:
        blockers.append("phase21_runtime_execution_activation_not_eligible")
    activation = packet.get("runtime_execution_activation_contract", {})
    matrix = activation.get("runtime_execution_activation_matrix", [])
    if isinstance(matrix, list):
        for surface in matrix:
            if surface.get("runtime_execution_activation_recorded") is not True:
                blockers.append(
                    f"phase21_runtime_execution_activation_not_recorded:{surface.get('surface_id', 'unknown')}"
                )
    brier_runtime = packet.get("runtime_brier_telemetry_contract", {})
    if brier_runtime.get("murphy_decomposition_default") is not True:
        blockers.append("phase21_murphy_decomposition_default_not_enabled")
    if brier_runtime.get("yates_decomposition_default") is not True:
        blockers.append("phase21_yates_decomposition_default_not_enabled")
    locks = packet.get("authority_locks")
    if locks is not None and not _locks_all_false(locks):
        blockers.append("phase21_authority_locks_not_false")
    blockers.extend(
        _authority_expansion_blockers("phase21_runtime_execution_surface_activation_gate", packet)
    )
    return blockers


def _controlled_runtime_execution_promotion_contract(
    repo_root: Path,
    *,
    promotion_recorded: bool,
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
                "prior_promotion_class": RUNTIME_EXECUTION_ACTIVATION_PROMOTION_CLASSES[surface_id],
                "promotion_class": CONTROLLED_RUNTIME_EXECUTION_PROMOTION_CLASSES[surface_id],
                "write_posture": (
                    "controlled_runtime_execution_promotion_recorded_pending_external_authority"
                    if promotion_recorded
                    else "controlled_runtime_execution_promotion_pending_phase21_ready"
                ),
                "path_observations": path_observations,
                "all_paths_observed": all(item["observed"] for item in path_observations),
                "runtime_execution_activation_recorded": promotion_recorded,
                "controlled_runtime_execution_promotion_recorded": promotion_recorded,
                "controlled_runtime_execution_authorized": False,
                "limited_write_allowed": LIMITED_WRITE_ALLOWED_BY_SURFACE[surface_id],
                "full_execution_denied": True,
                "authority_granted": False,
                "runtime_guards": _runtime_guards(),
            }
        )
    return {
        "contract_id": "v2_hygiene_phase15_controlled_runtime_execution_promotion_contract_001",
        "controlled_runtime_execution_promotion_matrix": surfaces,
        "surface_count": len(surfaces),
        "controlled_runtime_execution_promotion_recorded_count": sum(
            1
            for surface in surfaces
            if surface["controlled_runtime_execution_promotion_recorded"] is True
        ),
        "controlled_runtime_execution_authorized": False,
        "execution_authority_granted": False,
    }


def _controlled_runtime_execution_receipt_contract(
    *,
    promotion_recorded: bool,
) -> dict[str, Any]:
    receipts = []
    for surface_id in CONTROLLED_RUNTIME_EXECUTION_PROMOTION_CLASSES:
        receipts.append(
            {
                "surface_id": surface_id,
                "receipt_id": f"v2_controlled_runtime_execution_promotion_receipt_{surface_id}_001",
                "receipt_observed": promotion_recorded,
                "promotion_recorded": promotion_recorded,
                "controlled_runtime_only": True,
                "operator_signoff_required": True,
                "execution_authority_granted": False,
                "authority_granted": False,
            }
        )
    return {
        "contract_id": "v2_hygiene_phase15_controlled_runtime_execution_receipt_contract_001",
        "execution_receipts": receipts,
        "receipt_count": len(receipts),
        "all_receipts_recorded": promotion_recorded,
        "execution_authority_granted": False,
    }


def _controlled_runtime_brier_telemetry_contract() -> dict[str, Any]:
    fixture_decomposition = compute_full_decomposition(
        BRIER_CONTROLLED_RUNTIME_FIXTURE_PREDICTIONS,
        BRIER_CONTROLLED_RUNTIME_FIXTURE_TARGETS,
    )
    promotion_packet = build_brier_controlled_runtime_promotion_packet()
    hooks = []
    for surface_id in CONTROLLED_RUNTIME_EXECUTION_PROMOTION_CLASSES:
        hook = {
            "claim_id": surface_id,
            "forecast_probability": 0.91,
            "binary_outcome": NOT_COMPUTABLE,
            "brier_score": NOT_COMPUTABLE,
            "resolution_source": "core/governance/brier_provenance.py",
            "resolution_allowed": False,
            "brier_resolution_authorized": False,
            "promotion_tier": "CONTROLLED_RUNTIME",
            "operator_signoff_required": True,
            "controlled_runtime_promotion": True,
            "decomposition": fixture_decomposition,
            "adversarial_calibration_blockers": [],
        }
        hook["adversarial_calibration_blockers"] = validate_adversarial_calibration(hook)
        hooks.append(hook)
    hooks.append(
        {
            "claim_id": "controlled_runtime_dual_brier_decomposition",
            "forecast_probability": compute_brier_score(0.85, 0.0),
            "binary_outcome": NOT_COMPUTABLE,
            "brier_score": NOT_COMPUTABLE,
            "resolution_source": "core/scoring/brier.py",
            "resolution_allowed": False,
            "brier_resolution_authorized": False,
            "promotion_tier": "CONTROLLED_RUNTIME",
            "operator_signoff_required": True,
            "controlled_runtime_promotion": True,
            "decomposition": fixture_decomposition,
            "adversarial_calibration_blockers": validate_adversarial_calibration(
                {
                    "claim_id": "controlled_runtime_dual_brier_decomposition",
                    "forecast_probability": compute_brier_score(0.85, 0.0),
                    "binary_outcome": NOT_COMPUTABLE,
                    "brier_score": NOT_COMPUTABLE,
                    "resolution_allowed": False,
                    "brier_resolution_authorized": False,
                }
            ),
        }
    )
    signal_forager = build_signal_forager_brier_contract()
    return {
        "contract_id": "v2_hygiene_phase15_controlled_runtime_brier_telemetry_contract_001",
        "telemetry_only": True,
        "runtime_telemetry_only": True,
        "controlled_runtime_promotion": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "decomposition_mode": DECOMPOSITION_MODE,
        "murphy_decomposition_default": True,
        "yates_decomposition_default": True,
        "operator_signoff_required": True,
        "fixture_decomposition": fixture_decomposition,
        "controlled_runtime_promotion_packet": promotion_packet,
        "telemetry_hooks": hooks,
        "oracle_shadow_binding": {
            "paths": ["out/oracle/", "core/ingest/"],
            "signal_forager_contract_id": signal_forager["contract_id"],
            "decomposition_mode": signal_forager["decomposition_mode"],
        },
        "rune_visualization_binding": {
            "paths": [
                "docs/atlas/abx-runes.md",
                "docs/media/abx-runes.svg",
                "docs/status/badges/runes.json",
            ],
            "decomposition_mode": DECOMPOSITION_MODE,
        },
        "resolution_allowed": False,
        "brier_resolution_authorized": False,
    }


def _brier_scoring_contract() -> dict[str, Any]:
    controlled = _controlled_runtime_brier_telemetry_contract()
    return {
        "contract_id": "v2_hygiene_phase15_controlled_runtime_execution_brier_telemetry_contract_001",
        "telemetry_only": True,
        "brier_score_formula": controlled["brier_score_formula"],
        "decomposition_mode": controlled["decomposition_mode"],
        "telemetry_hooks": controlled["telemetry_hooks"],
        "resolution_allowed": False,
        "brier_resolution_authorized": False,
    }


def _operator_attestation_workflow_contract(*, ready: bool) -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase15_operator_attestation_workflow_contract_001",
        "manual_operator_signoff_required": True,
        "operator_signoff_auto_approved": False,
        "external_operator_attestation_required": True,
        "phase21_handoff_template_path": PHASE21_HANDOFF_TEMPLATE_PATH.as_posix(),
        "notion_writeback_allowed": False,
        "hash_chain_review_required": True,
        "hash_chain": {
            "phase21_gate_hash": EXPECTED_PHASE21_HASH if ready else NOT_COMPUTABLE,
            "phase22_gate_hash": NOT_COMPUTABLE,
        },
        "claims": [
            {
                "field": "phase21_hash_chain_reviewed",
                "classification": "OBSERVED" if ready else "INFERRED",
                "provenance": SOURCE_PHASE21_GATE_JSON_PATH.as_posix(),
                "value": ready,
            },
            {
                "field": "controlled_runtime_dual_brier_decomposition_active",
                "classification": "OBSERVED" if ready else "SPECULATIVE",
                "provenance": "core/scoring/brier.py",
                "value": ready,
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
        "contract_id": "v2_hygiene_phase15_dependency_denial_contract_001",
        "package_lock_mutation_authorized": False,
        "package_lock_tracking_authorized": False,
        "toolchain_provisioning_authorized": False,
        "dependency_mutation_authorized": False,
        "npmrc_stabilization_observed": (Path(".") / "apps/aal-viz-live-console/.npmrc").exists(),
        "package_lock_resolution_held": True,
        "high_risk_mutations_denied": True,
    }


def _rune_governance_mapping() -> list[dict[str, Any]]:
    fixture = build_brier_decomposition_fixture()
    return [
        {
            "rune": "Observe",
            "governance_mapping": "Phase 21 runtime activation and controlled promotion path observation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": "Phase 21 hash linkage and controlled runtime execution surface binding",
            "authority_granted": False,
            "risk_level": "MEDIUM",
        },
        {
            "rune": "Hold",
            "governance_mapping": "gate execution authority, uncontrolled runtime mutation, and high-risk mutations held",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Weigh",
            "governance_mapping": (
                "Murphy+Yates controlled-runtime Brier telemetry default on all promoted execution surfaces"
            ),
            "authority_granted": False,
            "risk_level": "LOW",
            "decomposition_mode": fixture["decomposition_mode"],
        },
        {
            "rune": "Seal",
            "governance_mapping": "Phase 22 controlled runtime promotion gate only; gate does not grant execution authority",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate(
    repo_root: str | Path = ".",
    *,
    source_phase21_gate_path: str | Path = SOURCE_PHASE21_GATE_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_phase21_gate_path)
    phase21 = _read_json(_resolve(root, source_path)) or {}
    blockers: list[str] = []
    if not phase21:
        blockers.append("required_phase21_runtime_execution_surface_activation_gate_missing")
    else:
        blockers.extend(_phase21_blockers(phase21))
    if not (root / PHASE21_HANDOFF_TEMPLATE_PATH).exists():
        blockers.append("phase21_handoff_template_missing")
    phase21_ready = bool(phase21) and not any(
        blocker.startswith("phase21_")
        or blocker.startswith("required_phase21")
        or blocker == "phase21_handoff_template_missing"
        for blocker in blockers
    )
    for entry in FULL_OPERATOR_EXECUTION_AUTONOMY_MATRIX:
        for path in entry["paths"]:
            if not _path_observed(root, path):
                blockers.append(
                    f"controlled_runtime_execution_surface_path_missing:{entry['surface_id']}"
                )
    blockers = sorted(set(blockers))
    gate_ready = phase21_ready and not blockers
    promotion_contract = _controlled_runtime_execution_promotion_contract(
        root,
        promotion_recorded=gate_ready,
    )
    status = READY_STATUS if gate_ready else BLOCKED_STATUS
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "operator_phase_number": OPERATOR_PHASE_NUMBER,
        "status": status,
        "sources_observed": bool(phase21),
        "source_records": [
            _source_record(
                "phase21_runtime_execution_surface_activation_gate",
                source_path,
                phase21,
            )
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if phase21_ready else "SOURCE_ARTIFACTS_NOT_READY",
        "controlled_runtime_execution_promotion_gate_ready": gate_ready,
        "phase21_runtime_execution_surface_activation_gate_hash_verified": phase21_ready,
        "planning_lane_status": phase21.get("planning_lane_status", NOT_COMPUTABLE) if phase21 else NOT_COMPUTABLE,
        "planning_lane_activated": phase21.get("planning_lane_activated", False) if phase21 else False,
        "controlled_runtime_execution_promotion_contract": promotion_contract,
        "controlled_runtime_execution_receipt_contract": _controlled_runtime_execution_receipt_contract(
            promotion_recorded=gate_ready,
        ),
        "controlled_runtime_brier_telemetry_contract": _controlled_runtime_brier_telemetry_contract(),
        "operator_attestation_workflow_contract": _operator_attestation_workflow_contract(ready=phase21_ready),
        "dependency_denial_contract": _dependency_denial_contract(),
        "brier_scoring_contract": _brier_scoring_contract(),
        "rune_governance_mapping": _rune_governance_mapping(),
        "recommended_next_action": (
            "controlled runtime execution promotion recorded for activated surfaces with dual "
            "Murphy+Yates Brier telemetry; gate does not grant execution authority; package-lock "
            "and high-risk mutations remain fail-closed"
            if gate_ready
            else "restore the Phase 21 runtime execution surface activation gate before controlled promotion"
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
        "valid_for_planning_lane": phase21_ready,
        "valid_for_controlled_writeback": phase21_ready,
        "valid_for_controlled_execution": phase21_ready,
        "valid_for_rune_viz_integration": phase21_ready,
        "valid_for_operator_execution_autonomy_eligibility": phase21_ready,
        "valid_for_operator_execution_autonomy_activation": phase21_ready,
        "valid_for_autonomy_hardening": phase21_ready,
        "valid_for_runtime_execution_activation": phase21_ready,
        "valid_for_controlled_runtime_execution_promotion": gate_ready,
        "valid_for_execution": False,
        "valid_for_promotion": False,
        "valid_for_activation": False,
        "operator_signoff_auto_approved": False,
        "external_operator_attestation_required": True,
        "operator_review_posture": "ACTIVE",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "authority_locks": _copied_authority_locks(phase21),
        "controlled_runtime_execution_promotion_gate_hash": "",
    }
    packet["controlled_runtime_execution_promotion_gate_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "controlled_runtime_execution_promotion_gate_hash"
        }
    )
    return packet


def render_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    promotion = packet["controlled_runtime_execution_promotion_contract"]
    denial = packet["dependency_denial_contract"]
    workflow = packet["operator_attestation_workflow_contract"]
    brier_controlled = packet["controlled_runtime_brier_telemetry_contract"]
    lines = [
        "# v2.0 Hygiene Phase 15 Controlled Runtime Execution Promotion Gate (Operator Phase 22)",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- operator_phase_number: {packet['operator_phase_number']}",
        f"- status: {packet['status']}",
        f"- valid_for_controlled_runtime_execution_promotion: {packet['valid_for_controlled_runtime_execution_promotion']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- operator_review_posture: {packet['operator_review_posture']}",
        "",
        "## Hash Chain",
        f"- phase21_gate_hash: {workflow['hash_chain']['phase21_gate_hash']}",
        f"- phase22_gate_hash: {packet['controlled_runtime_execution_promotion_gate_hash']}",
        "",
        "## Controlled Runtime Execution Promotion Matrix",
    ]
    for surface in promotion["controlled_runtime_execution_promotion_matrix"]:
        lines.append(
            f"- {surface['surface_id']}: {surface['promotion_class']} "
            f"promotion_recorded={surface['controlled_runtime_execution_promotion_recorded']}"
        )
    lines.extend(
        [
            "",
            "## Controlled Runtime Brier Telemetry Contract",
            f"- decomposition_mode: {brier_controlled['decomposition_mode']}",
            f"- murphy_decomposition_default: {brier_controlled['murphy_decomposition_default']}",
            f"- yates_decomposition_default: {brier_controlled['yates_decomposition_default']}",
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


def write_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
    source_phase21_gate_path: str | Path = SOURCE_PHASE21_GATE_JSON_PATH,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate(
        repo_root,
        source_phase21_gate_path=source_phase21_gate_path,
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase15_controlled_runtime_execution_promotion_gate_markdown(packet)
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
