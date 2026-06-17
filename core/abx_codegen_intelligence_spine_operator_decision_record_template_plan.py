from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_harness_interface_spec_plan import (
    OUT_JSON as SOURCE_HARNESS_INTERFACE_SPEC_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineOperatorDecisionRecordTemplatePlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_OPERATOR_DECISION_RECORD_TEMPLATE_PLAN_001"
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_operator_decision_record_template_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_operator_decision_record_template_plan_001.latest.md"
)

EXPECTED_SOURCE_STATUS = "ABX_CODEGEN_HARNESS_INTERFACE_SPEC_PLAN_HELD_FOR_OPERATOR"

NOTION_SPECS = [
    {
        "title": "Operator Decision Record Template - Codegen Intelligence (incl. Meta-Gate)",
        "page_id": "37d3e8ba-2f5c-8162-b008-f2b101f38cb2",
        "observed_as_of": "2026-06-12",
        "status": "Planning Template (Advisory)",
        "version": "v0.1",
        "timestamp_policy": "template_placeholder_only_no_wall_clock_generation",
    },
    {
        "title": "Operator Decision Record (ODR) Templates - Codegen Intelligence Spine",
        "page_id": "37d3e8ba-2f5c-819a-9f0b-e6eb1b53b0f5",
        "observed_as_of": "2026-06-12",
        "status": "Ready-to-use Templates",
        "version": "v1.0",
        "timestamp_policy": "template_placeholder_only_no_wall_clock_generation",
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


def build_abx_codegen_intelligence_spine_operator_decision_record_template_plan(
    *,
    repo_root: str | Path,
    source_harness_interface_spec_plan_path: str | Path = SOURCE_HARNESS_INTERFACE_SPEC_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_harness_interface_spec_plan_path).as_posix()
    source = _read_json(root / source_harness_interface_spec_plan_path)
    source_ready = (
        source.get("artifact_type") == "AbxCodegenIntelligenceSpineHarnessInterfaceSpecPlan.v1"
        and source.get("harness_interface_spec_plan_status") == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and source.get("safe_to_auto_continue") is False
        and source.get("execution_authority") is False
        and source.get("valid_for_implementation") is False
    )
    status = _planning_status(source_ready)

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "operator_decision_record_template_plan_status": (
            "ABX_CODEGEN_OPERATOR_DECISION_RECORD_TEMPLATE_PLAN_HELD_FOR_OPERATOR"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_notion_specs": [
            {**spec, "notion_writeback_performed": False} for spec in NOTION_SPECS
        ],
        "source_harness_interface_spec_plan": {
            "path": source_path,
            "hash": _sha256(root / source_harness_interface_spec_plan_path),
            "harness_interface_spec_plan_status": str(
                source.get("harness_interface_spec_plan_status", "NOT_COMPUTABLE")
            ),
            "source_ready": source_ready,
        },
        "template_families": [
            {
                "template_family": "standard_codegen_proposal_odr",
                "record_id_pattern": "ODR-CODEGEN-[source_observed_date]-[deterministic_sequence]",
                "decision_type": "Normal Proposal",
                "template_status": status,
                "record_creation_authorized": False,
            },
            {
                "template_family": "meta_gate_self_improvement_odr",
                "record_id_pattern": "ODR-META-CODEGEN-[source_observed_date]-[deterministic_sequence]",
                "decision_type": "Meta-Gate - Self-Improvement",
                "template_status": status,
                "record_creation_authorized": False,
            },
        ],
        "required_sections": [
            {
                "section": "proposal_summary",
                "required_fields": [
                    "proposal_type",
                    "target_surface",
                    "intent",
                    "self_modification_risk",
                ],
                "section_status": status,
            },
            {
                "section": "shadow_replay_results",
                "required_fields": [
                    "recommendation",
                    "promotion_blockers",
                    "replay_status",
                    "correctness_score",
                    "invariance_result",
                    "governance_compliance",
                ],
                "section_status": status,
            },
            {
                "section": "risk_assessment",
                "required_fields": ["governance_rent", "complexity_delta", "drift_risk"],
                "section_status": status,
            },
            {
                "section": "operator_decision",
                "required_fields": ["decision", "rationale", "conditions"],
                "section_status": status,
            },
            {
                "section": "authorization_and_provenance",
                "required_fields": [
                    "operator_attestation",
                    "decision_record_hash",
                    "continuity_lane",
                    "feeds_into",
                ],
                "section_status": status,
            },
            {
                "section": "attachments",
                "required_fields": [
                    "ImprovementProposal.v1",
                    "ShadowImprovementReceipt.v1",
                    "fixtures_or_test_vectors",
                ],
                "section_status": status,
            },
        ],
        "decision_vocabularies": {
            "standard_decisions": [
                "APPROVE",
                "REJECT",
                "REQUEST_REFINEMENT",
                "HOLD_FOR_FURTHER_EVIDENCE",
                "ESCALATE",
            ],
            "meta_gate_decisions": [
                "APPROVE_META_GATE",
                "REJECT",
                "REQUEST_ADDITIONAL_EVIDENCE",
                "REQUIRE_REFINED_PROPOSAL",
            ],
            "receipt_recommendations_referenced": [
                "PROMOTE_TO_CANARY",
                "HOLD_FOR_OPERATOR",
                "HOLD_FOR_META_GATE",
                "BLOCK_REPLAY_FAILURE",
                "BLOCK_POLICY_VIOLATION",
                "REJECT",
            ],
            "vocabulary_authority_granted": False,
        },
        "meta_gate_requirements": [
            {
                "requirement": "use_meta_gate_template_when_self_modification_risk_true",
                "requirement_status": status,
                "authorization_granted": False,
            },
            {
                "requirement": "use_meta_gate_template_when_recommendation_hold_for_meta_gate",
                "requirement_status": status,
                "authorization_granted": False,
            },
            {
                "requirement": "complete_full_meta_gate_authorization_chain_before_promotion_consideration",
                "requirement_status": status,
                "authorization_granted": False,
            },
            {
                "requirement": "state_that_meta_gate_odr_does_not_grant_promotion_authority",
                "requirement_status": status,
                "authorization_granted": False,
            },
        ],
        "provenance_requirements": [
            {
                "requirement": "operator_identity_or_attestation_required",
                "requirement_status": status,
                "record_creation_authorized": False,
            },
            {
                "requirement": "decision_record_hash_required_if_record_exists",
                "requirement_status": status,
                "record_creation_authorized": False,
            },
            {
                "requirement": "continuity_lane_reference_required",
                "requirement_status": status,
                "record_creation_authorized": False,
            },
            {
                "requirement": "promotion_blockers_must_be_populated_for_non_clean_promotion",
                "requirement_status": status,
                "record_creation_authorized": False,
            },
        ],
        "template_output_policy": {
            "canonical_template_surface_suitable": True,
            "canonical_template_artifact_emitted_by_this_plan": False,
            "operator_decision_record_emitted_by_this_plan": False,
            "meta_gate_authorization_record_emitted_by_this_plan": False,
            "artifact_registry_registration_authorized": False,
            "temporal_continuity_spine_update_authorized": False,
            "timestamp_generation_authorized": False,
            "template_placeholders_are_not_decision_evidence": True,
        },
        "implementation_blockers": [
            "harness_interface_spec_plan_held_for_operator",
            "operator_attestation_missing",
            "decision_record_creation_denied",
            "meta_gate_authorization_record_creation_denied",
            "temporal_continuity_spine_update_denied",
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
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "decision_record_creation": False,
            "execution": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "meta_gate_authorization": False,
            "meta_gate_authorization_record_creation": False,
            "notion_writeback": False,
            "operator_decision_authority": False,
            "queue_mutation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "shadow_replay_execution": False,
            "temporal_continuity_spine_update": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_operator_decision_record_template_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_operator_decision_record_template_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Operator Decision Record Template Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        "- operator_decision_record_template_plan_status: "
        f"{packet['operator_decision_record_template_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Template Families",
    ]
    for family in packet.get("template_families", []):
        if isinstance(family, Mapping):
            lines.append(
                f"- {family['template_family']}: {family['template_status']} "
                f"(record_creation_authorized={family['record_creation_authorized']})"
            )
    lines.extend(["", "## Meta-Gate Requirements"])
    for requirement in packet.get("meta_gate_requirements", []):
        if isinstance(requirement, Mapping):
            lines.append(
                f"- {requirement['requirement']}: "
                f"authorization_granted={requirement['authorization_granted']}"
            )
    lines.extend(["", "## Implementation Blockers"])
    for blocker in packet.get("implementation_blockers", []):
        lines.append(f"- {blocker}")
    return lines


def write_abx_codegen_intelligence_spine_operator_decision_record_template_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_operator_decision_record_template_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
