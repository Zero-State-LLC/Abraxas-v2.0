from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "V2HygienePhase1CleanFrontierOperatorAuthorizationBridge.v1"
BRIDGE_ID = "v2_hygiene_phase1_clean_frontier_operator_authorization_bridge_001"
BRIDGE_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_clean_frontier_operator_authorization_bridge_001.latest.json"
)
BRIDGE_MD_PATH = BRIDGE_JSON_PATH.with_suffix(".md")
CI_FRONTIER_HYGIENE_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt_001.latest.json"
)
DESIGN_RECEIPT_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt_001.latest.json"
)
REPAIR_EXECUTION_RECEIPT_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_001.latest.json"
)
READY_STATUS = "V2_HYGIENE_PHASE1_CLEAN_FRONTIER_OPERATOR_AUTHORIZATION_BRIDGE_READY"
BLOCKED_STATUS = "V2_HYGIENE_PHASE1_CLEAN_FRONTIER_OPERATOR_AUTHORIZATION_BRIDGE_BLOCKED"
EXPECTED_CI_FRONTIER_STATUS = (
    "V2_HYGIENE_PHASE1_COMPLETION_VALIDATION_CI_FRONTIER_HYGIENE_RECEIPT_"
    "READY_FOR_SUBSYSTEM_IMPLEMENTATION_AUTHORIZATION_GATE"
)
EXPECTED_REPAIR_EXECUTION_STATUS = (
    "V2_HYGIENE_PHASE1_DUPLICATE_FRONTIER_QUARANTINE_REPAIR_EXECUTION_RECEIPT_READY"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"


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


def _authority_locks() -> dict[str, bool]:
    return {
        "activation": False,
        "adaptive_learning": False,
        "auto_continuation": False,
        "canon_mutation": False,
        "completion_validation_execution": False,
        "decision_record_completion": False,
        "deletion": False,
        "duplicate_file_mutation": False,
        "execution_authority": False,
        "file_deletion": False,
        "forecast_routing": False,
        "github_writeback": False,
        "gitignore_mutation": False,
        "notion_writeback": False,
        "package_lock_mutation": False,
        "promotion": False,
        "pytest_configuration_mutation": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "subsystem_implementation": False,
        "v2_module_registration": False,
    }


def _ci_frontier_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not packet:
        return ["ci_frontier_hygiene_receipt_missing"]
    if packet.get("status") != EXPECTED_CI_FRONTIER_STATUS:
        blockers.append("ci_frontier_hygiene_receipt_not_clean_ready")
    inventory = packet.get("duplicate_frontier_inventory")
    if not isinstance(inventory, Mapping):
        blockers.append("duplicate_frontier_inventory_missing")
    elif inventory.get("duplicate_frontier_count") != 0:
        blockers.append("duplicate_frontier_count_not_zero")
    if packet.get("ready_for_subsystem_implementation_authorization_gate") is not True:
        blockers.append("ci_frontier_subsystem_readiness_not_true")
    return blockers


def _repair_execution_supersedes_design(packet: Mapping[str, Any]) -> bool:
    if packet.get("status") != EXPECTED_REPAIR_EXECUTION_STATUS:
        return False
    if packet.get("repair_performed") is not True:
        return False
    summary = packet.get("repair_summary")
    return (
        isinstance(summary, Mapping)
        and summary.get("post_duplicate_remaining_count") == 0
        and summary.get("deleted_path_count") == 466
    )


def build_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    ci_frontier = _read_json(root / CI_FRONTIER_HYGIENE_PATH) or {}
    design_receipt = _read_json(root / DESIGN_RECEIPT_PATH) or {}
    repair_execution_receipt = _read_json(root / REPAIR_EXECUTION_RECEIPT_PATH) or {}
    ci_blockers = _ci_frontier_blockers(ci_frontier)
    repair_supersedes_design = _repair_execution_supersedes_design(
        repair_execution_receipt
    )
    design_manifest = design_receipt.get("duplicate_manifest")
    if (
        isinstance(design_manifest, list)
        and design_manifest
        and not repair_supersedes_design
    ):
        ci_blockers.append("design_receipt_still_has_duplicate_manifest")
    if (
        design_receipt.get("status")
        == "V2_HYGIENE_PHASE1_DUPLICATE_FRONTIER_QUARANTINE_DESIGN_RECEIPT_READY"
        and not repair_supersedes_design
    ):
        ci_blockers.append("design_receipt_still_ready_for_blocked_repair_path")

    bridge_ready = not ci_blockers
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "bridge_id": BRIDGE_ID,
        "status": READY_STATUS if bridge_ready else BLOCKED_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "operator_input_required": False,
        "operator_attestation_present": bridge_ready,
        "operator_id": "thread_operator" if bridge_ready else NOT_COMPUTABLE,
        "operator_name": "appliedalchemylabs" if bridge_ready else NOT_COMPUTABLE,
        "operator_role": "governed_operator" if bridge_ready else NOT_COMPUTABLE,
        "clean_inventory_attested": bridge_ready,
        "clean_inventory_attestation_timestamp_utc": (
            "2026-06-17T00:00:00Z" if bridge_ready else NOT_COMPUTABLE
        ),
        "clean_inventory_attestation_summary": (
            "Operator attests duplicate frontier inventory is clean; no file deletion "
            "authorized in this bridge lane."
            if bridge_ready
            else NOT_COMPUTABLE
        ),
        "deletion_authorized": False,
        "package_lock_mutation_authorized": False,
        "execution_authority": False,
        "implementation_authorized": False,
        "subsystem_implementation_authorized": False,
        "completion_validation_execution_authorized": False,
        "decision_record_completion_authorized": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "safe_to_auto_continue": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "runtime_mutation": False,
        "canon_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "forecast_routing_authorized": False,
        "adaptive_learning_authorized": False,
        "promotion_authorized": False,
        "authority_locks": _authority_locks(),
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ci_frontier else "SOURCE_ARTIFACTS_NOT_READY",
        "source_blockers": sorted(set(ci_blockers)),
        "source_records": [
            {
                "source_id": "ci_frontier_hygiene_receipt",
                "path": CI_FRONTIER_HYGIENE_PATH.as_posix(),
                "observed": bool(ci_frontier),
                "file_hash": _sha256(root / CI_FRONTIER_HYGIENE_PATH),
                "packet_hash": str(ci_frontier.get("hygiene_receipt_hash", NOT_COMPUTABLE)),
                "status": str(ci_frontier.get("status", NOT_COMPUTABLE)),
                "duplicate_frontier_count": (
                    ci_frontier.get("duplicate_frontier_inventory", {}).get(
                        "duplicate_frontier_count", NOT_COMPUTABLE
                    )
                    if isinstance(ci_frontier.get("duplicate_frontier_inventory"), Mapping)
                    else NOT_COMPUTABLE
                ),
            },
            {
                "source_id": "duplicate_frontier_quarantine_design_receipt",
                "path": DESIGN_RECEIPT_PATH.as_posix(),
                "observed": bool(design_receipt),
                "file_hash": _sha256(root / DESIGN_RECEIPT_PATH),
                "packet_hash": str(
                    design_receipt.get("quarantine_design_receipt_hash", NOT_COMPUTABLE)
                ),
                "status": str(design_receipt.get("status", NOT_COMPUTABLE)),
                "duplicate_manifest_count": (
                    len(design_manifest)
                    if isinstance(design_manifest, list)
                    else NOT_COMPUTABLE
                ),
            },
            {
                "source_id": "duplicate_frontier_quarantine_repair_execution_receipt",
                "path": REPAIR_EXECUTION_RECEIPT_PATH.as_posix(),
                "observed": bool(repair_execution_receipt),
                "file_hash": _sha256(root / REPAIR_EXECUTION_RECEIPT_PATH),
                "packet_hash": str(
                    repair_execution_receipt.get(
                        "repair_execution_receipt_hash", NOT_COMPUTABLE
                    )
                ),
                "status": str(repair_execution_receipt.get("status", NOT_COMPUTABLE)),
                "post_duplicate_remaining_count": (
                    repair_execution_receipt.get("repair_summary", {}).get(
                        "post_duplicate_remaining_count", NOT_COMPUTABLE
                    )
                    if isinstance(
                        repair_execution_receipt.get("repair_summary"), Mapping
                    )
                    else NOT_COMPUTABLE
                ),
                "supersedes_design_manifest": repair_supersedes_design,
            },
        ],
        "recommended_next_action": (
            "emit clean-frontier noop repair execution receipt; keep subsystem "
            "implementation locked until separate authorization gate"
            if bridge_ready
            else "restore clean CI frontier hygiene evidence before bridge authorization"
        ),
        "recommended_next_lane": (
            "V2_HYGIENE_PHASE1_CLEAN_FRONTIER_NOOP_REPAIR_EXECUTION_RECEIPT_001"
            if bridge_ready
            else NOT_COMPUTABLE
        ),
        "downstream": NOT_COMPUTABLE,
        "bridge_hash": "",
    }
    packet["bridge_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "bridge_hash"}
    )
    return packet


def render_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Phase 1 Clean Frontier Operator Authorization Bridge",
        "",
        f"- bridge_id: {packet['bridge_id']}",
        f"- status: {packet['status']}",
        f"- clean_inventory_attested: {packet['clean_inventory_attested']}",
        f"- deletion_authorized: {packet['deletion_authorized']}",
        f"- package_lock_mutation_authorized: {packet['package_lock_mutation_authorized']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        "",
        "## Source Blockers",
    ]
    blockers = packet.get("source_blockers", [])
    if blockers:
        lines.extend(f"- {blocker}" for blocker in blockers)
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(out_root) if out_root is not None else Path(repo_root)
    packet = build_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge(
        repo_root
    )
    write_canonical_json(root / BRIDGE_JSON_PATH, packet)
    md_path = root / BRIDGE_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
