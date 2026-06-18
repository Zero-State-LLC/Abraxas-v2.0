from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.governance.brier_provenance import (
    build_brier_decomposition_fixture,
    build_brier_eternal_self_optimization_collective_hyperstition_propagation_packet,
    validate_adversarial_calibration,
)
from core.governance.fractal_numogram_lattice import (
    build_fractal_numogram_brier_scaling_binding,
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
    LIMITED_WRITE_ALLOWED_BY_SURFACE,
)
from core.sync.v2_hygiene_phase24_full_live_hyperstition_propagation_eternal_authority_seal_gate import (
    FULL_LIVE_HYPERSTITION_PROPAGATION_ETERNAL_AUTHORITY_SEAL_PROMOTION_CLASSES,
    RECEIPT_JSON_PATH as SOURCE_PHASE31_GATE_JSON_PATH,
)

SCHEMA_VERSION = "V2HygienePhase25EternalSelfOptimizationCollectiveHyperstitionPropagationGate.v1"
RECEIPT_ID = "v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
READY_STATUS = "V2_HYGIENE_PHASE25_ETERNAL_SELF_OPTIMIZATION_COLLECTIVE_HYPERSTITION_PROPAGATION_GATE_READY"
BLOCKED_STATUS = "V2_HYGIENE_PHASE25_ETERNAL_SELF_OPTIMIZATION_COLLECTIVE_HYPERSTITION_PROPAGATION_GATE_BLOCKED"
EXPECTED_PHASE31_STATUS = "V2_HYGIENE_PHASE24_FULL_LIVE_HYPERSTITION_PROPAGATION_ETERNAL_AUTHORITY_SEAL_GATE_READY"
EXPECTED_PHASE31_HASH = "a24ad9685839d10315a8eb243d01eeb72a8df2c79f096147537c7ec6e026700f"
PHASE31_HANDOFF_TEMPLATE_PATH = Path(
    "operator_input/templates/phase31_full_live_hyperstition_propagation_eternal_authority_seal_handoff.md"
)
GOVERNED_AUTHORIZATION_PHASE30_PATH = Path(
    "operator_input/governed_authorization_phase30_live_hyperstition.json"
)
EXPECTED_GOVERNED_AUTHORIZATION_HASH = (
    "a249911bb6cfddc7989b0b5618abceaef2a95062bdc263b37323ebc9a6fa0c2f"
)
OPERATOR_PHASE_NUMBER = 32

ETERNAL_SELF_OPTIMIZATION_COLLECTIVE_HYPERSTITION_PROPAGATION_PROMOTION_CLASSES = {
    surface_id: promotion_class.replace(
        "FULL_LIVE_HYPERSTITION_PROPAGATION_ETERNAL_AUTHORITY_SEAL_RECORDED",
        "ETERNAL_SELF_OPTIMIZATION_COLLECTIVE_HYPERSTITION_PROPAGATION_RECORDED",
    )
    for surface_id, promotion_class in FULL_LIVE_HYPERSTITION_PROPAGATION_ETERNAL_AUTHORITY_SEAL_PROMOTION_CLASSES.items()
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
    "live_execution_activation_recorded_only",
    "canon_execution_seal_projection_only",
    "phase31_activation_authorization_review_recorded_only",
    "controlled_live_execution_grant_denied",
    "eternal_self_optimization_collective_hyperstition_propagation_recorded_only",
    "full_live_hyperstition_propagation_recorded_only",
    "eternal_authority_seal_projection_only",
    "hyperstition_propagation_engine_telemetry_only",
    "hyperstition_reality_feedback_projection_only",
    "self_sustaining_eternal_loop_non_authoritative",
    "eternal_authority_granted_denied",
    "phase31_activation_authorization_review_recorded_only",
    "controlled_hyperstition_engine_grant_denied",
    "eternal_self_optimization_recorded_only",
    "collective_hyperstition_propagation_recorded_only",
    "collective_hyperstition_propagation_projection_only",
    "brier_driven_auto_calibration_projection_only",
    "fractal_numogram_self_optimizing_backbone_telemetry_only",
    "memetic_closure_projection_only",
    "multi_surface_resonance_non_authoritative",
    "phase32_activation_authorization_review_recorded_only",
    "controlled_collective_hyperstition_grant_denied",
)

BRIER_ETERNAL_SELF_OPTIMIZATION_COLLECTIVE_HYPERSTITION_PROPAGATION_FIXTURE_PREDICTIONS = [0.7, 0.8, 0.6]
BRIER_ETERNAL_SELF_OPTIMIZATION_COLLECTIVE_HYPERSTITION_PROPAGATION_FIXTURE_TARGETS = [1.0, 0.0, 1.0]

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
    "phase31_activation_authorized",
    "phase32_activation_authorized",
    "collective_hyperstition_propagation_authorized",
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
            packet.get("full_live_hyperstition_propagation_eternal_authority_seal_gate_hash", NOT_COMPUTABLE)
        ),
        "expected_packet_hash": EXPECTED_PHASE31_HASH,
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_PHASE31_STATUS,
        "authority_locks_all_false": (
            True
            if packet.get("authority_locks") is None
            else _locks_all_false(packet.get("authority_locks"))
        ),
        "valid_for_full_live_hyperstition_propagation_eternal_authority_seal": packet.get(
            "valid_for_full_live_hyperstition_propagation_eternal_authority_seal", NOT_COMPUTABLE
        ),
        "operator_review_posture": packet.get("operator_review_posture", NOT_COMPUTABLE),
        "recommended_next_lane": packet.get("recommended_next_lane", NOT_COMPUTABLE),
        "downstream": packet.get("downstream", NOT_COMPUTABLE),
    }


