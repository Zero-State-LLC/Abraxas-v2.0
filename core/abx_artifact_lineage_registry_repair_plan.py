from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxArtifactLineageRegistryRepairPlan.v1"
PLAN_ID = "ABX_ARTIFACT_LINEAGE_REGISTRY_REPAIR_PLAN_001"
DETERMINISTIC_GENERATED_AT = "2026-06-05T00:00:00Z"
SOURCE_TRACEABILITY_AUDIT_PATH = "out/sync/abx_artifact_lineage_registry_traceability_audit/latest.json"
OUT_JSON = "out/sync/abx_artifact_lineage_registry_repair_plan/latest.json"
OUT_MD = "out/sync/abx_artifact_lineage_registry_repair_plan/latest.md"
DOWNSTREAM = "NOT_COMPUTABLE"
RECOMMENDED_NEXT_PLAN = "ABX_ARTIFACT_LINEAGE_REGISTRY_REPAIR_EXECUTION_PLAN_001"
NO_ACTIONABLE_REPAIR_PLAN = "NOT_COMPUTABLE"

FORBIDDEN_ACTIONS = [
    "implement_runtime_execution",
    "promote_research_to_canon",
    "mutate_governance",
    "grant_execution_authority",
    "rewrite_historical_artifacts_without_governed_evidence",
    "normalize_runner_casing_without_operator_review",
    "invent_missing_notion_mappings",
    "treat_repair_plan_as_completion_proof",
]

