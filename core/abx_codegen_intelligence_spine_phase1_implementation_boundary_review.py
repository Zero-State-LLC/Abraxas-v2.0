from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_module_surface_plan import (
    OUT_JSON as SOURCE_MODULE_SURFACE_PLAN_JSON,
)
from core.abx_codegen_intelligence_spine_phase1_code_detail_plan import (
    OUT_JSON as SOURCE_PHASE1_CODE_DETAIL_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpinePhase1ImplementationBoundaryReview.v1"
REVIEW_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_PHASE1_IMPLEMENTATION_BOUNDARY_REVIEW_001"
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_phase1_implementation_boundary_review_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_phase1_implementation_boundary_review_001.latest.md"
)

EXPECTED_PHASE1_CODE_DETAIL_STATUS = "ABX_CODEGEN_PHASE1_CODE_DETAIL_PLAN_HELD_FOR_OPERATOR"
EXPECTED_MODULE_SURFACE_STATUS = "ABX_CODEGEN_MODULE_SURFACE_PLAN_HELD_FOR_OPERATOR"

NOTION_PHASE1_SOURCES = [
    {
        "title": "Harness Implementation Roadmap - Codegen Intelligence Spine",
        "page_id": "37d3e8ba-2f5c-8160-a6a4-e47bae761b2e",
        "observed_as_of": "2026-06-12",
        "status": "Implementation Planning",
        "source_role": "phase1_starting_point",
    },
    {
        "title": "Planning Stub: core/codegen_shadow_replay_harness.py",
        "page_id": "37d3e8ba-2f5c-8147-8aea-ccfd7be5d1e2",
        "observed_as_of": "2026-06-12",
        "status": "Detailed Implementation Planning Spec",
        "source_role": "harness_implementation_spec",
    },
    {
        "title": "Phase 1 Harness Code Detail - core/codegen_shadow_replay_harness.py",
        "page_id": "37d3e8ba-2f5c-813f-8ce3-d571c8736020",
        "observed_as_of": "2026-06-12",
        "status": "Detailed Code Outline for Implementation",
        "source_role": "phase1_code_outline",
    },
]


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _read_json(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _phase1_intent(source_ready: bool) -> list[dict[str, Any]]:
    status = "BOUNDARY_REVIEWED_HELD_FOR_OPERATOR" if source_ready else "NOT_COMPUTABLE"
    rows = [
        (
            "implement_run_codegen_shadow_replay_skeleton",
            "Implement Phase 1 entry point for normal non-self-modifying proposals",
        ),
        (
            "validate_improvement_proposal",
            "Validate ImprovementProposal.v1 shape and reject unsupported self-modification",
        ),
        (
            "build_replay_config",
            "Build deterministic replay configuration from shadow_validation_plan",
        ),
        (
            "execute_deterministic_replay_simulation",
            "Run a deterministic Phase 1 simulation before future real replay integration",
        ),
        (
            "evaluate_standard_proof_flags",
            "Evaluate inherited proof flags without granting routing authority",
        ),
        (
            "build_shadow_improvement_receipt",
            "Produce a ShadowImprovementReceipt.v1-shaped result",
        ),
        (
            "write_canonical_output",
            "Optionally write canonical output in a future authorized implementation lane",
        ),
    ]
    return [
        {
            "notion_intent": name,
            "summary": summary,
            "review_status": status,
            "implementation_authorized_by_repo": False,
        }
        for name, summary in rows
    ]


def _blocked_actions(source_ready: bool) -> list[dict[str, Any]]:
    status = "BLOCKED_PENDING_OPERATOR_AUTHORIZATION" if source_ready else "NOT_COMPUTABLE"
    actions = [
        "create_core_codegen_shadow_replay_harness",
        "create_core_codegen_namespace_or_modules",
        "execute_shadow_replay_or_simulation",
        "create_shadow_improvement_receipts",
        "register_artifacts",
        "emit_implementation_prompts",
        "route_promote_to_canary",
        "mutate_runtime_or_canon",
        "write_back_to_notion_or_github",
    ]
    return [
        {
            "action": action,
            "action_status": status,
            "authorized": False,
        }
        for action in actions
    ]


def _allowed_actions(source_ready: bool) -> list[dict[str, Any]]:
    status = "ALLOWED_ADVISORY_REPO_ACTION" if source_ready else "NOT_COMPUTABLE"
    return [
        {
            "action": "emit_boundary_review_artifact",
            "action_status": status,
            "authority": "advisory_only",
        },
        {
            "action": "validate_existing_planning_artifacts",
            "action_status": status,
            "authority": "validation_only",
        },
        {
            "action": "update_repo_status_docs_from_observed_artifacts",
            "action_status": status,
            "authority": "documentation_sync_only",
        },
    ]


def build_abx_codegen_intelligence_spine_phase1_implementation_boundary_review(
    *,
    repo_root: str | Path,
    source_phase1_code_detail_plan_path: str
    | Path = SOURCE_PHASE1_CODE_DETAIL_PLAN_JSON,
    source_module_surface_plan_path: str | Path = SOURCE_MODULE_SURFACE_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    phase1_path = Path(source_phase1_code_detail_plan_path).as_posix()
    module_path = Path(source_module_surface_plan_path).as_posix()
    phase1_source = _read_json(root / source_phase1_code_detail_plan_path)
    module_source = _read_json(root / source_module_surface_plan_path)

    phase1_ready = (
        phase1_source.get("artifact_type")
        == "AbxCodegenIntelligenceSpinePhase1CodeDetailPlan.v1"
        and phase1_source.get("phase1_code_detail_plan_status")
        == EXPECTED_PHASE1_CODE_DETAIL_STATUS
        and phase1_source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and phase1_source.get("safe_to_auto_continue") is False
        and phase1_source.get("execution_authority") is False
        and phase1_source.get("valid_for_implementation") is False
    )
    module_ready = (
        module_source.get("artifact_type")
        == "AbxCodegenIntelligenceSpineModuleSurfacePlan.v1"
        and module_source.get("module_surface_plan_status") == EXPECTED_MODULE_SURFACE_STATUS
        and module_source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and module_source.get("safe_to_auto_continue") is False
        and module_source.get("execution_authority") is False
        and module_source.get("valid_for_implementation") is False
    )
    source_ready = phase1_ready and module_ready

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "review_id": REVIEW_ID,
        "phase1_implementation_boundary_review_status": (
            "ABX_CODEGEN_PHASE1_IMPLEMENTATION_BOUNDARY_REVIEW_HELD_FOR_OPERATOR"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "notion_phase1_sources": NOTION_PHASE1_SOURCES,
        "source_phase1_code_detail_plan": {
            "path": phase1_path,
            "hash": _sha256(root / source_phase1_code_detail_plan_path),
            "phase1_code_detail_plan_status": str(
                phase1_source.get("phase1_code_detail_plan_status", "NOT_COMPUTABLE")
            ),
            "source_ready": phase1_ready,
        },
        "source_module_surface_plan": {
            "path": module_path,
            "hash": _sha256(root / source_module_surface_plan_path),
            "module_surface_plan_status": str(
                module_source.get("module_surface_plan_status", "NOT_COMPUTABLE")
            ),
            "source_ready": module_ready,
        },
        "phase1_notion_intent": _phase1_intent(source_ready),
        "repo_authority_assessment": {
            "notion_phase1_detail_present": True,
            "repo_phase1_detail_plan_present": phase1_ready,
            "repo_module_surface_plan_present": module_ready,
            "phase1_implementation_authorized": False,
            "reason": "notion_phase1_code_detail_is_not_operator_implementation_authorization",
        },
        "blocked_phase1_actions": _blocked_actions(source_ready),
        "allowed_repo_actions": _allowed_actions(source_ready),
        "implementation_blockers": [
            "phase1_code_detail_plan_held_for_operator",
            "module_surface_plan_held_for_operator",
            "operator_authorization_missing",
            "core_codegen_shadow_replay_harness_creation_denied",
            "core_codegen_namespace_creation_denied",
            "module_file_creation_denied",
            "shadow_replay_execution_denied",
            "receipt_creation_denied",
            "artifact_registry_registration_denied",
            "promotion_routing_denied",
            "notion_writeback_denied",
            "github_writeback_denied",
        ],
        "recommended_next_lane": "NOT_COMPUTABLE",
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "authority_locks": {
            "artifact_registry_registration": False,
            "auto_approval": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "core_codegen_namespace_creation": False,
            "core_harness_file_creation": False,
            "execution": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "implementation_prompt_emission": False,
            "module_file_creation": False,
            "notion_writeback": False,
            "operator_decision_record_creation": False,
            "promotion_to_canary": False,
            "queue_mutation": False,
            "receipt_creation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "shadow_replay_execution": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_phase1_implementation_boundary_review(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_phase1_implementation_boundary_review_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Phase 1 Implementation Boundary Review",
        "",
        f"- review_id: {packet['review_id']}",
        "- phase1_implementation_boundary_review_status: "
        f"{packet['phase1_implementation_boundary_review_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Blocked Phase 1 Actions",
    ]
    for action in packet.get("blocked_phase1_actions", []):
        if isinstance(action, Mapping):
            lines.append(f"- {action['action']}: authorized={action['authorized']}")
    lines.extend(["", "## Allowed Repo Actions"])
    for action in packet.get("allowed_repo_actions", []):
        if isinstance(action, Mapping):
            lines.append(f"- {action['action']}: {action['authority']}")
    lines.extend(["", "## Implementation Blockers"])
    for blocker in packet.get("implementation_blockers", []):
        lines.append(f"- {blocker}")
    return lines


def write_abx_codegen_intelligence_spine_phase1_implementation_boundary_review_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_phase1_implementation_boundary_review_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
