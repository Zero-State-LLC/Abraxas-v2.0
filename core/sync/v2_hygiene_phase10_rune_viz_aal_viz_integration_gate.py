from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.scoring.brier import compute_brier_score
from core.sync.v2_hygiene_phase9_controlled_execution_promotion_gate import (
    RECEIPT_JSON_PATH as SOURCE_PHASE16_GATE_JSON_PATH,
)

SCHEMA_VERSION = "V2HygienePhase10RuneVizAalVizIntegrationGate.v1"
RECEIPT_ID = "v2_hygiene_phase10_rune_viz_aal_viz_integration_gate_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase10_rune_viz_aal_viz_integration_gate_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
READY_STATUS = "V2_HYGIENE_PHASE10_RUNE_VIZ_AAL_VIZ_INTEGRATION_GATE_READY"
BLOCKED_STATUS = "V2_HYGIENE_PHASE10_RUNE_VIZ_AAL_VIZ_INTEGRATION_GATE_BLOCKED"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
EXPECTED_PHASE16_STATUS = "V2_HYGIENE_PHASE9_CONTROLLED_EXECUTION_PROMOTION_GATE_READY"
EXPECTED_PHASE16_HASH = "2c3f2014f39bae4b506e75bd56b2f0484d6a465b1a2b350a4a1de9e993e07d4f"
EXPECTED_PHASE16_PLANNING_LANE_STATUS = "PLANNING_LANE_ACTIVE_ADVISORY_ONLY"
PHASE16_HANDOFF_TEMPLATE_PATH = Path(
    "operator_input/templates/phase16_controlled_execution_promotion_handoff.md"
)
PHASE14_PLANNING_STUB_PATH = Path("docs/plans/phase14_slang_memetic_rune_activation.md")
OPERATOR_PHASE_NUMBER = 17

