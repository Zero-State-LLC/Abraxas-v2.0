from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "V2HygienePhase1DuplicateFrontierQuarantineDesignReceipt.v1"
RECEIPT_ID = "v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
SOURCE_HYGIENE_RECEIPT_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt_001.latest.json"
)
EXPECTED_SOURCE_STATUS = (
    "V2_HYGIENE_PHASE1_COMPLETION_VALIDATION_CI_FRONTIER_HYGIENE_RECEIPT_"
    "BLOCKED_BY_UNQUARANTINED_FRONTIER_DRIFT"
)
READY_STATUS = (
    "V2_HYGIENE_PHASE1_DUPLICATE_FRONTIER_QUARANTINE_DESIGN_RECEIPT_READY"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"
PACKAGE_LOCK_PATH = "apps/aal-viz-live-console/package-lock.json"

AUTHORITY_FIELDS = (
    "cleanup_authorized",
    "deletion_authorized",
    "file_movement_authorized",
    "quarantine_execution_authorized",
    "duplicate_file_mutation_authorized",
    "gitignore_mutation_authorized",
    "pytest_configuration_mutation_authorized",
    "fixture_mutation_authorized",
    "package_lock_mutation_authorized",
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
        "cleanup": False,
        "completion_validation_execution": False,
        "decision_record_completion": False,
        "deletion": False,
        "duplicate_file_mutation": False,
        "execution_authority": False,
        "file_movement": False,
        "fixture_mutation": False,
        "forecast_routing": False,
        "github_writeback": False,
        "gitignore_mutation": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "package_lock_mutation": False,
        "promotion": False,
        "pytest_configuration_mutation": False,
        "quarantine_execution": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
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
    return sorted(entry[3:] for entry in result.stdout.split("\0") if entry)


def _is_duplicate_path(path: str) -> bool:
    return " 2." in Path(path).name


def _canonical_counterpart(path: str) -> str:
    p = Path(path)
    return (p.parent / p.name.replace(" 2.", ".", 1)).as_posix()


def _category(path: str) -> str:
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
    if path.startswith(("operator_input/", "input/")):
        return "operator_or_input"
    return "other"


def _manifest_classification(path: str, counterpart_exists: bool, hashes_equal: bool) -> str:
    if path == PACKAGE_LOCK_PATH:
        return "OUT_OF_SCOPE_PACKAGE_LOCK"
    if path.startswith("tests/fixtures/codegen/") and path.endswith(".json"):
        return "CODEGEN_FIXTURE_BLOCKER"
    if path.startswith("tests/") and path.endswith(".py") and Path(path).name.startswith(
        "test_"
    ):
        return "PYTEST_COLLECTION_BLOCKER"
    if path.startswith("out/"):
        return "GENERATED_OUTPUT_DUPLICATE"
    if counterpart_exists and hashes_equal:
        return "SAFE_DUPLICATE_CANDIDATE"
    return "NON_IDENTICAL_HOLD"


def _recommended_action(classification: str) -> str:
    return {
        "SAFE_DUPLICATE_CANDIDATE": "plan_future_operator_approved_quarantine_or_removal",
        "NON_IDENTICAL_HOLD": "hold_for_manual_diff_review_before_any_repair",
        "PYTEST_COLLECTION_BLOCKER": "plan_future_operator_approved_pytest_duplicate_quarantine",
        "CODEGEN_FIXTURE_BLOCKER": "plan_future_operator_approved_fixture_duplicate_quarantine",
        "GENERATED_OUTPUT_DUPLICATE": "plan_future_operator_approved_generated_duplicate_quarantine",
        "OUT_OF_SCOPE_PACKAGE_LOCK": "keep_out_of_scope_for_dependency_hygiene_lane",
    }[classification]


def _risk_level(classification: str) -> str:
    if classification in {
        "PYTEST_COLLECTION_BLOCKER",
        "CODEGEN_FIXTURE_BLOCKER",
        "NON_IDENTICAL_HOLD",
    }:
        return "HIGH"
    if classification in {"GENERATED_OUTPUT_DUPLICATE", "OUT_OF_SCOPE_PACKAGE_LOCK"}:
        return "MEDIUM"
    return "LOW"


def _build_manifest(
    repo_root: Path,
    *,
    status_paths_override: Sequence[str] | None,
) -> list[dict[str, Any]]:
    status_paths = (
        sorted(status_paths_override)
        if status_paths_override is not None
        else _run_git_status(repo_root)
    )
    duplicate_paths = sorted(path for path in status_paths if _is_duplicate_path(path))
    manifest: list[dict[str, Any]] = []
    for path in duplicate_paths:
        duplicate_path = repo_root / path
        counterpart = _canonical_counterpart(path)
        counterpart_path = repo_root / counterpart
        duplicate_hash = _sha256(duplicate_path)
        counterpart_hash = _sha256(counterpart_path)
        counterpart_exists = counterpart_path.exists()
        hashes_equal = (
            duplicate_hash != NOT_COMPUTABLE
            and counterpart_hash != NOT_COMPUTABLE
            and duplicate_hash == counterpart_hash
        )
        classification = _manifest_classification(path, counterpart_exists, hashes_equal)
        manifest.append(
            {
                "path": path,
                "category": _category(path),
                "canonical_counterpart": counterpart,
                "canonical_counterpart_observed": counterpart_exists,
                "duplicate_hash": duplicate_hash,
                "canonical_counterpart_hash": counterpart_hash,
                "byte_equal_to_counterpart": hashes_equal,
                "pytest_collectable": path.startswith("tests/")
                and path.endswith(".py")
                and Path(path).name.startswith("test_"),
                "fixture_impact": path.startswith("tests/fixtures/codegen/")
                and path.endswith(".json"),
                "classification": classification,
                "recommended_action": _recommended_action(classification),
                "provenance": "git_status_porcelain_path_inventory_with_hash_comparison",
                "risk_level": _risk_level(classification),
                "mutation_authorized": False,
            }
        )
    return manifest


def _manifest_summary(manifest: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_category = Counter(str(item["category"]) for item in manifest)
    by_classification = Counter(str(item["classification"]) for item in manifest)
    byte_equal_count = sum(1 for item in manifest if item["byte_equal_to_counterpart"])
    counterpart_missing_count = sum(
        1 for item in manifest if not item["canonical_counterpart_observed"]
    )
    return {
        "duplicate_manifest_count": len(manifest),
        "by_category": dict(sorted(by_category.items())),
        "by_classification": dict(sorted(by_classification.items())),
        "byte_equal_to_counterpart_count": byte_equal_count,
        "non_byte_equal_or_missing_counterpart_count": len(manifest) - byte_equal_count,
        "counterpart_missing_count": counterpart_missing_count,
        "pytest_collectable_count": sum(1 for item in manifest if item["pytest_collectable"]),
        "fixture_impact_count": sum(1 for item in manifest if item["fixture_impact"]),
    }


def _source_blockers(source: Mapping[str, Any], manifest: Sequence[Mapping[str, Any]]) -> list[str]:
    blockers = []
    if not source:
        return ["required_ci_frontier_hygiene_receipt_missing"]
    if source.get("status") != EXPECTED_SOURCE_STATUS:
        blockers.append("source_ci_frontier_hygiene_receipt_not_blocked_as_expected")
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
    if not manifest:
        blockers.append("duplicate_manifest_empty")
    return blockers


def _source_record(path: Path, packet: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": "ci_frontier_hygiene_receipt",
        "path": path.as_posix(),
        "observed": bool(packet),
        "file_hash": _sha256(path),
        "packet_hash": str(packet.get("hygiene_receipt_hash", NOT_COMPUTABLE)),
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_SOURCE_STATUS,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "ready_for_subsystem_implementation_authorization_gate": packet.get(
            "ready_for_subsystem_implementation_authorization_gate"
        ),
        "recommended_next_lane": str(packet.get("recommended_next_lane", NOT_COMPUTABLE)),
        "downstream": str(packet.get("downstream", NOT_COMPUTABLE)),
    }


def _repair_playbook() -> dict[str, Any]:
    return {
        "playbook_id": "v2_hygiene_phase1_duplicate_frontier_repair_playbook_plan_001",
        "repair_authorized": False,
        "steps": [
            "review_manifest_classifications",
            "hold_non_identical_paths_for_manual_diff_review",
            "request_separate_operator_repair_authorization",
            "only_after_authorization_quarantine_or_remove_proven_duplicate_candidates",
            "rerun_targeted_codegen_tests_and_fast_ci",
            "emit_separate_repair_validation_receipt",
        ],
        "disallowed_actions_in_this_receipt": [
            "delete_files",
            "move_files",
            "edit_gitignore",
            "edit_pytest_configuration",
            "mutate_fixtures",
            "mutate_package_lock",
            "implement_completion_validation_subsystem",
        ],
    }


def _planned_brier_contract() -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase1_duplicate_frontier_brier_telemetry_contract_001",
        "telemetry_only": True,
        "claim_id": "duplicate_is_safe_to_quarantine",
        "required_fields": [
            "claim_id",
            "forecast_probability",
            "binary_outcome",
            "brier_score",
            "resolution_source",
        ],
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "resolution_allowed": False,
        "adaptive_learning_authorized": False,
        "forecast_routing_authorized": False,
        "promotion_authorized": False,
        "execution_authority": False,
    }


def _rune_mapping() -> list[dict[str, Any]]:
    return [
        {
            "rune": "Observe",
            "governance_mapping": "inventory duplicate frontier paths",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": "bind duplicate paths to canonical counterparts and hashes",
            "authority_granted": False,
            "risk_level": "MEDIUM",
        },
        {
            "rune": "Hold",
            "governance_mapping": "keep subsystem implementation blocked while contamination remains",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Sever",
            "governance_mapping": "future repair lane only; no current quarantine authority",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Seal",
            "governance_mapping": "future post-repair validation state only",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt(
    repo_root: str | Path = ".",
    *,
    source_hygiene_receipt_path: str | Path = SOURCE_HYGIENE_RECEIPT_PATH,
    status_paths_override: Sequence[str] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_hygiene_receipt_path)
    source = _read_json(root / source_path) or {}
    manifest = _build_manifest(root, status_paths_override=status_paths_override)
    blockers = sorted(set(_source_blockers(source, manifest)))
    design_ready = bool(source) and not blockers
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": READY_STATUS if design_ready else NOT_COMPUTABLE,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if source else "SOURCE_ARTIFACTS_NOT_READY",
        "source_blockers": blockers,
        "sources_observed": bool(source),
        "source_records": [_source_record(source_path, source)],
        "duplicate_manifest_summary": _manifest_summary(manifest),
        "duplicate_manifest": manifest,
        "repair_playbook": _repair_playbook(),
        "planned_brier_scoring_contract": _planned_brier_contract(),
        "planned_rune_governance_mapping": _rune_mapping(),
        "ready_for_subsystem_implementation_authorization_gate": False,
        "recommended_next_action": (
            "request separate operator repair authorization for duplicate frontier "
            "quarantine or removal; keep subsystem implementation locked"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "downstream": NOT_COMPUTABLE,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authority_locks": _authority_locks(),
        "quarantine_design_receipt_hash": "",
    }
    for field in AUTHORITY_FIELDS:
        packet[field] = False
    packet["quarantine_design_receipt_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "quarantine_design_receipt_hash"
        }
    )
    return packet


def render_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    summary = packet["duplicate_manifest_summary"]
    brier = packet["planned_brier_scoring_contract"]
    lines = [
        "# v2.0 Hygiene Phase 1 Duplicate Frontier Quarantine Design Receipt",
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
        "## Duplicate Manifest Summary",
        f"- duplicate_manifest_count: {summary['duplicate_manifest_count']}",
        f"- pytest_collectable_count: {summary['pytest_collectable_count']}",
        f"- fixture_impact_count: {summary['fixture_impact_count']}",
        f"- byte_equal_to_counterpart_count: {summary['byte_equal_to_counterpart_count']}",
        f"- non_byte_equal_or_missing_counterpart_count: {summary['non_byte_equal_or_missing_counterpart_count']}",
        f"- by_classification: {summary['by_classification']}",
        f"- by_category: {summary['by_category']}",
        "",
        "## Repair Playbook",
    ]
    lines.extend(f"- {step}" for step in packet["repair_playbook"]["steps"])
    lines.extend(
        [
            "",
            "## Brier Telemetry Contract",
            f"- telemetry_only: {brier['telemetry_only']}",
            f"- claim_id: {brier['claim_id']}",
            f"- brier_score_formula: {brier['brier_score_formula']}",
            f"- resolution_allowed: {brier['resolution_allowed']}",
            f"- adaptive_learning_authorized: {brier['adaptive_learning_authorized']}",
            f"- forecast_routing_authorized: {brier['forecast_routing_authorized']}",
            "",
            "## Source Blockers",
        ]
    )
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt(
        repo_root
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
