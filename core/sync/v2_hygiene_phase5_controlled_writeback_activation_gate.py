from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_receipt import (
    RECEIPT_JSON_PATH as SOURCE_PHASE10_RECEIPT_JSON_PATH,
)

SCHEMA_VERSION = "V2HygienePhase5ControlledWritebackActivationGate.v1"
RECEIPT_ID = "v2_hygiene_phase5_controlled_writeback_activation_gate_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase5_controlled_writeback_activation_gate_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
READY_STATUS = "V2_HYGIENE_PHASE5_CONTROLLED_WRITEBACK_ACTIVATION_GATE_READY"
BLOCKED_STATUS = "V2_HYGIENE_PHASE5_CONTROLLED_WRITEBACK_ACTIVATION_GATE_BLOCKED"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
EXPECTED_PHASE10_STATUS = (
    "V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_ROOT_CAUSE_RECEIPT_READY"
)
EXPECTED_PHASE10_HASH = "7ddfe8d7da78457b4949c050dffa7565f377cee00cf9ce4ae2f6af6cc891d302"
EXPECTED_PHASE10_RECOMMENDED_LANE = "V2_HYGIENE_PHASE5_CONTROLLED_WRITEBACK_ACTIVATION_GATE_001"
NPMRC_PATH = Path("apps/aal-viz-live-console/.npmrc")

CONTROLLED_WRITEBACK_SURFACES = (
    {"surface_id": "core", "path": "core/", "writeback_class": "CONTROLLED_WRITEBACK_ENABLED"},
    {"surface_id": "docs", "path": "docs/", "writeback_class": "CONTROLLED_WRITEBACK_ENABLED"},
    {"surface_id": "scripts", "path": "scripts/", "writeback_class": "CONTROLLED_WRITEBACK_ENABLED"},
    {"surface_id": "tests", "path": "tests/", "writeback_class": "CONTROLLED_WRITEBACK_ENABLED"},
    {
        "surface_id": "out_audit",
        "path": "out/audit/",
        "writeback_class": "CONTROLLED_WRITEBACK_ENABLED",
    },
)

