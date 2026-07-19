from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_merge_anchor_source_selection_request import (
    build_abx_codegen_merge_anchor_source_selection_request,
    render_abx_codegen_merge_anchor_source_selection_request_markdown,
    write_abx_codegen_merge_anchor_source_selection_request,
)
from scripts.codegen import run_abx_codegen_merge_anchor_source_selection_request

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_codegen_source_selection_request_is_held() -> None:
    first = build_abx_codegen_merge_anchor_source_selection_request(REPO_ROOT)
    second = build_abx_codegen_merge_anchor_source_selection_request(REPO_ROOT)

    assert first["request_hash"] == second["request_hash"]
    assert first["status"] == "ABX_CODEGEN_MERGE_ANCHOR_SOURCE_SELECTION_REQUEST_HELD"
    assert first["decision_scope"] == (
        "CODEGEN_MERGE_ANCHOR_CANONICAL_SOURCE_SELECTION_REQUIRED"
    )
    assert first["normalization_plan_ready_for_review"] is True
    assert first["recommended_decision"] == "HOLD_FOR_OPERATOR_REVIEW"
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_codegen_source_selection_request_carries_required_decisions() -> None:
    packet = build_abx_codegen_merge_anchor_source_selection_request(REPO_ROOT)

    decisions = {item["decision"]: item for item in packet["source_selection_requests"]}
    assert len(decisions) == 5
    assert decisions["select_canonical_prompting_upgrade_stack_source"][
        "candidate_page_id_or_url"
    ] == "NOT_COMPUTABLE"
    assert decisions["confirm_global_code_drop_envelope_rule_source"][
        "applies_to_anchor_id"
    ] == "code_drop_envelope_rule"
    assert decisions["confirm_no_implementation_unblock_from_normalization"][
        "implementation_unblocked_by_request"
    ] is False


def test_codegen_source_selection_request_denies_authority() -> None:
    packet = build_abx_codegen_merge_anchor_source_selection_request(REPO_ROOT)

    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["safe_to_auto_continue"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert "CANONICAL_SOURCE_SELECTION_BY_AGENT" in packet["blocked_actions"]
    assert "CODEGEN_IMPLEMENTATION_UNBLOCK" in packet["blocked_actions"]


def test_codegen_source_selection_request_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_merge_anchor_source_selection_request(tmp_path)

    assert packet["status"] == "ABX_CODEGEN_MERGE_ANCHOR_SOURCE_SELECTION_REQUEST_BLOCKED"
    assert packet["normalization_plan_ready_for_review"] is False
    assert packet["source_selection_requests"] == []


def test_codegen_source_selection_request_writer_schema_and_markdown(
    tmp_path: Path,
) -> None:
    packet = write_abx_codegen_merge_anchor_source_selection_request(
        REPO_ROOT,
        out_root=tmp_path,
    )
    json_path = (
        tmp_path
        / "out/operator_review/"
        "abx_codegen_merge_anchor_source_selection_request_001.latest.json"
    )
    md_path = json_path.with_suffix(".md")

    assert json_path.exists()
    assert md_path.exists()
    runner_packet = run_abx_codegen_merge_anchor_source_selection_request.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )
    assert runner_packet["request_hash"] == packet["request_hash"]

    schema = json.loads(
        (
            REPO_ROOT
            / "contracts/operator_review/"
            "abx_codegen_merge_anchor_source_selection_request.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_abx_codegen_merge_anchor_source_selection_request_markdown(packet)
    assert markdown[0] == "# ABX Codegen Merge Anchor Source Selection Request"
    assert any("HOLD_FOR_OPERATOR_REVIEW" in line for line in markdown)
