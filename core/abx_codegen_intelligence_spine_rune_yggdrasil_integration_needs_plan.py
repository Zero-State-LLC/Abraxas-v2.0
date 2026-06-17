from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_shadow_replay_harness_operator_decision_record_review import (
    OUT_JSON as SOURCE_ODR_REVIEW_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineRuneYggdrasilIntegrationNeedsPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_RUNE_YGGDRASIL_INTEGRATION_NEEDS_PLAN_001"
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan_001.latest.md"
)

NOTION_SPEC = {
    "title": "Rune & YGGDRASIL Integration Needs - Codegen Intelligence",
    "page_id": "37d3e8ba-2f5c-81c1-b160-ebaabb3e920d",
    "observed_as_of": "2026-06-12",
    "status": "Planning Spec (Advisory)",
}

EXPECTED_REVIEW_STATUS = (
    "ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_REVIEW_HELD_FOR_OPERATOR"
)


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


def _candidate_runes(source_ready: bool) -> list[dict[str, Any]]:
    candidate_status = "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE"
    return [
        {
            "rune": "RUNE.CODEGEN.PROPOSE",
            "purpose": "Trigger generation of an ImprovementProposal",
            "required_level": "Medium",
            "notes": "Could be useful for automation",
            "candidate_status": candidate_status,
            "registration_authorized": False,
            "binding_matrix_update_authorized": False,
        },
        {
            "rune": "RUNE.CODEGEN.SHADOW_REPLAY",
            "purpose": "Execute shadow replay for a proposal",
            "required_level": "High",
            "notes": "Core to the harness",
            "candidate_status": candidate_status,
            "registration_authorized": False,
            "binding_matrix_update_authorized": False,
        },
        {
            "rune": "RUNE.CODEGEN.META_GATE",
            "purpose": "Route self-improvement proposals through Meta-Gate",
            "required_level": "High",
            "notes": "Critical for safety",
            "candidate_status": candidate_status,
            "registration_authorized": False,
            "binding_matrix_update_authorized": False,
        },
        {
            "rune": "RUNE.CODEGEN.ODR",
            "purpose": "Create or process Operator Decision Record",
            "required_level": "Medium",
            "notes": "Operator tooling support",
            "candidate_status": candidate_status,
            "registration_authorized": False,
            "binding_matrix_update_authorized": False,
        },
        {
            "rune": "RUNE.CODEGEN.SEAL",
            "purpose": "Trigger or validate Meta-Gate Chain Seal",
            "required_level": "Medium",
            "notes": "Chain completion",
            "candidate_status": candidate_status,
            "registration_authorized": False,
            "binding_matrix_update_authorized": False,
        },
    ]


def _candidate_routes(source_ready: bool) -> list[dict[str, Any]]:
    route_status = "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE"
    routes = [
        "codegen.proposal.generate",
        "codegen.shadow.replay",
        "codegen.meta.gate",
        "codegen.operator.decision",
    ]
    return [
        {
            "route_family": route,
            "namespace": "codegen",
            "route_status": route_status,
            "default_authority": "projection_only",
            "route_registration_authorized": False,
            "runtime_binding_authorized": False,
            "operator_review_required": True,
        }
        for route in routes
    ]


def build_abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan(
    *,
    repo_root: str | Path,
    source_codegen_operator_decision_record_review_path: str | Path = SOURCE_ODR_REVIEW_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_codegen_operator_decision_record_review_path).as_posix()
    source = _read_json(root / source_codegen_operator_decision_record_review_path)
    source_ready = (
        source.get("artifact_type")
        == "AbxCodegenShadowReplayHarnessOperatorDecisionRecordReview.v1"
        and source.get("operator_decision_record_review_status") == EXPECTED_REVIEW_STATUS
        and source.get("selected_operator_decision") == "MAINTAIN_HOLD"
        and source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and source.get("safe_to_auto_continue") is False
        and source.get("implementation_authorization_granted") is False
        and source.get("meta_gate_authorization_granted") is False
        and source.get("execution_authority") is False
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "integration_needs_plan_status": (
            "ABX_CODEGEN_RUNE_YGGDRASIL_INTEGRATION_NEEDS_PLAN_READY"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_notion_spec": {
            **NOTION_SPEC,
            "spec_hash_policy": "source_observed_metadata_only",
            "notion_writeback_performed": False,
        },
        "source_codegen_operator_decision_record_review": {
            "path": source_path,
            "hash": _sha256(root / source_codegen_operator_decision_record_review_path),
            "operator_decision_record_review_status": str(
                source.get("operator_decision_record_review_status", "NOT_COMPUTABLE")
            ),
            "selected_operator_decision": str(
                source.get("selected_operator_decision", "NOT_COMPUTABLE")
            ),
            "recommended_next_lane": str(source.get("recommended_next_lane", "NOT_COMPUTABLE")),
            "source_ready": source_ready,
        },
        "candidate_runes": _candidate_runes(source_ready),
        "candidate_route_families": _candidate_routes(source_ready),
        "route_defaults": {
            "new_namespace": "codegen.*",
            "default_route_authority": "projection_only_or_advisory_only",
            "meta_gate_operator_review_bypass_allowed": False,
            "route_mutation_authorized": False,
            "runtime_wiring_authorized": False,
        },
        "recommendation": {
            "recommended_starting_runes": [
                "RUNE.CODEGEN.SHADOW_REPLAY",
                "RUNE.CODEGEN.META_GATE",
            ],
            "expansion_policy": "expand_only_as_implementation_needs_become_clear",
            "over_proliferation_guard": True,
            "catalog_registration_required": True,
            "binding_matrix_update_required": True,
            "registration_authorized_by_this_plan": False,
            "implementation_blocked_by_operator_hold": True,
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
            "binding_matrix_update": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "harness_implementation": False,
            "meta_gate_authorization": False,
            "notion_writeback": False,
            "operator_decision_record_creation": False,
            "queue_mutation": False,
            "route_registration": False,
            "rune_catalog_registration": False,
            "runtime_binding": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "shadow_replay_execution": False,
            "yggdrasil_route_mutation": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Rune YGGDRASIL Integration Needs Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- integration_needs_plan_status: {packet['integration_needs_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Candidate Runes",
    ]
    for rune in packet.get("candidate_runes", []):
        if isinstance(rune, Mapping):
            lines.append(
                f"- {rune['rune']}: {rune['candidate_status']} "
                f"(registration_authorized={rune['registration_authorized']})"
            )
    lines.extend(["", "## Candidate Route Families"])
    for route in packet.get("candidate_route_families", []):
        if isinstance(route, Mapping):
            lines.append(
                f"- {route['route_family']}: {route['route_status']} "
                f"(runtime_binding_authorized={route['runtime_binding_authorized']})"
            )
    return lines


def write_abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_rune_yggdrasil_integration_needs_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
