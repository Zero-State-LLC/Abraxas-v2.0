from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "RuntimeIntegrationGateOperatorReviewDryRun.v1"
DRY_RUN_ID = "runtime_integration_gate_operator_review_dry_run_001"
DRY_RUN_JSON_PATH = Path(
    "out/audit/runtime_integration_gate_operator_review_dry_run_001.latest.json"
)
DRY_RUN_MD_PATH = DRY_RUN_JSON_PATH.with_suffix(".md")
SOURCE_SPEC_PLAN_PATH = Path(
    "out/audit/runtime_integration_gate_operator_review_advisory_spec_plan_001.latest.json"
)
EXPECTED_SOURCE_STATUS = "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_ADVISORY_SPEC_PLAN_READY"
NOT_COMPUTABLE = "NOT_COMPUTABLE"


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


def build_runtime_integration_gate_operator_review_dry_run(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    spec_plan = _read_json(root / SOURCE_SPEC_PLAN_PATH)
    spec_plan_observed = spec_plan is not None
    spec_plan = spec_plan or {}
    source_ready = (
        spec_plan.get("artifact_type") == "RuntimeIntegrationGateOperatorReviewAdvisorySpecPlan.v1"
        and spec_plan.get("plan_status") == EXPECTED_SOURCE_STATUS
        and spec_plan.get("operator_review_required") is True
        and spec_plan.get("operator_attestation_present") is False
        and spec_plan.get("valid_for_execution") is False
        and spec_plan.get("valid_for_runtime_wiring") is False
        and spec_plan.get("runtime_mutation_allowed") is False
        and spec_plan.get("recommended_next_lane") == "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DRY_RUN"
    )

    if not spec_plan_observed:
        status = NOT_COMPUTABLE
        validation_passed = False
        validation_blockers = [
            "source_spec_plan_missing_or_unreadable",
            f"source_path:{SOURCE_SPEC_PLAN_PATH.as_posix()}",
        ]
    elif not source_ready:
        status = "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DRY_RUN_BLOCKED"
        validation_passed = False
        validation_blockers = ["source_spec_plan_not_ready"]
    else:
        status = "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DRY_RUN_READY"
        validation_passed = True
        validation_blockers = [
            "operator_identity_not_attested",
            "authority_owner_mapping_not_attested",
            "no_authority_seal_review_not_attested",
            "codegen_boundary_review_not_attested",
            "receipt_freshness_review_not_attested",
        ]

    simulated_review_record = {
        "artifact_type": "RuntimeIntegrationGateOperatorReviewRecord.v1.simulated",
        "simulated_only": True,
        "review_record_id": "runtime_integration_gate_operator_review_record_001.simulated",
        "review_record_hash": "SIMULATED_PENDING_OPERATOR_INPUT",
        "selected_decision": "HOLD_FOR_OPERATOR_REVIEW",
        "decision_outcome_summary": "SIMULATED_HOLD_PENDING_OPERATOR_INPUT",
        "mandatory_pre_dispatch_wiring_enabled": False,
        "runtime_mutation_allowed": False,
        "valid_for_execution": False,
        "valid_for_runtime_wiring": False,
        "operator_attestation_present": False,
        "review_questions_acknowledged": False,
        "blocked_patch_classes_acknowledged": True,
    }

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "dry_run_id": DRY_RUN_ID,
        "status": status,
        "source_spec_plan_path": SOURCE_SPEC_PLAN_PATH.as_posix(),
        "source_spec_plan_hash": str(spec_plan.get("packet_hash", NOT_COMPUTABLE)),
        "source_spec_plan_ready": source_ready,
        "validation_passed": validation_passed,
        "validation_blockers": validation_blockers,
        "simulated_review_record": simulated_review_record,
        "simulated_only": True,
        "operator_input_required": True,
        "operator_attestation_present": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "authority_locks": _authority_locks(),
        "recommended_next_lane": (
            "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DRY_RUN_REVIEW"
            if source_ready
            else NOT_COMPUTABLE
        ),
        "recommended_next_action": (
            "review the simulated runtime integration gate operator review record "
            "and hold for external operator attestations without enabling runtime wiring"
            if source_ready
            else "restore the runtime integration gate operator review spec plan before dry-run review"
        ),
        "safe_to_auto_continue": False,
        "downstream": NOT_COMPUTABLE,
    }
    return {**packet, "dry_run_hash": canonical_hash(packet)}


def render_markdown(packet: Mapping[str, Any]) -> list[str]:
    lines = [
        "# Runtime Integration Gate Operator Review Dry Run 001",
        "",
        f"- dry_run_id: {packet['dry_run_id']}",
        f"- status: {packet['status']}",
        f"- source_spec_plan_ready: {packet['source_spec_plan_ready']}",
        f"- validation_passed: {packet['validation_passed']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        "",
        "## Validation Blockers",
    ]
    for blocker in packet.get("validation_blockers", []):
        lines.append(f"- {blocker}")
    return lines


def write_runtime_integration_gate_operator_review_dry_run(
    repo_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_runtime_integration_gate_operator_review_dry_run(root)
    write_canonical_json(target_root / DRY_RUN_JSON_PATH, packet)
    target_root.joinpath(DRY_RUN_MD_PATH).parent.mkdir(parents=True, exist_ok=True)
    target_root.joinpath(DRY_RUN_MD_PATH).write_text(
        "\n".join(render_markdown(packet)) + "\n",
        encoding="utf-8",
    )
    return packet
