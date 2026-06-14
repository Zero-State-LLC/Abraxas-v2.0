from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_shadow_replay_integration_exploration_plan import (
    OUT_JSON as SOURCE_SHADOW_REPLAY_INTEGRATION_EXPLORATION_PLAN_JSON,
)
from core.abx_codegen_phase1_operator_review_request import (
    REQUEST_JSON_PATH as SOURCE_PHASE1_OPERATOR_REVIEW_REQUEST_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = (
    "AbxCodegenIntelligenceSpineImprovementProposalShadowReplayWiringSpecPlan.v1"
)
PLAN_ID = (
    "ABX_CODEGEN_INTELLIGENCE_SPINE_IMPROVEMENT_PROPOSAL_"
    "SHADOW_REPLAY_WIRING_SPEC_PLAN_001"
)
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan_001.latest.md"
)

EXPECTED_EXPLORATION_STATUS = (
    "ABX_CODEGEN_SHADOW_REPLAY_INTEGRATION_EXPLORATION_PLAN_HELD_FOR_OPERATOR"
)
EXPECTED_OPERATOR_REVIEW_STATUS = "ABX_CODEGEN_PHASE1_OPERATOR_REVIEW_REQUEST_HELD"

NOTION_SPEC = {
    "title": "ImprovementProposal.v1 -> Shadow Replay Harness Wiring Spec",
    "page_id": "37d3e8ba-2f5c-81a3-b6a7-c53020554e81",
    "observed_as_of": "2026-06-12",
    "status": "Advisory Planning Draft",
    "version": "source_observed",
    "timestamp_policy": "source_observed_date_only_no_wall_clock_generation",
}


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


def _planning_status(sources_ready: bool) -> str:
    return "WIRING_SPEC_DEFINED_HELD_FOR_OPERATOR" if sources_ready else "NOT_COMPUTABLE"


