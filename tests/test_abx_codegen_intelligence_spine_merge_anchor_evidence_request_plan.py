from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan import (
    build_abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan,
    render_abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan.v1.schema.json"
)


def test_codegen_merge_anchor_evidence_request_plan_is_held() -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan(
        repo_root=REPO_ROOT
    )

    assert packet["merge_anchor_evidence_request_plan_status"] == (
        "ABX_CODEGEN_MERGE_ANCHOR_EVIDENCE_REQUEST_PLAN_HELD_FOR_OPERATOR"
    )
    assert packet["source_merge_anchor_coverage_plan"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_merge_anchor_evidence_request_lists_notion_only_anchors() -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan(
        repo_root=REPO_ROOT
    )

    anchors = {item["anchor_id"]: item for item in packet["notion_only_anchor_requests"]}
    assert len(anchors) == 10
    assert "codegen_upgrade_v0_1_v0_2" in anchors
    assert "code_drop_envelope_rule" in anchors
    assert "incremental_patch_only_doctrine" in anchors
    assert "research_shadow_replay_engine_001" not in anchors
    assert all(item["notion_fetch_required"] is True for item in anchors.values())
    assert all(item["notion_writeback_authorized"] is False for item in anchors.values())


def test_codegen_merge_anchor_evidence_request_normalization_fields() -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan(
        repo_root=REPO_ROOT
    )

    first_request = packet["notion_only_anchor_requests"][0]
    assert first_request["requested_evidence_fields"] == [
        "notion_page_id_or_url",
        "source_title",
        "source_role",
        "governance_posture",
        "authority_boundaries",
        "merge_rules",
        "repo_relevance_summary",
        "implementation_constraints",
        "evidence_hash_policy",
        "operator_review_requirement",
    ]
    assert all(
        item["normalization_authorized"] is False
        for item in packet["evidence_normalization_requirements"]
    )


def test_codegen_merge_anchor_evidence_request_summary_blocks_implementation() -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan(
        repo_root=REPO_ROOT
    )

    summary = packet["request_summary"]
    assert summary["source_anchor_count"] == 15
    assert summary["notion_only_anchor_count"] == 10
    assert summary["request_ready_for_operator"] is True
    assert summary["all_requested_evidence_present"] is False
    assert summary["implementation_unblocked"] is False


def test_codegen_merge_anchor_evidence_request_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert "notion_writeback" in packet["blocked_actions"]
    assert "implementation_unblock" in packet["blocked_actions"]


def test_codegen_merge_anchor_evidence_request_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan(
        repo_root=tmp_path
    )

    assert packet["merge_anchor_evidence_request_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_merge_anchor_coverage_plan"]["source_ready"] is False
    assert packet["notion_only_anchor_requests"] == []


def test_codegen_merge_anchor_evidence_request_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_merge_anchor_evidence_request_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_merge_anchor_evidence_request_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan_markdown(
        packet
    )

    assert markdown[0] == (
        "# ABX Codegen Intelligence Spine Merge Anchor Evidence Request Plan"
    )
    assert any("code_drop_envelope_rule" in line for line in markdown)
    assert any("notion_writeback" in line for line in markdown)
