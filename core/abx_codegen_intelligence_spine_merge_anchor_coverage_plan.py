from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan import (
    OUT_JSON as SOURCE_RECOMMENDED_PATCH_SEQUENCE_PRECONDITION_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineMergeAnchorCoveragePlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_MERGE_ANCHOR_COVERAGE_PLAN_001"
OUT_JSON = (
    "out/audit/abx_codegen_intelligence_spine_merge_anchor_coverage_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/abx_codegen_intelligence_spine_merge_anchor_coverage_plan_001.latest.md"
)

EXPECTED_PRECONDITION_STATUS = (
    "ABX_CODEGEN_RECOMMENDED_PATCH_SEQUENCE_PRECONDITION_PLAN_HELD_FOR_OPERATOR"
)

NOTION_CANON_SHADOW_FORMALIZATION = {
    "title": "ABX_CODEGEN_INTELLIGENCE_SPINE_001 - Canon-Shadow Subsystem Formalization",
    "page_id": "3713e8ba-2f5c-81ee-b7e6-c0542b9859a4",
    "observed_as_of": "2026-05-31",
    "section": "Existing Merge Anchors",
    "authority": "ADVISORY_ONLY_NON_AUTHORITATIVE_SHADOW_ONLY",
    "notion_writeback_performed": False,
}

MERGE_ANCHORS = [
    {
        "anchor_id": "codegen_upgrade_v0_1_v0_2",
        "anchor_title": "Abraxas CodeGen Upgrade v0.1-v0.2 - Coding Intelligence Canon-Shadow",
        "anchor_kind": "notion_historical_codegen_doctrine",
        "repo_evidence_paths": [],
    },
    {
        "anchor_id": "codegen_upgrade_v0_4",
        "anchor_title": "Abraxas CodeGen Upgrade v0.4 - Autonomous Patch Loop + Promotion Gate",
        "anchor_kind": "notion_historical_codegen_doctrine",
        "repo_evidence_paths": [],
    },
    {
        "anchor_id": "codegen_upgrade_v0_7",
        "anchor_title": (
            "Abraxas CodeGen Upgrade v0.7 - Adversarial Policy Generator + "
            "Red-Team Mutation Harness"
        ),
        "anchor_kind": "notion_historical_codegen_doctrine",
        "repo_evidence_paths": [],
    },
    {
        "anchor_id": "codeir_v1_1",
        "anchor_title": "Abraxas CodeIR v1.1 - ABX-Native Design Doctrine + Profundity Gate",
        "anchor_kind": "notion_design_doctrine",
        "repo_evidence_paths": [],
    },
    {
        "anchor_id": "prompting_upgrade_stack_v0_1",
        "anchor_title": "ABX Prompting Upgrade Stack v0.1 - Canon-Shadow",
        "anchor_kind": "notion_prompting_doctrine",
        "repo_evidence_paths": [],
    },
    {
        "anchor_id": "code_drop_envelope_rule",
        "anchor_title": "ABX Code Drop Envelope rule",
        "anchor_kind": "notion_code_drop_doctrine",
        "repo_evidence_paths": [],
    },
    {
        "anchor_id": "incremental_patch_only_doctrine",
        "anchor_title": "Incremental Patch Only doctrine",
        "anchor_kind": "notion_patch_scope_doctrine",
        "repo_evidence_paths": [],
    },
    {
        "anchor_id": "abx_runes_contract_doctrine",
        "anchor_title": "ABX-Runes contract doctrine",
        "anchor_kind": "repo_observed_contract_doctrine",
        "repo_evidence_paths": ["contracts/runes/catalog.v1.json"],
    },
    {
        "anchor_id": "subsystem_merge_map_002",
        "anchor_title": "ABRAXAS_SUBSYSTEM_MERGE_MAP_002",
        "anchor_kind": "notion_merge_map",
        "repo_evidence_paths": [],
    },
    {
        "anchor_id": "research_shadow_replay_engine_001",
        "anchor_title": "RESEARCH_SHADOW_REPLAY_ENGINE_001",
        "anchor_kind": "repo_observed_shadow_replay_surface",
        "repo_evidence_paths": [
            "core/research_shadow_replay_audit.py",
            "scripts/run_research_shadow_replay_audit.py",
            "contracts/canon/research_shadow_replay_audit.v1.schema.json",
            "out/research_shadow_replay_audit/latest.json",
        ],
    },
    {
        "anchor_id": "belief_graph_engine_spec_001",
        "anchor_title": "BELIEF_GRAPH_ENGINE_SPEC_001",
        "anchor_kind": "repo_observed_advisory_planning_surface",
        "repo_evidence_paths": [
            "core/belief_graph_engine_gap_analysis_plan.py",
            "out/audit/belief_graph_engine_gap_analysis_plan_001.latest.json",
        ],
    },
    {
        "anchor_id": "patch_abx_belief_graph_001",
        "anchor_title": "PATCH-ABX-BELIEF-GRAPH-001",
        "anchor_kind": "repo_observed_contract_surface",
        "repo_evidence_paths": [
            "core/belief_graph/belief_graph_packet.py",
            "contracts/belief_graph/belief_graph_packet.v1.schema.json",
        ],
    },
    {
        "anchor_id": "rune_promotion_gate",
        "anchor_title": "RUNE.PROMOTION_GATE - SHADOW to FORECAST Bridge Contract",
        "anchor_kind": "notion_rune_contract_doctrine",
        "repo_evidence_paths": [],
    },
    {
        "anchor_id": "subsystem_inventory_canon_spine",
        "anchor_title": "Abraxas - Subsystem Inventory (Canon Spine)",
        "anchor_kind": "notion_canon_inventory_with_fixture_reference",
        "repo_evidence_paths": ["fixtures/canon/canon_attestation_fixture.v1.json"],
    },
    {
        "anchor_id": "system_state_snapshot_authoritative",
        "anchor_title": "Abraxas - System State Snapshot (Authoritative)",
        "anchor_kind": "notion_system_state_snapshot",
        "repo_evidence_paths": [],
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


def _anchor_status(source_ready: bool, observed: bool) -> str:
    if not source_ready:
        return "NOT_COMPUTABLE"
    if observed:
        return "MERGE_ANCHOR_REPO_EVIDENCE_OBSERVED_HELD_FOR_OPERATOR"
    return "MERGE_ANCHOR_NOTION_ONLY_HELD_FOR_OPERATOR"


def _evidence_rows(repo_root: Path, paths: list[str]) -> list[dict[str, Any]]:
    rows = []
    for path in paths:
        target = repo_root / path
        rows.append(
            {
                "path": path,
                "observed": target.exists(),
                "hash": _sha256(target),
            }
        )
    return rows


def build_abx_codegen_intelligence_spine_merge_anchor_coverage_plan(
    *,
    repo_root: str | Path,
    source_recommended_patch_sequence_precondition_plan_path: str
    | Path = SOURCE_RECOMMENDED_PATCH_SEQUENCE_PRECONDITION_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_recommended_patch_sequence_precondition_plan_path).as_posix()
    source = _read_json(root / source_recommended_patch_sequence_precondition_plan_path)
    source_ready = (
        source.get("artifact_type")
        == "AbxCodegenIntelligenceSpineRecommendedPatchSequencePreconditionPlan.v1"
        and source.get("recommended_patch_sequence_precondition_plan_status")
        == EXPECTED_PRECONDITION_STATUS
        and source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and source.get("safe_to_auto_continue") is False
        and source.get("execution_authority") is False
        and source.get("valid_for_implementation") is False
    )

    anchors: list[dict[str, Any]] = []
    for anchor in MERGE_ANCHORS:
        evidence = _evidence_rows(root, list(anchor["repo_evidence_paths"]))
        observed = bool(evidence) and all(row["observed"] for row in evidence)
        anchors.append(
            {
                **anchor,
                "repo_evidence": evidence,
                "repo_evidence_observed": observed,
                "coverage_status": _anchor_status(source_ready, observed),
                "merge_required_before_implementation": True,
                "creates_authority": False,
                "defer_to_anchor": True,
            }
        )

    observed_count = sum(1 for anchor in anchors if anchor["repo_evidence_observed"])
    notion_only_count = len(anchors) - observed_count
    row_status = (
        "MERGE_ANCHOR_COVERAGE_DEFINED_HELD_FOR_OPERATOR"
        if source_ready
        else "NOT_COMPUTABLE"
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "merge_anchor_coverage_plan_status": (
            "ABX_CODEGEN_MERGE_ANCHOR_COVERAGE_PLAN_HELD_FOR_OPERATOR"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_notion_canon_shadow_formalization": NOTION_CANON_SHADOW_FORMALIZATION,
        "source_recommended_patch_sequence_precondition_plan": {
            "path": source_path,
            "hash": _sha256(root / source_recommended_patch_sequence_precondition_plan_path),
            "recommended_patch_sequence_precondition_plan_status": str(
                source.get(
                    "recommended_patch_sequence_precondition_plan_status",
                    "NOT_COMPUTABLE",
                )
            ),
            "source_ready": source_ready,
        },
        "merge_anchors": anchors,
        "coverage_summary": {
            "anchor_count": len(anchors),
            "repo_evidence_observed_count": observed_count,
            "notion_only_anchor_count": notion_only_count,
            "all_anchors_covered_by_repo_evidence": notion_only_count == 0,
            "implementation_merge_readiness": "HELD_FOR_OPERATOR",
            "reason": (
                "notion_merge_anchors_are_listed_but_not_all_have_repo_visible_"
                "evidence_and_no_operator_authorization_exists"
            ),
        },
        "merge_rules": [
            {
                "rule": "do_not_create_autonomous_coding_agent_authority",
                "rule_status": row_status,
                "authorized": False,
            },
            {
                "rule": "formalize_codegen_as_deterministic_patch_contract_compiler",
                "rule_status": row_status,
                "authorized": False,
            },
            {
                "rule": "defer_to_existing_governance_and_operator_review",
                "rule_status": row_status,
                "authorized": False,
            },
            {
                "rule": "avoid_duplicate_codegen_authority_surfaces",
                "rule_status": row_status,
                "authorized": False,
            },
        ],
        "blocked_actions": [
            "merge_anchor_mutation",
            "notion_anchor_writeback",
            "autonomous_coding_agent_authority_creation",
            "duplicate_codegen_authority_surface_creation",
            "contracts_codegen_directory_creation",
            "core_codegen_directory_creation",
            "patch_contract_builder_creation",
            "code_drop_envelope_builder_creation",
            "policy_review_packet_builder_creation",
            "implementation_prompt_emission",
            "patch_application",
            "runtime_mutation",
            "canon_mutation",
            "forecast_routing",
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
            "auto_approval": False,
            "autonomous_coding_agent_authority_creation": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "contracts_codegen_directory_creation": False,
            "core_codegen_directory_creation": False,
            "duplicate_authority_surface_creation": False,
            "execution": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "implementation_prompt_emission": False,
            "merge_anchor_mutation": False,
            "module_creation": False,
            "notion_writeback": False,
            "operator_attestation": False,
            "operator_decision_record_creation": False,
            "patch_application": False,
            "queue_mutation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "schema_creation": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_merge_anchor_coverage_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_merge_anchor_coverage_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Merge Anchor Coverage Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- merge_anchor_coverage_plan_status: {packet['merge_anchor_coverage_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Coverage Summary",
    ]
    summary = packet["coverage_summary"]
    lines.extend(
        [
            f"- anchor_count: {summary['anchor_count']}",
            f"- repo_evidence_observed_count: {summary['repo_evidence_observed_count']}",
            f"- notion_only_anchor_count: {summary['notion_only_anchor_count']}",
            f"- implementation_merge_readiness: {summary['implementation_merge_readiness']}",
            "",
            "## Merge Anchors",
        ]
    )
    for anchor in packet.get("merge_anchors", []):
        if isinstance(anchor, Mapping):
            lines.append(
                f"- {anchor['anchor_id']}: {anchor['coverage_status']} "
                f"(repo_evidence_observed={anchor['repo_evidence_observed']})"
            )
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- {action}")
    return lines


def write_abx_codegen_intelligence_spine_merge_anchor_coverage_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_merge_anchor_coverage_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
