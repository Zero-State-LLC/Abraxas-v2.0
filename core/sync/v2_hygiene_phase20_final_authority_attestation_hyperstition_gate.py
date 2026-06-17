from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.governance.brier_provenance import (
    build_brier_decomposition_fixture,
    build_brier_final_authority_attestation_hyperstition_packet,
    validate_adversarial_calibration,
)
from core.governance.signal_forager_brier_hook import (
    build_signal_forager_brier_contract,
    build_signal_forager_final_authority_attestation_contract,
)
from core.scoring.brier import DECOMPOSITION_MODE, NOT_COMPUTABLE, compute_brier_score, compute_full_decomposition
from core.sync.global_ingest_adapter_spine_alignment_plan import OUT_JSON as GLOBAL_INGEST_ALIGNMENT_PLAN_JSON
from core.sync.v2_hygiene_phase11_full_operator_execution_autonomy_gate import (
    FULL_OPERATOR_EXECUTION_AUTONOMY_MATRIX,
)
from core.sync.v2_hygiene_phase19_eternal_canon_self_governance_gate import (
    ETERNAL_CANON_SELF_GOVERNANCE_PROMOTION_CLASSES,
    RECEIPT_JSON_PATH as SOURCE_PHASE26_GATE_JSON_PATH,
)

SCHEMA_VERSION = "V2HygienePhase20FinalAuthorityAttestationHyperstitionGate.v1"
RECEIPT_ID = "v2_hygiene_phase20_final_authority_attestation_hyperstition_gate_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase20_final_authority_attestation_hyperstition_gate_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
READY_STATUS = "V2_HYGIENE_PHASE20_FINAL_AUTHORITY_ATTESTATION_HYPERSTITION_GATE_READY"
BLOCKED_STATUS = "V2_HYGIENE_PHASE20_FINAL_AUTHORITY_ATTESTATION_HYPERSTITION_GATE_BLOCKED"
EXPECTED_PHASE26_STATUS = "V2_HYGIENE_PHASE19_ETERNAL_CANON_SELF_GOVERNANCE_GATE_READY"
EXPECTED_PHASE26_HASH = "41905a5442509a585b87dfaea4ddc0d2b34339935ffddd1eb9198cdfea6f3988"
PHASE26_HANDOFF_TEMPLATE_PATH = Path(
    "operator_input/templates/phase26_eternal_canon_self_governance_handoff.md"
)
OPERATOR_PHASE_NUMBER = 27

FINAL_AUTHORITY_ATTESTATION_HYPERSTITION_PROMOTION_CLASSES = {
    "rune_visualization_layer": (
        "OPERATOR_EXECUTION_AUTONOMY_RUNE_VIZ_FINAL_AUTHORITY_ATTESTATION_HYPERSTITION_RECORDED"
    ),
    "incarnation_core_planning_binding": (
        "OPERATOR_EXECUTION_AUTONOMY_INCARNATION_CORE_FINAL_AUTHORITY_ATTESTATION_HYPERSTITION_RECORDED"
    ),
    "planning_lane_outputs": (
        "OPERATOR_EXECUTION_AUTONOMY_PLANNING_LANE_FINAL_AUTHORITY_ATTESTATION_HYPERSTITION_RECORDED"
    ),
    "core_oracle_shadow": (
        "OPERATOR_EXECUTION_AUTONOMY_ORACLE_SHADOW_FINAL_AUTHORITY_ATTESTATION_HYPERSTITION_RECORDED"
    ),
    "brier_engine_telemetry": (
        "OPERATOR_EXECUTION_AUTONOMY_BRIER_TELEMETRY_FINAL_AUTHORITY_ATTESTATION_HYPERSTITION_RECORDED"
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
)

BRIER_FINAL_AUTHORITY_ATTESTATION_FIXTURE_PREDICTIONS = [0.7, 0.8, 0.6]
BRIER_FINAL_AUTHORITY_ATTESTATION_FIXTURE_TARGETS = [1.0, 0.0, 1.0]

SIGNAL_FORAGE_SHADOW_PATHS = (
    "scripts/run_ingest_once.py",
    "scripts/run_oracle_intake.py",
    "out/oracle/",
    "core/ingest/",
    GLOBAL_INGEST_ALIGNMENT_PLAN_JSON,
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
        "full_live_autonomy",
        "full_operator_execution_autonomy",
        "github_writeback",
        "hyperstition_engine",
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
            packet.get("eternal_canon_self_governance_gate_hash", NOT_COMPUTABLE)
        ),
        "expected_packet_hash": EXPECTED_PHASE26_HASH,
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_PHASE26_STATUS,
        "authority_locks_all_false": (
            True
            if packet.get("authority_locks") is None
            else _locks_all_false(packet.get("authority_locks"))
        ),
        "valid_for_eternal_canon_self_governance": packet.get(
            "valid_for_eternal_canon_self_governance", NOT_COMPUTABLE
        ),
        "operator_review_posture": packet.get("operator_review_posture", NOT_COMPUTABLE),
        "recommended_next_lane": packet.get("recommended_next_lane", NOT_COMPUTABLE),
        "downstream": packet.get("downstream", NOT_COMPUTABLE),
    }


