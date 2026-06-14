from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_module_surface_plan import (
    OUT_JSON as SOURCE_MODULE_SURFACE_PLAN_JSON,
)
from core.abx_codegen_intelligence_spine_object_model_schema_plan import (
    OUT_JSON as SOURCE_OBJECT_MODEL_SCHEMA_PLAN_JSON,
)
from core.abx_codegen_intelligence_spine_sample_fixture_normalization_plan import (
    OUT_JSON as SOURCE_SAMPLE_FIXTURE_NORMALIZATION_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineSchemaMasterRegistryAlignmentPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_SCHEMA_MASTER_REGISTRY_ALIGNMENT_PLAN_001"
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_schema_master_registry_alignment_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_schema_master_registry_alignment_plan_001.latest.md"
)

EXPECTED_OBJECT_MODEL_STATUS = "ABX_CODEGEN_OBJECT_MODEL_SCHEMA_PLAN_HELD_FOR_OPERATOR"
EXPECTED_MODULE_SURFACE_STATUS = "ABX_CODEGEN_MODULE_SURFACE_PLAN_HELD_FOR_OPERATOR"
EXPECTED_SAMPLE_FIXTURE_STATUS = (
    "ABX_CODEGEN_SAMPLE_FIXTURE_NORMALIZATION_PLAN_HELD_FOR_OPERATOR"
)

NOTION_SCHEMA_MASTER_REGISTRY = {
    "title": "ABX_SCHEMA_MASTER_REGISTRY_001 - Packet + Contract Schema Ledger",
    "page_id": "3713e8ba-2f5c-8126-806a-fc158bdd668f",
    "observed_as_of": "2026-06-12",
    "status": "SCHEMA_LEDGER_READY_ADVISORY_ONLY",
    "notion_writeback_performed": False,
}

REQUIRED_SCHEMA_FIELDS = [
    "schema_id",
    "version",
    "owner",
    "route",
    "used_by_runes",
    "direction",
    "repo_path",
    "required_fields",
    "governance_locks",
    "provenance_requirements",
    "not_computable_conditions",
    "golden_tests",
    "implementation_status",
]

REQUIRED_GOLDEN_TEST_CLASSES = [
    "schema_validation_success",
    "schema_validation_failure",
    "deterministic_serialization_hash",
    "governance_lock_preservation",
    "missing_provenance_failure",
    "not_computable_behavior",
    "forbidden_status_rejection",
    "route_rune_compatibility",
    "no_authority_escalation",
]

