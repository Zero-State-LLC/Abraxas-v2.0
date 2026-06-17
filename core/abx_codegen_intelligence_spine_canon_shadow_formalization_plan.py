from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_governance_decision_vocabulary_plan import (
    OUT_JSON as SOURCE_GOVERNANCE_DECISION_VOCABULARY_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineCanonShadowFormalizationPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_CANON_SHADOW_FORMALIZATION_PLAN_001"
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_canon_shadow_formalization_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_canon_shadow_formalization_plan_001.latest.md"
)

EXPECTED_SOURCE_STATUS = "ABX_CODEGEN_GOVERNANCE_DECISION_VOCABULARY_PLAN_HELD_FOR_OPERATOR"

NOTION_SPECS = [
    {
        "title": "ABX_CODEGEN_INTELLIGENCE_SPINE_001 - Governed Recursive Self-Improvement Spec",
        "page_id": "37d3e8ba-2f5c-816d-8ccc-c0b46b9a2760",
        "observed_as_of": "2026-06-12",
        "status": "ADVISORY_DRAFT / PLANNING_ONLY",
        "version": "source_observed",
    },
    {
        "title": "ABX_CODEGEN_INTELLIGENCE_SPINE_001 - Canon-Shadow Subsystem Formalization",
        "page_id": "3713e8ba-2f5c-81ee-b7e6-c0542b9859a4",
        "observed_as_of": "2026-05-31",
        "status": "CANON-SHADOW",
        "version": "source_observed",
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
    return "FORMALIZATION_DEFINED_HELD_FOR_OPERATOR" if source_ready else "NOT_COMPUTABLE"


def build_abx_codegen_intelligence_spine_canon_shadow_formalization_plan(
    *,
    repo_root: str | Path,
    source_governance_decision_vocabulary_plan_path: str
    | Path = SOURCE_GOVERNANCE_DECISION_VOCABULARY_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_governance_decision_vocabulary_plan_path).as_posix()
    source = _read_json(root / source_governance_decision_vocabulary_plan_path)
    source_ready = (
        source.get("artifact_type")
        == "AbxCodegenIntelligenceSpineGovernanceDecisionVocabularyPlan.v1"
        and source.get("governance_decision_vocabulary_plan_status")
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
        "canon_shadow_formalization_plan_status": (
            "ABX_CODEGEN_CANON_SHADOW_FORMALIZATION_PLAN_HELD_FOR_OPERATOR"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_notion_specs": [
            {**spec, "notion_writeback_performed": False} for spec in NOTION_SPECS
        ],
        "source_governance_decision_vocabulary_plan": {
            "path": source_path,
            "hash": _sha256(root / source_governance_decision_vocabulary_plan_path),
            "governance_decision_vocabulary_plan_status": str(
                source.get("governance_decision_vocabulary_plan_status", "NOT_COMPUTABLE")
            ),
            "source_ready": source_ready,
        },
        "architectural_placement": {
            "placement": "outside_five_layer_runtime_stack",
            "five_layer_stack": ["INGEST", "BELIEF", "REPLAY", "PHASE", "VIZ"],
            "codegen_spine_flow": [
                "research_spec_repo_state",
                "patch_contract",
                "code_drop_envelope",
                "validation",
                "seal",
            ],
            "runtime_layer_authority_granted": False,
        },
        "subsystem_responsibilities": [
            {"responsibility": "patch_contract_compiler", "status": status},
            {"responsibility": "code_drop_envelope_builder", "status": status},
            {"responsibility": "incremental_patch_enforcer", "status": status},
            {"responsibility": "adversarial_policy_reviewer", "status": status},
            {"responsibility": "repo_state_binder", "status": status},
            {"responsibility": "seal_validator", "status": status},
        ],
        "candidate_object_models": [
            {
                "object_model": "PatchContract.v1",
                "planned_fields": [
                    "contract_id",
                    "patch_name",
                    "patch_class",
                    "primary_objective",
                    "execution_slice",
                    "validation_groups",
                    "governance_locks",
                    "final_seal",
                    "provenance_hash",
                ],
                "schema_creation_authorized": False,
            },
            {
                "object_model": "CodeDropEnvelope.v1",
                "planned_fields": [
                    "envelope_id",
                    "patch_contract_ref",
                    "schemas_required",
                    "files_allowed",
                    "files_forbidden",
                    "tests_required",
                    "docs_required",
                    "governance_locks",
                ],
                "schema_creation_authorized": False,
            },
            {
                "object_model": "PolicyReviewPacket.v1",
                "planned_fields": [
                    "review_id",
                    "patch_contract_ref",
                    "authority_drift_flags",
                    "scope_drift_flags",
                    "missing_validation_flags",
                    "forbidden_mutation_flags",
                    "recommendation",
                ],
                "schema_creation_authorized": False,
            },
            {
                "object_model": "CodegenHandoffPacket.v1",
                "planned_fields": [
                    "packet_id",
                    "patch_contract",
                    "code_drop_envelope",
                    "policy_review_packet",
                    "repo_audit_refs",
                    "recommended_prompt",
                    "validation_commands",
                    "final_status",
                ],
                "schema_creation_authorized": False,
            },
        ],
        "allowed_final_statuses": [
            "PATCH_CONTRACT_READY_ADVISORY_ONLY",
            "CODE_DROP_ENVELOPE_READY_ADVISORY_ONLY",
            "POLICY_REVIEW_REQUIRED",
            "REPO_AUDIT_REQUIRED",
            "IMPLEMENTATION_PROMPT_READY_ADVISORY_ONLY",
            "NOT_COMPUTABLE",
        ],
        "forbidden_final_statuses": [
            "PATCH_APPLIED",
            "CANON_PROMOTED",
            "FORECAST_AUTHORIZED",
            "EXECUTION_READY",
            "AUTONOMOUSLY_APPROVED",
            "CI_CERTIFIED_WITHOUT_EVIDENCE",
        ],
        "validation_requirements": [
            {"requirement": "deterministic_patch_contract_serialization", "status": status},
            {"requirement": "deterministic_code_drop_envelope_hashing", "status": status},
            {"requirement": "missing_repo_audit_returns_required_or_not_computable", "status": status},
            {"requirement": "missing_tests_are_flagged", "status": status},
            {"requirement": "forbidden_mutation_is_flagged", "status": status},
            {"requirement": "operator_review_remains_required", "status": status},
            {"requirement": "autonomous_patch_application_remains_false", "status": status},
            {"requirement": "canon_mutation_remains_false", "status": status},
        ],
        "implementation_blockers": [
            "governance_decision_vocabulary_plan_held_for_operator",
            "patch_contract_schema_creation_denied",
            "code_drop_envelope_schema_creation_denied",
            "policy_review_packet_schema_creation_denied",
            "codegen_handoff_packet_schema_creation_denied",
            "implementation_prompt_emission_denied",
            "autonomous_patch_application_denied",
            "artifact_registry_registration_denied",
            "notion_writeback_denied",
            "github_writeback_denied",
        ],
        "recommended_next_lane": "NOT_COMPUTABLE",
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "shadow_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "authority_locks": {
            "artifact_registry_registration": False,
            "autonomous_patch_application": False,
            "autonomous_promotion": False,
            "canon_mutation": False,
            "code_drop_envelope_creation": False,
            "code_generation": False,
            "code_mutation": False,
            "execution": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "implementation_prompt_emission": False,
            "notion_writeback": False,
            "patch_contract_creation": False,
            "policy_review_packet_creation": False,
            "queue_mutation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "schema_creation": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_canon_shadow_formalization_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_canon_shadow_formalization_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Canon Shadow Formalization Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- canon_shadow_formalization_plan_status: {packet['canon_shadow_formalization_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Candidate Object Models",
    ]
    for item in packet.get("candidate_object_models", []):
        if isinstance(item, Mapping):
            lines.append(
                f"- {item['object_model']}: schema_creation_authorized="
                f"{item['schema_creation_authorized']}"
            )
    lines.extend(["", "## Forbidden Statuses"])
    for status in packet.get("forbidden_final_statuses", []):
        lines.append(f"- {status}")
    lines.extend(["", "## Implementation Blockers"])
    for blocker in packet.get("implementation_blockers", []):
        lines.append(f"- {blocker}")
    return lines


def write_abx_codegen_intelligence_spine_canon_shadow_formalization_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(render_abx_codegen_intelligence_spine_canon_shadow_formalization_plan_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
