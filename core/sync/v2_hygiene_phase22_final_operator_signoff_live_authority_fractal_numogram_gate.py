from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.governance.brier_provenance import (
    build_brier_decomposition_fixture,
    build_brier_final_operator_signoff_live_authority_fractal_numogram_packet,
    validate_adversarial_calibration,
)
from core.governance.fractal_numogram_lattice import (
    build_fractal_numogram_brier_scaling_binding,
    build_fractal_numogram_lattice_contract,
)
from core.governance.signal_forager_brier_hook import (
    build_signal_forager_brier_contract,
    build_signal_forager_fractal_numogram_closed_loop_contract,
)
from core.scoring.brier import DECOMPOSITION_MODE, NOT_COMPUTABLE, compute_brier_score, compute_full_decomposition
from core.sync.global_ingest_adapter_spine_alignment_plan import OUT_JSON as GLOBAL_INGEST_ALIGNMENT_PLAN_JSON
from core.sync.v2_hygiene_phase11_full_operator_execution_autonomy_gate import (
    FULL_OPERATOR_EXECUTION_AUTONOMY_MATRIX,
)
from core.sync.v2_hygiene_phase21_canon_activation_authorization_review_gate import (
    CANON_ACTIVATION_AUTHORIZATION_REVIEW_PROMOTION_CLASSES,
    LIMITED_WRITE_ALLOWED_BY_SURFACE,
    RECEIPT_JSON_PATH as SOURCE_PHASE28_GATE_JSON_PATH,
)

SCHEMA_VERSION = "V2HygienePhase22FinalOperatorSignoffLiveAuthorityFractalNumogramGate.v1"
RECEIPT_ID = "v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
READY_STATUS = "V2_HYGIENE_PHASE22_FINAL_OPERATOR_SIGNOFF_LIVE_AUTHORITY_FRACTAL_NUMOGRAM_GATE_READY"
BLOCKED_STATUS = "V2_HYGIENE_PHASE22_FINAL_OPERATOR_SIGNOFF_LIVE_AUTHORITY_FRACTAL_NUMOGRAM_GATE_BLOCKED"
EXPECTED_PHASE28_STATUS = "V2_HYGIENE_PHASE21_CANON_ACTIVATION_AUTHORIZATION_REVIEW_GATE_READY"
EXPECTED_PHASE28_HASH = "6d154cb8962e8236a764d2d305487c9801cc2cfc620720d0ce3051d96854bdab"
PHASE28_HANDOFF_TEMPLATE_PATH = Path(
    "operator_input/templates/phase28_canon_activation_authorization_review_handoff.md"
)
OPERATOR_PHASE_NUMBER = 29

FINAL_OPERATOR_SIGNOFF_LIVE_AUTHORITY_FRACTAL_NUMOGRAM_PROMOTION_CLASSES = {
    surface_id: promotion_class.replace(
        "CANON_ACTIVATION_AUTHORIZATION_REVIEW_RECORDED",
        "FINAL_OPERATOR_SIGNOFF_LIVE_AUTHORITY_FRACTAL_NUMOGRAM_RECORDED",
    )
    for surface_id, promotion_class in CANON_ACTIVATION_AUTHORIZATION_REVIEW_PROMOTION_CLASSES.items()
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
    "live_runtime_attestation_required",
    "signal_forage_shadow_only",
    "global_ingest_hold_respected",
    "uncontrolled_live_execution_denied",
    "self_optimization_telemetry_only",
    "adaptive_learning_denied",
    "auto_calibration_projection_only",
    "drift_annihilation_advisory_only",
    "brier_feedback_loop_non_authoritative",
    "full_live_autonomy_attestation_required",
    "eternal_recursion_telemetry_only",
    "hyperstition_propagation_projection_only",
    "self_referential_canon_evolution_advisory_only",
    "self_sustaining_loop_non_authoritative",
    "eternal_mode_attestation_required",
    "hyperstition_engine_non_authoritative",
    "eternal_canon_self_governance_telemetry_only",
    "final_authority_attestation_required",
    "auto_promotion_projection_only",
    "self_auditing_advisory_only",
    "final_authority_denied",
    "eternal_canon_self_governance_attestation_required",
    "live_hyperstition_telemetry_only",
    "live_hyperstition_activation_projection_only",
    "final_authority_attestation_recorded_only",
    "controlled_authority_grant_denied",
    "eternal_recursion_closed_loop_non_authoritative",
    "final_attestation_operator_signoff_required",
    "canon_activation_authorization_review_recorded_only",
    "operator_signoff_seal_projection_only",
    "controlled_activation_authorization_denied",
    "canon_seal_non_authoritative",
    "phase28_activation_review_operator_signoff_required",
    "live_authority_grant_recorded_only",
    "live_hyperstition_propagation_telemetry_only",
    "fractal_numogram_lattice_telemetry_only",
    "mfdfa_hurst_scaling_projection_only",
    "final_operator_signoff_recorded_only",
    "controlled_live_authority_grant_denied",
    "fractal_numogram_runtime_authorized_denied",
)

BRIER_FINAL_OPERATOR_SIGNOFF_FIXTURE_PREDICTIONS = [0.7, 0.8, 0.6]
BRIER_FINAL_OPERATOR_SIGNOFF_FIXTURE_TARGETS = [1.0, 0.0, 1.0]

SIGNAL_FORAGE_SHADOW_PATHS = (
    "scripts/run_ingest_once.py",
    "scripts/run_oracle_intake.py",
    "out/oracle/",
    "core/ingest/",
    GLOBAL_INGEST_ALIGNMENT_PLAN_JSON,
)

