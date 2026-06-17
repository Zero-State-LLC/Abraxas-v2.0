from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_foundation_backlog_plan import (
    PLAN_JSON_PATH as SOURCE_PHASE1_BACKLOG_JSON,
)

SCHEMA_VERSION = "V2HygienePhase2ModuleSkeletonBacklogPlan.v1"
PLAN_ID = "v2_hygiene_phase2_module_skeleton_backlog_plan_001"
PLAN_JSON_PATH = Path("out/sync/v2_hygiene_phase2_module_skeleton_backlog_plan/latest.json")
PLAN_MD_PATH = PLAN_JSON_PATH.with_suffix(".md")
NOT_COMPUTABLE = "NOT_COMPUTABLE"

SOURCE_OPERATOR_GATE_JSON = (
    "out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.json"
)
SOURCE_REGISTRATION_READINESS_JSON = "out/sync/v2_hygiene_registration_readiness_audit/latest.json"

NOTION_PHASE2_SOURCES: tuple[dict[str, str], ...] = (
    {
        "page_id": "37e3e8ba-2f5c-8100-8c1e-fff304c1f8d9",
        "title": "Phase 2: Module Skeletons & Governance Hooks",
        "status": "READY_FOR_ADVISORY_BACKLOG",
        "source_observed_at": "2026-06-13T16:43:43Z",
    },
    {
        "page_id": "37e3e8ba-2f5c-8170-b132-d06f5c8f0acd",
        "title": "Phase 3: Output Surface Integration",
        "status": "PLACEHOLDER_PLANNING_SURFACE",
        "source_observed_at": "2026-06-13T16:22:47Z",
    },
    {
        "page_id": "37e3e8ba-2f5c-81a7-a55b-da585d0fe220",
        "title": "Phase 4: Full Integration & Promotion",
        "status": "PLACEHOLDER_PLANNING_SURFACE",
        "source_observed_at": "2026-06-13T16:22:47Z",
    },
)

PHASE2_MODULES: tuple[dict[str, Any], ...] = (
    {
        "module_id": "retrocausal_signal_hygiene_module",
        "module_name": "Retrocausal Signal Hygiene Module",
        "owner_runes": ["LoopAwarenessRune", "HyperstitionTagRune"],
        "primary_responsibility": "Detect and tag retrocausal/hyperstitional risk in outputs",
        "initial_posture": "ADVISORY_ONLY",
        "planned_repo_path": "abraxas/v2/modules/retrocausal_hygiene",
    },
    {
        "module_id": "mandatory_output_schema_enforcer",
        "module_name": "Mandatory Output Schema Enforcer",
        "owner_runes": ["ProvenanceEnforceRune", "OutputRegisterEnforceRune"],
        "primary_responsibility": "Enforce three-register format and provenance requirements",
        "initial_posture": "ADVISORY_ONLY",
        "planned_repo_path": "abraxas/v2/modules/output_schema_enforcer",
    },
    {
        "module_id": "self_adversarial_testing_loop",
        "module_name": "Self-Adversarial Testing Loop",
        "owner_runes": ["AdversarialAuditRune"],
        "primary_responsibility": "Generate internal counter-arguments and confidence adjustments",
        "initial_posture": "ADVISORY_ONLY",
        "planned_repo_path": "abraxas/v2/modules/self_adversarial_loop",
    },
    {
        "module_id": "hyperstition_potency_evaluator",
        "module_name": "Hyperstition Potency Evaluator",
        "owner_runes": ["HyperstitionTagRune"],
        "primary_responsibility": (
            "Assess self-fulfilling potential of outputs and recommend mitigations"
        ),
        "initial_posture": "ADVISORY_ONLY",
        "planned_repo_path": "abraxas/v2/modules/hyperstition_evaluator",
    },
)