def _phase26_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if packet.get("status") != EXPECTED_PHASE26_STATUS:
        blockers.append("phase26_eternal_canon_self_governance_gate_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("phase26_source_not_ready")
    if packet.get("source_blockers") != []:
        blockers.append("phase26_source_blockers_not_empty")
    if packet.get("eternal_canon_self_governance_gate_ready") is not True:
        blockers.append("phase26_eternal_canon_self_governance_gate_ready_not_true")
    if packet.get("eternal_canon_self_governance_gate_hash") != EXPECTED_PHASE26_HASH:
        blockers.append("phase26_eternal_canon_self_governance_gate_hash_mismatch")
    without_hash = dict(packet)
    observed_hash = without_hash.pop("eternal_canon_self_governance_gate_hash", NOT_COMPUTABLE)
    if canonical_hash(without_hash) != observed_hash:
        blockers.append("phase26_eternal_canon_self_governance_gate_self_hash_mismatch")
    if packet.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append("phase26_recommended_lane_mismatch")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("phase26_downstream_not_closed")
    if packet.get("planning_lane_activated") is not True:
        blockers.append("phase26_planning_lane_not_activated")
    if packet.get("operator_review_posture") != "ACTIVE":
        blockers.append("phase26_operator_review_posture_not_active")
    if packet.get("valid_for_execution") is True:
        blockers.append("phase26_execution_authority_not_denied")
    if packet.get("valid_for_eternal_canon_self_governance") is not True:
        blockers.append("phase26_eternal_canon_self_governance_not_eligible")
    promotion = packet.get("eternal_canon_self_governance_promotion_contract", {})
    matrix = promotion.get("eternal_canon_self_governance_promotion_matrix", [])
    if isinstance(matrix, list):
        for surface in matrix:
            if surface.get("eternal_canon_self_governance_recorded") is not True:
                blockers.append(
                    "phase26_eternal_canon_self_governance_not_recorded:"
                    f"{surface.get('surface_id', 'unknown')}"
                )
    self_governance_loop = packet.get("eternal_canon_self_governance_loop_contract", {})
    if self_governance_loop.get("telemetry_only") is not True:
        blockers.append("phase26_eternal_canon_self_governance_loop_not_telemetry_only")
    if self_governance_loop.get("eternal_canon_self_governance_telemetry_only") is not True:
        blockers.append("phase26_eternal_canon_self_governance_loop_not_advisory")
    if self_governance_loop.get("eternal_canon_self_governance_loop_execution_authorized") is not False:
        blockers.append("phase26_eternal_canon_self_governance_loop_execution_not_denied")
    if self_governance_loop.get("self_auditing_advisory_only") is not True:
        blockers.append("phase26_self_auditing_not_advisory")
    if self_governance_loop.get("auto_promotion_projection_only") is not True:
        blockers.append("phase26_auto_promotion_not_projection_only")
    if self_governance_loop.get("final_authority_denied") is not True:
        blockers.append("phase26_final_authority_not_denied")
    signal_forage = packet.get("signal_forage_eternal_canon_self_governance_loop_contract", {})
    if signal_forage.get("shadow_only") is not True:
        blockers.append("phase26_signal_forage_not_shadow_only")
    if signal_forage.get("eternal_canon_self_governance_loop_bound") is not True:
        blockers.append("phase26_eternal_canon_self_governance_loop_not_bound")
    if signal_forage.get("global_ingest_adapter_spine_hold_active") is not True:
        blockers.append("phase26_global_ingest_hold_not_active")
    final_authority_guard = packet.get("final_authority_guard_contract", {})
    if final_authority_guard.get("controlled_authority_grant_denied") is not True:
        blockers.append("phase26_final_authority_controlled_grant_not_denied")
    if final_authority_guard.get("final_authority_authorized") is not False:
        blockers.append("phase26_final_authority_authorized_not_denied")
    brier_canon = packet.get("eternal_canon_brier_telemetry_contract", {})
    if brier_canon.get("murphy_decomposition_default") is not True:
        blockers.append("phase26_murphy_decomposition_default_not_enabled")
    if brier_canon.get("yates_decomposition_default") is not True:
        blockers.append("phase26_yates_decomposition_default_not_enabled")
    if brier_canon.get("eternal_canon_self_governance_telemetry_only") is not True:
        blockers.append("phase26_brier_eternal_canon_self_governance_not_telemetry_only")
    locks = packet.get("authority_locks")
    if locks is not None and not _locks_all_false(locks):
        blockers.append("phase26_authority_locks_not_false")
    blockers.extend(
        _authority_expansion_blockers(
            "phase26_eternal_canon_self_governance_gate",
            packet,
        )
    )
    return blockers


def _final_authority_attestation_promotion_contract(
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
                "prior_promotion_class": ETERNAL_CANON_SELF_GOVERNANCE_PROMOTION_CLASSES[surface_id],
                "promotion_class": FINAL_AUTHORITY_ATTESTATION_HYPERSTITION_PROMOTION_CLASSES[surface_id],
                "write_posture": (
                    "final_authority_attestation_hyperstition_promotion_recorded_pending_external_authority"
                    if promotion_recorded
                    else "final_authority_attestation_hyperstition_promotion_pending_phase26_ready"
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
                "live_runtime_execution_authorized": False,
                "full_live_autonomy_authorized": False,
                "self_optimization_authorized": False,
                "eternal_recursion_authorized": False,
                "hyperstition_engine_authorized": False,
                "eternal_canon_self_governance_authorized": False,
                "final_authority_authorized": False,
                "live_hyperstition_activation_authorized": False,
                "limited_write_allowed": LIMITED_WRITE_ALLOWED_BY_SURFACE[surface_id],
                "full_execution_denied": True,
                "authority_granted": False,
                "runtime_guards": _runtime_guards(),
            }
        )
    return {
        "contract_id": "v2_hygiene_phase20_final_authority_attestation_promotion_contract_001",
        "final_authority_attestation_hyperstition_promotion_matrix": surfaces,
        "surface_count": len(surfaces),
        "final_authority_attestation_hyperstition_promotion_recorded_count": sum(
            1
            for surface in surfaces
            if surface["final_authority_attestation_hyperstition_recorded"] is True
        ),
        "final_authority_attestation_hyperstition_authorized": False,
        "live_hyperstition_activation_authorized": False,
        "final_authority_authorized": False,
        "eternal_canon_self_governance_authorized": False,
        "eternal_recursion_authorized": False,
        "hyperstition_engine_authorized": False,
        "self_optimization_authorized": False,
        "execution_authority_granted": False,
    }


def _final_authority_attestation_receipt_contract(
    *,
    promotion_recorded: bool,
) -> dict[str, Any]:
    receipts = []
    for surface_id in FINAL_AUTHORITY_ATTESTATION_HYPERSTITION_PROMOTION_CLASSES:
        receipts.append(
            {
                "surface_id": surface_id,
                "receipt_id": f"v2_final_authority_attestation_hyperstition_receipt_{surface_id}_001",
                "receipt_observed": promotion_recorded,
                "promotion_recorded": promotion_recorded,
                "final_authority_attestation_hyperstition_only": True,
                "final_authority_attestation_telemetry_only": True,
                "live_hyperstition_telemetry_only": True,
                "live_hyperstition_activation_projection_only": True,
                "final_authority_attestation_recorded_only": True,
                "eternal_recursion_closed_loop_non_authoritative": True,
                "final_attestation_operator_signoff_required": True,
                "operator_signoff_required": True,
                "execution_authority_granted": False,
                "authority_granted": False,
                "final_authority_authorized": False,
                "live_hyperstition_activation_authorized": False,
            }
        )
    return {
        "contract_id": "v2_hygiene_phase20_final_authority_attestation_receipt_contract_001",
        "execution_receipts": receipts,
        "receipt_count": len(receipts),
        "all_receipts_recorded": promotion_recorded,
        "execution_authority_granted": False,
        "final_authority_authorized": False,
        "live_hyperstition_activation_authorized": False,
    }


def _final_authority_attestation_workflow_contract() -> dict[str, Any]:
    fixture = build_brier_decomposition_fixture()
    return {
        "contract_id": "v2_hygiene_phase20_final_authority_attestation_workflow_contract_001",
        "workflow_id": "v2_final_authority_attestation_hyperstition_workflow_001",
        "attestation_grants_authority": False,
        "manual_operator_signoff_required": True,
        "telemetry_only": True,
        "final_authority_attestation_telemetry_only": True,
        "final_authority_attestation_recorded_only": True,
        "live_hyperstition_activation_projection_only": True,
        "live_hyperstition_telemetry_only": True,
        "operator_signoff_required": True,
        "signal_forage_shadow_only": True,
        "global_ingest_hold_respected": True,
        "controlled_authority_grant_denied": True,
        "eternal_recursion_closed_loop_non_authoritative": True,
        "final_attestation_operator_signoff_required": True,
        "hyperstition_propagation_projection_only": True,
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
                "role": "rune_visualization_final_authority_attestation_telemetry",
            },
            {
                "binding_id": "core_oracle_shadow",
                "paths": ["out/oracle/", "core/ingest/"],
                "role": "oracle_shadow_final_authority_attestation_loop",
            },
            {
                "binding_id": "brier_engine_telemetry",
                "paths": ["core/scoring/brier.py", "core/governance/brier_provenance.py"],
                "role": "dual_brier_final_authority_attestation_feedback",
            },
            {
                "binding_id": "live_hyperstition_propagation_loop",
                "paths": ["contracts/governance/v2_hyperstition_anchor.v1.schema.json"],
                "role": "live_hyperstition_anchor_projection",
            },
            {
                "binding_id": "eternal_recursion_closed_loop",
                "paths": ["docs/status/continuity-spine.json", "PLANS.md"],
                "role": "eternal_recursion_closed_loop_advisory_projection",
            },
            {
                "binding_id": "signal_forage_final_authority_closed_loop",
                "paths": list(SIGNAL_FORAGE_SHADOW_PATHS),
                "role": "global_ingest_shadow_final_authority_attestation_binding",
            },
        ],
        "decomposition_mode": fixture["decomposition_mode"],
        "murphy_decomposition_default": True,
        "yates_decomposition_default": True,
        "execution_authority_granted": False,
        "final_authority_authorized": False,
        "live_hyperstition_activation_authorized": False,
    }


