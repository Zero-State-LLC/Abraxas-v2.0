from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_phase1_operator_decision_record_plan import (
    PLAN_JSON_PATH as SOURCE_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxCodegenPhase1OperatorDecisionRecordDryRun.v1"
DRY_RUN_ID = "abx_codegen_phase1_operator_decision_record_dry_run_001"
DRY_RUN_JSON_PATH = Path(
    "out/operator_review/abx_codegen_phase1_operator_decision_record_dry_run_001.latest.json"
)
DRY_RUN_MD_PATH = DRY_RUN_JSON_PATH.with_suffix(".md")

EXPECTED_SOURCE_STATUS = "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_RECORD_PLAN_READY"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _authority_locks() -> dict[str, bool]:
    return {
        "authorization_record_creation": False,
        "authorization_record_lane_creation": False,
        "canon_mutation": False,
        "code_generation": False,
        "code_mutation": False,
        "contracts_codegen_directory_creation": False,
        "core_codegen_directory_creation": False,
        "core_harness_file_creation": False,
        "decision_record_creation": False,
        "execution": False,
        "file_writeback": False,
        "forecast_routing": False,
        "github_writeback": False,
        "implementation_authorization": False,
        "implementation_unblock": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "patch_application": False,
        "promotion_to_canary": False,
        "receipt_creation": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "shadow_replay_execution": False,
    }


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def build_abx_codegen_phase1_operator_decision_record_dry_run(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    plan = _read_json(root / SOURCE_PLAN_JSON)
    plan_observed = plan is not None
    plan = plan or {}

    source_ready = (
        plan.get("schema_version") == "AbxCodegenPhase1OperatorDecisionRecordPlan.v1"
        and plan.get("status") == EXPECTED_SOURCE_STATUS
        and plan.get("recommended_next_patch") == "NOT_COMPUTABLE"
        and plan.get("safe_to_auto_continue") is False
        and plan.get("operator_input_required") is True
        and plan.get("decision_record_created") is False
        and plan.get("authorization_record_lane_authorized") is False
        and plan.get("implementation_authorized") is False
        and plan.get("execution_authority") is False
        and plan.get("valid_for_implementation") is False
    )

    if not plan_observed:
        status = "NOT_COMPUTABLE"
        validation_passed = False
        validation_blockers = [
            "source_decision_record_plan_missing_or_unreadable",
            f"source_path:{SOURCE_PLAN_JSON}",
        ]
    elif not source_ready:
        status = "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_RECORD_DRY_RUN_BLOCKED"
        validation_passed = False
        validation_blockers = ["source_decision_record_plan_not_ready"]
    else:
        status = "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_RECORD_DRY_RUN_READY"
        validation_passed = True
        validation_blockers = [
            "operator_identity_not_attested",
            "operator_decision_not_attested",
            "operator_rationale_not_attested",
            "operator_acknowledgements_not_attested",
            "operator_evidence_bundle_not_attested",
        ]

    simulated_record = {
        "artifact_type": "AbxCodegenPhase1OperatorDecisionRecord.v1.simulated",
        "simulated_only": True,
        "decision_record_id": "abx_codegen_phase1_operator_decision_record_001.simulated",
        "decision_record_hash": "SIMULATED_PENDING_OPERATOR_INPUT",
        "selected_decision": "HOLD_FOR_OPERATOR_REVIEW",
        "decision_rationale": "SIMULATED_PENDING_OPERATOR_INPUT",
        "decision_outcome_summary": "SIMULATED_HOLD_PENDING_OPERATOR_INPUT",
        "selected_follow_on_action": "MAINTAIN_PHASE1_OPERATOR_REVIEW_HOLD",
        "terminal_authority_summary": "SIMULATED_NO_AUTHORITY_GRANTED",
        "operator_identity_fields": _string_list(
            plan.get("required_operator_identity_fields")
        ),
        "decision_fields": _string_list(plan.get("required_decision_fields")),
        "acknowledgement_fields": _string_list(
            plan.get("required_acknowledgement_fields")
        ),
        "evidence_fields": _string_list(plan.get("required_evidence_fields")),
        "output_fields": _string_list(plan.get("required_output_fields")),
        "operator_decision_attested": False,
        "decision_record_created": False,
        "authorization_record_created": False,
        "authorization_record_lane_authorized": False,
        "implementation_authorized": False,
        "implementation_unblocked": False,
        "shadow_replay_execution_authorized": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
    }

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "dry_run_id": DRY_RUN_ID,
        "dry_run_hash": "",
        "source_plan_path": str(SOURCE_PLAN_JSON),
        "source_plan_hash": str(plan.get("decision_record_plan_hash", "NOT_COMPUTABLE")),
        "source_plan_ready": source_ready,
        "validation_passed": validation_passed,
        "validation_blockers": validation_blockers,
        "simulated_decision_record": simulated_record,
        "simulated_only": True,
        "operator_input_required": True,
        "operator_decision_attested": False,
        "decision_record_created": False,
        "authorization_record_created": False,
        "authorization_record_lane_authorized": False,
        "implementation_authorized": False,
        "implementation_unblocked": False,
        "recommended_next_patch": "NOT_COMPUTABLE",
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "authority_locks": _authority_locks(),
    }
    packet["dry_run_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "dry_run_hash"}
    )
    return packet


def render_abx_codegen_phase1_operator_decision_record_dry_run_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Phase 1 Operator Decision Record Dry Run",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `source_plan_ready`: `{packet['source_plan_ready']}`",
        f"- `validation_passed`: `{packet['validation_passed']}`",
        f"- `simulated_only`: `{packet['simulated_only']}`",
        f"- `decision_record_created`: `{packet['decision_record_created']}`",
        f"- `authorization_record_lane_authorized`: `{packet['authorization_record_lane_authorized']}`",
        f"- `implementation_unblocked`: `{packet['implementation_unblocked']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Validation Blockers",
        "",
    ]
    for blocker in packet["validation_blockers"]:
        lines.append(f"- `{blocker}`")
    lines.extend(["", "## Simulated Decision Record", ""])
    simulated = packet["simulated_decision_record"]
    if isinstance(simulated, Mapping):
        lines.extend(
            [
                f"- `selected_decision`: `{simulated['selected_decision']}`",
                f"- `selected_follow_on_action`: `{simulated['selected_follow_on_action']}`",
                f"- `terminal_authority_summary`: `{simulated['terminal_authority_summary']}`",
            ]
        )
    return lines


def write_abx_codegen_phase1_operator_decision_record_dry_run(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_codegen_phase1_operator_decision_record_dry_run(root)
    write_canonical_json(target_root / DRY_RUN_JSON_PATH, packet)
    _write_markdown(
        target_root / DRY_RUN_MD_PATH,
        render_abx_codegen_phase1_operator_decision_record_dry_run_markdown(packet),
    )
    return packet
