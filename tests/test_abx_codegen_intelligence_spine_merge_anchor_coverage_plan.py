from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_merge_anchor_coverage_plan import (
    build_abx_codegen_intelligence_spine_merge_anchor_coverage_plan,
    render_abx_codegen_intelligence_spine_merge_anchor_coverage_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts.codegen import run_abx_codegen_intelligence_spine_merge_anchor_coverage_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_merge_anchor_coverage_plan.v1.schema.json"
)


def test_codegen_merge_anchor_coverage_plan_is_held() -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_coverage_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["merge_anchor_coverage_plan_status"]
        == "ABX_CODEGEN_MERGE_ANCHOR_COVERAGE_PLAN_HELD_FOR_OPERATOR"
    )
    assert packet["source_recommended_patch_sequence_precondition_plan"][
        "source_ready"
    ] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_merge_anchor_coverage_lists_notion_anchors() -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_coverage_plan(
        repo_root=REPO_ROOT
    )

    anchors = {item["anchor_id"]: item for item in packet["merge_anchors"]}
    assert set(anchors) == {
        "codegen_upgrade_v0_1_v0_2",
        "codegen_upgrade_v0_4",
        "codegen_upgrade_v0_7",
        "codeir_v1_1",
        "prompting_upgrade_stack_v0_1",
        "code_drop_envelope_rule",
        "incremental_patch_only_doctrine",
        "abx_runes_contract_doctrine",
        "subsystem_merge_map_002",
        "research_shadow_replay_engine_001",
        "belief_graph_engine_spec_001",
        "patch_abx_belief_graph_001",
        "rune_promotion_gate",
        "subsystem_inventory_canon_spine",
        "system_state_snapshot_authoritative",
    }
    assert anchors["code_drop_envelope_rule"]["defer_to_anchor"] is True
    assert anchors["incremental_patch_only_doctrine"][
        "merge_required_before_implementation"
    ] is True


def test_codegen_merge_anchor_coverage_classifies_repo_observed_anchors() -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_coverage_plan(
        repo_root=REPO_ROOT
    )

    anchors = {item["anchor_id"]: item for item in packet["merge_anchors"]}
    assert anchors["research_shadow_replay_engine_001"][
        "repo_evidence_observed"
    ] is True
    assert anchors["patch_abx_belief_graph_001"]["repo_evidence_observed"] is True
    assert anchors["codegen_upgrade_v0_4"]["repo_evidence_observed"] is False
    assert anchors["rune_promotion_gate"]["coverage_status"] == (
        "MERGE_ANCHOR_NOTION_ONLY_HELD_FOR_OPERATOR"
    )


def test_codegen_merge_anchor_coverage_summary_counts() -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_coverage_plan(
        repo_root=REPO_ROOT
    )

    summary = packet["coverage_summary"]
    assert summary["anchor_count"] == 15
    assert summary["repo_evidence_observed_count"] == 5
    assert summary["notion_only_anchor_count"] == 10
    assert summary["all_anchors_covered_by_repo_evidence"] is False
    assert summary["implementation_merge_readiness"] == "HELD_FOR_OPERATOR"


def test_codegen_merge_anchor_coverage_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_coverage_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert "merge_anchor_mutation" in packet["blocked_actions"]
    assert "autonomous_coding_agent_authority_creation" in packet["blocked_actions"]


def test_codegen_merge_anchor_coverage_fails_closed_without_source(tmp_path: Path) -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_coverage_plan(
        repo_root=tmp_path
    )

    assert packet["merge_anchor_coverage_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_recommended_patch_sequence_precondition_plan"][
        "source_ready"
    ] is False
    assert all(
        item["coverage_status"] == "NOT_COMPUTABLE"
        for item in packet["merge_anchors"]
    )


def test_codegen_merge_anchor_coverage_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_coverage_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_merge_anchor_coverage_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_merge_anchor_coverage_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_merge_anchor_coverage_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_merge_anchor_coverage_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_merge_anchor_coverage_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_coverage_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_merge_anchor_coverage_plan_markdown(
        packet
    )

    assert markdown[0] == "# ABX Codegen Intelligence Spine Merge Anchor Coverage Plan"
    assert any("research_shadow_replay_engine_001" in line for line in markdown)
    assert any("merge_anchor_mutation" in line for line in markdown)
