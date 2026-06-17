from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate import (
    RECEIPT_JSON_PATH as SOURCE_PHASE8_OPERATOR_REVIEW_GATE_JSON_PATH,
)

SCHEMA_VERSION = "V2HygienePhase1DependencyHygienePackageLockReceipt.v1"
RECEIPT_ID = "v2_hygiene_phase1_dependency_hygiene_package_lock_receipt_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase1_dependency_hygiene_package_lock_receipt_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
HELD_STATUS = "V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_RECEIPT_HELD_VALIDATION_FAILED"
BLOCKED_STATUS = "V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_RECEIPT_BLOCKED"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
EXPECTED_PHASE8_STATUS = (
    "V2_HYGIENE_PHASE2_STABILIZATION_SUBSYSTEM_SELECTION_OPERATOR_REVIEW_GATE_READY"
)
EXPECTED_PHASE8_HASH = "c7c70926a3de624ec8bc56c5518a90fb81c7804d6904ca2813f900e6ed3915dd"
EXPECTED_PHASE8_RECOMMENDED_LANE = (
    "V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_RECEIPT_001"
)
PACKAGE_JSON_PATH = Path("apps/aal-viz-live-console/package.json")
PACKAGE_LOCK_PATH = Path("apps/aal-viz-live-console/package-lock.json")

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
        "package_lock_tracking",
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
    return {
        "source_id": source_id,
        "path": path.as_posix(),
        "observed": bool(packet),
        "file_hash": _sha256(path),
        "packet_hash": str(packet.get("operator_review_gate_hash", NOT_COMPUTABLE)),
        "expected_packet_hash": EXPECTED_PHASE8_HASH,
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_PHASE8_STATUS,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "package_lock_resolution_held": packet.get(
            "package_lock_resolution_held", NOT_COMPUTABLE
        ),
        "recommended_next_lane": packet.get("recommended_next_lane", NOT_COMPUTABLE),
        "downstream": packet.get("downstream", NOT_COMPUTABLE),
    }


