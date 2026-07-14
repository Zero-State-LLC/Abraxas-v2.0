from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.runtime_integration_gate_operator_review_dry_run import (
    DRY_RUN_JSON_PATH as SOURCE_DRY_RUN_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "RuntimeIntegrationGateOperatorReviewDryRunReview.v1"
REVIEW_ID = "runtime_integration_gate_operator_review_dry_run_review_001"
REVIEW_JSON_PATH = Path(
    "out/audit/runtime_integration_gate_operator_review_dry_run_review_001.latest.json"
)
REVIEW_MD_PATH = REVIEW_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DRY_RUN_READY"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return NOT_COMPUTABLE


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _authority_locks() -> dict[str, bool]:
    return {
        "activation_allowed": False,
        "auto_approval_allowed": False,
        "canon_mutation_allowed": False,
        "codegen_implementation_allowed": False,
        "decision_record_creation": False,
        "execution_authority": False,
        "forecast_routing_allowed": False,
        "github_writeback_allowed": False,
        "mandatory_pre_dispatch_wiring": False,
        "notion_writeback_allowed": False,
        "operator_attestation": False,
        "queue_mutation_allowed": False,
        "replay_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "valid_for_execution": False,
        "valid_for_runtime_wiring": False,
    }


def build_runtime_integration_gate_operator_review_dry_run_review(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / SOURCE_DRY_RUN_JSON_PATH
    dry_run = _read_json(source_path)
    dry_run_observed = dry_run is not None
    dry_run = dry_run or {}
    validation_blockers = _string_list(dry_run.get("validation_blockers"))
    simulated = dry_run.get("simulated_review_record", {})
    source_ready = (
        dry_run.get("schema_version") == "RuntimeIntegrationGateOperatorReviewDryRun.v1"
        and dry_run.get("status") == EXPECTED_SOURCE_STATUS
        and dry_run.get("validation_passed") is True
        and dry_run.get("simulated_only") is True
        and dry_run.get("operator_input_required") is True
        and dry_run.get("operator_attestation_present") is False
        and isinstance(simulated, Mapping)
        and simulated.get("mandatory_pre_dispatch_wiring_enabled") is False
        and simulated.get("valid_for_execution") is False
        and simulated.get("valid_for_runtime_wiring") is False
        and bool(validation_blockers)
    )

    if not dry_run_observed:
        status = NOT_COMPUTABLE
        source_readiness = "SOURCE_DRY_RUN_MISSING"
        terminal_hold_reason = "source dry-run evidence is missing or unreadable"
    elif not source_ready:
        status = "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DRY_RUN_REVIEW_BLOCKED"
        source_readiness = "SOURCE_DRY_RUN_NOT_READY"
        terminal_hold_reason = "source dry-run is not ready for review"
    else:
        status = "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DRY_RUN_REVIEW_HELD_FOR_OPERATOR"
        source_readiness = "SOURCE_DRY_RUN_READY"
        terminal_hold_reason = (
            "simulated runtime integration gate operator review held for external attestations"
        )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "review_id": REVIEW_ID,
        "status": status,
        "source_dry_run_path": SOURCE_DRY_RUN_JSON_PATH.as_posix(),
        "source_dry_run_hash": str(dry_run.get("dry_run_hash", NOT_COMPUTABLE)),
        "source_dry_run_status": str(dry_run.get("status", NOT_COMPUTABLE)),
        "source_readiness": source_readiness,
        "source_ready": source_ready,
        "validation_blockers": validation_blockers,
        "simulated_review_record": simulated if isinstance(simulated, Mapping) else {},
        "terminal_hold_reason": terminal_hold_reason,
        "operator_attestation_present": False,
        "operator_input_required": True,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "authority_locks": _authority_locks(),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_action": (
            "hold runtime integration gate operator review for external attestations; "
            "do not enable mandatory pre-dispatch wiring or runtime mutation"
            if source_ready
            else "restore runtime integration gate operator review dry-run evidence before review"
        ),
        "safe_to_auto_continue": False,
        "downstream": NOT_COMPUTABLE,
    }
    return {**packet, "review_hash": canonical_hash(packet)}


def render_markdown(packet: Mapping[str, Any]) -> list[str]:
    lines = [
        "# Runtime Integration Gate Operator Review Dry Run Review 001",
        "",
        f"- review_id: {packet['review_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- terminal_hold_reason: {packet['terminal_hold_reason']}",
        "",
        "## Validation Blockers",
    ]
    for blocker in packet.get("validation_blockers", []):
        lines.append(f"- {blocker}")
    return lines


def write_runtime_integration_gate_operator_review_dry_run_review(
    repo_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_runtime_integration_gate_operator_review_dry_run_review(root)
    write_canonical_json(target_root / REVIEW_JSON_PATH, packet)
    target_root.joinpath(REVIEW_MD_PATH).parent.mkdir(parents=True, exist_ok=True)
    target_root.joinpath(REVIEW_MD_PATH).write_text(
        "\n".join(render_markdown(packet)) + "\n",
        encoding="utf-8",
    )
    return packet