PHASE2_DELIVERABLES: tuple[dict[str, str], ...] = (
    {
        "deliverable_id": "phase2_high_001",
        "priority": "HIGH",
        "deliverable": "Four module skeleton classes",
        "description": "Basic structure with mode support for each v2 module",
        "planned_repo_path": "abraxas/v2/modules",
    },
    {
        "deliverable_id": "phase2_high_002",
        "priority": "HIGH",
        "deliverable": "Module configuration pattern",
        "description": "How to enable/disable or change mode per module",
        "planned_repo_path": "abraxas/v2/modules/*/config.py",
    },
    {
        "deliverable_id": "phase2_medium_003",
        "priority": "MEDIUM",
        "deliverable": "Integration with HygienePipeline",
        "description": "Show how modules can use the pipeline without gaining authority",
        "planned_repo_path": "abraxas/v2/modules/*/module.py",
    },
    {
        "deliverable_id": "phase2_medium_004",
        "priority": "MEDIUM",
        "deliverable": "Promotion criteria documentation",
        "description": "What is required to promote a module out of advisory",
        "planned_repo_path": "docs/v2_hygiene/module_promotion_criteria.md",
    },
    {
        "deliverable_id": "phase2_medium_005",
        "priority": "MEDIUM",
        "deliverable": "Basic tests for each module skeleton",
        "description": "Ensure module skeletons respect mode and authority boundaries",
        "planned_repo_path": "tests/v2/modules",
    },
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _hash_source(path: Path) -> str:
    value = _read_json(path)
    return canonical_hash(value) if value else NOT_COMPUTABLE


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _notion_source_records() -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for source in NOTION_PHASE2_SOURCES:
        record = dict(source)
        record["source_hash"] = canonical_hash(source)
        records.append(record)
    return records


def _authority_locks() -> dict[str, bool]:
    return {
        "activation": False,
        "auto_continuation": False,
        "auto_patch_generation": False,
        "canon_mutation": False,
        "execution_authority": False,
        "github_writeback": False,
        "hygiene_pipeline_integration": False,
        "implementation_authorization": False,
        "module_code_creation": False,
        "module_registration": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_authorization_record_creation": False,
        "projection_surface_mutation": False,
        "queue_mutation": False,
        "rune_binding_mutation": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "strict_mode_enablement": False,
        "test_file_creation": False,
        "token_minting": False,
        "v2_module_registration": False,
    }


def _module_records(repo_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for module in PHASE2_MODULES:
        target = repo_root / str(module["planned_repo_path"])
        repo_observed = target.exists()
        records.append(
            {
                **module,
                "repo_observed": repo_observed,
                "implementation_status": (
                    "REPO_PATH_OBSERVED_HELD_FOR_OPERATOR"
                    if repo_observed
                    else "NOTION_MODULE_TO_DO_HELD_FOR_OPERATOR"
                ),
                "module_creation_authorized": False,
                "module_registration_authorized": False,
                "execution_authority": False,
            }
        )
    return records


def _deliverable_records(repo_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for deliverable in PHASE2_DELIVERABLES:
        target = repo_root / deliverable["planned_repo_path"].replace("*", "retrocausal_hygiene")
        repo_observed = target.exists()
        records.append(
            {
                **deliverable,
                "repo_observed": repo_observed,
                "implementation_status": (
                    "REPO_PATH_OBSERVED_HELD_FOR_OPERATOR"
                    if repo_observed
                    else "NOTION_DELIVERABLE_TO_DO_HELD_FOR_OPERATOR"
                ),
                "implementation_authorized": False,
                "execution_authority": False,
            }
        )
    return records


def build_v2_hygiene_phase2_module_skeleton_backlog_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    source_paths = {
        "phase1_foundation_backlog_plan": str(SOURCE_PHASE1_BACKLOG_JSON),
        "operator_authorization_gate": SOURCE_OPERATOR_GATE_JSON,
        "registration_readiness_audit": SOURCE_REGISTRATION_READINESS_JSON,
    }
    source_packets = {key: _read_json(root / path) for key, path in source_paths.items()}
    phase1 = source_packets["phase1_foundation_backlog_plan"] or {}
    gate = source_packets["operator_authorization_gate"] or {}
    registration = source_packets["registration_readiness_audit"] or {}
    source_ready = (
        phase1.get("status") == "V2_HYGIENE_PHASE1_FOUNDATION_BACKLOG_PLAN_READY"
        and phase1.get("implementation_authorized") is False
        and gate.get("authorization_granted") is False
        and gate.get("valid_for_implementation") is False
        and registration.get("valid_for_implementation") is False
        and registration.get("v2_module_registration_authorized") is False
    )
    module_records = _module_records(root)
    deliverable_records = _deliverable_records(root)
    blocked_module_count = sum(
        1 for module in module_records if module["module_creation_authorized"] is False
    )
    blocked_deliverable_count = sum(
        1
        for deliverable in deliverable_records
        if deliverable["implementation_authorized"] is False
    )
    blockers = [] if source_ready else ["v2_hygiene_phase2_sources_not_ready"]

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "V2_HYGIENE_PHASE2_MODULE_SKELETON_BACKLOG_PLAN_READY"
            if source_ready
            else "V2_HYGIENE_PHASE2_MODULE_SKELETON_BACKLOG_PLAN_BLOCKED"
        ),
        "plan_id": PLAN_ID,
        "plan_hash": "",
        "source_paths": source_paths,
        "source_hashes": {
            key: _hash_source(root / path) for key, path in source_paths.items()
        },
        "source_ready": source_ready,
        "notion_phase2_sources": _notion_source_records(),
        "phase2_goal": (
            "Map Notion Phase 2 module skeleton and governance hook requirements into "
            "repo-visible advisory backlog without creating module code or granting authority."
        ),
        "phase3_status": "PLACEHOLDER_HELD_FOR_FUTURE_DETAIL",
        "phase4_status": "PLACEHOLDER_HELD_FOR_FUTURE_DETAIL",
        "module_records": module_records,
        "deliverable_records": deliverable_records,
        "module_summary": {
            "total_module_count": len(module_records),
            "repo_observed_module_count": sum(
                1 for module in module_records if module["repo_observed"]
            ),
            "blocked_module_count": blocked_module_count,
            "advisory_only_module_count": sum(
                1 for module in module_records if module["initial_posture"] == "ADVISORY_ONLY"
            ),
        },
        "deliverable_summary": {
            "total_deliverable_count": len(deliverable_records),
            "high_priority_deliverable_count": sum(
                1 for item in deliverable_records if item["priority"] == "HIGH"
            ),
            "medium_priority_deliverable_count": sum(
                1 for item in deliverable_records if item["priority"] == "MEDIUM"
            ),
            "repo_observed_deliverable_count": sum(
                1 for item in deliverable_records if item["repo_observed"]
            ),
            "blocked_deliverable_count": blocked_deliverable_count,
        },
        "acceptance_gate_summary": {
            "operator_authorization_required": True,
            "operator_authorization_observed": False,
            "phase1_backlog_ready": source_ready,
            "safe_to_create_module_code": False,
            "safe_to_create_module_tests": False,
            "safe_to_register_modules": False,
            "safe_to_integrate_hygiene_pipeline": False,
            "safe_to_promote_out_of_advisory": False,
        },
        "recommended_next_action": (
            "hold Phase 2 module skeleton work as advisory backlog until explicit external "
            "operator authorization evidence permits a separate implementation record lane"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "implementation_authorized": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_prepare_patch": False,
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "authority_locks": _authority_locks(),
        "blockers": blockers,
    }
    packet["plan_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "plan_hash"}
    )
    return packet


def render_v2_hygiene_phase2_module_skeleton_backlog_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Phase 2 Module Skeleton Backlog Plan",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `source_ready`: `{packet['source_ready']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        f"- `implementation_authorized`: `{packet['implementation_authorized']}`",
        f"- `valid_for_execution`: `{packet['valid_for_execution']}`",
        f"- `phase3_status`: `{packet['phase3_status']}`",
        f"- `phase4_status`: `{packet['phase4_status']}`",
        "",
        "## Module Summary",
        "",
    ]
    for key in [
        "total_module_count",
        "repo_observed_module_count",
        "blocked_module_count",
        "advisory_only_module_count",
    ]:
        lines.append(f"- `{key}`: `{packet['module_summary'][key]}`")
    lines.extend(["", "## Modules", ""])
    for module in packet["module_records"]:
        lines.append(
            f"- `{module['module_id']}` {module['module_name']}: "
            f"`{module['implementation_status']}`"
        )
    lines.extend(["", "## Deliverables", ""])
    for deliverable in packet["deliverable_records"]:
        lines.append(
            f"- `{deliverable['deliverable_id']}` {deliverable['deliverable']}: "
            f"`{deliverable['implementation_status']}`"
        )
    if packet["blockers"]:
        lines.extend(["", "## Blockers", ""])
        for blocker in packet["blockers"]:
            lines.append(f"- `{blocker}`")
    return lines


def write_v2_hygiene_phase2_module_skeleton_backlog_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_v2_hygiene_phase2_module_skeleton_backlog_plan(root)
    write_canonical_json(target_root / PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / PLAN_MD_PATH,
        render_v2_hygiene_phase2_module_skeleton_backlog_plan_markdown(packet),
    )
    return packet