DENIED_DEPENDENCY_SURFACES = (
    {
        "surface_id": "package_lock",
        "path": "apps/aal-viz-live-console/package-lock.json",
        "denial_class": "FAIL_CLOSED_HELD",
    },
    {
        "surface_id": "package_json",
        "path": "apps/aal-viz-live-console/package.json",
        "denial_class": "FAIL_CLOSED_HELD",
    },
    {
        "surface_id": "npmrc",
        "path": "apps/aal-viz-live-console/.npmrc",
        "denial_class": "STABILIZATION_ONLY_NO_MUTATION_AT_GATE",
    },
    {
        "surface_id": "toolchain_provisioning",
        "path": "NOT_COMPUTABLE",
        "denial_class": "FAIL_CLOSED_HELD",
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
        "packet_hash": str(packet.get("root_cause_receipt_hash", NOT_COMPUTABLE)),
        "expected_packet_hash": EXPECTED_PHASE10_HASH,
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_PHASE10_STATUS,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "recommended_next_lane": packet.get("recommended_next_lane", NOT_COMPUTABLE),
        "downstream": packet.get("downstream", NOT_COMPUTABLE),
    }


def _phase10_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers = []
    if packet.get("status") != EXPECTED_PHASE10_STATUS:
        blockers.append("phase10_root_cause_receipt_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("phase10_source_not_ready")
    if packet.get("source_blockers") != []:
        blockers.append("phase10_source_blockers_not_empty")
    if packet.get("root_cause_receipt_ready") is not True:
        blockers.append("phase10_root_cause_receipt_ready_not_true")
    if packet.get("root_cause_receipt_hash") != EXPECTED_PHASE10_HASH:
        blockers.append("phase10_root_cause_receipt_hash_mismatch")
    without_hash = dict(packet)
    observed_hash = without_hash.pop("root_cause_receipt_hash", NOT_COMPUTABLE)
    if canonical_hash(without_hash) != observed_hash:
        blockers.append("phase10_root_cause_receipt_self_hash_mismatch")
    if packet.get("recommended_next_lane") != EXPECTED_PHASE10_RECOMMENDED_LANE:
        blockers.append("phase10_recommended_lane_mismatch")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("phase10_downstream_not_closed")
    if not _locks_all_false(packet.get("authority_locks")):
        blockers.append("phase10_authority_locks_not_false")
    blockers.extend(_authority_expansion_blockers("phase10_root_cause_receipt", packet))
    return blockers


def _controlled_writeback_contract(repo_root: Path) -> dict[str, Any]:
    surfaces = []
    for entry in CONTROLLED_WRITEBACK_SURFACES:
        path = repo_root / entry["path"]
        surfaces.append(
            {
                **entry,
                "path_observed": path.exists(),
                "writeback_authorized": True,
                "authority_granted": False,
                "operator_review_required": True,
            }
        )
    return {
        "contract_id": "v2_hygiene_phase5_controlled_writeback_surfaces_contract_001",
        "controlled_writeback_enabled": True,
        "controlled_writeback_surfaces": surfaces,
        "surface_count": len(surfaces),
        "uncontrolled_writeback_authorized": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
    }


def _dependency_denial_contract(repo_root: Path) -> dict[str, Any]:
    npmrc_path = repo_root / NPMRC_PATH
    return {
        "contract_id": "v2_hygiene_phase5_dependency_denial_contract_001",
        "denied_surfaces": list(DENIED_DEPENDENCY_SURFACES),
        "package_lock_mutation_authorized": False,
        "package_lock_tracking_authorized": False,
        "package_lock_tracking_performed": False,
        "package_json_mutation_authorized": False,
        "npmrc_mutation_authorized": False,
        "npmrc_stabilization_observed": npmrc_path.exists(),
        "npmrc_path": NPMRC_PATH.as_posix(),
        "npmrc_hash": _sha256(npmrc_path),
        "gitignore_mutation_authorized": False,
        "toolchain_provisioning_authorized": False,
        "dependency_mutation_authorized": False,
        "package_lock_resolution_held": True,
        "package_lock_resolution_ready": False,
    }


def _brier_scoring_contract() -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase5_controlled_writeback_brier_telemetry_contract_001",
        "telemetry_only": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "telemetry_hooks": [
            {
                "claim_id": "controlled_writeback_surfaces_safe",
                "forecast_probability": 0.8,
                "binary_outcome": NOT_COMPUTABLE,
                "brier_score": NOT_COMPUTABLE,
                "resolution_source": NOT_COMPUTABLE,
                "resolution_allowed": False,
            },
            {
                "claim_id": "package_lock_remains_held",
                "forecast_probability": 0.95,
                "binary_outcome": NOT_COMPUTABLE,
                "brier_score": NOT_COMPUTABLE,
                "resolution_source": NOT_COMPUTABLE,
                "resolution_allowed": False,
            },
        ],
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
            "governance_mapping": "Phase 10 root-cause receipt and controlled writeback surface observation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": "Phase 10 hash linkage and controlled writeback surface binding",
            "authority_granted": False,
            "risk_level": "MEDIUM",
        },
        {
            "rune": "Hold",
            "governance_mapping": "package-lock, toolchain, and dependency mutations remain held",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Weigh",
            "governance_mapping": "telemetry-only Brier posture for controlled writeback activation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Seal",
            "governance_mapping": "controlled writeback gate only, not execution surface promotion",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase5_controlled_writeback_activation_gate(
    repo_root: str | Path = ".",
    *,
    source_phase10_receipt_path: str | Path = SOURCE_PHASE10_RECEIPT_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_phase10_receipt_path)
    phase10 = _read_json(_resolve(root, source_path)) or {}
    blockers = []
    if not phase10:
        blockers.append("required_phase10_root_cause_receipt_missing")
    else:
        blockers.extend(_phase10_blockers(phase10))
    for entry in CONTROLLED_WRITEBACK_SURFACES:
        if not (root / entry["path"]).exists():
            blockers.append(f"controlled_writeback_surface_missing:{entry['surface_id']}")
    blockers = sorted(set(blockers))
    ready = bool(phase10) and not blockers
    writeback_contract = _controlled_writeback_contract(root)
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": READY_STATUS if ready else BLOCKED_STATUS,
        "sources_observed": bool(phase10),
        "source_records": [_source_record("phase10_root_cause_receipt", source_path, phase10)],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "controlled_writeback_activation_gate_ready": ready,
        "phase10_root_cause_receipt_hash_verified": ready,
        "controlled_writeback_contract": writeback_contract,
        "dependency_denial_contract": _dependency_denial_contract(root),
        "controlled_writeback_enabled": ready,
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
            "promote safe execution surfaces under operator review; "
            "keep package-lock and dependency mutations fail-closed"
            if ready
            else "restore the Phase 10 root-cause receipt before controlled writeback activation"
        ),
        "recommended_next_lane": (
            "V2_HYGIENE_PHASE6_EXECUTION_SURFACE_PROMOTION_GATE_001"
            if ready
            else NOT_COMPUTABLE
        ),
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
        "authority_locks": _copied_authority_locks(phase10),
        "controlled_writeback_activation_gate_hash": "",
    }
    packet["controlled_writeback_activation_gate_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "controlled_writeback_activation_gate_hash"
        }
    )
    return packet


def render_v2_hygiene_phase5_controlled_writeback_activation_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    writeback = packet["controlled_writeback_contract"]
    denial = packet["dependency_denial_contract"]
    brier = packet["brier_scoring_contract"]
    lines = [
        "# v2.0 Hygiene Phase 5 Controlled Writeback Activation Gate",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- controlled_writeback_activation_gate_ready: {packet['controlled_writeback_activation_gate_ready']}",
        f"- phase10_root_cause_receipt_hash_verified: {packet['phase10_root_cause_receipt_hash_verified']}",
        f"- controlled_writeback_enabled: {packet['controlled_writeback_enabled']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- downstream: {packet['downstream']}",
        f"- operator_review_posture: {packet['operator_review_posture']}",
        f"- valid_for_controlled_writeback: {packet['valid_for_controlled_writeback']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Controlled Writeback Surfaces",
    ]
    for surface in writeback["controlled_writeback_surfaces"]:
        lines.append(
            f"- {surface['surface_id']}: {surface['path']} "
            f"(class={surface['writeback_class']}, observed={surface['path_observed']})"
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


def write_v2_hygiene_phase5_controlled_writeback_activation_gate(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase5_controlled_writeback_activation_gate(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(render_v2_hygiene_phase5_controlled_writeback_activation_gate_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
    return packet
