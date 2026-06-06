from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxArtifactLineageRegistryDirectRepairFinalApprovalDryRun.v1"
DRY_RUN_ID = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_FINAL_APPROVAL_DRY_RUN_001"
DETERMINISTIC_GENERATED_AT = "2026-06-05T00:00:00Z"
SOURCE_FINAL_APPROVAL_PLAN_PATH = "out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_plan/latest.json"
OUT_JSON = "out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_dry_run/latest.json"
OUT_MD = "out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_dry_run/latest.md"
DOWNSTREAM = "NOT_COMPUTABLE"
RECOMMENDED_NEXT_PLAN = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_FINAL_APPROVAL_VALIDATION_PLAN_001"

FORBIDDEN_ACTIONS = [
    "execute_direct_repairs",
    "grant_repair_authority",
    "grant_execution_authority",
    "mutate_governance",
    "treat_final_approval_dry_run_as_final_approval_record",
    "treat_final_approval_dry_run_as_repair_completion",
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


def _simulated_final_approval_execution(source_plan: Mapping[str, Any]) -> dict[str, Any]:
    acknowledgements = [str(item) for item in source_plan.get("required_operator_acknowledgements", [])]
    fields = [str(item) for item in source_plan.get("required_operator_approval_fields", [])]
    constraints = [str(item) for item in source_plan.get("final_approval_constraints", [])]

    requirements_present = bool(acknowledgements and fields and constraints)
    blockers: list[str] = []
    if not requirements_present:
        blockers.append("missing_final_approval_requirement_group")

    return {
        "simulated_only": True,
        "operator_input_required": True,
        "final_approval_ready": requirements_present,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "approval_authority_granted": False,
        "repair_authority_granted": False,
        "execution_authority_granted": False,
        "final_approval_blockers": blockers,
    }


def build_abx_artifact_lineage_registry_direct_repair_final_approval_dry_run(
    *,
    repo_root: str | Path = ".",
    source_final_approval_plan_path: str | Path = SOURCE_FINAL_APPROVAL_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    approval_plan_path = root / source_final_approval_plan_path
    source_plan = _load_json(approval_plan_path)

    source_final_approval_plan_hash = _source_hash(approval_plan_path)
    source_final_approval_plan_observed = (
        source_plan.get("artifact_type") == "AbxArtifactLineageRegistryDirectRepairFinalApprovalPlan.v1"
        and source_plan.get("final_approval_plan_id") == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_FINAL_APPROVAL_PLAN_001"
        and source_plan.get("status") == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_FINAL_APPROVAL_PLAN_READY"
    )
    validation_passed = bool(source_plan.get("validation_passed", False))

    simulated_final_approval_execution = _simulated_final_approval_execution(source_plan)
    final_approval_ready = bool(simulated_final_approval_execution["final_approval_ready"])

    blockers: list[str] = []
    if not source_final_approval_plan_observed:
        blockers.append("SOURCE_FINAL_APPROVAL_PLAN_NOT_READY")
    if source_final_approval_plan_observed and not validation_passed:
        blockers.append("SOURCE_FINAL_APPROVAL_PLAN_VALIDATION_FAILED")
    blockers.extend(simulated_final_approval_execution["final_approval_blockers"])

    status = (
        "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_FINAL_APPROVAL_DRY_RUN_READY"
        if not blockers and final_approval_ready
        else "NOT_COMPUTABLE"
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "dry_run_id": DRY_RUN_ID,
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "status": status,
        "source_final_approval_plan": source_plan.get("final_approval_plan_id", "NOT_COMPUTABLE"),
        "source_final_approval_plan_path": Path(source_final_approval_plan_path).as_posix(),
        "source_final_approval_plan_hash": source_final_approval_plan_hash,
        "source_final_approval_plan_observed": source_final_approval_plan_observed,
        "source_final_approval_plan_status": source_plan.get("status", "NOT_COMPUTABLE"),
        "validation_passed": validation_passed,
        "ready_workstreams": list(source_plan.get("ready_workstreams", [])),
        "validation_checks": list(source_plan.get("validation_checks", [])),
        "simulated_final_approval_execution": simulated_final_approval_execution,
        "final_approval_ready": final_approval_ready,
        "final_approval_blockers": sorted(simulated_final_approval_execution["final_approval_blockers"]),
        "blockers": sorted(blockers),
        "required_operator_actions": [
            "review_direct_repair_final_approval_plan",
            "review_direct_repair_final_approval_dry_run",
            "maintain_non_authoritative_direct_repair_boundary",
        ],
        "recommended_next_action": (
            "treat the final-approval dry run as advisory-only simulated evidence; do not execute registry, output-pairing, or docs-reference repairs from dry-run readiness alone"
            if status.endswith("_READY")
            else "repair final-approval-dry-run prerequisites before further direct-repair review"
        ),
        "recommended_next_plan": RECOMMENDED_NEXT_PLAN,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "governance_locks": _source_governance_locks(source_plan),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "final_approval_dry_run_only": True,
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
        "# ABX Artifact Lineage Registry Direct Repair Final Approval Dry Run",
        "",
        f"- `dry_run_id`: `{packet['dry_run_id']}`",
        f"- `status`: `{packet['status']}`",
        f"- `source_final_approval_plan`: `{packet['source_final_approval_plan']}`",
        f"- `recommended_next_plan`: `{packet['recommended_next_plan']}`",
        f"- `final_approval_ready`: `{packet['final_approval_ready']}`",
        "",
        "## Final Approval Blockers",
    ]
    for blocker in packet["final_approval_blockers"]:
        lines.append(f"- `{blocker}`")
    return "\n".join(lines) + "\n"


def write_abx_artifact_lineage_registry_direct_repair_final_approval_dry_run(
    json_path: Path,
    md_path: Path,
) -> dict[str, Any]:
    packet = build_abx_artifact_lineage_registry_direct_repair_final_approval_dry_run()
    write_canonical_json(json_path, packet)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(packet), encoding="utf-8")
    return packet
