from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_merge_anchor_source_selection_decision_record_plan import (
    build_abx_codegen_merge_anchor_source_selection_decision_record_plan,
    render_abx_codegen_merge_anchor_source_selection_decision_record_plan_markdown,
    write_abx_codegen_merge_anchor_source_selection_decision_record_plan,
)
from scripts.codegen import run_abx_codegen_merge_anchor_source_selection_decision_record_plan

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_codegen_source_selection_decision_record_plan_is_ready() -> None:
    first = build_abx_codegen_merge_anchor_source_selection_decision_record_plan(
        REPO_ROOT
    )
    second = build_abx_codegen_merge_anchor_source_selection_decision_record_plan(
        REPO_ROOT
    )

    assert first["decision_record_plan_hash"] == second["decision_record_plan_hash"]
    assert first["status"] == (
        "ABX_CODEGEN_MERGE_ANCHOR_SOURCE_SELECTION_DECISION_RECORD_PLAN_READY"
    )
    assert first["source_request_ready"] is True
    assert first["recommended_default_decision"] == "MAINTAIN_HOLD"
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert first["decision_record_created"] is False


def test_codegen_source_selection_decision_record_plan_carries_required_fields() -> None:
    packet = build_abx_codegen_merge_anchor_source_selection_decision_record_plan(
        REPO_ROOT
    )

    assert "selected_decision" in packet["required_decision_fields"]
    assert "operator_id" in packet["required_operator_identity_fields"]
    assert "reviewed_source_selection_request_hash" in packet["required_evidence_fields"]
    assert "implementation_unblocked" in packet["required_per_anchor_decision_fields"]
    assert any(
        "decision_record_001.latest.json" in item
        for item in packet["future_record_output_candidates"]
    )


def test_codegen_source_selection_decision_record_plan_keeps_anchor_holds() -> None:
    packet = build_abx_codegen_merge_anchor_source_selection_decision_record_plan(
        REPO_ROOT
    )

    requirements = {
        item["applies_to_anchor_id"]: item for item in packet["source_selection_requirements"]
    }
    assert len(requirements) == 5
    assert requirements["prompting_upgrade_stack_v0_1"]["candidate_page_id_or_url"] == (
        "NOT_COMPUTABLE"
    )
    assert requirements["code_drop_envelope_rule"]["selection_authorized_by_plan"] is False
    assert requirements["all"]["implementation_unblocked_by_record"] is False


def test_codegen_source_selection_decision_record_plan_denies_authority() -> None:
    packet = build_abx_codegen_merge_anchor_source_selection_decision_record_plan(
        REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert "OPERATOR_DECISION_RECORD_CREATION" in packet["blocked_actions"]
    assert "CODEGEN_IMPLEMENTATION_UNBLOCK" in packet["blocked_actions"]


def test_codegen_source_selection_decision_record_plan_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_merge_anchor_source_selection_decision_record_plan(
        tmp_path
    )

    assert packet["status"] == (
        "ABX_CODEGEN_MERGE_ANCHOR_SOURCE_SELECTION_DECISION_RECORD_PLAN_BLOCKED"
    )
    assert packet["source_request_ready"] is False
    assert packet["source_selection_requirements"] == []


def test_codegen_source_selection_decision_record_plan_writer_schema_and_markdown(
    tmp_path: Path,
) -> None:
    packet = write_abx_codegen_merge_anchor_source_selection_decision_record_plan(
        REPO_ROOT,
        out_root=tmp_path,
    )
    json_path = (
        tmp_path
        / "out/operator_review/"
        "abx_codegen_merge_anchor_source_selection_decision_record_plan_001.latest.json"
    )
    md_path = json_path.with_suffix(".md")

    assert json_path.exists()
    assert md_path.exists()
    runner_packet = run_abx_codegen_merge_anchor_source_selection_decision_record_plan.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )
    assert runner_packet["decision_record_plan_hash"] == packet["decision_record_plan_hash"]

    schema = json.loads(
        (
            REPO_ROOT
            / "contracts/operator_review/"
            "abx_codegen_merge_anchor_source_selection_decision_record_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_abx_codegen_merge_anchor_source_selection_decision_record_plan_markdown(
        packet
    )
    assert markdown[0] == (
        "# ABX Codegen Merge Anchor Source Selection Decision Record Plan"
    )
    assert any("selected_decision" in line for line in markdown)
