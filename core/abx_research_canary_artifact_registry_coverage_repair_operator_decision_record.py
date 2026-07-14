from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "AbxResearchCanaryArtifactRegistryCoverageRepairOperatorDecisionRecord.v1"
RECORD_ID = "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_RECORD_001"
PLAN_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan_001.latest.json"
)
EXECUTION_SPEC_PLAN_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan_001.latest.json"
)
RECORD_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_001.latest.json"
)
RECORD_MD_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_001.latest.md"
)
EXECUTION_SPEC_PLAN_LANE = "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_EXECUTION_SPEC_PLAN_001"
AUTHORIZED_DECISION = "AUTHORIZE_REGISTRY_REPAIR_EXECUTION_SPEC"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _read_optional_json(path: Path) -> dict[str, Any]:
    return _read_json(path)


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    plan = _read_json(root / PLAN_JSON_PATH)
    execution_spec = _read_optional_json(root / EXECUTION_SPEC_PLAN_JSON_PATH)

    plan_ready = (
        plan.get("schema_version") == "AbxResearchCanaryArtifactRegistryCoverageRepairOperatorDecisionRecordPlan.v1"
        and plan.get("status") == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_RECORD_PLAN_READY"
        and plan.get("execution_authority") is False
        and plan.get("implementation_authorized") is False
    )
    execution_spec_observed = (
        execution_spec.get("schema_version")
        == "AbxResearchCanaryArtifactRegistryCoverageRepairExecutionSpecPlan.v1"
        and execution_spec.get("status") == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_EXECUTION_SPEC_PLAN_READY"
        and execution_spec.get("execution_allowed") is False
        and execution_spec.get("valid_for_repair") is False
    )
    consumed_by_execution_spec = plan_ready and execution_spec_observed

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": RECORD_ID,
        "status": (
            "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_RECORD_CONSUMED_BY_EXECUTION_SPEC"
            if consumed_by_execution_spec
            else "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_RECORD_APPROVED_FOR_EXECUTION_SPEC"
            if plan_ready
            else "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_RECORD_BLOCKED"
        ),
        "decision_record_id": RECORD_ID,
        "command": "BUILD_ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_RECORD_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "decision_scope": str(plan.get("decision_scope", NOT_COMPUTABLE)),
        "selected_decision": AUTHORIZED_DECISION if plan_ready else NOT_COMPUTABLE,
        "decision_outcome_summary": (
            "Registry repair execution spec authoring is approved for P103-P130 canonical lanes. "
            "No direct registry mutation, P130 activation, orphan inclusion, or execution authority is authorized."
        ),
        "decision_rationale": (
            "Operator authorized research-canary registry coverage repair at the spec-authoring boundary "
            "after all five repair-spec phases completed and governance boundaries were preserved."
        ),
        "operator_id": "thread_operator",
        "operator_name": "appliedalchemylabs",
        "operator_role": "governed_operator",
        "operator_instruction_observed": "AUTHORIZE_REGISTRY_REPAIR_EXECUTION_SPEC",
        "decision_timestamp_utc": "2026-06-17T00:00:00Z",
        "decision_scope_acknowledged": True,
        "registry_repair_execution_spec_required": True,
        "advisory_only_acknowledged": True,
        "non_authoritative_acknowledged": True,
        "execution_authority_denied_acknowledged": True,
        "p130_advisory_hold_preservation_acknowledged": True,
        "orphan_exclusion_policy_acknowledged": True,
        "runtime_mutation_denied_acknowledged": True,
        "canon_mutation_denied_acknowledged": True,
        "queue_mutation_denied_acknowledged": True,
        "implementation_authorized": False,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "registry_mutation_allowed": False,
        "repair_execution_performed": False,
        "registry_mutation_performed": False,
        "approval_granted": True,
        "registry_repair_execution_spec_authoring_approved": plan_ready,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_planning_pr": not consumed_by_execution_spec and plan_ready,
        "operator_input_required": False,
        "execution_spec_observed": consumed_by_execution_spec,
        "execution_spec": {
            "path": str(EXECUTION_SPEC_PLAN_JSON_PATH),
            "hash": str(execution_spec.get("spec_plan_hash", NOT_COMPUTABLE)),
            "status": str(execution_spec.get("status", NOT_COMPUTABLE)),
            "observed": consumed_by_execution_spec,
        },
        "recommended_next_action": (
            "registry repair execution spec has been observed; do not prepare another planning PR from this record"
            if consumed_by_execution_spec
            else "author the governed registry repair execution specification before any P103-P130 registry mutation"
        ),
        "recommended_next_lane": NOT_COMPUTABLE if consumed_by_execution_spec else EXECUTION_SPEC_PLAN_LANE,
        "allowed_follow_on_actions": [
            *([] if consumed_by_execution_spec else ["AUTHOR_REGISTRY_REPAIR_EXECUTION_SPEC"]),
            "MAINTAIN_EXECUTION_DENIAL",
            "MAINTAIN_P130_ADVISORY_HOLD",
            "MAINTAIN_ORPHAN_EXCLUSION",
        ],
        "blocked_actions": list(plan.get("disallowed_follow_on_actions", [])),
        "unresolved_hold_reasons": [
            "SCOPE_PREFIX_VS_DERIVED_OPTIONAL_POLICY_UNRESOLVED",
            "ORPHAN_RESEARCH_OUTPUT_POLICY_OPERATOR_HELD",
            "DIRECT_REGISTRY_REPAIR_EXECUTION_AUTHORITY_REMAINS_DENIED",
        ],
        "reviewed_request_id": str(plan.get("source_request_id", NOT_COMPUTABLE)),
        "reviewed_request_hash": str(plan.get("source_hashes", {}).get("operator_decision_request", NOT_COMPUTABLE)),
        "reviewed_phase_receipt_hash": str(
            plan.get("source_hashes", {}).get("phase_execution_receipt", NOT_COMPUTABLE)
        ),
        "source_plan_path": str(PLAN_JSON_PATH),
        "source_plan_hash": str(plan.get("decision_record_plan_hash", NOT_COMPUTABLE)),
    }
    return {**packet, "decision_record_hash": canonical_hash(packet)}


def render_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Research Canary Artifact Registry Coverage Repair Operator Decision Record 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `selected_decision`: `{packet['selected_decision']}`",
        f"- `registry_repair_execution_spec_authoring_approved`: `{packet['registry_repair_execution_spec_authoring_approved']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        f"- `registry_mutation_performed`: `{packet['registry_mutation_performed']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        "",
        "## Decision Boundary",
        "",
        str(packet["decision_outcome_summary"]),
        "",
        "## Unresolved Hold Reasons",
    ]
    for item in packet.get("unresolved_hold_reasons", []):
        lines.append(f"- `{item}`")
    return lines


def write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record(root)
    write_canonical_json(target_root / RECORD_JSON_PATH, packet)
    _write_markdown(
        target_root / RECORD_MD_PATH,
        render_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_markdown(packet),
    )
    return packet