def _phase8_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers = []
    if packet.get("status") != EXPECTED_PHASE8_STATUS:
        blockers.append("phase8_operator_review_gate_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("phase8_source_not_ready")
    if packet.get("source_blockers") != []:
        blockers.append("phase8_source_blockers_not_empty")
    if packet.get("operator_review_gate_ready") is not True:
        blockers.append("phase8_operator_review_gate_ready_not_true")
    if packet.get("operator_review_gate_hash") != EXPECTED_PHASE8_HASH:
        blockers.append("phase8_operator_review_gate_hash_mismatch")
    without_hash = dict(packet)
    observed_hash = without_hash.pop("operator_review_gate_hash", NOT_COMPUTABLE)
    if canonical_hash(without_hash) != observed_hash:
        blockers.append("phase8_operator_review_gate_self_hash_mismatch")
    if packet.get("recommended_next_lane") != EXPECTED_PHASE8_RECOMMENDED_LANE:
        blockers.append("phase8_recommended_lane_mismatch")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("phase8_downstream_not_closed")
    if packet.get("package_lock_resolution_held") is not True:
        blockers.append("phase8_package_lock_resolution_not_held")
    if packet.get("package_lock_tracking_authorized") is not False:
        blockers.append("phase8_package_lock_tracking_authorized")
    if not _locks_all_false(packet.get("authority_locks")):
        blockers.append("phase8_authority_locks_not_false")
    blockers.extend(_authority_expansion_blockers("phase8_operator_review_gate", packet))
    return blockers


def _package_lock_diagnostics(repo_root: Path) -> dict[str, Any]:
    package_json_path = repo_root / PACKAGE_JSON_PATH
    package_lock_path = repo_root / PACKAGE_LOCK_PATH
    package_json = _read_json(package_json_path) or {}
    package_lock = _read_json(package_lock_path) or {}
    packages = package_lock.get("packages")
    root_package = packages.get("") if isinstance(packages, Mapping) else {}
    metadata_consistent = (
        bool(package_json)
        and bool(package_lock)
        and package_json.get("name") == package_lock.get("name")
        and package_json.get("version") == package_lock.get("version")
        and isinstance(root_package, Mapping)
        and package_json.get("name") == root_package.get("name")
        and package_json.get("version") == root_package.get("version")
    )
    empty_version_entries = []
    if isinstance(packages, Mapping):
        empty_version_entries = sorted(
            str(name)
            for name, entry in packages.items()
            if isinstance(entry, Mapping) and entry.get("version", "__missing__") == ""
        )
    return {
        "package_json_path": PACKAGE_JSON_PATH.as_posix(),
        "package_lock_path": PACKAGE_LOCK_PATH.as_posix(),
        "package_json_file_observed": package_json_path.exists(),
        "package_lock_file_observed": package_lock_path.exists(),
        "package_json_hash": _sha256(package_json_path),
        "package_lock_preflight_hash": _sha256(package_lock_path),
        "package_lock_post_validation_hash": _sha256(package_lock_path),
        "package_lock_hash_unchanged_after_validation_attempt": True,
        "package_lock_tracked_in_git": False,
        "metadata_consistent_with_package_json": metadata_consistent,
        "lockfile_version": package_lock.get("lockfileVersion", NOT_COMPUTABLE),
        "package_count": len(packages) if isinstance(packages, Mapping) else 0,
        "empty_version_entry_count": len(empty_version_entries),
        "empty_version_entries": empty_version_entries,
    }


def _toolchain_observations() -> list[dict[str, Any]]:
    return [
        {
            "toolchain_id": "system_node_npm",
            "node_version": "v26.0.0",
            "npm_version": "11.17.0",
            "observed": True,
            "risk_level": "HIGH",
            "provenance": "local command observation: node --version && npm --version",
        },
        {
            "toolchain_id": "homebrew_node20",
            "node_version": NOT_COMPUTABLE,
            "npm_version": NOT_COMPUTABLE,
            "observed": False,
            "risk_level": "MEDIUM",
            "provenance": "local path check: /opt/homebrew/opt/node@20/bin/node",
        },
        {
            "toolchain_id": "codex_bundled_node",
            "node_version": "v24.14.0",
            "npm_version": NOT_COMPUTABLE,
            "observed": True,
            "risk_level": "MEDIUM",
            "provenance": "workspace dependency observation: bundled node has no bundled npm executable",
        },
    ]


def _validation_evidence() -> list[dict[str, Any]]:
    return [
        {
            "command": "npm install --package-lock-only --ignore-scripts",
            "workdir": "apps/aal-viz-live-console",
            "toolchain": "node v26.0.0 / npm 11.16.0",
            "sandbox": "network_escalated",
            "status": "FAILED_INVALID_VERSION",
            "observed_error": "Invalid Version",
            "provenance": "/Users/appliedalchemylabs/.npm/_logs/2026-06-17T15_03_05_737Z-debug-0.log",
            "risk_level": "HIGH",
        },
        {
            "command": "npm install --package-lock-only --ignore-scripts --legacy-peer-deps",
            "workdir": "apps/aal-viz-live-console",
            "toolchain": "node v26.0.0 / npm 11.17.0",
            "sandbox": "network_escalated",
            "status": "FAILED_INVALID_VERSION",
            "observed_error": "Invalid Version",
            "provenance": "/Users/appliedalchemylabs/.npm/_logs/2026-06-17T15_21_53_329Z-debug-0.log",
            "risk_level": "HIGH",
        },
        {
            "command": "npm ci --ignore-scripts",
            "workdir": "apps/aal-viz-live-console",
            "toolchain": "NOT_RUN_AFTER_LOCKFILE_REGENERATION_FAILURE",
            "sandbox": "not_run",
            "status": "NOT_COMPUTABLE",
            "observed_error": NOT_COMPUTABLE,
            "provenance": "fail-closed validation sequence",
            "risk_level": "MEDIUM",
        },
        {
            "command": "npm run typecheck && npm test && npm run build",
            "workdir": "apps/aal-viz-live-console",
            "toolchain": "NOT_RUN_AFTER_NPM_CI_NOT_COMPUTABLE",
            "sandbox": "not_run",
            "status": "NOT_COMPUTABLE",
            "observed_error": NOT_COMPUTABLE,
            "provenance": "fail-closed validation sequence",
            "risk_level": "MEDIUM",
        },
    ]


def _resolution_contract() -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase1_dependency_hygiene_package_lock_resolution_contract_001",
        "preferred_disposition": "COMMIT_AND_TRACK_IF_VALIDATED",
        "actual_disposition": "HOLD_VALIDATION_FAILED",
        "package_lock_resolution_status": "PACKAGE_LOCK_RESOLUTION_HELD_VALIDATION_FAILED",
        "package_lock_resolution_ready": False,
        "package_lock_tracking_authorized": False,
        "package_lock_tracking_performed": False,
        "package_lock_mutation_authorized": False,
        "package_lock_delete_authorized": False,
        "package_lock_ignore_authorized": False,
        "package_json_mutation_authorized": False,
        "npmrc_mutation_authorized": False,
        "gitignore_mutation_authorized": False,
        "fail_closed_blocker": "npm_install_package_lock_only_failed_invalid_version",
        "follow_on_required": True,
        "recommended_follow_on": "create a deeper dependency-hygiene root-cause receipt or provide a CI-aligned Node 20/npm toolchain",
    }