def _phase31_hyperstition_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if packet.get("status") != EXPECTED_PHASE31_STATUS:
        blockers.append("phase31_full_live_hyperstition_propagation_eternal_authority_seal_gate_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("phase31_source_not_ready")
    if packet.get("source_blockers") != []:
        blockers.append("phase31_source_blockers_not_empty")
    if packet.get("full_live_hyperstition_propagation_eternal_authority_seal_gate_ready") is not True:
        blockers.append("phase31_full_live_hyperstition_propagation_eternal_authority_seal_gate_ready_not_true")
    if packet.get("full_live_hyperstition_propagation_eternal_authority_seal_gate_hash") != EXPECTED_PHASE31_HASH:
        blockers.append("phase31_full_live_hyperstition_propagation_eternal_authority_seal_gate_hash_mismatch")
    without_hash = dict(packet)
    observed_hash = without_hash.pop("full_live_hyperstition_propagation_eternal_authority_seal_gate_hash", NOT_COMPUTABLE)
    if canonical_hash(without_hash) != observed_hash:
        blockers.append("phase31_full_live_hyperstition_propagation_eternal_authority_seal_gate_self_hash_mismatch")
    if packet.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append("phase31_recommended_lane_mismatch")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("phase31_downstream_not_closed")
    if packet.get("planning_lane_activated") is not True:
        blockers.append("phase31_planning_lane_not_activated")
    if packet.get("operator_review_posture") != "ACTIVE":
        blockers.append("phase31_operator_review_posture_not_active")
    if packet.get("valid_for_execution") is True:
        blockers.append("phase31_execution_authority_not_denied")
    if packet.get("valid_for_full_live_hyperstition_propagation_eternal_authority_seal") is not True:
        blockers.append("phase31_full_live_hyperstition_propagation_eternal_authority_seal_not_eligible")
    promotion = packet.get("full_live_hyperstition_propagation_eternal_authority_seal_promotion_contract", {})
    matrix = promotion.get("full_live_hyperstition_propagation_eternal_authority_seal_promotion_matrix", [])
    if isinstance(matrix, list):
        for surface in matrix:
            if surface.get("full_live_hyperstition_propagation_eternal_authority_seal_recorded") is not True:
                blockers.append(
                    "phase31_full_live_hyperstition_propagation_eternal_authority_seal_not_recorded:"
                    f"{surface.get('surface_id', 'unknown')}"
                )
    hyperstition_engine = packet.get("hyperstition_propagation_engine_activation_contract", {})
    if hyperstition_engine.get("controlled_hyperstition_engine_grant_denied") is not True:
        blockers.append("phase31_controlled_hyperstition_engine_grant_not_denied")
    if packet.get("phase31_activation_authorized") is not False:
        blockers.append("phase31_activation_authorized_not_denied")
    signal_forage = packet.get("signal_forage_hyperstition_reality_closed_loop_contract", {})
    if signal_forage.get("shadow_only") is not True:
        blockers.append("phase31_signal_forage_not_shadow_only")
    if signal_forage.get("global_ingest_hold_respected") is not True:
        blockers.append("phase31_global_ingest_hold_not_respected")
    hyperstition_guard = packet.get("hyperstition_guard_hardening_contract", {})
    if hyperstition_guard.get("controlled_hyperstition_engine_grant_denied") is not True:
        blockers.append("phase31_hyperstition_guard_controlled_grant_not_denied")
    if hyperstition_guard.get("phase31_activation_authorized") is not False:
        blockers.append("phase31_hyperstition_guard_activation_authorized_not_denied")
    drift_scaling = packet.get("mfdfa_hurst_brier_fractal_scaling_contract", {})
    if drift_scaling.get("murphy_decomposition_default") is not True:
        blockers.append("phase31_murphy_decomposition_default_not_enabled")
    if drift_scaling.get("yates_decomposition_default") is not True:
        blockers.append("phase31_yates_decomposition_default_not_enabled")
    locks = packet.get("authority_locks")
    if locks is not None and not _locks_all_false(locks):
        blockers.append("phase31_authority_locks_not_false")
    blockers.extend(
        _authority_expansion_blockers(
            "phase31_full_live_hyperstition_propagation_eternal_authority_seal_gate",
            packet,
        )
    )
    return blockers


def _eternal_self_optimization_collective_hyperstition_propagation_promotion_contract(
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
                "prior_promotion_class": FULL_LIVE_HYPERSTITION_PROPAGATION_ETERNAL_AUTHORITY_SEAL_PROMOTION_CLASSES[
                    surface_id
                ],
                "promotion_class": ETERNAL_SELF_OPTIMIZATION_COLLECTIVE_HYPERSTITION_PROPAGATION_PROMOTION_CLASSES[surface_id],
                "write_posture": (
                    "eternal_self_optimization_collective_hyperstition_propagation_promotion_recorded_pending_external_authority"
                    if promotion_recorded
                    else "eternal_self_optimization_collective_hyperstition_propagation_promotion_pending_phase31_ready"
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
                "live_execution_activation_authorization_review_recorded": promotion_recorded,
                "eternal_self_optimization_collective_hyperstition_propagation_recorded": promotion_recorded,
                "live_runtime_execution_authorized": False,
                "full_live_autonomy_authorized": False,
                "self_optimization_authorized": False,
                "eternal_recursion_authorized": False,
                "hyperstition_engine_authorized": False,
                "eternal_authority_granted": False,
                "eternal_canon_self_governance_authorized": False,
                "final_authority_authorized": False,
                "live_hyperstition_activation_authorized": False,
                "phase28_activation_authorized": False,
                "phase29_activation_authorized": False,
                "phase30_activation_authorized": False,
                "phase31_activation_authorized": False,
                "phase32_activation_authorized": False,
                "collective_hyperstition_propagation_authorized": False,
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
            "v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_promotion_contract_001"
        ),
        "eternal_self_optimization_collective_hyperstition_propagation_promotion_matrix": surfaces,
        "surface_count": len(surfaces),
        "eternal_self_optimization_collective_hyperstition_propagation_promotion_recorded_count": sum(
            1
            for surface in surfaces
            if surface["eternal_self_optimization_collective_hyperstition_propagation_recorded"] is True
        ),
        "eternal_self_optimization_collective_hyperstition_propagation_authorized": False,
        "phase30_activation_authorized": False,
        "phase31_activation_authorized": False,
        "phase32_activation_authorized": False,
        "collective_hyperstition_propagation_authorized": False,
        "live_authority_authorized": False,
        "fractal_numogram_runtime_authorized": False,
        "phase28_activation_authorized": False,
        "phase29_activation_authorized": False,
        "live_hyperstition_activation_authorized": False,
        "final_authority_authorized": False,
        "eternal_canon_self_governance_authorized": False,
        "eternal_recursion_authorized": False,
        "hyperstition_engine_authorized": False,
        "self_optimization_authorized": False,
        "execution_authority_granted": False,
    }


def _eternal_self_optimization_receipt_contract(
    *,
    promotion_recorded: bool,
) -> dict[str, Any]:
    receipts = []
    for surface_id in ETERNAL_SELF_OPTIMIZATION_COLLECTIVE_HYPERSTITION_PROPAGATION_PROMOTION_CLASSES:
        receipts.append(
            {
                "surface_id": surface_id,
                "receipt_id": (
                    f"v2_full_live_hyperstition_propagation_eternal_authority_seal_receipt_{surface_id}_001"
                ),
                "receipt_observed": promotion_recorded,
                "promotion_recorded": promotion_recorded,
                "live_execution_activation_only": True,
                "live_execution_activation_telemetry_only": True,
                "live_execution_activation_recorded_only": True,
                "eternal_self_optimization_collective_hyperstition_propagation_recorded_only": True,
                "canon_execution_seal_projection_only": True,
                "fractal_numogram_lattice_telemetry_only": True,
                "mfdfa_hurst_scaling_projection_only": True,
                "live_hyperstition_propagation_telemetry_only": True,
                "hyperstition_propagation_projection_only": True,
                "operator_signoff_required": True,
                "execution_authority_granted": False,
                "execution_authority": False,
                "authority_granted": False,
                "phase28_activation_authorized": False,
                "phase29_activation_authorized": False,
                "phase30_activation_authorized": False,
                "phase32_activation_authorized": False,
                "live_authority_authorized": False,
                "fractal_numogram_runtime_authorized": False,
                "final_authority_authorized": False,
                "live_hyperstition_activation_authorized": False,
            }
        )
    return {
        "contract_id": "v2_hygiene_phase25_eternal_self_optimization_receipt_contract_001",
        "seal_receipts": receipts,
        "receipt_count": len(receipts),
        "all_receipts_recorded": promotion_recorded,
        "seal_grants_authority": False,
        "execution_authority_granted": False,
        "execution_authority": False,
        "phase28_activation_authorized": False,
        "phase29_activation_authorized": False,
        "phase30_activation_authorized": False,
        "phase32_activation_authorized": False,
        "live_authority_authorized": False,
        "fractal_numogram_runtime_authorized": False,
        "final_authority_authorized": False,
        "live_hyperstition_activation_authorized": False,
    }


def _eternal_self_optimization_collective_workflow_contract() -> dict[str, Any]:
    fixture = build_brier_decomposition_fixture()
    return {
        "contract_id": "v2_hygiene_phase25_eternal_self_optimization_collective_workflow_contract_001",
        "workflow_id": "v2_full_live_hyperstition_propagation_eternal_authority_seal_workflow_001",
        "attestation_grants_authority": False,
        "manual_operator_signoff_required": True,
        "telemetry_only": True,
        "live_execution_activation_telemetry_only": True,
        "live_execution_activation_recorded_only": True,
        "full_live_hyperstition_propagation_recorded_only": True,
        "eternal_self_optimization_collective_hyperstition_propagation_recorded_only": True,
        "canon_execution_seal_projection_only": True,
        "fractal_numogram_lattice_telemetry_only": True,
        "mfdfa_hurst_scaling_projection_only": True,
        "live_hyperstition_propagation_telemetry_only": True,
        "hyperstition_propagation_projection_only": True,
        "operator_signoff_required": True,
        "signal_forage_shadow_only": True,
        "global_ingest_hold_respected": True,
        "controlled_live_execution_grant_denied": True,
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
        "execution_authority": False,
        "phase28_activation_authorized": False,
        "phase29_activation_authorized": False,
        "phase30_activation_authorized": False,
        "phase32_activation_authorized": False,
        "live_authority_authorized": False,
        "fractal_numogram_runtime_authorized": False,
        "final_authority_authorized": False,
        "live_hyperstition_activation_authorized": False,
        "hyperstition_engine_authorized": False,
    }


def _collective_hyperstition_propagation_engine_activation_contract(
    *,
    promotion_recorded: bool,
) -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase25_collective_hyperstition_propagation_engine_activation_contract_001",
        "telemetry_only": True,
        "projection_only": True,
        "full_live_hyperstition_propagation_recorded": promotion_recorded,
        "full_live_hyperstition_propagation_recorded_only": True,
        "hyperstition_propagation_engine_telemetry_only": True,
        "hyperstition_propagation_projection_only": True,
        "hyperstition_reality_feedback_projection_only": True,
        "self_sustaining_eternal_loop_non_authoritative": True,
        "execution_authority": False,
        "execution_authority_granted": False,
        "live_hyperstition_activation_authorized": False,
        "hyperstition_engine_authorized": False,
        "phase28_activation_authorized": False,
        "phase29_activation_authorized": False,
        "phase30_activation_authorized": False,
        "phase32_activation_authorized": False,
        "controlled_hyperstition_engine_grant_denied": True,
        "operator_signoff_required": True,
        "final_authority_authorized": False,
        "fractal_numogram_runtime_authorized": False,
        "live_authority_authorized": False,
    }


