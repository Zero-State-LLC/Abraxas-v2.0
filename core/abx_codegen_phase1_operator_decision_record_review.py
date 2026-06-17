from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_phase1_operator_decision_record_dry_run import (
    DRY_RUN_JSON_PATH as SOURCE_DRY_RUN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxCodegenPhase1OperatorDecisionRecordReview.v1"
REVIEW_ID = "abx_codegen_phase1_operator_decision_record_review_001"
REVIEW_JSON_PATH = Path(
    "out/operator_review/abx_codegen_phase1_operator_decision_record_review_001.latest.json"
)
REVIEW_MD_PATH = REVIEW_JSON_PATH.with_suffix(".md")

EXPECTED_SOURCE_STATUS = "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_RECORD_DRY_RUN_READY"


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
        return "NOT_COMPUTABLE"


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


def build_abx_codegen_phase1_operator_decision_record_review(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    source_path = root / SOURCE_DRY_RUN_JSON
    dry_run = _read_json(source_path)
    dry_run_observed = dry_run is not None
    dry_run = dry_run or {}
    validation_blockers = _string_list(dry_run.get("validation_blockers"))
    simulated = dry_run.get("simulated_decision_record", {})

    source_ready = (
        dry_run.get("schema_version") == "AbxCodegenPhase1OperatorDecisionRecordDryRun.v1"
        and dry_run.get("status") == EXPECTED_SOURCE_STATUS
        and dry_run.get("validation_passed") is True
        and dry_run.get("simulated_only") is True
        and dry_run.get("operator_input_required") is True
        and dry_run.get("operator_decision_attested") is False
        and dry_run.get("decision_record_created") is False
        and dry_run.get("authorization_record_lane_authorized") is False
        and dry_run.get("implementation_authorized") is False
        and dry_run.get("implementation_unblocked") is False
        and dry_run.get("execution_authority") is False
        and dry_run.get("valid_for_implementation") is False
        and dry_run.get("recommended_next_patch") == "NOT_COMPUTABLE"
        and isinstance(simulated, Mapping)
        and simulated.get("selected_follow_on_action") == "MAINTAIN_PHASE1_OPERATOR_REVIEW_HOLD"
        and bool(validation_blockers)
    )

    if not dry_run_observed:
        status = "NOT_COMPUTABLE"
        source_readiness = "SOURCE_DRY_RUN_MISSING"
        review_findings = [
            {
                "finding_id": "source_dry_run_missing",
                "finding_status": "NOT_COMPUTABLE",
                "authority_granted": False,
            }
        ]
        terminal_hold_reason = "source dry-run evidence is missing or unreadable"
    elif not source_ready:
        status = "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_RECORD_REVIEW_BLOCKED"
        source_readiness = "SOURCE_DRY_RUN_NOT_READY"
        review_findings = [
            {
                "finding_id": "source_dry_run_not_ready",
                "finding_status": "BLOCKED",
                "authority_granted": False,
            }
        ]
        terminal_hold_reason = "source dry-run evidence is not ready for operator review"
    else:
        status = "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_RECORD_REVIEW_HELD_FOR_OPERATOR"
        source_readiness = "SOURCE_DRY_RUN_READY"
        review_findings = [
            {
                "finding_id": "simulated_decision_record_shape_validated",
                "finding_status": "OBSERVED",
                "authority_granted": False,
            },
            {
                "finding_id": "operator_attestations_missing",
                "finding_status": "HELD_FOR_OPERATOR",
                "authority_granted": False,
            },
            {
                "finding_id": "decision_record_creation_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
            {
                "finding_id": "authorization_record_lane_creation_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
            {
                "finding_id": "implementation_unblock_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
        ]
        terminal_hold_reason = (
            "operator attestations are missing; this review cannot create a Phase 1 "
            "decision record, authorize an authorization-record lane, or unblock Codegen implementation"
        )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "review_id": REVIEW_ID,
        "review_hash": "",
        "source_dry_run_path": str(SOURCE_DRY_RUN_JSON),
        "source_dry_run_file_hash": _sha256(source_path),
        "source_dry_run_packet_hash": str(dry_run.get("dry_run_hash", "NOT_COMPUTABLE")),
        "source_dry_run_ready": source_ready,
        "source_readiness": source_readiness,
        "validation_blockers": validation_blockers,
        "review_findings": review_findings,
        "selected_operator_decision": "HOLD_FOR_OPERATOR_REVIEW"
        if source_ready
        else "NOT_COMPUTABLE",
        "selected_follow_on_action": "MAINTAIN_PHASE1_OPERATOR_REVIEW_HOLD"
        if source_ready
        else "NOT_COMPUTABLE",
        "terminal_hold_reason": terminal_hold_reason,
        "operator_review_required": True,
        "operator_input_required": True,
        "operator_attestations_present": False,
        "operator_decision_attested": False,
        "decision_record_created": False,
        "authorization_record_created": False,
        "authorization_record_lane_authorized": False,
        "implementation_authorized": False,
        "implementation_unblocked": False,
        "shadow_replay_execution_authorized": False,
        "recommended_next_patch": "NOT_COMPUTABLE",
        "recommended_next_action": (
            "collect explicit external operator attestation evidence before any future "
            "Phase 1 decision-record lane; do not auto-create a decision record, "
            "authorization-record lane, implementation patch, shadow replay, or Codegen execution"
            if source_ready
            else "repair source dry-run evidence before review"
        ),
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "authority_locks": _authority_locks(),
    }
    packet["review_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "review_hash"}
    )
    return packet


def render_abx_codegen_phase1_operator_decision_record_review_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Phase 1 Operator Decision Record Review",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `source_dry_run_ready`: `{packet['source_dry_run_ready']}`",
        f"- `selected_operator_decision`: `{packet['selected_operator_decision']}`",
        f"- `selected_follow_on_action`: `{packet['selected_follow_on_action']}`",
        f"- `operator_attestations_present`: `{packet['operator_attestations_present']}`",
        f"- `decision_record_created`: `{packet['decision_record_created']}`",
        f"- `authorization_record_lane_authorized`: `{packet['authorization_record_lane_authorized']}`",
        f"- `implementation_unblocked`: `{packet['implementation_unblocked']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Review Findings",
        "",
    ]
    for finding in packet["review_findings"]:
        if isinstance(finding, Mapping):
            lines.append(f"- `{finding['finding_id']}`: `{finding['finding_status']}`")
    lines.extend(["", "## Source Validation Blockers", ""])
    for blocker in packet["validation_blockers"]:
        lines.append(f"- `{blocker}`")
    return lines


def write_abx_codegen_phase1_operator_decision_record_review(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_codegen_phase1_operator_decision_record_review(root)
    write_canonical_json(target_root / REVIEW_JSON_PATH, packet)
    _write_markdown(
        target_root / REVIEW_MD_PATH,
        render_abx_codegen_phase1_operator_decision_record_review_markdown(packet),
    )
    return packet
