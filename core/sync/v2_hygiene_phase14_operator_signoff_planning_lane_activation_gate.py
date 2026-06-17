from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.scoring.brier import compute_brier_score
from core.sync.v2_hygiene_phase13_operator_intelligence_closure_receipt import (
    RECEIPT_JSON_PATH as SOURCE_PHASE13_CLOSURE_JSON_PATH,
)
from core.sync.v2_hygiene_phase13_operator_intelligence_entry_receipt import (
    EXPECTED_PHASE12_HASH,
)

EXPECTED_PHASE13_ENTRY_HASH = "99a157deb8be0df1c7281b09488f73b5ce2c02aaaf7662f45314b5d258d0245f"

SCHEMA_VERSION = "V2HygienePhase14OperatorSignoffPlanningLaneActivationGate.v1"
RECEIPT_ID = "v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
READY_STATUS = "V2_HYGIENE_PHASE14_OPERATOR_SIGNOFF_PLANNING_LANE_ACTIVATION_GATE_READY"
BLOCKED_STATUS = "V2_HYGIENE_PHASE14_OPERATOR_SIGNOFF_PLANNING_LANE_ACTIVATION_GATE_BLOCKED"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
EXPECTED_PHASE13_CLOSURE_STATUS = "V2_HYGIENE_PHASE13_OPERATOR_INTELLIGENCE_CLOSURE_RECEIPT_READY"
EXPECTED_PHASE13_CLOSURE_HASH = "aad1d5cca8e1cc6e25d3e9feb0b25b7ead81dbb38b24e257ea95de228f9771a3"
EXPECTED_PHASE13_CLOSURE_RECOMMENDED_LANE = NOT_COMPUTABLE
PHASE14_PLANNING_STUB_PATH = Path("docs/plans/phase14_slang_memetic_rune_activation.md")
NOTION_SYNC_PACKET_PATH = Path("out/sync/phase13_notion_sync_packet_001.latest.json")
PHASE_NUMBER = 14

