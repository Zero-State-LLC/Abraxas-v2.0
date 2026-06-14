from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_merge_anchor_source_selection_decision_record_plan import (
    PLAN_JSON_PATH as SOURCE_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxCodegenMergeAnchorSourceSelectionDecisionRecordDryRun.v1"
DRY_RUN_ID = "abx_codegen_merge_anchor_source_selection_decision_record_dry_run_001"
DRY_RUN_JSON_PATH = Path(
    "out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_dry_run_001.latest.json"
)
DRY_RUN_MD_PATH = DRY_RUN_JSON_PATH.with_suffix(".md")

EXPECTED_SOURCE_STATUS = (
    "ABX_CODEGEN_MERGE_ANCHOR_SOURCE_SELECTION_DECISION_RECORD_PLAN_READY"
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _authority_locks() -> dict[str, bool]:
    return {
        "authorization_record_creation": False,
        "canon_mutation": False,
        "canonical_source_selection": False,
        "code_generation": False,
        "code_mutation": False,
        "contracts_codegen_directory_creation": False,
        "core_codegen_directory_creation": False,
        "decision_record_creation": False,
        "execution": False,
        "file_writeback": False,
        "forecast_routing": False,
        "github_writeback": False,
        "implementation_authorization": False,
        "implementation_unblock": False,
        "merge_anchor_mutation": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "patch_application": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "source_promotion": False,
    }


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _simulated_per_anchor_decisions(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = plan.get("source_selection_requirements", [])
    if not isinstance(rows, list):
        return []
    simulated: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        simulated.append(
            {
                "anchor_id": str(row.get("applies_to_anchor_id", "NOT_COMPUTABLE")),
                "selected_decision": "MAINTAIN_HOLD",
                "canonical_source_page_id_or_url": str(
                    row.get("candidate_page_id_or_url", "NOT_COMPUTABLE")
                ),
                "canonical_source_title": str(
                    row.get("candidate_source_title", "NOT_COMPUTABLE")
                ),
                "operator_rationale": "SIMULATED_PENDING_OPERATOR_INPUT",
                "authority_boundary_acknowledgement": "SIMULATED_PENDING_OPERATOR_INPUT",
                "implementation_unblocked": False,
                "operator_attested": False,
                "source_evidence_hash": str(
                    row.get("source_evidence_hash", "NOT_COMPUTABLE")
                ),
            }
        )
    return simulated


def build_abx_codegen_merge_anchor_source_selection_decision_record_dry_run(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    plan = _read_json(root / SOURCE_PLAN_JSON)
    plan_observed = plan is not None
    plan = plan or {}

    source_ready = (
        plan.get("schema_version")
        == "AbxCodegenMergeAnchorSourceSelectionDecisionRecordPlan.v1"
        and plan.get("status") == EXPECTED_SOURCE_STATUS
        and plan.get("recommended_next_patch") == "NOT_COMPUTABLE"
        and plan.get("safe_to_auto_continue") is False
        and plan.get("operator_input_required") is True
        and plan.get("decision_record_created") is False
        and plan.get("execution_authority") is False
        and plan.get("valid_for_implementation") is False
    )

    if not plan_observed:
        status = "NOT_COMPUTABLE"
        validation_passed = False
        validation_blockers = [
            "source_decision_record_plan_missing_or_unreadable",
            f"source_path:{SOURCE_PLAN_JSON}",
        ]
    elif not source_ready:
        status = "ABX_CODEGEN_MERGE_ANCHOR_SOURCE_SELECTION_DECISION_RECORD_DRY_RUN_BLOCKED"
        validation_passed = False
        validation_blockers = ["source_decision_record_plan_not_ready"]
    else:
        status = "ABX_CODEGEN_MERGE_ANCHOR_SOURCE_SELECTION_DECISION_RECORD_DRY_RUN_READY"
        validation_passed = True
        validation_blockers = [
            "operator_identity_not_attested",
            "operator_decision_not_attested",
            "operator_rationale_not_attested",
            "operator_acknowledgements_not_attested",
            "operator_evidence_bundle_not_attested",
        ]

    simulated_record = {
        "artifact_type": "AbxCodegenMergeAnchorSourceSelectionDecisionRecord.v1.simulated",
        "simulated_only": True,
        "decision_record_id": "abx_codegen_merge_anchor_source_selection_decision_record_001.simulated",
        "decision_record_hash": "SIMULATED_PENDING_OPERATOR_INPUT",
        "selected_decision": "MAINTAIN_HOLD",
        "decision_rationale": "SIMULATED_PENDING_OPERATOR_INPUT",
        "operator_identity_fields": _string_list(plan.get("required_operator_identity_fields")),
        "decision_fields": _string_list(plan.get("required_decision_fields")),
        "acknowledgement_fields": _string_list(plan.get("required_acknowledgement_fields")),
        "evidence_fields": _string_list(plan.get("required_evidence_fields")),
        "per_anchor_decisions": _simulated_per_anchor_decisions(plan),
        "operator_decision_attested": False,
        "decision_record_created": False,
        "canonical_source_selection_authorized": False,
        "implementation_authorized": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
    }

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "dry_run_id": DRY_RUN_ID,
        "dry_run_hash": "",
        "source_plan_path": str(SOURCE_PLAN_JSON),
        "source_plan_hash": str(plan.get("decision_record_plan_hash", "NOT_COMPUTABLE")),
        "source_plan_ready": source_ready,
        "validation_passed": validation_passed,
        "validation_blockers": validation_blockers,
        "simulated_decision_record": simulated_record,
        "simulated_only": True,
        "operator_input_required": True,
        "operator_decision_attested": False,
        "decision_record_created": False,
        "recommended_next_patch": "NOT_COMPUTABLE",
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "implementation_authorized": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "authority_locks": _authority_locks(),
    }
    packet["dry_run_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "dry_run_hash"}
    )
    return packet


def render_abx_codegen_merge_anchor_source_selection_decision_record_dry_run_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Merge Anchor Source Selection Decision Record Dry Run",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `source_plan_ready`: `{packet['source_plan_ready']}`",
        f"- `validation_passed`: `{packet['validation_passed']}`",
        f"- `simulated_only`: `{packet['simulated_only']}`",
        f"- `decision_record_created`: `{packet['decision_record_created']}`",
        f"- `operator_decision_attested`: `{packet['operator_decision_attested']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Validation Blockers",
        "",
    ]
    for blocker in packet["validation_blockers"]:
        lines.append(f"- `{blocker}`")
    lines.extend(["", "## Simulated Per-Anchor Decisions", ""])
    simulated = packet["simulated_decision_record"]
    if isinstance(simulated, Mapping):
        for row in simulated.get("per_anchor_decisions", []):
            if isinstance(row, Mapping):
                lines.append(
                    f"- `{row['anchor_id']}`: `{row['selected_decision']}` "
                    f"(implementation_unblocked={row['implementation_unblocked']})"
                )
    return lines


def write_abx_codegen_merge_anchor_source_selection_decision_record_dry_run(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_codegen_merge_anchor_source_selection_decision_record_dry_run(root)
    write_canonical_json(target_root / DRY_RUN_JSON_PATH, packet)
    _write_markdown(
        target_root / DRY_RUN_MD_PATH,
        render_abx_codegen_merge_anchor_source_selection_decision_record_dry_run_markdown(
            packet
        ),
    )
    return packet
