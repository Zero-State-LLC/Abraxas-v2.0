from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxResearchCanaryArtifactRegistryCoverageRepairOperatorDecisionRecordPlan.v1"
PLAN_ID = "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_RECORD_PLAN_001"
REQUEST_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_operator_decision_request_001.latest.json"
)
PHASE_RECEIPT_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt_001.latest.json"
)
PLAN_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan_001.latest.json"
)
PLAN_MD_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan_001.latest.md"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    request = _read_json(root / REQUEST_JSON_PATH)
    phase_receipt = _read_json(root / PHASE_RECEIPT_JSON_PATH)

    request_ready = (
        request.get("status") == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_REQUEST_EMITTED"
        and request.get("spec_plan_ready") is True
    )
    phase_receipt_ready = (
        phase_receipt.get("receipt_status")
        == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_PHASE_EXECUTION_RECEIPT_EMITTED"
        and phase_receipt.get("phases_complete") is True
    )
    plan_ready = request_ready and phase_receipt_ready

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": PLAN_ID,
        "status": "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_RECORD_PLAN_READY"
        if plan_ready
        else "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_RECORD_PLAN_BLOCKED",
        "decision_record_plan_id": PLAN_ID,
        "command": "BUILD_ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_RECORD_PLAN_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "registry_mutation_allowed": False,
        "implementation_authorized": False,
        "spec_authoring_only_if_approved": True,
        "safe_to_auto_continue": False,
        "operator_input_required": True,
        "decision_scope": str(request.get("decision_scope", NOT_COMPUTABLE)),
        "target_surface": str(request.get("target_surface", NOT_COMPUTABLE)),
        "target_plan_id": str(request.get("target_plan_id", NOT_COMPUTABLE)),
        "recommended_default_decision": str(request.get("recommended_decision", "HOLD")),
        "recommended_next_action": (
            "collect explicit operator decision evidence; operator may select AUTHORIZE_REGISTRY_REPAIR_EXECUTION_SPEC "
            "to approve spec authoring only while preserving registry repair execution denial"
            if plan_ready
            else "repair decision request and phase execution receipt prerequisites"
        ),
        "recommended_next_lane": "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_RECORD_001"
        if plan_ready
        else NOT_COMPUTABLE,
        "decision_options": list(request.get("decision_options", [])),
        "required_operator_identity_fields": [
            "operator_id",
            "operator_name",
            "operator_role",
            "decision_timestamp_utc",
        ],
        "required_decision_fields": [
            "selected_decision",
            "decision_rationale",
            "decision_scope_acknowledged",
            "registry_repair_execution_spec_required",
        ],
        "required_acknowledgement_fields": [
            "advisory_only_acknowledged",
            "non_authoritative_acknowledged",
            "execution_authority_denied_acknowledged",
            "p130_advisory_hold_preservation_acknowledged",
            "orphan_exclusion_policy_acknowledged",
        ],
        "required_evidence_fields": [
            "reviewed_request_id",
            "reviewed_request_hash",
            "reviewed_phase_receipt_hash",
            "reviewed_phase_count",
        ],
        "allowed_follow_on_actions": sorted(
            set(
                list(request.get("follow_on_actions_if_approved", []))
                + list(request.get("follow_on_actions_if_held", []))
                + list(request.get("follow_on_actions_if_rejected", []))
                + list(request.get("follow_on_actions_if_orphan_review_requested", []))
            )
        ),
        "disallowed_follow_on_actions": list(request.get("blocked_actions", [])),
        "future_record_output_candidates": [
            "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_001.latest.json",
            "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_001.latest.md",
        ],
        "required_review_artifacts": [
            str(REQUEST_JSON_PATH),
            str(PHASE_RECEIPT_JSON_PATH),
            str(request.get("source_spec_plan_path", NOT_COMPUTABLE)),
        ],
        "source_request_path": str(REQUEST_JSON_PATH),
        "source_request_id": str(request.get("request_id", NOT_COMPUTABLE)),
        "source_phase_receipt_path": str(PHASE_RECEIPT_JSON_PATH),
        "source_hashes": {
            "operator_decision_request": str(request.get("request_hash", NOT_COMPUTABLE)),
            "phase_execution_receipt": str(phase_receipt.get("receipt_hash", NOT_COMPUTABLE)),
            "repair_spec_plan": str(
                request.get("source_spec_plan", {}).get("source_spec_plan_hash", NOT_COMPUTABLE)
            ),
        },
    }
    return {**packet, "decision_record_plan_hash": canonical_hash(packet)}


def render_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Research Canary Artifact Registry Coverage Repair Operator Decision Record Plan 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `target_surface`: `{packet['target_surface']}`",
        f"- `recommended_default_decision`: `{packet['recommended_default_decision']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        "",
        "## Decision Options",
    ]
    for option in packet.get("decision_options", []):
        lines.append(f"- `{option}`")
    lines.extend(["", "## Required Review Artifacts"])
    for item in packet.get("required_review_artifacts", []):
        lines.append(f"- `{item}`")
    return lines


def write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan(root)
    write_canonical_json(target_root / PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / PLAN_MD_PATH,
        render_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan_markdown(packet),
    )
    return packet
