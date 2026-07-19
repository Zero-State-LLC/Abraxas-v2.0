from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan import (
    build_abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan,
    render_abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts.codegen import (
    run_abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan.v1.schema.json"
)


def test_codegen_merge_anchor_evidence_normalization_plan_is_held() -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan(
        repo_root=REPO_ROOT
    )

    assert packet["merge_anchor_evidence_normalization_plan_status"] == (
        "ABX_CODEGEN_MERGE_ANCHOR_EVIDENCE_NORMALIZATION_PLAN_HELD_FOR_OPERATOR"
    )
    assert packet["source_merge_anchor_evidence_request_plan"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_merge_anchor_evidence_normalization_rows_are_source_observed() -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan(
        repo_root=REPO_ROOT
    )

    anchors = {item["anchor_id"]: item for item in packet["normalized_anchor_evidence"]}
    assert len(anchors) == 10
    assert anchors["codegen_upgrade_v0_4"]["governance_posture"] == "CANON_SHADOW"
    assert "may_not_merge_to_main" in anchors["codegen_upgrade_v0_4"][
        "implementation_constraints"
    ]
    assert anchors["rune_promotion_gate"]["notion_page_id_or_url"] == (
        "3523e8ba-2f5c-814e-a011-d87765678d34"
    )
    assert "no_subsystem_may_self_promote" in anchors["rune_promotion_gate"][
        "merge_rules"
    ]
    assert anchors["prompting_upgrade_stack_v0_1"]["notion_page_id_or_url"] == (
        "NOT_COMPUTABLE"
    )


def test_codegen_merge_anchor_evidence_normalization_summary_requires_operator() -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan(
        repo_root=REPO_ROOT
    )

    summary = packet["normalization_summary"]
    assert summary["requested_anchor_count"] == 10
    assert summary["observed_anchor_count"] == 10
    assert summary["operator_decision_required"] is True
    assert summary["all_requested_evidence_present"] is False
    assert summary["implementation_unblocked"] is False
    assert "prompting_upgrade_stack_v0_1" in summary["unresolved_anchor_ids"]
    assert "code_drop_envelope_rule" in summary["unresolved_anchor_ids"]


def test_codegen_merge_anchor_evidence_normalization_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert "canonical_source_selection" in packet["blocked_actions"]
    assert "implementation_unblock" in packet["blocked_actions"]
    assert "forecast_routing" in packet["blocked_actions"]


def test_codegen_merge_anchor_evidence_normalization_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan(
        repo_root=tmp_path
    )

    assert packet["merge_anchor_evidence_normalization_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_merge_anchor_evidence_request_plan"]["source_ready"] is False
    assert packet["normalized_anchor_evidence"] == []


def test_codegen_merge_anchor_evidence_normalization_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_merge_anchor_evidence_normalization_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_merge_anchor_evidence_normalization_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan(
        repo_root=REPO_ROOT
    )
    markdown = (
        render_abx_codegen_intelligence_spine_merge_anchor_evidence_normalization_plan_markdown(
            packet
        )
    )

    assert markdown[0] == (
        "# ABX Codegen Intelligence Spine Merge Anchor Evidence Normalization Plan"
    )
    assert any("rune_promotion_gate" in line for line in markdown)
    assert any("select_canonical_prompting_upgrade_stack_source" in line for line in markdown)
