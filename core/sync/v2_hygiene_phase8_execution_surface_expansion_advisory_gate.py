from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.scoring.brier import compute_brier_score
from core.sync.v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate import (
    RECEIPT_JSON_PATH as SOURCE_PHASE14_GATE_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygienePhase8ExecutionSurfaceExpansionAdvisoryGate.v1"
RECEIPT_ID = "v2_hygiene_phase8_execution_surface_expansion_advisory_gate_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase8_execution_surface_expansion_advisory_gate_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
READY_STATUS = "V2_HYGIENE_PHASE8_EXECUTION_SURFACE_EXPANSION_ADVISORY_GATE_READY"
BLOCKED_STATUS = "V2_HYGIENE_PHASE8_EXECUTION_SURFACE_EXPANSION_ADVISORY_GATE_BLOCKED"
EXPECTED_PHASE14_STATUS = (
    "V2_HYGIENE_PHASE14_OPERATOR_SIGNOFF_PLANNING_LANE_ACTIVATION_GATE_READY"
)
EXPECTED_PHASE14_HASH = "25f6e08d8e8c9a4239457c9274961eba68b630cbe1ffa51e742d839fa98b7945"
EXPECTED_PHASE14_PLANNING_LANE_STATUS = "PLANNING_LANE_ACTIVE_ADVISORY_ONLY"
OPERATOR_PHASE_NUMBER = 15

EXECUTION_SURFACE_EXPANSION_MATRIX = (
    {
        "surface_id": "core_oracle_shadow",
        "paths": ["out/oracle/", "core/ingest/"],
        "promotion_class": "ADVISORY_PROMOTED_SHADOW_READ",
        "write_posture": "advisory_shadow_intake_only_execution_denied",
    },
    {
        "surface_id": "brier_engine_telemetry",
        "paths": ["core/scoring/brier.py", "core/governance/brier_provenance.py"],
        "promotion_class": "ADVISORY_PROMOTED_TELEMETRY_READ",
        "write_posture": "telemetry_only_brier_resolution_denied",
    },
    {
        "surface_id": "planning_lane_outputs",
        "paths": [
            "out/operator_review/v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate_001.latest.json",
            "docs/plans/phase14_slang_memetic_rune_activation.md",
        ],
        "promotion_class": "ADVISORY_PROMOTED_PLANNING_READ",
        "write_posture": "planning_lane_advisory_read_execution_denied",
    },
    {
        "surface_id": "aal_viz_projection_hooks",
        "paths": [
            "apps/aal-viz-live-console/public/projection-bundle.json",
            "apps/aal-viz-live-console/public/operator-action-packets.json",
            "core/aal_viz_runtime_projection.py",
        ],
        "promotion_class": "ADVISORY_PROMOTED_PROJECTION_READ",
        "write_posture": "projection_hook_read_controlled_write_runtime_mutation_denied",
    },
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
    "execution_surface_expansion_authorized",
    "advisory_promotion_authorized",
    "phase16_activation_authorized",
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
        "controlled_writeback",
        "dependency_mutation",
        "execution_authority",
        "execution_surface_expansion",
        "forecast_routing",
        "github_writeback",
        "notion_writeback",
        "package_lock_mutation",
        "planning_lane_execution",
        "promotion",
        "queue_mutation",
        "rune_registration",
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
        "packet_hash": str(
            packet.get("operator_signoff_planning_lane_activation_gate_hash", NOT_COMPUTABLE)
        ),
        "expected_packet_hash": EXPECTED_PHASE14_HASH,
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_PHASE14_STATUS,
        "authority_locks_all_false": (
            True
            if packet.get("authority_locks") is None
            else _locks_all_false(packet.get("authority_locks"))
        ),
        "planning_lane_activated": packet.get("planning_lane_activated", NOT_COMPUTABLE),
        "planning_lane_status": packet.get("planning_lane_status", NOT_COMPUTABLE),
        "operator_review_posture": packet.get("operator_review_posture", NOT_COMPUTABLE),
        "recommended_next_lane": packet.get("recommended_next_lane", NOT_COMPUTABLE),
        "downstream": packet.get("downstream", NOT_COMPUTABLE),
    }


def _phase14_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if packet.get("status") != EXPECTED_PHASE14_STATUS:
        blockers.append("phase14_planning_lane_gate_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("phase14_source_not_ready")
    if packet.get("source_blockers") != []:
        blockers.append("phase14_source_blockers_not_empty")
    if packet.get("operator_signoff_planning_lane_activation_gate_ready") is not True:
        blockers.append("phase14_planning_lane_gate_ready_not_true")
    if packet.get("operator_signoff_planning_lane_activation_gate_hash") != EXPECTED_PHASE14_HASH:
        blockers.append("phase14_planning_lane_gate_hash_mismatch")
    without_hash = dict(packet)
    observed_hash = without_hash.pop(
        "operator_signoff_planning_lane_activation_gate_hash", NOT_COMPUTABLE
    )
    if canonical_hash(without_hash) != observed_hash:
        blockers.append("phase14_planning_lane_gate_self_hash_mismatch")
    if packet.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append("phase14_recommended_lane_mismatch")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("phase14_downstream_not_closed")
    if packet.get("planning_lane_activated") is not True:
        blockers.append("phase14_planning_lane_not_activated")
    if packet.get("planning_lane_status") != EXPECTED_PHASE14_PLANNING_LANE_STATUS:
        blockers.append("phase14_planning_lane_status_mismatch")
    if packet.get("operator_review_posture") != "ACTIVE":
        blockers.append("phase14_operator_review_posture_not_active")
    if packet.get("valid_for_execution") is True:
        blockers.append("phase14_execution_authority_not_denied")
    locks = packet.get("authority_locks")
    if locks is not None and not _locks_all_false(locks):
        blockers.append("phase14_authority_locks_not_false")
    blockers.extend(_authority_expansion_blockers("phase14_planning_lane_gate", packet))
    return blockers


def _execution_surface_expansion_contract(repo_root: Path) -> dict[str, Any]:
    surfaces = []
    for entry in EXECUTION_SURFACE_EXPANSION_MATRIX:
        path_observations = [
            {
                "path": path,
                "observed": _path_observed(repo_root, path),
                "file_hash": _sha256(repo_root / path) if _path_observed(repo_root, path) else NOT_COMPUTABLE,
            }
            for path in entry["paths"]
        ]
        surfaces.append(
            {
                "surface_id": entry["surface_id"],
                "paths": list(entry["paths"]),
                "promotion_class": entry["promotion_class"],
                "write_posture": entry["write_posture"],
                "path_observations": path_observations,
                "all_paths_observed": all(item["observed"] for item in path_observations),
                "authority_granted": False,
                "advisory_promotion_only": True,
                "operator_review_required": True,
                "execution_denied": True,
            }
        )
    return {
        "contract_id": "v2_hygiene_phase8_execution_surface_expansion_contract_001",
        "execution_surface_expansion_matrix": surfaces,
        "surface_count": len(surfaces),
        "advisory_promotion_only": True,
        "promotion_authorized": False,
        "execution_surface_expansion_authorized": False,
    }


def _planning_lane_inheritance_contract(phase14: Mapping[str, Any]) -> dict[str, Any]:
    planning = phase14.get("planning_lane_activation_contract", {})
    return {
        "contract_id": "v2_hygiene_phase8_planning_lane_inheritance_contract_001",
        "inherited_from": "v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate_001",
        "planning_lane_status": phase14.get("planning_lane_status", NOT_COMPUTABLE),
        "planning_lane_activated": phase14.get("planning_lane_activated", False),
        "planning_lane_execution_denied": True,
        "inherited_planning_surfaces": planning.get("planning_surface_matrix", []),
        "surface_count": len(planning.get("planning_surface_matrix", [])),
        "activation_authority_granted": False,
        "implementation_authority_granted": False,
    }


def _advisory_promotion_hash_chain_contract(*, ready: bool) -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase8_advisory_promotion_hash_chain_contract_001",
        "hash_chain_review_required": True,
        "hash_chain": {
            "phase14_gate_hash": EXPECTED_PHASE14_HASH if ready else NOT_COMPUTABLE,
            "phase15_gate_hash": NOT_COMPUTABLE,
        },
        "manual_operator_review_required": True,
        "notion_writeback_allowed": False,
    }


def _dependency_denial_contract() -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase8_dependency_denial_contract_001",
        "package_lock_mutation_authorized": False,
        "package_lock_tracking_authorized": False,
        "toolchain_provisioning_authorized": False,
        "dependency_mutation_authorized": False,
        "npmrc_stabilization_observed": (Path(".") / "apps/aal-viz-live-console/.npmrc").exists(),
        "package_lock_resolution_held": True,
    }