def build_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan(
    *,
    repo_root: str | Path,
    source_shadow_replay_integration_exploration_plan_path: str
    | Path = SOURCE_SHADOW_REPLAY_INTEGRATION_EXPLORATION_PLAN_JSON,
    source_phase1_operator_review_request_path: str
    | Path = SOURCE_PHASE1_OPERATOR_REVIEW_REQUEST_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    exploration_path = Path(source_shadow_replay_integration_exploration_plan_path).as_posix()
    review_path = Path(source_phase1_operator_review_request_path).as_posix()
    exploration = _read_json(root / source_shadow_replay_integration_exploration_plan_path)
    review = _read_json(root / source_phase1_operator_review_request_path)

    exploration_ready = (
        exploration.get("artifact_type")
        == "AbxCodegenIntelligenceSpineShadowReplayIntegrationExplorationPlan.v1"
        and exploration.get("shadow_replay_integration_exploration_plan_status")
        == EXPECTED_EXPLORATION_STATUS
        and exploration.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and exploration.get("safe_to_auto_continue") is False
        and exploration.get("execution_authority") is False
        and exploration.get("valid_for_implementation") is False
    )
    review_ready = (
        review.get("schema_version") == "AbxCodegenPhase1OperatorReviewRequest.v1"
        and review.get("status") == EXPECTED_OPERATOR_REVIEW_STATUS
        and review.get("recommended_next_patch") == "NOT_COMPUTABLE"
        and review.get("safe_to_auto_continue") is False
        and review.get("execution_authority") is False
        and review.get("valid_for_implementation") is False
    )
    sources_ready = exploration_ready and review_ready
    status = _planning_status(sources_ready)

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "wiring_spec_plan_status": (
            "ABX_CODEGEN_IMPROVEMENT_PROPOSAL_SHADOW_REPLAY_WIRING_SPEC_PLAN_HELD_FOR_OPERATOR"
            if sources_ready
            else "NOT_COMPUTABLE"
        ),
        "source_notion_spec": {**NOTION_SPEC, "notion_writeback_performed": False},
        "source_shadow_replay_integration_exploration_plan": {
            "path": exploration_path,
            "hash": _sha256(root / source_shadow_replay_integration_exploration_plan_path),
            "shadow_replay_integration_exploration_plan_status": str(
                exploration.get(
                    "shadow_replay_integration_exploration_plan_status", "NOT_COMPUTABLE"
                )
            ),
            "source_ready": exploration_ready,
        },
        "source_phase1_operator_review_request": {
            "path": review_path,
            "hash": _sha256(root / source_phase1_operator_review_request_path),
            "status": str(review.get("status", "NOT_COMPUTABLE")),
            "source_ready": review_ready,
        },
        "input_mapping": [
            {
                "proposal_field": "proposal_id",
                "harness_input": "candidate_id",
                "transformation": "direct_mapping",
                "mapping_status": status,
            },
            {
                "proposal_field": "source_gap_diagnosis_id",
                "harness_input": "upstream_diagnosis_ref",
                "transformation": "direct_provenance_passthrough",
                "mapping_status": status,
            },
            {
                "proposal_field": "proposal_type",
                "harness_input": "candidate_type",
                "transformation": "enum_mapping_with_self_improvement_escalation",
                "mapping_status": status,
            },
            {
                "proposal_field": "target_surface",
                "harness_input": "target_surface",
                "transformation": "direct_scope_boundary_input",
                "mapping_status": status,
            },
            {
                "proposal_field": "intent",
                "harness_input": "intent_summary",
                "transformation": "source_text_hash_or_bounded_summary_future_decision",
                "mapping_status": status,
            },
            {
                "proposal_field": "contract_deltas",
                "harness_input": "proposed_changes",
                "transformation": "canonical_serialization_required",
                "mapping_status": status,
            },
            {
                "proposal_field": "affected_runes_and_affected_pipelines",
                "harness_input": "affected_artifacts",
                "transformation": "stable_ordered_scope_validation_input",
                "mapping_status": status,
            },
            {
                "proposal_field": "required_fixtures",
                "harness_input": "validation_fixtures",
                "transformation": "fixture_reference_only_no_fixture_execution",
                "mapping_status": status,
            },
            {
                "proposal_field": "validation_invariants",
                "harness_input": "required_invariants",
                "transformation": "direct_invariant_list_mapping",
                "mapping_status": status,
            },
            {
                "proposal_field": "risk_assessment.governance_rent",
                "harness_input": "governance_rent",
                "transformation": "receipt_metadata_and_threshold_input_only",
                "mapping_status": status,
            },
            {
                "proposal_field": "risk_assessment.self_modification_risk",
                "harness_input": "self_modification_flag",
                "transformation": "forces_hold_for_meta_gate_planning_path",
                "mapping_status": status,
            },
            {
                "proposal_field": "shadow_validation_plan",
                "harness_input": "replay_config",
                "transformation": "environment_seed_constraints_mapping",
                "mapping_status": status,
            },
            {
                "proposal_field": "promotion_path",
                "harness_input": "requested_promotion_path",
                "transformation": "direct_canon_path_forbidden",
                "mapping_status": status,
            },
            {
                "proposal_field": "provenance",
                "harness_input": "provenance_chain",
                "transformation": "full_chain_passthrough_to_receipt_template",
                "mapping_status": status,
            },
        ],
        "derived_inputs": {
            "replay_seed_policy": "derive_from_proposal_id_plus_shadow_validation_plan_seed",
            "replay_run_count_default": 12,
            "self_modification_replay_run_count_policy": (
                "greater_than_or_equal_to_12_pending_operator_decision"
            ),
            "authority_lock_expectations": [
                "no_code_mutation_in_shadow",
                "no_file_write",
                "no_network",
                "no_runtime_activation",
                "no_canon_promotion",
                "operator_review_required",
            ],
            "derivation_authorized": False,
        },
        "processing_steps": [
            {"step": "validate_proposal_structure", "step_status": status},
            {"step": "apply_shadow_validation_constraints", "step_status": status},
            {"step": "execute_deterministic_replays", "step_status": "NOT_AUTHORIZED"},
            {"step": "compute_replay_hashes", "step_status": "NOT_AUTHORIZED"},
            {"step": "evaluate_proof_flags", "step_status": "NOT_AUTHORIZED"},
            {"step": "determine_replay_status", "step_status": status},
            {"step": "apply_self_modification_rules", "step_status": status},
            {"step": "generate_recommendation", "step_status": "ROUTING_NOT_AUTHORIZED"},
        ],
        "output_mapping": [
            {
                "harness_output": "candidate_id_and_run_metadata",
                "receipt_field": "receipt_id",
                "mapping": "deterministic_hash_template_no_timestamp_generation",
                "mapping_status": status,
            },
            {
                "harness_output": "proposal_id",
                "receipt_field": "proposal_id",
                "mapping": "direct",
                "mapping_status": status,
            },
            {
                "harness_output": "shadow_run_id",
                "receipt_field": "shadow_run_id",
                "mapping": "deterministic_source_observed_identifier_required",
                "mapping_status": status,
            },
            {
                "harness_output": "replay_config",
                "receipt_field": "environment",
                "mapping": "full_environment_and_constraints_block",
                "mapping_status": status,
            },
            {
                "harness_output": "replay_run_hashes_and_status",
                "receipt_field": "validation_results",
                "mapping": "metrics_and_invariance_results",
                "mapping_status": status,
            },
            {
                "harness_output": "proof_flag_evaluation",
                "receipt_field": "governance_flags",
                "mapping": "requires_operator_review_and_self_modification_flags",
                "mapping_status": status,
            },
            {
                "harness_output": "rollback_snapshot_info",
                "receipt_field": "rollback_info",
                "mapping": "snapshot_hash_and_rollback_procedure_reference",
                "mapping_status": status,
            },
            {
                "harness_output": "final_status_and_recommendation",
                "receipt_field": "recommendation",
                "mapping": "expanded_hold_block_recommendation_enum",
                "mapping_status": status,
            },
            {
                "harness_output": "full_provenance",
                "receipt_field": "provenance",
                "mapping": "extended_with_replay_specific_fields",
                "mapping_status": status,
            },
        ],
        "recommendation_rules": [
            {
                "replay_condition": "twelve_or_more_identical_hashes_all_proofs_true_no_self_modification",
                "recommendation": "PROMOTE_TO_CANARY",
                "promotion_blockers_required": False,
                "routing_authorized": False,
            },
            {
                "replay_condition": "self_modification_flag_true",
                "recommendation": "HOLD_FOR_META_GATE",
                "promotion_blockers_required": True,
                "routing_authorized": False,
            },
            {
                "replay_condition": "operator_review_required_without_policy_violation",
                "recommendation": "HOLD_FOR_OPERATOR",
                "promotion_blockers_required": True,
                "routing_authorized": False,
            },
            {
                "replay_condition": "policy_boundary_violation",
                "recommendation": "BLOCK_POLICY_VIOLATION",
                "promotion_blockers_required": True,
                "routing_authorized": False,
            },
            {
                "replay_condition": "hash_divergence_or_missing_required_proofs",
                "recommendation": "BLOCK_REPLAY_FAILURE",
                "promotion_blockers_required": True,
                "routing_authorized": False,
            },
            {
                "replay_condition": "invalid_or_incomplete_proposal",
                "recommendation": "REJECT_OR_REFINE_PROPOSAL",
                "promotion_blockers_required": True,
                "routing_authorized": False,
            },
        ],
        "governance_safety_rules": [
            {
                "rule": "shadow_replays_are_observational_only",
                "enforced_by_this_plan": False,
                "planned_requirement": True,
            },
            {
                "rule": "self_modification_routes_to_hold_for_meta_gate",
                "enforced_by_this_plan": False,
                "planned_requirement": True,
            },
            {
                "rule": "requested_promotion_path_cannot_be_canon_directly",
                "enforced_by_this_plan": False,
                "planned_requirement": True,
            },
            {
                "rule": "promotion_blockers_required_for_hold_or_block",
                "enforced_by_this_plan": False,
                "planned_requirement": True,
            },
            {
                "rule": "receipts_feed_operator_decision_templates_only",
                "enforced_by_this_plan": False,
                "planned_requirement": True,
            },
            {
                "rule": "continuity_lane_creation_requires_separate_governed_lane",
                "enforced_by_this_plan": False,
                "planned_requirement": True,
            },
        ],
        "open_questions": [
            {
                "question": "Should codegen-specific proof flags live in shared P103 flags or a codegen extension module",
                "status": "UNRESOLVED",
            },
            {
                "question": "How complex contract_deltas can be replayed without filesystem mutation",
                "status": "UNRESOLVED",
            },
            {
                "question": "Whether the implementation should fork P103, share a utility, or use a thin wrapper",
                "status": "UNRESOLVED",
            },
            {
                "question": "Performance bounds for large contract deltas during repeated replay",
                "status": "UNRESOLVED",
            },
        ],
        "implementation_blockers": [
            "phase1_operator_review_request_held",
            "operator_attestation_missing",
            "authorization_record_missing",
            "target_harness_module_creation_denied",
            "shadow_replay_execution_denied",
            "shadow_improvement_receipt_creation_denied",
            "artifact_registry_runtime_registration_denied",
            "continuity_lane_creation_denied",
            "recommendation_routing_denied",
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
            "artifact_registry_runtime_registration": False,
            "auto_approval": False,
            "canary_promotion": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "continuity_lane_creation": False,
            "deterministic_replay_execution": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "harness_implementation": False,
            "meta_gate_routing": False,
            "notion_writeback": False,
            "operator_attestation": False,
            "operator_decision_record_creation": False,
            "proof_flag_evaluation": False,
            "queue_mutation": False,
            "receipt_creation": False,
            "recommendation_routing": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "target_harness_module_creation": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine ImprovementProposal Shadow Replay Wiring Spec Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- wiring_spec_plan_status: {packet['wiring_spec_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Input Mapping",
    ]
    for item in packet.get("input_mapping", []):
        if isinstance(item, Mapping):
            lines.append(
                f"- {item['proposal_field']} -> {item['harness_input']}: "
                f"{item['mapping_status']} ({item['transformation']})"
            )
    lines.extend(["", "## Recommendation Rules"])
    for rule in packet.get("recommendation_rules", []):
        if isinstance(rule, Mapping):
            lines.append(
                f"- {rule['replay_condition']}: {rule['recommendation']} "
                f"(routing_authorized={rule['routing_authorized']})"
            )
    lines.extend(["", "## Implementation Blockers"])
    for blocker in packet.get("implementation_blockers", []):
        lines.append(f"- {blocker}")
    return lines


def write_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
