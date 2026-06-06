from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxArtifactLineageRegistryDirectRepairImplementationDryRun.v1"
DRY_RUN_ID = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_IMPLEMENTATION_DRY_RUN_001"
DETERMINISTIC_GENERATED_AT = "2026-06-05T00:00:00Z"
SOURCE_IMPLEMENTATION_PLAN_PATH = (
    "out/sync/abx_artifact_lineage_registry_direct_repair_implementation_plan/latest.json"
)
SOURCE_BATCH_PATH = "out/sync/abx_artifact_lineage_registry_direct_repair_batch/latest.json"
OUT_JSON = "out/sync/abx_artifact_lineage_registry_direct_repair_implementation_dry_run/latest.json"
OUT_MD = "out/sync/abx_artifact_lineage_registry_direct_repair_implementation_dry_run/latest.md"
DOWNSTREAM = "NOT_COMPUTABLE"
RECOMMENDED_NEXT_PLAN = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_VALIDATION_PLAN_001"

FORBIDDEN_ACTIONS = [
    "implement_runtime_execution",
    "promote_research_to_canon",
    "mutate_governance",
    "grant_execution_authority",
    "rewrite_generated_outputs_without_producer_proof",
    "author_registry_mutations_from_dry_run_only",
    "normalize_runner_casing_without_operator_review",
    "infer_notion_evidence",
    "claim_dry_run_as_repair_completion",
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


def _simulated_workstream_runs(source_plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    for phase in source_plan.get("implementation_phases", []):
        runs.append(
            {
                "phase_id": phase.get("phase_id", "NOT_COMPUTABLE"),
                "source_workstream_id": phase.get("source_workstream_id", "NOT_COMPUTABLE"),
                "source_finding_id": phase.get("source_finding_id", "NOT_COMPUTABLE"),
                "dry_run_status": "SIMULATED_READY",
                "simulated_only": True,
                "repo_mutation_performed": False,
                "valid_for_execution": False,
                "classification_scope": phase.get("implementation_scope", "NOT_COMPUTABLE"),
                "expected_outputs": list(phase.get("expected_outputs", [])),
                "guardrails": list(phase.get("guardrails", [])),
                "impacted_count": phase.get("impacted_count", 0),
            }
        )
    return runs


def _not_computable_reasons(
    implementation_plan_ready: bool,
    source_batch_ready: bool,
    simulated_runs: list[dict[str, Any]],
) -> list[str]:
    reasons: list[str] = []
    if not implementation_plan_ready:
        reasons.append("DIRECT_REPAIR_IMPLEMENTATION_PLAN_NOT_READY")
    if not source_batch_ready:
        reasons.append("DIRECT_REPAIR_BATCH_NOT_READY")
    if not simulated_runs:
        reasons.append("SIMULATED_WORKSTREAM_RUNS_MISSING")
    reasons.extend(
        [
            "DIRECT_REPAIR_EXECUTION_NOT_APPROVED",
            "RUNNER_CASING_POLICY_OUT_OF_SCOPE",
            "NOTION_MAPPING_EVIDENCE_OUT_OF_SCOPE",
            "DRY_RUN_CANNOT_GRANT_REPAIR_CLOSURE",
        ]
    )
    return reasons


def build_abx_artifact_lineage_registry_direct_repair_implementation_dry_run(
    *,
    repo_root: str | Path = ".",
    source_implementation_plan_path: str | Path = SOURCE_IMPLEMENTATION_PLAN_PATH,
    source_batch_path: str | Path = SOURCE_BATCH_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    implementation_plan_path = root / source_implementation_plan_path
    batch_path = root / source_batch_path
    source_plan = _load_json(implementation_plan_path)
    source_batch = _load_json(batch_path)
    simulated_runs = _simulated_workstream_runs(source_plan)
    implementation_plan_ready = (
        source_plan.get("artifact_type") == "AbxArtifactLineageRegistryDirectRepairImplementationPlan.v1"
        and source_plan.get("plan_id") == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_IMPLEMENTATION_PLAN_001"
        and source_plan.get("recommended_next_plan") == DRY_RUN_ID
        and source_plan.get("valid_for_execution") is False
        and bool(simulated_runs)
    )
    source_batch_ready = (
        source_batch.get("artifact_type") == "AbxArtifactLineageRegistryDirectRepairBatch.v1"
        and source_batch.get("batch_id") == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_BATCH_001"
        and source_batch.get("direct_batch_ready") is True
    )
    dry_run_ready = implementation_plan_ready and source_batch_ready and bool(simulated_runs)

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "dry_run_id": DRY_RUN_ID,
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "dry_run_status": (
            "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_IMPLEMENTATION_DRY_RUN_READY"
            if dry_run_ready
            else "NOT_COMPUTABLE"
        ),
        "source_implementation_plan": source_plan.get("plan_id", "NOT_COMPUTABLE"),
        "source_implementation_plan_path": Path(source_implementation_plan_path).as_posix(),
        "source_implementation_plan_hash": _source_hash(implementation_plan_path),
        "source_implementation_plan_observed": implementation_plan_ready,
        "source_batch": source_batch.get("batch_id", "NOT_COMPUTABLE"),
        "source_batch_path": Path(source_batch_path).as_posix(),
        "source_batch_hash": _source_hash(batch_path),
        "source_batch_observed": source_batch_ready,
        "simulated_workstream_runs": simulated_runs,
        "simulated_workstream_count": len(simulated_runs),
        "required_operator_actions": [
            "review_direct_repair_implementation_plan",
            "review_simulated_workstream_runs",
            "maintain_runner_policy_and_notion_evidence_holds",
        ],
        "recommended_next_action": (
            "review the direct repair implementation dry run as a simulated classification sequence only; do not execute repairs from this surface"
            if dry_run_ready
            else "repair direct repair implementation dry-run prerequisites before further lineage planning"
        ),
        "recommended_next_plan": RECOMMENDED_NEXT_PLAN,
        "safe_to_prepare_planning_pr": False,
        "safe_to_prepare_implementation_pr": False,
        "safe_to_auto_continue": False,
        "repair_execution_performed": False,
        "implementation_authorized": False,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "governance_locks": _governance_locks(source_plan),
        "not_computable_reasons": _not_computable_reasons(
            implementation_plan_ready, source_batch_ready, simulated_runs
        ),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "dry_run_only": True,
        "execution_authority": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "downstream": DOWNSTREAM,
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_artifact_lineage_registry_direct_repair_implementation_dry_run(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)


def write_abx_artifact_lineage_registry_direct_repair_implementation_dry_run_markdown(
    path: str | Path, packet: dict[str, Any]
) -> None:
    lines = [
        "# ABX Artifact Lineage Registry Direct Repair Implementation Dry Run",
        "",
        f"- `dry_run_id`: `{packet['dry_run_id']}`",
        f"- `dry_run_status`: `{packet['dry_run_status']}`",
        f"- `source_implementation_plan`: `{packet['source_implementation_plan']}`",
        f"- `source_batch`: `{packet['source_batch']}`",
        f"- `recommended_next_plan`: `{packet['recommended_next_plan']}`",
        f"- `valid_for_repair`: `{packet['valid_for_repair']}`",
        f"- `valid_for_execution`: `{packet['valid_for_execution']}`",
        "",
        "## Simulated Workstream Runs",
    ]
    for run in packet.get("simulated_workstream_runs", []):
        lines.append(f"- `{run['phase_id']}` -> `{run['source_workstream_id']}`")
    lines.extend(["", "## Not Computable Reasons"])
    for reason in packet.get("not_computable_reasons", []):
        lines.append(f"- `{reason}`")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
