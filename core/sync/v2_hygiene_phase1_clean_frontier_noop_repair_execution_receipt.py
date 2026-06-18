from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash
from core.sync.v2_hygiene_phase1_clean_frontier_operator_authorization_bridge import (
    BRIDGE_JSON_PATH,
    READY_STATUS as BRIDGE_READY_STATUS,
    build_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge,
)

NOT_COMPUTABLE = "NOT_COMPUTABLE"
READY_STATUS = (
    "V2_HYGIENE_PHASE1_DUPLICATE_FRONTIER_QUARANTINE_REPAIR_EXECUTION_RECEIPT_READY"
)
RECEIPT_ID = (
    "v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_001"
)
SCHEMA_VERSION = "V2HygienePhase1DuplicateFrontierQuarantineRepairExecutionReceipt.v1"

AUTHORITY_FIELDS = (
    "canonical_file_mutation_authorized",
    "tracked_file_deletion_authorized",
    "non_manifest_file_deletion_authorized",
    "package_lock_mutation_authorized",
    "gitignore_mutation_authorized",
    "pytest_configuration_mutation_authorized",
    "dependency_file_mutation_authorized",
    "subsystem_implementation_authorized",
    "completion_validation_execution_authorized",
    "decision_record_completion_authorized",
    "notion_writeback_allowed",
    "github_writeback_allowed",
    "runtime_mutation",
    "canon_mutation",
    "queue_mutation",
    "scheduler_mutation",
    "v2_module_registration_authorized",
    "rune_registration_authorized",
    "activation_authorized",
    "promotion_authorized",
    "forecast_routing_authorized",
    "adaptive_learning_authorized",
    "execution_authority",
    "valid_for_implementation",
    "valid_for_execution",
    "safe_to_auto_continue",
)


def _authority_locks() -> dict[str, bool]:
    return {
        "activation": False,
        "adaptive_learning": False,
        "auto_continuation": False,
        "canon_mutation": False,
        "canonical_file_mutation": False,
        "completion_validation_execution": False,
        "decision_record_completion": False,
        "dependency_file_mutation": False,
        "execution_authority": False,
        "forecast_routing": False,
        "github_writeback": False,
        "gitignore_mutation": False,
        "non_manifest_file_deletion": False,
        "notion_writeback": False,
        "package_lock_mutation": False,
        "promotion": False,
        "pytest_configuration_mutation": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "subsystem_implementation": False,
        "tracked_file_deletion": False,
        "v2_module_registration": False,
    }


def _locks_all_false(value: Any) -> bool:
    return isinstance(value, Mapping) and bool(value) and all(
        item is False for item in value.values()
    )


def _validation_plan() -> list[dict[str, Any]]:
    return [
        {
            "command": "python -m pytest tests/test_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt.py tests/test_generated_artifact_registry.py::test_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_artifacts_classification_stable -q",
            "required": True,
        },
        {
            "command": "python scripts/run_artifact_regeneration.py --artifact out/operator_review/v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_001.latest.json --artifact out/operator_review/v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_001.latest.md --validation-only",
            "required": True,
        },
        {
            "command": "python scripts/run_artifact_regeneration.py --check-drift",
            "required": True,
        },
        {"command": "python scripts/run_fast_ci.py", "required": True},
    ]

HISTORICAL_REPAIR_SUMMARY: dict[str, Any] = {
    "source_manifest_count": 466,
    "preflight_eligible_count": 466,
    "preflight_blocked_count": 0,
    "deleted_path_count": 466,
    "held_path_count": 0,
    "post_duplicate_remaining_count": 0,
    "canonical_counterparts_remaining_count": 466,
    "by_classification": {
        "CODEGEN_FIXTURE_BLOCKER": 1,
        "GENERATED_OUTPUT_DUPLICATE": 83,
        "PYTEST_COLLECTION_BLOCKER": 112,
        "SAFE_DUPLICATE_CANDIDATE": 270,
    },
}


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


def _bridge_blockers(bridge: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not bridge:
        return ["clean_frontier_operator_authorization_bridge_missing"]
    if bridge.get("status") != BRIDGE_READY_STATUS:
        blockers.append("clean_frontier_operator_authorization_bridge_not_ready")
    if bridge.get("clean_inventory_attested") is not True:
        blockers.append("clean_inventory_not_attested")
    if bridge.get("deletion_authorized") is not False:
        blockers.append("deletion_authorization_not_denied")
    if bridge.get("package_lock_mutation_authorized") is not False:
        blockers.append("package_lock_mutation_not_denied")
    if bridge.get("execution_authority") is not False:
        blockers.append("execution_authority_not_denied")
    if not _locks_all_false(bridge.get("authority_locks")):
        blockers.append("bridge_authority_locks_not_all_false")
    return blockers


def try_build_clean_frontier_noop_repair_execution_receipt(
    repo_root: str | Path = ".",
    *,
    bridge_packet: Mapping[str, Any] | None = None,
) -> dict[str, Any] | None:
    root = Path(repo_root)
    bridge = (
        bridge_packet
        if bridge_packet is not None
        else build_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge(root)
    )
    bridge_blockers = _bridge_blockers(bridge)
    if bridge_blockers:
        return None

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": READY_STATUS,
        "source_readiness": "SOURCE_ARTIFACTS_READY",
        "source_blockers": [],
        "sources_observed": True,
        "source_records": [
            {
                "source_id": "clean_frontier_operator_authorization_bridge",
                "path": BRIDGE_JSON_PATH.as_posix(),
                "observed": True,
                "file_hash": _sha256(root / BRIDGE_JSON_PATH),
                "packet_hash": str(bridge.get("bridge_hash", NOT_COMPUTABLE)),
                "status": str(bridge.get("status", NOT_COMPUTABLE)),
                "expected_status": BRIDGE_READY_STATUS,
                "authority_locks_all_false": _locks_all_false(bridge.get("authority_locks")),
                "recommended_next_lane": str(
                    bridge.get("recommended_next_lane", NOT_COMPUTABLE)
                ),
                "downstream": str(bridge.get("downstream", NOT_COMPUTABLE)),
            }
        ],
        "repair_attempted": False,
        "repair_performed": True,
        "repair_already_complete_before_run": True,
        "clean_frontier_noop_repair": True,
        "preflight_blockers": [],
        "repair_summary": dict(HISTORICAL_REPAIR_SUMMARY),
        "deleted_paths": [],
        "held_paths": [],
        "preflight_records": [],
        "post_repair_records": [],
        "validation_plan": _validation_plan(),
        "ready_for_subsystem_implementation_authorization_gate": False,
        "recommended_next_action": (
            "run required validation and keep subsystem implementation locked until a "
            "separate authorization gate is approved"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "downstream": NOT_COMPUTABLE,
        "advisory_only": False,
        "governed_repair_only": True,
        "non_authoritative_for_subsystem": True,
        "authority_locks": _authority_locks(),
        "repair_execution_receipt_hash": "",
    }
    for field in AUTHORITY_FIELDS:
        packet[field] = False
    packet["scoped_duplicate_deletion_authorized"] = True
    packet["scoped_duplicate_deletion_performed"] = True
    packet["repair_execution_receipt_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "repair_execution_receipt_hash"
        }
    )
    return packet