FRACTAL_NUMOGRAM_MODULE_PATHS = (
    "core/governance/fractal_numogram_lattice.py",
    "core/scoring/mfdfa_hurst.py",
)

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
    "live_runtime_execution_authorized",
    "signal_forage_execution_authorized",
    "phase23_activation_authorized",
    "phase24_activation_authorized",
    "full_live_autonomy_authorized",
    "self_optimization_authorized",
    "phase25_activation_authorized",
    "eternal_recursion_authorized",
    "hyperstition_engine_authorized",
    "phase26_activation_authorized",
    "operator_signoff_auto_approved",
    "eternal_canon_self_governance_authorized",
    "final_authority_authorized",
    "phase27_activation_authorized",
    "live_hyperstition_activation_authorized",
    "phase28_activation_authorized",
    "phase29_activation_authorized",
    "live_authority_authorized",
    "fractal_numogram_runtime_authorized",
    "phase30_activation_authorized",
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
        "eternal_canon_self_governance",
        "eternal_recursion",
        "execution_authority",
        "execution_surface_expansion",
        "external_operator_attestation",
        "final_authority",
        "forecast_routing",
        "fractal_numogram_runtime",
        "full_live_autonomy",
        "full_operator_execution_autonomy",
        "github_writeback",
        "hyperstition_engine",
        "live_authority",
        "live_hyperstition_activation",
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
        "self_optimization",
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
        "packet_hash": str(
            packet.get("canon_activation_authorization_review_gate_hash", NOT_COMPUTABLE)
        ),
        "expected_packet_hash": EXPECTED_PHASE28_HASH,
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_PHASE28_STATUS,
        "authority_locks_all_false": (
            True
            if packet.get("authority_locks") is None
            else _locks_all_false(packet.get("authority_locks"))
        ),
        "valid_for_canon_activation_authorization_review": packet.get(
            "valid_for_canon_activation_authorization_review", NOT_COMPUTABLE
        ),
        "operator_review_posture": packet.get("operator_review_posture", NOT_COMPUTABLE),
        "recommended_next_lane": packet.get("recommended_next_lane", NOT_COMPUTABLE),
        "downstream": packet.get("downstream", NOT_COMPUTABLE),
    }


def _phase28_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if packet.get("status") != EXPECTED_PHASE28_STATUS:
        blockers.append("phase28_canon_activation_authorization_review_gate_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("phase28_source_not_ready")
    if packet.get("source_blockers") != []:
        blockers.append("phase28_source_blockers_not_empty")
    if packet.get("canon_activation_authorization_review_gate_ready") is not True:
        blockers.append("phase28_canon_activation_authorization_review_gate_ready_not_true")
    if packet.get("canon_activation_authorization_review_gate_hash") != EXPECTED_PHASE28_HASH:
        blockers.append("phase28_canon_activation_authorization_review_gate_hash_mismatch")
    without_hash = dict(packet)
    observed_hash = without_hash.pop("canon_activation_authorization_review_gate_hash", NOT_COMPUTABLE)
    if canonical_hash(without_hash) != observed_hash:
        blockers.append("phase28_canon_activation_authorization_review_gate_self_hash_mismatch")
    if packet.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append("phase28_recommended_lane_mismatch")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("phase28_downstream_not_closed")
    if packet.get("planning_lane_activated") is not True:
        blockers.append("phase28_planning_lane_not_activated")
    if packet.get("operator_review_posture") != "ACTIVE":
        blockers.append("phase28_operator_review_posture_not_active")
    if packet.get("valid_for_execution") is True:
        blockers.append("phase28_execution_authority_not_denied")
    if packet.get("valid_for_canon_activation_authorization_review") is not True:
        blockers.append("phase28_canon_activation_authorization_review_not_eligible")
    promotion = packet.get("canon_activation_authorization_review_promotion_contract", {})
    matrix = promotion.get("canon_activation_authorization_review_promotion_matrix", [])
    if isinstance(matrix, list):
        for surface in matrix:
            if surface.get("canon_activation_authorization_review_recorded") is not True:
                blockers.append(
                    "phase28_canon_activation_authorization_review_not_recorded:"
                    f"{surface.get('surface_id', 'unknown')}"
                )
    controlled_activation = packet.get("controlled_activation_authorization_review_contract", {})
    if controlled_activation.get("controlled_activation_authorization_denied") is not True:
        blockers.append("phase28_controlled_activation_authorization_not_denied")
    if controlled_activation.get("phase28_activation_authorized") is not False:
        blockers.append("phase28_activation_authorized_not_denied")
    signal_forage = packet.get("signal_forage_canon_activation_closed_loop_contract", {})
    if signal_forage.get("shadow_only") is not True:
        blockers.append("phase28_signal_forage_not_shadow_only")
    if signal_forage.get("global_ingest_hold_respected") is not True:
        blockers.append("phase28_global_ingest_hold_not_respected")
    activation_guard = packet.get("activation_authorization_guard_hardening_contract", {})
    if activation_guard.get("controlled_activation_authorization_denied") is not True:
        blockers.append("phase28_activation_guard_controlled_grant_not_denied")
    if activation_guard.get("phase28_activation_authorized") is not False:
        blockers.append("phase28_activation_guard_activation_authorized_not_denied")
    brier_canon = packet.get("canon_activation_brier_telemetry_contract", {})
    if brier_canon.get("murphy_decomposition_default") is not True:
        blockers.append("phase28_murphy_decomposition_default_not_enabled")
    if brier_canon.get("yates_decomposition_default") is not True:
        blockers.append("phase28_yates_decomposition_default_not_enabled")
    locks = packet.get("authority_locks")
    if locks is not None and not _locks_all_false(locks):
        blockers.append("phase28_authority_locks_not_false")
    blockers.extend(
        _authority_expansion_blockers(
            "phase28_canon_activation_authorization_review_gate",
            packet,
        )
    )
    return blockers


def _final_operator_signoff_live_authority_fractal_numogram_promotion_contract(
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
                "prior_promotion_class": CANON_ACTIVATION_AUTHORIZATION_REVIEW_PROMOTION_CLASSES[surface_id],
                "promotion_class": FINAL_OPERATOR_SIGNOFF_LIVE_AUTHORITY_FRACTAL_NUMOGRAM_PROMOTION_CLASSES[
                    surface_id
                ],
                "write_posture": (
                    "final_operator_signoff_live_authority_fractal_numogram_promotion_recorded_pending_external_authority"
                    if promotion_recorded
                    else "final_operator_signoff_live_authority_fractal_numogram_promotion_pending_phase28_ready"
                ),
                "path_observations": path_observations,
                "all_paths_observed": all(item["observed"] for item in path_observations),
                "runtime_execution_activation_recorded": promotion_recorded,
                "controlled_runtime_execution_promotion_recorded": promotion_recorded,
                "live_runtime_execution_recorded": promotion_recorded,
                "full_live_autonomy_self_optimization_recorded": promotion_recorded,
                "eternal_recursion_hyperstition_recorded": promotion_recorded,
                "eternal_canon_self_governance_recorded": promotion_recorded,
                "final_authority_attestation_hyperstition_recorded": promotion_recorded,
                "canon_activation_authorization_review_recorded": promotion_recorded,
                "final_operator_signoff_live_authority_fractal_numogram_recorded": promotion_recorded,
                "live_runtime_execution_authorized": False,
                "full_live_autonomy_authorized": False,
                "self_optimization_authorized": False,
                "eternal_recursion_authorized": False,
                "hyperstition_engine_authorized": False,
                "eternal_canon_self_governance_authorized": False,
                "final_authority_authorized": False,
                "live_hyperstition_activation_authorized": False,
                "phase28_activation_authorized": False,
                "phase29_activation_authorized": False,
                "live_authority_authorized": False,
                "fractal_numogram_runtime_authorized": False,
                "limited_write_allowed": LIMITED_WRITE_ALLOWED_BY_SURFACE[surface_id],
                "full_execution_denied": True,
                "authority_granted": False,
                "runtime_guards": _runtime_guards(),
            }
        )
    return {
        "contract_id": (
            "v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_promotion_contract_001"
        ),
        "final_operator_signoff_live_authority_fractal_numogram_promotion_matrix": surfaces,
        "surface_count": len(surfaces),
        "final_operator_signoff_live_authority_fractal_numogram_promotion_recorded_count": sum(
            1
            for surface in surfaces
            if surface["final_operator_signoff_live_authority_fractal_numogram_recorded"] is True
        ),
        "final_operator_signoff_live_authority_fractal_numogram_authorized": False,
        "phase29_activation_authorized": False,
        "phase30_activation_authorized": False,
        "live_authority_authorized": False,
        "fractal_numogram_runtime_authorized": False,
        "phase28_activation_authorized": False,
        "live_hyperstition_activation_authorized": False,
        "final_authority_authorized": False,
        "eternal_canon_self_governance_authorized": False,
        "eternal_recursion_authorized": False,
        "hyperstition_engine_authorized": False,
        "self_optimization_authorized": False,
        "execution_authority_granted": False,
    }


