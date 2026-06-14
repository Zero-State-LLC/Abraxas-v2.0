from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_shadow_replay_harness_operator_decision_record_plan import (
    OUT_JSON as SOURCE_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenShadowReplayHarnessOperatorDecisionRecordDryRun.v1"
DRY_RUN_ID = (
    "ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_REPLAY_HARNESS_"
    "OPERATOR_DECISION_RECORD_DRY_RUN_001"
)
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_"
    "record_dry_run_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_"
    "record_dry_run_001.latest.md"
)

EXPECTED_SOURCE_STATUS = (
    "ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_PLAN_READY"
)
EXPECTED_SOURCE_NEXT_LANE = (
    "ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_DRY_RUN"
)
RECOMMENDED_NEXT_LANE = (
    "ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_REVIEW"
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


def _field_names(rows: Any) -> list[str]:
    if not isinstance(rows, list):
        return []
    names: list[str] = []
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get("field"), str):
            names.append(row["field"])
    return names


def _decision_names(rows: Any) -> list[str]:
    if not isinstance(rows, list):
        return []
    names: list[str] = []
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get("decision"), str):
            names.append(row["decision"])
    return names


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _check(check_id: str, passed: bool) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed}


def build_abx_codegen_shadow_replay_harness_operator_decision_record_dry_run(
    *,
    repo_root: str | Path,
    source_operator_decision_record_plan_path: str | Path = SOURCE_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_operator_decision_record_plan_path).as_posix()
    source = _read_json(root / source_operator_decision_record_plan_path)
    source_observed = bool(source)

    required_fields = _field_names(source.get("required_record_fields"))
    allowed_decisions = _decision_names(source.get("allowed_decisions"))
    attachments = _string_list(source.get("required_attachments"))
    lineage_requirements = _string_list(source.get("lineage_requirements"))
    attestation = source.get("operator_attestation_requirements", {})
    meta_gate = source.get("meta_gate_requirements", {})

    source_ready = (
        source.get("artifact_type")
        == "AbxCodegenShadowReplayHarnessOperatorDecisionRecordPlan.v1"
        and source.get("operator_decision_record_plan_status") == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == EXPECTED_SOURCE_NEXT_LANE
        and source.get("planned_record_type") == "CodegenOperatorDecisionRecord.v1"
        and source.get("record_creation_authorized") is False
        and source.get("operator_decision_attested") is False
        and source.get("implementation_authorization_granted") is False
        and source.get("decision_record_created") is False
        and source.get("valid_for_execution") is False
        and source.get("valid_for_implementation") is False
        and isinstance(attestation, dict)
        and attestation.get("human_operator_required") is True
        and attestation.get("codex_or_spine_attestation_allowed") is False
        and isinstance(meta_gate, dict)
        and meta_gate.get("codegen_spine_self_authorization_allowed") is False
    )

    validation_results = sorted(
        [
            _check("source_ready", source_ready),
            _check("required_record_fields_present", bool(required_fields)),
            _check("allowed_decisions_present", bool(allowed_decisions)),
            _check("required_attachments_present", bool(attachments)),
            _check("lineage_requirements_present", bool(lineage_requirements)),
            _check(
                "human_operator_attestation_required",
                isinstance(attestation, dict) and attestation.get("human_operator_required") is True,
            ),
            _check(
                "codex_attestation_denied",
                isinstance(attestation, dict)
                and attestation.get("codex_or_spine_attestation_allowed") is False,
            ),
            _check(
                "meta_gate_self_authorization_denied",
                isinstance(meta_gate, dict)
                and meta_gate.get("codegen_spine_self_authorization_allowed") is False,
            ),
            _check("decision_record_creation_denied", source.get("decision_record_created") is False),
            _check(
                "implementation_authorization_denied",
                source.get("implementation_authorization_granted") is False,
            ),
            _check("execution_denied", source.get("valid_for_execution") is False),
        ],
        key=lambda row: row["check_id"],
    )
    failed_checks = [str(row["check_id"]) for row in validation_results if row["passed"] is False]

    if not source_observed:
        dry_run_status = "NOT_COMPUTABLE"
        validation_passed = False
        blockers = [
            "source_operator_decision_record_plan_missing_or_unreadable",
            f"source_path:{source_path}",
        ]
        recommended_next_lane = "NOT_COMPUTABLE"
    elif not source_ready:
        dry_run_status = "BLOCKED_BY_ABX_CODEGEN_OPERATOR_DECISION_RECORD_PLAN"
        validation_passed = False
        blockers = [f"validation_check_failed:{check_id}" for check_id in failed_checks]
        recommended_next_lane = "NOT_COMPUTABLE"
    else:
        dry_run_status = "ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_DRY_RUN_READY"
        validation_passed = True
        blockers = [
            "operator_identity_not_attested",
            "operator_decision_not_attested",
            "operator_rationale_not_attested",
            "operator_signature_not_attested",
            "operator_evidence_bundle_not_attested",
        ]
        recommended_next_lane = RECOMMENDED_NEXT_LANE

    simulated_record = {
        "artifact_type": "CodegenOperatorDecisionRecord.v1.simulated",
        "simulated_only": True,
        "decision_record_id": (
            "ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_REPLAY_HARNESS_"
            "OPERATOR_DECISION_RECORD_001_SIMULATED"
        ),
        "decision_type": "Normal | Meta-Gate | High-Risk",
        "selected_decision": "DEFER",
        "allowed_decisions": allowed_decisions,
        "required_record_fields": required_fields,
        "required_attachments": attachments,
        "lineage_requirements": lineage_requirements,
        "operator_attestation_required": True,
        "operator_decision_attested": False,
        "decision_record_created": False,
        "implementation_authorization_granted": False,
        "meta_gate_authorization_granted": False,
        "execution_authority": False,
        "valid_for_execution": False,
    }

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "dry_run_id": DRY_RUN_ID,
        "operator_decision_record_dry_run_status": dry_run_status,
        "source_operator_decision_record_plan": {
            "path": source_path,
            "hash": _sha256(root / source_operator_decision_record_plan_path),
            "operator_decision_record_plan_status": str(
                source.get("operator_decision_record_plan_status", "NOT_COMPUTABLE")
            ),
            "recommended_next_lane": str(source.get("recommended_next_lane", "NOT_COMPUTABLE")),
            "source_observed": source_observed,
            "source_ready": source_ready,
        },
        "validation_results": validation_results,
        "validation_passed": validation_passed,
        "validation_blockers": blockers,
        "simulated_decision_record": simulated_record,
        "simulated_only": True,
        "operator_input_required": True,
        "operator_approved": False,
        "decision_record_created": False,
        "implementation_authorization_granted": False,
        "meta_gate_authorization_granted": False,
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_action": (
            "review the advisory simulated operator decision record shape only; do not create "
            "a decision record, authorize harness implementation, or grant meta-gate authority"
            if validation_passed
            else "repair source operator decision record plan evidence before review"
        ),
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


