from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_phase1_code_detail_plan import (
    OUT_JSON as SOURCE_PHASE1_CODE_DETAIL_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineHarnessInterfaceSpecPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_HARNESS_INTERFACE_SPEC_PLAN_001"
OUT_JSON = "out/audit/abx_codegen_intelligence_spine_harness_interface_spec_plan_001.latest.json"
OUT_MD = "out/audit/abx_codegen_intelligence_spine_harness_interface_spec_plan_001.latest.md"

NOTION_SPEC = {
    "title": "Planning Stub: core/codegen_shadow_replay_harness.py",
    "page_id": "37d3e8ba-2f5c-8147-8aea-ccfd7be5d1e2",
    "observed_as_of": "2026-06-12",
    "status": "Detailed Implementation Planning Spec",
    "version": "v0.2",
}

EXPECTED_SOURCE_STATUS = "ABX_CODEGEN_PHASE1_CODE_DETAIL_PLAN_HELD_FOR_OPERATOR"


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


def _planning_status(source_ready: bool) -> str:
    return "BLOCKED_PENDING_OPERATOR_AUTHORIZATION" if source_ready else "NOT_COMPUTABLE"


def build_abx_codegen_intelligence_spine_harness_interface_spec_plan(
    *,
    repo_root: str | Path,
    source_phase1_code_detail_plan_path: str | Path = SOURCE_PHASE1_CODE_DETAIL_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_phase1_code_detail_plan_path).as_posix()
    source = _read_json(root / source_phase1_code_detail_plan_path)
    source_ready = (
        source.get("artifact_type") == "AbxCodegenIntelligenceSpinePhase1CodeDetailPlan.v1"
        and source.get("phase1_code_detail_plan_status") == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and source.get("safe_to_auto_continue") is False
        and source.get("execution_authority") is False
        and source.get("valid_for_implementation") is False
    )
    status = _planning_status(source_ready)

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "harness_interface_spec_plan_status": (
            "ABX_CODEGEN_HARNESS_INTERFACE_SPEC_PLAN_HELD_FOR_OPERATOR"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_notion_spec": {
            **NOTION_SPEC,
            "spec_hash_policy": "source_observed_metadata_only",
            "notion_writeback_performed": False,
        },
        "source_phase1_code_detail_plan": {
            "path": source_path,
            "hash": _sha256(root / source_phase1_code_detail_plan_path),
            "phase1_code_detail_plan_status": str(
                source.get("phase1_code_detail_plan_status", "NOT_COMPUTABLE")
            ),
            "source_ready": source_ready,
        },
        "target_module": "core/codegen_shadow_replay_harness.py",
        "design_goals": [
            {"goal": "deterministic_and_replay_safe", "goal_status": status},
            {"goal": "strict_authority_locks_and_fail_closed_posture", "goal_status": status},
            {
                "goal": "separate_general_replay_logic_from_codegen_extensions",
                "goal_status": status,
            },
            {"goal": "support_elevated_self_improvement_scrutiny", "goal_status": status},
        ],
        "architecture_stages": [
            {"stage": "ImprovementProposal.v1", "stage_status": status},
            {"stage": "Validation & Normalization Layer", "stage_status": status},
            {"stage": "Replay Configuration Builder", "stage_status": status},
            {"stage": "Deterministic Replay Executor", "stage_status": status},
            {"stage": "Proof Flag Evaluator", "stage_status": status},
            {"stage": "Status & Recommendation Engine", "stage_status": status},
            {"stage": "ShadowImprovementReceipt.v1 Builder", "stage_status": status},
            {"stage": "Canonical JSON Output + Artifact Registry Registration", "stage_status": status},
        ],
        "core_interfaces": [
            {
                "interface_name": "run_codegen_shadow_replay",
                "signature_summary": "proposal, upstream_diagnosis, config_overrides -> ShadowImprovementReceipt.v1 dict",
                "interface_status": status,
                "implementation_authorized": False,
            },
            {
                "interface_name": "_validate_proposal",
                "signature_summary": "proposal -> validation findings",
                "interface_status": status,
                "implementation_authorized": False,
            },
            {
                "interface_name": "_build_replay_config",
                "signature_summary": "proposal, overrides -> replay config",
                "interface_status": status,
                "implementation_authorized": False,
            },
            {
                "interface_name": "_execute_deterministic_replays",
                "signature_summary": "config -> run results and hashes",
                "interface_status": status,
                "implementation_authorized": False,
            },
            {
                "interface_name": "_evaluate_proof_flags",
                "signature_summary": "proposal, replay_results -> bool flags",
                "interface_status": status,
                "implementation_authorized": False,
            },
            {
                "interface_name": "_determine_recommendation",
                "signature_summary": "status, proof_flags, self_mod_flag -> recommendation",
                "interface_status": status,
                "implementation_authorized": False,
            },
            {
                "interface_name": "_build_receipt",
                "signature_summary": "inputs -> ShadowImprovementReceipt.v1",
                "interface_status": status,
                "implementation_authorized": False,
            },
        ],
        "proof_flags": {
            "standard": [
                "authority_lock_invariance_observed",
                "not_computable_replay_observed",
                "aal_viz_projection_only_observed",
                "operator_review_observed",
                "no_runtime_mutation_observed",
                "no_canon_promotion_observed",
                "no_forecast_weight_mutation_observed",
            ],
            "codegen_specific": [
                "codegen_deterministic_output_observed",
                "contract_delta_replay_successful",
                "self_modification_invariants_satisfied",
                "meta_gate_extra_checks_passed",
            ],
            "proof_flag_evaluation_authorized": False,
        },
        "meta_gate_handling_rules": [
            {
                "rule": "increase_required_replay_run_count_to_24_for_self_modification",
                "rule_status": status,
                "implementation_authorized": False,
            },
            {
                "rule": "require_codegen_specific_and_meta_gate_flags",
                "rule_status": status,
                "implementation_authorized": False,
            },
            {
                "rule": "force_hold_for_meta_gate_unless_checks_pass_perfectly",
                "rule_status": status,
                "implementation_authorized": False,
            },
            {
                "rule": "populate_promotion_blockers_with_relevant_reasons",
                "rule_status": status,
                "implementation_authorized": False,
            },
        ],
        "failure_modes": [
            {
                "failure_mode": "Hash divergence",
                "recommendation": "BLOCK_REPLAY_FAILURE",
                "promotion_blockers_example": ["replay_hash_divergence"],
                "routing_authorized": False,
            },
            {
                "failure_mode": "Governance compliance failed",
                "recommendation": "BLOCK_POLICY_VIOLATION",
                "promotion_blockers_example": ["governance_compliance_failed"],
                "routing_authorized": False,
            },
            {
                "failure_mode": "Self-modification detected",
                "recommendation": "HOLD_FOR_META_GATE",
                "promotion_blockers_example": ["self_modification_detected"],
                "routing_authorized": False,
            },
            {
                "failure_mode": "Missing required proof flags",
                "recommendation": "BLOCK_REPLAY_FAILURE",
                "promotion_blockers_example": ["missing_required_proof_flags"],
                "routing_authorized": False,
            },
            {
                "failure_mode": "Proposal validation failed",
                "recommendation": "REJECT",
                "promotion_blockers_example": ["invalid_proposal_structure"],
                "routing_authorized": False,
            },
        ],
        "integration_guidance": {
            "prefer_extend_research_shadow_replay_audit": True,
            "shared_replay_utility_refactor_allowed_by_this_plan": False,
            "codegen_specific_logic_stays_in_target_module": True,
            "p103_reuse_authorized": False,
        },
        "output_requirements": {
            "canonical_json_return_required": True,
            "artifact_registry_registration_suitable": True,
            "full_provenance_chain_required": True,
            "deterministic_given_same_inputs_and_seed": True,
            "canonical_output_write_authorized": False,
            "artifact_registry_registration_authorized": False,
            "receipt_creation_authorized": False,
        },
        "open_questions": [
            {
                "question": "How to simulate/apply contract_deltas during replay",
                "status": "UNRESOLVED",
            },
            {"question": "Performance considerations for large proposals", "status": "UNRESOLVED"},
            {
                "question": "Dedicated CodegenShadowReplayAudit.v1 vs ShadowImprovementReceipt.v1",
                "status": "UNRESOLVED",
            },
        ],
        "implementation_blockers": [
            "phase1_code_detail_plan_held_for_operator",
            "target_module_creation_denied",
            "deterministic_replay_execution_denied",
            "receipt_creation_denied",
            "artifact_registry_registration_denied",
            "shared_replay_refactor_denied",
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
            "meta_gate_routing": False,
            "notion_writeback": False,
            "operator_decision_record_creation": False,
            "p103_replay_refactor": False,
            "proof_flag_evaluation": False,
            "queue_mutation": False,
            "receipt_creation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "shadow_replay_execution": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_harness_interface_spec_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_harness_interface_spec_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Harness Interface Spec Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- harness_interface_spec_plan_status: {packet['harness_interface_spec_plan_status']}",
        f"- target_module: {packet['target_module']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Core Interfaces",
    ]
    for interface in packet.get("core_interfaces", []):
        if isinstance(interface, Mapping):
            lines.append(
                f"- {interface['interface_name']}: {interface['interface_status']} "
                f"(implementation_authorized={interface['implementation_authorized']})"
            )
    lines.extend(["", "## Implementation Blockers"])
    for blocker in packet.get("implementation_blockers", []):
        lines.append(f"- {blocker}")
    return lines


def write_abx_codegen_intelligence_spine_harness_interface_spec_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_harness_interface_spec_plan_markdown(packet)
        )
        + "\n",
        encoding="utf-8",
    )