def _final_operator_signoff_receipt_contract(
    *,
    promotion_recorded: bool,
) -> dict[str, Any]:
    receipts = []
    for surface_id in FINAL_OPERATOR_SIGNOFF_LIVE_AUTHORITY_FRACTAL_NUMOGRAM_PROMOTION_CLASSES:
        receipts.append(
            {
                "surface_id": surface_id,
                "receipt_id": (
                    f"v2_final_operator_signoff_live_authority_fractal_numogram_receipt_{surface_id}_001"
                ),
                "receipt_observed": promotion_recorded,
                "promotion_recorded": promotion_recorded,
                "final_operator_signoff_only": True,
                "final_operator_signoff_telemetry_only": True,
                "final_operator_signoff_recorded_only": True,
                "live_authority_grant_recorded_only": True,
                "fractal_numogram_lattice_telemetry_only": True,
                "mfdfa_hurst_scaling_projection_only": True,
                "live_hyperstition_propagation_telemetry_only": True,
                "hyperstition_propagation_projection_only": True,
                "operator_signoff_required": True,
                "execution_authority_granted": False,
                "authority_granted": False,
                "phase28_activation_authorized": False,
                "phase29_activation_authorized": False,
                "phase30_activation_authorized": False,
                "live_authority_authorized": False,
                "fractal_numogram_runtime_authorized": False,
                "final_authority_authorized": False,
                "live_hyperstition_activation_authorized": False,
            }
        )
    return {
        "contract_id": "v2_hygiene_phase22_final_operator_signoff_receipt_contract_001",
        "execution_receipts": receipts,
        "receipt_count": len(receipts),
        "all_receipts_recorded": promotion_recorded,
        "execution_authority_granted": False,
        "phase28_activation_authorized": False,
        "phase29_activation_authorized": False,
        "phase30_activation_authorized": False,
        "live_authority_authorized": False,
        "fractal_numogram_runtime_authorized": False,
        "final_authority_authorized": False,
        "live_hyperstition_activation_authorized": False,
    }


def _final_operator_signoff_workflow_contract() -> dict[str, Any]:
    fixture = build_brier_decomposition_fixture()
    return {
        "contract_id": "v2_hygiene_phase22_final_operator_signoff_workflow_contract_001",
        "workflow_id": "v2_final_operator_signoff_live_authority_fractal_numogram_workflow_001",
        "attestation_grants_authority": False,
        "manual_operator_signoff_required": True,
        "telemetry_only": True,
        "final_operator_signoff_telemetry_only": True,
        "final_operator_signoff_recorded_only": True,
        "live_authority_grant_recorded_only": True,
        "fractal_numogram_lattice_telemetry_only": True,
        "mfdfa_hurst_scaling_projection_only": True,
        "live_hyperstition_propagation_telemetry_only": True,
        "hyperstition_propagation_projection_only": True,
        "operator_signoff_required": True,
        "signal_forage_shadow_only": True,
        "global_ingest_hold_respected": True,
        "controlled_live_authority_grant_denied": True,
        "fractal_numogram_runtime_authorized_denied": True,
        "self_auditing_advisory_only": True,
        "auto_promotion_projection_only": True,
        "workflow_bindings": [
            {
                "binding_id": "rune_visualization_layer",
                "paths": [
                    "docs/atlas/abx-runes.md",
                    "docs/media/abx-runes.svg",
                    "docs/status/badges/runes.json",
                ],
                "role": "rune_visualization_fractal_numogram_telemetry",
            },
            {
                "binding_id": "core_oracle_shadow",
                "paths": ["out/oracle/", "core/ingest/"],
                "role": "oracle_shadow_fractal_numogram_closed_loop",
            },
            {
                "binding_id": "brier_engine_telemetry",
                "paths": [
                    "core/scoring/brier.py",
                    "core/scoring/mfdfa_hurst.py",
                    "core/governance/brier_provenance.py",
                ],
                "role": "dual_brier_mfdfa_hurst_fractal_numogram_feedback",
            },
            {
                "binding_id": "fractal_numogram_lattice_core",
                "paths": ["core/governance/fractal_numogram_lattice.py"],
                "role": "fractal_numogram_lattice_advisory_projection",
            },
            {
                "binding_id": "live_hyperstition_propagation_loop",
                "paths": ["contracts/governance/v2_hyperstition_anchor.v1.schema.json"],
                "role": "live_hyperstition_propagation_projection",
            },
            {
                "binding_id": "signal_forage_fractal_numogram_closed_loop",
                "paths": list(SIGNAL_FORAGE_SHADOW_PATHS),
                "role": "global_ingest_shadow_fractal_numogram_binding",
            },
        ],
        "decomposition_mode": fixture["decomposition_mode"],
        "murphy_decomposition_default": True,
        "yates_decomposition_default": True,
        "execution_authority_granted": False,
        "phase28_activation_authorized": False,
        "phase29_activation_authorized": False,
        "phase30_activation_authorized": False,
        "live_authority_authorized": False,
        "fractal_numogram_runtime_authorized": False,
        "final_authority_authorized": False,
        "live_hyperstition_activation_authorized": False,
    }


