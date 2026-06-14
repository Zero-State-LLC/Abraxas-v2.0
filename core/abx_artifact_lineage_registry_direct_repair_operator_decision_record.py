from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxArtifactLineageRegistryDirectRepairOperatorDecisionRecord.v1"
PLAN_JSON_PATH = Path("out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan_001.latest.json")
RECORD_JSON_PATH = Path("out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_001.latest.json")
RECORD_MD_PATH = Path("out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_001.latest.md")
SEPARATE_EXECUTION_SPEC_PLAN_JSON_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan_001.latest.json"
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_optional_json(path: Path) -> dict[str, Any]:
    try:
        return _read_json(path)
    except (OSError, json.JSONDecodeError):
        return {}


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_abx_artifact_lineage_registry_direct_repair_operator_decision_record(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    plan = _read_json(root / PLAN_JSON_PATH)
    plan_ready = (
        plan.get("schema_version") == "AbxArtifactLineageRegistryDirectRepairOperatorDecisionRecordPlan.v1"
        and plan.get("status") == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_PLAN_READY"
        and plan.get("recommended_default_decision") == "HOLD"
        and plan.get("execution_authority") is False
        and plan.get("implementation_authorized") is False
        and plan.get("safe_to_auto_continue") is False
    )
    separate_spec = _read_optional_json(root / SEPARATE_EXECUTION_SPEC_PLAN_JSON_PATH)
    separate_spec_observed = (
        separate_spec.get("schema_version")
        == "AbxArtifactLineageRegistryDirectRepairSeparateExecutionSpecPlan.v1"
        and separate_spec.get("status")
        == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SEPARATE_EXECUTION_SPEC_PLAN_READY"
        and separate_spec.get("safe_to_prepare_planning_pr") is False
        and separate_spec.get("execution_allowed") is False
        and separate_spec.get("valid_for_execution") is False
        and separate_spec.get("valid_for_repair") is False
    )
    consumed_by_separate_spec = plan_ready and separate_spec_observed

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_CONSUMED_BY_SEPARATE_EXECUTION_SPEC"
            if consumed_by_separate_spec
            else "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_APPROVED_FOR_SEPARATE_EXECUTION_SPEC"
            if plan_ready
            else "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_BLOCKED"
        ),
        "decision_record_id": "abx_artifact_lineage_registry_direct_repair_operator_decision_record_001",
        "decision_record_hash": "",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "decision_scope": str(plan.get("decision_scope", "DIRECT_REPAIR_EXECUTION_DECISION_REQUIRED")),
        "selected_decision": "AUTHORIZE_SEPARATE_DIRECT_REPAIR_EXECUTION_SPEC" if plan_ready else "NOT_COMPUTABLE",
        "decision_outcome_summary": (
            "Separate direct-repair execution spec authoring is approved. No repo-local repair mutation, runner "
            "casing policy change, Notion completeness claim, or execution authority is authorized."
        ),
        "decision_rationale": (
            "Operator approved Artifact Lineage continuation at the spec-authoring boundary while preserving "
            "all repair execution, runner casing, and Notion evidence holds."
        ),
        "operator_id": "thread_operator",
        "operator_name": "appliedalchemylabs",
        "operator_role": "governed_operator",
        "operator_instruction_observed": "approve artifact lineage",
        "decision_timestamp_utc": "2026-06-11T00:00:00Z",
        "decision_scope_acknowledged": True,
        "separate_execution_spec_required": True,
        "advisory_only_acknowledged": True,
        "non_authoritative_acknowledged": True,
        "execution_authority_denied_acknowledged": True,
        "runtime_mutation_denied_acknowledged": True,
        "canon_mutation_denied_acknowledged": True,
        "queue_mutation_denied_acknowledged": True,
        "implementation_authorized": False,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "promotion_allowed": False,
        "approval_granted": True,
        "separate_execution_spec_authoring_approved": True,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_planning_pr": not consumed_by_separate_spec and plan_ready,
        "operator_input_required": False,
        "completion_hold_active": False,
        "repair_completion_recognized": consumed_by_separate_spec,
        "separate_execution_spec_observed": consumed_by_separate_spec,
        "separate_execution_spec": {
            "path": str(SEPARATE_EXECUTION_SPEC_PLAN_JSON_PATH),
            "hash": str(separate_spec.get("spec_plan_hash", "NOT_COMPUTABLE")),
            "status": str(separate_spec.get("status", "NOT_COMPUTABLE")),
            "observed": consumed_by_separate_spec,
        },
        "recommended_next_action": (
            "separate direct-repair execution spec has been observed; do not prepare another planning PR from this decision record"
            if consumed_by_separate_spec
            else "author a separate governed direct-repair execution specification before any repo-local repair mutation"
        ),
        "recommended_next_patch": (
            "NOT_COMPUTABLE"
            if consumed_by_separate_spec
            else "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SEPARATE_EXECUTION_SPEC_PLAN"
        ),
        "allowed_follow_on_actions": [
            *([] if consumed_by_separate_spec else ["AUTHOR_SEPARATE_DIRECT_REPAIR_EXECUTION_SPEC"]),
            "MAINTAIN_EXECUTION_DENIAL",
        ],
        "blocked_actions": list(plan.get("disallowed_follow_on_actions", [])),
        "unresolved_hold_reasons": [
            "RUNNER_CASING_POLICY_REMAINS_OPERATOR_HELD",
            "NOTION_MAPPING_EVIDENCE_REMAINS_NOT_COMPUTABLE",
            "DIRECT_REPAIR_EXECUTION_AUTHORITY_REMAINS_DENIED",
        ],
        "reviewed_request_id": str(plan.get("source_request_id", "NOT_COMPUTABLE")),
        "reviewed_request_hash": str(
            plan.get("source_hashes", {}).get(
                "abx_artifact_lineage_registry_direct_repair_operator_decision_record_operator_decision_request",
                "NOT_COMPUTABLE",
            )
        ),
        "reviewed_completion_hold_plan_hash": str(
            plan.get("source_hashes", {}).get("operator_decision_record_completion_hold_plan", "NOT_COMPUTABLE")
        ),
        "reviewed_external_hold_reasons": [
            "RUNNER_CASING_POLICY_REMAINS_OPERATOR_HELD",
            "NOTION_MAPPING_EVIDENCE_REMAINS_NOT_COMPUTABLE",
        ],
        "source_plan_path": str(PLAN_JSON_PATH),
        "source_plan_hash": str(plan.get("decision_record_plan_hash", "NOT_COMPUTABLE")),
        "source_hashes": {
            "abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan": str(
                plan.get("decision_record_plan_hash", "NOT_COMPUTABLE")
            ),
            **{str(key): str(value) for key, value in dict(plan.get("source_hashes", {})).items()},
        },
    }
    packet["decision_record_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "decision_record_hash"}
    )
    return packet


def render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Artifact Lineage Registry Direct Repair Operator Decision Record",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `selected_decision`: `{packet['selected_decision']}`",
        f"- `decision_scope`: `{packet['decision_scope']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        f"- `valid_for_repair`: `{packet['valid_for_repair']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Decision Boundary",
        "",
        str(packet["decision_outcome_summary"]),
        "",
        "## Unresolved Hold Reasons",
        "",
    ]
    for item in packet["unresolved_hold_reasons"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Blocked Actions", ""])
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    return lines


def write_abx_artifact_lineage_registry_direct_repair_operator_decision_record(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record(root)
    write_canonical_json(target_root / RECORD_JSON_PATH, packet)
    _write_markdown(
        target_root / RECORD_MD_PATH,
        render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_markdown(packet),
    )
    return packet
