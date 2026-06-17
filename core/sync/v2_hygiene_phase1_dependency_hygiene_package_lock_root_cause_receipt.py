from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_dependency_hygiene_package_lock_receipt import (
    RECEIPT_JSON_PATH as SOURCE_PHASE9_RECEIPT_JSON_PATH,
)

SCHEMA_VERSION = "V2HygienePhase1DependencyHygienePackageLockRootCauseReceipt.v1"
RECEIPT_ID = "v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_receipt_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_receipt_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
READY_STATUS = "V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_ROOT_CAUSE_RECEIPT_READY"
BLOCKED_STATUS = "V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_ROOT_CAUSE_RECEIPT_BLOCKED"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
EXPECTED_PHASE9_STATUS = (
    "V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_RECEIPT_HELD_VALIDATION_FAILED"
)
EXPECTED_PHASE9_HASH = "728e3aa192cf2ca489d6423f822f3b565548832e78d7ff0d739baee66c01afdd"
EXPECTED_PHASE9_RECOMMENDED_LANE = (
    "V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_ROOT_CAUSE_RECEIPT_001"
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
    "valid_for_controlled_writeback",
    "safe_to_auto_continue",
    "npmrc_mutation_authorized",
    "package_json_mutation_authorized",
    "gitignore_mutation_authorized",
    "toolchain_provisioning_authorized",
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
        "package_lock_tracking",
        "promotion",
        "queue_mutation",
        "rune_registration",
        "runtime_mutation",
        "scheduler_mutation",
        "toolchain_provisioning",
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
        "packet_hash": str(packet.get("dependency_hygiene_receipt_hash", NOT_COMPUTABLE)),
        "expected_packet_hash": EXPECTED_PHASE9_HASH,
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_PHASE9_STATUS,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "package_lock_resolution_held": packet.get(
            "package_lock_resolution_held", NOT_COMPUTABLE
        ),
        "recommended_next_lane": packet.get("recommended_next_lane", NOT_COMPUTABLE),
        "downstream": packet.get("downstream", NOT_COMPUTABLE),
    }


def _phase9_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers = []
    if packet.get("status") != EXPECTED_PHASE9_STATUS:
        blockers.append("phase9_dependency_hygiene_receipt_not_held")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("phase9_source_not_ready")
    if packet.get("source_blockers") != []:
        blockers.append("phase9_source_blockers_not_empty")
    if packet.get("dependency_hygiene_receipt_ready") is not True:
        blockers.append("phase9_dependency_hygiene_receipt_ready_not_true")
    if packet.get("dependency_hygiene_receipt_hash") != EXPECTED_PHASE9_HASH:
        blockers.append("phase9_dependency_hygiene_receipt_hash_mismatch")
    without_hash = dict(packet)
    observed_hash = without_hash.pop("dependency_hygiene_receipt_hash", NOT_COMPUTABLE)
    if canonical_hash(without_hash) != observed_hash:
        blockers.append("phase9_dependency_hygiene_receipt_self_hash_mismatch")
    if packet.get("recommended_next_lane") != EXPECTED_PHASE9_RECOMMENDED_LANE:
        blockers.append("phase9_recommended_lane_mismatch")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("phase9_downstream_not_closed")
    if packet.get("package_lock_resolution_held") is not True:
        blockers.append("phase9_package_lock_resolution_not_held")
    if not _locks_all_false(packet.get("authority_locks")):
        blockers.append("phase9_authority_locks_not_false")
    blockers.extend(_authority_expansion_blockers("phase9_dependency_hygiene_receipt", packet))
    return blockers


def _root_cause_analysis_contract(phase9: Mapping[str, Any]) -> dict[str, Any]:
    classification = phase9.get("root_cause_classification", {})
    return {
        "contract_id": "v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_analysis_contract_001",
        "classification": classification.get("classification", NOT_COMPUTABLE),
        "confidence": classification.get("confidence", NOT_COMPUTABLE),
        "risk_level": classification.get("risk_level", NOT_COMPUTABLE),
        "evidence": list(classification.get("evidence", [])),
        "not_proven": list(classification.get("not_proven", [])),
        "root_cause_sealed": True,
        "dependency_mutation_authorized": False,
        "package_lock_mutation_authorized": False,
        "toolchain_provisioning_authorized": False,
        "recommended_follow_on": (
            "enable controlled writeback for non-dependency surfaces only"
        ),
    }