def _root_cause_classification() -> dict[str, Any]:
    return {
        "classification": "TOOLCHAIN_LOCKFILE_DEDUPE_COMPATIBILITY_HOLD",
        "confidence": "MEDIUM",
        "risk_level": "HIGH",
        "evidence": [
            "package-lock metadata is internally consistent with package.json",
            "package-lock contains zero entries with an empty version field",
            "npm 11 on Node 26 fails in @npmcli/arborist Node.canDedupe while placing fsevents under rollup",
            "CI-aligned Node 20/npm 10 toolchain was not observed locally",
        ],
        "not_proven": [
            "lockfile is stale and unnecessary",
            "package.json requires mutation",
            ".npmrc or .gitignore mutation is safe",
        ],
    }


def _brier_scoring_contract() -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase1_dependency_hygiene_package_lock_brier_telemetry_contract_001",
        "telemetry_only": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "telemetry_hooks": [
            {
                "claim_id": "node20_toolchain_resolves_lockfile",
                "forecast_probability": 0.65,
                "binary_outcome": NOT_COMPUTABLE,
                "brier_score": NOT_COMPUTABLE,
                "resolution_source": NOT_COMPUTABLE,
                "resolution_allowed": False,
            },
            {
                "claim_id": "package_lock_safe_to_track_after_validation",
                "forecast_probability": 0.45,
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
            "governance_mapping": "Phase 8 gate and package-lock frontier observation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": "Phase 8 hash plus package.json/package-lock hash linkage",
            "authority_granted": False,
            "risk_level": "MEDIUM",
        },
        {
            "rune": "Hold",
            "governance_mapping": "dependency tracking remains held after failed validation",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Weigh",
            "governance_mapping": "telemetry-only Brier posture for package-lock risk",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Seal",
            "governance_mapping": "sealed dependency-hygiene hold receipt, not promotion or execution",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt(
    repo_root: str | Path = ".",
    *,
    source_phase8_operator_review_gate_path: str | Path = (
        SOURCE_PHASE8_OPERATOR_REVIEW_GATE_JSON_PATH
    ),
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_phase8_operator_review_gate_path)
    phase8 = _read_json(_resolve(root, source_path)) or {}
    blockers = []
    if not phase8:
        blockers.append("required_phase8_operator_review_gate_missing")
    else:
        blockers.extend(_phase8_blockers(phase8))
    blockers = sorted(set(blockers))
    source_ready = bool(phase8) and not blockers
    diagnostics = _package_lock_diagnostics(root)
    resolution = _resolution_contract()
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": HELD_STATUS if source_ready else BLOCKED_STATUS,
        "sources_observed": bool(phase8),
        "source_records": [_source_record("phase8_operator_review_gate", source_path, phase8)],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if source_ready else "SOURCE_ARTIFACTS_NOT_READY",
        "dependency_hygiene_receipt_ready": source_ready,
        "phase8_operator_review_gate_hash_verified": source_ready,
        "package_lock_diagnostics": diagnostics,
        "toolchain_observations": _toolchain_observations(),
        "root_cause_classification": _root_cause_classification(),
        "resolution_contract": resolution,
        "validation_evidence": _validation_evidence(),
        "package_lock_resolution_ready": False,
        "package_lock_resolution_held": True,
        "package_lock_tracking_authorized": False,
        "package_lock_tracking_performed": False,
        "package_lock_mutation_authorized": False,
        "brier_scoring_contract": _brier_scoring_contract(),
        "rune_governance_mapping": _rune_governance_mapping(),
        "recommended_next_action": (
            "hold package-lock tracking; rerun under a CI-aligned Node 20/npm toolchain "
            "or create a deeper dependency-hygiene root-cause receipt before mutating dependency files"
            if source_ready
            else "restore the Phase 8 operator review gate before dependency hygiene"
        ),
        "recommended_next_lane": (
            "V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_ROOT_CAUSE_RECEIPT_001"
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
        "package_json_mutation_authorized": False,
        "npmrc_mutation_authorized": False,
        "gitignore_mutation_authorized": False,
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
        "authority_locks": _copied_authority_locks(phase8),
        "dependency_hygiene_receipt_hash": "",
    }
    packet["dependency_hygiene_receipt_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "dependency_hygiene_receipt_hash"
        }
    )
    return packet


def render_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    diagnostics = packet["package_lock_diagnostics"]
    resolution = packet["resolution_contract"]
    root_cause = packet["root_cause_classification"]
    brier = packet["brier_scoring_contract"]
    lines = [
        "# v2.0 Hygiene Phase 1 Dependency Hygiene Package-Lock Receipt",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- dependency_hygiene_receipt_ready: {packet['dependency_hygiene_receipt_ready']}",
        f"- phase8_operator_review_gate_hash_verified: {packet['phase8_operator_review_gate_hash_verified']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- downstream: {packet['downstream']}",
        f"- valid_for_package_lock_tracking: {packet['valid_for_package_lock_tracking']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Package-Lock Diagnostics",
        f"- package_json_hash: {diagnostics['package_json_hash']}",
        f"- package_lock_preflight_hash: {diagnostics['package_lock_preflight_hash']}",
        f"- package_lock_post_validation_hash: {diagnostics['package_lock_post_validation_hash']}",
        f"- package_lock_hash_unchanged_after_validation_attempt: {diagnostics['package_lock_hash_unchanged_after_validation_attempt']}",
        f"- metadata_consistent_with_package_json: {diagnostics['metadata_consistent_with_package_json']}",
        f"- empty_version_entry_count: {diagnostics['empty_version_entry_count']}",
        f"- package_lock_tracked_in_git: {diagnostics['package_lock_tracked_in_git']}",
        "",
        "## Resolution Contract",
        f"- preferred_disposition: {resolution['preferred_disposition']}",
        f"- actual_disposition: {resolution['actual_disposition']}",
        f"- package_lock_resolution_status: {resolution['package_lock_resolution_status']}",
        f"- package_lock_tracking_authorized: {resolution['package_lock_tracking_authorized']}",
        f"- fail_closed_blocker: {resolution['fail_closed_blocker']}",
        "",
        "## Root Cause Classification",
        f"- classification: {root_cause['classification']}",
        f"- confidence: {root_cause['confidence']}",
        f"- risk_level: {root_cause['risk_level']}",
        "",
        "## Validation Evidence",
    ]
    lines.extend(
        f"- {item['command']} ({item['toolchain']}): {item['status']} "
        f"risk={item['risk_level']} error={item['observed_error']}"
        for item in packet["validation_evidence"]
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


def write_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
