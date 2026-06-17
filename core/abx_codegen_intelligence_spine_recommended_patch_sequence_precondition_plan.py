from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_phase1_implementation_boundary_review import (
    OUT_JSON as SOURCE_PHASE1_BOUNDARY_REVIEW_JSON,
)
from core.abx_codegen_intelligence_spine_schema_master_registry_alignment_plan import (
    OUT_JSON as SOURCE_SCHEMA_MASTER_ALIGNMENT_PLAN_JSON,
)
from core.abx_codegen_phase1_operator_review_request import (
    REQUEST_JSON_PATH as SOURCE_PHASE1_OPERATOR_REVIEW_REQUEST_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = (
    "AbxCodegenIntelligenceSpineRecommendedPatchSequencePreconditionPlan.v1"
)
PLAN_ID = (
    "ABX_CODEGEN_INTELLIGENCE_SPINE_RECOMMENDED_PATCH_SEQUENCE_PRECONDITION_PLAN_001"
)
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan_001."
    "latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan_001."
    "latest.md"
)

EXPECTED_SCHEMA_MASTER_STATUS = (
    "ABX_CODEGEN_SCHEMA_MASTER_REGISTRY_ALIGNMENT_PLAN_HELD_FOR_OPERATOR"
)
EXPECTED_PHASE1_BOUNDARY_STATUS = (
    "ABX_CODEGEN_PHASE1_IMPLEMENTATION_BOUNDARY_REVIEW_HELD_FOR_OPERATOR"
)
EXPECTED_OPERATOR_REVIEW_STATUS = "ABX_CODEGEN_PHASE1_OPERATOR_REVIEW_REQUEST_HELD"

NOTION_CANON_SHADOW_FORMALIZATION = {
    "title": "ABX_CODEGEN_INTELLIGENCE_SPINE_001 - Canon-Shadow Subsystem Formalization",
    "page_id": "3713e8ba-2f5c-81ee-b7e6-c0542b9859a4",
    "observed_as_of": "2026-05-31",
    "recommended_patch_name": "PATCH-ABX-CODEGEN-INTELLIGENCE-SPINE-001",
    "patch_class_directive": "IMPLEMENTATION_PLAN_first_then_IMPLEMENTATION_after_repo_audit",
    "authority": "ADVISORY_ONLY_NON_AUTHORITATIVE_SHADOW_ONLY",
    "notion_writeback_performed": False,
}

PATCH_SEQUENCE = [
    (
        "audit_existing_codegen_modules",
        "Audit repo for existing codegen modules and prompt or patch contract utilities.",
    ),
    (
        "avoid_duplicate_codegen_authority_surfaces",
        "Extend existing modules where appropriate and avoid duplicate authority surfaces.",
    ),
    (
        "add_or_align_contracts_codegen_schemas",
        "Add or align contracts/codegen schemas only after explicit authorization.",
    ),
    ("add_patch_contract_builder", "Add PatchContract.v1 builder."),
    ("add_code_drop_envelope_builder", "Add CodeDropEnvelope.v1 builder."),
    ("add_policy_review_packet_builder", "Add PolicyReviewPacket.v1 builder."),
    (
        "add_incremental_patch_enforcer",
        "Add IncrementalPatchEnforcer for broad rewrite and unrelated edit rejection.",
    ),
    (
        "add_repo_state_binder_and_seal_validator",
        "Add RepoStateBinder and SealValidator.",
    ),
    ("add_codegen_handoff_packet_builder", "Add CodegenHandoffPacket.v1 builder."),
    (
        "add_golden_tests",
        "Add determinism, missing audit, missing tests, forbidden mutation, and "
        "no-authority escalation tests.",
    ),
    (
        "update_docs",
        "Update README, AGENTS.md, PLANS.md, and changelog after authorized work.",
    ),
]