def write_abx_codegen_shadow_replay_harness_operator_decision_record_dry_run(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_shadow_replay_harness_operator_decision_record_dry_run_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Shadow Replay Harness Operator Decision Record Dry Run",
        "",
        f"- dry_run_id: {packet['dry_run_id']}",
        f"- operator_decision_record_dry_run_status: {packet['operator_decision_record_dry_run_status']}",
        f"- validation_passed: {packet['validation_passed']}",
        f"- simulated_only: {packet['simulated_only']}",
        f"- operator_input_required: {packet['operator_input_required']}",
        f"- operator_approved: {packet['operator_approved']}",
        f"- decision_record_created: {packet['decision_record_created']}",
        f"- implementation_authorization_granted: {packet['implementation_authorization_granted']}",
        f"- meta_gate_authorization_granted: {packet['meta_gate_authorization_granted']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Validation Results",
    ]
    for row in packet.get("validation_results", []):
        if isinstance(row, dict):
            lines.append(f"- {row['check_id']}: {row['passed']}")
    lines.extend(["", "## Validation Blockers"])
    for blocker in packet.get("validation_blockers", []):
        lines.append(f"- {blocker}")
    sim = packet.get("simulated_decision_record", {})
    if isinstance(sim, dict):
        lines.extend(["", "## Simulated Decision Record"])
        lines.append(f"- artifact_type: {sim['artifact_type']}")
        lines.append(f"- selected_decision: {sim['selected_decision']}")
        lines.append(f"- decision_record_created: {sim['decision_record_created']}")
        lines.append(
            f"- implementation_authorization_granted: {sim['implementation_authorization_granted']}"
        )
    return lines


def write_abx_codegen_shadow_replay_harness_operator_decision_record_dry_run_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(render_abx_codegen_shadow_replay_harness_operator_decision_record_dry_run_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