RUNE_VIZ_AAL_VIZ_INTEGRATION_MATRIX = (
    {
        "surface_id": "rune_visualization_layer",
        "paths": [
            "docs/atlas/abx-runes.md",
            "docs/media/abx-runes.svg",
            "docs/status/badges/runes.json",
        ],
        "prior_promotion_class": "CONTROLLED_EXECUTION_PLANNING_READ_WRITE",
        "promotion_class": "CONTROLLED_EXECUTION_RUNE_VIZ_READ_WRITE",
        "write_posture": "controlled_rune_viz_read_plus_limited_render_write",
        "limited_write_allowed": True,
        "full_execution_denied": True,
    },
    {
        "surface_id": "incarnation_core_planning_binding",
        "paths": [
            "docs/plans/phase14_slang_memetic_rune_activation.md",
            "core/yggdrasil/rune_route_binding_matrix.py",
            "out/audit/yggdrasil_rune_route_binding_matrix_001.latest.json",
        ],
        "prior_promotion_class": "CONTROLLED_EXECUTION_PLANNING_READ_WRITE",
        "promotion_class": "CONTROLLED_EXECUTION_INCARNATION_CORE_READ_WRITE",
        "write_posture": "controlled_incarnation_core_read_plus_limited_binding_write",
        "limited_write_allowed": True,
        "full_execution_denied": True,
    },
    {
        "surface_id": "aal_viz_projection_bundle_surface",
        "paths": [
            "apps/aal-viz-live-console/public/projection-bundle.json",
            "scripts/build_aal_viz_projection_bundle.py",
        ],
        "prior_promotion_class": "CONTROLLED_EXECUTION_PROJECTION_READ_WRITE",
        "promotion_class": "CONTROLLED_EXECUTION_PROJECTION_BUNDLE_READ_WRITE",
        "write_posture": "controlled_projection_bundle_read_plus_limited_write",
        "limited_write_allowed": True,
        "full_execution_denied": True,
    },
    {
        "surface_id": "aal_viz_operator_packets_surface",
        "paths": [
            "apps/aal-viz-live-console/public/operator-action-packets.json",
            "scripts/build_aal_viz_operator_action_packets.py",
        ],
        "prior_promotion_class": "CONTROLLED_EXECUTION_PROJECTION_READ_WRITE",
        "promotion_class": "CONTROLLED_EXECUTION_OPERATOR_PACKETS_READ_WRITE",
        "write_posture": "controlled_operator_packets_read_plus_limited_write",
        "limited_write_allowed": True,
        "full_execution_denied": True,
    },
    {
        "surface_id": "aal_viz_rune_rendering_hooks",
        "paths": [
            "core/aal_viz_runtime_projection.py",
            "core/aal_viz_graph_render_packet.py",
        ],
        "prior_promotion_class": "CONTROLLED_EXECUTION_PROJECTION_READ_WRITE",
        "promotion_class": "CONTROLLED_EXECUTION_RUNE_RENDERING_READ_WRITE",
        "write_posture": "controlled_rune_rendering_read_plus_limited_hook_write",
        "limited_write_allowed": True,
        "full_execution_denied": True,
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
    "controlled_execution_promotion_authorized",
    "rune_viz_integration_authorized",
    "aal_viz_integration_authorized",
    "phase18_activation_authorized",
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
        "forecast_routing",
        "github_writeback",
        "notion_writeback",
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
        "packet_hash": str(packet.get("controlled_execution_promotion_gate_hash", NOT_COMPUTABLE)),
        "expected_packet_hash": EXPECTED_PHASE16_HASH,
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_PHASE16_STATUS,
        "authority_locks_all_false": (
            True
            if packet.get("authority_locks") is None
            else _locks_all_false(packet.get("authority_locks"))
        ),
        "planning_lane_activated": packet.get("planning_lane_activated", NOT_COMPUTABLE),
        "planning_lane_status": packet.get("planning_lane_status", NOT_COMPUTABLE),
        "valid_for_controlled_execution": packet.get("valid_for_controlled_execution", NOT_COMPUTABLE),
        "operator_review_posture": packet.get("operator_review_posture", NOT_COMPUTABLE),
        "recommended_next_lane": packet.get("recommended_next_lane", NOT_COMPUTABLE),
        "downstream": packet.get("downstream", NOT_COMPUTABLE),
    }


def _phase16_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if packet.get("status") != EXPECTED_PHASE16_STATUS:
        blockers.append("phase16_controlled_execution_promotion_gate_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("phase16_source_not_ready")
    if packet.get("source_blockers") != []:
        blockers.append("phase16_source_blockers_not_empty")
    if packet.get("controlled_execution_promotion_gate_ready") is not True:
        blockers.append("phase16_controlled_execution_promotion_gate_ready_not_true")
    if packet.get("controlled_execution_promotion_gate_hash") != EXPECTED_PHASE16_HASH:
        blockers.append("phase16_controlled_execution_promotion_gate_hash_mismatch")
    without_hash = dict(packet)
    observed_hash = without_hash.pop("controlled_execution_promotion_gate_hash", NOT_COMPUTABLE)
    if canonical_hash(without_hash) != observed_hash:
        blockers.append("phase16_controlled_execution_promotion_gate_self_hash_mismatch")
    if packet.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append("phase16_recommended_lane_mismatch")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("phase16_downstream_not_closed")
    if packet.get("planning_lane_activated") is not True:
        blockers.append("phase16_planning_lane_not_activated")
    if packet.get("operator_review_posture") != "ACTIVE":
        blockers.append("phase16_operator_review_posture_not_active")
    if packet.get("valid_for_execution") is True:
        blockers.append("phase16_execution_authority_not_denied")
    if packet.get("valid_for_controlled_execution") is not True:
        blockers.append("phase16_controlled_execution_not_eligible")
    locks = packet.get("authority_locks")
    if locks is not None and not _locks_all_false(locks):
        blockers.append("phase16_authority_locks_not_false")
    blockers.extend(_authority_expansion_blockers("phase16_controlled_execution_promotion_gate", packet))
    return blockers


def _rune_viz_aal_viz_integration_contract(repo_root: Path) -> dict[str, Any]:
    surfaces = []
    for entry in RUNE_VIZ_AAL_VIZ_INTEGRATION_MATRIX:
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
                "prior_promotion_class": entry["prior_promotion_class"],
                "promotion_class": entry["promotion_class"],
                "write_posture": entry["write_posture"],
                "path_observations": path_observations,
                "all_paths_observed": all(item["observed"] for item in path_observations),
                "limited_write_allowed": entry["limited_write_allowed"],
                "full_execution_denied": entry["full_execution_denied"],
                "authority_granted": False,
                "rune_viz_integration_promoted": True,
                "operator_review_required": True,
                "operator_signoff_required": True,
            }
        )
    return {
        "contract_id": "v2_hygiene_phase10_rune_viz_aal_viz_integration_contract_001",
        "rune_viz_aal_viz_integration_matrix": surfaces,
        "surface_count": len(surfaces),
        "rune_viz_integration_authorized": False,
        "aal_viz_integration_authorized": False,
        "full_execution_authority_granted": False,
    }