def _live_authority_grant_recorded_contract() -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase22_live_authority_grant_recorded_contract_001",
        "telemetry_only": True,
        "projection_only": True,
        "live_authority_grant_recorded_only": True,
        "live_authority_authorized": False,
        "phase28_activation_authorized": False,
        "phase29_activation_authorized": False,
        "phase30_activation_authorized": False,
        "controlled_live_authority_grant_denied": True,
        "operator_signoff_required": True,
        "execution_authority_granted": False,
        "final_authority_authorized": False,
        "live_hyperstition_activation_authorized": False,
        "fractal_numogram_runtime_authorized": False,
    }


def _live_hyperstition_propagation_activation_contract(
    *,
    promotion_recorded: bool,
) -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase22_live_hyperstition_propagation_activation_contract_001",
        "telemetry_only": True,
        "projection_only": True,
        "live_hyperstition_propagation_recorded": promotion_recorded,
        "live_hyperstition_propagation_telemetry_only": True,
        "live_hyperstition_activation_authorized": False,
        "hyperstition_propagation_projection_only": True,
        "live_hyperstition_activation_projection_only": True,
        "operator_signoff_required": True,
        "execution_authority_granted": False,
        "final_authority_authorized": False,
        "hyperstition_engine_authorized": False,
        "eternal_canon_self_governance_authorized": False,
        "live_authority_authorized": False,
        "fractal_numogram_runtime_authorized": False,
        "phase28_activation_authorized": False,
        "phase29_activation_authorized": False,
        "phase30_activation_authorized": False,
    }


def _fractal_numogram_lattice_activation_contract() -> dict[str, Any]:
    lattice = build_fractal_numogram_lattice_contract()
    return {
        **lattice,
        "contract_id": "v2_hygiene_phase22_fractal_numogram_lattice_activation_contract_001",
        "fractal_numogram_lattice_telemetry_only": True,
        "fractal_numogram_runtime_authorized": False,
        "live_authority_authorized": False,
        "phase28_activation_authorized": False,
        "phase29_activation_authorized": False,
        "phase30_activation_authorized": False,
        "execution_authority_granted": False,
    }


