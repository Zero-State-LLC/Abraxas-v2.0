from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase5_controlled_writeback_activation_gate import (
    RECEIPT_JSON_PATH as SOURCE_PHASE11_GATE_JSON_PATH,
)

SCHEMA_VERSION = "V2HygienePhase6ExecutionSurfacePromotionGate.v1"
RECEIPT_ID = "v2_hygiene_phase6_execution_surface_promotion_gate_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase6_execution_surface_promotion_gate_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
READY_STATUS = "V2_HYGIENE_PHASE6_EXECUTION_SURFACE_PROMOTION_GATE_READY"
BLOCKED_STATUS = "V2_HYGIENE_PHASE6_EXECUTION_SURFACE_PROMOTION_GATE_BLOCKED"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
EXPECTED_PHASE11_STATUS = "V2_HYGIENE_PHASE5_CONTROLLED_WRITEBACK_ACTIVATION_GATE_READY"
EXPECTED_PHASE11_HASH = "5241dd8113f326f01799c96bd70f534ffccbca957fc10687feaeb69815f757e3"
EXPECTED_PHASE11_RECOMMENDED_LANE = "V2_HYGIENE_PHASE6_EXECUTION_SURFACE_PROMOTION_GATE_001"

EXECUTION_SURFACE_MATRIX = (
    {
        "surface_id": "core_governance_modules",
        "paths": ["core/governance/", "core/receipts/"],
        "promotion_class": "PROMOTED_CONTROLLED_WRITE",
        "write_posture": "read_plus_governed_write_when_review_passes",
    },
    {
        "surface_id": "brier_engine",
        "paths": ["core/sync/"],
        "promotion_class": "PROMOTED_TELEMETRY_READ",
        "write_posture": "telemetry_only_brier_resolution_denied",
    },
    {
        "surface_id": "oracle_hooks",
        "paths": ["out/oracle/"],
        "promotion_class": "PROMOTED_SHADOW_READ",
        "write_posture": "advisory_shadow_intake_only",
    },
    {
        "surface_id": "runtime_surface",
        "paths": ["out/audit/runtime_integration_gate_receipt_001.latest.json"],
        "promotion_class": "PROMOTED_READ_CONTROLLED_WRITE",
        "write_posture": "read_plus_controlled_write_runtime_mutation_denied",
    },
    {
        "surface_id": "canon_surface",
        "paths": ["out/canon_resume_state/", "docs/status/continuity-spine.json"],
        "promotion_class": "PROMOTED_READ_CONTROLLED_WRITE",
        "write_posture": "read_plus_controlled_write_canon_mutation_denied",
    },
    {
        "surface_id": "queue_surface",
        "paths": ["out/ingest/oracle_intake_queue_001.latest.json"],
        "promotion_class": "PROMOTED_READ_CONTROLLED_WRITE",
        "write_posture": "read_plus_controlled_write_queue_mutation_denied",
    },
    {
        "surface_id": "scheduler_surface",
        "paths": ["out/audit/controlled_ingest_scheduler_governance_audit_001.latest.json"],
        "promotion_class": "PROMOTED_READ_CONTROLLED_WRITE",
        "write_posture": "read_plus_controlled_write_scheduler_mutation_denied",
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
    "package_lock_mutation_authorized",
    "package_lock_tracking_authorized",
    "package_lock_tracking_performed",
    "v2_module_registration_authorized",
    "rune_registration_authorized",
    "implementation_authorized",
    "valid_for_writeback",
    "valid_for_promotion",
    "valid_for_activation",
    "valid_for_execution",
    "valid_for_implementation",
    "valid_for_package_lock_tracking",
    "safe_to_auto_continue",
    "dependency_mutation_authorized",
    "toolchain_provisioning_authorized",
    "uncontrolled_writeback_authorized",
    "execution_surface_promotion_authorized",
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
    resolved = repo_root / path
    return resolved.exists()


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
        "execution_surface_promotion",
        "forecast_routing",
        "github_writeback",
        "notion_writeback",
        "package_lock_mutation",
        "package_lock_tracking",
        "promotion",
        "queue_mutation",
        "rune_registration",
        "runtime_mutation",
        "scheduler_mutation",
        "toolchain_provisioning",
        "uncontrolled_writeback",
        "v2_module_registration",
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
            packet.get("controlled_writeback_activation_gate_hash", NOT_COMPUTABLE)
        ),
        "expected_packet_hash": EXPECTED_PHASE11_HASH,
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_PHASE11_STATUS,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "controlled_writeback_enabled": packet.get("controlled_writeback_enabled", NOT_COMPUTABLE),
        "recommended_next_lane": packet.get("recommended_next_lane", NOT_COMPUTABLE),
        "downstream": packet.get("downstream", NOT_COMPUTABLE),
    }