PRECONDITION_GROUPS = [
    (
        "schema_authorization",
        [
            "contracts_codegen_namespace_authorization_record",
            "PatchContract.v1_schema_creation_authorization",
            "CodeDropEnvelope.v1_schema_creation_authorization",
            "PolicyReviewPacket.v1_schema_creation_authorization",
            "CodegenHandoffPacket.v1_schema_creation_authorization",
        ],
    ),
    (
        "operator_authorization",
        [
            "operator_decision_record_with_human_rationale",
            "operator_attestation",
            "separate_authorization_record",
            "phase1_or_full_patch_scope_approval",
        ],
    ),
    (
        "validation_authorization",
        [
            "canonical_golden_fixture_creation_authorization",
            "contracts_codegen_schema_validation_authorization",
            "no_authority_escalation_test_authorization",
            "generated_artifact_registry_registration_authorization",
        ],
    ),
    (
        "runtime_containment",
        [
            "no_shadow_replay_execution",
            "no_runtime_mutation",
            "no_canon_mutation",
            "no_forecast_routing",
            "no_patch_application",
        ],
    ),
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


def _status(sources_ready: bool) -> str:
    if sources_ready:
        return "PRECONDITION_DEFINED_HELD_FOR_OPERATOR"
    return "NOT_COMPUTABLE"


def build_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan(
    *,
    repo_root: str | Path,
    source_schema_master_registry_alignment_plan_path: str
    | Path = SOURCE_SCHEMA_MASTER_ALIGNMENT_PLAN_JSON,
    source_phase1_implementation_boundary_review_path: str
    | Path = SOURCE_PHASE1_BOUNDARY_REVIEW_JSON,
    source_phase1_operator_review_request_path: str
    | Path = SOURCE_PHASE1_OPERATOR_REVIEW_REQUEST_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    schema_path = Path(source_schema_master_registry_alignment_plan_path).as_posix()
    boundary_path = Path(source_phase1_implementation_boundary_review_path).as_posix()
    operator_path = Path(source_phase1_operator_review_request_path).as_posix()

    schema_source = _read_json(root / source_schema_master_registry_alignment_plan_path)
    boundary_source = _read_json(root / source_phase1_implementation_boundary_review_path)
    operator_source = _read_json(root / source_phase1_operator_review_request_path)

    schema_ready = (
        schema_source.get("artifact_type")
        == "AbxCodegenIntelligenceSpineSchemaMasterRegistryAlignmentPlan.v1"
        and schema_source.get("schema_master_registry_alignment_plan_status")
        == EXPECTED_SCHEMA_MASTER_STATUS
        and schema_source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and schema_source.get("safe_to_auto_continue") is False
        and schema_source.get("execution_authority") is False
        and schema_source.get("valid_for_implementation") is False
    )
    boundary_ready = (
        boundary_source.get("artifact_type")
        == "AbxCodegenIntelligenceSpinePhase1ImplementationBoundaryReview.v1"
        and boundary_source.get("phase1_implementation_boundary_review_status")
        == EXPECTED_PHASE1_BOUNDARY_STATUS
        and boundary_source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and boundary_source.get("safe_to_auto_continue") is False
        and boundary_source.get("execution_authority") is False
        and boundary_source.get("valid_for_implementation") is False
    )
    operator_ready = (
        operator_source.get("schema_version")
        == "AbxCodegenPhase1OperatorReviewRequest.v1"
        and operator_source.get("status") == EXPECTED_OPERATOR_REVIEW_STATUS
        and operator_source.get("recommended_next_patch") == "NOT_COMPUTABLE"
        and operator_source.get("safe_to_auto_continue") is False
        and operator_source.get("execution_authority") is False
        and operator_source.get("valid_for_implementation") is False
    )
    sources_ready = schema_ready and boundary_ready and operator_ready
    row_status = _status(sources_ready)

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "recommended_patch_sequence_precondition_plan_status": (
            "ABX_CODEGEN_RECOMMENDED_PATCH_SEQUENCE_PRECONDITION_PLAN_HELD_FOR_OPERATOR"
            if sources_ready
            else "NOT_COMPUTABLE"
        ),
        "source_notion_canon_shadow_formalization": NOTION_CANON_SHADOW_FORMALIZATION,
        "source_schema_master_registry_alignment_plan": {
            "path": schema_path,
            "hash": _sha256(root / source_schema_master_registry_alignment_plan_path),
            "schema_master_registry_alignment_plan_status": str(
                schema_source.get(
                    "schema_master_registry_alignment_plan_status", "NOT_COMPUTABLE"
                )
            ),
            "source_ready": schema_ready,
        },
        "source_phase1_implementation_boundary_review": {
            "path": boundary_path,
            "hash": _sha256(root / source_phase1_implementation_boundary_review_path),
            "phase1_implementation_boundary_review_status": str(
                boundary_source.get(
                    "phase1_implementation_boundary_review_status", "NOT_COMPUTABLE"
                )
            ),
            "source_ready": boundary_ready,
        },
        "source_phase1_operator_review_request": {
            "path": operator_path,
            "hash": _sha256(root / source_phase1_operator_review_request_path),
            "status": str(operator_source.get("status", "NOT_COMPUTABLE")),
            "source_ready": operator_ready,
        },
        "recommended_patch_sequence": [
            {
                "sequence_index": index,
                "sequence_step": step,
                "summary": summary,
                "step_status": row_status,
                "authorized_in_this_plan": False,
            }
            for index, (step, summary) in enumerate(PATCH_SEQUENCE, start=1)
        ],
        "precondition_groups": [
            {
                "group": group,
                "requirements": [
                    {
                        "requirement": requirement,
                        "requirement_status": row_status,
                        "satisfied": False,
                    }
                    for requirement in requirements
                ],
                "group_status": row_status,
            }
            for group, requirements in PRECONDITION_GROUPS
        ],
        "implementation_readiness_assessment": {
            "notion_patch_class": "IMPLEMENTATION_PLAN_first",
            "schema_master_alignment_ready": schema_ready,
            "phase1_boundary_review_ready": boundary_ready,
            "phase1_operator_review_request_held": operator_ready,
            "operator_authorization_present": False,
            "schema_creation_authorization_present": False,
            "module_creation_authorization_present": False,
            "implementation_readiness": "HELD_FOR_OPERATOR",
            "reason": (
                "notion_recommended_patch_sequence_is_mapped_but_operator_and_schema_"
                "authorization_records_are_absent"
            ),
        },
        "blocked_actions": [
            "contracts_codegen_directory_creation",
            "core_codegen_directory_creation",
            "patch_contract_schema_creation",
            "code_drop_envelope_schema_creation",
            "policy_review_packet_schema_creation",
            "codegen_handoff_packet_schema_creation",
            "patch_contract_builder_creation",
            "code_drop_envelope_builder_creation",
            "policy_review_packet_builder_creation",
            "incremental_patch_enforcer_creation",
            "repo_state_binder_creation",
            "seal_validator_creation",
            "codegen_handoff_packet_builder_creation",
            "golden_test_creation",
            "implementation_prompt_emission",
            "shadow_replay_execution",
            "patch_application",
            "notion_writeback",
            "github_writeback",
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
            "authorization_record_creation": False,
            "auto_approval": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "contracts_codegen_directory_creation": False,
            "core_codegen_directory_creation": False,
            "execution": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "golden_test_creation": False,
            "implementation_prompt_emission": False,
            "module_creation": False,
            "notion_writeback": False,
            "operator_attestation": False,
            "operator_decision_record_creation": False,
            "patch_application": False,
            "queue_mutation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "schema_creation": False,
            "shadow_replay_execution": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Recommended Patch Sequence Precondition Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        "- recommended_patch_sequence_precondition_plan_status: "
        f"{packet['recommended_patch_sequence_precondition_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Recommended Patch Sequence",
    ]
    for step in packet.get("recommended_patch_sequence", []):
        if isinstance(step, Mapping):
            lines.append(
                f"- {step['sequence_index']}. {step['sequence_step']}: "
                f"{step['step_status']} "
                f"(authorized_in_this_plan={step['authorized_in_this_plan']})"
            )
    lines.extend(["", "## Precondition Groups"])
    for group in packet.get("precondition_groups", []):
        if isinstance(group, Mapping):
            lines.append(f"- {group['group']}: {group['group_status']}")
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- {action}")
    return lines


def write_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
