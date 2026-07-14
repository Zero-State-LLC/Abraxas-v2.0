from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.scoring.brier import compute_brier_score
from core.sync.v2_hygiene_phase10_rune_viz_aal_viz_integration_gate import (
    RECEIPT_JSON_PATH as SOURCE_PHASE17_GATE_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygienePhase11FullOperatorExecutionAutonomyGate.v1"
RECEIPT_ID = "v2_hygiene_phase11_full_operator_execution_autonomy_gate_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase11_full_operator_execution_autonomy_gate_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
READY_STATUS = "V2_HYGIENE_PHASE11_FULL_OPERATOR_EXECUTION_AUTONOMY_GATE_READY"
BLOCKED_STATUS = "V2_HYGIENE_PHASE11_FULL_OPERATOR_EXECUTION_AUTONOMY_GATE_BLOCKED"
EXPECTED_PHASE17_STATUS = "V2_HYGIENE_PHASE10_RUNE_VIZ_AAL_VIZ_INTEGRATION_GATE_READY"
EXPECTED_PHASE17_HASH = "37f21b4b821085d60256757fcf260893a688a328e686e35769fae6bea3450502"
PHASE17_HANDOFF_TEMPLATE_PATH = Path(
    "operator_input/templates/phase17_rune_viz_aal_viz_integration_handoff.md"
)
OPERATOR_PHASE_NUMBER = 18

FULL_OPERATOR_EXECUTION_AUTONOMY_MATRIX = (
    {
        "surface_id": "rune_visualization_layer",
        "paths": [
            "docs/atlas/abx-runes.md",
            "docs/media/abx-runes.svg",
            "docs/status/badges/runes.json",
        ],
        "prior_promotion_class": "CONTROLLED_EXECUTION_RUNE_VIZ_READ_WRITE",
        "promotion_class": "OPERATOR_EXECUTION_AUTONOMY_RUNE_VIZ_ELIGIBLE",
        "write_posture": "operator_execution_autonomy_eligible_pending_final_attestation",
        "autonomy_eligible": True,
        "autonomy_authorized": False,
    },
    {
        "surface_id": "incarnation_core_planning_binding",
        "paths": [
            "docs/plans/phase14_slang_memetic_rune_activation.md",
            "core/yggdrasil/rune_route_binding_matrix.py",
            "out/audit/yggdrasil_rune_route_binding_matrix_001.latest.json",
        ],
        "prior_promotion_class": "CONTROLLED_EXECUTION_INCARNATION_CORE_READ_WRITE",
        "promotion_class": "OPERATOR_EXECUTION_AUTONOMY_INCARNATION_CORE_ELIGIBLE",
        "write_posture": "operator_execution_autonomy_eligible_pending_final_attestation",
        "autonomy_eligible": True,
        "autonomy_authorized": False,
    },
    {
        "surface_id": "planning_lane_outputs",
        "paths": [
            "out/operator_review/v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate_001.latest.json",
            "docs/plans/phase14_slang_memetic_rune_activation.md",
            "PLANS.md",
        ],
        "prior_promotion_class": "CONTROLLED_EXECUTION_PLANNING_READ_WRITE",
        "promotion_class": "OPERATOR_EXECUTION_AUTONOMY_PLANNING_LANE_ELIGIBLE",
        "write_posture": "operator_execution_autonomy_eligible_pending_final_attestation",
        "autonomy_eligible": True,
        "autonomy_authorized": False,
    },
    {
        "surface_id": "core_oracle_shadow",
        "paths": ["out/oracle/", "core/ingest/"],
        "prior_promotion_class": "CONTROLLED_EXECUTION_SHADOW_READ_WRITE",
        "promotion_class": "OPERATOR_EXECUTION_AUTONOMY_ORACLE_SHADOW_ELIGIBLE",
        "write_posture": "operator_execution_autonomy_eligible_pending_final_attestation",
        "autonomy_eligible": True,
        "autonomy_authorized": False,
    },
    {
        "surface_id": "brier_engine_telemetry",
        "paths": ["core/scoring/brier.py", "core/governance/brier_provenance.py"],
        "prior_promotion_class": "CONTROLLED_EXECUTION_TELEMETRY_READ",
        "promotion_class": "OPERATOR_EXECUTION_AUTONOMY_BRIER_TELEMETRY_ELIGIBLE",
        "write_posture": "operator_execution_autonomy_telemetry_eligible_brier_resolution_denied",
        "autonomy_eligible": True,
        "autonomy_authorized": False,
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
    "full_operator_execution_autonomy_authorized",
    "operator_execution_autonomy_authorized",
    "rune_viz_integration_authorized",
    "aal_viz_integration_authorized",
    "phase19_activation_authorized",
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
        "packet_hash": str(packet.get("rune_viz_aal_viz_integration_gate_hash", NOT_COMPUTABLE)),
        "expected_packet_hash": EXPECTED_PHASE17_HASH,
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_PHASE17_STATUS,
        "authority_locks_all_false": (
            True
            if packet.get("authority_locks") is None
            else _locks_all_false(packet.get("authority_locks"))
        ),
        "valid_for_rune_viz_integration": packet.get("valid_for_rune_viz_integration", NOT_COMPUTABLE),
        "valid_for_controlled_execution": packet.get("valid_for_controlled_execution", NOT_COMPUTABLE),
        "operator_review_posture": packet.get("operator_review_posture", NOT_COMPUTABLE),
        "recommended_next_lane": packet.get("recommended_next_lane", NOT_COMPUTABLE),
        "downstream": packet.get("downstream", NOT_COMPUTABLE),
    }


def _phase17_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if packet.get("status") != EXPECTED_PHASE17_STATUS:
        blockers.append("phase17_rune_viz_aal_viz_integration_gate_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("phase17_source_not_ready")
    if packet.get("source_blockers") != []:
        blockers.append("phase17_source_blockers_not_empty")
    if packet.get("rune_viz_aal_viz_integration_gate_ready") is not True:
        blockers.append("phase17_rune_viz_aal_viz_integration_gate_ready_not_true")
    if packet.get("rune_viz_aal_viz_integration_gate_hash") != EXPECTED_PHASE17_HASH:
        blockers.append("phase17_rune_viz_aal_viz_integration_gate_hash_mismatch")
    without_hash = dict(packet)
    observed_hash = without_hash.pop("rune_viz_aal_viz_integration_gate_hash", NOT_COMPUTABLE)
    if canonical_hash(without_hash) != observed_hash:
        blockers.append("phase17_rune_viz_aal_viz_integration_gate_self_hash_mismatch")
    if packet.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append("phase17_recommended_lane_mismatch")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("phase17_downstream_not_closed")
    if packet.get("planning_lane_activated") is not True:
        blockers.append("phase17_planning_lane_not_activated")
    if packet.get("operator_review_posture") != "ACTIVE":
        blockers.append("phase17_operator_review_posture_not_active")
    if packet.get("valid_for_execution") is True:
        blockers.append("phase17_execution_authority_not_denied")
    if packet.get("valid_for_rune_viz_integration") is not True:
        blockers.append("phase17_rune_viz_integration_not_eligible")
    if packet.get("valid_for_controlled_execution") is not True:
        blockers.append("phase17_controlled_execution_not_eligible")
    locks = packet.get("authority_locks")
    if locks is not None and not _locks_all_false(locks):
        blockers.append("phase17_authority_locks_not_false")
    blockers.extend(_authority_expansion_blockers("phase17_rune_viz_aal_viz_integration_gate", packet))
    return blockers


def _full_operator_execution_autonomy_contract(repo_root: Path) -> dict[str, Any]:
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
        surfaces.append(
            {
                "surface_id": entry["surface_id"],
                "paths": list(entry["paths"]),
                "prior_promotion_class": entry["prior_promotion_class"],
                "promotion_class": entry["promotion_class"],
                "write_posture": entry["write_posture"],
                "path_observations": path_observations,
                "all_paths_observed": all(item["observed"] for item in path_observations),
                "autonomy_eligible": entry["autonomy_eligible"],
                "autonomy_authorized": entry["autonomy_authorized"],
                "authority_granted": False,
                "operator_review_required": True,
                "operator_attestation_required": True,
                "final_signoff_required": True,
            }
        )
    return {
        "contract_id": "v2_hygiene_phase11_full_operator_execution_autonomy_contract_001",
        "full_operator_execution_autonomy_matrix": surfaces,
        "surface_count": len(surfaces),
        "full_operator_execution_autonomy_authorized": False,
        "operator_execution_autonomy_authorized": False,
        "execution_authority_granted": False,
    }


def _rune_viz_integration_inheritance_contract(phase17: Mapping[str, Any]) -> dict[str, Any]:
    integration = phase17.get("rune_viz_aal_viz_integration_contract", {})
    matrix = integration.get("rune_viz_aal_viz_integration_matrix", [])
    return {
        "contract_id": "v2_hygiene_phase11_rune_viz_integration_inheritance_contract_001",
        "inherited_from": "v2_hygiene_phase10_rune_viz_aal_viz_integration_gate_001",
        "inherited_rune_viz_surfaces": matrix if isinstance(matrix, list) else [],
        "surface_count": len(matrix) if isinstance(matrix, list) else 0,
        "rune_viz_integration_authorized": False,
        "aal_viz_integration_authorized": False,
    }


def _operator_attestation_workflow_contract(*, ready: bool) -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase11_operator_attestation_workflow_contract_001",
        "manual_operator_signoff_required": True,
        "operator_signoff_auto_approved": False,
        "external_operator_attestation_required": True,
        "phase17_handoff_template_path": PHASE17_HANDOFF_TEMPLATE_PATH.as_posix(),
        "notion_writeback_allowed": False,
        "hash_chain_review_required": True,
        "hash_chain": {
            "phase17_gate_hash": EXPECTED_PHASE17_HASH if ready else NOT_COMPUTABLE,
            "phase18_gate_hash": NOT_COMPUTABLE,
        },
        "claims": [
            {
                "field": "phase17_hash_chain_reviewed",
                "classification": "OBSERVED" if ready else "INFERRED",
                "provenance": SOURCE_PHASE17_GATE_JSON_PATH.as_posix(),
                "value": ready,
            },
            {
                "field": "full_operator_execution_autonomy_attestation_pending",
                "classification": "SPECULATIVE",
                "provenance": "operator_input/templates/phase18_full_operator_execution_autonomy_handoff.md",
                "value": True,
            },
            {
                "field": "execution_authority_remains_external",
                "classification": "OBSERVED",
                "provenance": "v2_hygiene_phase11_full_operator_execution_autonomy_gate_001",
                "value": True,
            },
        ],
    }


def _dependency_denial_contract() -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase11_dependency_denial_contract_001",
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
            "claim_id": entry["surface_id"],
            "forecast_probability": 0.86,
            "binary_outcome": NOT_COMPUTABLE,
            "brier_score": NOT_COMPUTABLE,
            "resolution_source": NOT_COMPUTABLE,
            "resolution_allowed": False,
        }
        for entry in FULL_OPERATOR_EXECUTION_AUTONOMY_MATRIX
    ]
    hooks.append(
        {
            "claim_id": "operator_execution_autonomy_without_gate_granted_execution",
            "forecast_probability": compute_brier_score(0.82, 0.0),
            "binary_outcome": NOT_COMPUTABLE,
            "brier_score": NOT_COMPUTABLE,
            "resolution_source": "core/governance/brier_provenance.py",
            "resolution_allowed": False,
        }
    )
    return {
        "contract_id": "v2_hygiene_phase11_full_operator_execution_autonomy_brier_telemetry_contract_001",
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
            "governance_mapping": "Phase 17 rune viz integration gate and autonomy surface observation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": "Incarnation core, planning lane, and oracle shadow autonomy eligibility binding",
            "authority_granted": False,
            "risk_level": "MEDIUM",
        },
        {
            "rune": "Hold",
            "governance_mapping": "package-lock, toolchain, dependency mutations, and gate-granted execution authority held",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Weigh",
            "governance_mapping": "telemetry-only Brier posture for operator execution autonomy eligibility",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Seal",
            "governance_mapping": "Phase 18 autonomy eligibility gate only; external operator attestation required",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase11_full_operator_execution_autonomy_gate(
    repo_root: str | Path = ".",
    *,
    source_phase17_gate_path: str | Path = SOURCE_PHASE17_GATE_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_phase17_gate_path)
    phase17 = _read_json(_resolve(root, source_path)) or {}
    blockers: list[str] = []
    if not phase17:
        blockers.append("required_phase17_rune_viz_aal_viz_integration_gate_missing")
    else:
        blockers.extend(_phase17_blockers(phase17))
    if not (root / PHASE17_HANDOFF_TEMPLATE_PATH).exists():
        blockers.append("phase17_handoff_template_missing")
    autonomy_contract = _full_operator_execution_autonomy_contract(root)
    for surface in autonomy_contract["full_operator_execution_autonomy_matrix"]:
        if not surface["all_paths_observed"]:
            blockers.append(f"full_operator_execution_autonomy_path_missing:{surface['surface_id']}")
    blockers = sorted(set(blockers))
    ready = bool(phase17) and not blockers
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "operator_phase_number": OPERATOR_PHASE_NUMBER,
        "status": READY_STATUS if ready else BLOCKED_STATUS,
        "sources_observed": bool(phase17),
        "source_records": [
            _source_record(
                "phase17_rune_viz_aal_viz_integration_gate",
                source_path,
                phase17,
            )
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "full_operator_execution_autonomy_gate_ready": ready,
        "phase17_rune_viz_aal_viz_integration_gate_hash_verified": ready,
        "planning_lane_status": phase17.get("planning_lane_status", NOT_COMPUTABLE) if phase17 else NOT_COMPUTABLE,
        "planning_lane_activated": phase17.get("planning_lane_activated", False) if phase17 else False,
        "full_operator_execution_autonomy_contract": autonomy_contract,
        "rune_viz_integration_inheritance_contract": _rune_viz_integration_inheritance_contract(phase17),
        "operator_attestation_workflow_contract": _operator_attestation_workflow_contract(ready=ready),
        "dependency_denial_contract": _dependency_denial_contract(),
        "brier_scoring_contract": _brier_scoring_contract(),
        "rune_governance_mapping": _rune_governance_mapping(),
        "recommended_next_action": (
            "hold operator review posture; surfaces are eligible for full operator execution autonomy "
            "pending external attestation; package-lock and gate-granted execution authority remain fail-closed"
            if ready
            else "restore the Phase 17 rune viz + AAL-Viz integration gate before autonomy promotion"
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
        "valid_for_planning_lane": ready,
        "valid_for_controlled_writeback": ready,
        "valid_for_controlled_execution": ready,
        "valid_for_rune_viz_integration": ready,
        "valid_for_operator_execution_autonomy_eligibility": ready,
        "valid_for_execution": False,
        "valid_for_promotion": False,
        "valid_for_activation": False,
        "operator_signoff_auto_approved": False,
        "external_operator_attestation_required": True,
        "operator_review_posture": "ACTIVE",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "authority_locks": _copied_authority_locks(phase17),
        "full_operator_execution_autonomy_gate_hash": "",
    }
    packet["full_operator_execution_autonomy_gate_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "full_operator_execution_autonomy_gate_hash"
        }
    )
    return packet


def render_v2_hygiene_phase11_full_operator_execution_autonomy_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    autonomy = packet["full_operator_execution_autonomy_contract"]
    denial = packet["dependency_denial_contract"]
    attestation = packet["operator_attestation_workflow_contract"]
    lines = [
        "# v2.0 Hygiene Phase 11 Full Operator Execution Autonomy Gate (Operator Phase 18)",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- operator_phase_number: {packet['operator_phase_number']}",
        f"- status: {packet['status']}",
        f"- planning_lane_status: {packet['planning_lane_status']}",
        f"- full_operator_execution_autonomy_gate_ready: {packet['full_operator_execution_autonomy_gate_ready']}",
        f"- operator_review_posture: {packet['operator_review_posture']}",
        f"- valid_for_operator_execution_autonomy_eligibility: {packet['valid_for_operator_execution_autonomy_eligibility']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- external_operator_attestation_required: {packet['external_operator_attestation_required']}",
        "",
        "## Operator Attestation",
        f"- manual_operator_signoff_required: {attestation['manual_operator_signoff_required']}",
        f"- external_operator_attestation_required: {attestation['external_operator_attestation_required']}",
        "",
        "## Hash Chain",
        f"- phase17_gate_hash: {attestation['hash_chain']['phase17_gate_hash']}",
        f"- phase18_gate_hash: {attestation['hash_chain']['phase18_gate_hash']}",
        "",
        "## Full Operator Execution Autonomy Matrix",
    ]
    for surface in autonomy["full_operator_execution_autonomy_matrix"]:
        lines.append(
            f"- {surface['surface_id']}: {surface['promotion_class']} "
            f"autonomy_eligible={surface['autonomy_eligible']} "
            f"autonomy_authorized={surface['autonomy_authorized']} "
            f"observed={surface['all_paths_observed']}"
        )
    lines.extend(
        [
            "",
            "## Dependency Denial Contract",
            f"- package_lock_mutation_authorized: {denial['package_lock_mutation_authorized']}",
            f"- toolchain_provisioning_authorized: {denial['toolchain_provisioning_authorized']}",
            f"- dependency_mutation_authorized: {denial['dependency_mutation_authorized']}",
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


def write_v2_hygiene_phase11_full_operator_execution_autonomy_gate(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase11_full_operator_execution_autonomy_gate(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(render_v2_hygiene_phase11_full_operator_execution_autonomy_gate_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
    return packet
