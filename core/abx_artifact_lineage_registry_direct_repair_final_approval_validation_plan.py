from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxArtifactLineageRegistryDirectRepairFinalApprovalValidationPlan.v1"
PLAN_ID = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_FINAL_APPROVAL_VALIDATION_PLAN_001"
DETERMINISTIC_GENERATED_AT = "2026-06-05T00:00:00Z"
SOURCE_FINAL_APPROVAL_DRY_RUN_PATH = "out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_dry_run/latest.json"
OUT_JSON = "out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_validation_plan/latest.json"
OUT_MD = "out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_validation_plan/latest.md"
DOWNSTREAM = "NOT_COMPUTABLE"
RECOMMENDED_NEXT_PLAN = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_FINAL_APPROVAL_VALIDATION_DRY_RUN_001"

FORBIDDEN_ACTIONS = [
    "execute_direct_repairs",
    "grant_repair_authority",
    "grant_execution_authority",
    "mutate_governance",
    "treat_final_approval_validation_plan_as_final_approval_record",
    "treat_validation_plan_as_repair_completion",
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


def _source_governance_locks(source_dry_run: Mapping[str, Any]) -> dict[str, Any]:
    return dict(source_dry_run.get("governance_locks", {}))


def _normalized_results(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"check_id": str(item.get("check_id", "NOT_COMPUTABLE")), "passed": bool(item.get("passed", False))}
        for item in checks
    ]


def build_abx_artifact_lineage_registry_direct_repair_final_approval_validation_plan(
    *,
    repo_root: str | Path = ".",
    source_final_approval_dry_run_path: str | Path = SOURCE_FINAL_APPROVAL_DRY_RUN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    dry_run_path = root / source_final_approval_dry_run_path
    source_dry_run = _load_json(dry_run_path)

    source_final_approval_dry_run_hash = _source_hash(dry_run_path)
    source_final_approval_dry_run_observed = (
        source_dry_run.get("artifact_type") == "AbxArtifactLineageRegistryDirectRepairFinalApprovalDryRun.v1"
        and source_dry_run.get("dry_run_id") == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_FINAL_APPROVAL_DRY_RUN_001"
        and source_dry_run.get("status") == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_FINAL_APPROVAL_DRY_RUN_READY"
    )
    final_approval_ready = bool(source_dry_run.get("final_approval_ready", False))

    simulation_checks = _normalized_results(list(source_dry_run.get("ready_workstreams", [])))
    validation_checks = _normalized_results(list(source_dry_run.get("validation_checks", [])))
    invariant_checks = [
        {"check_id": "approval_granted_remains_false", "passed": source_dry_run.get("approval_granted") is False},
        {"check_id": "valid_for_repair_remains_false", "passed": source_dry_run.get("valid_for_repair") is False},
        {"check_id": "valid_for_execution_remains_false", "passed": source_dry_run.get("valid_for_execution") is False},
    ]

    blockers: list[str] = []
    if not source_final_approval_dry_run_observed:
        blockers.append("SOURCE_FINAL_APPROVAL_DRY_RUN_NOT_READY")
    if source_final_approval_dry_run_observed and not final_approval_ready:
        blockers.append("SOURCE_FINAL_APPROVAL_DRY_RUN_NOT_FINAL_APPROVAL_READY")
    if simulation_checks and not all(item["passed"] for item in simulation_checks):
        blockers.append("SIMULATION_CHECK_FAILED")
    if validation_checks and not all(item["passed"] for item in validation_checks):
        blockers.append("VALIDATION_CHECK_FAILED")
    if not all(item["passed"] for item in invariant_checks):
        blockers.append("INVARIANT_CHECK_FAILED")

    status = (
        "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_FINAL_APPROVAL_VALIDATION_PLAN_READY"
        if not blockers
        else "NOT_COMPUTABLE"
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "status": status,
        "source_final_approval_dry_run": source_dry_run.get("dry_run_id", "NOT_COMPUTABLE"),
        "source_final_approval_dry_run_path": Path(source_final_approval_dry_run_path).as_posix(),
        "source_final_approval_dry_run_hash": source_final_approval_dry_run_hash,
        "source_final_approval_dry_run_observed": source_final_approval_dry_run_observed,
        "source_final_approval_dry_run_status": source_dry_run.get("status", "NOT_COMPUTABLE"),
        "final_approval_ready": final_approval_ready,
        "simulation_checks": simulation_checks,
        "validation_checks": validation_checks,
        "invariant_checks": invariant_checks,
        "blockers": sorted(blockers),
        "required_operator_actions": [
            "review_direct_repair_final_approval_dry_run",
            "review_direct_repair_final_approval_validation_plan",
            "maintain_non_authoritative_direct_repair_boundary",
        ],
        "recommended_next_action": (
            "validate the simulated final-approval surface only; do not execute registry, output-pairing, or docs-reference repairs from final-approval-validation readiness alone"
            if status.endswith("_READY")
            else "repair final-approval-validation-plan prerequisites before further direct-repair review"
        ),
        "recommended_next_plan": RECOMMENDED_NEXT_PLAN,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "governance_locks": _source_governance_locks(source_dry_run),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "final_approval_validation_plan_only": True,
        "implementation_authorized": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "downstream": DOWNSTREAM,
    }
    return {**base, "packet_hash": canonical_hash(base)}


def render_markdown(packet: Mapping[str, Any]) -> str:
    lines = [
        "# ABX Artifact Lineage Registry Direct Repair Final Approval Validation Plan",
        "",
        f"- `plan_id`: `{packet['plan_id']}`",
        f"- `status`: `{packet['status']}`",
        f"- `source_final_approval_dry_run`: `{packet['source_final_approval_dry_run']}`",
        f"- `recommended_next_plan`: `{packet['recommended_next_plan']}`",
        f"- `final_approval_ready`: `{packet['final_approval_ready']}`",
        "",
        "## Blockers",
    ]
    for blocker in packet["blockers"]:
        lines.append(f"- `{blocker}`")
    return "\n".join(lines) + "\n"


def write_abx_artifact_lineage_registry_direct_repair_final_approval_validation_plan(
    json_path: Path,
    md_path: Path,
) -> dict[str, Any]:
    packet = build_abx_artifact_lineage_registry_direct_repair_final_approval_validation_plan()
    write_canonical_json(json_path, packet)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(packet), encoding="utf-8")
    return packet
