from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_continuity_lane_conventions_plan import (
    OUT_JSON as SOURCE_CONTINUITY_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineArtifactRegistryIntegrationPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_ARTIFACT_REGISTRY_INTEGRATION_PLAN_001"
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_artifact_registry_integration_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_artifact_registry_integration_plan_001.latest.md"
)

NOTION_SPEC = {
    "title": "Artifact Registry Integration - Codegen Intelligence Spine",
    "page_id": "37d3e8ba-2f5c-8111-811f-e95fcdff4e64",
    "observed_as_of": "2026-06-12",
    "status": "Planning Spec (Advisory)",
}

EXPECTED_SOURCE_STATUS = "ABX_CODEGEN_CONTINUITY_LANE_CONVENTIONS_PLAN_READY"


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


def _artifact_types(source_ready: bool) -> list[dict[str, Any]]:
    registration_status = "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE"
    return [
        {
            "artifact_type": "ImprovementProposal.v1",
            "description": "Structured proposal for code changes or improvements",
            "typical_producer": "Harness / Planning layer",
            "lineage_requirement": "Must link to source GapDiagnosisPacket",
            "registration_status": registration_status,
            "registration_authorized": False,
        },
        {
            "artifact_type": "ShadowImprovementReceipt.v1",
            "description": "Result of shadow replay validation",
            "typical_producer": "codegen_shadow_replay_harness.py",
            "lineage_requirement": "Must link to originating ImprovementProposal",
            "registration_status": registration_status,
            "registration_authorized": False,
        },
        {
            "artifact_type": "CodegenOperatorDecisionRecord.v1",
            "description": "Operator decision on a proposal/receipt",
            "typical_producer": "Operator tooling",
            "lineage_requirement": "Must link to Proposal + Receipt",
            "registration_status": registration_status,
            "registration_authorized": False,
        },
        {
            "artifact_type": "MetaGateAuthorizationRecord.v1",
            "description": "Formal authorization for self-improvement",
            "typical_producer": "Meta-Gate process",
            "lineage_requirement": "Must link to ODR + Receipt",
            "registration_status": registration_status,
            "registration_authorized": False,
        },
        {
            "artifact_type": "MetaGateChainSeal.v1",
            "description": "Seal closing the Meta-Gate chain",
            "typical_producer": "Meta-Gate process",
            "lineage_requirement": "Must link to Authorization Record",
            "registration_status": registration_status,
            "registration_authorized": False,
        },
    ]


def _lineage_rules(source_ready: bool) -> list[dict[str, Any]]:
    rule_status = "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE"
    return [
        {
            "rule_id": "shadow_receipt_references_source_proposal",
            "rule_status": rule_status,
            "required": True,
            "enforcement_authorized": False,
        },
        {
            "rule_id": "meta_gate_chain_back_to_original_proposal",
            "rule_status": rule_status,
            "required": True,
            "enforcement_authorized": False,
        },
        {
            "rule_id": "queryable_by_proposal_or_receipt_id",
            "rule_status": rule_status,
            "required": True,
            "enforcement_authorized": False,
        },
    ]


def build_abx_codegen_intelligence_spine_artifact_registry_integration_plan(
    *,
    repo_root: str | Path,
    source_continuity_lane_conventions_plan_path: str | Path = SOURCE_CONTINUITY_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_continuity_lane_conventions_plan_path).as_posix()
    source = _read_json(root / source_continuity_lane_conventions_plan_path)
    source_ready = (
        source.get("artifact_type")
        == "AbxCodegenIntelligenceSpineContinuityLaneConventionsPlan.v1"
        and source.get("continuity_lane_conventions_plan_status") == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and source.get("safe_to_auto_continue") is False
        and source.get("execution_authority") is False
        and source.get("valid_for_implementation") is False
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "artifact_registry_integration_plan_status": (
            "ABX_CODEGEN_ARTIFACT_REGISTRY_INTEGRATION_PLAN_READY"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_notion_spec": {
            **NOTION_SPEC,
            "spec_hash_policy": "source_observed_metadata_only",
            "notion_writeback_performed": False,
        },
        "source_continuity_lane_conventions_plan": {
            "path": source_path,
            "hash": _sha256(root / source_continuity_lane_conventions_plan_path),
            "continuity_lane_conventions_plan_status": str(
                source.get("continuity_lane_conventions_plan_status", "NOT_COMPUTABLE")
            ),
            "recommended_next_lane": str(source.get("recommended_next_lane", "NOT_COMPUTABLE")),
            "source_ready": source_ready,
        },
        "artifact_types_to_register": _artifact_types(source_ready),
        "registration_requirements": {
            "required_fields": [
                "artifact_type",
                "canonical_hash",
                "source_observed_timestamp",
                "provenance",
                "continuity_lane",
                "governance_status",
            ],
            "timestamp_policy": (
                "Notion field named timestamp is represented as source_observed_timestamp; "
                "wall-clock generation time is forbidden for deterministic repo artifacts"
            ),
            "provenance_object_required": True,
            "continuity_lane_required_where_applicable": True,
            "allowed_governance_statuses": ["ADVISORY_ONLY", "PROJECTION_ONLY"],
            "registration_write_authorized": False,
        },
        "lineage_rules": _lineage_rules(source_ready),
        "integration_points": [
            {
                "integration_point": "harness_after_receipt",
                "notion_guidance": "Harness should call registry registration after receipt production",
                "integration_status": "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE",
                "registry_call_authorized": False,
                "harness_implementation_authorized": False,
            },
            {
                "integration_point": "operator_decision_records",
                "notion_guidance": "ODRs should be registered by operator tooling",
                "integration_status": "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE",
                "registry_call_authorized": False,
                "operator_tooling_authorized": False,
            },
            {
                "integration_point": "meta_gate_artifacts",
                "notion_guidance": "Meta-Gate artifacts should be registered by Meta-Gate processes/tools",
                "integration_status": "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE",
                "registry_call_authorized": False,
                "meta_gate_process_authorized": False,
            },
        ],
        "future_considerations": {
            "versioning_strategy_required": True,
            "search_indexing_strategy_required": True,
            "retention_archival_policy_required": True,
            "future_policy_authorized_by_this_plan": False,
        },
        "recommended_next_lane": "NOT_COMPUTABLE",
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "authority_locks": {
            "artifact_registry_mutation": False,
            "auto_approval": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "continuity_lane_creation": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "harness_implementation": False,
            "meta_gate_authorization": False,
            "meta_gate_process_execution": False,
            "notion_writeback": False,
            "operator_decision_record_creation": False,
            "operator_tooling_mutation": False,
            "queue_mutation": False,
            "registry_registration": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "shadow_replay_execution": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_artifact_registry_integration_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_artifact_registry_integration_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Artifact Registry Integration Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- artifact_registry_integration_plan_status: {packet['artifact_registry_integration_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Artifact Types To Register",
    ]
    for item in packet.get("artifact_types_to_register", []):
        if isinstance(item, Mapping):
            lines.append(
                f"- {item['artifact_type']}: {item['registration_status']} "
                f"(registration_authorized={item['registration_authorized']})"
            )
    lines.extend(["", "## Registration Requirements"])
    requirements = packet.get("registration_requirements", {})
    if isinstance(requirements, Mapping):
        lines.append(f"- timestamp_policy: {requirements['timestamp_policy']}")
        lines.append(f"- registration_write_authorized: {requirements['registration_write_authorized']}")
    return lines


def write_abx_codegen_intelligence_spine_artifact_registry_integration_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_artifact_registry_integration_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