def _controlled_execution_inheritance_contract(phase16: Mapping[str, Any]) -> dict[str, Any]:
    promotion = phase16.get("controlled_execution_promotion_contract", {})
    matrix = promotion.get("controlled_execution_promotion_matrix", [])
    return {
        "contract_id": "v2_hygiene_phase10_controlled_execution_inheritance_contract_001",
        "inherited_from": "v2_hygiene_phase9_controlled_execution_promotion_gate_001",
        "inherited_controlled_execution_surfaces": matrix if isinstance(matrix, list) else [],
        "surface_count": len(matrix) if isinstance(matrix, list) else 0,
        "controlled_execution_promotion_authorized": False,
    }


def _incarnation_core_integration_contract(repo_root: Path, phase16: Mapping[str, Any]) -> dict[str, Any]:
    planning_stub_observed = (repo_root / PHASE14_PLANNING_STUB_PATH).exists()
    rune_matrix = _read_json(
        repo_root / "out/audit/yggdrasil_rune_route_binding_matrix_001.latest.json"
    ) or {}
    return {
        "contract_id": "v2_hygiene_phase10_incarnation_core_integration_contract_001",
        "incarnation_core_planning_stub_path": PHASE14_PLANNING_STUB_PATH.as_posix(),
        "incarnation_core_planning_stub_observed": planning_stub_observed,
        "rune_route_binding_matrix_observed": bool(rune_matrix),
        "rune_route_binding_matrix_status": str(rune_matrix.get("status", NOT_COMPUTABLE)),
        "planning_lane_status": phase16.get("planning_lane_status", NOT_COMPUTABLE),
        "planning_lane_activated": phase16.get("planning_lane_activated", False),
        "incarnation_core_binding_authority_granted": False,
        "rune_registration_authorized": False,
    }


def _operator_signoff_workflow_contract(*, ready: bool) -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase10_rune_viz_aal_viz_operator_signoff_workflow_contract_001",
        "manual_operator_signoff_required": True,
        "operator_signoff_auto_approved": False,
        "phase16_handoff_template_path": PHASE16_HANDOFF_TEMPLATE_PATH.as_posix(),
        "notion_writeback_allowed": False,
        "hash_chain_review_required": True,
        "hash_chain": {
            "phase16_gate_hash": EXPECTED_PHASE16_HASH if ready else NOT_COMPUTABLE,
            "phase17_gate_hash": NOT_COMPUTABLE,
        },
        "claims": [
            {
                "field": "phase16_hash_chain_reviewed",
                "classification": "OBSERVED" if ready else "INFERRED",
                "provenance": SOURCE_PHASE16_GATE_JSON_PATH.as_posix(),
                "value": ready,
            },
            {
                "field": "rune_viz_limited_write_acknowledged",
                "classification": "SPECULATIVE",
                "provenance": "operator_input/templates/phase17_rune_viz_aal_viz_integration_handoff.md",
                "value": True,
            },
            {
                "field": "external_operator_attestation_pending",
                "classification": "SPECULATIVE",
                "provenance": "operator_input/templates/phase17_rune_viz_aal_viz_integration_handoff.md",
                "value": True,
            },
        ],
    }


