from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_operator_decision_record_template_plan import (
    OUT_JSON as SOURCE_OPERATOR_DECISION_RECORD_TEMPLATE_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineMetaGateAuthorizationRecordTemplatePlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_META_GATE_AUTHORIZATION_RECORD_TEMPLATE_PLAN_001"
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan_001.latest.md"
)

EXPECTED_SOURCE_STATUS = "ABX_CODEGEN_OPERATOR_DECISION_RECORD_TEMPLATE_PLAN_HELD_FOR_OPERATOR"

NOTION_SPECS = [
    {
        "title": "Meta-Gate Authorization Record Template - Codegen Intelligence Spine",
        "page_id": "37d3e8ba-2f5c-816c-a655-e99aaeb3652d",
        "observed_as_of": "2026-06-12",
        "status": "Planning Template (Advisory)",
        "version": "v0.1",
        "timestamp_policy": "template_placeholder_only_no_wall_clock_generation",
    },
    {
        "title": "Meta-Gate Authorization Chain Seal Template - Codegen Intelligence Spine",
        "page_id": "37d3e8ba-2f5c-813c-aa30-d9f904bc5527",
        "observed_as_of": "2026-06-12",
        "status": "Planning Template (Advisory)",
        "version": "v0.1",
        "timestamp_policy": "template_placeholder_only_no_wall_clock_generation",
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
    return "TEMPLATE_DEFINED_HELD_FOR_OPERATOR" if source_ready else "NOT_COMPUTABLE"


def build_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan(
    *,
    repo_root: str | Path,
    source_operator_decision_record_template_plan_path: str
    | Path = SOURCE_OPERATOR_DECISION_RECORD_TEMPLATE_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_operator_decision_record_template_plan_path).as_posix()
    source = _read_json(root / source_operator_decision_record_template_plan_path)
    source_ready = (
        source.get("artifact_type")
        == "AbxCodegenIntelligenceSpineOperatorDecisionRecordTemplatePlan.v1"
        and source.get("operator_decision_record_template_plan_status")
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
        "meta_gate_authorization_record_template_plan_status": (
            "ABX_CODEGEN_META_GATE_AUTHORIZATION_RECORD_TEMPLATE_PLAN_HELD_FOR_OPERATOR"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_notion_specs": [
            {**spec, "notion_writeback_performed": False} for spec in NOTION_SPECS
        ],
        "source_operator_decision_record_template_plan": {
            "path": source_path,
            "hash": _sha256(root / source_operator_decision_record_template_plan_path),
            "operator_decision_record_template_plan_status": str(
                source.get("operator_decision_record_template_plan_status", "NOT_COMPUTABLE")
            ),
            "source_ready": source_ready,
        },
        "authorization_record_template": {
            "record_id_pattern": "MGAUTH-CODEGEN-[source_observed_date]-[deterministic_sequence]",
            "template_status": status,
            "required_sections": [
                "authorization_summary",
                "review_evidence",
                "authorization_scope",
                "provenance_and_linkage",
                "operator_attestation",
                "conditions_and_safeguards",
                "next_steps_in_chain",
            ],
            "allowed_scope_template_text": [
                "progression_to_meta_gate_authorization_chain_seal_step",
                "creation_of_downstream_meta_gate_authorization_record_creation_artifact",
                "consideration_for_canary_promotion_only_after_successful_seal",
            ],
            "record_creation_authorized": False,
            "continuation_authority_granted": False,
        },
        "chain_seal_template": {
            "dry_run_seal_id_pattern": (
                "MGSEAL-DRY-CODEGEN-[source_observed_date]-[deterministic_sequence]"
            ),
            "real_seal_id_pattern": (
                "MGSEAL-REAL-CODEGEN-[source_observed_date]-[deterministic_sequence]"
            ),
            "template_status": status,
            "seal_phases": ["dry_run", "operator_review", "real_seal"],
            "post_seal_allowed_step": "normal_canary_promotion_gate_review_only",
            "dry_run_creation_authorized": False,
            "real_seal_creation_authorized": False,
            "post_seal_promotion_authority_granted": False,
        },
        "scope_boundary_policy": {
            "green_zone_examples": [
                "packet_schemas_and_validation_rules_with_meta_gate_approval",
                "harness_implementation_logic",
                "fixture_generation_and_test_vector_logic",
                "self_related_documentation_and_planning_surfaces",
                "projection_only_aal_viz_or_oracle_integration_points",
            ],
            "yellow_zone_extra_scrutiny": [
                "proof_flag_definition_changes",
                "recommendation_or_promotion_blocker_population_changes",
                "governance_rent_calculation_changes",
                "self_modification_detection_logic_changes",
            ],
            "red_zone_forbidden": [
                "core_governance_promotion_gates",
                "authorization_record_creation_or_sealing_logic",
                "meta_gate_or_meta_gate_authorization_chain_controls",
                "continuity_spine_lane_creation_or_management_rules",
                "artifact_registry_core_registration_logic",
                "operator_review_bypass_or_self_authorization_mechanisms",
                "foundational_authority_lock_definitions",
                "rune_catalog_or_yggdrasil_core_routing_rules",
            ],
            "red_zone_recommendation": "BLOCK_POLICY_VIOLATION",
            "boundary_enforcement_authorized": False,
        },
        "required_upstream_evidence": [
            {
                "evidence": "ImprovementProposal.v1 hash",
                "required": True,
                "evidence_present_in_this_plan": False,
            },
            {
                "evidence": "ShadowImprovementReceipt.v1 with HOLD_FOR_META_GATE hash",
                "required": True,
                "evidence_present_in_this_plan": False,
            },
            {
                "evidence": "Positive Meta-Gate Operator Decision Record hash",
                "required": True,
                "evidence_present_in_this_plan": False,
            },
            {
                "evidence": "Real operator attestation",
                "required": True,
                "evidence_present_in_this_plan": False,
            },
        ],
        "explicit_denials": [
            "direct_promotion_denied",
            "runtime_mutation_denied",
            "canon_promotion_denied",
            "execution_authority_denied",
            "scheduler_changes_denied",
            "self_authorization_denied",
            "self_signing_denied",
            "self_sealing_denied",
            "operator_attestation_fabrication_denied",
            "artifact_registry_registration_denied",
            "temporal_continuity_spine_update_denied",
            "notion_writeback_denied",
            "github_writeback_denied",
        ],
        "template_output_policy": {
            "canonical_template_surface_suitable": True,
            "canonical_template_artifact_emitted_by_this_plan": False,
            "meta_gate_authorization_record_emitted_by_this_plan": False,
            "meta_gate_dry_run_seal_emitted_by_this_plan": False,
            "meta_gate_real_seal_emitted_by_this_plan": False,
            "operator_attestation_emitted_by_this_plan": False,
            "timestamp_generation_authorized": False,
            "template_placeholders_are_not_authorization_evidence": True,
        },
        "implementation_blockers": [
            "operator_decision_record_template_plan_held_for_operator",
            "positive_meta_gate_operator_decision_record_missing",
            "operator_attestation_missing",
            "meta_gate_authorization_record_creation_denied",
            "meta_gate_dry_run_seal_creation_denied",
            "meta_gate_real_seal_creation_denied",
            "normal_canary_promotion_gate_review_missing",
            "artifact_registry_registration_denied",
            "temporal_continuity_spine_update_denied",
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
            "boundary_enforcement": False,
            "canary_promotion": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "execution": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "meta_gate_authorization_record_creation": False,
            "meta_gate_continuation_authority": False,
            "meta_gate_dry_run_seal_creation": False,
            "meta_gate_real_seal_creation": False,
            "notion_writeback": False,
            "operator_attestation_creation": False,
            "queue_mutation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "self_authorization": False,
            "self_sealing": False,
            "temporal_continuity_spine_update": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Meta-Gate Authorization Record Template Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        "- meta_gate_authorization_record_template_plan_status: "
        f"{packet['meta_gate_authorization_record_template_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Authorization Record Template",
        f"- template_status: {packet['authorization_record_template']['template_status']}",
        "- record_creation_authorized: "
        f"{packet['authorization_record_template']['record_creation_authorized']}",
        "- continuation_authority_granted: "
        f"{packet['authorization_record_template']['continuation_authority_granted']}",
        "",
        "## Chain Seal Template",
        f"- template_status: {packet['chain_seal_template']['template_status']}",
        "- dry_run_creation_authorized: "
        f"{packet['chain_seal_template']['dry_run_creation_authorized']}",
        "- real_seal_creation_authorized: "
        f"{packet['chain_seal_template']['real_seal_creation_authorized']}",
        "",
        "## Red Zone",
    ]
    for item in packet.get("scope_boundary_policy", {}).get("red_zone_forbidden", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Implementation Blockers"])
    for blocker in packet.get("implementation_blockers", []):
        lines.append(f"- {blocker}")
    return lines


def write_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
