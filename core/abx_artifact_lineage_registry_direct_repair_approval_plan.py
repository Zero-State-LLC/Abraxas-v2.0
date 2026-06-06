from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxArtifactLineageRegistryDirectRepairApprovalPlan.v1"
APPROVAL_PLAN_ID = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_APPROVAL_PLAN_001"
DETERMINISTIC_GENERATED_AT = "2026-06-05T00:00:00Z"
SOURCE_VALIDATION_DRY_RUN_PATH = "out/sync/abx_artifact_lineage_registry_direct_repair_validation_dry_run/latest.json"
OUT_JSON = "out/sync/abx_artifact_lineage_registry_direct_repair_approval_plan/latest.json"
OUT_MD = "out/sync/abx_artifact_lineage_registry_direct_repair_approval_plan/latest.md"
DOWNSTREAM = "NOT_COMPUTABLE"
RECOMMENDED_NEXT_PLAN = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_APPROVAL_DRY_RUN_001"

FORBIDDEN_ACTIONS = [
    "execute_direct_repairs",
    "grant_repair_authority",
    "grant_execution_authority",
    "mutate_governance",
    "normalize_runner_casing_without_operator_review",
    "infer_notion_evidence",
    "treat_approval_plan_as_approval_record",
    "treat_approval_readiness_as_repair_completion",
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


def build_abx_artifact_lineage_registry_direct_repair_approval_plan(
    *,
    repo_root: str | Path = ".",
    source_validation_dry_run_path: str | Path = SOURCE_VALIDATION_DRY_RUN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    dry_run_path = root / source_validation_dry_run_path
    source_dry_run = _load_json(dry_run_path)

    source_validation_dry_run_hash = _source_hash(dry_run_path)
    source_validation_dry_run_observed = (
        source_dry_run.get("artifact_type") == "AbxArtifactLineageRegistryDirectRepairValidationDryRun.v1"
        and source_dry_run.get("dry_run_id") == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_VALIDATION_DRY_RUN_001"
        and source_dry_run.get("status") == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_VALIDATION_DRY_RUN_READY"
    )
    validation_passed = bool(source_dry_run.get("validation_passed", False))

    blockers: list[str] = []
    if not source_validation_dry_run_observed:
        blockers.append("SOURCE_VALIDATION_DRY_RUN_NOT_READY")
    if source_validation_dry_run_observed and not validation_passed:
        blockers.append("SOURCE_VALIDATION_DRY_RUN_FAILED")

    status = (
        "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_APPROVAL_PLAN_READY"
        if not blockers and validation_passed
        else "NOT_COMPUTABLE"
    )

    required_operator_acknowledgements = [
        "ack_advisory_only_non_authoritative_surface",
        "ack_direct_repair_scope_is_repo_local_only",
        "ack_runner_casing_policy_remains_out_of_scope",
        "ack_notion_mapping_evidence_remains_not_computable",
        "ack_no_repair_or_execution_authority_is_granted",
    ]
    required_operator_approval_fields = [
        "operator_id",
        "operator_name",
        "operator_role",
        "approval_timestamp_utc",
        "approval_scope_acknowledged",
        "approval_rationale",
    ]
    approval_constraints = [
        "approval_plan_only_no_execution",
        "no_registry_mutation_from_plan_alone",
        "no_output_pairing_repair_from_plan_alone",
        "no_docs_reference_repair_from_plan_alone",
        "no_runner_policy_override",
        "no_notion_evidence_import",
    ]
    approval_provenance_requirements = [
        "source_validation_dry_run_path_must_match",
        "source_validation_dry_run_hash_must_match",
        "source_validation_dry_run_status_must_be_ready",
        "validation_passed_must_remain_true",
    ]
    approval_hash_requirements = [
        "approval_plan_hash_must_match",
        "source_validation_dry_run_hash_must_match",
        "canonical_json_sha256_required",
    ]

    ready_workstreams = list(source_dry_run.get("simulation_results", []))
    validation_results = list(source_dry_run.get("validation_results", []))
    source_validation_blockers = list(source_dry_run.get("validation_blockers", []))

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "approval_plan_id": APPROVAL_PLAN_ID,
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "status": status,
        "source_validation_dry_run": source_dry_run.get("dry_run_id", "NOT_COMPUTABLE"),
        "source_validation_dry_run_path": Path(source_validation_dry_run_path).as_posix(),
        "source_validation_dry_run_hash": source_validation_dry_run_hash,
        "source_validation_dry_run_observed": source_validation_dry_run_observed,
        "source_validation_dry_run_status": source_dry_run.get("status", "NOT_COMPUTABLE"),
        "validation_passed": validation_passed,
        "ready_workstreams": ready_workstreams,
        "validation_results": validation_results,
        "source_validation_blockers": source_validation_blockers,
        "required_operator_acknowledgements": required_operator_acknowledgements,
        "required_operator_approval_fields": required_operator_approval_fields,
        "approval_constraints": approval_constraints,
        "approval_provenance_requirements": approval_provenance_requirements,
        "approval_hash_requirements": approval_hash_requirements,
        "blockers": sorted(blockers),
        "required_operator_actions": [
            "review_direct_repair_validation_dry_run",
            "prepare_operator_approval_surface_only",
            "maintain_non_authoritative_direct_repair_boundary",
        ],
        "recommended_next_action": (
            "prepare only the operator approval surface for direct repair; do not execute registry, output-pairing, or docs-reference changes from approval readiness alone"
            if status.endswith("_READY")
            else "repair approval-plan prerequisites before further direct-repair review"
        ),
        "recommended_next_plan": RECOMMENDED_NEXT_PLAN,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "governance_locks": _source_governance_locks(source_dry_run),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "approval_plan_only": True,
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
        "# ABX Artifact Lineage Registry Direct Repair Approval Plan",
        "",
        f"- `approval_plan_id`: `{packet['approval_plan_id']}`",
        f"- `status`: `{packet['status']}`",
        f"- `source_validation_dry_run`: `{packet['source_validation_dry_run']}`",
        f"- `recommended_next_plan`: `{packet['recommended_next_plan']}`",
        f"- `validation_passed`: `{packet['validation_passed']}`",
        "",
        "## Approval Blockers",
    ]
    for blocker in packet["blockers"]:
        lines.append(f"- `{blocker}`")
    return "\n".join(lines) + "\n"


def write_abx_artifact_lineage_registry_direct_repair_approval_plan(
    json_path: Path,
    md_path: Path,
) -> dict[str, Any]:
    packet = build_abx_artifact_lineage_registry_direct_repair_approval_plan()
    write_canonical_json(json_path, packet)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(packet), encoding="utf-8")
    return packet
