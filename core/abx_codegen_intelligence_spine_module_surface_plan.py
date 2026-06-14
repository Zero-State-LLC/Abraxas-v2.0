from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_object_model_schema_plan import (
    OUT_JSON as SOURCE_OBJECT_MODEL_SCHEMA_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineModuleSurfacePlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_MODULE_SURFACE_PLAN_001"
OUT_JSON = "out/audit/abx_codegen_intelligence_spine_module_surface_plan_001.latest.json"
OUT_MD = "out/audit/abx_codegen_intelligence_spine_module_surface_plan_001.latest.md"

EXPECTED_SOURCE_STATUS = "ABX_CODEGEN_OBJECT_MODEL_SCHEMA_PLAN_HELD_FOR_OPERATOR"


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
    return "MODULE_SURFACE_DEFINED_HELD_FOR_OPERATOR" if source_ready else "NOT_COMPUTABLE"


def build_abx_codegen_intelligence_spine_module_surface_plan(
    *,
    repo_root: str | Path,
    source_object_model_schema_plan_path: str
    | Path = SOURCE_OBJECT_MODEL_SCHEMA_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_object_model_schema_plan_path).as_posix()
    source = _read_json(root / source_object_model_schema_plan_path)
    source_ready = (
        source.get("artifact_type") == "AbxCodegenIntelligenceSpineObjectModelSchemaPlan.v1"
        and source.get("object_model_schema_plan_status") == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and source.get("safe_to_auto_continue") is False
        and source.get("execution_authority") is False
        and source.get("valid_for_implementation") is False
    )
    status = _planning_status(source_ready)

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "module_surface_plan_status": (
            "ABX_CODEGEN_MODULE_SURFACE_PLAN_HELD_FOR_OPERATOR"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_object_model_schema_plan": {
            "path": source_path,
            "hash": _sha256(root / source_object_model_schema_plan_path),
            "object_model_schema_plan_status": str(
                source.get("object_model_schema_plan_status", "NOT_COMPUTABLE")
            ),
            "source_ready": source_ready,
        },
        "planned_module_namespace": {
            "preferred_directory": "core/codegen",
            "namespace_creation_authorized": False,
            "module_file_creation_authorized": False,
            "reason": "canon_shadow_formalization_names_responsibilities_but_current_lane_is_plan_only",
        },
        "planned_modules": [
            {
                "module": "core/codegen/patch_contract.py",
                "responsibility": "PatchContract.v1 builder and canonical serializer",
                "depends_on_schema": "PatchContract.v1",
                "module_status": status,
                "module_creation_authorized": False,
            },
            {
                "module": "core/codegen/code_drop_envelope.py",
                "responsibility": "CodeDropEnvelope.v1 builder and file-scope envelope planner",
                "depends_on_schema": "CodeDropEnvelope.v1",
                "module_status": status,
                "module_creation_authorized": False,
            },
            {
                "module": "core/codegen/incremental_patch_enforcer.py",
                "responsibility": "Incremental patch only scope checks and broad rewrite rejection",
                "depends_on_schema": "CodeDropEnvelope.v1",
                "module_status": status,
                "module_creation_authorized": False,
            },
            {
                "module": "core/codegen/policy_reviewer.py",
                "responsibility": "Authority drift, scope drift, validation gap, and forbidden mutation review",
                "depends_on_schema": "PolicyReviewPacket.v1",
                "module_status": status,
                "module_creation_authorized": False,
            },
            {
                "module": "core/codegen/repo_state_binder.py",
                "responsibility": "Repo audit reference binding before handoff readiness",
                "depends_on_schema": "CodegenHandoffPacket.v1",
                "module_status": status,
                "module_creation_authorized": False,
            },
            {
                "module": "core/codegen/seal_validator.py",
                "responsibility": "Final seal expectation validation without CI certification authority",
                "depends_on_schema": "CodegenHandoffPacket.v1",
                "module_status": status,
                "module_creation_authorized": False,
            },
            {
                "module": "core/codegen/handoff_packet.py",
                "responsibility": "CodegenHandoffPacket.v1 builder and prompt envelope assembler",
                "depends_on_schema": "CodegenHandoffPacket.v1",
                "module_status": status,
                "module_creation_authorized": False,
            },
            {
                "module": "core/codegen/shadow_router.py",
                "responsibility": "Advisory routing from stable research/spec surfaces into patch-contract planning",
                "depends_on_schema": "PolicyReviewPacket.v1",
                "module_status": status,
                "module_creation_authorized": False,
            },
        ],
        "planned_scripts": [
            {
                "script": "scripts/run_codegen_contract_audit.py",
                "purpose": "emit advisory contract audit for planned codegen packets",
                "script_creation_authorized": False,
            },
            {
                "script": "scripts/run_codegen_handoff_packet.py",
                "purpose": "emit advisory handoff packet once schemas/builders are separately authorized",
                "script_creation_authorized": False,
            },
        ],
        "planned_tests": [
            {
                "test": "tests/codegen/test_patch_contract.py",
                "covers": "deterministic PatchContract.v1 serialization",
                "test_creation_authorized": False,
            },
            {
                "test": "tests/codegen/test_code_drop_envelope.py",
                "covers": "deterministic envelope hashing and file allow/deny lists",
                "test_creation_authorized": False,
            },
            {
                "test": "tests/codegen/test_incremental_patch_enforcer.py",
                "covers": "broad rewrite and unrelated edit rejection",
                "test_creation_authorized": False,
            },
            {
                "test": "tests/codegen/test_policy_reviewer.py",
                "covers": "authority drift and forbidden mutation flags",
                "test_creation_authorized": False,
            },
            {
                "test": "tests/codegen/test_codegen_handoff_packet.py",
                "covers": "repo audit refs, validation commands, governance locks, and final status",
                "test_creation_authorized": False,
            },
            {
                "test": "tests/codegen/test_codegen_authority_locks.py",
                "covers": "no autonomous patch application, promotion, forecast routing, canon mutation, or execution authority",
                "test_creation_authorized": False,
            },
        ],
        "validation_groups": [
            {"group": "deterministic_patch_contracts", "status": status},
            {"group": "deterministic_hashing", "status": status},
            {"group": "fail_closed_missing_repo_audit_provenance_tests", "status": status},
            {"group": "incremental_patch_enforcement", "status": status},
            {"group": "adversarial_authority_drift_detection", "status": status},
            {"group": "operator_review_required", "status": status},
            {"group": "no_autonomous_patch_application", "status": status},
            {"group": "no_forecast_routing", "status": status},
            {"group": "no_canon_mutation", "status": status},
            {"group": "no_execution_authority", "status": status},
        ],
        "implementation_blockers": [
            "object_model_schema_plan_held_for_operator",
            "core_codegen_namespace_creation_denied",
            "module_file_creation_denied",
            "script_creation_denied",
            "test_creation_denied",
            "schema_creation_denied",
            "builder_creation_denied",
            "handoff_packet_creation_denied",
            "implementation_prompt_emission_denied",
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
            "builder_creation": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "core_codegen_namespace_creation": False,
            "execution": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "handoff_packet_creation": False,
            "implementation_prompt_emission": False,
            "module_file_creation": False,
            "notion_writeback": False,
            "queue_mutation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "schema_creation": False,
            "script_creation": False,
            "test_creation": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_module_surface_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_module_surface_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Module Surface Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- module_surface_plan_status: {packet['module_surface_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Planned Modules",
    ]
    for module in packet.get("planned_modules", []):
        if isinstance(module, Mapping):
            lines.append(
                f"- {module['module']}: module_creation_authorized="
                f"{module['module_creation_authorized']}"
            )
    lines.extend(["", "## Implementation Blockers"])
    for blocker in packet.get("implementation_blockers", []):
        lines.append(f"- {blocker}")
    return lines


def write_abx_codegen_intelligence_spine_module_surface_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(render_abx_codegen_intelligence_spine_module_surface_plan_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
