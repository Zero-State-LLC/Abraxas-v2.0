from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxArtifactLineageRegistryDirectRepairBatch.v1"
BATCH_ID = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_BATCH_001"
DETERMINISTIC_GENERATED_AT = "2026-06-05T00:00:00Z"
SOURCE_EXECUTION_PLAN_PATH = "out/sync/abx_artifact_lineage_registry_repair_execution_plan/latest.json"
SOURCE_TRACEABILITY_AUDIT_PATH = "out/sync/abx_artifact_lineage_registry_traceability_audit/latest.json"
OUT_JSON = "out/sync/abx_artifact_lineage_registry_direct_repair_batch/latest.json"
OUT_MD = "out/sync/abx_artifact_lineage_registry_direct_repair_batch/latest.md"
DOWNSTREAM = "NOT_COMPUTABLE"
RECOMMENDED_NEXT_PLAN = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_IMPLEMENTATION_PLAN_001"

FORBIDDEN_ACTIONS = [
    "implement_runtime_execution",
    "promote_research_to_canon",
    "mutate_governance",
    "grant_execution_authority",
    "repair_runner_casing_policy",
    "infer_notion_evidence",
    "claim_direct_repair_batch_as_closure",
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


def _find_finding(source_audit: Mapping[str, Any], finding_id: str) -> dict[str, Any]:
    for section in (
        "registry_findings",
        "runner_findings",
        "schema_findings",
        "output_findings",
        "docs_findings",
        "notion_mapping_findings",
    ):
        for finding in source_audit.get(section, []):
            if finding.get("finding_id") == finding_id:
                return finding
    return {}


def _workstreams(source_audit: Mapping[str, Any]) -> list[dict[str, Any]]:
    registry = _find_finding(source_audit, "detect_artifacts_with_outputs_but_no_registry_entry")
    pairing = _find_finding(source_audit, "detect_markdown_outputs_without_json_pair")
    docs = _find_finding(source_audit, "detect_docs_references_to_missing_artifacts")
    return [
        {
            "workstream_id": "DIRECT_REGISTRY_COVERAGE_CLASSIFICATION",
            "status": "PLANNED",
            "source_finding_id": "detect_artifacts_with_outputs_but_no_registry_entry",
            "impacted_count": registry.get("impacted_count", 0),
            "sample_impacted": registry.get("sample_impacted", []),
            "classification_goal": "separate intentionally unmanaged latest outputs from true missing registry coverage",
            "bounded_actions": [
                "group output artifacts by top-level family",
                "mark likely json-only or review-only surfaces for explicit keep/defer review",
                "identify registry additions only where producer evidence is already repo-local and deterministic",
            ],
        },
        {
            "workstream_id": "DIRECT_OUTPUT_PAIRING_CLASSIFICATION",
            "status": "PLANNED",
            "source_finding_id": "detect_markdown_outputs_without_json_pair",
            "impacted_count": pairing.get("impacted_count", 0),
            "sample_impacted": pairing.get("sample_impacted", []),
            "classification_goal": "separate approved single-format latest surfaces from incomplete pair drift",
            "bounded_actions": [
                "group pairing drift by family",
                "detect likely json-only latest patterns",
                "mark unresolved families for explicit keep/defer review instead of auto-repair",
            ],
        },
        {
            "workstream_id": "DIRECT_DOCS_REFERENCE_CLASSIFICATION",
            "status": "PLANNED",
            "source_finding_id": "detect_docs_references_to_missing_artifacts",
            "impacted_count": docs.get("impacted_count", 0),
            "sample_impacted": docs.get("sample_impacted", []),
            "classification_goal": "separate repo-provable stale references from unresolved missing-surface references",
            "bounded_actions": [
                "group docs drift by source document",
                "mark references to renamed or namespaced families as direct-repair candidates only when repo-proof exists",
                "leave unresolved references fail-closed",
            ],
        },
    ]


def _classification_ledger(source_audit: Mapping[str, Any]) -> list[dict[str, Any]]:
    registry = _find_finding(source_audit, "detect_artifacts_with_outputs_but_no_registry_entry")
    pairing = _find_finding(source_audit, "detect_markdown_outputs_without_json_pair")
    docs = _find_finding(source_audit, "detect_docs_references_to_missing_artifacts")
    return [
        {
            "ledger_entry_id": "REGISTRY_DRIFT_LEDGER",
            "status": "DIRECT_REPAIRABLE_CLASSIFICATION_READY",
            "source_finding_id": "detect_artifacts_with_outputs_but_no_registry_entry",
            "observed_impacted_count": registry.get("impacted_count", 0),
            "next_operator_free_step": "classify output families before any registry mutation proposal",
        },
        {
            "ledger_entry_id": "PAIRING_DRIFT_LEDGER",
            "status": "DIRECT_REPAIRABLE_CLASSIFICATION_READY",
            "source_finding_id": "detect_markdown_outputs_without_json_pair",
            "observed_impacted_count": pairing.get("impacted_count", 0),
            "next_operator_free_step": "classify single-format exceptions before any generated artifact proposal",
        },
        {
            "ledger_entry_id": "DOCS_DRIFT_LEDGER",
            "status": "DIRECT_REPAIRABLE_CLASSIFICATION_READY",
            "source_finding_id": "detect_docs_references_to_missing_artifacts",
            "observed_impacted_count": docs.get("impacted_count", 0),
            "next_operator_free_step": "classify stale references with repo-provable replacements before any docs patch",
        },
    ]


def _unresolved_items() -> list[dict[str, Any]]:
    return [
        {
            "item_id": "DIRECT_REPAIR_IMPLEMENTATION",
            "status": "NOT_COMPUTABLE",
            "reason": "this lane classifies direct-repairable drift but does not implement the fixes",
        },
        {
            "item_id": "FULL_LINEAGE_REPAIR_CLOSURE",
            "status": "NOT_COMPUTABLE",
            "reason": "classification alone is not closure; later implementation and evidence lanes remain required",
        },
    ]


def build_abx_artifact_lineage_registry_direct_repair_batch(
    *,
    repo_root: str | Path = ".",
    source_execution_plan_path: str | Path = SOURCE_EXECUTION_PLAN_PATH,
    source_traceability_audit_path: str | Path = SOURCE_TRACEABILITY_AUDIT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    execution_plan_path = root / source_execution_plan_path
    traceability_audit_path = root / source_traceability_audit_path
    source_plan = _load_json(execution_plan_path)
    source_audit = _load_json(traceability_audit_path)
    source_plan_observed = (
        source_plan.get("artifact_type") == "AbxArtifactLineageRegistryRepairExecutionPlan.v1"
        and source_plan.get("plan_id") == "ABX_ARTIFACT_LINEAGE_REGISTRY_REPAIR_EXECUTION_PLAN_001"
        and source_plan.get("recommended_next_plan") == BATCH_ID
    )
    batch_ready = "DIRECT_REPAIR_BATCH_001" in source_plan.get("ready_batches", [])
    workstreams = _workstreams(source_audit)
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "batch_id": BATCH_ID,
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "source_execution_plan": source_plan.get("plan_id", "NOT_COMPUTABLE"),
        "source_execution_plan_path": Path(source_execution_plan_path).as_posix(),
        "source_execution_plan_hash": _source_hash(execution_plan_path),
        "source_execution_plan_observed": source_plan_observed,
        "source_traceability_audit": source_audit.get("audit_id", "NOT_COMPUTABLE"),
        "source_traceability_audit_path": Path(source_traceability_audit_path).as_posix(),
        "source_traceability_audit_hash": _source_hash(traceability_audit_path),
        "direct_batch_ready": batch_ready,
        "workstreams": workstreams,
        "classification_ledger": _classification_ledger(source_audit),
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "governance_locks": _governance_locks(source_plan),
        "unresolved_items": _unresolved_items(),
        "recommended_next_plan": RECOMMENDED_NEXT_PLAN,
        "downstream": DOWNSTREAM,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "valid_for_execution": False,
    }
    return {**base, "packet_hash": canonical_hash(base)}


def render_markdown(batch: Mapping[str, Any]) -> str:
    lines = [
        "# ABX Artifact Lineage Registry Direct Repair Batch",
        "",
        f"- `batch_id`: `{batch['batch_id']}`",
        f"- `source_execution_plan`: `{batch['source_execution_plan']}`",
        f"- `recommended_next_plan`: `{batch['recommended_next_plan']}`",
        f"- `downstream`: `{batch['downstream']}`",
        f"- `direct_batch_ready`: `{batch['direct_batch_ready']}`",
        "",
        "## Workstreams",
    ]
    for workstream in batch["workstreams"]:
        lines.append(
            f"- `{workstream['workstream_id']}`: `{workstream['status']}` ({workstream['impacted_count']} impacted)"
        )
    lines.extend(["", "## Unresolved Items"])
    for item in batch["unresolved_items"]:
        lines.append(f"- `{item['item_id']}`: `{item['status']}`")
    return "\n".join(lines) + "\n"


def write_abx_artifact_lineage_registry_direct_repair_batch(json_path: Path, md_path: Path) -> dict[str, Any]:
    batch = build_abx_artifact_lineage_registry_direct_repair_batch()
    write_canonical_json(json_path, batch)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(batch), encoding="utf-8")
    return batch
