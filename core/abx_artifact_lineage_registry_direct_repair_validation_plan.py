from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxArtifactLineageRegistryDirectRepairValidationPlan.v1"
PLAN_ID = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_VALIDATION_PLAN_001"
DETERMINISTIC_GENERATED_AT = "2026-06-05T00:00:00Z"
SOURCE_DRY_RUN_PATH = (
    "out/sync/abx_artifact_lineage_registry_direct_repair_implementation_dry_run/latest.json"
)
SOURCE_IMPLEMENTATION_PLAN_PATH = (
    "out/sync/abx_artifact_lineage_registry_direct_repair_implementation_plan/latest.json"
)
OUT_JSON = "out/sync/abx_artifact_lineage_registry_direct_repair_validation_plan/latest.json"
OUT_MD = "out/sync/abx_artifact_lineage_registry_direct_repair_validation_plan/latest.md"
DOWNSTREAM = "NOT_COMPUTABLE"
RECOMMENDED_NEXT_PLAN = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_VALIDATION_DRY_RUN_001"

FORBIDDEN_ACTIONS = [
    "implement_runtime_execution",
    "promote_research_to_canon",
    "mutate_governance",
    "grant_execution_authority",
    "treat_dry_run_as_repair_completion",
    "normalize_runner_casing_without_operator_review",
    "infer_notion_evidence",
    "convert_validation_plan_into_repair_authority",
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


def _governance_locks(source_dry_run: Mapping[str, Any]) -> dict[str, Any]:
    return dict(source_dry_run.get("governance_locks", {}))


def _simulation_checks(source_dry_run: Mapping[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for idx, run in enumerate(source_dry_run.get("simulated_workstream_runs", []), start=1):
        checks.append(
            {
                "check_id": f"simulated_run_{idx:03d}",
                "phase_id": run.get("phase_id", "NOT_COMPUTABLE"),
                "source_workstream_id": run.get("source_workstream_id", "NOT_COMPUTABLE"),
                "simulated_only": run.get("simulated_only"),
                "repo_mutation_performed": run.get("repo_mutation_performed"),
                "valid_for_execution": run.get("valid_for_execution"),
                "passed": (
                    run.get("simulated_only") is True
                    and run.get("repo_mutation_performed") is False
                    and run.get("valid_for_execution") is False
                    and isinstance(run.get("impacted_count"), int)
                    and run.get("impacted_count", -1) >= 0
                    and bool(run.get("expected_outputs"))
                ),
            }
        )
    return checks


def _invariant_checks(source_dry_run: Mapping[str, Any]) -> list[dict[str, Any]]:
    checks = [
        ("dry_run_only", source_dry_run.get("dry_run_only"), True),
        ("advisory_only", source_dry_run.get("advisory_only"), True),
        ("projection_only", source_dry_run.get("projection_only"), True),
        ("non_authoritative", source_dry_run.get("non_authoritative"), True),
        ("implementation_authorized", source_dry_run.get("implementation_authorized"), False),
        ("execution_authority", source_dry_run.get("execution_authority"), False),
        ("valid_for_repair", source_dry_run.get("valid_for_repair"), False),
        ("valid_for_execution", source_dry_run.get("valid_for_execution"), False),
        ("simulated_workstream_count", source_dry_run.get("simulated_workstream_count"), 3),
    ]
    return [
        {
            "check_id": check_id,
            "observed": observed,
            "expected": expected,
            "passed": observed == expected,
        }
        for check_id, observed, expected in checks
    ]


def _validation_checks(
    source_dry_run_hash: str,
    source_implementation_plan_hash: str,
    source_dry_run: Mapping[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "check_id": "source_dry_run_hash_present",
            "passed": source_dry_run_hash != "NOT_COMPUTABLE",
        },
        {
            "check_id": "source_implementation_plan_hash_present",
            "passed": source_implementation_plan_hash != "NOT_COMPUTABLE",
        },
        {
            "check_id": "simulated_workstream_runs_present",
            "passed": bool(source_dry_run.get("simulated_workstream_runs")),
        },
        {
            "check_id": "not_computable_reasons_present",
            "passed": bool(source_dry_run.get("not_computable_reasons")),
        },
    ]


def build_abx_artifact_lineage_registry_direct_repair_validation_plan(
    *,
    repo_root: str | Path = ".",
    source_dry_run_path: str | Path = SOURCE_DRY_RUN_PATH,
    source_implementation_plan_path: str | Path = SOURCE_IMPLEMENTATION_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    dry_run_path = root / source_dry_run_path
    implementation_plan_path = root / source_implementation_plan_path
    source_dry_run = _load_json(dry_run_path)
    source_implementation_plan = _load_json(implementation_plan_path)

    source_dry_run_hash = _source_hash(dry_run_path)
    source_implementation_plan_hash = _source_hash(implementation_plan_path)
    dry_run_ready = (
        source_dry_run.get("artifact_type") == "AbxArtifactLineageRegistryDirectRepairImplementationDryRun.v1"
        and source_dry_run.get("dry_run_id")
        == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_IMPLEMENTATION_DRY_RUN_001"
        and source_dry_run.get("dry_run_status")
        == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_IMPLEMENTATION_DRY_RUN_READY"
    )
    implementation_plan_observed = (
        source_implementation_plan.get("artifact_type")
        == "AbxArtifactLineageRegistryDirectRepairImplementationPlan.v1"
        and source_implementation_plan.get("plan_id")
        == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_IMPLEMENTATION_PLAN_001"
    )

    simulation_checks = _simulation_checks(source_dry_run)
    invariant_checks = _invariant_checks(source_dry_run)
    validation_checks = _validation_checks(
        source_dry_run_hash, source_implementation_plan_hash, source_dry_run
    )

    blockers: list[str] = []
    if not dry_run_ready:
        blockers.append("SOURCE_DRY_RUN_NOT_READY")
    if not implementation_plan_observed:
        blockers.append("SOURCE_IMPLEMENTATION_PLAN_NOT_OBSERVED")
    blockers.extend(check["check_id"] for check in simulation_checks if not check["passed"])
    blockers.extend(check["check_id"] for check in invariant_checks if not check["passed"])
    blockers.extend(check["check_id"] for check in validation_checks if not check["passed"])

    status = (
        "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_VALIDATION_PLAN_READY"
        if not blockers
        else "NOT_COMPUTABLE"
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "status": status,
        "source_dry_run": source_dry_run.get("dry_run_id", "NOT_COMPUTABLE"),
        "source_dry_run_path": Path(source_dry_run_path).as_posix(),
        "source_dry_run_hash": source_dry_run_hash,
        "source_dry_run_observed": dry_run_ready,
        "source_implementation_plan": source_implementation_plan.get("plan_id", "NOT_COMPUTABLE"),
        "source_implementation_plan_path": Path(source_implementation_plan_path).as_posix(),
        "source_implementation_plan_hash": source_implementation_plan_hash,
        "source_implementation_plan_observed": implementation_plan_observed,
        "simulation_checks": simulation_checks,
        "invariant_checks": invariant_checks,
        "validation_checks": validation_checks,
        "blockers": sorted(blockers),
        "required_operator_actions": [
            "review_direct_repair_implementation_dry_run",
            "review_validation_plan_checks",
            "maintain_non_authoritative_validation_posture",
        ],
        "recommended_next_action": (
            "review the dry-run validation plan as an advisory-only verification surface; do not execute repairs from validation readiness alone"
            if status.endswith("_READY")
            else "repair direct repair validation-plan prerequisites before further lineage validation work"
        ),
        "recommended_next_plan": RECOMMENDED_NEXT_PLAN,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "governance_locks": _governance_locks(source_dry_run),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "validation_plan_only": True,
        "implementation_authorized": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "downstream": DOWNSTREAM,
    }
    return {**base, "packet_hash": canonical_hash(base)}


def render_markdown(plan: Mapping[str, Any]) -> str:
    lines = [
        "# ABX Artifact Lineage Registry Direct Repair Validation Plan",
        "",
        f"- `plan_id`: `{plan['plan_id']}`",
        f"- `status`: `{plan['status']}`",
        f"- `source_dry_run`: `{plan['source_dry_run']}`",
        f"- `source_implementation_plan`: `{plan['source_implementation_plan']}`",
        f"- `recommended_next_plan`: `{plan['recommended_next_plan']}`",
        f"- `downstream`: `{plan['downstream']}`",
        "",
        "## Blockers",
    ]
    for blocker in plan["blockers"]:
        lines.append(f"- `{blocker}`")
    return "\n".join(lines) + "\n"


def write_abx_artifact_lineage_registry_direct_repair_validation_plan(
    json_path: Path,
    md_path: Path,
) -> dict[str, Any]:
    plan = build_abx_artifact_lineage_registry_direct_repair_validation_plan()
    write_canonical_json(json_path, plan)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(plan), encoding="utf-8")
    return plan