def _phase11_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers = []
    if packet.get("status") != EXPECTED_PHASE11_STATUS:
        blockers.append("phase11_controlled_writeback_gate_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("phase11_source_not_ready")
    if packet.get("source_blockers") != []:
        blockers.append("phase11_source_blockers_not_empty")
    if packet.get("controlled_writeback_activation_gate_ready") is not True:
        blockers.append("phase11_controlled_writeback_activation_gate_ready_not_true")
    if packet.get("controlled_writeback_activation_gate_hash") != EXPECTED_PHASE11_HASH:
        blockers.append("phase11_controlled_writeback_activation_gate_hash_mismatch")
    without_hash = dict(packet)
    observed_hash = without_hash.pop(
        "controlled_writeback_activation_gate_hash", NOT_COMPUTABLE
    )
    if canonical_hash(without_hash) != observed_hash:
        blockers.append("phase11_controlled_writeback_activation_gate_self_hash_mismatch")
    if packet.get("recommended_next_lane") != EXPECTED_PHASE11_RECOMMENDED_LANE:
        blockers.append("phase11_recommended_lane_mismatch")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("phase11_downstream_not_closed")
    if packet.get("controlled_writeback_enabled") is not True:
        blockers.append("phase11_controlled_writeback_not_enabled")
    if not _locks_all_false(packet.get("authority_locks")):
        blockers.append("phase11_authority_locks_not_false")
    blockers.extend(_authority_expansion_blockers("phase11_controlled_writeback_gate", packet))
    return blockers


def _execution_surface_promotion_contract(repo_root: Path) -> dict[str, Any]:
    surfaces = []
    for entry in EXECUTION_SURFACE_MATRIX:
        path_observations = [
            {
                "path": path,
                "observed": _path_observed(repo_root, path),
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
                "operator_review_required": True,
            }
        )
    return {
        "contract_id": "v2_hygiene_phase6_execution_surface_promotion_contract_001",
        "execution_surface_matrix": surfaces,
        "surface_count": len(surfaces),
        "promotion_authorized": False,
        "execution_surface_promotion_authorized": False,
    }


def _controlled_writeback_inheritance_contract(phase11: Mapping[str, Any]) -> dict[str, Any]:
    writeback = phase11.get("controlled_writeback_contract", {})
    surfaces = writeback.get("controlled_writeback_surfaces", [])
    return {
        "contract_id": "v2_hygiene_phase6_controlled_writeback_inheritance_contract_001",
        "inherited_from": "v2_hygiene_phase5_controlled_writeback_activation_gate_001",
        "controlled_writeback_enabled": phase11.get("controlled_writeback_enabled", False),
        "inherited_surfaces": surfaces if isinstance(surfaces, list) else [],
        "surface_count": len(surfaces) if isinstance(surfaces, list) else 0,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "uncontrolled_writeback_authorized": False,
    }


def _dependency_denial_contract(phase11: Mapping[str, Any]) -> dict[str, Any]:
    denial = phase11.get("dependency_denial_contract", {})
    return {
        "contract_id": "v2_hygiene_phase6_dependency_denial_contract_001",
        "inherited_from": "v2_hygiene_phase5_controlled_writeback_activation_gate_001",
        "package_lock_mutation_authorized": False,
        "package_lock_tracking_authorized": False,
        "package_lock_tracking_performed": False,
        "package_json_mutation_authorized": False,
        "npmrc_mutation_authorized": False,
        "gitignore_mutation_authorized": False,
        "toolchain_provisioning_authorized": False,
        "dependency_mutation_authorized": False,
        "package_lock_resolution_held": True,
        "package_lock_resolution_ready": False,
        "npmrc_stabilization_observed": denial.get("npmrc_stabilization_observed", False),
        "npmrc_path": denial.get("npmrc_path", "apps/aal-viz-live-console/.npmrc"),
    }


def _brier_scoring_contract() -> dict[str, Any]:
    hooks = [
        {
            "claim_id": entry["surface_id"],
            "forecast_probability": 0.75,
            "binary_outcome": NOT_COMPUTABLE,
            "brier_score": NOT_COMPUTABLE,
            "resolution_source": NOT_COMPUTABLE,
            "resolution_allowed": False,
        }
        for entry in EXECUTION_SURFACE_MATRIX
    ]
    return {
        "contract_id": "v2_hygiene_phase6_execution_surface_promotion_brier_telemetry_contract_001",
        "telemetry_only": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "telemetry_hooks": hooks,
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
            "governance_mapping": "Phase 11 controlled writeback gate and execution surface observation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": "Phase 11 hash linkage and execution surface path binding",
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
            "governance_mapping": "telemetry-only Brier posture for execution surface promotion risk",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Seal",
            "governance_mapping": "execution surface promotion gate only, operator review posture active",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase6_execution_surface_promotion_gate(
    repo_root: str | Path = ".",
    *,
    source_phase11_gate_path: str | Path = SOURCE_PHASE11_GATE_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_phase11_gate_path)
    phase11 = _read_json(_resolve(root, source_path)) or {}
    blockers = []
    if not phase11:
        blockers.append("required_phase11_controlled_writeback_gate_missing")
    else:
        blockers.extend(_phase11_blockers(phase11))
    promotion_contract = _execution_surface_promotion_contract(root)
    for surface in promotion_contract["execution_surface_matrix"]:
        if not surface["all_paths_observed"]:
            blockers.append(f"execution_surface_path_missing:{surface['surface_id']}")
    blockers = sorted(set(blockers))
    ready = bool(phase11) and not blockers
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": READY_STATUS if ready else BLOCKED_STATUS,
        "sources_observed": bool(phase11),
        "source_records": [_source_record("phase11_controlled_writeback_gate", source_path, phase11)],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "execution_surface_promotion_gate_ready": ready,
        "phase11_controlled_writeback_activation_gate_hash_verified": ready,
        "execution_surface_promotion_contract": promotion_contract,
        "controlled_writeback_inheritance_contract": _controlled_writeback_inheritance_contract(
            phase11
        ),
        "dependency_denial_contract": _dependency_denial_contract(phase11),
        "package_lock_resolution_held": True,
        "package_lock_resolution_ready": False,
        "package_lock_tracking_authorized": False,
        "package_lock_tracking_performed": False,
        "package_lock_mutation_authorized": False,
        "package_json_mutation_authorized": False,
        "npmrc_mutation_authorized": False,
        "gitignore_mutation_authorized": False,
        "toolchain_provisioning_authorized": False,
        "dependency_mutation_authorized": False,
        "brier_scoring_contract": _brier_scoring_contract(),
        "rune_governance_mapping": _rune_governance_mapping(),
        "recommended_next_action": (
            "hold operator review posture; execution surfaces promoted for read/controlled-write "
            "eligibility only; package-lock and dependency mutations remain fail-closed"
            if ready
            else "restore the Phase 11 controlled writeback activation gate before promotion"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
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
        "execution_surface_promotion_authorized": False,
        "forecast_routing_authorized": False,
        "adaptive_learning_authorized": False,
        "brier_resolution_authorized": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "implementation_authorized": False,
        "valid_for_writeback": False,
        "valid_for_controlled_writeback": ready,
        "valid_for_promotion": False,
        "valid_for_activation": False,
        "valid_for_package_lock_tracking": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "uncontrolled_writeback_authorized": False,
        "safe_to_auto_continue": False,
        "operator_review_posture": "ACTIVE",
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authority_locks": _copied_authority_locks(phase11),
        "execution_surface_promotion_gate_hash": "",
    }
    packet["execution_surface_promotion_gate_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "execution_surface_promotion_gate_hash"
        }
    )
    return packet


def render_v2_hygiene_phase6_execution_surface_promotion_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    promotion = packet["execution_surface_promotion_contract"]
    denial = packet["dependency_denial_contract"]
    brier = packet["brier_scoring_contract"]
    lines = [
        "# v2.0 Hygiene Phase 6 Execution Surface Promotion Gate",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- execution_surface_promotion_gate_ready: {packet['execution_surface_promotion_gate_ready']}",
        f"- phase11_controlled_writeback_activation_gate_hash_verified: {packet['phase11_controlled_writeback_activation_gate_hash_verified']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- downstream: {packet['downstream']}",
        f"- operator_review_posture: {packet['operator_review_posture']}",
        f"- valid_for_controlled_writeback: {packet['valid_for_controlled_writeback']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Execution Surface Matrix",
    ]
    for surface in promotion["execution_surface_matrix"]:
        lines.append(
            f"- {surface['surface_id']}: {surface['promotion_class']} "
            f"paths={surface['paths']} observed={surface['all_paths_observed']}"
        )
    lines.extend(
        [
            "",
            "## Dependency Denial Contract",
            f"- package_lock_mutation_authorized: {denial['package_lock_mutation_authorized']}",
            f"- package_lock_tracking_authorized: {denial['package_lock_tracking_authorized']}",
            f"- toolchain_provisioning_authorized: {denial['toolchain_provisioning_authorized']}",
            f"- dependency_mutation_authorized: {denial['dependency_mutation_authorized']}",
            f"- npmrc_stabilization_observed: {denial['npmrc_stabilization_observed']}",
            "",
            "## Brier Scoring Contract",
            f"- telemetry_only: {brier['telemetry_only']}",
            f"- resolution_allowed: {brier['resolution_allowed']}",
            f"- promotion_authorized: {brier['promotion_authorized']}",
            f"- brier_resolution_authorized: {brier['brier_resolution_authorized']}",
            "",
            "## Source Blockers",
        ]
    )
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase6_execution_surface_promotion_gate(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase6_execution_surface_promotion_gate(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(render_v2_hygiene_phase6_execution_surface_promotion_gate_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
    return packet