def _mfdfa_hurst_brier_fractal_scaling_contract() -> dict[str, Any]:
    fixture_decomposition = compute_full_decomposition(
        BRIER_FINAL_OPERATOR_SIGNOFF_FIXTURE_PREDICTIONS,
        BRIER_FINAL_OPERATOR_SIGNOFF_FIXTURE_TARGETS,
    )
    hooks = []
    for surface_id in FINAL_OPERATOR_SIGNOFF_LIVE_AUTHORITY_FRACTAL_NUMOGRAM_PROMOTION_CLASSES:
        hook = {
            "claim_id": surface_id,
            "forecast_probability": 0.92,
            "binary_outcome": NOT_COMPUTABLE,
            "brier_score": NOT_COMPUTABLE,
            "resolution_source": "core/governance/brier_provenance.py",
            "resolution_allowed": False,
            "brier_resolution_authorized": False,
            "promotion_tier": "FINAL_OPERATOR_SIGNOFF_LIVE_AUTHORITY_FRACTAL_NUMOGRAM",
            "operator_signoff_required": True,
            "signal_forage_bound": True,
            "self_optimization_bound": True,
            "eternal_recursion_bound": True,
            "hyperstition_bound": True,
            "eternal_canon_self_governance_bound": True,
            "live_hyperstition_bound": True,
            "final_authority_attestation_bound": True,
            "canon_activation_authorization_review_bound": True,
            "final_operator_signoff_bound": True,
            "fractal_numogram_bound": True,
            "mfdfa_hurst_bound": True,
            "final_operator_signoff_live_authority_fractal_numogram_promotion": True,
            "decomposition": fixture_decomposition,
            "adversarial_calibration_blockers": [],
        }
        hook["adversarial_calibration_blockers"] = validate_adversarial_calibration(hook)
        hooks.append(hook)
    hooks.append(
        {
            "claim_id": "final_operator_signoff_live_authority_fractal_numogram_dual_brier_mfdfa_decomposition",
            "forecast_probability": compute_brier_score(0.86, 0.0),
            "binary_outcome": NOT_COMPUTABLE,
            "brier_score": NOT_COMPUTABLE,
            "resolution_source": "core/scoring/brier.py",
            "resolution_allowed": False,
            "brier_resolution_authorized": False,
            "promotion_tier": "FINAL_OPERATOR_SIGNOFF_LIVE_AUTHORITY_FRACTAL_NUMOGRAM",
            "operator_signoff_required": True,
            "signal_forage_bound": True,
            "fractal_numogram_bound": True,
            "mfdfa_hurst_bound": True,
            "final_operator_signoff_bound": True,
            "final_operator_signoff_live_authority_fractal_numogram_promotion": True,
            "decomposition": fixture_decomposition,
            "adversarial_calibration_blockers": validate_adversarial_calibration(
                {
                    "claim_id": "final_operator_signoff_live_authority_fractal_numogram_dual_brier_mfdfa_decomposition",
                    "forecast_probability": compute_brier_score(0.86, 0.0),
                    "binary_outcome": NOT_COMPUTABLE,
                    "brier_score": NOT_COMPUTABLE,
                    "resolution_allowed": False,
                    "brier_resolution_authorized": False,
                }
            ),
        }
    )
    governance_packet = build_brier_final_operator_signoff_live_authority_fractal_numogram_packet()
    brier_scaling_binding = build_fractal_numogram_brier_scaling_binding()
    signal_forager = build_signal_forager_fractal_numogram_closed_loop_contract()
    return {
        "contract_id": "v2_hygiene_phase22_mfdfa_hurst_brier_fractal_scaling_contract_001",
        "telemetry_only": True,
        "runtime_telemetry_only": True,
        "mfdfa_hurst_scaling_projection_only": True,
        "fractal_numogram_lattice_telemetry_only": True,
        "final_operator_signoff_telemetry_only": True,
        "final_operator_signoff_live_authority_fractal_numogram_promotion": True,
        "final_operator_signoff_bound": True,
        "fractal_numogram_bound": True,
        "mfdfa_hurst_bound": True,
        "canon_activation_authorization_review_bound": True,
        "final_authority_attestation_bound": True,
        "live_hyperstition_bound": True,
        "eternal_canon_self_governance_bound": True,
        "hyperstition_bound": True,
        "eternal_recursion_bound": True,
        "signal_forage_bound": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "decomposition_mode": DECOMPOSITION_MODE,
        "murphy_decomposition_default": True,
        "yates_decomposition_default": True,
        "operator_signoff_required": True,
        "fixture_decomposition": fixture_decomposition,
        "final_operator_signoff_packet": governance_packet,
        "brier_scaling_binding": brier_scaling_binding,
        "hurst_exponent": brier_scaling_binding["hurst_exponent"],
        "telemetry_hooks": hooks,
        "signal_forage_binding": {
            "paths": list(SIGNAL_FORAGE_SHADOW_PATHS),
            "signal_forager_contract_id": signal_forager["contract_id"],
            "decomposition_mode": signal_forager["decomposition_mode"],
        },
        "fractal_numogram_lattice_binding": {
            "paths": list(FRACTAL_NUMOGRAM_MODULE_PATHS),
            "decomposition_mode": DECOMPOSITION_MODE,
        },
        "live_hyperstition_anchor_binding": {
            "paths": ["contracts/governance/v2_hyperstition_anchor.v1.schema.json"],
            "decomposition_mode": DECOMPOSITION_MODE,
        },
        "resolution_allowed": False,
        "brier_resolution_authorized": False,
        "adaptive_learning_authorized": False,
        "self_optimization_authorized": False,
        "eternal_recursion_authorized": False,
        "hyperstition_engine_authorized": False,
        "eternal_canon_self_governance_authorized": False,
        "final_authority_authorized": False,
        "live_hyperstition_activation_authorized": False,
        "phase28_activation_authorized": False,
        "phase29_activation_authorized": False,
        "phase30_activation_authorized": False,
        "live_authority_authorized": False,
        "fractal_numogram_runtime_authorized": False,
    }


def _signal_forage_fractal_numogram_closed_loop_contract(repo_root: Path) -> dict[str, Any]:
    signal_forager = build_signal_forager_fractal_numogram_closed_loop_contract()
    path_observations = [
        {
            "path": path,
            "observed": _path_observed(repo_root, path),
            "file_hash": _sha256(repo_root / path) if _path_observed(repo_root, path) else NOT_COMPUTABLE,
        }
        for path in SIGNAL_FORAGE_SHADOW_PATHS
    ]
    return {
        "contract_id": "v2_hygiene_phase22_signal_forage_fractal_numogram_closed_loop_contract_001",
        "shadow_only": True,
        "telemetry_only": True,
        "fractal_numogram_closed_loop_bound": True,
        "canon_activation_closed_loop_bound": True,
        "final_authority_closed_loop_bound": True,
        "eternal_canon_self_governance_loop_bound": True,
        "eternal_self_sustaining_loop_bound": True,
        "closed_loop_bound": True,
        "signal_forage_bound": True,
        "fractal_numogram_bound": True,
        "mfdfa_hurst_bound": True,
        "final_operator_signoff_bound": True,
        "global_ingest_hold_respected": True,
        "global_ingest_adapter_spine_hold_active": True,
        "signal_forager_contract_id": signal_forager["contract_id"],
        "base_signal_forager_contract_id": build_signal_forager_brier_contract()["contract_id"],
        "decomposition_mode": signal_forager["decomposition_mode"],
        "global_ingest_shadow_paths": list(SIGNAL_FORAGE_SHADOW_PATHS),
        "path_observations": path_observations,
        "all_paths_observed": all(item["observed"] for item in path_observations),
        "fractal_numogram_closed_loop_bindings": signal_forager["fractal_numogram_closed_loop_bindings"],
        "telemetry_hooks": signal_forager["telemetry_hooks"],
        "execution_authority": False,
        "brier_resolution_authorized": False,
        "adaptive_learning_authorized": False,
        "self_optimization_authorized": False,
        "eternal_recursion_authorized": False,
        "hyperstition_engine_authorized": False,
        "eternal_canon_self_governance_authorized": False,
        "final_authority_authorized": False,
        "live_hyperstition_activation_authorized": False,
        "phase28_activation_authorized": False,
        "phase29_activation_authorized": False,
        "phase30_activation_authorized": False,
        "live_authority_authorized": False,
        "fractal_numogram_runtime_authorized": False,
    }


