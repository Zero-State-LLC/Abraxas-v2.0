from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxArtifactLineageRegistryRepairExecutionPlan.v1"
PLAN_ID = "ABX_ARTIFACT_LINEAGE_REGISTRY_REPAIR_EXECUTION_PLAN_001"
DETERMINISTIC_GENERATED_AT = "2026-06-05T00:00:00Z"
SOURCE_REPAIR_PLAN_PATH = "out/sync/abx_artifact_lineage_registry_repair_plan/latest.json"
OUT_JSON = "out/sync/abx_artifact_lineage_registry_repair_execution_plan/latest.json"
OUT_MD = "out/sync/abx_artifact_lineage_registry_repair_execution_plan/latest.md"
DOWNSTREAM = "NOT_COMPUTABLE"
RECOMMENDED_NEXT_PLAN = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_BATCH_001"

FORBIDDEN_ACTIONS = [
    "implement_runtime_execution",
    "promote_research_to_canon",
    "mutate_governance",
    "grant_execution_authority",
    "normalize_runner_casing_without_operator_review",
    "resolve_external_evidence_gaps_without_imported_evidence",
    "treat_execution_plan_as_repair_completion",
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


def _execution_batches(source_plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    batches_by_id = {batch["batch_id"]: batch for batch in source_plan.get("repair_batches", [])}
    execution_batches = [
        {
            "batch_id": "DIRECT_REPAIR_BATCH_001",
            "batch_status": "PLANNED",
            "repair_scope": "REPO_LOCAL_DIRECT_REPAIR_CANDIDATE",
            "source_batch_ids": [
                "REGISTRY_COVERAGE_REPAIR_BATCH",
                "MARKDOWN_JSON_PAIRING_REPAIR_BATCH",
                "DOCS_ARTIFACT_REFERENCE_REPAIR_BATCH",
            ],
            "blocking_dependencies": [],
            "planned_steps": [
                "classify registry coverage drift into missing registry entries vs intentionally unmanaged latest outputs",
                "classify markdown/json pairing drift into missing pairs vs approved single-format families",
                "classify docs references into stale paths with provable replacements vs unresolved missing surfaces",
            ],
            "guardrails": [
                "do not rewrite generated artifacts unless a current producer already exists",
                "do not rename runner paths",
                "preserve unresolved items as NOT_COMPUTABLE",
            ],
            "expected_outputs": [
                "repair classification ledger for direct repairable drift",
                "explicit keep/defer recommendations per direct repair family",
            ],
            "impacted_count_estimate": sum(
                batches_by_id[batch_id]["impacted_count"]
                for batch_id in (
                    "REGISTRY_COVERAGE_REPAIR_BATCH",
                    "MARKDOWN_JSON_PAIRING_REPAIR_BATCH",
                    "DOCS_ARTIFACT_REFERENCE_REPAIR_BATCH",
                )
                if batch_id in batches_by_id
            ),
        },
    ]
    if batches_by_id.get("RUNNER_CASING_POLICY_REVIEW_BATCH", {}).get("batch_status") != "PASS":
        execution_batches.append(
            {
                "batch_id": "RUNNER_POLICY_HOLD_BATCH_001",
                "batch_status": "NOT_COMPUTABLE",
                "repair_scope": "OPERATOR_REVIEW_REQUIRED",
                "source_batch_ids": ["RUNNER_CASING_POLICY_REVIEW_BATCH"],
                "blocking_dependencies": ["CANONICAL_RUNNER_PATH_POLICY_DECISION"],
                "planned_steps": [
                    "prepare a governed operator-facing summary of dual-surface runner overlap",
                    "do not perform casing convergence without explicit policy evidence",
                ],
                "guardrails": [
                    "no unilateral Scripts/scripts normalization",
                    "no runner-path deletion",
                ],
                "expected_outputs": [
                    "operator review packet or future policy record",
                ],
                "impacted_count_estimate": batches_by_id.get("RUNNER_CASING_POLICY_REVIEW_BATCH", {}).get(
                    "impacted_count", 0
                ),
            }
        )
    if batches_by_id.get("NOTION_MAPPING_EVIDENCE_BATCH", {}).get("batch_status") != "PASS":
        execution_batches.append(
            {
                "batch_id": "NOTION_EVIDENCE_HOLD_BATCH_001",
                "batch_status": "NOT_COMPUTABLE",
                "repair_scope": "EXTERNAL_EVIDENCE_REQUIRED",
                "source_batch_ids": ["NOTION_MAPPING_EVIDENCE_BATCH"],
                "blocking_dependencies": ["GOVERNED_NOTION_MAPPING_EVIDENCE_IMPORT"],
                "planned_steps": [
                    "collect governed Notion mapping evidence outside the repo",
                    "import that evidence through a deterministic sync surface before any closure claim",
                ],
                "guardrails": [
                    "do not infer Notion completeness from repo-local paths alone",
                    "preserve these families as NOT_COMPUTABLE until evidence is imported",
                ],
                "expected_outputs": [
                    "future sync artifact carrying Notion mapping evidence",
                ],
                "impacted_count_estimate": batches_by_id.get("NOTION_MAPPING_EVIDENCE_BATCH", {}).get(
                    "impacted_count", 0
                ),
            }
        )
    return execution_batches


def _execution_sequence(execution_batches: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    blocked_batch_ids = {str(batch["batch_id"]) for batch in execution_batches if batch["batch_status"] == "NOT_COMPUTABLE"}
    sequence = [
        {
            "step_id": "SEQ_001_DIRECT_REPAIR_CLASSIFICATION",
            "step_status": "READY",
            "batch_id": "DIRECT_REPAIR_BATCH_001",
            "why_now": "repo-local direct-repair candidates can be classified without waiting on operator or external evidence",
        },
    ]
    if "RUNNER_POLICY_HOLD_BATCH_001" in blocked_batch_ids:
        sequence.append(
            {
                "step_id": "SEQ_002_RUNNER_POLICY_REVIEW",
                "step_status": "NOT_COMPUTABLE",
                "batch_id": "RUNNER_POLICY_HOLD_BATCH_001",
                "why_now": "blocked pending canonical runner-path policy evidence",
            }
        )
    if "NOTION_EVIDENCE_HOLD_BATCH_001" in blocked_batch_ids:
        sequence.append(
            {
                "step_id": "SEQ_003_NOTION_MAPPING_EVIDENCE",
                "step_status": "NOT_COMPUTABLE",
                "batch_id": "NOTION_EVIDENCE_HOLD_BATCH_001",
                "why_now": "blocked pending governed external mapping evidence",
            }
        )
    return sequence


def _unresolved_items(source_plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    unresolved = [
        {
            "item_id": "DIRECT_REPAIR_BATCH_EXECUTION",
            "status": "NOT_COMPUTABLE",
            "reason": "this lane defines execution order and guardrails but does not perform the repairs",
        },
        {
            "item_id": "FULL_LINEAGE_REPAIR_CLOSURE",
            "status": "NOT_COMPUTABLE",
            "reason": "repair closure depends on later direct repair execution and unresolved evidence lanes",
        },
    ]
    unresolved_item_ids = {str(item.get("item_id")) for item in source_plan.get("unresolved_items", [])}
    if "RUNNER_CASING_POLICY_DECISION" in unresolved_item_ids:
        unresolved.append(
            {
                "item_id": "RUNNER_CASING_POLICY_DECISION",
                "status": "NOT_COMPUTABLE",
                "reason": "requires governed operator review",
            }
        )
    if "NOTION_SURFACE_COMPLETENESS_PROOF" in unresolved_item_ids:
        unresolved.append(
            {
                "item_id": "NOTION_MAPPING_EVIDENCE_IMPORT",
                "status": "NOT_COMPUTABLE",
                "reason": "requires external governed evidence import",
            }
        )
    return unresolved


def build_abx_artifact_lineage_registry_repair_execution_plan(
    *,
    repo_root: str | Path = ".",
    source_repair_plan_path: str | Path = SOURCE_REPAIR_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_repair_plan_path
    source_plan = _load_json(source_path)
    source_observed = (
        source_plan.get("artifact_type") == "AbxArtifactLineageRegistryRepairPlan.v1"
        and source_plan.get("plan_id") == "ABX_ARTIFACT_LINEAGE_REGISTRY_REPAIR_PLAN_001"
        and source_plan.get("recommended_next_plan") == PLAN_ID
    )
    execution_batches = _execution_batches(source_plan)
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "source_repair_plan": source_plan.get("plan_id", "NOT_COMPUTABLE"),
        "source_repair_plan_path": Path(source_repair_plan_path).as_posix(),
        "source_repair_plan_hash": _source_hash(source_path),
        "source_repair_plan_observed": source_observed,
        "execution_batches": execution_batches,
        "execution_sequence": _execution_sequence(execution_batches),
        "ready_batches": [
            batch["batch_id"] for batch in execution_batches if batch["batch_status"] == "PLANNED"
        ],
        "blocked_batches": [
            batch["batch_id"] for batch in execution_batches if batch["batch_status"] == "NOT_COMPUTABLE"
        ],
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "governance_locks": _governance_locks(source_plan),
        "unresolved_items": _unresolved_items(source_plan),
        "recommended_next_plan": RECOMMENDED_NEXT_PLAN,
        "downstream": DOWNSTREAM,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "valid_for_execution": False,
    }
    return {**base, "packet_hash": canonical_hash(base)}


def render_markdown(plan: Mapping[str, Any]) -> str:
    lines = [
        "# ABX Artifact Lineage Registry Repair Execution Plan",
        "",
        f"- `plan_id`: `{plan['plan_id']}`",
        f"- `source_repair_plan`: `{plan['source_repair_plan']}`",
        f"- `recommended_next_plan`: `{plan['recommended_next_plan']}`",
        f"- `downstream`: `{plan['downstream']}`",
        f"- `canon_status`: `{plan['governance_locks']['canon_status']}`",
        "",
        "## Execution Batches",
    ]
    for batch in plan["execution_batches"]:
        lines.append(
            f"- `{batch['batch_id']}`: `{batch['batch_status']}` via `{batch['repair_scope']}` ({batch['impacted_count_estimate']} impacted est.)"
        )
    lines.extend(["", "## Unresolved Items"])
    for item in plan["unresolved_items"]:
        lines.append(f"- `{item['item_id']}`: `{item['status']}`")
    return "\n".join(lines) + "\n"


def write_abx_artifact_lineage_registry_repair_execution_plan(json_path: Path, md_path: Path) -> dict[str, Any]:
    plan = build_abx_artifact_lineage_registry_repair_execution_plan()
    write_canonical_json(json_path, plan)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(plan), encoding="utf-8")
    return plan
