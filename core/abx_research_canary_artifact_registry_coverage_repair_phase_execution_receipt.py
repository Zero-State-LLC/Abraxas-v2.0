from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_research_canary_artifact_registry_coverage_audit import AUDIT_ID
from core.abx_research_canary_artifact_registry_coverage_repair_spec_plan import (
    BLOCKED_ACTIONS as SPEC_PLAN_BLOCKED_ACTIONS,
    PROPOSED_PHASES,
    SPEC_PLAN_ID,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxResearchCanaryArtifactRegistryCoverageRepairPhaseExecutionReceipt.v1"
RECEIPT_ID = "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_PHASE_EXECUTION_RECEIPT_001"
SOURCE_SPEC_PLAN_PATH = (
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_spec_plan_001.latest.json"
)
SOURCE_AUDIT_PATH = "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_001.latest.json"
SOURCE_DECISION_REQUEST_PATH = (
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_operator_decision_request_001.latest.json"
)
OUT_JSON = (
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt_001.latest.json"
)
OUT_MD = (
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt_001.latest.md"
)
OPERATOR_DECISION_RECORD_PLAN_LANE = (
    "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_RECORD_PLAN_001"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"
SAMPLE_CAP = 5


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _sample(items: list[str]) -> list[str]:
    return sorted(items)[:SAMPLE_CAP]


def _validate_spec_plan(spec_plan: Mapping[str, Any]) -> bool:
    return (
        spec_plan.get("schema_version") == "AbxResearchCanaryArtifactRegistryCoverageRepairSpecPlan.v1"
        and spec_plan.get("spec_plan_id") == SPEC_PLAN_ID
        and spec_plan.get("spec_plan_status") == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_SPEC_PLAN_READY"
        and spec_plan.get("registry_mutation_performed") is False
    )


def _validate_decision_request(decision_request: Mapping[str, Any]) -> bool:
    return (
        decision_request.get("schema_version")
        == "AbxResearchCanaryArtifactRegistryCoverageRepairOperatorDecisionRequest.v1"
        and decision_request.get("request_id")
        == "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_REQUEST_001"
        and decision_request.get("status")
        == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_REQUEST_EMITTED"
        and decision_request.get("registry_mutation_performed") is False
    )


def _phase_results(audit: Mapping[str, Any]) -> list[dict[str, Any]]:
    lane_records = [record for record in audit.get("lane_records", []) if isinstance(record, dict)]
    orphan_outputs = [
        record for record in audit.get("orphan_research_outputs", []) if isinstance(record, dict)
    ]

    output_path_gaps = sorted(
        str(record["output_json_path"])
        for record in lane_records
        if not record.get("output_json_in_registry_entries")
        and record.get("output_json_path") not in {None, NOT_COMPUTABLE}
    )
    all_output_paths = sorted(
        {
            str(record["output_json_path"])
            for record in lane_records
            if record.get("output_json_path") not in {None, NOT_COMPUTABLE}
        }
    )
    lane_id_gaps = sorted(
        str(record["lane_id"])
        for record in lane_records
        if not record.get("lane_id_in_registry_source")
    )
    partial_scope_prefix_lanes = sorted(
        str(record["lane_id"])
        for record in lane_records
        if record.get("output_json_in_registry_entries") is True
    )
    orphan_paths = sorted(
        {
            str(record["output_json_path"])
            for record in orphan_outputs
            if record.get("output_json_path") not in {None, NOT_COMPUTABLE}
        }
    )

    classified_output_paths = [
        {
            "output_json_path": path,
            "classification": "REPO_LOCAL_DIRECT_REPAIR_CANDIDATE",
            "in_registry_entries": path not in output_path_gaps,
        }
        for path in all_output_paths
    ]
    classified_lane_ids = [
        {
            "lane_id": lane_id,
            "classification": "LANE_ID_TRACEABILITY_METADATA_CANDIDATE",
            "in_registry_source": False,
        }
        for lane_id in lane_id_gaps
    ]
    orphan_classifications = [
        {
            "output_json_path": path,
            "classification": "EXCLUDED_FROM_CANONICAL_P103_P130_REPAIR",
            "lane_id_observed": str(
                next(
                    (
                        record.get("lane_id_observed", NOT_COMPUTABLE)
                        for record in orphan_outputs
                        if record.get("output_json_path") == path
                    ),
                    NOT_COMPUTABLE,
                )
            ),
        }
        for path in orphan_paths
    ]

    return [
        {
            "phase_id": "REPAIR_SPEC_PHASE_001",
            "phase_name": "classify_canonical_lane_output_path_gaps",
            "phase_status": "CLASSIFICATION_COMPLETE",
            "execution_allowed": False,
            "repair_execution_performed": False,
            "classified_count": len(all_output_paths),
            "gap_count": len(output_path_gaps),
            "classification_summary": "REPO_LOCAL_DIRECT_REPAIR_CANDIDATE",
            "sample_classified": _sample(output_path_gaps),
            "classified_items": classified_output_paths,
            "source_batch_id": "CANONICAL_LANE_OUTPUT_PATH_REGISTRY_BATCH",
        },
        {
            "phase_id": "REPAIR_SPEC_PHASE_002",
            "phase_name": "classify_lane_id_traceability_gaps",
            "phase_status": "CLASSIFICATION_COMPLETE",
            "execution_allowed": False,
            "repair_execution_performed": False,
            "classified_count": len(lane_id_gaps),
            "gap_count": len(lane_id_gaps),
            "classification_summary": "LANE_ID_TRACEABILITY_METADATA_CANDIDATE",
            "sample_classified": _sample(lane_id_gaps),
            "classified_items": classified_lane_ids,
            "source_batch_id": "LANE_ID_TRACEABILITY_METADATA_BATCH",
        },
        {
            "phase_id": "REPAIR_SPEC_PHASE_003",
            "phase_name": "resolve_scope_prefix_vs_derived_optional_policy",
            "phase_status": "OPERATOR_REVIEW_REQUIRED",
            "execution_allowed": False,
            "repair_execution_performed": False,
            "classified_count": len(partial_scope_prefix_lanes) + len(output_path_gaps),
            "gap_count": len(output_path_gaps),
            "classification_summary": "SCOPE_PREFIX_VS_DERIVED_OPTIONAL_UNRESOLVED",
            "policy_options": [
                "DERIVED_OPTIONAL_PER_PATH",
                "BULK_SCOPE_PREFIX_OUT_RESEARCH",
                "BULK_SCOPE_PREFIX_OUT_RESEARCH_CANARY",
            ],
            "partial_scope_prefix_lane_ids": partial_scope_prefix_lanes,
            "sample_classified": _sample(output_path_gaps),
            "source_batch_id": "PARTIAL_SCOPE_PREFIX_NORMALIZATION_BATCH",
        },
        {
            "phase_id": "REPAIR_SPEC_PHASE_004",
            "phase_name": "orphan_output_exclusion_policy",
            "phase_status": "EXCLUSION_POLICY_EMITTED",
            "execution_allowed": False,
            "repair_execution_performed": False,
            "classified_count": len(orphan_paths),
            "gap_count": len(orphan_paths),
            "classification_summary": "EXCLUDED_FROM_CANONICAL_P103_P130_REPAIR",
            "sample_classified": _sample(orphan_paths),
            "classified_items": orphan_classifications,
            "source_batch_id": "ORPHAN_RESEARCH_OUTPUT_POLICY_BATCH",
        },
        {
            "phase_id": "REPAIR_SPEC_PHASE_005",
            "phase_name": "future_operator_authorization_gate_before_registry_mutation",
            "phase_status": "GATE_EMITTED",
            "execution_allowed": False,
            "repair_execution_performed": False,
            "classified_count": 1,
            "gap_count": 1,
            "classification_summary": "PENDING_OPERATOR_DECISION",
            "authorization_granted": False,
            "operator_decision_request_lane": (
                "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_REQUEST_001"
            ),
            "required_before_registry_mutation": True,
            "source_batch_id": "P130_ADVISORY_HOLD_PRESERVATION_BATCH",
        },
    ]


def build_abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    spec_plan = _read_json(root / SOURCE_SPEC_PLAN_PATH)
    audit = _read_json(root / SOURCE_AUDIT_PATH)
    decision_request = _read_json(root / SOURCE_DECISION_REQUEST_PATH)

    spec_plan_ready = _validate_spec_plan(spec_plan)
    audit_ready = (
        audit.get("audit_id") == AUDIT_ID
        and audit.get("audit_status") == "RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_GAP_CONFIRMED"
        and audit.get("registry_mutation_performed") is False
    )
    decision_request_ready = _validate_decision_request(decision_request)
    source_ready = spec_plan_ready and audit_ready and decision_request_ready

    phase_results = _phase_results(audit) if source_ready else []
    phases_complete = len(phase_results) == len(PROPOSED_PHASES) and all(
        phase["phase_status"]
        in {
            "CLASSIFICATION_COMPLETE",
            "OPERATOR_REVIEW_REQUIRED",
            "EXCLUSION_POLICY_EMITTED",
            "GATE_EMITTED",
        }
        for phase in phase_results
    )

    if source_ready and phases_complete:
        receipt_status = "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_PHASE_EXECUTION_RECEIPT_EMITTED"
        recommended_next_lane = OPERATOR_DECISION_RECORD_PLAN_LANE
        downstream_status = "READY_FOR_OPERATOR_DECISION_RECORD_PLAN"
    else:
        receipt_status = "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_PHASE_EXECUTION_RECEIPT_BLOCKED"
        recommended_next_lane = NOT_COMPUTABLE
        downstream_status = NOT_COMPUTABLE

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": RECEIPT_ID,
        "receipt_id": RECEIPT_ID,
        "receipt_status": receipt_status,
        "command": "BUILD_ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_PHASE_EXECUTION_RECEIPT_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "evidence_only": True,
        "source_spec_plan": {
            "source_spec_plan_path": SOURCE_SPEC_PLAN_PATH,
            "source_spec_plan_hash": str(spec_plan.get("spec_plan_hash", NOT_COMPUTABLE)),
            "source_spec_plan_status": str(spec_plan.get("spec_plan_status", NOT_COMPUTABLE)),
            "source_spec_plan_observed": spec_plan_ready,
        },
        "source_audit": {
            "source_audit_path": SOURCE_AUDIT_PATH,
            "source_audit_id": audit.get("audit_id", NOT_COMPUTABLE),
            "source_audit_status": audit.get("audit_status", NOT_COMPUTABLE),
            "source_audit_hash": canonical_hash(audit) if audit else NOT_COMPUTABLE,
            "source_audit_observed": audit_ready,
        },
        "source_decision_request": {
            "source_decision_request_path": SOURCE_DECISION_REQUEST_PATH,
            "source_decision_request_hash": str(decision_request.get("request_hash", NOT_COMPUTABLE)),
            "source_decision_request_status": str(decision_request.get("status", NOT_COMPUTABLE)),
            "source_decision_request_observed": decision_request_ready,
        },
        "phase_results": phase_results,
        "phases_complete": phases_complete,
        "phase_count": len(phase_results),
        "expected_phase_count": len(PROPOSED_PHASES),
        "governance_boundaries": {
            "p102g_temporal_continuity_spine_edge_preserved": True,
            "p130_advisory_frontier_only": True,
            "research_canary_not_promoted_to_temporal_continuity": True,
            "registry_repair_performed": False,
            "research_canary_spine_refresh_performed": False,
        },
        "blocked_actions": [
            *SPEC_PLAN_BLOCKED_ACTIONS,
            "DIRECT_REGISTRY_COVERAGE_REPAIR_EXECUTION",
            "AUTO_APPROVE_REGISTRY_REPAIR",
        ],
        "execution_allowed": False,
        "repair_execution_performed": False,
        "registry_mutation_performed": False,
        "implementation_authorized": False,
        "authorization_granted": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_planning_pr": False,
        "recommended_next_action": (
            "consume all five phase classifications as advisory evidence; require explicit operator "
            "decision record before any P103-P130 registry repair execution"
            if phases_complete
            else "repair upstream spec plan, audit, and operator decision request prerequisites"
        ),
        "recommended_next_lane": recommended_next_lane,
        "downstream_status": downstream_status,
        "downstream": downstream_status,
    }
    return {**packet, "receipt_hash": canonical_hash(packet)}


def render_abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Research Canary Artifact Registry Coverage Repair Phase Execution Receipt 001",
        "",
        f"- `receipt_id`: `{packet['receipt_id']}`",
        f"- `receipt_status`: `{packet['receipt_status']}`",
        f"- `phases_complete`: `{packet['phases_complete']}`",
        f"- `phase_count`: `{packet['phase_count']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        f"- `registry_mutation_performed`: `{packet['registry_mutation_performed']}`",
        "",
        "## Phase Results",
    ]
    for phase in packet.get("phase_results", []):
        if isinstance(phase, dict):
            lines.append(
                f"- `{phase['phase_id']}`: `{phase['phase_status']}` "
                f"({phase.get('classified_count', 0)} classified, "
                f"summary=`{phase.get('classification_summary', NOT_COMPUTABLE)}`)"
            )
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- `{action}`")
    return lines


def write_abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt(root)
    write_canonical_json(target_root / OUT_JSON, packet)
    (target_root / OUT_MD).parent.mkdir(parents=True, exist_ok=True)
    (target_root / OUT_MD).write_text(
        "\n".join(
            render_abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt_markdown(packet)
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
