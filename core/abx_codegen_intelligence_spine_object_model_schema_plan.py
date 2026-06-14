from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_canon_shadow_formalization_plan import (
    OUT_JSON as SOURCE_CANON_SHADOW_FORMALIZATION_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineObjectModelSchemaPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_OBJECT_MODEL_SCHEMA_PLAN_001"
OUT_JSON = "out/audit/abx_codegen_intelligence_spine_object_model_schema_plan_001.latest.json"
OUT_MD = "out/audit/abx_codegen_intelligence_spine_object_model_schema_plan_001.latest.md"

EXPECTED_SOURCE_STATUS = "ABX_CODEGEN_CANON_SHADOW_FORMALIZATION_PLAN_HELD_FOR_OPERATOR"


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
    return "SCHEMA_PLAN_DEFINED_HELD_FOR_OPERATOR" if source_ready else "NOT_COMPUTABLE"


def build_abx_codegen_intelligence_spine_object_model_schema_plan(
    *,
    repo_root: str | Path,
    source_canon_shadow_formalization_plan_path: str
    | Path = SOURCE_CANON_SHADOW_FORMALIZATION_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_canon_shadow_formalization_plan_path).as_posix()
    source = _read_json(root / source_canon_shadow_formalization_plan_path)
    source_ready = (
        source.get("artifact_type")
        == "AbxCodegenIntelligenceSpineCanonShadowFormalizationPlan.v1"
        and source.get("canon_shadow_formalization_plan_status") == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and source.get("safe_to_auto_continue") is False
        and source.get("execution_authority") is False
        and source.get("valid_for_implementation") is False
    )
    status = _planning_status(source_ready)

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "object_model_schema_plan_status": (
            "ABX_CODEGEN_OBJECT_MODEL_SCHEMA_PLAN_HELD_FOR_OPERATOR"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_canon_shadow_formalization_plan": {
            "path": source_path,
            "hash": _sha256(root / source_canon_shadow_formalization_plan_path),
            "canon_shadow_formalization_plan_status": str(
                source.get("canon_shadow_formalization_plan_status", "NOT_COMPUTABLE")
            ),
            "source_ready": source_ready,
        },
        "planned_contract_namespace": {
            "preferred_directory": "contracts/codegen",
            "namespace_creation_authorized": False,
            "schema_file_creation_authorized": False,
            "reason": "formalization_names_candidate_models_but_current_lane_is_plan_only",
        },
        "schema_plans": [
            {
                "schema_name": "PatchContract.v1",
                "planned_path": "contracts/codegen/patch_contract.v1.schema.json",
                "required_fields": [
                    "contract_id",
                    "patch_name",
                    "patch_class",
                    "primary_objective",
                    "secondary_objective",
                    "current_verified_state",
                    "out_of_scope",
                    "execution_slice",
                    "validation_groups",
                    "governance_locks",
                    "final_seal",
                    "provenance_hash",
                ],
                "schema_status": status,
                "schema_creation_authorized": False,
            },
            {
                "schema_name": "CodeDropEnvelope.v1",
                "planned_path": "contracts/codegen/code_drop_envelope.v1.schema.json",
                "required_fields": [
                    "envelope_id",
                    "patch_contract_ref",
                    "schemas_required",
                    "runes_required",
                    "files_allowed",
                    "files_forbidden",
                    "tests_required",
                    "docs_required",
                    "changelog_required",
                    "semantic_versioning_required",
                    "governance_locks",
                    "provenance_hash",
                ],
                "schema_status": status,
                "schema_creation_authorized": False,
            },
            {
                "schema_name": "PolicyReviewPacket.v1",
                "planned_path": "contracts/codegen/policy_review_packet.v1.schema.json",
                "required_fields": [
                    "review_id",
                    "patch_contract_ref",
                    "authority_drift_flags",
                    "scope_drift_flags",
                    "missing_validation_flags",
                    "duplicate_surface_flags",
                    "forbidden_mutation_flags",
                    "recommendation",
                    "governance_locks",
                    "provenance_hash",
                ],
                "schema_status": status,
                "schema_creation_authorized": False,
            },
            {
                "schema_name": "CodegenHandoffPacket.v1",
                "planned_path": "contracts/codegen/codegen_handoff_packet.v1.schema.json",
                "required_fields": [
                    "packet_id",
                    "patch_contract",
                    "code_drop_envelope",
                    "policy_review_packet",
                    "repo_audit_refs",
                    "recommended_prompt",
                    "validation_commands",
                    "governance_locks",
                    "provenance_hash",
                    "final_status",
                ],
                "schema_status": status,
                "schema_creation_authorized": False,
            },
        ],
        "shared_invariants": [
            {"invariant": "advisory_only_true", "status": status},
            {"invariant": "shadow_only_true", "status": status},
            {"invariant": "non_authoritative_true", "status": status},
            {"invariant": "operator_review_required_true", "status": status},
            {"invariant": "autonomous_patch_application_false", "status": status},
            {"invariant": "autonomous_promotion_false", "status": status},
            {"invariant": "forecast_routing_false", "status": status},
            {"invariant": "canon_mutation_false", "status": status},
            {"invariant": "runtime_mutation_false", "status": status},
            {"invariant": "execution_authority_false", "status": status},
        ],
        "validation_plan": [
            {"validation": "deterministic_schema_serialization", "status": status},
            {"validation": "required_governance_locks_present", "status": status},
            {"validation": "forbidden_final_statuses_rejected", "status": status},
            {"validation": "missing_repo_audit_fails_closed", "status": status},
            {"validation": "missing_tests_or_provenance_flagged", "status": status},
            {"validation": "broad_rewrite_scope_rejected", "status": status},
            {"validation": "authority_drift_detected", "status": status},
        ],
        "implementation_blockers": [
            "canon_shadow_formalization_plan_held_for_operator",
            "contracts_codegen_namespace_creation_denied",
            "patch_contract_schema_creation_denied",
            "code_drop_envelope_schema_creation_denied",
            "policy_review_packet_schema_creation_denied",
            "codegen_handoff_packet_schema_creation_denied",
            "builders_creation_denied",
            "runner_creation_denied",
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
            "builders_creation": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "contracts_codegen_namespace_creation": False,
            "execution": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "notion_writeback": False,
            "queue_mutation": False,
            "runner_creation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "schema_creation": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_object_model_schema_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_object_model_schema_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Object Model Schema Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- object_model_schema_plan_status: {packet['object_model_schema_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Schema Plans",
    ]
    for schema in packet.get("schema_plans", []):
        if isinstance(schema, Mapping):
            lines.append(
                f"- {schema['schema_name']}: {schema['planned_path']} "
                f"(schema_creation_authorized={schema['schema_creation_authorized']})"
            )
    lines.extend(["", "## Implementation Blockers"])
    for blocker in packet.get("implementation_blockers", []):
        lines.append(f"- {blocker}")
    return lines


def write_abx_codegen_intelligence_spine_object_model_schema_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(render_abx_codegen_intelligence_spine_object_model_schema_plan_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