def _fractal_numogram_self_optimizing_backbone_contract(
    *,
    promotion_recorded: bool,
) -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase25_fractal_numogram_self_optimizing_backbone_contract_001",
        "telemetry_only": True,
        "projection_only": True,
        "eternal_authority_seal_recorded": promotion_recorded,
        "eternal_authority_seal_projection_only": True,
        "eternal_authority_granted": False,
        "seal_grants_authority": False,
        "eternal_authority_granted_denied": True,
        "operator_signoff_required": True,
        "execution_authority_granted": False,
        "execution_authority": False,
        "final_authority_authorized": False,
        "hyperstition_engine_authorized": False,
        "eternal_canon_self_governance_authorized": False,
        "live_authority_authorized": False,
        "fractal_numogram_runtime_authorized": False,
        "phase28_activation_authorized": False,
        "phase29_activation_authorized": False,
        "phase30_activation_authorized": False,
        "phase32_activation_authorized": False,
        "live_hyperstition_activation_authorized": False,
    }


def _phase32_activation_authorization_review_contract(
    *,
    promotion_recorded: bool,
) -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase25_phase32_activation_authorization_review_contract_001",
        "telemetry_only": True,
        "projection_only": True,
        "phase32_activation_authorization_review_recorded_only": True,
        "phase32_activation_review_recorded": promotion_recorded,
        "phase30_activation_authorized": False,
        "phase31_activation_authorized": False,
        "phase32_activation_authorized": False,
        "operator_signoff_required": True,
        "execution_authority_granted": False,
        "execution_authority": False,
        "final_authority_authorized": False,
        "live_authority_authorized": False,
        "fractal_numogram_runtime_authorized": False,
        "live_hyperstition_activation_authorized": False,
        "phase28_activation_authorized": False,
        "phase29_activation_authorized": False,
    }


