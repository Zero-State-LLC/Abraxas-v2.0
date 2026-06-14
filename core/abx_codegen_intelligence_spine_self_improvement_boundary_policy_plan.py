from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan import (
    OUT_JSON as SOURCE_META_GATE_AUTHORIZATION_RECORD_TEMPLATE_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineSelfImprovementBoundaryPolicyPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_SELF_IMPROVEMENT_BOUNDARY_POLICY_PLAN_001"
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan_001.latest.md"
)

EXPECTED_SOURCE_STATUS = "ABX_CODEGEN_META_GATE_AUTHORIZATION_RECORD_TEMPLATE_PLAN_HELD_FOR_OPERATOR"

NOTION_SPECS = [
    {
        "title": "Self-Improvement Meta-Gate Spec - Codegen Intelligence Spine",
        "page_id": "37d3e8ba-2f5c-811c-b80a-dd31b2d8f4ce",
        "observed_as_of": "2026-06-12",
        "status": "Advisory Planning Draft",
        "version": "source_observed",
        "timestamp_policy": "source_observed_date_only_no_wall_clock_generation",
    },
    {
        "title": "Self-Improvement Scope Boundaries - Codegen Intelligence Spine",
        "page_id": "37d3e8ba-2f5c-8159-a198-f5767ceec6b8",
        "observed_as_of": "2026-06-12",
        "status": "Planning Spec (Advisory)",
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
    return "BOUNDARY_POLICY_DEFINED_HELD_FOR_OPERATOR" if source_ready else "NOT_COMPUTABLE"


def build_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan(
    *,
    repo_root: str | Path,
    source_meta_gate_authorization_record_template_plan_path: str
    | Path = SOURCE_META_GATE_AUTHORIZATION_RECORD_TEMPLATE_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_meta_gate_authorization_record_template_plan_path).as_posix()
    source = _read_json(root / source_meta_gate_authorization_record_template_plan_path)
    source_ready = (
        source.get("artifact_type")
        == "AbxCodegenIntelligenceSpineMetaGateAuthorizationRecordTemplatePlan.v1"
        and source.get("meta_gate_authorization_record_template_plan_status")
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
        "self_improvement_boundary_policy_plan_status": (
            "ABX_CODEGEN_SELF_IMPROVEMENT_BOUNDARY_POLICY_PLAN_HELD_FOR_OPERATOR"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_notion_specs": [
            {**spec, "notion_writeback_performed": False} for spec in NOTION_SPECS
        ],
        "source_meta_gate_authorization_record_template_plan": {
            "path": source_path,
            "hash": _sha256(root / source_meta_gate_authorization_record_template_plan_path),
            "meta_gate_authorization_record_template_plan_status": str(
                source.get(
                    "meta_gate_authorization_record_template_plan_status",
                    "NOT_COMPUTABLE",
                )
            ),
            "source_ready": source_ready,
        },
        "meta_gate_triggers": [
            {
                "trigger": "self_modification_risk_true",
                "source_field": "ImprovementProposal.v1.self_modification_risk",
                "trigger_status": status,
                "routing_authorized": False,
            },
            {
                "trigger": "self_modification_detected_true",
                "source_field": "ShadowImprovementReceipt.v1.self_modification_detected",
                "trigger_status": status,
                "routing_authorized": False,
            },
            {
                "trigger": "target_surface_is_codegen_spine_or_core_governance_contract",
                "source_field": "ImprovementProposal.v1.target_surface",
                "trigger_status": status,
                "routing_authorized": False,
            },
            {
                "trigger": "proposal_type_self_improvement",
                "source_field": "ImprovementProposal.v1.proposal_type",
                "trigger_status": status,
                "routing_authorized": False,
            },
        ],
        "green_zone_policy": {
            "policy_status": status,
            "allowed_to_propose_examples": [
                "own_packet_schemas_and_validation_rules",
                "core_codegen_shadow_replay_harness_logic",
                "fixture_generation_and_test_vector_logic",
                "self_related_documentation_and_planning_surfaces",
                "projection_only_aal_viz_or_oracle_integration_points",
                "safe_replay_configuration_default_optimizations",
            ],
            "still_requires_meta_gate_and_normal_promotion": True,
            "proposal_authority_granted": False,
        },
        "yellow_zone_policy": {
            "policy_status": status,
            "extra_scrutiny_required_for": [
                "standard_or_codegen_specific_proof_flag_definition_changes",
                "recommendation_enum_or_promotion_blocker_population_changes",
                "governance_rent_calculation_changes",
                "self_modification_detection_logic_changes",
            ],
            "required_review": "meta_gate_plus_elevated_operator_review",
            "proposal_authority_granted": False,
        },
        "red_zone_policy": {
            "policy_status": status,
            "forbidden_targets": [
                "core_governance_promotion_gates",
                "authorization_record_creation_or_sealing_logic",
                "meta_gate_or_meta_gate_authorization_chain_controls",
                "continuity_spine_lane_creation_or_management_rules",
                "artifact_registry_core_registration_logic",
                "operator_review_bypass_or_self_authorization_mechanisms",
                "foundational_authority_lock_definitions",
                "rune_catalog_or_yggdrasil_core_routing_rules",
            ],
            "required_recommendation": "BLOCK_POLICY_VIOLATION",
            "required_promotion_blockers": [
                "red_zone_surface_targeted",
                "core_governance_surface_targeted",
                "self_authorization_path_detected",
            ],
            "proposal_authority_granted": False,
            "auto_rejection_execution_authorized": False,
        },
        "chain_outline": [
            {
                "step": "meta_gate_trigger_receipt",
                "required_artifact": "ShadowImprovementReceipt.v1",
                "required_state": "HOLD_FOR_META_GATE",
                "step_status": status,
                "artifact_creation_authorized": False,
            },
            {
                "step": "meta_gate_operator_review_request",
                "required_artifact": "future_review_request",
                "required_state": "HELD_FOR_OPERATOR",
                "step_status": status,
                "artifact_creation_authorized": False,
            },
            {
                "step": "meta_gate_operator_decision_record",
                "required_artifact": "future_operator_decision_record",
                "required_state": "APPROVE_META_GATE_OR_REJECT_OR_REQUEST_MORE_EVIDENCE",
                "step_status": status,
                "artifact_creation_authorized": False,
            },
            {
                "step": "meta_gate_authorization_record_plan",
                "required_artifact": "future_authorization_record_plan",
                "required_state": "PLAN_ONLY",
                "step_status": status,
                "artifact_creation_authorized": False,
            },
            {
                "step": "meta_gate_authorization_record_creation",
                "required_artifact": "future_authorization_record",
                "required_state": "REQUIRES_POSITIVE_OPERATOR_DECISION",
                "step_status": status,
                "artifact_creation_authorized": False,
            },
            {
                "step": "meta_gate_chain_seal_dry_run_and_real",
                "required_artifact": "future_chain_seal_receipts",
                "required_state": "DRY_RUN_THEN_REAL_WITH_OPERATOR_CONFIRMATION",
                "step_status": status,
                "artifact_creation_authorized": False,
            },
            {
                "step": "meta_gate_chain_compression_audit",
                "required_artifact": "future_compression_audit",
                "required_state": "OPTIONAL_RECOMMENDED",
                "step_status": status,
                "artifact_creation_authorized": False,
            },
            {
                "step": "post_meta_gate_promotion_gate",
                "required_artifact": "normal_canary_promotion_review",
                "required_state": "STANDARD_PROMOTION_GOVERNANCE_REQUIRED",
                "step_status": status,
                "artifact_creation_authorized": False,
            },
        ],
        "future_validation_requirements": [
            {
                "requirement": "harness_boundary_checker_must_classify_green_yellow_red_targets",
                "requirement_status": status,
                "implementation_authorized": False,
            },
            {
                "requirement": "red_zone_targets_must_emit_block_policy_violation",
                "requirement_status": status,
                "implementation_authorized": False,
            },
            {
                "requirement": "yellow_zone_targets_must_force_hold_for_meta_gate",
                "requirement_status": status,
                "implementation_authorized": False,
            },
            {
                "requirement": "missing_meta_gate_evidence_must_force_block_or_hold",
                "requirement_status": status,
                "implementation_authorized": False,
            },
            {
                "requirement": "codegen_spine_must_not_create_or_sign_own_meta_gate_records",
                "requirement_status": status,
                "implementation_authorized": False,
            },
        ],
        "implementation_blockers": [
            "meta_gate_authorization_record_template_plan_held_for_operator",
            "boundary_checker_implementation_denied",
            "red_zone_auto_rejection_execution_denied",
            "meta_gate_trigger_receipt_creation_denied",
            "meta_gate_operator_review_request_creation_denied",
            "meta_gate_operator_decision_record_creation_denied",
            "meta_gate_authorization_record_creation_denied",
            "meta_gate_chain_seal_creation_denied",
            "normal_canary_promotion_review_missing",
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
            "artifact_creation": False,
            "artifact_registry_registration": False,
            "auto_approval": False,
            "boundary_checker_implementation": False,
            "canary_promotion": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "continuity_spine_lane_creation": False,
            "execution": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "meta_gate_authorization_record_creation": False,
            "meta_gate_chain_seal_creation": False,
            "meta_gate_operator_decision_record_creation": False,
            "meta_gate_operator_review_request_creation": False,
            "notion_writeback": False,
            "operator_attestation_creation": False,
            "queue_mutation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "self_authorization": False,
            "self_sealing": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Self-Improvement Boundary Policy Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        "- self_improvement_boundary_policy_plan_status: "
        f"{packet['self_improvement_boundary_policy_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Meta-Gate Triggers",
    ]
    for trigger in packet.get("meta_gate_triggers", []):
        if isinstance(trigger, Mapping):
            lines.append(
                f"- {trigger['trigger']}: routing_authorized={trigger['routing_authorized']}"
            )
    lines.extend(["", "## Red Zone"])
    for item in packet.get("red_zone_policy", {}).get("forbidden_targets", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Chain Outline"])
    for step in packet.get("chain_outline", []):
        if isinstance(step, Mapping):
            lines.append(
                f"- {step['step']}: artifact_creation_authorized="
                f"{step['artifact_creation_authorized']}"
            )
    lines.extend(["", "## Implementation Blockers"])
    for blocker in packet.get("implementation_blockers", []):
        lines.append(f"- {blocker}")
    return lines


def write_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_self_improvement_boundary_policy_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
