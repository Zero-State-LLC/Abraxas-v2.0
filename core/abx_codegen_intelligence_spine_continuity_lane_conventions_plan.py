from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan import (
    OUT_JSON as SOURCE_AAL_VIZ_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineContinuityLaneConventionsPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_CONTINUITY_LANE_CONVENTIONS_PLAN_001"
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_continuity_lane_conventions_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_continuity_lane_conventions_plan_001.latest.md"
)

NOTION_SPEC = {
    "title": "Continuity Spine Lane Conventions - Codegen Intelligence",
    "page_id": "37d3e8ba-2f5c-81f3-a3fc-f1fae7ce3d6f",
    "observed_as_of": "2026-06-12",
    "status": "Planning Spec (Advisory)",
}

EXPECTED_SOURCE_STATUS = "ABX_CODEGEN_AAL_VIZ_PROJECTION_BINDINGS_PLAN_READY"


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


def _lane_categories(source_ready: bool) -> list[dict[str, Any]]:
    convention_status = "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE"
    return [
        {
            "category": "Shadow Replay",
            "naming_pattern": "P102G+CODEGEN-SHADOW-###",
            "example": "P102G+CODEGEN-SHADOW-007",
            "description": "Standard shadow replay runs for normal proposals",
            "convention_status": convention_status,
            "lane_creation_authorized": False,
        },
        {
            "category": "Meta-Gate",
            "naming_pattern": "META-P102G+CODEGEN-META-###",
            "example": "META-P102G+CODEGEN-META-ODR-019",
            "description": "Meta-Gate specific lanes for ODR, authorization record, and seal paths",
            "convention_status": convention_status,
            "elevated_scrutiny_required": True,
            "lane_creation_authorized": False,
        },
        {
            "category": "Operator Decision",
            "naming_pattern": "P102G+CODEGEN-ODR-###",
            "example": "P102G+CODEGEN-ODR-033",
            "description": "Operator Decision Records for normal proposals",
            "convention_status": convention_status,
            "lane_creation_authorized": False,
        },
        {
            "category": "Authorization",
            "naming_pattern": "P102G+CODEGEN-AUTH-###",
            "example": "P102G+CODEGEN-AUTH-012",
            "description": "Authorization Records",
            "convention_status": convention_status,
            "lane_creation_authorized": False,
        },
        {
            "category": "Seal",
            "naming_pattern": "P102G+CODEGEN-SEAL-###",
            "example": "P102G+CODEGEN-SEAL-005",
            "description": "Chain Seal artifacts",
            "convention_status": convention_status,
            "lane_creation_authorized": False,
        },
    ]


def build_abx_codegen_intelligence_spine_continuity_lane_conventions_plan(
    *,
    repo_root: str | Path,
    source_projection_bindings_plan_path: str | Path = SOURCE_AAL_VIZ_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_projection_bindings_plan_path).as_posix()
    source = _read_json(root / source_projection_bindings_plan_path)
    source_ready = (
        source.get("artifact_type")
        == "AbxCodegenIntelligenceSpineAalVizProjectionBindingsPlan.v1"
        and source.get("projection_bindings_plan_status") == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and source.get("safe_to_auto_continue") is False
        and source.get("execution_authority") is False
        and source.get("valid_for_implementation") is False
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "continuity_lane_conventions_plan_status": (
            "ABX_CODEGEN_CONTINUITY_LANE_CONVENTIONS_PLAN_READY"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_notion_spec": {
            **NOTION_SPEC,
            "spec_hash_policy": "source_observed_metadata_only",
            "notion_writeback_performed": False,
        },
        "source_projection_bindings_plan": {
            "path": source_path,
            "hash": _sha256(root / source_projection_bindings_plan_path),
            "projection_bindings_plan_status": str(
                source.get("projection_bindings_plan_status", "NOT_COMPUTABLE")
            ),
            "recommended_next_lane": str(source.get("recommended_next_lane", "NOT_COMPUTABLE")),
            "source_ready": source_ready,
        },
        "base_lane_prefix": "CODEGEN-",
        "lane_categories": _lane_categories(source_ready),
        "lane_creation_rules": {
            "harness_lane_creation_observed_in_spec": True,
            "meta_gate_lane_creation_observed_in_spec": True,
            "deterministic_id_basis": "proposal_hash_plus_category_where_possible",
            "lane_id_generation_authorized": False,
            "harness_lane_creation_authorized": False,
            "meta_gate_lane_creation_authorized": False,
            "all_codegen_lanes_default_to_advisory_projection_only": True,
            "explicit_governance_promotion_required": True,
        },
        "p102g_relationship": {
            "additive_extension_of_p102g_terminal_handoff": True,
            "replaces_existing_p102_research_lanes": False,
            "interferes_with_existing_p102_research_lanes": False,
            "p102g_extension_authorized_by_this_plan": False,
            "meta_prefix_marks_elevated_scrutiny": True,
        },
        "future_evolution": {
            "additional_subcategories_allowed_by_convention": [
                "CODEGEN-FIXTURE-",
                "CODEGEN-TEST-",
            ],
            "subcategories_authorized_by_this_plan": False,
            "must_follow_prefix_category_sequence_pattern": True,
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
            "auto_approval": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "continuity_lane_creation": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "harness_implementation": False,
            "harness_lane_creation": False,
            "meta_gate_authorization": False,
            "meta_gate_lane_creation": False,
            "notion_writeback": False,
            "operator_decision_record_creation": False,
            "p102g_extension_activation": False,
            "queue_mutation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "shadow_replay_execution": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_continuity_lane_conventions_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_continuity_lane_conventions_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Continuity Lane Conventions Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- continuity_lane_conventions_plan_status: {packet['continuity_lane_conventions_plan_status']}",
        f"- base_lane_prefix: {packet['base_lane_prefix']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Lane Categories",
    ]
    for lane in packet.get("lane_categories", []):
        if isinstance(lane, Mapping):
            lines.append(
                f"- {lane['category']}: {lane['naming_pattern']} "
                f"({lane['convention_status']})"
            )
    lines.extend(["", "## Lane Creation Rules"])
    rules = packet.get("lane_creation_rules", {})
    if isinstance(rules, Mapping):
        lines.append(f"- lane_id_generation_authorized: {rules['lane_id_generation_authorized']}")
        lines.append(f"- harness_lane_creation_authorized: {rules['harness_lane_creation_authorized']}")
        lines.append(f"- meta_gate_lane_creation_authorized: {rules['meta_gate_lane_creation_authorized']}")
    return lines


def write_abx_codegen_intelligence_spine_continuity_lane_conventions_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_continuity_lane_conventions_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