REPAIR_PHASES = [
    "CONSTRAIN_REPO_LOCAL_REPAIR_SCOPE",
    "GROUP_DIRECT_REPAIRABLE_DRIFT",
    "SEPARATE_OPERATOR_REVIEW_DEPENDENCIES",
    "SEPARATE_EXTERNAL_EVIDENCE_DEPENDENCIES",
    "PRESERVE_UNRESOLVED_ITEMS_AS_NOT_COMPUTABLE",
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


def _governance_locks(source_audit: Mapping[str, Any]) -> dict[str, Any]:
    return dict(source_audit.get("governance_locks", {}))


def _repair_batches(source_audit: Mapping[str, Any]) -> list[dict[str, Any]]:
    findings = {}
    for section in (
        "registry_findings",
        "runner_findings",
        "schema_findings",
        "output_findings",
        "docs_findings",
        "notion_mapping_findings",
    ):
        for finding in source_audit.get(section, []):
            findings[finding["finding_id"]] = finding

    return [
        {
            "batch_id": "REGISTRY_COVERAGE_REPAIR_BATCH",
            "batch_status": findings["detect_artifacts_with_outputs_but_no_registry_entry"]["status"],
            "repair_mode": "REPO_LOCAL_DIRECT_REPAIR_CANDIDATE",
            "source_finding_id": "detect_artifacts_with_outputs_but_no_registry_entry",
            "impacted_count": findings["detect_artifacts_with_outputs_but_no_registry_entry"]["impacted_count"],
            "sample_impacted": findings["detect_artifacts_with_outputs_but_no_registry_entry"]["sample_impacted"],
            "proposed_actions": [
                "classify_unregistered_latest_outputs_by artifact family",
                "separate intentionally unregistered latest outputs from missed registry entries",
                "add missing registry entries only where repo-local producer evidence is explicit",
            ],
        },
        {
            "batch_id": "MARKDOWN_JSON_PAIRING_REPAIR_BATCH",
            "batch_status": findings["detect_markdown_outputs_without_json_pair"]["status"],
            "repair_mode": "REPO_LOCAL_DIRECT_REPAIR_CANDIDATE",
            "source_finding_id": "detect_markdown_outputs_without_json_pair",
            "impacted_count": findings["detect_markdown_outputs_without_json_pair"]["impacted_count"],
            "sample_impacted": findings["detect_markdown_outputs_without_json_pair"]["sample_impacted"],
            "proposed_actions": [
                "separate json-only families from incomplete latest-pair drift",
                "add explicit single-format exceptions where repo convention allows them",
                "repair missing paired outputs only when a producer already exists",
            ],
        },
        {
            "batch_id": "DOCS_ARTIFACT_REFERENCE_REPAIR_BATCH",
            "batch_status": findings["detect_docs_references_to_missing_artifacts"]["status"],
            "repair_mode": "REPO_LOCAL_DIRECT_REPAIR_CANDIDATE",
            "source_finding_id": "detect_docs_references_to_missing_artifacts",
            "impacted_count": findings["detect_docs_references_to_missing_artifacts"]["impacted_count"],
            "sample_impacted": findings["detect_docs_references_to_missing_artifacts"]["sample_impacted"],
            "proposed_actions": [
                "confirm whether each missing path has a renamed or namespaced successor",
                "update docs references where the replacement is repo-provable",
                "leave unresolved docs references fail-closed when no replacement is provable",
            ],
        },
        {
            "batch_id": "RUNNER_CASING_POLICY_REVIEW_BATCH",
            "batch_status": findings["detect_uppercase_Scripts_runner_discovery_gaps"]["status"],
            "repair_mode": "OPERATOR_REVIEW_REQUIRED",
            "source_finding_id": "detect_uppercase_Scripts_runner_discovery_gaps",
            "impacted_count": findings["detect_uppercase_Scripts_runner_discovery_gaps"]["impacted_count"],
            "sample_impacted": findings["detect_uppercase_Scripts_runner_discovery_gaps"]["sample_impacted"],
            "proposed_actions": [
                "establish a canonical runner-path policy",
                "define whether lowercase scripts and uppercase Scripts remain dual-surface or are converged",
                "do not rename runner paths until the policy is explicitly governed",
            ],
        },
        {
            "batch_id": "NOTION_MAPPING_EVIDENCE_BATCH",
            "batch_status": findings["detect_generated_outputs_with_no_notion_surface"]["status"],
            "repair_mode": "EXTERNAL_EVIDENCE_REQUIRED",
            "source_finding_id": "detect_generated_outputs_with_no_notion_surface",
            "impacted_count": findings["detect_generated_outputs_with_no_notion_surface"]["impacted_count"],
            "sample_impacted": findings["detect_generated_outputs_with_no_notion_surface"]["sample_impacted"],
            "proposed_actions": [
                "collect deterministic Notion mapping evidence outside the repo",
                "import that evidence through a governed sync surface",
                "preserve these items as NOT_COMPUTABLE until the mapping evidence is repo-visible",
            ],
        },
    ]


def _unresolved_items(source_audit: Mapping[str, Any]) -> list[dict[str, Any]]:
    findings = {}
    for section in ("runner_findings", "notion_mapping_findings"):
        for finding in source_audit.get(section, []):
            findings[finding["finding_id"]] = finding

    unresolved = []
    if findings.get("detect_uppercase_Scripts_runner_discovery_gaps", {}).get("status") != "PASS":
        unresolved.append(
            {
                "item_id": "RUNNER_CASING_POLICY_DECISION",
                "status": "NOT_COMPUTABLE",
                "reason": "runner path overlap is real but requires governed policy, not unilateral repair",
            }
        )
    if findings.get("detect_generated_outputs_with_no_notion_surface", {}).get("status") != "PASS":
        unresolved.append(
            {
                "item_id": "NOTION_SURFACE_COMPLETENESS_PROOF",
                "status": "NOT_COMPUTABLE",
                "reason": "repo-local evidence still cannot prove Notion mapping completeness",
            }
        )
    unresolved.extend(
        [
            {
            "item_id": "FULL_ARTIFACT_LINEAGE_RECONCILIATION",
            "status": "NOT_COMPUTABLE",
            "reason": "this lane plans the repair batches but does not execute them or claim closure",
            },
            {
            "item_id": "REPAIR_EXECUTION_AUTHORITY",
            "status": "NOT_COMPUTABLE",
            "reason": "the repair plan does not authorize implementation, runtime execution, or governance mutation",
            },
        ]
    )
    return unresolved


def _active_batches(repair_batches: list[dict[str, Any]], repair_mode: str) -> list[str]:
    return [
        str(batch["batch_id"])
        for batch in repair_batches
        if batch["repair_mode"] == repair_mode and batch["batch_status"] != "PASS"
    ]


def build_abx_artifact_lineage_registry_repair_plan(
    *,
    repo_root: str | Path = ".",
    source_traceability_audit_path: str | Path = SOURCE_TRACEABILITY_AUDIT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_traceability_audit_path
    source_audit = _load_json(source_path)
    source_observed = (
        source_audit.get("artifact_type") == "AbxArtifactLineageRegistryTraceabilityAudit.v1"
        and source_audit.get("audit_id") == "ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_001"
        and source_audit.get("recommended_next_plan") == PLAN_ID
    )
    repair_batches = _repair_batches(source_audit)
    direct_repairable_batches = _active_batches(repair_batches, "REPO_LOCAL_DIRECT_REPAIR_CANDIDATE")
    operator_review_batches = _active_batches(repair_batches, "OPERATOR_REVIEW_REQUIRED")
    external_evidence_batches = _active_batches(repair_batches, "EXTERNAL_EVIDENCE_REQUIRED")
    active_repair_batch_count = (
        len(direct_repairable_batches) + len(operator_review_batches) + len(external_evidence_batches)
    )
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "source_traceability_audit": source_audit.get("audit_id", "NOT_COMPUTABLE"),
        "source_traceability_audit_path": Path(source_traceability_audit_path).as_posix(),
        "source_traceability_audit_hash": _source_hash(source_path),
        "source_traceability_audit_observed": source_observed,
        "repair_phases": REPAIR_PHASES,
        "repair_batches": repair_batches,
        "direct_repairable_batches": direct_repairable_batches,
        "operator_review_batches": operator_review_batches,
        "external_evidence_batches": external_evidence_batches,
        "active_repair_batch_count": active_repair_batch_count,
        "repair_execution_plan_applicable": bool(direct_repairable_batches),
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "governance_locks": _governance_locks(source_audit),
        "unresolved_items": _unresolved_items(source_audit),
        "recommended_next_plan": RECOMMENDED_NEXT_PLAN if direct_repairable_batches else NO_ACTIONABLE_REPAIR_PLAN,
        "downstream": DOWNSTREAM,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "valid_for_execution": False,
    }
    return {**base, "packet_hash": canonical_hash(base)}


def render_markdown(plan: Mapping[str, Any]) -> str:
    lines = [
        "# ABX Artifact Lineage Registry Repair Plan",
        "",
        f"- `plan_id`: `{plan['plan_id']}`",
        f"- `source_traceability_audit`: `{plan['source_traceability_audit']}`",
        f"- `recommended_next_plan`: `{plan['recommended_next_plan']}`",
        f"- `downstream`: `{plan['downstream']}`",
        f"- `canon_status`: `{plan['governance_locks']['canon_status']}`",
        "",
        "## Repair Batches",
    ]
    for batch in plan["repair_batches"]:
        lines.append(
            f"- `{batch['batch_id']}`: `{batch['batch_status']}` via `{batch['repair_mode']}` ({batch['impacted_count']} impacted)"
        )
    lines.extend(["", "## Unresolved Items"])
    for item in plan["unresolved_items"]:
        lines.append(f"- `{item['item_id']}`: `{item['status']}`")
    return "\n".join(lines) + "\n"


def write_abx_artifact_lineage_registry_repair_plan(json_path: Path, md_path: Path) -> dict[str, Any]:
    plan = build_abx_artifact_lineage_registry_repair_plan()
    write_canonical_json(json_path, plan)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(plan), encoding="utf-8")
    return plan
