from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan import (
    OUT_JSON as SOURCE_SELF_IMPROVEMENT_BOUNDARY_POLICY_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineShadowReplayIntegrationExplorationPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_REPLAY_INTEGRATION_EXPLORATION_PLAN_001"
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan_001.latest.md"
)

EXPECTED_SOURCE_STATUS = "ABX_CODEGEN_SELF_IMPROVEMENT_BOUNDARY_POLICY_PLAN_HELD_FOR_OPERATOR"

NOTION_SPECS = [
    {
        "title": "Shadow Replay Integration Exploration - Codegen Intelligence Spine",
        "page_id": "37d3e8ba-2f5c-8194-9334-e30d4cd5c355",
        "observed_as_of": "2026-06-12",
        "status": "Advisory Planning Exploration",
        "version": "source_observed",
        "timestamp_policy": "source_observed_date_only_no_wall_clock_generation",
    },
    {
        "title": "ImprovementProposal.v1 -> Shadow Replay Harness Wiring Spec",
        "page_id": "37d3e8ba-2f5c-81a3-b6a7-c53020554e81",
        "observed_as_of": "2026-06-12",
        "status": "Advisory Planning Draft",
        "version": "source_observed",
        "timestamp_policy": "source_observed_date_only_no_wall_clock_generation",
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


def _planning_status(source_ready: bool) -> str:
    return "EXPLORATION_DEFINED_HELD_FOR_OPERATOR" if source_ready else "NOT_COMPUTABLE"


def build_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan(
    *,
    repo_root: str | Path,
    source_self_improvement_boundary_policy_plan_path: str
    | Path = SOURCE_SELF_IMPROVEMENT_BOUNDARY_POLICY_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_self_improvement_boundary_policy_plan_path).as_posix()
    source = _read_json(root / source_self_improvement_boundary_policy_plan_path)
    source_ready = (
        source.get("artifact_type")
        == "AbxCodegenIntelligenceSpineSelfImprovementBoundaryPolicyPlan.v1"
        and source.get("self_improvement_boundary_policy_plan_status")
        == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and source.get("safe_to_auto_continue") is False
        and source.get("execution_authority") is False
        and source.get("valid_for_implementation") is False
    )
    status = _planning_status(source_ready)

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "shadow_replay_integration_exploration_plan_status": (
            "ABX_CODEGEN_SHADOW_REPLAY_INTEGRATION_EXPLORATION_PLAN_HELD_FOR_OPERATOR"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_notion_specs": [
            {**spec, "notion_writeback_performed": False} for spec in NOTION_SPECS
        ],
        "source_self_improvement_boundary_policy_plan": {
            "path": source_path,
            "hash": _sha256(root / source_self_improvement_boundary_policy_plan_path),
            "self_improvement_boundary_policy_plan_status": str(
                source.get("self_improvement_boundary_policy_plan_status", "NOT_COMPUTABLE")
            ),
            "source_ready": source_ready,
        },
        "observed_p103_replay_patterns": [
            {
                "pattern": "twelve_run_invariance",
                "source_surface": "core/research_shadow_replay_audit.py",
                "planned_reuse_status": status,
                "reuse_authorized": False,
            },
            {
                "pattern": "identical_replay_hash_requirement",
                "source_surface": "ResearchShadowReplayAudit.v1",
                "planned_reuse_status": status,
                "reuse_authorized": False,
            },
            {
                "pattern": "standard_governance_proof_flags",
                "source_surface": "P103 shadow replay lane",
                "planned_reuse_status": status,
                "reuse_authorized": False,
            },
            {
                "pattern": "advisory_only_projection_only_authority_locks",
                "source_surface": "P103 shadow replay lane",
                "planned_reuse_status": status,
                "reuse_authorized": False,
            },
        ],
        "proposal_to_harness_mapping": [
            {
                "proposal_field": "proposal_id",
                "harness_input": "candidate_id",
                "mapping": "direct",
                "mapping_status": status,
            },
            {
                "proposal_field": "source_gap_diagnosis_id",
                "harness_input": "upstream_diagnosis_ref",
                "mapping": "direct_provenance",
                "mapping_status": status,
            },
            {
                "proposal_field": "proposal_type",
                "harness_input": "candidate_type",
                "mapping": "enum_with_self_improvement_escalation",
                "mapping_status": status,
            },
            {
                "proposal_field": "target_surface",
                "harness_input": "target_surface",
                "mapping": "direct_scope_boundary_input",
                "mapping_status": status,
            },
            {
                "proposal_field": "contract_deltas",
                "harness_input": "proposed_changes",
                "mapping": "canonical_serialization_required",
                "mapping_status": status,
            },
            {
                "proposal_field": "required_fixtures",
                "harness_input": "validation_fixtures",
                "mapping": "fixture_reference_only",
                "mapping_status": status,
            },
            {
                "proposal_field": "validation_invariants",
                "harness_input": "required_invariants",
                "mapping": "direct",
                "mapping_status": status,
            },
            {
                "proposal_field": "risk_assessment.self_modification_risk",
                "harness_input": "self_modification_flag",
                "mapping": "forces_meta_gate_planning_path",
                "mapping_status": status,
            },
            {
                "proposal_field": "shadow_validation_plan",
                "harness_input": "replay_config",
                "mapping": "environment_seed_constraints",
                "mapping_status": status,
            },
            {
                "proposal_field": "promotion_path",
                "harness_input": "requested_promotion_path",
                "mapping": "canon_direct_path_forbidden",
                "mapping_status": status,
            },
        ],
        "replay_constraints": {
            "minimum_run_count": 12,
            "self_modification_run_count": "greater_than_or_equal_to_12_future_decision_required",
            "seed_policy": "derive_from_proposal_id_plus_shadow_validation_plan_seed",
            "no_network_required": True,
            "no_file_write_required": True,
            "bounded_runtime_required": True,
            "bounded_memory_required": True,
            "constraint_enforcement_authorized": False,
            "deterministic_replay_execution_authorized": False,
        },
        "proof_flag_plan": {
            "standard_flags": [
                "authority_lock_invariance_observed",
                "not_computable_replay_observed",
                "aal_viz_projection_only_observed",
                "operator_review_observed",
                "no_runtime_mutation_observed",
                "no_canon_promotion_observed",
                "no_forecast_weight_mutation_observed",
            ],
            "codegen_specific_flags": [
                "codegen_deterministic_output_observed",
                "no_code_mutation_in_shadow_observed",
                "contract_delta_replay_successful",
                "meta_gate_invariants_satisfied",
            ],
            "proof_flag_evaluation_authorized": False,
        },
        "status_and_recommendation_rules": [
            {
                "condition": "twelve_or_more_identical_hashes_and_all_proof_flags_true",
                "shadow_replay_status": "REPLAY_PASS",
                "recommendation": "PROMOTE_TO_CANARY_OR_HOLD_FOR_META_GATE_DEPENDING_ON_RISK",
                "rule_status": status,
                "routing_authorized": False,
            },
            {
                "condition": "replay_hashes_differ",
                "shadow_replay_status": "REPLAY_FAIL_HASH_DIVERGENCE",
                "recommendation": "BLOCK_REPLAY_FAILURE",
                "rule_status": status,
                "routing_authorized": False,
            },
            {
                "condition": "proof_flags_missing",
                "shadow_replay_status": "REPLAY_BLOCKED_MISSING_PROOFS",
                "recommendation": "BLOCK_REPLAY_FAILURE",
                "rule_status": status,
                "routing_authorized": False,
            },
            {
                "condition": "run_count_insufficient",
                "shadow_replay_status": "REPLAY_INCOMPLETE",
                "recommendation": "HOLD_FOR_OPERATOR",
                "rule_status": status,
                "routing_authorized": False,
            },
            {
                "condition": "self_modification_flag_true",
                "shadow_replay_status": "REPLAY_PASS_WITH_META_GATE_TRIGGER",
                "recommendation": "HOLD_FOR_META_GATE",
                "rule_status": status,
                "routing_authorized": False,
            },
        ],
        "integration_strategy": {
            "preferred_shape": "shared_general_replay_mechanics_with_thin_codegen_specific_harness",
            "target_module": "core/codegen_shadow_replay_harness.py",
            "reuse_p103_patterns": True,
            "fork_p103_module_preferred": False,
            "shared_library_refactor_authorized": False,
            "target_module_creation_authorized": False,
            "shadow_improvement_receipt_creation_authorized": False,
            "operator_decision_record_attachment_authorized": False,
            "aal_viz_consumption_mode": "display_only",
            "oracle_consumption_mode": "shadow_context_only",
        },
        "open_questions": [
            {
                "question": "Should codegen-specific proof flags live in shared P103 flags or a codegen extension module",
                "status": "UNRESOLVED",
            },
            {
                "question": "How should complex contract_deltas be replayed without mutation",
                "status": "UNRESOLVED",
            },
            {
                "question": "Whether implementation should use fork, shared library, or thin wrapper",
                "status": "UNRESOLVED",
            },
            {
                "question": "Performance bounds for large contract deltas during 12-run replay",
                "status": "UNRESOLVED",
            },
        ],
        "implementation_blockers": [
            "self_improvement_boundary_policy_plan_held_for_operator",
            "target_module_creation_denied",
            "deterministic_replay_execution_denied",
            "constraint_enforcement_denied",
            "proof_flag_evaluation_denied",
            "shadow_improvement_receipt_creation_denied",
            "operator_decision_record_attachment_denied",
            "shared_replay_refactor_denied",
            "artifact_registry_registration_denied",
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
            "canary_promotion": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "constraint_enforcement": False,
            "deterministic_replay_execution": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "meta_gate_routing": False,
            "notion_writeback": False,
            "operator_decision_record_attachment": False,
            "proof_flag_evaluation": False,
            "queue_mutation": False,
            "receipt_creation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "shared_replay_refactor": False,
            "target_module_creation": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Shadow Replay Integration Exploration Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        "- shadow_replay_integration_exploration_plan_status: "
        f"{packet['shadow_replay_integration_exploration_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Proposal Mapping",
    ]
    for item in packet.get("proposal_to_harness_mapping", []):
        if isinstance(item, Mapping):
            lines.append(
                f"- {item['proposal_field']} -> {item['harness_input']}: "
                f"{item['mapping_status']}"
            )
    lines.extend(["", "## Status Rules"])
    for rule in packet.get("status_and_recommendation_rules", []):
        if isinstance(rule, Mapping):
            lines.append(
                f"- {rule['shadow_replay_status']}: {rule['recommendation']} "
                f"(routing_authorized={rule['routing_authorized']})"
            )
    lines.extend(["", "## Implementation Blockers"])
    for blocker in packet.get("implementation_blockers", []):
        lines.append(f"- {blocker}")
    return lines


def write_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
