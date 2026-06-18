from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_shadow_replay_harness_operator_attestation_intake_gate import (
    GATE_JSON_PATH as SOURCE_INTAKE_GATE_JSON_PATH,
)
from core.abx_codegen_shadow_replay_harness_operator_decision_record_dry_run import (
    OUT_JSON as SOURCE_DRY_RUN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenShadowReplayHarnessOperatorDecisionRecordReview.v1"
REVIEW_ID = (
    "ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_REPLAY_HARNESS_"
    "OPERATOR_DECISION_RECORD_REVIEW_001"
)
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_"
    "record_review_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_"
    "record_review_001.latest.md"
)

EXPECTED_SOURCE_STATUS = (
    "ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_DRY_RUN_READY"
)
EXPECTED_SOURCE_NEXT_LANE = (
    "ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_REVIEW"
)
EXPECTED_INTAKE_STATUS = (
    "ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_ATTESTATION_INTAKE_VALIDATED"
)
EXPECTED_INTAKE_DOWNSTREAM = "INTAKE_CLEARED_ONLY"
REVIEW_HELD_STATUS = (
    "ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_REVIEW_HELD_FOR_OPERATOR"
)
REVIEW_INTAKE_CLEARED_STATUS = (
    "ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_REVIEW_INTAKE_CLEARED_OBSERVED"
)


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _read_json(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def build_abx_codegen_shadow_replay_harness_operator_decision_record_review(
    *,
    repo_root: str | Path,
    source_operator_decision_record_dry_run_path: str | Path = SOURCE_DRY_RUN_JSON,
    source_attestation_intake_gate_path: str | Path = SOURCE_INTAKE_GATE_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_operator_decision_record_dry_run_path).as_posix()
    intake_path = Path(source_attestation_intake_gate_path).as_posix()
    source = _read_json(root / source_operator_decision_record_dry_run_path)
    intake = _read_json(root / source_attestation_intake_gate_path)
    validation_blockers = _list(source.get("validation_blockers"))
    source_ready = (
        source.get("artifact_type")
        == "AbxCodegenShadowReplayHarnessOperatorDecisionRecordDryRun.v1"
        and source.get("operator_decision_record_dry_run_status") == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == EXPECTED_SOURCE_NEXT_LANE
        and source.get("validation_passed") is True
        and source.get("simulated_only") is True
        and source.get("operator_input_required") is True
        and source.get("operator_approved") is False
        and source.get("decision_record_created") is False
        and source.get("implementation_authorization_granted") is False
        and source.get("meta_gate_authorization_granted") is False
        and source.get("execution_authority") is False
        and bool(validation_blockers)
    )
    intake_observed = bool(intake)
    intake_cleared = (
        intake_observed
        and intake.get("status") == EXPECTED_INTAKE_STATUS
        and intake.get("downstream") == EXPECTED_INTAKE_DOWNSTREAM
        and intake.get("intake_validated_for_operator_decision_record") is True
        and intake.get("harness_implementation_authorized") is False
        and intake.get("authority_granted") is False
    )

    if source_ready and intake_cleared:
        review_status = REVIEW_INTAKE_CLEARED_STATUS
    elif source_ready:
        review_status = REVIEW_HELD_STATUS
    else:
        review_status = "NOT_COMPUTABLE"

    review_findings = [
        {
            "finding_id": "review_finding_001_simulated_odr_shape_validated",
            "finding_status": "OBSERVED" if source_ready else "NOT_COMPUTABLE",
            "authority_granted": False,
        },
        {
            "finding_id": "review_finding_002_operator_attestations_missing",
            "finding_status": "HELD_FOR_OPERATOR" if source_ready else "NOT_COMPUTABLE",
            "authority_granted": False,
        },
        {
            "finding_id": "review_finding_003_decision_record_creation_denied",
            "finding_status": "ENFORCED" if source_ready else "NOT_COMPUTABLE",
            "authority_granted": False,
        },
        {
            "finding_id": "review_finding_004_harness_implementation_denied",
            "finding_status": "ENFORCED" if source_ready else "NOT_COMPUTABLE",
            "authority_granted": False,
        },
        {
            "finding_id": "review_finding_005_meta_gate_authorization_denied",
            "finding_status": "ENFORCED" if source_ready else "NOT_COMPUTABLE",
            "authority_granted": False,
        },
        {
            "finding_id": "review_finding_006_attestation_intake_gate_cleared_observed",
            "finding_status": "OBSERVED" if intake_cleared else "NOT_COMPUTABLE",
            "authority_granted": False,
        },
    ]

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "review_id": REVIEW_ID,
        "operator_decision_record_review_status": review_status,
        "source_operator_decision_record_dry_run": {
            "path": source_path,
            "hash": _sha256(root / source_operator_decision_record_dry_run_path),
            "operator_decision_record_dry_run_status": str(
                source.get("operator_decision_record_dry_run_status", "NOT_COMPUTABLE")
            ),
            "recommended_next_lane": str(source.get("recommended_next_lane", "NOT_COMPUTABLE")),
            "validation_passed": source.get("validation_passed") is True,
            "validation_blockers": validation_blockers,
            "source_ready": source_ready,
        },
        "source_attestation_intake_gate": {
            "path": intake_path,
            "hash": str(intake.get("gate_hash", _sha256(root / source_attestation_intake_gate_path))),
            "status": str(intake.get("status", "NOT_COMPUTABLE")),
            "downstream": str(intake.get("downstream", "NOT_COMPUTABLE")),
            "intake_validated_for_operator_decision_record": intake.get(
                "intake_validated_for_operator_decision_record", False
            )
            is True,
            "intake_cleared_observed": intake_cleared,
        },
        "selected_operator_decision": "MAINTAIN_HOLD" if source_ready else "NOT_COMPUTABLE",
        "review_only": True,
        "operator_review_required": True,
        "operator_input_required": True,
        "operator_approved": False,
        "operator_attestations_present": False,
        "decision_record_created": False,
        "implementation_authorization_granted": False,
        "meta_gate_authorization_granted": False,
        "review_findings": review_findings,
        "terminal_hold_reason": (
            "attestation intake gate cleared; harness implementation authorization still "
            "denied; no codegen operator decision record, harness implementation, or "
            "meta-gate authorization can be created by this review"
            if intake_cleared
            else (
                "operator attestations are missing; no codegen operator decision record, "
                "harness implementation, or meta-gate authorization can be created by this review"
                if source_ready
                else "NOT_COMPUTABLE"
            )
        ),
        "recommended_next_lane": "NOT_COMPUTABLE",
        "recommended_next_action": (
            "intake clearance observed; separate harness implementation authorization "
            "required before any future Codegen decision record lane; do not auto-create "
            "a decision record, implement the harness, or grant meta-gate authority"
            if intake_cleared
            else (
                "collect explicit external operator attestation evidence before any future "
                "Codegen decision record lane; do not auto-create a decision record, implement "
                "the harness, or grant meta-gate authority"
                if source_ready
                else "repair source operator decision record dry-run evidence before review"
            )
        ),
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "authority_locks": {
            "authorization_record_creation": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "decision_record_creation": False,
            "execution_authority": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "harness_implementation": False,
            "meta_gate_authorization": False,
            "notion_writeback": False,
            "operator_decision_attestation": False,
            "queue_mutation": False,
            "receipt_creation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "self_authorization": False,
            "shadow_replay_execution": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_shadow_replay_harness_operator_decision_record_review(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_shadow_replay_harness_operator_decision_record_review_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Shadow Replay Harness Operator Decision Record Review",
        "",
        f"- review_id: {packet['review_id']}",
        f"- operator_decision_record_review_status: {packet['operator_decision_record_review_status']}",
        f"- selected_operator_decision: {packet['selected_operator_decision']}",
        f"- operator_attestations_present: {packet['operator_attestations_present']}",
        f"- decision_record_created: {packet['decision_record_created']}",
        f"- implementation_authorization_granted: {packet['implementation_authorization_granted']}",
        f"- meta_gate_authorization_granted: {packet['meta_gate_authorization_granted']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Source Attestation Intake Gate",
    ]
    intake = packet.get("source_attestation_intake_gate", {})
    if isinstance(intake, Mapping):
        lines.extend(
            [
                f"- path: {intake.get('path', 'NOT_COMPUTABLE')}",
                f"- status: {intake.get('status', 'NOT_COMPUTABLE')}",
                f"- downstream: {intake.get('downstream', 'NOT_COMPUTABLE')}",
                f"- intake_cleared_observed: {intake.get('intake_cleared_observed', False)}",
            ]
        )
    lines.extend(["", "## Review Findings"])
    for finding in packet.get("review_findings", []):
        if isinstance(finding, Mapping):
            lines.append(f"- {finding['finding_id']}: {finding['finding_status']}")
    lines.extend(["", "## Source Validation Blockers"])
    source = packet.get("source_operator_decision_record_dry_run", {})
    blockers = source.get("validation_blockers", []) if isinstance(source, Mapping) else []
    for blocker in blockers:
        lines.append(f"- {blocker}")
    return lines


def write_abx_codegen_shadow_replay_harness_operator_decision_record_review_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(render_abx_codegen_shadow_replay_harness_operator_decision_record_review_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