SCHEMA_REGISTRY_BINDINGS = [
    {
        "schema_id": "PatchContract.v1",
        "owner": "ABX_CODEGEN_INTELLIGENCE_SPINE",
        "route": "yggdrasil.codegen",
        "used_by_rune": "RUNE.CODEGEN.BUILD_PATCH_CONTRACT",
        "direction": "output",
        "repo_path": "contracts/codegen/patch_contract.v1.schema.json",
        "implementation_status": "PLANNED",
    },
    {
        "schema_id": "CodeDropEnvelope.v1",
        "owner": "ABX_CODEGEN_INTELLIGENCE_SPINE",
        "route": "yggdrasil.codegen",
        "used_by_rune": "RUNE.CODEGEN.BUILD_CODE_DROP_ENVELOPE",
        "direction": "output",
        "repo_path": "contracts/codegen/code_drop_envelope.v1.schema.json",
        "implementation_status": "PLANNED",
    },
    {
        "schema_id": "PolicyReviewPacket.v1",
        "owner": "ABX_CODEGEN_INTELLIGENCE_SPINE",
        "route": "yggdrasil.codegen",
        "used_by_rune": "RUNE.CODEGEN.POLICY_REVIEW",
        "direction": "output",
        "repo_path": "contracts/codegen/policy_review_packet.v1.schema.json",
        "implementation_status": "PLANNED",
    },
    {
        "schema_id": "CodegenHandoffPacket.v1",
        "owner": "ABX_CODEGEN_INTELLIGENCE_SPINE",
        "route": "yggdrasil.codegen",
        "used_by_rune": "RUNE.CODEGEN.BUILD_HANDOFF",
        "direction": "output",
        "repo_path": "contracts/codegen/codegen_handoff_packet.v1.schema.json",
        "implementation_status": "PLANNED",
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


def _binding_status(sources_ready: bool) -> str:
    if sources_ready:
        return "SCHEMA_MASTER_REGISTRY_BINDING_DEFINED_HELD_FOR_OPERATOR"
    return "NOT_COMPUTABLE"


def build_abx_codegen_intelligence_spine_schema_master_registry_alignment_plan(
    *,
    repo_root: str | Path,
    source_object_model_schema_plan_path: str
    | Path = SOURCE_OBJECT_MODEL_SCHEMA_PLAN_JSON,
    source_module_surface_plan_path: str | Path = SOURCE_MODULE_SURFACE_PLAN_JSON,
    source_sample_fixture_normalization_plan_path: str
    | Path = SOURCE_SAMPLE_FIXTURE_NORMALIZATION_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    object_model_path = Path(source_object_model_schema_plan_path).as_posix()
    module_surface_path = Path(source_module_surface_plan_path).as_posix()
    sample_fixture_path = Path(source_sample_fixture_normalization_plan_path).as_posix()

    object_model = _read_json(root / source_object_model_schema_plan_path)
    module_surface = _read_json(root / source_module_surface_plan_path)
    sample_fixture = _read_json(root / source_sample_fixture_normalization_plan_path)

    object_model_ready = (
        object_model.get("artifact_type")
        == "AbxCodegenIntelligenceSpineObjectModelSchemaPlan.v1"
        and object_model.get("object_model_schema_plan_status")
        == EXPECTED_OBJECT_MODEL_STATUS
        and object_model.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and object_model.get("safe_to_auto_continue") is False
        and object_model.get("execution_authority") is False
        and object_model.get("valid_for_implementation") is False
    )
    module_surface_ready = (
        module_surface.get("artifact_type")
        == "AbxCodegenIntelligenceSpineModuleSurfacePlan.v1"
        and module_surface.get("module_surface_plan_status")
        == EXPECTED_MODULE_SURFACE_STATUS
        and module_surface.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and module_surface.get("safe_to_auto_continue") is False
        and module_surface.get("execution_authority") is False
        and module_surface.get("valid_for_implementation") is False
    )
    sample_fixture_ready = (
        sample_fixture.get("artifact_type")
        == "AbxCodegenIntelligenceSpineSampleFixtureNormalizationPlan.v1"
        and sample_fixture.get("sample_fixture_normalization_plan_status")
        == EXPECTED_SAMPLE_FIXTURE_STATUS
        and sample_fixture.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and sample_fixture.get("safe_to_auto_continue") is False
        and sample_fixture.get("execution_authority") is False
        and sample_fixture.get("valid_for_implementation") is False
    )
    sources_ready = object_model_ready and module_surface_ready and sample_fixture_ready
    binding_status = _binding_status(sources_ready)

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "schema_master_registry_alignment_plan_status": (
            "ABX_CODEGEN_SCHEMA_MASTER_REGISTRY_ALIGNMENT_PLAN_HELD_FOR_OPERATOR"
            if sources_ready
            else "NOT_COMPUTABLE"
        ),
        "source_notion_schema_master_registry": NOTION_SCHEMA_MASTER_REGISTRY,
        "source_object_model_schema_plan": {
            "path": object_model_path,
            "hash": _sha256(root / source_object_model_schema_plan_path),
            "object_model_schema_plan_status": str(
                object_model.get("object_model_schema_plan_status", "NOT_COMPUTABLE")
            ),
            "source_ready": object_model_ready,
        },
        "source_module_surface_plan": {
            "path": module_surface_path,
            "hash": _sha256(root / source_module_surface_plan_path),
            "module_surface_plan_status": str(
                module_surface.get("module_surface_plan_status", "NOT_COMPUTABLE")
            ),
            "source_ready": module_surface_ready,
        },
        "source_sample_fixture_normalization_plan": {
            "path": sample_fixture_path,
            "hash": _sha256(root / source_sample_fixture_normalization_plan_path),
            "sample_fixture_normalization_plan_status": str(
                sample_fixture.get(
                    "sample_fixture_normalization_plan_status", "NOT_COMPUTABLE"
                )
            ),
            "source_ready": sample_fixture_ready,
        },
        "schema_registry_bindings": [
            {
                **binding,
                "binding_status": binding_status,
                "schema_creation_authorized": False,
                "runtime_binding_authorized": False,
                "rune_invocation_authorized": False,
                "implementation_status_promotion_authorized": False,
            }
            for binding in SCHEMA_REGISTRY_BINDINGS
        ],
        "required_schema_fields": REQUIRED_SCHEMA_FIELDS,
        "required_golden_test_classes": REQUIRED_GOLDEN_TEST_CLASSES,
        "implementation_sequence_position": {
            "registry_directive": (
                "codegen_schemas_after_route_rune_and_schema_conventions_stabilize"
            ),
            "sequence_status": binding_status,
            "sequence_execution_authorized": False,
            "schema_creation_authorized": False,
            "golden_test_creation_authorized": False,
            "runtime_behavior_authorized": False,
        },
        "alignment_findings": [
            {
                "finding": "object_model_schema_plan_names_the_four_planned_codegen_packets",
                "status": binding_status,
            },
            {
                "finding": "module_surface_plan_maps_planned_modules_to_packet_schemas",
                "status": binding_status,
            },
            {
                "finding": "schema_master_registry_keeps_codegen_entries_planned",
                "status": binding_status,
            },
            {
                "finding": "contracts_codegen_creation_remains_denied_by_current_lane",
                "status": binding_status,
            },
            {
                "finding": "sample_fixtures_require_normalized_golden_tests_before_schema_execution",
                "status": binding_status,
            },
        ],
        "blocked_actions": [
            "contracts_codegen_directory_creation",
            "patch_contract_schema_creation",
            "code_drop_envelope_schema_creation",
            "policy_review_packet_schema_creation",
            "codegen_handoff_packet_schema_creation",
            "runtime_behavior_creation",
            "rune_invocation",
            "golden_test_creation",
            "fixture_mutation",
            "schema_registry_implementation_status_promotion",
            "codegen_handoff_packet_creation",
            "patch_application",
            "operator_decision_record_creation",
            "authorization_record_creation",
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
            "execution": False,
            "file_writeback": False,
            "fixture_mutation": False,
            "forecast_routing": False,
            "github_writeback": False,
            "golden_test_creation": False,
            "implementation_status_promotion": False,
            "notion_writeback": False,
            "operator_decision_record_creation": False,
            "patch_application": False,
            "queue_mutation": False,
            "rune_invocation": False,
            "runtime_binding": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "schema_creation": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_schema_master_registry_alignment_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_schema_master_registry_alignment_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Schema Master Registry Alignment Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        "- schema_master_registry_alignment_plan_status: "
        f"{packet['schema_master_registry_alignment_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Schema Registry Bindings",
    ]
    for binding in packet.get("schema_registry_bindings", []):
        if isinstance(binding, Mapping):
            lines.append(
                f"- {binding['schema_id']} -> {binding['repo_path']} "
                f"({binding['binding_status']}, schema_creation_authorized="
                f"{binding['schema_creation_authorized']})"
            )
    lines.extend(["", "## Required Golden Test Classes"])
    for test_class in packet.get("required_golden_test_classes", []):
        lines.append(f"- {test_class}")
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- {action}")
    return lines


def write_abx_codegen_intelligence_spine_schema_master_registry_alignment_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_schema_master_registry_alignment_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
