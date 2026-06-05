from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxArtifactLineageRegistryDirectRepairImplementationPlan.v1"
PLAN_ID = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_IMPLEMENTATION_PLAN_001"
DETERMINISTIC_GENERATED_AT = "2026-06-05T00:00:00Z"
SOURCE_BATCH_PATH = "out/sync/abx_artifact_lineage_registry_direct_repair_batch/latest.json"
SOURCE_EXECUTION_PLAN_PATH = "out/sync/abx_artifact_lineage_registry_repair_execution_plan/latest.json"
OUT_JSON = "out/sync/abx_artifact_lineage_registry_direct_repair_implementation_plan/latest.json"
OUT_MD = "out/sync/abx_artifact_lineage_registry_direct_repair_implementation_plan/latest.md"
DOWNSTREAM = "NOT_COMPUTABLE"
RECOMMENDED_NEXT_PLAN = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_IMPLEMENTATION_DRY_RUN_001"

FORBIDDEN_ACTIONS = [
    "implement_runtime_execution",
    "promote_research_to_canon",
    "mutate_governance",
    "grant_execution_authority",
    "rewrite_generated_outputs_without_producer_proof",
    "auto_register_unclassified_artifacts",
    "normalize_runner_casing_without_operator_review",
    "infer_notion_evidence",
    "claim_implementation_plan_as_repair_completion",
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


def _governance_locks(source_batch: Mapping[str, Any]) -> dict[str, Any]:
    return dict(source_batch.get("governance_locks", {}))


def _phase_for_workstream(workstream: Mapping[str, Any]) -> dict[str, Any]:
    phase_map = {
        "DIRECT_REGISTRY_COVERAGE_CLASSIFICATION": {
            "phase_id": "DIRECT-IMPL-001",
            "title": "Registry coverage classification implementation",
            "implementation_scope": "classify missing registry coverage into add, keep-unmanaged, or defer buckets",
            "expected_outputs": [
                "classification ledger for registry coverage families",
                "repo-local keep/add/defer decision table",
            ],
        },
        "DIRECT_OUTPUT_PAIRING_CLASSIFICATION": {
            "phase_id": "DIRECT-IMPL-002",
            "title": "Markdown and JSON pairing classification implementation",
            "implementation_scope": "classify single-format latest surfaces into approved singleton vs incomplete pair buckets",
            "expected_outputs": [
                "pairing family classification ledger",
                "explicit singleton exemptions for repo-provable families",
            ],
        },
        "DIRECT_DOCS_REFERENCE_CLASSIFICATION": {
            "phase_id": "DIRECT-IMPL-003",
            "title": "Docs reference classification implementation",
            "implementation_scope": "classify stale docs references into repo-provable replacement vs unresolved hold buckets",
            "expected_outputs": [
                "docs reference replacement table",
                "unresolved docs reference hold ledger",
            ],
        },
    }
    template = phase_map[workstream["workstream_id"]]
    return {
        "phase_id": template["phase_id"],
        "phase_status": "PLANNED_ADVISORY_ONLY",
        "title": template["title"],
        "source_workstream_id": workstream["workstream_id"],
        "source_finding_id": workstream["source_finding_id"],
        "implementation_scope": template["implementation_scope"],
        "bounded_actions": list(workstream.get("bounded_actions", [])),
        "expected_outputs": template["expected_outputs"],
        "impacted_count": workstream.get("impacted_count", 0),
        "guardrails": [
            "preserve unresolved families as NOT_COMPUTABLE",
            "do not mutate generated outputs during planning",
            "do not treat repo-local proof gaps as repairable by inference",
        ],
    }


def _implementation_phases(source_batch: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [_phase_for_workstream(workstream) for workstream in source_batch.get("workstreams", [])]


def _acceptance_gates() -> list[dict[str, Any]]:
    return [
        {
            "gate_id": "DIRECT-PLAN-GATE-001",
            "gate_status": "PLANNING_ONLY",
            "required_before": "any direct repair implementation patch",
            "condition": "all three direct classification phases remain advisory-only and bounded",
        },
        {
            "gate_id": "DIRECT-PLAN-GATE-002",
            "gate_status": "AUTHORITY_DENIED",
            "required_before": "any runner casing change or Notion completeness claim",
            "condition": "runner policy and Notion evidence lanes remain out of scope and NOT_COMPUTABLE",
        },
        {
            "gate_id": "DIRECT-PLAN-GATE-003",
            "gate_status": "AUTHORITY_DENIED",
            "required_before": "any closure claim",
            "condition": "full lineage repair closure remains NOT_COMPUTABLE until later governed lanes exist",
        },
    ]


def _planned_step_sequence(source_batch: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "step_id": "DIRECT-STEP-001",
            "step_status": "READY",
            "phase_id": "DIRECT-IMPL-001",
            "action": "classify registry coverage families using repo-local producer evidence",
        },
        {
            "step_id": "DIRECT-STEP-002",
            "step_status": "READY",
            "phase_id": "DIRECT-IMPL-002",
            "action": "classify markdown/json pairing families without adding new generated outputs",
        },
        {
            "step_id": "DIRECT-STEP-003",
            "step_status": "READY",
            "phase_id": "DIRECT-IMPL-003",
            "action": "classify docs drift into repo-provable replacements and unresolved holds",
        },
        {
            "step_id": "DIRECT-STEP-004",
            "step_status": "NOT_COMPUTABLE",
            "phase_id": "DIRECT-IMPL-CLOSURE",
            "action": "full repair closure remains blocked pending later execution and external evidence lanes",
        },
    ]


def _unresolved_items() -> list[dict[str, Any]]:
    return [
        {
            "item_id": "DIRECT_REPAIR_PATCH_EXECUTION",
            "status": "NOT_COMPUTABLE",
            "reason": "this lane emits an implementation plan only and does not perform direct repairs",
        },
        {
            "item_id": "RUNNER_CASING_POLICY_DECISION",
            "status": "NOT_COMPUTABLE",
            "reason": "runner casing remains an operator-review hold outside this implementation plan",
        },
        {
            "item_id": "NOTION_MAPPING_EVIDENCE_IMPORT",
            "status": "NOT_COMPUTABLE",
            "reason": "external mapping evidence remains required and out of scope",
        },
        {
            "item_id": "FULL_LINEAGE_REPAIR_CLOSURE",
            "status": "NOT_COMPUTABLE",
            "reason": "closure requires later repair execution and unresolved evidence lanes",
        },
    ]


def build_abx_artifact_lineage_registry_direct_repair_implementation_plan(
    *,
    repo_root: str | Path = ".",
    source_batch_path: str | Path = SOURCE_BATCH_PATH,
    source_execution_plan_path: str | Path = SOURCE_EXECUTION_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    batch_path = root / source_batch_path
    execution_plan_path = root / source_execution_plan_path
    source_batch = _load_json(batch_path)
    source_execution_plan = _load_json(execution_plan_path)
    phases = _implementation_phases(source_batch)
    source_batch_observed = (
        source_batch.get("artifact_type") == "AbxArtifactLineageRegistryDirectRepairBatch.v1"
        and source_batch.get("batch_id") == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_BATCH_001"
        and source_batch.get("recommended_next_plan") == PLAN_ID
        and source_batch.get("direct_batch_ready") is True
    )
    source_execution_plan_observed = (
        source_execution_plan.get("artifact_type") == "AbxArtifactLineageRegistryRepairExecutionPlan.v1"
        and "DIRECT_REPAIR_BATCH_001" in source_execution_plan.get("ready_batches", [])
    )
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "source_batch": source_batch.get("batch_id", "NOT_COMPUTABLE"),
        "source_batch_path": Path(source_batch_path).as_posix(),
        "source_batch_hash": _source_hash(batch_path),
        "source_batch_observed": source_batch_observed,
        "source_execution_plan": source_execution_plan.get("plan_id", "NOT_COMPUTABLE"),
        "source_execution_plan_path": Path(source_execution_plan_path).as_posix(),
        "source_execution_plan_hash": _source_hash(execution_plan_path),
        "source_execution_plan_observed": source_execution_plan_observed,
        "implementation_scope": "REPO_LOCAL_DIRECT_REPAIR_CLASSIFICATION_IMPLEMENTATION_ONLY",
        "planned_step_sequence": _planned_step_sequence(source_batch),
        "implementation_phases": phases,
        "acceptance_gates": _acceptance_gates(),
        "ready_phase_ids": [phase["phase_id"] for phase in phases],
        "blocked_phase_ids": ["DIRECT-IMPL-CLOSURE"],
        "impacted_count_total": sum(phase["impacted_count"] for phase in phases),
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "governance_locks": _governance_locks(source_batch),
        "unresolved_items": _unresolved_items(),
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
        "# ABX Artifact Lineage Registry Direct Repair Implementation Plan",
        "",
        f"- `plan_id`: `{plan['plan_id']}`",
        f"- `source_batch`: `{plan['source_batch']}`",
        f"- `source_execution_plan`: `{plan['source_execution_plan']}`",
        f"- `implementation_scope`: `{plan['implementation_scope']}`",
        f"- `recommended_next_plan`: `{plan['recommended_next_plan']}`",
        f"- `downstream`: `{plan['downstream']}`",
        "",
        "## Implementation Phases",
    ]
    for phase in plan["implementation_phases"]:
        lines.append(
            f"- `{phase['phase_id']}`: `{phase['source_workstream_id']}` ({phase['impacted_count']} impacted)"
        )
    lines.extend(["", "## Unresolved Items"])
    for item in plan["unresolved_items"]:
        lines.append(f"- `{item['item_id']}`: `{item['status']}`")
    return "\n".join(lines) + "\n"


def write_abx_artifact_lineage_registry_direct_repair_implementation_plan(
    json_path: Path,
    md_path: Path,
) -> dict[str, Any]:
    plan = build_abx_artifact_lineage_registry_direct_repair_implementation_plan()
    write_canonical_json(json_path, plan)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(plan), encoding="utf-8")
    return plan