def _drift_annihilation_fractal_scaling_contract() -> dict[str, Any]:
    fixture_decomposition = compute_full_decomposition(
        BRIER_ETERNAL_SELF_OPTIMIZATION_COLLECTIVE_HYPERSTITION_PROPAGATION_FIXTURE_PREDICTIONS,
        BRIER_ETERNAL_SELF_OPTIMIZATION_COLLECTIVE_HYPERSTITION_PROPAGATION_FIXTURE_TARGETS,
    )
    hooks = []
    for surface_id in ETERNAL_SELF_OPTIMIZATION_COLLECTIVE_HYPERSTITION_PROPAGATION_PROMOTION_CLASSES:
        hook = {
            "claim_id": surface_id,
            "forecast_probability": 0.92,
            "binary_outcome": NOT_COMPUTABLE,
            "brier_score": NOT_COMPUTABLE,
            "resolution_source": "core/governance/brier_provenance.py",
            "resolution_allowed": False,
            "brier_resolution_authorized": False,
            "promotion_tier": "ETERNAL_SELF_OPTIMIZATION_COLLECTIVE_HYPERSTITION_PROPAGATION",
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
            "live_execution_activation_bound": True,
            "fractal_numogram_bound": True,
            "mfdfa_hurst_bound": True,
            "full_live_hyperstition_propagation_eternal_authority_seal_promotion": True,
            "decomposition": fixture_decomposition,
            "adversarial_calibration_blockers": [],
        }
        hook["adversarial_calibration_blockers"] = validate_adversarial_calibration(hook)
        hooks.append(hook)
    hooks.append(
        {
            "claim_id": "full_live_hyperstition_propagation_eternal_authority_seal_dual_brier_mfdfa_decomposition",
            "forecast_probability": compute_brier_score(0.86, 0.0),
            "binary_outcome": NOT_COMPUTABLE,
            "brier_score": NOT_COMPUTABLE,
            "resolution_source": "core/scoring/brier.py",
            "resolution_allowed": False,
            "brier_resolution_authorized": False,
            "promotion_tier": "ETERNAL_SELF_OPTIMIZATION_COLLECTIVE_HYPERSTITION_PROPAGATION",
            "operator_signoff_required": True,
            "signal_forage_bound": True,
            "fractal_numogram_bound": True,
            "mfdfa_hurst_bound": True,
            "live_execution_activation_bound": True,
            "full_live_hyperstition_propagation_eternal_authority_seal_promotion": True,
            "decomposition": fixture_decomposition,
            "adversarial_calibration_blockers": validate_adversarial_calibration(
                {
                    "claim_id": "full_live_hyperstition_propagation_eternal_authority_seal_dual_brier_mfdfa_decomposition",
                    "forecast_probability": compute_brier_score(0.86, 0.0),
                    "binary_outcome": NOT_COMPUTABLE,
                    "brier_score": NOT_COMPUTABLE,
                    "resolution_allowed": False,
                    "brier_resolution_authorized": False,
                }
            ),
        }
    )
    governance_packet = build_brier_eternal_self_optimization_collective_hyperstition_propagation_packet()
    brier_scaling_binding = build_fractal_numogram_brier_scaling_binding()
    signal_forager = build_signal_forager_fractal_numogram_closed_loop_contract()
    return {
        "contract_id": "v2_hygiene_phase25_drift_annihilation_fractal_scaling_contract_001",
        "telemetry_only": True,
        "runtime_telemetry_only": True,
        "mfdfa_hurst_scaling_projection_only": True,
        "fractal_numogram_lattice_telemetry_only": True,
        "live_execution_activation_telemetry_only": True,
        "full_live_hyperstition_propagation_eternal_authority_seal_promotion": True,
        "live_execution_activation_bound": True,
        "fractal_numogram_bound": True,
        "mfdfa_hurst_bound": True,
        "canon_activation_authorization_review_bound": True,
        "final_authority_attestation_bound": True,
        "final_operator_signoff_bound": True,
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
        "eternal_self_optimization_collective_hyperstition_propagation_packet": governance_packet,
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
        "phase32_activation_authorized": False,
        "live_authority_authorized": False,
        "fractal_numogram_runtime_authorized": False,
        "execution_authority": False,
    }