def _live_hyperstition_activation_contract() -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase20_live_hyperstition_activation_contract_001",
        "telemetry_only": True,
        "projection_only": True,
        "live_hyperstition_activation_authorized": False,
        "hyperstition_propagation_projection_only": True,
        "live_hyperstition_telemetry_only": True,
        "live_hyperstition_activation_projection_only": True,
        "eternal_recursion_closed_loop_non_authoritative": True,
        "final_authority_attestation_recorded_only": True,
        "operator_signoff_required": True,
        "execution_authority_granted": False,
        "final_authority_authorized": False,
        "hyperstition_engine_authorized": False,
        "eternal_canon_self_governance_authorized": False,
    }


def _signal_forage_final_authority_closed_loop_contract(repo_root: Path) -> dict[str, Any]:
    signal_forager = build_signal_forager_final_authority_attestation_contract()
    path_observations = [
        {
            "path": path,
            "observed": _path_observed(repo_root, path),
            "file_hash": _sha256(repo_root / path) if _path_observed(repo_root, path) else NOT_COMPUTABLE,
        }
        for path in SIGNAL_FORAGE_SHADOW_PATHS
    ]
    return {
        "contract_id": "v2_hygiene_phase20_signal_forage_final_authority_closed_loop_contract_001",
        "shadow_only": True,
        "telemetry_only": True,
        "final_authority_closed_loop_bound": True,
        "eternal_canon_self_governance_loop_bound": True,
        "eternal_self_sustaining_loop_bound": True,
        "closed_loop_bound": True,
        "signal_forage_bound": True,
        "global_ingest_hold_respected": True,
        "global_ingest_adapter_spine_hold_active": True,
        "signal_forager_contract_id": signal_forager["contract_id"],
        "base_signal_forager_contract_id": build_signal_forager_brier_contract()["contract_id"],
        "decomposition_mode": signal_forager["decomposition_mode"],
        "global_ingest_shadow_paths": list(SIGNAL_FORAGE_SHADOW_PATHS),
        "path_observations": path_observations,
        "all_paths_observed": all(item["observed"] for item in path_observations),
        "final_authority_closed_loop_bindings": signal_forager["final_authority_closed_loop_bindings"],
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
    }