def _dependency_denial_contract() -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase10_dependency_denial_contract_001",
        "package_lock_mutation_authorized": False,
        "package_lock_tracking_authorized": False,
        "toolchain_provisioning_authorized": False,
        "dependency_mutation_authorized": False,
        "npmrc_stabilization_observed": (Path(".") / "apps/aal-viz-live-console/.npmrc").exists(),
        "package_lock_resolution_held": True,
        "high_authority_mutations_denied": True,
    }


def _brier_scoring_contract() -> dict[str, Any]:
    hooks = [
        {
            "claim_id": entry["surface_id"],
            "forecast_probability": 0.84,
            "binary_outcome": NOT_COMPUTABLE,
            "brier_score": NOT_COMPUTABLE,
            "resolution_source": NOT_COMPUTABLE,
            "resolution_allowed": False,
        }
        for entry in RUNE_VIZ_AAL_VIZ_INTEGRATION_MATRIX
    ]
    hooks.append(
        {
            "claim_id": "rune_viz_aal_viz_integration_without_full_execution_authority",
            "forecast_probability": compute_brier_score(0.8, 0.0),
            "binary_outcome": NOT_COMPUTABLE,
            "brier_score": NOT_COMPUTABLE,
            "resolution_source": "core/governance/brier_provenance.py",
            "resolution_allowed": False,
        }
    )
    return {
        "contract_id": "v2_hygiene_phase10_rune_viz_aal_viz_integration_brier_telemetry_contract_001",
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
            "governance_mapping": "Phase 16 controlled execution gate and rune viz surface observation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": "Incarnation core planning stub and rune route binding matrix linkage",
            "authority_granted": False,
            "risk_level": "MEDIUM",
        },
        {
            "rune": "Hold",
            "governance_mapping": "package-lock, toolchain, dependency mutations, and full execution authority held",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Weigh",
            "governance_mapping": "telemetry-only Brier posture for rune viz + AAL-Viz integration risk",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Seal",
            "governance_mapping": "Phase 17 rune viz + AAL-Viz integration gate only; operator review remains active",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate(
    repo_root: str | Path = ".",
    *,
    source_phase16_gate_path: str | Path = SOURCE_PHASE16_GATE_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_phase16_gate_path)
    phase16 = _read_json(_resolve(root, source_path)) or {}
    blockers: list[str] = []
    if not phase16:
        blockers.append("required_phase16_controlled_execution_promotion_gate_missing")
    else:
        blockers.extend(_phase16_blockers(phase16))
    if not (root / PHASE16_HANDOFF_TEMPLATE_PATH).exists():
        blockers.append("phase16_handoff_template_missing")
    integration_contract = _rune_viz_aal_viz_integration_contract(root)
    for surface in integration_contract["rune_viz_aal_viz_integration_matrix"]:
        if not surface["all_paths_observed"]:
            blockers.append(f"rune_viz_aal_viz_integration_path_missing:{surface['surface_id']}")
    blockers = sorted(set(blockers))
    ready = bool(phase16) and not blockers
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "operator_phase_number": OPERATOR_PHASE_NUMBER,
        "status": READY_STATUS if ready else BLOCKED_STATUS,
        "sources_observed": bool(phase16),
        "source_records": [
            _source_record(
                "phase16_controlled_execution_promotion_gate",
                source_path,
                phase16,
            )
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "rune_viz_aal_viz_integration_gate_ready": ready,
        "phase16_controlled_execution_promotion_gate_hash_verified": ready,
        "planning_lane_status": phase16.get("planning_lane_status", NOT_COMPUTABLE) if phase16 else NOT_COMPUTABLE,
        "planning_lane_activated": phase16.get("planning_lane_activated", False) if phase16 else False,
        "rune_viz_aal_viz_integration_contract": integration_contract,
        "controlled_execution_inheritance_contract": _controlled_execution_inheritance_contract(phase16),
        "incarnation_core_integration_contract": _incarnation_core_integration_contract(root, phase16),
        "operator_signoff_workflow_contract": _operator_signoff_workflow_contract(ready=ready),
        "dependency_denial_contract": _dependency_denial_contract(),
        "brier_scoring_contract": _brier_scoring_contract(),
        "rune_governance_mapping": _rune_governance_mapping(),
        "recommended_next_action": (
            "hold operator review posture; rune visualization and AAL-Viz surfaces allow controlled "
            "read plus limited governed write for projection bundles, operator packets, and rune "
            "rendering; package-lock and full execution authority remain fail-closed"
            if ready
            else "restore the Phase 16 controlled execution promotion gate before integration"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "downstream": NOT_COMPUTABLE,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "promotion_authorized": False,
        "rune_viz_integration_authorized": False,
        "aal_viz_integration_authorized": False,
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
        "valid_for_planning_lane": ready,
        "valid_for_controlled_writeback": ready,
        "valid_for_controlled_execution": ready,
        "valid_for_rune_viz_integration": ready,
        "valid_for_execution": False,
        "valid_for_promotion": False,
        "valid_for_activation": False,
        "operator_signoff_auto_approved": False,
        "operator_review_posture": "ACTIVE",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "authority_locks": _copied_authority_locks(phase16),
        "rune_viz_aal_viz_integration_gate_hash": "",
    }
    packet["rune_viz_aal_viz_integration_gate_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "rune_viz_aal_viz_integration_gate_hash"
        }
    )
    return packet


def render_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    integration = packet["rune_viz_aal_viz_integration_contract"]
    denial = packet["dependency_denial_contract"]
    signoff = packet["operator_signoff_workflow_contract"]
    incarnation = packet["incarnation_core_integration_contract"]
    lines = [
        "# v2.0 Hygiene Phase 10 Rune Viz + AAL-Viz Integration Gate (Operator Phase 17)",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- operator_phase_number: {packet['operator_phase_number']}",
        f"- status: {packet['status']}",
        f"- planning_lane_status: {packet['planning_lane_status']}",
        f"- rune_viz_aal_viz_integration_gate_ready: {packet['rune_viz_aal_viz_integration_gate_ready']}",
        f"- operator_review_posture: {packet['operator_review_posture']}",
        f"- valid_for_rune_viz_integration: {packet['valid_for_rune_viz_integration']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Operator Signoff",
        f"- manual_operator_signoff_required: {signoff['manual_operator_signoff_required']}",
        f"- operator_signoff_auto_approved: {signoff['operator_signoff_auto_approved']}",
        "",
        "## Hash Chain",
        f"- phase16_gate_hash: {signoff['hash_chain']['phase16_gate_hash']}",
        f"- phase17_gate_hash: {signoff['hash_chain']['phase17_gate_hash']}",
        "",
        "## Incarnation Core Integration",
        f"- planning_stub_observed: {incarnation['incarnation_core_planning_stub_observed']}",
        f"- rune_route_binding_matrix_observed: {incarnation['rune_route_binding_matrix_observed']}",
        "",
        "## Rune Viz + AAL-Viz Integration Matrix",
    ]
    for surface in integration["rune_viz_aal_viz_integration_matrix"]:
        lines.append(
            f"- {surface['surface_id']}: {surface['promotion_class']} "
            f"limited_write={surface['limited_write_allowed']} "
            f"paths={surface['paths']} observed={surface['all_paths_observed']}"
        )
    lines.extend(
        [
            "",
            "## Dependency Denial Contract",
            f"- package_lock_mutation_authorized: {denial['package_lock_mutation_authorized']}",
            f"- toolchain_provisioning_authorized: {denial['toolchain_provisioning_authorized']}",
            f"- dependency_mutation_authorized: {denial['dependency_mutation_authorized']}",
            f"- high_authority_mutations_denied: {denial['high_authority_mutations_denied']}",
            "",
            "## Source Blockers",
        ]
    )
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(render_v2_hygiene_phase10_rune_viz_aal_viz_integration_gate_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
    return packet