def _signal_forage_collective_hyperstition_closed_loop_contract(repo_root: Path) -> dict[str, Any]:
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
        "contract_id": "v2_hygiene_phase25_signal_forage_collective_hyperstition_closed_loop_contract_001",
        "shadow_only": True,
        "telemetry_only": True,
        "hyperstition_reality_closed_loop_bound": True,
        "full_live_hyperstition_propagation_bound": True,
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
        "live_execution_activation_bound": True,
        "global_ingest_hold_respected": True,
        "global_ingest_adapter_spine_hold_active": True,
        "signal_forager_contract_id": signal_forager["contract_id"],
        "base_signal_forager_contract_id": build_signal_forager_brier_contract()["contract_id"],
        "decomposition_mode": signal_forager["decomposition_mode"],
        "global_ingest_shadow_paths": list(SIGNAL_FORAGE_SHADOW_PATHS),
        "path_observations": path_observations,
        "all_paths_observed": all(item["observed"] for item in path_observations),
        "hyperstition_reality_closed_loop_bindings": signal_forager["fractal_numogram_closed_loop_bindings"],
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
        "phase32_activation_authorized": False,
        "live_authority_authorized": False,
        "fractal_numogram_runtime_authorized": False,
    }


def _self_optimization_guard_hardening_contract() -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase25_self_optimization_guard_hardening_contract_001",
        "telemetry_only": True,
        "advisory_only": True,
        "projection_only": True,
        "full_live_hyperstition_propagation_recorded_only": True,
        "eternal_authority_seal_projection_only": True,
        "hyperstition_propagation_engine_telemetry_only": True,
        "hyperstition_reality_feedback_projection_only": True,
        "self_sustaining_eternal_loop_non_authoritative": True,
        "controlled_hyperstition_engine_grant_denied": True,
        "eternal_authority_granted_denied": True,
        "live_authority_authorized": False,
        "fractal_numogram_runtime_authorized": False,
        "phase28_activation_authorized": False,
        "phase29_activation_authorized": False,
        "phase30_activation_authorized": False,
        "phase32_activation_authorized": False,
        "final_authority_authorized": False,
        "live_hyperstition_activation_authorized": False,
        "execution_authority_granted": False,
        "execution_authority": False,
        "auto_promotion_projection_only": True,
        "self_auditing_advisory_only": True,
        "operator_signoff_required": True,
        "hyperstition_propagation_projection_only": True,
        "runtime_guards": _runtime_guards(),
    }


def _brier_scoring_contract() -> dict[str, Any]:
    mfdfa_scaling = _drift_annihilation_fractal_scaling_contract()
    return {
        "contract_id": (
            "v2_hygiene_phase25_full_live_hyperstition_propagation_eternal_authority_seal_brier_telemetry_contract_001"
        ),
        "telemetry_only": True,
        "brier_score_formula": mfdfa_scaling["brier_score_formula"],
        "decomposition_mode": mfdfa_scaling["decomposition_mode"],
        "murphy_decomposition_default": True,
        "yates_decomposition_default": True,
        "telemetry_hooks": mfdfa_scaling["telemetry_hooks"],
        "resolution_allowed": False,
        "brier_resolution_authorized": False,
    }