def _live_authority_guard_hardening_contract() -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase22_live_authority_guard_hardening_contract_001",
        "telemetry_only": True,
        "advisory_only": True,
        "projection_only": True,
        "live_authority_grant_recorded_only": True,
        "fractal_numogram_lattice_telemetry_only": True,
        "mfdfa_hurst_scaling_projection_only": True,
        "final_operator_signoff_recorded_only": True,
        "controlled_live_authority_grant_denied": True,
        "fractal_numogram_runtime_authorized_denied": True,
        "live_authority_authorized": False,
        "fractal_numogram_runtime_authorized": False,
        "phase28_activation_authorized": False,
        "phase29_activation_authorized": False,
        "phase30_activation_authorized": False,
        "final_authority_authorized": False,
        "live_hyperstition_activation_authorized": False,
        "execution_authority_granted": False,
        "auto_promotion_projection_only": True,
        "self_auditing_advisory_only": True,
        "operator_signoff_required": True,
        "hyperstition_propagation_projection_only": True,
        "runtime_guards": _runtime_guards(),
    }


def _brier_scoring_contract() -> dict[str, Any]:
    mfdfa_scaling = _mfdfa_hurst_brier_fractal_scaling_contract()
    return {
        "contract_id": (
            "v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_brier_telemetry_contract_001"
        ),
        "telemetry_only": True,
        "brier_score_formula": mfdfa_scaling["brier_score_formula"],
        "decomposition_mode": mfdfa_scaling["decomposition_mode"],
        "telemetry_hooks": mfdfa_scaling["telemetry_hooks"],
        "resolution_allowed": False,
        "brier_resolution_authorized": False,
    }