PLANNING_SURFACE_MATRIX = (
    {
        "surface_id": "phase14_planning_documents",
        "paths": ["docs/plans/phase14_slang_memetic_rune_activation.md"],
        "promotion_class": "PLANNING_LANE_CONTROLLED_WRITE",
        "write_posture": "advisory_planning_only_execution_denied",
    },
    {
        "surface_id": "plans_md_roadmap_surface",
        "paths": ["PLANS.md"],
        "promotion_class": "PLANNING_LANE_CONTROLLED_WRITE",
        "write_posture": "advisory_planning_only_execution_denied",
    },
    {
        "surface_id": "readme_evidence_surface",
        "paths": ["README.md"],
        "promotion_class": "PLANNING_LANE_CONTROLLED_READ_WRITE",
        "write_posture": "evidence_table_planning_updates_only",
    },
    {
        "surface_id": "operator_signoff_templates",
        "paths": ["operator_input/templates/phase14_operator_signoff_handoff.md"],
        "promotion_class": "PLANNING_LANE_CONTROLLED_WRITE",
        "write_posture": "manual_operator_signoff_documentation_only",
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
    "phase15_activation_authorized",
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
        "packet_hash": str(packet.get("operator_intelligence_closure_receipt_hash", NOT_COMPUTABLE)),
        "expected_packet_hash": EXPECTED_PHASE13_CLOSURE_HASH,
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_PHASE13_CLOSURE_STATUS,
        "authority_locks_all_false": (
            True if packet.get("authority_locks") is None else _locks_all_false(packet.get("authority_locks"))
        ),
        "operator_review_posture": packet.get("operator_review_posture", NOT_COMPUTABLE),
        "recommended_next_lane": packet.get("recommended_next_lane", NOT_COMPUTABLE),
        "downstream": packet.get("downstream", NOT_COMPUTABLE),
    }


def _phase13_closure_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if packet.get("status") != EXPECTED_PHASE13_CLOSURE_STATUS:
        blockers.append("phase13_closure_receipt_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("phase13_closure_source_not_ready")
    if packet.get("source_blockers") != []:
        blockers.append("phase13_closure_source_blockers_not_empty")
    if packet.get("operator_intelligence_closure_receipt_ready") is not True:
        blockers.append("phase13_closure_receipt_ready_not_true")
    if packet.get("operator_intelligence_closure_receipt_hash") != EXPECTED_PHASE13_CLOSURE_HASH:
        blockers.append("phase13_closure_receipt_hash_mismatch")
    without_hash = dict(packet)
    observed_hash = without_hash.pop("operator_intelligence_closure_receipt_hash", NOT_COMPUTABLE)
    if canonical_hash(without_hash) != observed_hash:
        blockers.append("phase13_closure_receipt_self_hash_mismatch")
    if packet.get("recommended_next_lane") != EXPECTED_PHASE13_CLOSURE_RECOMMENDED_LANE:
        blockers.append("phase13_closure_recommended_lane_mismatch")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("phase13_closure_downstream_not_closed")
    if packet.get("operator_review_posture") != "ACTIVE":
        blockers.append("phase13_closure_operator_review_posture_not_active")
    if packet.get("phase14_activation_authorized") is True:
        blockers.append("phase13_closure_premature_phase14_activation")
    locks = packet.get("authority_locks")
    if locks is not None and not _locks_all_false(locks):
        blockers.append("phase13_closure_authority_locks_not_false")
    blockers.extend(_authority_expansion_blockers("phase13_closure_receipt", packet))
    return blockers


def _planning_surface_matrix(root: Path) -> list[dict[str, Any]]:
    matrix: list[dict[str, Any]] = []
    for entry in PLANNING_SURFACE_MATRIX:
        paths_observed = []
        for rel_path in entry["paths"]:
            path = root / rel_path
            paths_observed.append(
                {
                    "path": rel_path,
                    "observed": path.exists(),
                    "file_hash": _sha256(path),
                }
            )
        matrix.append(
            {
                "surface_id": entry["surface_id"],
                "promotion_class": entry["promotion_class"],
                "write_posture": entry["write_posture"],
                "paths": paths_observed,
                "all_paths_observed": all(item["observed"] for item in paths_observed),
                "authority_granted": False,
                "planning_lane_only": True,
            }
        )
    return matrix


def _operator_signoff_workflow_contract(
    root: Path,
    *,
    closure_hash: str,
    ready: bool,
) -> dict[str, Any]:
    notion_packet = _read_json(root / NOTION_SYNC_PACKET_PATH) or {}
    return {
        "contract_id": "v2_hygiene_phase14_operator_signoff_workflow_contract_001",
        "manual_operator_signoff_required": True,
        "operator_signoff_auto_approved": False,
        "notion_sync_packet_path": NOTION_SYNC_PACKET_PATH.as_posix(),
        "notion_sync_packet_observed": bool(notion_packet),
        "notion_sync_packet_status": str(notion_packet.get("status", NOT_COMPUTABLE)),
        "notion_writeback_allowed": False,
        "hash_chain_review_required": True,
        "hash_chain": {
            "phase12_gate_hash": EXPECTED_PHASE12_HASH,
            "phase13_entry_receipt_hash": EXPECTED_PHASE13_ENTRY_HASH,
            "phase13_closure_receipt_hash": closure_hash if ready else NOT_COMPUTABLE,
            "phase14_gate_hash": NOT_COMPUTABLE,
        },
        "claims": [
            {
                "field": "closure_hash_chain_reviewed",
                "classification": "OBSERVED" if ready else "INFERRED",
                "provenance": SOURCE_PHASE13_CLOSURE_JSON_PATH.as_posix(),
                "value": ready,
            },
            {
                "field": "notion_sync_packet_manual_approval",
                "classification": "INFERRED",
                "provenance": NOTION_SYNC_PACKET_PATH.as_posix(),
                "value": notion_packet.get("manual_operator_copy_paste_only") is True,
            },
            {
                "field": "external_operator_attestation_pending",
                "classification": "SPECULATIVE",
                "provenance": "operator_input/templates/phase14_operator_signoff_handoff.md",
                "value": True,
            },
        ],
    }


def _planning_lane_activation_contract(matrix: list[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase14_planning_lane_activation_contract_001",
        "planning_lane_status": "PLANNING_LANE_ACTIVE_ADVISORY_ONLY",
        "planning_lane_execution_denied": True,
        "planning_surface_matrix": matrix,
        "phase14_planning_stub_path": PHASE14_PLANNING_STUB_PATH.as_posix(),
        "activation_authority_granted": False,
        "implementation_authority_granted": False,
    }


def _dependency_denial_contract() -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase14_dependency_denial_contract_001",
        "package_lock_mutation_authorized": False,
        "package_lock_tracking_authorized": False,
        "toolchain_provisioning_authorized": False,
        "dependency_mutation_authorized": False,
        "npmrc_stabilization_observed": (Path(".") / "apps/aal-viz-live-console/.npmrc").exists(),
        "package_lock_resolution_held": True,
    }


def _brier_scoring_contract() -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase14_operator_signoff_brier_telemetry_contract_001",
        "telemetry_only": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "telemetry_hooks": [
            {
                "claim_id": "phase14_planning_lane_activation_ready",
                "forecast_probability": 0.85,
                "binary_outcome": NOT_COMPUTABLE,
                "brier_score": NOT_COMPUTABLE,
                "resolution_source": NOT_COMPUTABLE,
                "resolution_allowed": False,
            },
            {
                "claim_id": "operator_signoff_manual_workflow_sufficient",
                "forecast_probability": 0.75,
                "binary_outcome": NOT_COMPUTABLE,
                "brier_score": NOT_COMPUTABLE,
                "resolution_source": "operator_input/templates/phase14_operator_signoff_handoff.md",
                "resolution_allowed": False,
            },
            {
                "claim_id": "planning_surface_promotion_without_execution",
                "forecast_probability": compute_brier_score(0.7, 0.0),
                "binary_outcome": NOT_COMPUTABLE,
                "brier_score": NOT_COMPUTABLE,
                "resolution_source": "core/governance/brier_provenance.py",
                "resolution_allowed": False,
            },
        ],
        "resolution_allowed": False,
        "brier_resolution_authorized": False,
    }


def _rune_governance_mapping() -> list[dict[str, Any]]:
    return [
        {
            "rune": "Observe",
            "governance_mapping": "Phase 13 closure hash chain and planning stub observation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": "Phase 13 closure hash binding and planning surface matrix",
            "authority_granted": False,
            "risk_level": "MEDIUM",
        },
        {
            "rune": "Hold",
            "governance_mapping": "package-lock, toolchain, dependency mutations, and execution held",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Weigh",
            "governance_mapping": "telemetry-only Brier posture for planning lane activation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Seal",
            "governance_mapping": "Phase 14 planning lane gate only; operator review remains active",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate(
    repo_root: str | Path = ".",
    *,
    source_phase13_closure_path: str | Path = SOURCE_PHASE13_CLOSURE_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_phase13_closure_path)
    phase13 = _read_json(_resolve(root, source_path)) or {}
    blockers: list[str] = []
    if not phase13:
        blockers.append("required_phase13_closure_receipt_missing")
    else:
        blockers.extend(_phase13_closure_blockers(phase13))
    notion_packet = _read_json(root / NOTION_SYNC_PACKET_PATH)
    if not notion_packet:
        blockers.append("phase13_notion_sync_packet_missing")
    elif notion_packet.get("status") != "PHASE13_NOTION_SYNC_PACKET_READY":
        blockers.append("phase13_notion_sync_packet_not_ready")
    elif notion_packet.get("notion_writeback_allowed") is True:
        blockers.append("phase13_notion_sync_packet_writeback_not_denied")
    if not (root / PHASE14_PLANNING_STUB_PATH).exists():
        blockers.append("phase14_planning_stub_missing")
    planning_matrix = _planning_surface_matrix(root)
    for surface in planning_matrix:
        if not surface["all_paths_observed"]:
            blockers.append(f"planning_surface_path_missing:{surface['surface_id']}")
    blockers = sorted(set(blockers))
    ready = bool(phase13) and not blockers
    closure_hash = str(phase13.get("operator_intelligence_closure_receipt_hash", NOT_COMPUTABLE))
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": READY_STATUS if ready else BLOCKED_STATUS,
        "sources_observed": bool(phase13),
        "source_records": [_source_record("phase13_operator_intelligence_closure_receipt", source_path, phase13)],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "operator_signoff_planning_lane_activation_gate_ready": ready,
        "phase13_operator_intelligence_closure_receipt_hash_verified": ready,
        "planning_lane_activated": ready,
        "planning_lane_status": "PLANNING_LANE_ACTIVE_ADVISORY_ONLY" if ready else "PLANNING_LANE_HELD",
        "operator_signoff_workflow_contract": _operator_signoff_workflow_contract(
            root,
            closure_hash=closure_hash,
            ready=ready,
        ),
        "planning_lane_activation_contract": _planning_lane_activation_contract(planning_matrix),
        "dependency_denial_contract": _dependency_denial_contract(),
        "brier_scoring_contract": _brier_scoring_contract(),
        "rune_governance_mapping": _rune_governance_mapping(),
        "recommended_next_action": (
            "execute Phase 14 planning work under controlled-write planning surfaces only; "
            "hold dependency mutations and execution authority fail-closed"
            if ready
            else "restore Phase 13 closure receipt and planning prerequisites before activation"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "downstream": NOT_COMPUTABLE,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "promotion_authorized": False,
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
        "valid_for_execution": False,
        "valid_for_promotion": False,
        "valid_for_activation": False,
        "operator_signoff_auto_approved": False,
        "operator_review_posture": "ACTIVE",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "authority_locks": _copied_authority_locks(phase13),
        "operator_signoff_planning_lane_activation_gate_hash": "",
    }
    packet["operator_signoff_planning_lane_activation_gate_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "operator_signoff_planning_lane_activation_gate_hash"
        }
    )
    return packet


def render_v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    signoff = packet["operator_signoff_workflow_contract"]
    planning = packet["planning_lane_activation_contract"]
    lines = [
        "# v2.0 Hygiene Phase 14 Operator Signoff Planning Lane Activation Gate",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- status: {packet['status']}",
        f"- planning_lane_activated: {packet['planning_lane_activated']}",
        f"- planning_lane_status: {packet['planning_lane_status']}",
        f"- operator_review_posture: {packet['operator_review_posture']}",
        "",
        "## Operator Signoff Workflow",
        f"- manual_operator_signoff_required: {signoff['manual_operator_signoff_required']}",
        f"- notion_writeback_allowed: {signoff['notion_writeback_allowed']}",
        "",
        "## Hash Chain",
        f"- phase12_gate_hash: {signoff['hash_chain']['phase12_gate_hash']}",
        f"- phase13_closure_receipt_hash: {signoff['hash_chain']['phase13_closure_receipt_hash']}",
        f"- phase14_gate_hash: {signoff['hash_chain']['phase14_gate_hash']}",
        "",
        "## Planning Lane",
        f"- planning_lane_status: {planning['planning_lane_status']}",
        f"- surfaces: {len(planning['planning_surface_matrix'])}",
        "",
        "## Source Blockers",
    ]
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase14_operator_signoff_planning_lane_activation_gate_markdown(packet)
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
