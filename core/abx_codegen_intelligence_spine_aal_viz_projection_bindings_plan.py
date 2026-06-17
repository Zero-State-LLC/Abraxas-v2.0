from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan import (
    OUT_JSON as SOURCE_RUNE_YGGDRASIL_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineAalVizProjectionBindingsPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_AAL_VIZ_PROJECTION_BINDINGS_PLAN_001"
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan_001.latest.md"
)

NOTION_SPEC = {
    "title": "AAL-Viz & Projection Bindings - Codegen Intelligence Spine",
    "page_id": "37d3e8ba-2f5c-81a8-adf9-da759cb89032",
    "observed_as_of": "2026-06-12",
    "status": "Planning Spec (Advisory)",
}

EXPECTED_SOURCE_STATUS = "ABX_CODEGEN_RUNE_YGGDRASIL_INTEGRATION_NEEDS_PLAN_READY"


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


def _projection_bindings(source_ready: bool) -> list[dict[str, Any]]:
    binding_status = "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE"
    return [
        {
            "artifact_type": "ImprovementProposal.v1",
            "recommended_viz_mode": "display_only",
            "purpose": "Show proposed changes and risk assessment",
            "binding_status": binding_status,
            "projection_binding_authorized": False,
            "execution_trigger_authorized": False,
        },
        {
            "artifact_type": "ShadowImprovementReceipt.v1",
            "recommended_viz_mode": "display_only",
            "purpose": "Visualize replay results, metrics, and recommendation",
            "binding_status": binding_status,
            "projection_binding_authorized": False,
            "execution_trigger_authorized": False,
        },
        {
            "artifact_type": "CodegenOperatorDecisionRecord",
            "recommended_viz_mode": "display_only",
            "purpose": "Display operator decisions and rationale",
            "binding_status": binding_status,
            "projection_binding_authorized": False,
            "execution_trigger_authorized": False,
        },
        {
            "artifact_type": "MetaGate*",
            "recommended_viz_mode": "display_only",
            "purpose": "Highlight elevated self-improvement activity",
            "binding_status": binding_status,
            "alert_on_meta_gate_path": True,
            "projection_binding_authorized": False,
            "execution_trigger_authorized": False,
        },
    ]


def _visualization_needs(source_ready: bool) -> list[dict[str, Any]]:
    need_status = "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE"
    return [
        {
            "view_id": "proposal_dashboard",
            "purpose": "List recent proposals with Pass, Hold, or Block status",
            "need_status": need_status,
            "display_only": True,
            "implementation_authorized": False,
        },
        {
            "view_id": "replay_metrics_view",
            "purpose": "Display correctness score, 12-run invariance, and governance compliance",
            "need_status": need_status,
            "display_only": True,
            "implementation_authorized": False,
        },
        {
            "view_id": "meta_gate_monitor",
            "purpose": "Flag self-improvement proposals in the Meta-Gate chain",
            "need_status": need_status,
            "display_only": True,
            "elevated_scrutiny_required": True,
            "implementation_authorized": False,
        },
        {
            "view_id": "lineage_graph",
            "purpose": "Trace proposal to receipt to ODR to seal",
            "need_status": need_status,
            "display_only": True,
            "implementation_authorized": False,
        },
    ]


def build_abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan(
    *,
    repo_root: str | Path,
    source_rune_yggdrasil_plan_path: str | Path = SOURCE_RUNE_YGGDRASIL_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_rune_yggdrasil_plan_path).as_posix()
    source = _read_json(root / source_rune_yggdrasil_plan_path)
    source_ready = (
        source.get("artifact_type")
        == "AbxCodegenIntelligenceSpineRuneYggdrasilIntegrationNeedsPlan.v1"
        and source.get("integration_needs_plan_status") == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and source.get("safe_to_auto_continue") is False
        and source.get("execution_authority") is False
        and source.get("valid_for_implementation") is False
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "projection_bindings_plan_status": (
            "ABX_CODEGEN_AAL_VIZ_PROJECTION_BINDINGS_PLAN_READY"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_notion_spec": {
            **NOTION_SPEC,
            "spec_hash_policy": "source_observed_metadata_only",
            "notion_writeback_performed": False,
        },
        "source_rune_yggdrasil_plan": {
            "path": source_path,
            "hash": _sha256(root / source_rune_yggdrasil_plan_path),
            "integration_needs_plan_status": str(
                source.get("integration_needs_plan_status", "NOT_COMPUTABLE")
            ),
            "recommended_next_lane": str(source.get("recommended_next_lane", "NOT_COMPUTABLE")),
            "source_ready": source_ready,
        },
        "recommended_projection_bindings": _projection_bindings(source_ready),
        "visualization_needs": _visualization_needs(source_ready),
        "projection_constraints": {
            "all_visualizations_display_only": True,
            "aal_viz_component_may_trigger_execution": False,
            "aal_viz_component_may_trigger_mutation": False,
            "aal_viz_component_may_trigger_promotion": False,
            "meta_gate_paths_require_elevated_scrutiny_label": True,
            "projection_runtime_mutation_authorized": False,
        },
        "compatibility_plan": {
            "specific_card_layouts_required": True,
            "dashboard_layouts_required": True,
            "existing_aal_viz_projection_patterns_must_be_preserved": True,
            "layout_definition_authorized_by_this_plan": False,
            "runtime_projection_builder_change_authorized_by_this_plan": False,
        },
        "recommended_next_lane": "NOT_COMPUTABLE",
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "display_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "authority_locks": {
            "aal_viz_component_execution_trigger": False,
            "aal_viz_runtime_mutation": False,
            "auto_approval": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "dashboard_layout_implementation": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "harness_implementation": False,
            "meta_gate_authorization": False,
            "notion_writeback": False,
            "operator_decision_record_creation": False,
            "promotion_authority": False,
            "projection_binding_registration": False,
            "queue_mutation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "shadow_replay_execution": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine AAL-Viz Projection Bindings Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- projection_bindings_plan_status: {packet['projection_bindings_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- display_only: {packet['display_only']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Recommended Projection Bindings",
    ]
    for binding in packet.get("recommended_projection_bindings", []):
        if isinstance(binding, Mapping):
            lines.append(
                f"- {binding['artifact_type']}: {binding['recommended_viz_mode']} "
                f"({binding['binding_status']})"
            )
    lines.extend(["", "## Visualization Needs"])
    for need in packet.get("visualization_needs", []):
        if isinstance(need, Mapping):
            lines.append(f"- {need['view_id']}: {need['need_status']}")
    return lines


def write_abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
