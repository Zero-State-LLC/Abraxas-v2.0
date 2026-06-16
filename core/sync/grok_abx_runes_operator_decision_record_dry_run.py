from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.grok_abx_runes_operator_decision_record_plan import (
    PLAN_JSON_PATH as SOURCE_PLAN_JSON_PATH,
)

SCHEMA_VERSION = "GrokAbxRunesOperatorDecisionRecordDryRun.v1"
DRY_RUN_ID = "grok_abx_runes_operator_decision_record_dry_run_001"
DRY_RUN_JSON_PATH = Path(
    "out/operator_review/grok_abx_runes_operator_decision_record_dry_run_001.latest.json"
)
DRY_RUN_MD_PATH = DRY_RUN_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = "GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_PLAN_READY"
NOT_COMPUTABLE = "NOT_COMPUTABLE"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _authority_locks() -> dict[str, bool]:
    return {
        "authorization_record_creation": False,
        "auto_approval": False,
        "auto_continuation": False,
        "backlog_acceptance_auto_apply": False,
        "canon_mutation": False,
        "catalog_mutation": False,
        "code_creation": False,
        "decision_record_creation": False,
        "execution_authority": False,
        "github_writeback": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "pr_merge_authority": False,
        "projection_surface_mutation": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "yggdrasil_binding_mutation": False,
    }


def _field_groups(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    groups = plan.get("required_field_groups", [])
    return [dict(group) for group in groups if isinstance(group, Mapping)]


def _field_names(groups: list[dict[str, Any]]) -> list[str]:
    fields: list[str] = []
    for group in groups:
        fields.extend(_string_list(group.get("fields")))
    return fields


def build_grok_abx_runes_operator_decision_record_dry_run(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    plan = _read_json(root / SOURCE_PLAN_JSON_PATH)
    plan_observed = plan is not None
    plan = plan or {}
    required_groups = _field_groups(plan)
    required_fields = _field_names(required_groups)
    source_ready = (
        plan.get("schema_version") == "GrokAbxRunesOperatorDecisionRecordPlan.v1"
        and plan.get("status") == EXPECTED_SOURCE_STATUS
        and plan.get("recommended_next_lane")
        == "GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_DRY_RUN"
        and plan.get("operator_input_required") is True
        and plan.get("decision_record_created") is False
        and plan.get("rune_registration_authorized") is False
        and plan.get("catalog_mutation_authorized") is False
        and plan.get("yggdrasil_binding_mutation_authorized") is False
        and plan.get("valid_for_execution") is False
        and plan.get("safe_to_auto_continue") is False
    )

    if not plan_observed:
        status = NOT_COMPUTABLE
        validation_passed = False
        validation_blockers = [
            "source_operator_decision_record_plan_missing_or_unreadable",
            f"source_path:{SOURCE_PLAN_JSON_PATH}",
        ]
    elif not source_ready:
        status = "GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_DRY_RUN_BLOCKED"
        validation_passed = False
        validation_blockers = ["source_operator_decision_record_plan_not_ready"]
    else:
        status = "GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_DRY_RUN_READY"
        validation_passed = True
        validation_blockers = [
            "operator_identity_not_attested",
            "grok_claim_disposition_not_attested",
            "authority_boundary_not_attested",
            "terminal_output_controls_not_attested",
        ]

    simulated_record = {
        "artifact_type": "GrokAbxRunesOperatorDecisionRecord.v1.simulated",
        "simulated_only": True,
        "decision_record_id": "grok_abx_runes_operator_decision_record_001.simulated",
        "decision_record_hash": "SIMULATED_PENDING_OPERATOR_INPUT",
        "selected_decision": "HOLD_FOR_OPERATOR_REVIEW",
        "decision_rationale": "SIMULATED_PENDING_OPERATOR_INPUT",
        "decision_outcome_summary": "SIMULATED_HOLD_PENDING_OPERATOR_INPUT",
        "selected_follow_on_action": "MAINTAIN_GROK_ABX_RUNES_OPERATOR_REVIEW_HOLD",
        "terminal_authority_summary": "SIMULATED_NO_AUTHORITY_GRANTED",
        "required_field_groups": required_groups,
        "required_field_names": required_fields,
        "attested_field_count": 0,
        "missing_attested_field_count": len(required_fields),
        "operator_decision_attested": False,
        "decision_record_created": False,
        "authorization_record_created": False,
        "external_backlog_accepted": False,
        "separate_registration_planning_authorized": False,
        "catalog_mutation_authorized": False,
        "rune_registration_authorized": False,
        "yggdrasil_binding_mutation_authorized": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "pr_merge_authority": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
    }

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "dry_run_id": DRY_RUN_ID,
        "status": status,
        "source_plan_path": SOURCE_PLAN_JSON_PATH.as_posix(),
        "source_plan_hash": str(plan.get("decision_record_plan_hash", NOT_COMPUTABLE)),
        "source_plan_ready": source_ready,
        "validation_passed": validation_passed,
        "validation_blockers": validation_blockers,
        "simulated_decision_record": simulated_record,
        "simulated_only": True,
        "operator_input_required": True,
        "operator_decision_attested": False,
        "decision_record_created": False,
        "authorization_record_created": False,
        "external_backlog_accepted": False,
        "separate_registration_planning_authorized": False,
        "catalog_mutation_authorized": False,
        "rune_registration_authorized": False,
        "yggdrasil_binding_mutation_authorized": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "pr_merge_authority": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "canon_mutation": False,
        "recommended_next_lane": (
            "GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_REVIEW"
            if source_ready
            else NOT_COMPUTABLE
        ),
        "recommended_next_action": (
            "review the simulated Grok ABX-Runes operator decision record and "
            "hold for external operator attestations without creating a record"
            if source_ready
            else "restore the Grok ABX-Runes operator decision-record plan before dry-run review"
        ),
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authorization_granted": False,
        "implementation_authorized": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "authority_locks": _authority_locks(),
        "downstream": NOT_COMPUTABLE,
    }
    return {**packet, "dry_run_hash": canonical_hash(packet)}


def render_grok_abx_runes_operator_decision_record_dry_run_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Grok ABX-Runes Operator Decision Record Dry Run",
        "",
        f"- dry_run_id: {packet['dry_run_id']}",
        f"- status: {packet['status']}",
        f"- source_plan_ready: {packet['source_plan_ready']}",
        f"- validation_passed: {packet['validation_passed']}",
        f"- simulated_only: {packet['simulated_only']}",
        f"- decision_record_created: {packet['decision_record_created']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Validation Blockers",
    ]
    for blocker in packet["validation_blockers"]:
        lines.append(f"- {blocker}")
    simulated = packet["simulated_decision_record"]
    if isinstance(simulated, Mapping):
        lines.extend(
            [
                "",
                "## Simulated Decision Record",
                f"- selected_decision: {simulated['selected_decision']}",
                f"- selected_follow_on_action: {simulated['selected_follow_on_action']}",
                f"- missing_attested_field_count: {simulated['missing_attested_field_count']}",
                f"- terminal_authority_summary: {simulated['terminal_authority_summary']}",
            ]
        )
    return lines


def write_grok_abx_runes_operator_decision_record_dry_run(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_grok_abx_runes_operator_decision_record_dry_run(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / DRY_RUN_JSON_PATH, packet)
    md_path = root / DRY_RUN_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(render_grok_abx_runes_operator_decision_record_dry_run_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
    return packet