def _brier_scoring_contract() -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_brier_telemetry_contract_001",
        "telemetry_only": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "telemetry_hooks": [
            {
                "claim_id": "root_cause_classification_sealed",
                "forecast_probability": 0.85,
                "binary_outcome": NOT_COMPUTABLE,
                "brier_score": NOT_COMPUTABLE,
                "resolution_source": NOT_COMPUTABLE,
                "resolution_allowed": False,
            },
            {
                "claim_id": "controlled_writeback_safe_without_dependency_mutation",
                "forecast_probability": 0.7,
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
            "governance_mapping": "Phase 9 package-lock receipt and root-cause classification",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": "Phase 9 hash linkage and sealed root-cause evidence",
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
            "governance_mapping": "telemetry-only Brier posture for root-cause follow-on risk",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Seal",
            "governance_mapping": "sealed root-cause receipt, routes to controlled writeback gate only",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_receipt(
    repo_root: str | Path = ".",
    *,
    source_phase9_receipt_path: str | Path = SOURCE_PHASE9_RECEIPT_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_phase9_receipt_path)
    phase9 = _read_json(_resolve(root, source_path)) or {}
    blockers = []
    if not phase9:
        blockers.append("required_phase9_dependency_hygiene_receipt_missing")
    else:
        blockers.extend(_phase9_blockers(phase9))
    blockers = sorted(set(blockers))
    source_ready = bool(phase9) and not blockers
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": READY_STATUS if source_ready else BLOCKED_STATUS,
        "sources_observed": bool(phase9),
        "source_records": [_source_record("phase9_dependency_hygiene_receipt", source_path, phase9)],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if source_ready else "SOURCE_ARTIFACTS_NOT_READY",
        "root_cause_receipt_ready": source_ready,
        "phase9_dependency_hygiene_receipt_hash_verified": source_ready,
        "root_cause_analysis_contract": _root_cause_analysis_contract(phase9),
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
            "activate controlled writeback gate for non-dependency surfaces only; "
            "keep package-lock and dependency mutations fail-closed"
            if source_ready
            else "restore the Phase 9 dependency hygiene receipt before root-cause sealing"
        ),
        "recommended_next_lane": (
            "V2_HYGIENE_PHASE5_CONTROLLED_WRITEBACK_ACTIVATION_GATE_001"
            if source_ready
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
        "valid_for_promotion": False,
        "valid_for_activation": False,
        "valid_for_package_lock_tracking": False,
        "valid_for_controlled_writeback": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authority_locks": _copied_authority_locks(phase9),
        "root_cause_receipt_hash": "",
    }
    packet["root_cause_receipt_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "root_cause_receipt_hash"}
    )
    return packet


def render_v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    analysis = packet["root_cause_analysis_contract"]
    brier = packet["brier_scoring_contract"]
    lines = [
        "# v2.0 Hygiene Phase 1 Dependency Hygiene Package-Lock Root Cause Receipt",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- root_cause_receipt_ready: {packet['root_cause_receipt_ready']}",
        f"- phase9_dependency_hygiene_receipt_hash_verified: {packet['phase9_dependency_hygiene_receipt_hash_verified']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- downstream: {packet['downstream']}",
        f"- valid_for_controlled_writeback: {packet['valid_for_controlled_writeback']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Root Cause Analysis Contract",
        f"- classification: {analysis['classification']}",
        f"- confidence: {analysis['confidence']}",
        f"- risk_level: {analysis['risk_level']}",
        f"- root_cause_sealed: {analysis['root_cause_sealed']}",
        f"- dependency_mutation_authorized: {analysis['dependency_mutation_authorized']}",
        f"- recommended_follow_on: {analysis['recommended_follow_on']}",
        "",
        "## Brier Scoring Contract",
        f"- telemetry_only: {brier['telemetry_only']}",
        f"- resolution_allowed: {brier['resolution_allowed']}",
        f"- promotion_authorized: {brier['promotion_authorized']}",
        f"- brier_resolution_authorized: {brier['brier_resolution_authorized']}",
        "",
        "## Source Blockers",
    ]
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_receipt(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_receipt(
        repo_root
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_dependency_hygiene_package_lock_root_cause_receipt_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
