from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_merge_anchor_source_selection_decision_record_dry_run import (
    build_abx_codegen_merge_anchor_source_selection_decision_record_dry_run,
    render_abx_codegen_merge_anchor_source_selection_decision_record_dry_run_markdown,
    write_abx_codegen_merge_anchor_source_selection_decision_record_dry_run,
)
from core.canonical.json import canonical_hash
from scripts.codegen import run_abx_codegen_merge_anchor_source_selection_decision_record_dry_run

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_codegen_source_selection_decision_record_dry_run_ready() -> None:
    packet = build_abx_codegen_merge_anchor_source_selection_decision_record_dry_run(
        REPO_ROOT
    )

    assert packet["status"] == (
        "ABX_CODEGEN_MERGE_ANCHOR_SOURCE_SELECTION_DECISION_RECORD_DRY_RUN_READY"
    )
    assert packet["source_plan_ready"] is True
    assert packet["validation_passed"] is True
    assert packet["simulated_only"] is True
    assert packet["operator_input_required"] is True
    assert "operator_decision_not_attested" in packet["validation_blockers"]
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_codegen_source_selection_decision_record_dry_run_simulates_hold_only() -> None:
    packet = build_abx_codegen_merge_anchor_source_selection_decision_record_dry_run(
        REPO_ROOT
    )
    simulated = packet["simulated_decision_record"]
    per_anchor = {row["anchor_id"]: row for row in simulated["per_anchor_decisions"]}

    assert simulated["selected_decision"] == "MAINTAIN_HOLD"
    assert simulated["operator_decision_attested"] is False
    assert simulated["decision_record_created"] is False
    assert simulated["canonical_source_selection_authorized"] is False
    assert per_anchor["prompting_upgrade_stack_v0_1"]["selected_decision"] == (
        "MAINTAIN_HOLD"
    )
    assert per_anchor["all"]["implementation_unblocked"] is False


def test_codegen_source_selection_decision_record_dry_run_denies_authority() -> None:
    packet = build_abx_codegen_merge_anchor_source_selection_decision_record_dry_run(
        REPO_ROOT
    )

    assert packet["decision_record_created"] is False
    assert packet["operator_decision_attested"] is False
    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_source_selection_decision_record_dry_run_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_merge_anchor_source_selection_decision_record_dry_run(
        tmp_path
    )

    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["source_plan_ready"] is False
    assert packet["validation_passed"] is False
    assert packet["simulated_decision_record"]["per_anchor_decisions"] == []


def test_codegen_source_selection_decision_record_dry_run_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_merge_anchor_source_selection_decision_record_dry_run(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("dry_run_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads(
        (
            REPO_ROOT
            / "contracts/operator_review/"
            "abx_codegen_merge_anchor_source_selection_decision_record_dry_run.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)


def test_codegen_source_selection_decision_record_dry_run_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_abx_codegen_merge_anchor_source_selection_decision_record_dry_run(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = (
        tmp_path
        / "out/operator_review/"
        "abx_codegen_merge_anchor_source_selection_decision_record_dry_run_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_merge_anchor_source_selection_decision_record_dry_run.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["dry_run_hash"] == packet["dry_run_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_source_selection_decision_record_dry_run_markdown() -> None:
    packet = build_abx_codegen_merge_anchor_source_selection_decision_record_dry_run(
        REPO_ROOT
    )
    markdown = render_abx_codegen_merge_anchor_source_selection_decision_record_dry_run_markdown(
        packet
    )

    assert markdown[0] == (
        "# ABX Codegen Merge Anchor Source Selection Decision Record Dry Run"
    )
    assert any("operator_decision_not_attested" in line for line in markdown)
    assert any("prompting_upgrade_stack_v0_1" in line for line in markdown)