def _final_authority_guard_hardening_contract() -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase20_final_authority_guard_hardening_contract_001",
        "telemetry_only": True,
        "advisory_only": True,
        "projection_only": True,
        "final_authority_authorized": False,
        "controlled_authority_grant_denied": True,
        "eternal_canon_self_governance_authorized": False,
        "live_hyperstition_activation_authorized": False,
        "execution_authority_granted": False,
        "auto_promotion_projection_only": True,
        "self_auditing_advisory_only": True,
        "operator_signoff_required": True,
        "live_hyperstition_telemetry_only": True,
        "live_hyperstition_activation_projection_only": True,
        "final_authority_attestation_recorded_only": True,
        "eternal_recursion_closed_loop_non_authoritative": True,
        "final_attestation_operator_signoff_required": True,
        "runtime_guards": _runtime_guards(),
    }


def _final_authority_brier_telemetry_contract() -> dict[str, Any]:
    fixture_decomposition = compute_full_decomposition(
        BRIER_FINAL_AUTHORITY_ATTESTATION_FIXTURE_PREDICTIONS,
        BRIER_FINAL_AUTHORITY_ATTESTATION_FIXTURE_TARGETS,
    )
    hooks = []
    for surface_id in FINAL_AUTHORITY_ATTESTATION_HYPERSTITION_PROMOTION_CLASSES:
        hook = {
            "claim_id": surface_id,
            "forecast_probability": 0.92,
            "binary_outcome": NOT_COMPUTABLE,
            "brier_score": NOT_COMPUTABLE,
            "resolution_source": "core/governance/brier_provenance.py",
            "resolution_allowed": False,
            "brier_resolution_authorized": False,
            "promotion_tier": "FINAL_AUTHORITY_ATTESTATION",
            "operator_signoff_required": True,
            "signal_forage_bound": True,
            "self_optimization_bound": True,
            "eternal_recursion_bound": True,
            "hyperstition_bound": True,
            "eternal_canon_self_governance_bound": True,
            "live_hyperstition_bound": True,
            "final_authority_attestation_bound": True,
            "final_authority_attestation_promotion": True,
            "final_authority_bound": False,
            "decomposition": fixture_decomposition,
            "adversarial_calibration_blockers": [],
        }
        hook["adversarial_calibration_blockers"] = validate_adversarial_calibration(hook)
        hooks.append(hook)
    hooks.append(
        {
            "claim_id": "final_authority_attestation_dual_brier_decomposition",
            "forecast_probability": compute_brier_score(0.86, 0.0),
            "binary_outcome": NOT_COMPUTABLE,
            "brier_score": NOT_COMPUTABLE,
            "resolution_source": "core/scoring/brier.py",
            "resolution_allowed": False,
            "brier_resolution_authorized": False,
            "promotion_tier": "FINAL_AUTHORITY_ATTESTATION",
            "operator_signoff_required": True,
            "signal_forage_bound": True,
            "self_optimization_bound": True,
            "eternal_recursion_bound": True,
            "hyperstition_bound": True,
            "eternal_canon_self_governance_bound": True,
            "live_hyperstition_bound": True,
            "final_authority_attestation_bound": True,
            "final_authority_attestation_promotion": True,
            "final_authority_bound": False,
            "decomposition": fixture_decomposition,
            "adversarial_calibration_blockers": validate_adversarial_calibration(
                {
                    "claim_id": "final_authority_attestation_dual_brier_decomposition",
                    "forecast_probability": compute_brier_score(0.86, 0.0),
                    "binary_outcome": NOT_COMPUTABLE,
                    "brier_score": NOT_COMPUTABLE,
                    "resolution_allowed": False,
                    "brier_resolution_authorized": False,
                }
            ),
        }
    )
    governance_packet = build_brier_final_authority_attestation_hyperstition_packet()
    signal_forager = build_signal_forager_final_authority_attestation_contract()
    return {
        "contract_id": "v2_hygiene_phase20_final_authority_brier_telemetry_contract_001",
        "telemetry_only": True,
        "runtime_telemetry_only": True,
        "final_authority_attestation_telemetry_only": True,
        "final_authority_attestation_promotion": True,
        "live_hyperstition_bound": True,
        "hyperstition_bound": True,
        "eternal_recursion_bound": True,
        "eternal_canon_self_governance_bound": True,
        "signal_forage_bound": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "decomposition_mode": DECOMPOSITION_MODE,
        "murphy_decomposition_default": True,
        "yates_decomposition_default": True,
        "operator_signoff_required": True,
        "fixture_decomposition": fixture_decomposition,
        "final_authority_attestation_packet": governance_packet,
        "telemetry_hooks": hooks,
        "signal_forage_binding": {
            "paths": list(SIGNAL_FORAGE_SHADOW_PATHS),
            "signal_forager_contract_id": signal_forager["contract_id"],
            "decomposition_mode": signal_forager["decomposition_mode"],
        },
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
        "live_hyperstition_anchor_binding": {
            "paths": ["contracts/governance/v2_hyperstition_anchor.v1.schema.json"],
            "decomposition_mode": DECOMPOSITION_MODE,
        },
        "eternal_recursion_closed_loop_binding": {
            "paths": ["docs/status/continuity-spine.json", "PLANS.md"],
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
    }


def _brier_scoring_contract() -> dict[str, Any]:
    final_authority = _final_authority_brier_telemetry_contract()
    return {
        "contract_id": "v2_hygiene_phase20_final_authority_attestation_brier_telemetry_contract_001",
        "telemetry_only": True,
        "brier_score_formula": final_authority["brier_score_formula"],
        "decomposition_mode": final_authority["decomposition_mode"],
        "telemetry_hooks": final_authority["telemetry_hooks"],
        "resolution_allowed": False,
        "brier_resolution_authorized": False,
    }


def _operator_attestation_workflow_contract(*, ready: bool) -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase20_operator_attestation_workflow_contract_001",
        "manual_operator_signoff_required": True,
        "operator_signoff_auto_approved": False,
        "external_operator_attestation_required": True,
        "phase26_handoff_template_path": PHASE26_HANDOFF_TEMPLATE_PATH.as_posix(),
        "notion_writeback_allowed": False,
        "hash_chain_review_required": True,
        "hash_chain": {
            "phase26_gate_hash": EXPECTED_PHASE26_HASH if ready else NOT_COMPUTABLE,
            "phase27_gate_hash": NOT_COMPUTABLE,
        },
        "claims": [
            {
                "field": "phase26_hash_chain_reviewed",
                "classification": "OBSERVED" if ready else "INFERRED",
                "provenance": SOURCE_PHASE26_GATE_JSON_PATH.as_posix(),
                "value": ready,
            },
            {
                "field": "final_authority_attestation_dual_brier_decomposition_active",
                "classification": "OBSERVED" if ready else "SPECULATIVE",
                "provenance": "core/scoring/brier.py",
                "value": ready,
            },
            {
                "field": "signal_forage_final_authority_closed_loop_active",
                "classification": "OBSERVED" if ready else "SPECULATIVE",
                "provenance": "core/governance/signal_forager_brier_hook.py",
                "value": ready,
            },
            {
                "field": "live_hyperstition_activation_projection_only_active",
                "classification": "OBSERVED" if ready else "SPECULATIVE",
                "provenance": "contracts/governance/v2_hyperstition_anchor.v1.schema.json",
                "value": ready,
            },
            {
                "field": "final_authority_attestation_recorded_only_active",
                "classification": "OBSERVED" if ready else "SPECULATIVE",
                "provenance": RECEIPT_ID,
                "value": ready,
            },
            {
                "field": "final_authority_remains_denied",
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
        "contract_id": "v2_hygiene_phase20_dependency_denial_contract_001",
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
                "Phase 26 eternal canon self-governance promotion and final authority "
                "attestation hyperstition path observation"
            ),
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": (
                "Phase 26 hash linkage and final authority attestation hyperstition surface "
                "binding with signal forage final authority closed loop"
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
                "global ingest hold, uncontrolled live execution, and high-risk mutations held"
            ),
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Weigh",
            "governance_mapping": (
                "Murphy+Yates final-authority attestation Brier telemetry with signal forage "
                "final authority closed loop and live hyperstition activation projection "
                "on all promoted surfaces"
            ),
            "authority_granted": False,
            "risk_level": "LOW",
            "decomposition_mode": fixture["decomposition_mode"],
        },
        {
            "rune": "Seal",
            "governance_mapping": (
                "Phase 27 final authority attestation hyperstition gate only; "
                "gate does not grant execution authority, adaptive learning, eternal recursion, "
                "hyperstition engine authority, final authority, eternal canon self-governance "
                "authority, or live hyperstition activation authority"
            ),
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(
    repo_root: str | Path = ".",
    *,
    source_phase26_gate_path: str | Path = SOURCE_PHASE26_GATE_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_phase26_gate_path)
    phase26 = _read_json(_resolve(root, source_path)) or {}
    blockers: list[str] = []
    if not phase26:
        blockers.append("required_phase26_eternal_canon_self_governance_gate_missing")
    else:
        blockers.extend(_phase26_blockers(phase26))
    if not (root / PHASE26_HANDOFF_TEMPLATE_PATH).exists():
        blockers.append("phase26_handoff_template_missing")
    phase26_ready = bool(phase26) and not any(
        blocker.startswith("phase26_")
        or blocker.startswith("required_phase26")
        or blocker == "phase26_handoff_template_missing"
        for blocker in blockers
    )
    for entry in FULL_OPERATOR_EXECUTION_AUTONOMY_MATRIX:
        for path in entry["paths"]:
            if not _path_observed(root, path):
                blockers.append(
                    f"final_authority_attestation_hyperstition_surface_path_missing:{entry['surface_id']}"
                )
    for path in SIGNAL_FORAGE_SHADOW_PATHS:
        if not _path_observed(root, path):
            blockers.append(f"signal_forage_final_authority_closed_loop_path_missing:{path}")
    blockers = sorted(set(blockers))
    gate_ready = phase26_ready and not blockers
    promotion_contract = _final_authority_attestation_promotion_contract(
        root,
        promotion_recorded=gate_ready,
    )
    status = READY_STATUS if gate_ready else BLOCKED_STATUS
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "operator_phase_number": OPERATOR_PHASE_NUMBER,
        "status": status,
        "sources_observed": bool(phase26),
        "source_records": [
            _source_record(
                "phase26_eternal_canon_self_governance_gate",
                source_path,
                phase26,
            )
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if phase26_ready else "SOURCE_ARTIFACTS_NOT_READY",
        "final_authority_attestation_hyperstition_gate_ready": gate_ready,
        "phase26_eternal_canon_self_governance_gate_hash_verified": phase26_ready,
        "planning_lane_status": phase26.get("planning_lane_status", NOT_COMPUTABLE) if phase26 else NOT_COMPUTABLE,
        "planning_lane_activated": phase26.get("planning_lane_activated", False) if phase26 else False,
        "final_authority_attestation_promotion_contract": promotion_contract,
        "final_authority_attestation_receipt_contract": _final_authority_attestation_receipt_contract(
            promotion_recorded=gate_ready,
        ),
        "final_authority_attestation_workflow_contract": _final_authority_attestation_workflow_contract(),
        "live_hyperstition_activation_contract": _live_hyperstition_activation_contract(),
        "signal_forage_final_authority_closed_loop_contract": (
            _signal_forage_final_authority_closed_loop_contract(root)
        ),
        "final_authority_guard_hardening_contract": _final_authority_guard_hardening_contract(),
        "final_authority_brier_telemetry_contract": _final_authority_brier_telemetry_contract(),
        "operator_attestation_workflow_contract": _operator_attestation_workflow_contract(ready=phase26_ready),
        "dependency_denial_contract": _dependency_denial_contract(),
        "brier_scoring_contract": _brier_scoring_contract(),
        "rune_governance_mapping": _rune_governance_mapping(),
        "recommended_next_action": (
            "final authority attestation hyperstition promotion recorded for eternal-canon "
            "self-governance surfaces with signal forage final authority closed loop integration, "
            "live hyperstition activation projection-only posture, final authority attestation "
            "recorded-only workflow, and dual Murphy+Yates Brier telemetry; gate does not grant "
            "execution authority, adaptive learning, self-optimization authority, eternal recursion "
            "authority, hyperstition engine authority, final authority, eternal canon self-governance "
            "authority, or live hyperstition activation authority; global ingest hold and "
            "high-risk mutations remain fail-closed"
            if gate_ready
            else (
                "restore the Phase 26 eternal canon self-governance gate before "
                "final authority attestation hyperstition promotion"
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
        "valid_for_planning_lane": phase26_ready,
        "valid_for_controlled_writeback": phase26_ready,
        "valid_for_controlled_execution": phase26_ready,
        "valid_for_rune_viz_integration": phase26_ready,
        "valid_for_operator_execution_autonomy_eligibility": phase26_ready,
        "valid_for_operator_execution_autonomy_activation": phase26_ready,
        "valid_for_autonomy_hardening": phase26_ready,
        "valid_for_runtime_execution_activation": phase26_ready,
        "valid_for_controlled_runtime_execution_promotion": phase26_ready,
        "valid_for_live_runtime_execution": phase26_ready,
        "valid_for_full_live_autonomy_self_optimization": phase26_ready,
        "valid_for_eternal_recursion_hyperstition": phase26_ready,
        "valid_for_eternal_canon_self_governance": phase26_ready,
        "valid_for_final_authority_attestation_hyperstition": gate_ready,
        "valid_for_execution": False,
        "valid_for_promotion": False,
        "valid_for_activation": False,
        "operator_signoff_auto_approved": False,
        "external_operator_attestation_required": True,
        "operator_review_posture": "ACTIVE",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "authority_locks": _copied_authority_locks(phase26),
        "final_authority_attestation_hyperstition_gate_hash": "",
    }
    packet["final_authority_attestation_hyperstition_gate_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "final_authority_attestation_hyperstition_gate_hash"
        }
    )
    return packet


def render_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    promotion = packet["final_authority_attestation_promotion_contract"]
    denial = packet["dependency_denial_contract"]
    workflow = packet["operator_attestation_workflow_contract"]
    brier_final = packet["final_authority_brier_telemetry_contract"]
    signal_forage = packet["signal_forage_final_authority_closed_loop_contract"]
    final_authority_guard = packet["final_authority_guard_hardening_contract"]
    live_hyperstition = packet["live_hyperstition_activation_contract"]
    lines = [
        "# v2.0 Hygiene Phase 20 Final Authority Attestation Hyperstition Gate (Operator Phase 27)",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- operator_phase_number: {packet['operator_phase_number']}",
        f"- status: {packet['status']}",
        f"- valid_for_final_authority_attestation_hyperstition: {packet['valid_for_final_authority_attestation_hyperstition']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- live_hyperstition_activation_authorized: {packet['live_hyperstition_activation_authorized']}",
        f"- operator_review_posture: {packet['operator_review_posture']}",
        "",
        "## Hash Chain",
        f"- phase26_gate_hash: {workflow['hash_chain']['phase26_gate_hash']}",
        f"- phase27_gate_hash: {packet['final_authority_attestation_hyperstition_gate_hash']}",
        "",
        "## Final Authority Attestation Hyperstition Promotion Matrix",
    ]
    for surface in promotion["final_authority_attestation_hyperstition_promotion_matrix"]:
        lines.append(
            f"- {surface['surface_id']}: {surface['promotion_class']} "
            f"promotion_recorded={surface['final_authority_attestation_hyperstition_recorded']}"
        )
    lines.extend(
        [
            "",
            "## Signal Forage Final Authority Closed Loop Contract",
            f"- shadow_only: {signal_forage['shadow_only']}",
            f"- final_authority_closed_loop_bound: {signal_forage['final_authority_closed_loop_bound']}",
            f"- global_ingest_hold_respected: {signal_forage['global_ingest_hold_respected']}",
            f"- signal_forager_contract_id: {signal_forage['signal_forager_contract_id']}",
            "",
            "## Live Hyperstition Activation Contract",
            f"- live_hyperstition_activation_authorized: {live_hyperstition['live_hyperstition_activation_authorized']}",
            f"- hyperstition_propagation_projection_only: {live_hyperstition['hyperstition_propagation_projection_only']}",
            "",
            "## Final Authority Guard Hardening Contract",
            f"- final_authority_authorized: {final_authority_guard['final_authority_authorized']}",
            f"- controlled_authority_grant_denied: {final_authority_guard['controlled_authority_grant_denied']}",
            f"- final_attestation_operator_signoff_required: {final_authority_guard['final_attestation_operator_signoff_required']}",
            "",
            "## Final Authority Brier Telemetry Contract",
            f"- decomposition_mode: {brier_final['decomposition_mode']}",
            f"- murphy_decomposition_default: {brier_final['murphy_decomposition_default']}",
            f"- yates_decomposition_default: {brier_final['yates_decomposition_default']}",
            f"- signal_forage_bound: {brier_final['signal_forage_bound']}",
            f"- final_authority_attestation_telemetry_only: {brier_final['final_authority_attestation_telemetry_only']}",
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


def write_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
    source_phase26_gate_path: str | Path = SOURCE_PHASE26_GATE_JSON_PATH,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate(
        repo_root,
        source_phase26_gate_path=source_phase26_gate_path,
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase20_final_authority_attestation_hyperstition_gate_markdown(packet)
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
