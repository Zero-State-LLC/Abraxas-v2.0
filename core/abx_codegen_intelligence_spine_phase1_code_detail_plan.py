from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_harness_implementation_roadmap_plan import (
    OUT_JSON as SOURCE_HARNESS_ROADMAP_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpinePhase1CodeDetailPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_PHASE1_CODE_DETAIL_PLAN_001"
OUT_JSON = "out/audit/abx_codegen_intelligence_spine_phase1_code_detail_plan_001.latest.json"
OUT_MD = "out/audit/abx_codegen_intelligence_spine_phase1_code_detail_plan_001.latest.md"

NOTION_SPEC = {
    "title": "Phase 1 Harness Code Detail - core/codegen_shadow_replay_harness.py",
    "page_id": "37d3e8ba-2f5c-813f-8ce3-d571c8736020",
    "observed_as_of": "2026-06-12",
    "status": "Detailed Code Outline for Implementation",
    "phase": "1 (Core Foundation)",
}

EXPECTED_SOURCE_STATUS = "ABX_CODEGEN_HARNESS_IMPLEMENTATION_ROADMAP_PLAN_HELD_FOR_OPERATOR"


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


def _planned_interfaces(source_ready: bool) -> list[dict[str, Any]]:
    status = "BLOCKED_PENDING_OPERATOR_AUTHORIZATION" if source_ready else "NOT_COMPUTABLE"
    rows = [
        (
            "run_codegen_shadow_replay",
            "Main entry point accepting ImprovementProposal.v1 and returning ShadowImprovementReceipt.v1",
        ),
        ("_validate_proposal", "Validate required fields and reject self-modification in Phase 1"),
        ("_build_replay_config", "Build deterministic replay config from shadow_validation_plan"),
        ("_execute_replays", "Draft deterministic replay simulation loop"),
        ("_evaluate_proof_flags", "Evaluate standard proof flags only"),
        ("_determine_recommendation", "Map replay/proof results to draft recommendation and status"),
        ("_build_receipt", "Build draft ShadowImprovementReceipt.v1 packet"),
        ("_build_error_receipt", "Build validation-error receipt for invalid proposals"),
    ]
    return [
        {
            "interface_name": name,
            "purpose": purpose,
            "interface_status": status,
            "implementation_authorized": False,
            "execution_authorized": False,
            "file_write_authorized": False,
        }
        for name, purpose in rows
    ]


def _draft_receipt_fields(source_ready: bool) -> list[dict[str, Any]]:
    status = "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE"
    fields = [
        "schema_version",
        "receipt_id",
        "source_observed_timestamp",
        "proposal_id",
        "shadow_run_id",
        "environment",
        "validation_results",
        "metrics",
        "governance_flags",
        "rollback_info",
        "promotion_blockers",
        "provenance",
        "recommendation",
    ]
    return [
        {
            "field": field,
            "field_status": status,
            "receipt_creation_authorized": False,
        }
        for field in fields
    ]


def _draft_recommendations(source_ready: bool) -> list[dict[str, Any]]:
    status = "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE"
    return [
        {
            "recommendation": "BLOCK_REPLAY_FAILURE",
            "status": "REPLAY_FAIL_HASH_DIVERGENCE",
            "recommendation_status": status,
            "routing_authorized": False,
        },
        {
            "recommendation": "BLOCK_REPLAY_FAILURE",
            "status": "REPLAY_BLOCKED_MISSING_PROOFS",
            "recommendation_status": status,
            "routing_authorized": False,
        },
        {
            "recommendation": "PROMOTE_TO_CANARY",
            "status": "REPLAY_PASS",
            "recommendation_status": status,
            "routing_authorized": False,
            "promotion_authorized": False,
        },
    ]


def build_abx_codegen_intelligence_spine_phase1_code_detail_plan(
    *,
    repo_root: str | Path,
    source_harness_implementation_roadmap_plan_path: str | Path = SOURCE_HARNESS_ROADMAP_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_harness_implementation_roadmap_plan_path).as_posix()
    source = _read_json(root / source_harness_implementation_roadmap_plan_path)
    source_ready = (
        source.get("artifact_type")
        == "AbxCodegenIntelligenceSpineHarnessImplementationRoadmapPlan.v1"
        and source.get("harness_implementation_roadmap_plan_status") == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and source.get("safe_to_auto_continue") is False
        and source.get("execution_authority") is False
        and source.get("valid_for_implementation") is False
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "phase1_code_detail_plan_status": (
            "ABX_CODEGEN_PHASE1_CODE_DETAIL_PLAN_HELD_FOR_OPERATOR"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_notion_spec": {
            **NOTION_SPEC,
            "spec_hash_policy": "source_observed_metadata_only",
            "notion_writeback_performed": False,
        },
        "source_harness_implementation_roadmap_plan": {
            "path": source_path,
            "hash": _sha256(root / source_harness_implementation_roadmap_plan_path),
            "harness_implementation_roadmap_plan_status": str(
                source.get("harness_implementation_roadmap_plan_status", "NOT_COMPUTABLE")
            ),
            "source_ready": source_ready,
        },
        "target_file": "core/codegen_shadow_replay_harness.py",
        "planned_interfaces": _planned_interfaces(source_ready),
        "draft_receipt_fields": _draft_receipt_fields(source_ready),
        "draft_recommendation_values": _draft_recommendations(source_ready),
        "phase1_next_steps": [
            {
                "next_step": "replace_simulation_with_real_replay_execution",
                "step_status": "FUTURE_BLOCKED",
                "authorized": False,
            },
            {
                "next_step": "implement_self_modification_logic_phase2",
                "step_status": "FUTURE_BLOCKED",
                "authorized": False,
            },
            {
                "next_step": "add_full_error_taxonomy",
                "step_status": "REFERENCE_ONLY",
                "authorized": False,
            },
            {
                "next_step": "integrate_with_artifact_registry",
                "step_status": "FUTURE_BLOCKED",
                "authorized": False,
            },
        ],
        "implementation_blockers": [
            "harness_implementation_roadmap_held_for_operator",
            "core_codegen_shadow_replay_harness_write_denied",
            "shadow_replay_execution_denied",
            "receipt_creation_denied",
            "promotion_to_canary_denied",
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
            "auto_approval": False,
            "canonical_output_write": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "core_harness_file_creation": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "harness_implementation": False,
            "meta_gate_authorization": False,
            "notion_writeback": False,
            "operator_decision_record_creation": False,
            "promotion_to_canary": False,
            "queue_mutation": False,
            "receipt_creation": False,
            "replay_simulation_execution": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "shadow_replay_execution": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_phase1_code_detail_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_phase1_code_detail_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Phase 1 Code Detail Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- phase1_code_detail_plan_status: {packet['phase1_code_detail_plan_status']}",
        f"- target_file: {packet['target_file']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Planned Interfaces",
    ]
    for interface in packet.get("planned_interfaces", []):
        if isinstance(interface, Mapping):
            lines.append(
                f"- {interface['interface_name']}: {interface['interface_status']} "
                f"(implementation_authorized={interface['implementation_authorized']})"
            )
    lines.extend(["", "## Implementation Blockers"])
    for blocker in packet.get("implementation_blockers", []):
        lines.append(f"- {blocker}")
    return lines


def write_abx_codegen_intelligence_spine_phase1_code_detail_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(render_abx_codegen_intelligence_spine_phase1_code_detail_plan_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