def _operator_attestation_workflow_contract(*, ready: bool) -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase22_operator_attestation_workflow_contract_001",
        "manual_operator_signoff_required": True,
        "operator_signoff_auto_approved": False,
        "external_operator_attestation_required": True,
        "phase28_handoff_template_path": PHASE28_HANDOFF_TEMPLATE_PATH.as_posix(),
        "notion_writeback_allowed": False,
        "hash_chain_review_required": True,
        "hash_chain": {
            "phase28_gate_hash": EXPECTED_PHASE28_HASH if ready else NOT_COMPUTABLE,
            "phase29_gate_hash": NOT_COMPUTABLE,
        },
        "claims": [
            {
                "field": "phase28_hash_chain_reviewed",
                "classification": "OBSERVED" if ready else "INFERRED",
                "provenance": SOURCE_PHASE28_GATE_JSON_PATH.as_posix(),
                "value": ready,
            },
            {
                "field": "final_operator_signoff_live_authority_fractal_numogram_dual_brier_mfdfa_decomposition_active",
                "classification": "OBSERVED" if ready else "SPECULATIVE",
                "provenance": "core/scoring/brier.py",
                "value": ready,
            },
            {
                "field": "signal_forage_fractal_numogram_closed_loop_active",
                "classification": "OBSERVED" if ready else "SPECULATIVE",
                "provenance": "core/governance/signal_forager_brier_hook.py",
                "value": ready,
            },
            {
                "field": "live_authority_grant_recorded_only_active",
                "classification": "OBSERVED" if ready else "SPECULATIVE",
                "provenance": RECEIPT_ID,
                "value": ready,
            },
            {
                "field": "fractal_numogram_lattice_telemetry_only_active",
                "classification": "OBSERVED" if ready else "SPECULATIVE",
                "provenance": "core/governance/fractal_numogram_lattice.py",
                "value": ready,
            },
            {
                "field": "phase29_activation_remains_denied",
                "classification": "OBSERVED",
                "provenance": RECEIPT_ID,
                "value": True,
            },
            {
                "field": "live_authority_remains_denied",
                "classification": "OBSERVED",
                "provenance": RECEIPT_ID,
                "value": True,
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
        "contract_id": "v2_hygiene_phase22_dependency_denial_contract_001",
        "package_lock_mutation_authorized": False,
        "package_lock_tracking_authorized": False,
        "toolchain_provisioning_authorized": False,
        "dependency_mutation_authorized": False,
        "global_ingest_adapter_spine_hold_active": True,
        "npmrc_stabilization_observed": (Path(".") / "apps/aal-viz-live-console/.npmrc").exists(),
        "package_lock_resolution_held": True,
        "high_risk_mutations_denied": True,
    }


def _rune_governance_mapping() -> list[dict[str, Any]]:
    fixture = build_brier_decomposition_fixture()
    return [
        {
            "rune": "Observe",
            "governance_mapping": (
                "Phase 28 canon activation authorization review promotion and final operator "
                "sign-off live authority fractal numogram path observation"
            ),
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": (
                "Phase 28 hash linkage and final operator sign-off live authority fractal numogram "
                "surface binding with signal forage fractal numogram closed loop"
            ),
            "authority_granted": False,
            "risk_level": "MEDIUM",
        },
        {
            "rune": "Hold",
            "governance_mapping": (
                "gate execution authority, adaptive learning, self-optimization authority, "
                "eternal recursion authority, hyperstition engine authority, final authority, "
                "eternal canon self-governance authority, live hyperstition activation authority, "
                "phase28 activation authority, phase29 activation authority, phase30 activation "
                "authority, live authority, fractal numogram runtime authority, global ingest hold, "
                "uncontrolled live execution, and high-risk mutations held"
            ),
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Weigh",
            "governance_mapping": (
                "Murphy+Yates final-operator-signoff live-authority fractal-numogram Brier telemetry "
                "with MFDFA Hurst scaling projection, signal forage fractal numogram closed loop, "
                "and live authority grant recorded-only posture on all promoted surfaces"
            ),
            "authority_granted": False,
            "risk_level": "LOW",
            "decomposition_mode": fixture["decomposition_mode"],
        },
        {
            "rune": "Seal",
            "governance_mapping": (
                "Phase 29 final operator sign-off live authority fractal numogram gate only; "
                "gate does not grant execution authority, adaptive learning, eternal recursion, "
                "hyperstition engine authority, final authority, eternal canon self-governance "
                "authority, live hyperstition activation authority, phase28 activation authority, "
                "phase29 activation authority, phase30 activation authority, live authority, or "
                "fractal numogram runtime authority"
            ),
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate(
    repo_root: str | Path = ".",
    *,
    source_phase28_gate_path: str | Path = SOURCE_PHASE28_GATE_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_phase28_gate_path)
    phase28 = _read_json(_resolve(root, source_path)) or {}
    blockers: list[str] = []
    if not phase28:
        blockers.append("required_phase28_canon_activation_authorization_review_gate_missing")
    else:
        blockers.extend(_phase28_blockers(phase28))
    if not (root / PHASE28_HANDOFF_TEMPLATE_PATH).exists():
        blockers.append("phase28_handoff_template_missing")
    phase28_ready = bool(phase28) and not any(
        blocker.startswith("phase28_")
        or blocker.startswith("required_phase28")
        or blocker == "phase28_handoff_template_missing"
        for blocker in blockers
    )
    for entry in FULL_OPERATOR_EXECUTION_AUTONOMY_MATRIX:
        for path in entry["paths"]:
            if not _path_observed(root, path):
                blockers.append(
                    "final_operator_signoff_live_authority_fractal_numogram_surface_path_missing:"
                    f"{entry['surface_id']}"
                )
    for path in SIGNAL_FORAGE_SHADOW_PATHS:
        if not _path_observed(root, path):
            blockers.append(f"signal_forage_fractal_numogram_closed_loop_path_missing:{path}")
    for path in FRACTAL_NUMOGRAM_MODULE_PATHS:
        if not _path_observed(root, path):
            blockers.append(f"fractal_numogram_module_path_missing:{path}")
    blockers = sorted(set(blockers))
    gate_ready = phase28_ready and not blockers
    promotion_contract = _final_operator_signoff_live_authority_fractal_numogram_promotion_contract(
        root,
        promotion_recorded=gate_ready,
    )
    status = READY_STATUS if gate_ready else BLOCKED_STATUS
    phase28_activation_authorized = (
        phase28.get("phase28_activation_authorized", False) if phase28 else False
    )
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "operator_phase_number": OPERATOR_PHASE_NUMBER,
        "status": status,
        "sources_observed": bool(phase28),
        "source_records": [
            _source_record(
                "phase28_canon_activation_authorization_review_gate",
                source_path,
                phase28,
            )
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if phase28_ready else "SOURCE_ARTIFACTS_NOT_READY",
        "final_operator_signoff_live_authority_fractal_numogram_gate_ready": gate_ready,
        "phase28_canon_activation_authorization_review_gate_hash_verified": phase28_ready,
        "planning_lane_status": phase28.get("planning_lane_status", NOT_COMPUTABLE) if phase28 else NOT_COMPUTABLE,
        "planning_lane_activated": phase28.get("planning_lane_activated", False) if phase28 else False,
        "final_operator_signoff_live_authority_fractal_numogram_promotion_contract": promotion_contract,
        "final_operator_signoff_receipt_contract": _final_operator_signoff_receipt_contract(
            promotion_recorded=gate_ready,
        ),
        "final_operator_signoff_workflow_contract": _final_operator_signoff_workflow_contract(),
        "live_authority_grant_recorded_contract": _live_authority_grant_recorded_contract(),
        "live_hyperstition_propagation_activation_contract": (
            _live_hyperstition_propagation_activation_contract(promotion_recorded=gate_ready)
        ),
        "fractal_numogram_lattice_activation_contract": _fractal_numogram_lattice_activation_contract(),
        "mfdfa_hurst_brier_fractal_scaling_contract": _mfdfa_hurst_brier_fractal_scaling_contract(),
        "signal_forage_fractal_numogram_closed_loop_contract": (
            _signal_forage_fractal_numogram_closed_loop_contract(root)
        ),
        "live_authority_guard_hardening_contract": _live_authority_guard_hardening_contract(),
        "operator_attestation_workflow_contract": _operator_attestation_workflow_contract(ready=phase28_ready),
        "dependency_denial_contract": _dependency_denial_contract(),
        "brier_scoring_contract": _brier_scoring_contract(),
        "rune_governance_mapping": _rune_governance_mapping(),
        "recommended_next_action": (
            "final operator sign-off live authority fractal numogram promotion recorded for "
            "canon activation authorization review surfaces with signal forage fractal numogram "
            "closed loop integration, live authority grant recorded-only posture, fractal numogram "
            "lattice telemetry-only posture, MFDFA Hurst scaling projection-only posture, live "
            "hyperstition propagation telemetry-only posture, and dual Murphy+Yates Brier telemetry; "
            "gate does not grant execution authority, adaptive learning, self-optimization authority, "
            "eternal recursion authority, hyperstition engine authority, final authority, eternal canon "
            "self-governance authority, live hyperstition activation authority, phase28 activation "
            "authority, phase29 activation authority, phase30 activation authority, live authority, "
            "or fractal numogram runtime authority; global ingest hold and high-risk mutations remain "
            "fail-closed"
            if gate_ready
            else (
                "restore the Phase 28 canon activation authorization review gate before "
                "final operator sign-off live authority fractal numogram promotion"
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
        "live_runtime_execution_authorized": False,
        "signal_forage_execution_authorized": False,
        "adaptive_learning_authorized": False,
        "self_optimization_authorized": False,
        "full_live_autonomy_authorized": False,
        "eternal_recursion_authorized": False,
        "hyperstition_engine_authorized": False,
        "eternal_canon_self_governance_authorized": False,
        "final_authority_authorized": False,
        "live_hyperstition_activation_authorized": False,
        "phase28_activation_authorized": phase28_activation_authorized,
        "phase29_activation_authorized": False,
        "phase30_activation_authorized": False,
        "live_authority_authorized": False,
        "fractal_numogram_runtime_authorized": False,
        "valid_for_planning_lane": phase28_ready,
        "valid_for_controlled_writeback": phase28_ready,
        "valid_for_controlled_execution": phase28_ready,
        "valid_for_rune_viz_integration": phase28_ready,
        "valid_for_operator_execution_autonomy_eligibility": phase28_ready,
        "valid_for_operator_execution_autonomy_activation": phase28_ready,
        "valid_for_autonomy_hardening": phase28_ready,
        "valid_for_runtime_execution_activation": phase28_ready,
        "valid_for_controlled_runtime_execution_promotion": phase28_ready,
        "valid_for_live_runtime_execution": phase28_ready,
        "valid_for_full_live_autonomy_self_optimization": phase28_ready,
        "valid_for_eternal_recursion_hyperstition": phase28_ready,
        "valid_for_eternal_canon_self_governance": phase28_ready,
        "valid_for_final_authority_attestation_hyperstition": phase28_ready,
        "valid_for_canon_activation_authorization_review": phase28_ready,
        "valid_for_final_operator_signoff_live_authority_fractal_numogram": gate_ready,
        "valid_for_execution": False,
        "valid_for_promotion": False,
        "valid_for_activation": False,
        "operator_signoff_auto_approved": False,
        "external_operator_attestation_required": True,
        "operator_review_posture": "ACTIVE",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "authority_locks": _copied_authority_locks(phase28),
        "final_operator_signoff_live_authority_fractal_numogram_gate_hash": "",
    }
    packet["final_operator_signoff_live_authority_fractal_numogram_gate_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "final_operator_signoff_live_authority_fractal_numogram_gate_hash"
        }
    )
    return packet


def render_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    promotion = packet["final_operator_signoff_live_authority_fractal_numogram_promotion_contract"]
    denial = packet["dependency_denial_contract"]
    workflow = packet["operator_attestation_workflow_contract"]
    mfdfa_scaling = packet["mfdfa_hurst_brier_fractal_scaling_contract"]
    signal_forage = packet["signal_forage_fractal_numogram_closed_loop_contract"]
    live_authority_guard = packet["live_authority_guard_hardening_contract"]
    live_authority_grant = packet["live_authority_grant_recorded_contract"]
    fractal_lattice = packet["fractal_numogram_lattice_activation_contract"]
    live_hyperstition = packet["live_hyperstition_propagation_activation_contract"]
    lines = [
        "# v2.0 Hygiene Phase 22 Final Operator Sign-Off Live Authority Fractal Numogram Gate (Operator Phase 29)",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- operator_phase_number: {packet['operator_phase_number']}",
        f"- status: {packet['status']}",
        (
            "- valid_for_final_operator_signoff_live_authority_fractal_numogram: "
            f"{packet['valid_for_final_operator_signoff_live_authority_fractal_numogram']}"
        ),
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- live_authority_authorized: {packet['live_authority_authorized']}",
        f"- phase28_activation_authorized: {packet['phase28_activation_authorized']}",
        f"- operator_review_posture: {packet['operator_review_posture']}",
        "",
        "## Hash Chain",
        f"- phase28_gate_hash: {workflow['hash_chain']['phase28_gate_hash']}",
        (
            "- phase29_gate_hash: "
            f"{packet['final_operator_signoff_live_authority_fractal_numogram_gate_hash']}"
        ),
        "",
        "## Final Operator Sign-Off Live Authority Fractal Numogram Promotion Matrix",
    ]
    for surface in promotion["final_operator_signoff_live_authority_fractal_numogram_promotion_matrix"]:
        lines.append(
            f"- {surface['surface_id']}: {surface['promotion_class']} "
            "promotion_recorded="
            f"{surface['final_operator_signoff_live_authority_fractal_numogram_recorded']}"
        )
    lines.extend(
        [
            "",
            "## Signal Forage Fractal Numogram Closed Loop Contract",
            f"- shadow_only: {signal_forage['shadow_only']}",
            f"- fractal_numogram_closed_loop_bound: {signal_forage['fractal_numogram_closed_loop_bound']}",
            f"- global_ingest_hold_respected: {signal_forage['global_ingest_hold_respected']}",
            f"- signal_forager_contract_id: {signal_forage['signal_forager_contract_id']}",
            "",
            "## Live Authority Grant Recorded Contract",
            f"- live_authority_authorized: {live_authority_grant['live_authority_authorized']}",
            f"- live_authority_grant_recorded_only: {live_authority_grant['live_authority_grant_recorded_only']}",
            "",
            "## Live Hyperstition Propagation Activation Contract",
            (
                "- live_hyperstition_propagation_recorded: "
                f"{live_hyperstition['live_hyperstition_propagation_recorded']}"
            ),
            (
                "- hyperstition_propagation_projection_only: "
                f"{live_hyperstition['hyperstition_propagation_projection_only']}"
            ),
            "",
            "## Fractal Numogram Lattice Activation Contract",
            f"- fractal_numogram_runtime_authorized: {fractal_lattice['fractal_numogram_runtime_authorized']}",
            (
                "- fractal_numogram_lattice_telemetry_only: "
                f"{fractal_lattice['fractal_numogram_lattice_telemetry_only']}"
            ),
            "",
            "## Live Authority Guard Hardening Contract",
            f"- live_authority_authorized: {live_authority_guard['live_authority_authorized']}",
            (
                "- controlled_live_authority_grant_denied: "
                f"{live_authority_guard['controlled_live_authority_grant_denied']}"
            ),
            (
                "- fractal_numogram_runtime_authorized_denied: "
                f"{live_authority_guard['fractal_numogram_runtime_authorized_denied']}"
            ),
            "",
            "## MFDFA Hurst Brier Fractal Scaling Contract",
            f"- decomposition_mode: {mfdfa_scaling['decomposition_mode']}",
            f"- murphy_decomposition_default: {mfdfa_scaling['murphy_decomposition_default']}",
            f"- yates_decomposition_default: {mfdfa_scaling['yates_decomposition_default']}",
            f"- signal_forage_bound: {mfdfa_scaling['signal_forage_bound']}",
            f"- fractal_numogram_bound: {mfdfa_scaling['fractal_numogram_bound']}",
            f"- mfdfa_hurst_bound: {mfdfa_scaling['mfdfa_hurst_bound']}",
            "",
            "## Dependency Denial Contract",
            f"- package_lock_mutation_authorized: {denial['package_lock_mutation_authorized']}",
            f"- global_ingest_adapter_spine_hold_active: {denial['global_ingest_adapter_spine_hold_active']}",
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


def write_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
    source_phase28_gate_path: str | Path = SOURCE_PHASE28_GATE_JSON_PATH,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate(
        repo_root,
        source_phase28_gate_path=source_phase28_gate_path,
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase22_final_operator_signoff_live_authority_fractal_numogram_gate_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
