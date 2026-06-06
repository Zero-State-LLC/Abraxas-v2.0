from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxArtifactLineageRegistryDirectRepairValidationDryRun.v1"
DRY_RUN_ID = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_VALIDATION_DRY_RUN_001"
DETERMINISTIC_GENERATED_AT = "2026-06-05T00:00:00Z"
SOURCE_VALIDATION_PLAN_PATH = "out/sync/abx_artifact_lineage_registry_direct_repair_validation_plan/latest.json"
SOURCE_DRY_RUN_PATH = "out/sync/abx_artifact_lineage_registry_direct_repair_implementation_dry_run/latest.json"
OUT_JSON = "out/sync/abx_artifact_lineage_registry_direct_repair_validation_dry_run/latest.json"
OUT_MD = "out/sync/abx_artifact_lineage_registry_direct_repair_validation_dry_run/latest.md"
DOWNSTREAM = "NOT_COMPUTABLE"
RECOMMENDED_NEXT_PLAN = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_APPROVAL_PLAN_001"

FORBIDDEN_ACTIONS = [
    "implement_runtime_execution",
    "promote_research_to_canon",
    "mutate_governance",
    "grant_execution_authority",
    "treat_validation_dry_run_as_repair_completion",
    "treat_validation_pass_as_repair_authority",
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
    source = _load_json(path)
    return canonical_hash(source) if source else "NOT_COMPUTABLE"


def _governance_locks(source_plan: Mapping[str, Any]) -> dict[str, Any]:
    return dict(source_plan.get("governance_locks", {}))


def _normalized_results(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"check_id": str(item.get("check_id", "NOT_COMPUTABLE")), "passed": bool(item.get("passed", False))}
        for item in checks
    ]


def _simulated_validation_execution(
    source_plan: Mapping[str, Any],
) -> dict[str, Any]:
    simulation_checks = _normalized_results(list(source_plan.get("simulation_checks", [])))
    invariant_checks = _normalized_results(list(source_plan.get("invariant_checks", [])))
    validation_checks = _normalized_results(list(source_plan.get("validation_checks", [])))

    checks_present = all([simulation_checks, invariant_checks, validation_checks])
    checks_passed = (
        checks_present
        and all(item["passed"] for item in simulation_checks)
        and all(item["passed"] for item in invariant_checks)
        and all(item["passed"] for item in validation_checks)
    )
    blockers = []
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
        "repair_authority_granted": False,
        "execution_authority_granted": False,
        "validation_blockers": blockers,
    }


def build_abx_artifact_lineage_registry_direct_repair_validation_dry_run(
    *,
    repo_root: str | Path = ".",
    source_validation_plan_path: str | Path = SOURCE_VALIDATION_PLAN_PATH,
    source_dry_run_path: str | Path = SOURCE_DRY_RUN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    validation_plan_path = root / source_validation_plan_path
    dry_run_path = root / source_dry_run_path
    source_plan = _load_json(validation_plan_path)
    source_dry_run = _load_json(dry_run_path)

    source_validation_plan_hash = _source_hash(validation_plan_path)
    source_dry_run_hash = _source_hash(dry_run_path)
    source_validation_plan_ready = (
        source_plan.get("artifact_type") == "AbxArtifactLineageRegistryDirectRepairValidationPlan.v1"
        and source_plan.get("plan_id") == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_VALIDATION_PLAN_001"
        and source_plan.get("status") == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_VALIDATION_PLAN_READY"
    )
    source_dry_run_observed = (
        source_dry_run.get("artifact_type") == "AbxArtifactLineageRegistryDirectRepairImplementationDryRun.v1"
        and source_dry_run.get("dry_run_id") == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_IMPLEMENTATION_DRY_RUN_001"
        and source_dry_run.get("dry_run_status")
        == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_IMPLEMENTATION_DRY_RUN_READY"
    )

    simulated_validation_execution = _simulated_validation_execution(source_plan)
    validation_passed = bool(simulated_validation_execution["validation_passed"])

    blockers: list[str] = []
    if not source_validation_plan_ready:
        blockers.append("SOURCE_VALIDATION_PLAN_NOT_READY")
    if not source_dry_run_observed:
        blockers.append("SOURCE_IMPLEMENTATION_DRY_RUN_NOT_OBSERVED")
    blockers.extend(simulated_validation_execution["validation_blockers"])

    status = (
        "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_VALIDATION_DRY_RUN_READY"
        if not blockers and validation_passed
        else "NOT_COMPUTABLE"
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "dry_run_id": DRY_RUN_ID,
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "status": status,
        "source_validation_plan": source_plan.get("plan_id", "NOT_COMPUTABLE"),
        "source_validation_plan_path": Path(source_validation_plan_path).as_posix(),
        "source_validation_plan_hash": source_validation_plan_hash,
        "source_validation_plan_observed": source_validation_plan_ready,
        "source_implementation_dry_run": source_dry_run.get("dry_run_id", "NOT_COMPUTABLE"),
        "source_implementation_dry_run_path": Path(source_dry_run_path).as_posix(),
        "source_implementation_dry_run_hash": source_dry_run_hash,
        "source_implementation_dry_run_observed": source_dry_run_observed,
        "simulation_results": _normalized_results(list(source_plan.get("simulation_checks", []))),
        "invariant_results": _normalized_results(list(source_plan.get("invariant_checks", []))),
        "validation_results": _normalized_results(list(source_plan.get("validation_checks", []))),
        "simulated_validation_execution": simulated_validation_execution,
        "validation_passed": validation_passed,
        "validation_blockers": sorted(simulated_validation_execution["validation_blockers"]),
        "blockers": sorted(blockers),
        "required_operator_actions": [
            "review_direct_repair_validation_plan",
            "review_validation_dry_run_execution",
            "maintain_non_authoritative_validation_boundary",
        ],
        "recommended_next_action": (
            "treat the validation dry run as advisory-only simulated proof; do not execute repairs from validation readiness alone"
            if status.endswith("_READY")
            else "repair validation dry-run prerequisites before further direct-repair review"
        ),
        "recommended_next_plan": RECOMMENDED_NEXT_PLAN,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "governance_locks": _governance_locks(source_plan),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "validation_dry_run_only": True,
        "implementation_authorized": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "downstream": DOWNSTREAM,
    }
    return {**base, "packet_hash": canonical_hash(base)}


def render_markdown(packet: Mapping[str, Any]) -> str:
    lines = [
        "# ABX Artifact Lineage Registry Direct Repair Validation Dry Run",
        "",
        f"- `dry_run_id`: `{packet['dry_run_id']}`",
        f"- `status`: `{packet['status']}`",
        f"- `source_validation_plan`: `{packet['source_validation_plan']}`",
        f"- `source_implementation_dry_run`: `{packet['source_implementation_dry_run']}`",
        f"- `recommended_next_plan`: `{packet['recommended_next_plan']}`",
        f"- `validation_passed`: `{packet['validation_passed']}`",
        "",
        "## Validation Blockers",
    ]
    for blocker in packet["validation_blockers"]:
        lines.append(f"- `{blocker}`")
    return "\n".join(lines) + "\n"


def write_abx_artifact_lineage_registry_direct_repair_validation_dry_run(
    json_path: Path,
    md_path: Path,
) -> dict[str, Any]:
    packet = build_abx_artifact_lineage_registry_direct_repair_validation_dry_run()
    write_canonical_json(json_path, packet)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(packet), encoding="utf-8")
    return packet
