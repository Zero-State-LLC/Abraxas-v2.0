from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_merge_anchor_source_selection_decision_record_review import (
    build_abx_codegen_merge_anchor_source_selection_decision_record_review,
    render_abx_codegen_merge_anchor_source_selection_decision_record_review_markdown,
    write_abx_codegen_merge_anchor_source_selection_decision_record_review,
)
from core.canonical.json import canonical_hash
from scripts.codegen import run_abx_codegen_merge_anchor_source_selection_decision_record_review

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_codegen_source_selection_decision_record_review_holds_for_operator() -> None:
    packet = build_abx_codegen_merge_anchor_source_selection_decision_record_review(
        REPO_ROOT
    )

    assert packet["status"] == (
        "ABX_CODEGEN_MERGE_ANCHOR_SOURCE_SELECTION_DECISION_RECORD_REVIEW_HELD_FOR_OPERATOR"
    )
    assert packet["source_dry_run_ready"] is True
    assert packet["selected_operator_decision"] == "MAINTAIN_HOLD"
    assert packet["operator_attestations_present"] is False
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_source_selection_decision_record_review_denies_authority() -> None:
    packet = build_abx_codegen_merge_anchor_source_selection_decision_record_review(
        REPO_ROOT
    )

    assert packet["decision_record_created"] is False
    assert packet["canonical_source_selection_authorized"] is False
    assert packet["canonical_source_selection_performed"] is False
    assert packet["implementation_authorized"] is False
    assert packet["implementation_unblocked"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_source_selection_decision_record_review_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_merge_anchor_source_selection_decision_record_review(
        tmp_path
    )

    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["source_dry_run_ready"] is False
    assert packet["source_readiness"] == "SOURCE_DRY_RUN_MISSING"
    assert packet["reviewed_anchor_count"] == 0
    assert packet["selected_operator_decision"] == "NOT_COMPUTABLE"


def test_codegen_source_selection_decision_record_review_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_merge_anchor_source_selection_decision_record_review(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("review_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads(
        (
            REPO_ROOT
            / "contracts/operator_review/"
            "abx_codegen_merge_anchor_source_selection_decision_record_review.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)


def test_codegen_source_selection_decision_record_review_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_abx_codegen_merge_anchor_source_selection_decision_record_review(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = (
        tmp_path
        / "out/operator_review/"
        "abx_codegen_merge_anchor_source_selection_decision_record_review_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_merge_anchor_source_selection_decision_record_review.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["review_hash"] == packet["review_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_source_selection_decision_record_review_markdown() -> None:
    packet = build_abx_codegen_merge_anchor_source_selection_decision_record_review(
        REPO_ROOT
    )
    markdown = render_abx_codegen_merge_anchor_source_selection_decision_record_review_markdown(
        packet
    )

    assert markdown[0] == (
        "# ABX Codegen Merge Anchor Source Selection Decision Record Review"
    )
    assert any("operator_attestations_present" in line for line in markdown)
    assert any("decision_record_creation_denied" in line for line in markdown)
