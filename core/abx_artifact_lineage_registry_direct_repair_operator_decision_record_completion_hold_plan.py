from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxArtifactLineageRegistryDirectRepairOperatorDecisionRecordCompletionHoldPlan.v1"
SOURCE_FINAL_APPROVAL_VALIDATION_DRY_RUN_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_dry_run_001.latest.json"
)
PLAN_JSON_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan_001.latest.json"
)
PLAN_MD_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan_001.latest.md"
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    source_dry_run = _read_json(root / SOURCE_FINAL_APPROVAL_VALIDATION_DRY_RUN_PATH)
    source_observed = source_dry_run is not None

    target_surface = "ABX Artifact Lineage Registry Direct Repair"
    decision_scope = "DIRECT_REPAIR_EXECUTION_DECISION_REQUIRED"
    source_final_approval_validation_dry_run_hash = "NOT_COMPUTABLE"
    source_request_id = "NOT_COMPUTABLE"
    source_validation_plan_hash = "NOT_COMPUTABLE"
    source_hashes = {
        "abx_artifact_lineage_registry_direct_repair_operator_decision_record_operator_decision_request": "NOT_COMPUTABLE",
        "operator_decision_record_completion_hold_plan": "NOT_COMPUTABLE",
    }
    validation_passed = False
    blockers = [
        "source_final_approval_validation_dry_run_missing_or_unreadable",
        f"source_path:{SOURCE_FINAL_APPROVAL_VALIDATION_DRY_RUN_PATH}",
    ]
    unresolved_hold_reasons = [
        "FINAL_OPERATOR_DECISION_RECORD_MISSING",
        "RUNNER_CASING_POLICY_REMAINS_OPERATOR_HELD",
        "NOTION_MAPPING_EVIDENCE_REMAINS_NOT_COMPUTABLE",
        "DIRECT_REPAIR_EXECUTION_AUTHORITY_REMAINS_DENIED",
    ]
    status = "NOT_COMPUTABLE"

    if source_dry_run is not None:
        target_surface = str(source_dry_run.get("target_surface", target_surface))
        decision_scope = str(source_dry_run.get("decision_scope", decision_scope))
        source_final_approval_validation_dry_run_hash = str(source_dry_run.get("dry_run_hash", "NOT_COMPUTABLE"))
        source_request_id = str(source_dry_run.get("source_request_id", source_request_id))
        source_validation_plan_hash = str(
            source_dry_run.get("source_validation_plan_hash", source_validation_plan_hash)
        )
        source_hashes = {
            str(key): str(value) for key, value in dict(source_dry_run.get("source_hashes", {})).items()
        }
        validation_passed = bool(source_dry_run.get("validation_passed", False))
        ready = (
            source_dry_run.get("status")
            == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_FINAL_APPROVAL_VALIDATION_DRY_RUN_READY"
            and validation_passed
        )
        blockers = [] if ready else ["source_final_approval_validation_dry_run_not_ready"]
        status = (
            "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_COMPLETION_HOLD_PLAN_EMITTED"
            if ready
            else "NOT_COMPUTABLE"
        )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "completion_hold_plan_id": "abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan_001",
        "completion_hold_plan_hash": "",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_COMPLETION_HOLD_PLAN_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "completion_hold_plan_only": True,
        "approval_granted": False,
        "implementation_authorized": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "target_surface": target_surface,
        "decision_scope": decision_scope,
        "recommended_next_action": "treat the operator-decision-record chain as terminally held advisory evidence; do not declare completion or execute repairs without explicit future operator decision evidence",
        "recommended_next_patch": "NOT_COMPUTABLE",
        "recommended_next_state": "hold",
        "source_final_approval_validation_dry_run_path": str(SOURCE_FINAL_APPROVAL_VALIDATION_DRY_RUN_PATH),
        "source_final_approval_validation_dry_run_observed": source_observed,
        "source_final_approval_validation_dry_run_hash": source_final_approval_validation_dry_run_hash,
        "source_request_id": source_request_id,
        "source_validation_plan_hash": source_validation_plan_hash,
        "source_hashes": source_hashes,
        "validation_passed": validation_passed,
        "completion_hold_active": True,
        "repair_completion_recognized": False,
        "operator_decision_required": True,
        "unresolved_hold_reasons": unresolved_hold_reasons,
        "required_operator_actions": [
            "review_operator_decision_record_completion_hold_plan",
            "maintain_execution_denial_until_explicit_operator_decision",
            "preserve_runner_policy_and_notion_evidence_holds",
        ],
        "blocked_actions": [
            "DIRECT_REGISTRY_COVERAGE_REPAIR_EXECUTION",
            "DIRECT_OUTPUT_PAIRING_REPAIR_EXECUTION",
            "DIRECT_DOCS_REFERENCE_REPAIR_EXECUTION",
            "RUNNER_CASING_POLICY_OVERRIDE",
            "NOTION_MAPPING_COMPLETENESS_ASSERTION",
        ],
        "blockers": blockers,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
    }
    packet["completion_hold_plan_hash"] = canonical_hash(
        {k: v for k, v in packet.items() if k != "completion_hold_plan_hash"}
    )
    return packet


def render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Artifact Lineage Registry Direct Repair Operator Decision Record Completion Hold Plan",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `target_surface`: `{packet['target_surface']}`",
        f"- `completion_hold_active`: `{packet['completion_hold_active']}`",
        f"- `recommended_next_state`: `{packet['recommended_next_state']}`",
        "",
        "## Unresolved Hold Reasons",
        "",
    ]
    for item in packet["unresolved_hold_reasons"]:
        lines.append(f"- `{item}`")
    return lines


def write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan(root)
    write_canonical_json(target_root / PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / PLAN_MD_PATH,
        render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan_markdown(
            packet
        ),
    )
    return packet
