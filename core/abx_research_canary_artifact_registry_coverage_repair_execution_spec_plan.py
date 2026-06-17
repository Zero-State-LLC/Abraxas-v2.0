from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxResearchCanaryArtifactRegistryCoverageRepairExecutionSpecPlan.v1"
SPEC_PLAN_ID = "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_EXECUTION_SPEC_PLAN_001"
DECISION_RECORD_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_001.latest.json"
)
AUDIT_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_001.latest.json"
)
SPEC_PLAN_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan_001.latest.json"
)
SPEC_PLAN_MD_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan_001.latest.md"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"
AUTHORIZATION_GATE_LANE = (
    "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_EXECUTION_AUTHORIZATION_GATE_001"
)

BLOCKED_ACTIONS = [
    "DIRECT_REGISTRY_REPAIR_EXECUTION",
    "RESEARCH_CANARY_SPINE_REFRESH",
    "RESEARCH_CANARY_ARTIFACT_REGENERATION",
    "P130_ACTIVATION",
    "ORPHAN_OUTPUT_REGISTRY_INCLUSION",
    "SCOPE_PREFIX_MUTATION_WITHOUT_OPERATOR_DECISION",
    "RUNTIME_MUTATION",
    "CANON_MUTATION",
    "QUEUE_MUTATION",
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _proposed_repair_steps(audit: Mapping[str, Any]) -> list[dict[str, Any]]:
    lane_records = [record for record in audit.get("lane_records", []) if isinstance(record, dict)]
    output_gaps = sorted(
        str(record["output_json_path"])
        for record in lane_records
        if not record.get("output_json_in_registry_entries")
        and record.get("output_json_path") not in {None, NOT_COMPUTABLE}
    )
    lane_id_gaps = sorted(
        str(record["lane_id"])
        for record in lane_records
        if not record.get("lane_id_in_registry_source")
    )
    return [
        {
            "step_id": "REGISTRY_REPAIR_STEP_001",
            "step_name": "add_derived_optional_entries_for_canonical_output_paths",
            "execution_allowed": False,
            "repair_execution_performed": False,
            "target_surface": "core/generated_artifact_registry.py _DERIVED_OPTIONAL_ARTIFACTS",
            "impacted_path_count": len(output_gaps),
            "sample_paths": output_gaps[:5],
            "policy": "DERIVED_OPTIONAL_PER_PATH",
        },
        {
            "step_id": "REGISTRY_REPAIR_STEP_002",
            "step_name": "add_lane_id_traceability_metadata_block",
            "execution_allowed": False,
            "repair_execution_performed": False,
            "target_surface": "core/generated_artifact_registry.py source metadata",
            "impacted_lane_id_count": len(lane_id_gaps),
            "sample_lane_ids": lane_id_gaps[:5],
            "policy": "LANE_ID_VISIBILITY_COMMENTS_OR_METADATA",
        },
        {
            "step_id": "REGISTRY_REPAIR_STEP_003",
            "step_name": "preserve_p130_advisory_hold_and_orphan_exclusion",
            "execution_allowed": False,
            "repair_execution_performed": False,
            "target_surface": "governance boundaries",
            "policy": "EXCLUDE_ORPHANS_AND_PRESERVE_P130_HOLD",
        },
        {
            "step_id": "REGISTRY_REPAIR_STEP_004",
            "step_name": "future_execution_authorization_gate",
            "execution_allowed": False,
            "repair_execution_performed": False,
            "target_surface": "operator authorization before registry mutation PR",
            "policy": "REQUIRE_SEPARATE_EXECUTION_AUTHORIZATION_RECORD",
        },
    ]


def build_abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    decision = _read_json(root / DECISION_RECORD_JSON_PATH)
    audit = _read_json(root / AUDIT_JSON_PATH)

    source_authorized = (
        decision.get("schema_version") == "AbxResearchCanaryArtifactRegistryCoverageRepairOperatorDecisionRecord.v1"
        and decision.get("selected_decision") == "AUTHORIZE_REGISTRY_REPAIR_EXECUTION_SPEC"
        and decision.get("registry_repair_execution_spec_authoring_approved") is True
        and decision.get("implementation_authorized") is False
        and decision.get("execution_authority") is False
        and decision.get("valid_for_repair") is False
        and decision.get("registry_mutation_performed") is False
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": SPEC_PLAN_ID,
        "status": "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_EXECUTION_SPEC_PLAN_READY"
        if source_authorized
        else "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_EXECUTION_SPEC_PLAN_BLOCKED",
        "spec_plan_id": SPEC_PLAN_ID,
        "command": "BUILD_ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_EXECUTION_SPEC_PLAN_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "source_authorization": {
            "source_decision_record_path": str(DECISION_RECORD_JSON_PATH),
            "source_decision_record_hash": str(decision.get("decision_record_hash", NOT_COMPUTABLE)),
            "source_status": str(decision.get("status", NOT_COMPUTABLE)),
            "selected_decision": str(decision.get("selected_decision", NOT_COMPUTABLE)),
            "spec_authoring_approved": source_authorized,
        },
        "authorization_scope": "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_EXECUTION_SPEC_AUTHORING_ONLY",
        "execution_allowed": False,
        "repair_execution_performed": False,
        "registry_mutation_performed": False,
        "implementation_authorized": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_planning_pr": False,
        "proposed_repair_steps": _proposed_repair_steps(audit) if source_authorized else [],
        "validation_gates": [
            {
                "gate_id": "source_authorization_scope_gate",
                "required_decision": "AUTHORIZE_REGISTRY_REPAIR_EXECUTION_SPEC",
                "passed": source_authorized,
            },
            {
                "gate_id": "no_repair_execution_gate",
                "required_value": False,
                "observed_value": False,
                "passed": True,
            },
            {
                "gate_id": "p130_hold_preserved_gate",
                "required_value": True,
                "passed": True,
            },
            {
                "gate_id": "orphan_exclusion_preserved_gate",
                "required_value": True,
                "passed": True,
            },
        ],
        "blocked_actions": list(BLOCKED_ACTIONS),
        "blocked_delivery_surfaces": [
            "scripts/run_research_canary_artifact_spine_refresh.py",
            "out/research_canary_*/latest.json regeneration targets",
            "P130 hold and activation surfaces",
            "orphan research output registry inclusion",
        ],
        "downstream_status": "READY_FOR_EXECUTION_AUTHORIZATION_GATE" if source_authorized else NOT_COMPUTABLE,
        "recommended_next_lane": AUTHORIZATION_GATE_LANE if source_authorized else NOT_COMPUTABLE,
        "recommended_next_action": (
            "emit execution authorization gate and collect explicit operator authorization before any "
            "P103-P130 registry mutation PR"
            if source_authorized
            else "repair operator decision record authorization prerequisites"
        ),
        "provenance": {
            "source_decision_record_path": str(DECISION_RECORD_JSON_PATH),
            "source_decision_record_hash": str(decision.get("decision_record_hash", NOT_COMPUTABLE)),
            "source_audit_path": str(AUDIT_JSON_PATH),
            "source_audit_hash": canonical_hash(audit) if audit else NOT_COMPUTABLE,
        },
    }
    return {**packet, "spec_plan_hash": canonical_hash(packet)}


def render_abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Research Canary Artifact Registry Coverage Repair Execution Spec Plan 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `authorization_scope`: `{packet['authorization_scope']}`",
        f"- `execution_allowed`: `{packet['execution_allowed']}`",
        f"- `registry_mutation_performed`: `{packet['registry_mutation_performed']}`",
        "",
        "## Proposed Repair Steps",
    ]
    for step in packet.get("proposed_repair_steps", []):
        if isinstance(step, dict):
            lines.append(f"- `{step['step_id']}`: `{step['step_name']}` ({step.get('policy', NOT_COMPUTABLE)})")
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- `{action}`")
    return lines


def write_abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan(root)
    write_canonical_json(target_root / SPEC_PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / SPEC_PLAN_MD_PATH,
        render_abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan_markdown(packet),
    )
    return packet
