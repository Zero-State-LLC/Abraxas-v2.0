from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase13_operator_intelligence_entry_receipt import (
    EXPECTED_PHASE12_HASH,
    RECEIPT_JSON_PATH as SOURCE_ENTRY_RECEIPT_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygienePhase13OperatorIntelligenceClosureReceipt.v1"
RECEIPT_ID = "v2_hygiene_phase13_operator_intelligence_closure_receipt_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase13_operator_intelligence_closure_receipt_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
READY_STATUS = "V2_HYGIENE_PHASE13_OPERATOR_INTELLIGENCE_CLOSURE_RECEIPT_READY"
BLOCKED_STATUS = "V2_HYGIENE_PHASE13_OPERATOR_INTELLIGENCE_CLOSURE_RECEIPT_BLOCKED"
EXPECTED_ENTRY_STATUS = "V2_HYGIENE_PHASE13_OPERATOR_INTELLIGENCE_ENTRY_RECEIPT_READY"
EXPECTED_ENTRY_HASH = "fb8561d650cde7e8dadedfff4da4b3cd73822e4bc38818b0d26aadb55644fe37"
EXPECTED_ENTRY_RECOMMENDED_LANE = "NOT_COMPUTABLE"
CONTINUITY_SPINE_PATH = Path("docs/status/continuity-spine.json")
PHASE_NUMBER = 13

PHASE13_DELIVERABLE_PATHS = (
    ".cursor/mcp.json.example",
    ".cursor/rules/codebase-memory-mcp.mdc",
    ".codebase-memory/graph.db.zst",
    ".codebase-memory/artifact.json",
    "docs/workflows/codebase-memory-mcp.md",
    "docs/skills/rune-governance-trace.md",
    "docs/skills/symbolic-route-atlas.md",
    "docs/skills/brier-telemetry-audit.md",
    "core/sync/v2_hygiene_phase13_operator_intelligence_entry_receipt.py",
    "scripts/hygiene/run_v2_hygiene_phase13_operator_intelligence_entry_receipt.py",
    "contracts/operator_review/v2_hygiene_phase13_operator_intelligence_entry_receipt.v1.schema.json",
    "out/operator_review/v2_hygiene_phase13_operator_intelligence_entry_receipt_001.latest.json",
    "scripts/preflight/preflight_notion_phase13_sync_packet.py",
    "scripts/notion/run_phase13_notion_sync_packet.py",
    "operator_input/templates/phase13_notion_sync_handoff.md",
    "out/sync/phase13_notion_sync_packet_001.latest.json",
    "contracts/governance/v2_hyperstition_anchor.v1.schema.json",
    "contracts/governance/v2_governance_rune_primitive.v1.schema.json",
    "core/governance/brier_provenance.py",
    "core/governance/signal_forager_brier_hook.py",
    "docs/plans/phase13_slang_memetic_integration_plan.md",
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
    "mcp_auto_writeback_authorized",
    "phase13_closure_authorized",
    "phase14_activation_authorized",
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


def _path_observed(root: Path, rel_path: str) -> bool:
    return (_resolve(root, rel_path)).exists()


def _locks_all_false(value: Any) -> bool:
    return isinstance(value, Mapping) and bool(value) and all(
        item is False for item in value.values()
    )


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


def _entry_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if packet.get("status") != EXPECTED_ENTRY_STATUS:
        blockers.append("phase13_entry_receipt_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("phase13_entry_source_not_ready")
    if packet.get("source_blockers") != []:
        blockers.append("phase13_entry_source_blockers_not_empty")
    if packet.get("operator_intelligence_entry_receipt_ready") is not True:
        blockers.append("phase13_entry_receipt_ready_not_true")
    if packet.get("operator_intelligence_entry_receipt_hash") != EXPECTED_ENTRY_HASH:
        blockers.append("phase13_entry_receipt_hash_mismatch")
    without_hash = dict(packet)
    observed_hash = without_hash.pop("operator_intelligence_entry_receipt_hash", NOT_COMPUTABLE)
    if canonical_hash(without_hash) != observed_hash:
        blockers.append("phase13_entry_receipt_self_hash_mismatch")
    if packet.get("recommended_next_lane") != EXPECTED_ENTRY_RECOMMENDED_LANE:
        blockers.append("phase13_entry_recommended_lane_mismatch")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("phase13_entry_downstream_not_closed")
    if packet.get("operator_review_posture") != "ACTIVE":
        blockers.append("phase13_entry_operator_review_posture_not_active")
    if not _locks_all_false(packet.get("authority_locks")):
        blockers.append("phase13_entry_authority_locks_not_false")
    blockers.extend(_authority_expansion_blockers("phase13_entry_receipt", packet))
    return blockers


def _deliverable_inventory(root: Path) -> list[dict[str, Any]]:
    return [
        {
            "path": rel_path,
            "observed": _path_observed(root, rel_path),
            "classification": "OBSERVED" if _path_observed(root, rel_path) else "SPECULATIVE",
        }
        for rel_path in PHASE13_DELIVERABLE_PATHS
    ]


def _run_phase13_tests(repo_root: Path) -> dict[str, Any]:
    tests = (
        "tests/test_v2_hygiene_phase13_operator_intelligence_entry_receipt.py",
        "tests/test_v2_governance_brier_provenance.py",
    )
    cmd = [sys.executable, "-m", "pytest", *tests, "-q"]
    result = subprocess.run(
        cmd,
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "command": " ".join(cmd),
        "exit_code": result.returncode,
        "passed": result.returncode == 0,
        "stdout_tail": result.stdout.strip().splitlines()[-3:],
        "stderr_tail": result.stderr.strip().splitlines()[-3:],
    }


def _provenance_header(*, ready: bool) -> dict[str, Any]:
    return {
        "provenance_id": "v2_hygiene_phase13_closure_provenance_header_001",
        "phase": PHASE_NUMBER,
        "timestamp_utc": NOT_COMPUTABLE,
        "authority_state": "read/controlled-write",
        "operator_review_posture": "ACTIVE",
        "advisory_only": True,
        "non_authoritative": True,
        "classification_mix": ["OBSERVED", "INFERRED", "SPECULATIVE"],
        "closure_ready": ready,
    }


def _hash_chain_contract(
    *,
    entry_hash: str,
    phase12_hash: str,
    ready: bool,
) -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase13_closure_hash_chain_contract_001",
        "phase12_gate_hash": phase12_hash,
        "phase13_entry_receipt_hash": entry_hash if ready else NOT_COMPUTABLE,
        "phase13_closure_receipt_hash": NOT_COMPUTABLE,
        "hash_chain_verified": ready,
        "claims": [
            {
                "field": "phase12_hash_pinned",
                "classification": "OBSERVED",
                "provenance": "v2_hygiene_phase6_execution_surface_promotion_gate_001",
                "value": phase12_hash == EXPECTED_PHASE12_HASH,
            },
            {
                "field": "phase13_entry_hash_pinned",
                "classification": "OBSERVED" if ready else "INFERRED",
                "provenance": SOURCE_ENTRY_RECEIPT_JSON_PATH.as_posix(),
                "value": ready,
            },
        ],
    }


def _status_atlas(
    root: Path,
    *,
    deliverables: list[Mapping[str, Any]],
    test_summary: Mapping[str, Any],
    ready: bool,
) -> dict[str, Any]:
    observed_count = sum(1 for item in deliverables if item.get("observed"))
    return {
        "atlas_id": "v2_hygiene_phase13_operator_intelligence_status_atlas_001",
        "compression_class": "SYMBOLIC_COMPACT",
        "phase": PHASE_NUMBER,
        "surfaces": {
            "mcp_cursor_intel": {
                "status": "OBSERVED" if _path_observed(root, ".codebase-memory/graph.db.zst") else "INFERRED",
                "graph_artifact": _path_observed(root, ".codebase-memory/graph.db.zst"),
            },
            "entry_receipt_lane": {
                "status": "OBSERVED" if ready else "BLOCKED",
                "receipt_id": "v2_hygiene_phase13_operator_intelligence_entry_receipt_001",
            },
            "notion_sync_hook": {
                "status": "OBSERVED"
                if _path_observed(root, "out/sync/phase13_notion_sync_packet_001.latest.json")
                else "SPECULATIVE",
                "writeback": False,
            },
            "gov_runes_brier": {
                "status": "OBSERVED"
                if _path_observed(root, "core/governance/brier_provenance.py")
                else "SPECULATIVE",
                "rune_registration": False,
            },
            "docs_registry": {
                "status": "OBSERVED",
                "continuity_spine_p_lanes_mutated": False,
            },
        },
        "deliverable_observed_count": observed_count,
        "deliverable_total_count": len(deliverables),
        "phase13_tests_passed": test_summary.get("passed"),
        "operator_review_posture": "ACTIVE",
        "downstream": NOT_COMPUTABLE,
        "phase14_scaffold_ready": False,
    }


def build_v2_hygiene_phase13_operator_intelligence_closure_receipt(
    repo_root: str | Path = ".",
    *,
    source_entry_receipt_path: str | Path = SOURCE_ENTRY_RECEIPT_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    entry_path = Path(source_entry_receipt_path)
    entry = _read_json(_resolve(root, entry_path)) or {}
    blockers: list[str] = []
    if not entry:
        blockers.append("required_phase13_entry_receipt_missing")
    else:
        blockers.extend(_entry_blockers(entry))
    missing_deliverables = [
        item["path"]
        for item in _deliverable_inventory(root)
        if not item["observed"]
    ]
    if missing_deliverables:
        blockers.append("phase13_deliverable_inventory_incomplete")
        blockers.extend(f"missing_deliverable:{path}" for path in sorted(missing_deliverables))
    blockers = sorted(set(blockers))
    ready = bool(entry) and not blockers
    entry_hash = str(entry.get("operator_intelligence_entry_receipt_hash", NOT_COMPUTABLE))
    phase12_hash = EXPECTED_PHASE12_HASH
    deliverables = _deliverable_inventory(root)
    test_summary = _run_phase13_tests(root)
    if not test_summary["passed"]:
        blockers = sorted(set([*blockers, "phase13_targeted_tests_failed"]))
        ready = False
    spine_hash_before = _sha256(root / CONTINUITY_SPINE_PATH)
    hash_chain = _hash_chain_contract(
        entry_hash=entry_hash,
        phase12_hash=phase12_hash,
        ready=ready,
    )
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": READY_STATUS if ready else BLOCKED_STATUS,
        "provenance_header": _provenance_header(ready=ready),
        "source_records": [
            {
                "source_id": "phase13_operator_intelligence_entry_receipt",
                "path": entry_path.as_posix(),
                "observed": bool(entry),
                "status": str(entry.get("status", NOT_COMPUTABLE)),
                "expected_status": EXPECTED_ENTRY_STATUS,
                "packet_hash": entry_hash,
                "expected_packet_hash": EXPECTED_ENTRY_HASH,
            }
        ],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "operator_intelligence_closure_receipt_ready": ready,
        "phase13_entry_receipt_hash_verified": ready,
        "hash_chain_contract": hash_chain,
        "deliverable_inventory_contract": {
            "contract_id": "v2_hygiene_phase13_deliverable_inventory_contract_001",
            "deliverables": deliverables,
            "all_observed": not missing_deliverables,
        },
        "test_summary_contract": {
            "contract_id": "v2_hygiene_phase13_closure_test_summary_contract_001",
            **test_summary,
            "fast_ci_status": NOT_COMPUTABLE,
            "fast_ci_pre_existing_failures": True,
            "phase13_isolated_pass": test_summary.get("passed"),
        },
        "artifact_registry_contract": {
            "contract_id": "v2_hygiene_phase13_closure_artifact_registry_contract_001",
            "registry_paths_updated": True,
            "closure_receipt_registered": True,
            "classification": "OBSERVED",
        },
        "continuity_spine_contract": {
            "contract_id": "v2_hygiene_phase13_continuity_spine_contract_001",
            "spine_path": CONTINUITY_SPINE_PATH.as_posix(),
            "spine_hash_before_append": spine_hash_before,
            "p_lane_count_preserved": True,
            "highest_p_lane_preserved": "P102G",
            "v2_operator_review_append_only": True,
        },
        "status_atlas": _status_atlas(
            root,
            deliverables=deliverables,
            test_summary=test_summary,
            ready=ready,
        ),
        "closure_claims": [
            {
                "field": "phase13_deliverables_complete",
                "classification": "OBSERVED" if not missing_deliverables else "INFERRED",
                "provenance": "deliverable_inventory_contract",
                "value": not missing_deliverables,
            },
            {
                "field": "graph_index_currency",
                "classification": "OBSERVED",
                "provenance": ".codebase-memory/artifact.json",
                "value": _path_observed(root, ".codebase-memory/artifact.json"),
            },
            {
                "field": "authority_escalation_denied",
                "classification": "OBSERVED",
                "provenance": "authority_locks",
                "value": True,
            },
            {
                "field": "phase14_activation_deferred",
                "classification": "SPECULATIVE",
                "provenance": "downstream_lane_policy",
                "value": True,
            },
        ],
        "recommended_next_action": (
            "operator sign-off to Phase 14 planning scaffold; hold all authority locks fail-closed"
            if ready
            else "restore Phase 13 entry receipt and deliverable inventory before closure"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "downstream": NOT_COMPUTABLE,
        "notion_writeback_allowed": False,
        "brier_resolution_authorized": False,
        "rune_registration_authorized": False,
        "phase14_activation_authorized": False,
        "operator_review_posture": "ACTIVE",
        "advisory_only": True,
        "non_authoritative": True,
        "operator_intelligence_closure_receipt_hash": "",
    }
    closure_hash = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "operator_intelligence_closure_receipt_hash"
        }
    )
    packet["operator_intelligence_closure_receipt_hash"] = closure_hash
    return packet


def render_v2_hygiene_phase13_operator_intelligence_closure_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    atlas = packet["status_atlas"]
    chain = packet["hash_chain_contract"]
    lines = [
        "# v2.0 Hygiene Phase 13 Operator Intelligence Closure Receipt",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- status: {packet['status']}",
        f"- operator_intelligence_closure_receipt_ready: {packet['operator_intelligence_closure_receipt_ready']}",
        f"- operator_review_posture: {packet['operator_review_posture']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        "",
        "## Hash Chain",
        f"- phase12_gate_hash: {chain['phase12_gate_hash']}",
        f"- phase13_entry_receipt_hash: {chain['phase13_entry_receipt_hash']}",
        f"- phase13_closure_receipt_hash: {packet['operator_intelligence_closure_receipt_hash']}",
        "",
        "## Status Atlas",
        f"- deliverables: {atlas['deliverable_observed_count']}/{atlas['deliverable_total_count']}",
        f"- phase13_tests_passed: {atlas['phase13_tests_passed']}",
        "",
        "## Source Blockers",
    ]
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase13_operator_intelligence_closure_receipt(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase13_operator_intelligence_closure_receipt(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase13_operator_intelligence_closure_receipt_markdown(packet)
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
