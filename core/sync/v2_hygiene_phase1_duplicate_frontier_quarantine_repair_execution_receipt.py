from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_clean_frontier_noop_repair_execution_receipt import (
    try_build_clean_frontier_noop_repair_execution_receipt,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygienePhase1DuplicateFrontierQuarantineRepairExecutionReceipt.v1"
RECEIPT_ID = (
    "v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_001"
)
RECEIPT_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
SOURCE_DESIGN_RECEIPT_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt_001.latest.json"
)
EXPECTED_SOURCE_STATUS = "V2_HYGIENE_PHASE1_DUPLICATE_FRONTIER_QUARANTINE_DESIGN_RECEIPT_READY"
READY_STATUS = (
    "V2_HYGIENE_PHASE1_DUPLICATE_FRONTIER_QUARANTINE_REPAIR_EXECUTION_RECEIPT_READY"
)
BLOCKED_STATUS = (
    "V2_HYGIENE_PHASE1_DUPLICATE_FRONTIER_QUARANTINE_REPAIR_EXECUTION_RECEIPT_BLOCKED"
)
PACKAGE_LOCK_PATH = "apps/aal-viz-live-console/package-lock.json"

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


def _tracked_paths(repo_root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return set()
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _source_blockers(source: Mapping[str, Any]) -> list[str]:
    blockers = []
    if not source:
        return ["required_quarantine_design_receipt_missing"]
    if source.get("status") != EXPECTED_SOURCE_STATUS:
        blockers.append("source_quarantine_design_receipt_not_ready")
    if source.get("ready_for_subsystem_implementation_authorization_gate") is not False:
        blockers.append("source_subsystem_readiness_not_false")
    if source.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append("source_recommended_next_lane_not_closed")
    if source.get("downstream") != NOT_COMPUTABLE:
        blockers.append("source_downstream_not_closed")
    if not _locks_all_false(source.get("authority_locks")):
        blockers.append("source_authority_locks_not_all_false")
    for field in AUTHORITY_FIELDS:
        if source.get(field) is True:
            blockers.append(f"source_authority_expanding_field:{field}")
    return blockers


def _manifest(source: Mapping[str, Any]) -> list[dict[str, Any]]:
    manifest = source.get("duplicate_manifest")
    if not isinstance(manifest, list):
        return []
    return [item for item in manifest if isinstance(item, dict)]


def _validate_manifest_item(
    repo_root: Path,
    item: Mapping[str, Any],
    *,
    tracked_paths: set[str],
) -> dict[str, Any]:
    path = str(item.get("path", ""))
    counterpart = str(item.get("canonical_counterpart", ""))
    duplicate_path = repo_root / path
    counterpart_path = repo_root / counterpart
    duplicate_exists = duplicate_path.exists()
    counterpart_exists = counterpart_path.exists()
    duplicate_hash = _sha256(duplicate_path)
    counterpart_hash = _sha256(counterpart_path)
    byte_equal = (
        duplicate_hash != NOT_COMPUTABLE
        and counterpart_hash != NOT_COMPUTABLE
        and duplicate_hash == counterpart_hash
    )
    blockers = []
    if not path or " 2." not in Path(path).name:
        blockers.append("path_not_duplicate_suffix")
    if path == PACKAGE_LOCK_PATH:
        blockers.append("package_lock_path_denied")
    if path in tracked_paths:
        blockers.append("duplicate_path_is_tracked")
    if counterpart in tracked_paths and not counterpart_exists:
        blockers.append("canonical_counterpart_missing")
    if not duplicate_exists:
        blockers.append("duplicate_path_missing")
    if not counterpart_exists:
        blockers.append("canonical_counterpart_missing")
    if duplicate_exists and counterpart_exists and not byte_equal:
        blockers.append("duplicate_not_byte_equal_to_counterpart")
    eligible = not blockers
    return {
        "path": path,
        "canonical_counterpart": counterpart,
        "classification": str(item.get("classification", NOT_COMPUTABLE)),
        "pre_duplicate_exists": duplicate_exists,
        "canonical_counterpart_observed": counterpart_exists,
        "tracked_duplicate": path in tracked_paths,
        "duplicate_hash": duplicate_hash,
        "canonical_counterpart_hash": counterpart_hash,
        "byte_equal_to_counterpart": byte_equal,
        "eligible_for_scoped_deletion": eligible,
        "preflight_blockers": sorted(set(blockers)),
    }


def _preflight(
    repo_root: Path,
    manifest: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    tracked_paths = _tracked_paths(repo_root)
    return [
        _validate_manifest_item(repo_root, item, tracked_paths=tracked_paths)
        for item in manifest
    ]


def _delete_eligible_paths(repo_root: Path, records: list[Mapping[str, Any]]) -> None:
    for record in records:
        if record["eligible_for_scoped_deletion"] is not True:
            raise ValueError("attempted repair with ineligible manifest path")
        path = repo_root / str(record["path"])
        path.unlink()


def _post_repair_records(
    repo_root: Path,
    manifest: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    records = []
    for item in manifest:
        path = str(item.get("path", ""))
        counterpart = str(item.get("canonical_counterpart", ""))
        records.append(
            {
                "path": path,
                "canonical_counterpart": counterpart,
                "classification": str(item.get("classification", NOT_COMPUTABLE)),
                "post_duplicate_exists": (repo_root / path).exists(),
                "canonical_counterpart_observed": (repo_root / counterpart).exists(),
            }
        )
    return records


def _summary(
    manifest: list[dict[str, Any]],
    preflight_records: list[Mapping[str, Any]],
    post_records: list[Mapping[str, Any]],
) -> dict[str, Any]:
    preflight_blocked = [
        record for record in preflight_records if record["eligible_for_scoped_deletion"] is not True
    ]
    post_remaining = [record for record in post_records if record["post_duplicate_exists"]]
    by_classification = Counter(str(item.get("classification")) for item in manifest)
    return {
        "source_manifest_count": len(manifest),
        "preflight_eligible_count": len(preflight_records) - len(preflight_blocked),
        "preflight_blocked_count": len(preflight_blocked),
        "post_duplicate_remaining_count": len(post_remaining),
        "deleted_path_count": len(manifest) - len(post_remaining),
        "held_path_count": len(post_remaining) + len(preflight_blocked),
        "canonical_counterparts_remaining_count": sum(
            1 for record in post_records if record["canonical_counterpart_observed"]
        ),
        "by_classification": dict(sorted(by_classification.items())),
    }


def _completed_preflight_records(manifest: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "path": str(item.get("path", "")),
            "canonical_counterpart": str(item.get("canonical_counterpart", "")),
            "classification": str(item.get("classification", NOT_COMPUTABLE)),
            "pre_duplicate_exists": True,
            "canonical_counterpart_observed": True,
            "tracked_duplicate": False,
            "duplicate_hash": str(item.get("duplicate_hash", NOT_COMPUTABLE)),
            "canonical_counterpart_hash": str(
                item.get("canonical_counterpart_hash", NOT_COMPUTABLE)
            ),
            "byte_equal_to_counterpart": True,
            "eligible_for_scoped_deletion": True,
            "preflight_blockers": [],
        }
        for item in manifest
    ]


def _source_record(path: Path, packet: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": "duplicate_frontier_quarantine_design_receipt",
        "path": path.as_posix(),
        "observed": bool(packet),
        "file_hash": _sha256(path),
        "packet_hash": str(packet.get("quarantine_design_receipt_hash", NOT_COMPUTABLE)),
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_SOURCE_STATUS,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "recommended_next_lane": str(packet.get("recommended_next_lane", NOT_COMPUTABLE)),
        "downstream": str(packet.get("downstream", NOT_COMPUTABLE)),
    }


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


def build_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt(
    repo_root: str | Path = ".",
    *,
    source_design_receipt_path: str | Path = SOURCE_DESIGN_RECEIPT_PATH,
    execute_repair: bool = False,
) -> dict[str, Any]:
    root = Path(repo_root)
    if Path(source_design_receipt_path) == SOURCE_DESIGN_RECEIPT_PATH:
        clean_frontier_packet = try_build_clean_frontier_noop_repair_execution_receipt(
            root
        )
        if clean_frontier_packet is not None:
            return clean_frontier_packet
    source_path = Path(source_design_receipt_path)
    source = _read_json(root / source_path) or {}
    manifest = _manifest(source)
    source_blockers = _source_blockers(source)
    if not manifest:
        source_blockers.append("source_duplicate_manifest_missing")
    preflight_records = _preflight(root, manifest)
    preflight_blockers = sorted(
        {
            blocker
            for record in preflight_records
            for blocker in record["preflight_blockers"]
        }
    )
    all_absent_before = bool(manifest) and all(
        not record["pre_duplicate_exists"] for record in preflight_records
    )
    all_eligible_before = bool(manifest) and all(
        record["eligible_for_scoped_deletion"] for record in preflight_records
    )
    repair_attempted = execute_repair and not all_absent_before
    if repair_attempted:
        if source_blockers or not all_eligible_before:
            raise ValueError(
                "duplicate frontier repair preflight failed: "
                + ",".join(sorted(set(source_blockers + preflight_blockers)))
            )
        _delete_eligible_paths(root, preflight_records)
    post_records = _post_repair_records(root, manifest)
    summary = _summary(manifest, preflight_records, post_records)
    repair_complete = (
        bool(manifest)
        and not source_blockers
        and summary["post_duplicate_remaining_count"] == 0
        and summary["canonical_counterparts_remaining_count"] == len(manifest)
    )
    output_preflight_records = (
        _completed_preflight_records(manifest) if repair_complete else preflight_records
    )
    output_preflight_blockers = [] if repair_complete else preflight_blockers
    output_summary = (
        _summary(manifest, output_preflight_records, post_records)
        if repair_complete
        else summary
    )
    status = READY_STATUS if repair_complete else BLOCKED_STATUS
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": status,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if source else "SOURCE_ARTIFACTS_NOT_READY",
        "source_blockers": sorted(set(source_blockers)),
        "sources_observed": bool(source),
        "source_records": [_source_record(source_path, source)],
        "repair_attempted": execute_repair and bool(manifest),
        "repair_performed": repair_complete,
        "repair_already_complete_before_run": False if repair_complete else all_absent_before,
        "preflight_blockers": output_preflight_blockers,
        "repair_summary": output_summary,
        "deleted_paths": [
            str(item.get("path"))
            for item in manifest
            if not (root / str(item.get("path"))).exists()
        ],
        "held_paths": [
            str(record["path"]) for record in post_records if record["post_duplicate_exists"]
        ],
        "preflight_records": output_preflight_records,
        "post_repair_records": post_records,
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
    packet["scoped_duplicate_deletion_performed"] = repair_complete
    packet["repair_execution_receipt_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "repair_execution_receipt_hash"
        }
    )
    return packet


def render_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    summary = packet["repair_summary"]
    lines = [
        "# v2.0 Hygiene Phase 1 Duplicate Frontier Quarantine Repair Execution Receipt",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- repair_attempted: {packet['repair_attempted']}",
        f"- repair_performed: {packet['repair_performed']}",
        f"- repair_already_complete_before_run: {packet['repair_already_complete_before_run']}",
        f"- scoped_duplicate_deletion_authorized: {packet['scoped_duplicate_deletion_authorized']}",
        f"- ready_for_subsystem_implementation_authorization_gate: {packet['ready_for_subsystem_implementation_authorization_gate']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- downstream: {packet['downstream']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Repair Summary",
        f"- source_manifest_count: {summary['source_manifest_count']}",
        f"- preflight_eligible_count: {summary['preflight_eligible_count']}",
        f"- preflight_blocked_count: {summary['preflight_blocked_count']}",
        f"- deleted_path_count: {summary['deleted_path_count']}",
        f"- held_path_count: {summary['held_path_count']}",
        f"- post_duplicate_remaining_count: {summary['post_duplicate_remaining_count']}",
        f"- canonical_counterparts_remaining_count: {summary['canonical_counterparts_remaining_count']}",
        f"- by_classification: {summary['by_classification']}",
        "",
        "## Validation Plan",
    ]
    lines.extend(
        f"- {item['command']} (required={item['required']})"
        for item in packet["validation_plan"]
    )
    lines.extend(["", "## Source Blockers"])
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    lines.extend(["", "## Preflight Blockers"])
    if packet["preflight_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["preflight_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
    source_design_receipt_path: str | Path = SOURCE_DESIGN_RECEIPT_PATH,
    execute_repair: bool = False,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt(
        repo_root,
        source_design_receipt_path=source_design_receipt_path,
        execute_repair=execute_repair,
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
