from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxArtifactLineageRegistryDirectRepairOperatorDecisionRecord.v1"
PLAN_JSON_PATH = Path("out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan_001.latest.json")
RECORD_JSON_PATH = Path("out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_001.latest.json")
RECORD_MD_PATH = Path("out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_001.latest.md")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_HELD"
        if plan_ready
        else "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_BLOCKED",
        "decision_record_id": "abx_artifact_lineage_registry_direct_repair_operator_decision_record_001",
        "decision_record_hash": "",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "decision_scope": str(plan.get("decision_scope", "DIRECT_REPAIR_EXECUTION_DECISION_REQUIRED")),
        "selected_decision": "HOLD" if plan_ready else "NOT_COMPUTABLE",
        "decision_outcome_summary": (
            "Direct repair remains held. No separate execution spec, repo-local repair mutation, runner casing "
            "policy change, or Notion completeness claim is authorized."
        ),
        "decision_rationale": (
            "Backlog continuation follows the plan default because final repair authority, runner casing policy, "
            "and Notion mapping evidence remain unresolved."
        ),
        "operator_id": "thread_operator",
        "operator_name": "appliedalchemylabs",
        "operator_role": "governed_operator",
        "operator_instruction_observed": "continue with backlog",
        "decision_timestamp_utc": "2026-06-11T00:00:00Z",
        "decision_scope_acknowledged": True,
        "separate_execution_spec_required": False,
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
        "valid_for_execution": False,
        "valid_for_repair": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_planning_pr": False,
        "operator_input_required": False,
        "completion_hold_active": True,
        "repair_completion_recognized": False,
        "recommended_next_action": (
            "maintain the direct-repair completion hold and continue backlog triage only from separately governed "
            "operator-decision evidence"
        ),
        "recommended_next_patch": "NOT_COMPUTABLE",
        "allowed_follow_on_actions": [
            "MAINTAIN_DIRECT_REPAIR_COMPLETION_HOLD",
            "MAINTAIN_EXECUTION_DENIAL",
            "CONTINUE_BACKLOG_TRIAGE",
        ],
        "blocked_actions": list(plan.get("disallowed_follow_on_actions", [])),
        "unresolved_hold_reasons": [
            "FINAL_OPERATOR_DECISION_RECORD_MISSING_BEFORE_THIS_RECORD",
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
