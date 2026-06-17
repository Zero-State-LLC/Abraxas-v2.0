from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "V2HygienePhase1CompletionValidationCiFrontierHygieneReceipt.v1"
RECEIPT_ID = "v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
SOURCE_RECEIPT_PLAN_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
    "receipt_plan_001.latest.json"
)
EXPECTED_SOURCE_STATUS = (
    "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
    "RECEIPT_PLAN_READY"
)
READY_STATUS = (
    "V2_HYGIENE_PHASE1_COMPLETION_VALIDATION_CI_FRONTIER_HYGIENE_RECEIPT_"
    "READY_FOR_SUBSYSTEM_IMPLEMENTATION_AUTHORIZATION_GATE"
)
BLOCKED_STATUS = (
    "V2_HYGIENE_PHASE1_COMPLETION_VALIDATION_CI_FRONTIER_HYGIENE_RECEIPT_"
    "BLOCKED_BY_UNQUARANTINED_FRONTIER_DRIFT"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"
CODEGEN_FIXTURE_DIR = Path("tests/fixtures/codegen")
PACKAGE_LOCK_PATH = Path("apps/aal-viz-live-console/package-lock.json")

AUTHORITY_FIELDS = (
    "cleanup_authorized",
    "deletion_authorized",
    "duplicate_file_mutation_authorized",
    "fixture_mutation_authorized",
    "package_lock_mutation_authorized",
    "decision_record_completion_authorized",
    "decision_record_completion_validation_authorized",
    "decision_record_completion_validation_performed",
    "decision_record_created",
    "decision_record_finalized",
    "decision_record_emitted",
    "decision_record_materialized",
    "authorization_record_created",
    "evidence_bundle_created",
    "operator_attestation_created",
    "subsystem_implementation_authorized",
    "implementation_authorized",
    "registry_mutation_authorized",
    "schema_mutation_authorized",
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
    "valid_for_decision_record_completion_validation",
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
        "cleanup": False,
        "decision_record_completion": False,
        "decision_record_completion_validation": False,
        "decision_record_creation": False,
        "decision_record_emission": False,
        "decision_record_finalization": False,
        "decision_record_materialization": False,
        "deletion": False,
        "duplicate_file_mutation": False,
        "evidence_bundle_creation": False,
        "execution_authority": False,
        "fixture_mutation": False,
        "forecast_routing": False,
        "github_writeback": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "package_lock_mutation": False,
        "promotion": False,
        "queue_mutation": False,
        "registry_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "subsystem_implementation": False,
        "v2_module_registration": False,
    }


def _run_git_status(repo_root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain=v1", "-z"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    paths: list[str] = []
    for entry in result.stdout.split("\0"):
        if not entry:
            continue
        # Porcelain v1 uses two status columns plus a space before the path.
        paths.append(entry[3:])
    return sorted(paths)


def _is_duplicate_frontier_path(path: str) -> bool:
    return " 2." in Path(path).name


def _classify_path(path: str) -> str:
    if path.startswith("tests/fixtures/codegen/"):
        return "codegen_fixture"
    if path.startswith("tests/"):
        return "pytest_candidate"
    if path.startswith("contracts/"):
        return "contract"
    if path.startswith("core/"):
        return "core"
    if path.startswith("scripts/"):
        return "script"
    if path.startswith("out/"):
        return "generated_output"
    if path.startswith("operator_input/") or path.startswith("input/"):
        return "operator_or_input"
    return "other"


def _canonical_counterpart(path: str) -> str:
    p = Path(path)
    return (p.parent / p.name.replace(" 2.", ".", 1)).as_posix()


def _inventory_duplicate_frontier(
    repo_root: Path,
    *,
    status_paths_override: Sequence[str] | None,
) -> dict[str, Any]:
    status_paths = (
        sorted(status_paths_override)
        if status_paths_override is not None
        else _run_git_status(repo_root)
    )
    duplicate_paths = sorted(path for path in status_paths if _is_duplicate_frontier_path(path))
    categories = Counter(_classify_path(path) for path in duplicate_paths)
    pytest_candidates = sorted(
        path
        for path in duplicate_paths
        if path.startswith("tests/") and path.endswith(".py")
    )
    sampled = duplicate_paths[:25]
    return {
        "status_path_count": len(status_paths),
        "duplicate_frontier_count": len(duplicate_paths),
        "duplicate_frontier_categories": dict(sorted(categories.items())),
        "duplicate_frontier_sample": sampled,
        "duplicate_pytest_collection_candidates": [
            {
                "path": path,
                "collected_by_pytest_pattern": Path(path).name.startswith("test_")
                and path.endswith(".py"),
                "provenance": "git_status_porcelain_path_inventory",
                "risk_level": "HIGH",
            }
            for path in pytest_candidates
        ],
        "duplicate_pytest_collection_candidate_count": len(pytest_candidates),
        "duplicate_frontier_mutation_authorized": False,
        "deletion_authorized": False,
        "cleanup_authorized": False,
    }


def _codegen_fixture_paths(
    repo_root: Path,
    *,
    codegen_fixture_paths_override: Sequence[str] | None,
) -> list[str]:
    if codegen_fixture_paths_override is not None:
        return sorted(codegen_fixture_paths_override)
    fixture_root = repo_root / CODEGEN_FIXTURE_DIR
    if not fixture_root.exists():
        return []
    return sorted(
        (CODEGEN_FIXTURE_DIR / path.name).as_posix()
        for path in fixture_root.glob("*.json")
    )


def _inventory_codegen_fixture_drift(
    repo_root: Path,
    *,
    codegen_fixture_paths_override: Sequence[str] | None,
) -> dict[str, Any]:
    fixture_paths = _codegen_fixture_paths(
        repo_root,
        codegen_fixture_paths_override=codegen_fixture_paths_override,
    )
    duplicate_fixture_paths = sorted(
        path for path in fixture_paths if _is_duplicate_frontier_path(path)
    )
    canonical_fixture_paths = sorted(
        path for path in fixture_paths if not _is_duplicate_frontier_path(path)
    )
    duplicate_assessments = []
    for path in duplicate_fixture_paths:
        counterpart = _canonical_counterpart(path)
        duplicate_assessments.append(
            {
                "path": path,
                "canonical_counterpart": counterpart,
                "canonical_counterpart_observed": counterpart in canonical_fixture_paths,
                "classification": (
                    "DUPLICATE_DERIVED_FRONTIER_CONTAMINANT"
                    if counterpart in canonical_fixture_paths
                    else "UNQUARANTINED_DUPLICATE_FIXTURE"
                ),
                "provenance": "tests/fixtures/codegen/*.json inventory",
                "risk_level": "HIGH",
            }
        )
    extra_fixture_source = (
        "duplicate_2_json_fixture"
        if duplicate_fixture_paths
        else "no_extra_fixture_observed"
    )
    return {
        "fixture_dir": CODEGEN_FIXTURE_DIR.as_posix(),
        "total_fixture_count": len(fixture_paths),
        "canonical_fixture_count": len(canonical_fixture_paths),
        "duplicate_fixture_count": len(duplicate_fixture_paths),
        "canonical_fixture_paths": canonical_fixture_paths,
        "duplicate_fixture_assessments": duplicate_assessments,
        "codegen_fixture_count_delta_source": extra_fixture_source,
        "extra_fixture_decision": (
            "DUPLICATE_DERIVED_NOT_CANONICAL"
            if duplicate_fixture_paths
            else "NO_DUPLICATE_DERIVED_EXTRA_FIXTURE"
        ),
        "fixture_mutation_authorized": False,
        "cleanup_authorized": False,
    }


def _package_lock_finding(repo_root: Path, package_lock_path: Path) -> dict[str, Any]:
    observed = (repo_root / package_lock_path).exists()
    return {
        "path": package_lock_path.as_posix(),
        "observed": observed,
        "classification": (
            "SEPARATE_DEPENDENCY_HYGIENE_FINDING"
            if observed
            else "DEPENDENCY_HYGIENE_FINDING_NOT_OBSERVED"
        ),
        "provenance": "filesystem_presence_check",
        "risk_level": "MEDIUM" if observed else "LOW",
        "package_lock_mutation_authorized": False,
        "bundled_into_completion_validation_lane": False,
    }


def _source_record(path: Path, packet: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": "completion_validation_receipt_plan",
        "path": path.as_posix(),
        "observed": bool(packet),
        "file_hash": _sha256(path),
        "packet_hash": str(packet.get("receipt_plan_hash", NOT_COMPUTABLE)),
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_SOURCE_STATUS,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "recommended_next_lane": str(packet.get("recommended_next_lane", NOT_COMPUTABLE)),
        "safe_to_auto_continue": packet.get("safe_to_auto_continue"),
        "valid_for_implementation": packet.get("valid_for_implementation"),
        "valid_for_execution": packet.get("valid_for_execution"),
    }


def _source_blockers(source: Mapping[str, Any]) -> list[str]:
    blockers = []
    if not source:
        return ["required_completion_validation_receipt_plan_missing"]
    if source.get("status") != EXPECTED_SOURCE_STATUS:
        blockers.append("source_completion_validation_receipt_plan_not_ready")
    if source.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("source_completion_validation_receipt_plan_not_source_ready")
    if source.get("recommended_next_lane") != NOT_COMPUTABLE:
        blockers.append("source_completion_validation_receipt_plan_lane_not_closed")
    if source.get("safe_to_auto_continue") is not False:
        blockers.append("source_completion_validation_receipt_plan_auto_continue_not_false")
    if source.get("valid_for_implementation") is not False:
        blockers.append("source_completion_validation_receipt_plan_implementation_not_false")
    if source.get("valid_for_execution") is not False:
        blockers.append("source_completion_validation_receipt_plan_execution_not_false")
    if not _locks_all_false(source.get("authority_locks")):
        blockers.append("source_completion_validation_receipt_plan_locks_not_all_false")
    for field in AUTHORITY_FIELDS:
        if source.get(field) is True:
            blockers.append(f"source_authority_expanding_field:{field}")
    return blockers


def _planned_quarantine_contract() -> dict[str, Any]:
    return {
        "contract_id": (
            "v2_hygiene_phase1_completion_validation_ci_frontier_quarantine_"
            "contract_001"
        ),
        "required_before_subsystem_implementation": True,
        "allowed_actions_in_this_receipt": [
            "inventory",
            "classification",
            "planning",
        ],
        "disallowed_actions_in_this_receipt": [
            "delete_duplicate_files",
            "modify_duplicate_files",
            "modify_package_lock",
            "perform_completion_validation",
            "implement_completion_validation_subsystem",
            "writeback_to_notion_or_github",
            "grant_execution_authority",
        ],
        "quarantine_authorized": False,
        "cleanup_authorized": False,
        "deletion_authorized": False,
        "subsystem_implementation_authorized": False,
    }


def build_v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt(
    repo_root: str | Path = ".",
    *,
    source_receipt_plan_path: str | Path = SOURCE_RECEIPT_PLAN_PATH,
    status_paths_override: Sequence[str] | None = None,
    codegen_fixture_paths_override: Sequence[str] | None = None,
    package_lock_path: str | Path = PACKAGE_LOCK_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_receipt_plan_path)
    source = _read_json(root / source_path) or {}
    duplicate_inventory = _inventory_duplicate_frontier(
        root,
        status_paths_override=status_paths_override,
    )
    fixture_inventory = _inventory_codegen_fixture_drift(
        root,
        codegen_fixture_paths_override=codegen_fixture_paths_override,
    )
    package_lock = _package_lock_finding(root, Path(package_lock_path))
    blockers = _source_blockers(source)
    if duplicate_inventory["duplicate_pytest_collection_candidate_count"]:
        blockers.append("duplicate_pytest_collection_candidates_unquarantined")
    if fixture_inventory["duplicate_fixture_count"]:
        blockers.append("codegen_duplicate_fixture_unquarantined")
    ready = bool(source) and not blockers
    status = READY_STATUS if ready else (BLOCKED_STATUS if source else NOT_COMPUTABLE)
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": status,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if source else "SOURCE_ARTIFACTS_NOT_READY",
        "source_blockers": sorted(set(blockers)),
        "sources_observed": bool(source),
        "source_records": [_source_record(source_path, source)],
        "duplicate_frontier_inventory": duplicate_inventory,
        "codegen_fixture_drift_inventory": fixture_inventory,
        "package_lock_hygiene_finding": package_lock,
        "planned_quarantine_contract": _planned_quarantine_contract(),
        "ready_for_subsystem_implementation_authorization_gate": ready,
        "recommended_next_action": (
            "request a separate subsystem implementation authorization gate"
            if ready
            else "obtain separate operator approval to quarantine or repair duplicate "
            "pytest collection candidates and duplicate Codegen fixture drift before "
            "subsystem implementation planning"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "downstream": NOT_COMPUTABLE,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authority_locks": _authority_locks(),
        "hygiene_receipt_hash": "",
    }
    for field in AUTHORITY_FIELDS:
        packet[field] = False
    packet["hygiene_receipt_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "hygiene_receipt_hash"}
    )
    return packet


def render_v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    duplicate_inventory = packet["duplicate_frontier_inventory"]
    fixture_inventory = packet["codegen_fixture_drift_inventory"]
    package_lock = packet["package_lock_hygiene_finding"]
    lines = [
        "# v2.0 Hygiene Phase 1 Completion-Validation CI Frontier Hygiene Receipt",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- ready_for_subsystem_implementation_authorization_gate: {packet['ready_for_subsystem_implementation_authorization_gate']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- downstream: {packet['downstream']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Duplicate Frontier Inventory",
        f"- duplicate_frontier_count: {duplicate_inventory['duplicate_frontier_count']}",
        f"- duplicate_pytest_collection_candidate_count: {duplicate_inventory['duplicate_pytest_collection_candidate_count']}",
        f"- deletion_authorized: {duplicate_inventory['deletion_authorized']}",
        f"- cleanup_authorized: {duplicate_inventory['cleanup_authorized']}",
        "",
        "## Codegen Fixture Drift",
        f"- total_fixture_count: {fixture_inventory['total_fixture_count']}",
        f"- canonical_fixture_count: {fixture_inventory['canonical_fixture_count']}",
        f"- duplicate_fixture_count: {fixture_inventory['duplicate_fixture_count']}",
        f"- codegen_fixture_count_delta_source: {fixture_inventory['codegen_fixture_count_delta_source']}",
        f"- extra_fixture_decision: {fixture_inventory['extra_fixture_decision']}",
        "",
        "## Package-Lock Hygiene Finding",
        f"- path: {package_lock['path']}",
        f"- observed: {package_lock['observed']}",
        f"- classification: {package_lock['classification']}",
        f"- package_lock_mutation_authorized: {package_lock['package_lock_mutation_authorized']}",
        "",
        "## Source Blockers",
    ]
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt(
        repo_root
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
