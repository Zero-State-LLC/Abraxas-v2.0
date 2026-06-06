from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxArtifactLineageRegistryDirectRepairApprovalValidationDryRun.v1"
DRY_RUN_ID = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_APPROVAL_VALIDATION_DRY_RUN_001"
DETERMINISTIC_GENERATED_AT = "2026-06-05T00:00:00Z"
SOURCE_VALIDATION_PLAN_PATH = "out/sync/abx_artifact_lineage_registry_direct_repair_approval_validation_plan/latest.json"
OUT_JSON = "out/sync/abx_artifact_lineage_registry_direct_repair_approval_validation_dry_run/latest.json"
OUT_MD = "out/sync/abx_artifact_lineage_registry_direct_repair_approval_validation_dry_run/latest.md"
DOWNSTREAM = "NOT_COMPUTABLE"
RECOMMENDED_NEXT_PLAN = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_FINAL_APPROVAL_PLAN_001"

FORBIDDEN_ACTIONS = [
    "execute_direct_repairs",
    "grant_repair_authority",
    "grant_execution_authority",
    "mutate_governance",
    "treat_approval_validation_dry_run_as_approval_record",
    "treat_validation_dry_run_as_repair_completion",
    "normalize_runner_casing_without_operator_review",
    "infer_notion_evidence",
]


def _load_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _source_hash(path: Path) -> str:
    payload = _load_json(path)
    return canonical_hash(payload) if payload else "NOT_COMPUTABLE"


def _source_governance_locks(source_plan: Mapping[str, Any]) -> dict[str, Any]:
    return dict(source_plan.get("governance_locks", {}))


def _simulated_validation_execution(source_plan: Mapping[str, Any]) -> dict[str, Any]:
    simulation_checks = list(source_plan.get("simulation_checks", []))
    validation_checks = list(source_plan.get("validation_checks", []))
    invariant_checks = list(source_plan.get("invariant_checks", []))

    checks_present = bool(simulation_checks and validation_checks and invariant_checks)
    checks_passed = (
        checks_present
        and all(bool(item.get("passed", False)) for item in simulation_checks)
        and all(bool(item.get("passed", False)) for item in validation_checks)
        and all(bool(item.get("passed", False)) for item in invariant_checks)
    )

    blockers: list[str] = []
    if not checks_present:
        blockers.append("missing_validation_check_group")
    if checks_present and not checks_passed:
        blockers.append("validation_check_failed")

    return {
        "simulated_only": True,
        "operator_input_required": True,
        "validation_passed": checks_passed,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "approval_authority_granted": False,
        "repair_authority_granted": False,
        "execution_authority_granted": False,
        "validation_blockers": blockers,
    }


def build_abx_artifact_lineage_registry_direct_repair_approval_validation_dry_run(
    *,
    repo_root: str | Path = ".",
    source_validation_plan_path: str | Path = SOURCE_VALIDATION_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    validation_plan_path = root / source_validation_plan_path
    source_plan = _load_json(validation_plan_path)

    source_validation_plan_hash = _source_hash(validation_plan_path)
    source_validation_plan_observed = (
        source_plan.get("artifact_type") == "AbxArtifactLineageRegistryDirectRepairApprovalValidationPlan.v1"
        and source_plan.get("plan_id") == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_APPROVAL_VALIDATION_PLAN_001"
        and source_plan.get("status") == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_APPROVAL_VALIDATION_PLAN_READY"
    )
    approval_ready = bool(source_plan.get("approval_ready", False))

    simulated_validation_execution = _simulated_validation_execution(source_plan)
    validation_passed = bool(simulated_validation_execution["validation_passed"])

    blockers: list[str] = []
    if not source_validation_plan_observed:
        blockers.append("SOURCE_APPROVAL_VALIDATION_PLAN_NOT_READY")
    if source_validation_plan_observed and not approval_ready:
        blockers.append("SOURCE_APPROVAL_VALIDATION_PLAN_NOT_APPROVAL_READY")
    blockers.extend(simulated_validation_execution["validation_blockers"])

    status = (
        "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_APPROVAL_VALIDATION_DRY_RUN_READY"
        if not blockers and validation_passed
        else "NOT_COMPUTABLE"
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "dry_run_id": DRY_RUN_ID,
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "status": status,
        "source_approval_validation_plan": source_plan.get("plan_id", "NOT_COMPUTABLE"),
        "source_approval_validation_plan_path": Path(source_validation_plan_path).as_posix(),
        "source_approval_validation_plan_hash": source_validation_plan_hash,
        "source_approval_validation_plan_observed": source_validation_plan_observed,
        "source_approval_validation_plan_status": source_plan.get("status", "NOT_COMPUTABLE"),
        "approval_ready": approval_ready,
        "simulation_checks": list(source_plan.get("simulation_checks", [])),
        "validation_checks": list(source_plan.get("validation_checks", [])),
        "invariant_checks": list(source_plan.get("invariant_checks", [])),
        "simulated_validation_execution": simulated_validation_execution,
        "validation_passed": validation_passed,
        "validation_blockers": sorted(simulated_validation_execution["validation_blockers"]),
        "blockers": sorted(blockers),
        "required_operator_actions": [
            "review_direct_repair_approval_validation_plan",
            "review_direct_repair_approval_validation_dry_run",
            "maintain_non_authoritative_direct_repair_boundary",
        ],
        "recommended_next_action": (
            "treat the approval-validation dry run as advisory-only simulated evidence; do not execute registry, output-pairing, or docs-reference repairs from validation readiness alone"
            if status.endswith("_READY")
            else "repair approval-validation-dry-run prerequisites before further direct-repair review"
        ),
        "recommended_next_plan": RECOMMENDED_NEXT_PLAN,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "governance_locks": _source_governance_locks(source_plan),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "approval_validation_dry_run_only": True,
        "simulated_only": True,
        "approval_granted": False,
        "implementation_authorized": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "downstream": DOWNSTREAM,
    }
    return {**base, "packet_hash": canonical_hash(base)}


def render_markdown(packet: Mapping[str, Any]) -> str:
    lines = [
        "# ABX Artifact Lineage Registry Direct Repair Approval Validation Dry Run",
        "",
        f"- `dry_run_id`: `{packet['dry_run_id']}`",
        f"- `status`: `{packet['status']}`",
        f"- `source_approval_validation_plan`: `{packet['source_approval_validation_plan']}`",
        f"- `recommended_next_plan`: `{packet['recommended_next_plan']}`",
        f"- `validation_passed`: `{packet['validation_passed']}`",
        "",
        "## Validation Blockers",
    ]
    for blocker in packet["validation_blockers"]:
        lines.append(f"- `{blocker}`")
    return "\n".join(lines) + "\n"


def write_abx_artifact_lineage_registry_direct_repair_approval_validation_dry_run(
    json_path: Path,
    md_path: Path,
) -> dict[str, Any]:
    packet = build_abx_artifact_lineage_registry_direct_repair_approval_validation_dry_run()
    write_canonical_json(json_path, packet)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(packet), encoding="utf-8")
    return packet