def _brier_scoring_contract() -> dict[str, Any]:
    hooks = [
        {
            "claim_id": entry["surface_id"],
            "forecast_probability": 0.8,
            "binary_outcome": NOT_COMPUTABLE,
            "brier_score": NOT_COMPUTABLE,
            "resolution_source": NOT_COMPUTABLE,
            "resolution_allowed": False,
        }
        for entry in EXECUTION_SURFACE_EXPANSION_MATRIX
    ]
    hooks.append(
        {
            "claim_id": "execution_surface_expansion_without_execution_authority",
            "forecast_probability": compute_brier_score(0.75, 0.0),
            "binary_outcome": NOT_COMPUTABLE,
            "brier_score": NOT_COMPUTABLE,
            "resolution_source": "core/governance/brier_provenance.py",
            "resolution_allowed": False,
        }
    )
    return {
        "contract_id": "v2_hygiene_phase8_execution_surface_expansion_brier_telemetry_contract_001",
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
            "governance_mapping": "Phase 14 planning lane gate and expanded execution surface observation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": "Phase 14 hash linkage and execution surface path binding",
            "authority_granted": False,
            "risk_level": "MEDIUM",
        },
        {
            "rune": "Hold",
            "governance_mapping": "package-lock, toolchain, dependency mutations, and execution authority held",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Weigh",
            "governance_mapping": "telemetry-only Brier posture for advisory execution surface expansion",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Seal",
            "governance_mapping": "Phase 15 advisory expansion gate only; operator review remains active",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase8_execution_surface_expansion_advisory_gate(
    repo_root: str | Path = ".",
    *,
    source_phase14_gate_path: str | Path = SOURCE_PHASE14_GATE_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_phase14_gate_path)
    phase14 = _read_json(_resolve(root, source_path)) or {}
    blockers: list[str] = []
    if not phase14:
        blockers.append("required_phase14_planning_lane_gate_missing")
    else:
        blockers.extend(_phase14_blockers(phase14))
    expansion_contract = _execution_surface_expansion_contract(root)
    for surface in expansion_contract["execution_surface_expansion_matrix"]:
        if not surface["all_paths_observed"]:
            blockers.append(f"execution_surface_expansion_path_missing:{surface['surface_id']}")
    blockers = sorted(set(blockers))
    ready = bool(phase14) and not blockers
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "operator_phase_number": OPERATOR_PHASE_NUMBER,
        "status": READY_STATUS if ready else BLOCKED_STATUS,
        "sources_observed": bool(phase14),
        "source_records": [
            _source_record("phase14_operator_signoff_planning_lane_activation_gate", source_path, phase14)
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "execution_surface_expansion_advisory_gate_ready": ready,
        "phase14_operator_signoff_planning_lane_activation_gate_hash_verified": ready,
        "planning_lane_status": (
            EXPECTED_PHASE14_PLANNING_LANE_STATUS if ready else phase14.get("planning_lane_status", NOT_COMPUTABLE)
        ),
        "planning_lane_activated": phase14.get("planning_lane_activated", False) if phase14 else False,
        "execution_surface_expansion_contract": expansion_contract,
        "planning_lane_inheritance_contract": _planning_lane_inheritance_contract(phase14),
        "advisory_promotion_hash_chain_contract": _advisory_promotion_hash_chain_contract(ready=ready),
        "dependency_denial_contract": _dependency_denial_contract(),
        "brier_scoring_contract": _brier_scoring_contract(),
        "rune_governance_mapping": _rune_governance_mapping(),
        "recommended_next_action": (
            "hold operator review posture; expanded execution surfaces are advisory-promoted for "
            "read/controlled-write eligibility only; package-lock and dependency mutations remain fail-closed"
            if ready
            else "restore the Phase 14 operator signoff planning lane activation gate before expansion"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "downstream": NOT_COMPUTABLE,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "promotion_authorized": False,
        "advisory_promotion_authorized": False,
        "activation_authorized": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "canon_mutation": False,
        "execution_authority": False,
        "execution_surface_expansion_authorized": False,
        "brier_resolution_authorized": False,
        "rune_registration_authorized": False,
        "implementation_authorized": False,
        "package_lock_mutation_authorized": False,
        "toolchain_provisioning_authorized": False,
        "dependency_mutation_authorized": False,
        "valid_for_planning_lane": ready,
        "valid_for_controlled_writeback": ready,
        "valid_for_advisory_promotion": ready,
        "valid_for_execution": False,
        "valid_for_promotion": False,
        "valid_for_activation": False,
        "operator_signoff_auto_approved": False,
        "operator_review_posture": "ACTIVE",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "authority_locks": _copied_authority_locks(phase14),
        "execution_surface_expansion_advisory_gate_hash": "",
    }
    packet["execution_surface_expansion_advisory_gate_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "execution_surface_expansion_advisory_gate_hash"
        }
    )
    return packet


def render_v2_hygiene_phase8_execution_surface_expansion_advisory_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    expansion = packet["execution_surface_expansion_contract"]
    denial = packet["dependency_denial_contract"]
    hash_chain = packet["advisory_promotion_hash_chain_contract"]
    lines = [
        "# v2.0 Hygiene Phase 8 Execution Surface Expansion Advisory Gate (Operator Phase 15)",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- operator_phase_number: {packet['operator_phase_number']}",
        f"- status: {packet['status']}",
        f"- planning_lane_status: {packet['planning_lane_status']}",
        f"- execution_surface_expansion_advisory_gate_ready: {packet['execution_surface_expansion_advisory_gate_ready']}",
        f"- operator_review_posture: {packet['operator_review_posture']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- valid_for_advisory_promotion: {packet['valid_for_advisory_promotion']}",
        "",
        "## Hash Chain",
        f"- phase14_gate_hash: {hash_chain['hash_chain']['phase14_gate_hash']}",
        f"- phase15_gate_hash: {hash_chain['hash_chain']['phase15_gate_hash']}",
        "",
        "## Execution Surface Expansion Matrix",
    ]
    for surface in expansion["execution_surface_expansion_matrix"]:
        lines.append(
            f"- {surface['surface_id']}: {surface['promotion_class']} "
            f"paths={surface['paths']} observed={surface['all_paths_observed']}"
        )
    lines.extend(
        [
            "",
            "## Dependency Denial Contract",
            f"- package_lock_mutation_authorized: {denial['package_lock_mutation_authorized']}",
            f"- toolchain_provisioning_authorized: {denial['toolchain_provisioning_authorized']}",
            f"- dependency_mutation_authorized: {denial['dependency_mutation_authorized']}",
            "",
            "## Source Blockers",
        ]
    )
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase8_execution_surface_expansion_advisory_gate(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase8_execution_surface_expansion_advisory_gate(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase8_execution_surface_expansion_advisory_gate_markdown(packet)
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
