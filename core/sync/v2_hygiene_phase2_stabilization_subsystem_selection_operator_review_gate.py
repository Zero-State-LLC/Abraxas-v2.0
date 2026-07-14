from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt import (
    RECEIPT_JSON_PATH as SOURCE_PHASE7_SELECTION_RECEIPT_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygienePhase2StabilizationSubsystemSelectionOperatorReviewGate.v1"
RECEIPT_ID = "v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
READY_STATUS = "V2_HYGIENE_PHASE2_STABILIZATION_SUBSYSTEM_SELECTION_OPERATOR_REVIEW_GATE_READY"
BLOCKED_STATUS = "V2_HYGIENE_PHASE2_STABILIZATION_SUBSYSTEM_SELECTION_OPERATOR_REVIEW_GATE_BLOCKED"
EXPECTED_PHASE7_STATUS = "V2_HYGIENE_PHASE2_NEXT_STABILIZATION_SUBSYSTEM_SELECTION_RECEIPT_READY"
EXPECTED_PHASE7_HASH = "4e929b0ceca2c834095fa6fab3c63a9ad9a5ca5fd16fbccb9193523208f09818"
EXPECTED_PHASE7_RECOMMENDED_LANE = (
    "V2_HYGIENE_PHASE2_STABILIZATION_SUBSYSTEM_SELECTION_OPERATOR_REVIEW_GATE_001"
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
    "v2_module_registration_authorized",
    "rune_registration_authorized",
    "implementation_authorized",
    "valid_for_writeback",
    "valid_for_promotion",
    "valid_for_activation",
    "valid_for_execution",
    "valid_for_implementation",
    "safe_to_auto_continue",
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
        "execution_authority",
        "forecast_routing",
        "github_writeback",
        "notion_writeback",
        "package_lock_mutation",
        "promotion",
        "queue_mutation",
        "rune_registration",
        "runtime_mutation",
        "scheduler_mutation",
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
    contract = packet.get("next_stabilization_subsystem_selection_contract")
    return {
        "source_id": source_id,
        "path": path.as_posix(),
        "observed": bool(packet),
        "file_hash": _sha256(path),
        "packet_hash": str(packet.get("selection_receipt_hash", NOT_COMPUTABLE)),
        "expected_packet_hash": EXPECTED_PHASE7_HASH,
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_PHASE7_STATUS,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "candidate_next_lane_count": packet.get("candidate_next_lane_count", NOT_COMPUTABLE),
        "recommended_next_lane": packet.get("recommended_next_lane", NOT_COMPUTABLE),
        "operator_review_gate": (
            contract.get("recommended_operator_review_gate", NOT_COMPUTABLE)
            if isinstance(contract, Mapping)
            else NOT_COMPUTABLE
        ),
        "downstream": packet.get("downstream", NOT_COMPUTABLE),
    }


def _phase7_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers = []
    if packet.get("status") != EXPECTED_PHASE7_STATUS:
        blockers.append("phase7_selection_receipt_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("phase7_source_not_ready")
    if packet.get("source_blockers") != []:
        blockers.append("phase7_source_blockers_not_empty")
    if packet.get("selection_receipt_ready") is not True:
        blockers.append("phase7_selection_receipt_ready_not_true")
    if packet.get("selection_receipt_hash") != EXPECTED_PHASE7_HASH:
        blockers.append("phase7_selection_receipt_hash_mismatch")
    without_hash = dict(packet)
    observed_hash = without_hash.pop("selection_receipt_hash", NOT_COMPUTABLE)
    if canonical_hash(without_hash) != observed_hash:
        blockers.append("phase7_selection_receipt_self_hash_mismatch")
    if packet.get("candidate_next_lane_count") != 5:
        blockers.append("phase7_candidate_count_not_five")
    if packet.get("recommended_next_lane") != EXPECTED_PHASE7_RECOMMENDED_LANE:
        blockers.append("phase7_recommended_lane_mismatch")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("phase7_downstream_not_closed")
    if not _locks_all_false(packet.get("authority_locks")):
        blockers.append("phase7_authority_locks_not_false")

    candidates = packet.get("candidate_next_lane_matrix")
    expected_candidates = {
        "writeback_authorization",
        "canon_promotion_authorization",
        "runtime_activation_planning",
        "package_lock_dependency_hygiene",
        "broader_subsystem_readiness_audit",
    }
    if not isinstance(candidates, list):
        blockers.append("phase7_candidate_matrix_missing")
    else:
        observed = {
            str(candidate.get("candidate_id"))
            for candidate in candidates
            if isinstance(candidate, Mapping)
        }
        if observed != expected_candidates:
            blockers.append("phase7_candidate_matrix_unexpected")
        if any(
            not isinstance(candidate, Mapping)
            or candidate.get("authority_granted") is not False
            for candidate in candidates
        ):
            blockers.append("phase7_candidate_authority_not_false")

    brier = packet.get("brier_scoring_contract")
    if not isinstance(brier, Mapping):
        blockers.append("phase7_brier_contract_missing")
    else:
        if brier.get("telemetry_only") is not True:
            blockers.append("phase7_brier_not_telemetry_only")
        for field in (
            "resolution_allowed",
            "adaptive_learning_authorized",
            "forecast_routing_authorized",
            "promotion_authorized",
            "execution_authority",
            "brier_resolution_authorized",
        ):
            if brier.get(field) is not False:
                blockers.append(f"phase7_brier_authority_not_false:{field}")

    runes = packet.get("rune_governance_mapping")
    expected_runes = {"Observe", "Bind", "Hold", "Weigh", "Seal"}
    if not isinstance(runes, list):
        blockers.append("phase7_rune_mapping_missing")
    else:
        observed_runes = {
            str(mapping.get("rune")) for mapping in runes if isinstance(mapping, Mapping)
        }
        if observed_runes != expected_runes:
            blockers.append("phase7_rune_mapping_unexpected")
        if any(
            not isinstance(mapping, Mapping) or mapping.get("authority_granted") is not False
            for mapping in runes
        ):
            blockers.append("phase7_rune_authority_not_false")
    blockers.extend(_authority_expansion_blockers("phase7_selection_receipt", packet))
    return blockers


def _package_lock_resolution_contract(repo_root: Path) -> dict[str, Any]:
    app_root = repo_root / "apps/aal-viz-live-console"
    package_json = app_root / "package.json"
    package_lock = app_root / "package-lock.json"
    package_json_packet = _read_json(package_json) or {}
    package_lock_packet = _read_json(package_lock) or {}
    root_package = package_lock_packet.get("packages", {}).get("", {})
    metadata_consistent = (
        bool(package_json_packet)
        and bool(package_lock_packet)
        and package_json_packet.get("name") == package_lock_packet.get("name")
        and package_json_packet.get("version") == package_lock_packet.get("version")
        and package_json_packet.get("name") == root_package.get("name")
        and package_json_packet.get("version") == root_package.get("version")
    )
    return {
        "contract_id": "v2_hygiene_phase2_package_lock_resolution_contract_001",
        "package_lock_path": "apps/aal-viz-live-console/package-lock.json",
        "package_json_path": "apps/aal-viz-live-console/package.json",
        "package_lock_file_observed": package_lock.exists(),
        "package_json_file_observed": package_json.exists(),
        "package_lock_hash": _sha256(package_lock),
        "package_json_hash": _sha256(package_json),
        "metadata_consistent_with_package_json": metadata_consistent,
        "preferred_disposition": "COMMIT_AND_TRACK_IF_VALIDATED",
        "actual_disposition": "HOLD_VALIDATION_FAILED",
        "package_lock_tracking_authorized": False,
        "package_lock_tracking_performed": False,
        "package_lock_delete_authorized": False,
        "package_lock_ignore_authorized": False,
        "package_lock_mutation_authorized": False,
        "package_lock_resolution_status": "PACKAGE_LOCK_RESOLUTION_HELD_VALIDATION_FAILED",
        "validation_evidence": [
            {
                "command": "npm ci",
                "workdir": "apps/aal-viz-live-console",
                "sandbox": "default",
                "status": "FAILED_NETWORK",
                "observed_error": "ENOTFOUND registry.npmjs.org",
                "risk_level": "MEDIUM",
            },
            {
                "command": "npm ci",
                "workdir": "apps/aal-viz-live-console",
                "sandbox": "network_escalated",
                "status": "FAILED_INVALID_VERSION",
                "observed_error": "Invalid Version",
                "risk_level": "HIGH",
            },
            {
                "command": "npm run typecheck && npm test && npm run build",
                "workdir": "apps/aal-viz-live-console",
                "status": "NOT_RUN_AFTER_NPM_CI_FAILURE",
                "observed_error": NOT_COMPUTABLE,
                "risk_level": "MEDIUM",
            },
        ],
        "fail_closed_blocker": "npm_ci_failed_invalid_version",
    }


def _operator_disposition_contract() -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase2_subsystem_selection_operator_disposition_contract_001",
        "recommended_operator_decision": "HOLD_FOR_PACKAGE_LOCK_RESOLUTION_REPAIR",
        "selected_follow_on_lane": "V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_RECEIPT_001",
        "follow_on_lane_authorization_only": True,
        "writeback_selected": False,
        "promotion_selected": False,
        "activation_selected": False,
        "broader_subsystem_readiness_selected": False,
        "package_lock_resolution_selected": True,
        "authority_denials": {
            "notion_writeback_allowed": False,
            "github_writeback_allowed": False,
            "canon_promotion_authorized": False,
            "runtime_activation_authorized": False,
            "runtime_mutation": False,
            "canon_mutation": False,
            "queue_mutation": False,
            "scheduler_mutation": False,
            "v2_module_registration_authorized": False,
            "rune_registration_authorized": False,
            "brier_resolution_authorized": False,
            "forecast_routing_authorized": False,
            "adaptive_learning_authorized": False,
            "execution_authority": False,
            "auto_continuation_authorized": False,
        },
    }


def _brier_scoring_contract() -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase2_operator_review_gate_brier_telemetry_contract_001",
        "telemetry_only": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "telemetry_hooks": [
            {
                "claim_id": "phase7_selection_receipt_ready",
                "forecast_probability": 0.95,
                "binary_outcome": NOT_COMPUTABLE,
                "brier_score": NOT_COMPUTABLE,
                "resolution_source": NOT_COMPUTABLE,
                "resolution_allowed": False,
            },
            {
                "claim_id": "package_lock_tracking_safe_if_validated",
                "forecast_probability": 0.55,
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
            "governance_mapping": "Phase 7 selection state and package-lock frontier observation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": "Phase 7 hash and package-lock/package.json metadata binding",
            "authority_granted": False,
            "risk_level": "MEDIUM",
        },
        {
            "rune": "Hold",
            "governance_mapping": "package-lock tracking, writeback, promotion, activation, mutation, and execution holds",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Weigh",
            "governance_mapping": "telemetry-only Brier scoring for operator-review and package-lock risk",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Seal",
            "governance_mapping": "operator-review gate only, not selected subsystem activation",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate(
    repo_root: str | Path = ".",
    *,
    source_phase7_selection_receipt_path: str | Path = (
        SOURCE_PHASE7_SELECTION_RECEIPT_JSON_PATH
    ),
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_phase7_selection_receipt_path)
    phase7 = _read_json(_resolve(root, source_path)) or {}
    blockers = []
    if not phase7:
        blockers.append("required_phase7_selection_receipt_missing")
    else:
        blockers.extend(_phase7_blockers(phase7))
    blockers = sorted(set(blockers))
    ready = bool(phase7) and not blockers
    package_lock_contract = _package_lock_resolution_contract(root)
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": READY_STATUS if ready else BLOCKED_STATUS,
        "sources_observed": bool(phase7),
        "source_records": [_source_record("phase7_selection_receipt", source_path, phase7)],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "operator_review_gate_ready": ready,
        "phase7_selection_receipt_hash_verified": ready,
        "operator_disposition_contract": _operator_disposition_contract(),
        "package_lock_resolution_contract": package_lock_contract,
        "package_lock_resolution_ready": False,
        "package_lock_resolution_held": True,
        "package_lock_tracking_authorized": False,
        "package_lock_tracking_performed": False,
        "brier_scoring_contract": _brier_scoring_contract(),
        "rune_governance_mapping": _rune_governance_mapping(),
        "recommended_next_action": (
            "repair or regenerate the package lockfile in a separate dependency-hygiene "
            "receipt before tracking; keep broader subsystem work locked"
            if ready
            else "restore the Phase 7 subsystem selection receipt before operator review"
        ),
        "recommended_next_lane": (
            "V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_RECEIPT_001"
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
        "package_lock_mutation_authorized": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "implementation_authorized": False,
        "valid_for_writeback": False,
        "valid_for_promotion": False,
        "valid_for_activation": False,
        "valid_for_package_lock_tracking": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authority_locks": _copied_authority_locks(phase7),
        "operator_review_gate_hash": "",
    }
    packet["operator_review_gate_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "operator_review_gate_hash"}
    )
    return packet


def render_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    disposition = packet["operator_disposition_contract"]
    package_lock = packet["package_lock_resolution_contract"]
    brier = packet["brier_scoring_contract"]
    lines = [
        "# v2.0 Hygiene Phase 2 Stabilization Subsystem Selection Operator Review Gate",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- operator_review_gate_ready: {packet['operator_review_gate_ready']}",
        f"- phase7_selection_receipt_hash_verified: {packet['phase7_selection_receipt_hash_verified']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- downstream: {packet['downstream']}",
        f"- valid_for_package_lock_tracking: {packet['valid_for_package_lock_tracking']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Operator Disposition Contract",
        f"- recommended_operator_decision: {disposition['recommended_operator_decision']}",
        f"- selected_follow_on_lane: {disposition['selected_follow_on_lane']}",
        f"- package_lock_resolution_selected: {disposition['package_lock_resolution_selected']}",
        "",
        "## Package-Lock Resolution Contract",
        f"- package_lock_path: {package_lock['package_lock_path']}",
        f"- metadata_consistent_with_package_json: {package_lock['metadata_consistent_with_package_json']}",
        f"- preferred_disposition: {package_lock['preferred_disposition']}",
        f"- actual_disposition: {package_lock['actual_disposition']}",
        f"- package_lock_resolution_status: {package_lock['package_lock_resolution_status']}",
        f"- package_lock_tracking_authorized: {package_lock['package_lock_tracking_authorized']}",
        f"- fail_closed_blocker: {package_lock['fail_closed_blocker']}",
        "",
        "## Package-Lock Validation Evidence",
    ]
    lines.extend(
        f"- {item['command']} ({item['sandbox'] if 'sandbox' in item else 'not_run'}): "
        f"{item['status']} risk={item['risk_level']} error={item['observed_error']}"
        for item in package_lock["validation_evidence"]
    )
    lines.extend(
        [
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


def write_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate(
        repo_root
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