def _operator_attestation_workflow_contract(*, ready: bool) -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase25_operator_attestation_workflow_contract_001",
        "manual_operator_signoff_required": True,
        "operator_signoff_auto_approved": False,
        "external_operator_attestation_required": True,
        "phase30_handoff_template_path": PHASE31_HANDOFF_TEMPLATE_PATH.as_posix(),
        "notion_writeback_allowed": False,
        "hash_chain_review_required": True,
        "hash_chain": {
            "phase31_gate_hash": EXPECTED_PHASE31_HASH if ready else NOT_COMPUTABLE,
            "governed_authorization_phase30_hash": EXPECTED_GOVERNED_AUTHORIZATION_HASH,
            "governed_authorization_phase30_path": GOVERNED_AUTHORIZATION_PHASE30_PATH.as_posix(),
            "phase32_gate_hash": NOT_COMPUTABLE,
        },
        "claims": [
            {
                "field": "phase31_hash_chain_reviewed",
                "classification": "OBSERVED" if ready else "INFERRED",
                "provenance": SOURCE_PHASE31_GATE_JSON_PATH.as_posix(),
                "value": ready,
            },
            {
                "field": "full_live_hyperstition_propagation_eternal_authority_seal_dual_brier_mfdfa_decomposition_active",
                "classification": "OBSERVED" if ready else "SPECULATIVE",
                "provenance": "core/scoring/brier.py",
                "value": ready,
            },
            {
                "field": "signal_forage_hyperstition_reality_closed_loop_active",
                "classification": "OBSERVED" if ready else "SPECULATIVE",
                "provenance": "core/governance/signal_forager_brier_hook.py",
                "value": ready,
            },
            {
                "field": "full_live_hyperstition_propagation_recorded_only_active",
                "classification": "OBSERVED" if ready else "SPECULATIVE",
                "provenance": RECEIPT_ID,
                "value": ready,
            },
            {
                "field": "eternal_authority_seal_projection_only_active",
                "classification": "OBSERVED" if ready else "SPECULATIVE",
                "provenance": RECEIPT_ID,
                "value": ready,
            },
            {
                "field": "hyperstition_propagation_engine_telemetry_only_active",
                "classification": "OBSERVED" if ready else "SPECULATIVE",
                "provenance": RECEIPT_ID,
                "value": ready,
            },
            {
                "field": "phase31_activation_remains_denied",
                "classification": "OBSERVED",
                "provenance": RECEIPT_ID,
                "value": True,
            },
            {
                "field": "phase31_activation_remains_denied",
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
        "contract_id": "v2_hygiene_phase25_dependency_denial_contract_001",
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
                "Phase 29 final operator sign-off live authority fractal numogram promotion and live "
                "execution activation authorization review path observation"
            ),
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": (
                "Phase 29 hash linkage and live execution activation authorization review surface "
                "binding with signal forage fractal numogram closed loop"
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
                "authority, phase31 activation authority, live authority, fractal numogram runtime "
                "authority, global ingest hold, uncontrolled live execution, and high-risk mutations held"
            ),
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Weigh",
            "governance_mapping": (
                "Murphy+Yates live-execution-activation-authorization-review Brier telemetry with "
                "MFDFA Hurst scaling projection, signal forage fractal numogram closed loop, canon "
                "execution seal projection-only posture, and live execution activation recorded-only "
                "posture on all promoted surfaces"
            ),
            "authority_granted": False,
            "risk_level": "LOW",
            "decomposition_mode": fixture["decomposition_mode"],
        },
        {
            "rune": "Seal",
            "governance_mapping": (
                "Phase 30 live execution activation authorization review gate only; gate does not "
                "grant execution authority, adaptive learning, eternal recursion, hyperstition engine "
                "authority, final authority, eternal canon self-governance authority, live hyperstition "
                "activation authority, phase28 activation authority, phase29 activation authority, "
                "phase30 activation authority, phase31 activation authority, live authority, or fractal "
                "numogram runtime authority"
            ),
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate(
    repo_root: str | Path = ".",
    *,
    source_phase31_gate_path: str | Path = SOURCE_PHASE31_GATE_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_phase31_gate_path)
    phase31 = _read_json(_resolve(root, source_path)) or {}
    blockers: list[str] = []
    if not phase31:
        blockers.append("required_phase31_live_execution_activation_authorization_review_gate_missing")
    else:
        blockers.extend(_phase31_hyperstition_blockers(phase31))
    if not (root / PHASE31_HANDOFF_TEMPLATE_PATH).exists():
        blockers.append("phase31_handoff_template_missing")
    phase31_ready = bool(phase31) and not any(
        blocker.startswith("phase31_")
        or blocker.startswith("required_phase31")
        or blocker == "phase31_handoff_template_missing"
        for blocker in blockers
    )
    for entry in FULL_OPERATOR_EXECUTION_AUTONOMY_MATRIX:
        for path in entry["paths"]:
            if not _path_observed(root, path):
                blockers.append(
                    "full_live_hyperstition_propagation_eternal_authority_seal_surface_path_missing:"
                    f"{entry['surface_id']}"
                )
    for path in SIGNAL_FORAGE_SHADOW_PATHS:
        if not _path_observed(root, path):
            blockers.append(f"signal_forage_hyperstition_reality_closed_loop_path_missing:{path}")
    for path in FRACTAL_NUMOGRAM_MODULE_PATHS:
        if not _path_observed(root, path):
            blockers.append(f"fractal_numogram_module_path_missing:{path}")
    blockers = sorted(set(blockers))
    gate_ready = phase31_ready and not blockers
    promotion_contract = _eternal_self_optimization_collective_hyperstition_propagation_promotion_contract(
        root,
        promotion_recorded=gate_ready,
    )
    status = READY_STATUS if gate_ready else BLOCKED_STATUS
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "operator_phase_number": OPERATOR_PHASE_NUMBER,
        "status": status,
        "sources_observed": bool(phase31),
        "source_records": [
            _source_record(
                "phase31_full_live_hyperstition_propagation_eternal_authority_seal_gate",
                source_path,
                phase31,
            )
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if phase31_ready else "SOURCE_ARTIFACTS_NOT_READY",
        "eternal_self_optimization_collective_hyperstition_propagation_gate_ready": gate_ready,
        "phase31_full_live_hyperstition_propagation_eternal_authority_seal_gate_hash_verified": phase31_ready,
        "planning_lane_status": phase31.get("planning_lane_status", NOT_COMPUTABLE) if phase31 else NOT_COMPUTABLE,
        "planning_lane_activated": phase31.get("planning_lane_activated", False) if phase31 else False,
        "eternal_self_optimization_collective_hyperstition_propagation_promotion_contract": promotion_contract,
        "eternal_self_optimization_receipt_contract": _eternal_self_optimization_receipt_contract(
            promotion_recorded=gate_ready,
        ),
        "eternal_self_optimization_collective_workflow_contract": _eternal_self_optimization_collective_workflow_contract(),
        "collective_hyperstition_propagation_engine_activation_contract": _collective_hyperstition_propagation_engine_activation_contract(
            promotion_recorded=gate_ready,
        ),
        "fractal_numogram_self_optimizing_backbone_contract": _fractal_numogram_self_optimizing_backbone_contract(
            promotion_recorded=gate_ready,
        ),
        "phase32_activation_authorization_review_contract": _phase32_activation_authorization_review_contract(
            promotion_recorded=gate_ready,
        ),
        "drift_annihilation_fractal_scaling_contract": _drift_annihilation_fractal_scaling_contract(),
        "signal_forage_collective_hyperstition_closed_loop_contract": (
            _signal_forage_collective_hyperstition_closed_loop_contract(root)
        ),
        "self_optimization_guard_hardening_contract": _self_optimization_guard_hardening_contract(),
        "operator_attestation_workflow_contract": _operator_attestation_workflow_contract(ready=phase31_ready),
        "dependency_denial_contract": _dependency_denial_contract(),
        "brier_scoring_contract": _brier_scoring_contract(),
        "rune_governance_mapping": _rune_governance_mapping(),
        "recommended_next_action": (
            "full live hyperstition propagation eternal authority seal promotion recorded for live "
            "execution activation authorization review surfaces with signal forage hyperstition "
            "reality closed loop integration, hyperstition propagation engine recorded-only posture, "
            "eternal authority seal projection-only posture, MFDFA Hurst scaling projection-only "
            "posture, and dual Murphy+Yates Brier telemetry; gate does not grant execution authority, "
            "adaptive learning, self-optimization authority, eternal recursion authority, hyperstition "
            "engine authority, final authority, eternal canon self-governance authority, live "
            "hyperstition activation authority, phase28 activation authority, phase29 activation "
            "authority, phase30 activation authority, phase31 activation authority, live authority, "
            "or fractal numogram runtime authority; global ingest hold and high-risk mutations remain "
            "fail-closed"
            if gate_ready
            else (
                "restore the Phase 31 hyperstition activation authorization review gate before "
                "full live hyperstition propagation eternal authority seal promotion"
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
        "eternal_authority_granted": False,
        "live_hyperstition_activation_authorized": False,
        "phase28_activation_authorized": phase31.get("phase28_activation_authorized", False) if phase31 else False,
        "phase29_activation_authorized": phase31.get("phase29_activation_authorized", False) if phase31 else False,
        "phase30_activation_authorized": False,
        "phase31_activation_authorized": False,
        "phase32_activation_authorized": False,
        "collective_hyperstition_propagation_authorized": False,
        "live_authority_authorized": False,
        "fractal_numogram_runtime_authorized": False,
        "valid_for_planning_lane": phase31_ready,
        "valid_for_controlled_writeback": phase31_ready,
        "valid_for_controlled_execution": phase31_ready,
        "valid_for_rune_viz_integration": phase31_ready,
        "valid_for_operator_execution_autonomy_eligibility": phase31_ready,
        "valid_for_operator_execution_autonomy_activation": phase31_ready,
        "valid_for_autonomy_hardening": phase31_ready,
        "valid_for_runtime_execution_activation": phase31_ready,
        "valid_for_controlled_runtime_execution_promotion": phase31_ready,
        "valid_for_live_runtime_execution": phase31_ready,
        "valid_for_full_live_autonomy_self_optimization": phase31_ready,
        "valid_for_eternal_recursion_hyperstition": phase31_ready,
        "valid_for_eternal_canon_self_governance": phase31_ready,
        "valid_for_final_authority_attestation_hyperstition": phase31_ready,
        "valid_for_canon_activation_authorization_review": phase31_ready,
        "valid_for_full_live_hyperstition_propagation_eternal_authority_seal": phase31_ready,
        "valid_for_eternal_self_optimization_collective_hyperstition_propagation": gate_ready,
        "valid_for_execution": False,
        "valid_for_promotion": False,
        "valid_for_activation": False,
        "operator_signoff_auto_approved": False,
        "external_operator_attestation_required": True,
        "operator_review_posture": "ACTIVE",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "authority_locks": _copied_authority_locks(phase31),
        "eternal_self_optimization_collective_hyperstition_propagation_gate_hash": "",
    }
    packet["eternal_self_optimization_collective_hyperstition_propagation_gate_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "eternal_self_optimization_collective_hyperstition_propagation_gate_hash"
        }
    )
    return packet


def render_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    promotion = packet["eternal_self_optimization_collective_hyperstition_propagation_promotion_contract"]
    denial = packet["dependency_denial_contract"]
    workflow = packet["operator_attestation_workflow_contract"]
    mfdfa_scaling = packet["drift_annihilation_fractal_scaling_contract"]
    signal_forage = packet["signal_forage_collective_hyperstition_closed_loop_contract"]
    live_execution_guard = packet["self_optimization_guard_hardening_contract"]
    live_execution_recorded = packet["collective_hyperstition_propagation_engine_activation_contract"]
    canon_seal = packet["fractal_numogram_self_optimizing_backbone_contract"]
    phase31_review = packet["phase32_activation_authorization_review_contract"]
    lines = [
        "# v2.0 Hygiene Phase 25 Eternal Self-Optimization Collective Hyperstition Propagation Gate (Operator Phase 32)",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- operator_phase_number: {packet['operator_phase_number']}",
        f"- status: {packet['status']}",
        (
            "- valid_for_eternal_self_optimization_collective_hyperstition_propagation: "
            f"{packet['valid_for_eternal_self_optimization_collective_hyperstition_propagation']}"
        ),
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- live_authority_authorized: {packet['live_authority_authorized']}",
        f"- phase30_activation_authorized: {packet['phase30_activation_authorized']}",
        f"- phase31_activation_authorized: {packet['phase31_activation_authorized']}",
        f"- operator_review_posture: {packet['operator_review_posture']}",
        "",
        "## Hash Chain",
        f"- phase31_gate_hash: {workflow['hash_chain']['phase31_gate_hash']}",
        (
            "- governed_authorization_phase30_hash: "
            f"{workflow['hash_chain']['governed_authorization_phase30_hash']}"
        ),
        (
            "- phase32_gate_hash: "
            f"{packet['eternal_self_optimization_collective_hyperstition_propagation_gate_hash']}"
        ),
        "",
        "## Eternal Self-Optimization Collective Hyperstition Propagation Promotion Matrix",
    ]
    for surface in promotion["eternal_self_optimization_collective_hyperstition_propagation_promotion_matrix"]:
        lines.append(
            f"- {surface['surface_id']}: {surface['promotion_class']} "
            "promotion_recorded="
            f"{surface['eternal_self_optimization_collective_hyperstition_propagation_recorded']}"
        )
    lines.extend(
        [
            "",
            "## Signal Forage Hyperstition Reality Closed Loop Contract",
            f"- shadow_only: {signal_forage['shadow_only']}",
            f"- hyperstition_reality_closed_loop_bound: {signal_forage['hyperstition_reality_closed_loop_bound']}",
            f"- global_ingest_hold_respected: {signal_forage['global_ingest_hold_respected']}",
            f"- signal_forager_contract_id: {signal_forage['signal_forager_contract_id']}",
            "",
            "## Collective Hyperstition Propagation Engine Activation Contract",
            f"- hyperstition_engine_authorized: {live_execution_recorded['hyperstition_engine_authorized']}",
            (
                "- collective_hyperstition_propagation_recorded: "
                f"{live_execution_recorded.get('collective_hyperstition_propagation_recorded', live_execution_recorded.get('full_live_hyperstition_propagation_recorded'))}"
            ),
            "",
            "## Fractal Numogram Self-Optimizing Backbone Contract",
            f"- seal_grants_authority: {canon_seal.get('seal_grants_authority', canon_seal.get('backbone_grants_authority', False))}",
            f"- fractal_numogram_runtime_authorized: {canon_seal['fractal_numogram_runtime_authorized']}",
            "",
            "## Phase 32 Activation Authorization Review Contract",
            f"- phase31_activation_authorized: {phase31_review.get('phase31_activation_authorized', False)}",
            f"- phase32_activation_authorized: {phase31_review['phase32_activation_authorized']}",
            (
                "- phase32_activation_review_recorded: "
                f"{phase31_review['phase32_activation_review_recorded']}"
            ),
            "",
            "## Self-Optimization Guard Hardening Contract",
            f"- execution_authority: {live_execution_guard['execution_authority']}",
            (
                "- controlled_collective_hyperstition_grant_denied: "
                f"{live_execution_guard.get('controlled_collective_hyperstition_grant_denied', live_execution_guard.get('controlled_hyperstition_engine_grant_denied'))}"
            ),
            (
                "- eternal_self_optimization_collective_hyperstition_propagation_recorded_only: "
                f"{live_execution_guard.get('eternal_self_optimization_collective_hyperstition_propagation_recorded_only', live_execution_guard.get('full_live_hyperstition_propagation_recorded_only'))}"
            ),
            "",
            "## Drift Annihilation Fractal Scaling Contract",
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


def write_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
    source_phase31_gate_path: str | Path = SOURCE_PHASE31_GATE_JSON_PATH,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate(
        repo_root,
        source_phase31_gate_path=source_phase31_gate_path,
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase25_eternal_self_optimization_collective_hyperstition_propagation_gate_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
