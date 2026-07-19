from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.grok_abx_runes_operator_decision_record_dry_run import (
    DRY_RUN_JSON_PATH,
    build_grok_abx_runes_operator_decision_record_dry_run,
    render_grok_abx_runes_operator_decision_record_dry_run_markdown,
    write_grok_abx_runes_operator_decision_record_dry_run,
)
from scripts.codegen import run_grok_abx_runes_operator_decision_record_dry_run

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "grok_abx_runes_operator_decision_record_dry_run.v1.schema.json"
)


def test_grok_abx_runes_operator_decision_record_dry_run_ready() -> None:
    first = build_grok_abx_runes_operator_decision_record_dry_run(REPO_ROOT)
    second = build_grok_abx_runes_operator_decision_record_dry_run(REPO_ROOT)

    assert first["dry_run_hash"] == second["dry_run_hash"]
    assert first["status"] == "GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_DRY_RUN_READY"
    assert first["source_plan_ready"] is True
    assert first["validation_passed"] is True
    assert first["simulated_only"] is True
    assert first["operator_input_required"] is True
    assert "grok_claim_disposition_not_attested" in first["validation_blockers"]
    assert first["recommended_next_lane"] == "GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_REVIEW"


def test_grok_abx_runes_operator_decision_record_dry_run_simulates_hold_only() -> None:
    packet = build_grok_abx_runes_operator_decision_record_dry_run(REPO_ROOT)
    simulated = packet["simulated_decision_record"]

    assert simulated["selected_decision"] == "HOLD_FOR_OPERATOR_REVIEW"
    assert (
        simulated["selected_follow_on_action"]
        == "MAINTAIN_GROK_ABX_RUNES_OPERATOR_REVIEW_HOLD"
    )
    assert simulated["terminal_authority_summary"] == "SIMULATED_NO_AUTHORITY_GRANTED"
    assert simulated["attested_field_count"] == 0
    assert simulated["missing_attested_field_count"] > 0
    assert "selected_decision" in simulated["required_field_names"]
    assert simulated["operator_decision_attested"] is False
    assert simulated["decision_record_created"] is False
    assert simulated["external_backlog_accepted"] is False


def test_grok_abx_runes_operator_decision_record_dry_run_denies_authority() -> None:
    packet = build_grok_abx_runes_operator_decision_record_dry_run(REPO_ROOT)
    simulated = packet["simulated_decision_record"]

    assert packet["decision_record_created"] is False
    assert packet["authorization_record_created"] is False
    assert packet["external_backlog_accepted"] is False
    assert packet["separate_registration_planning_authorized"] is False
    assert packet["catalog_mutation_authorized"] is False
    assert packet["rune_registration_authorized"] is False
    assert packet["yggdrasil_binding_mutation_authorized"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["valid_for_execution"] is False
    assert simulated["separate_registration_planning_authorized"] is False
    assert simulated["rune_registration_authorized"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_grok_abx_runes_operator_decision_record_dry_run_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_grok_abx_runes_operator_decision_record_dry_run(tmp_path)

    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["source_plan_ready"] is False
    assert packet["validation_passed"] is False
    assert packet["simulated_decision_record"]["required_field_names"] == []
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_grok_abx_runes_operator_decision_record_dry_run_schema_and_hash_are_stable() -> None:
    packet = build_grok_abx_runes_operator_decision_record_dry_run(REPO_ROOT)
    packet_without_hash = dict(packet)
    dry_run_hash = packet_without_hash.pop("dry_run_hash")

    assert dry_run_hash == canonical_hash(packet_without_hash)
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_grok_abx_runes_operator_decision_record_dry_run_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_grok_abx_runes_operator_decision_record_dry_run(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / DRY_RUN_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_grok_abx_runes_operator_decision_record_dry_run.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["dry_run_hash"] == packet["dry_run_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_grok_abx_runes_operator_decision_record_dry_run_markdown() -> None:
    packet = build_grok_abx_runes_operator_decision_record_dry_run(REPO_ROOT)
    markdown = render_grok_abx_runes_operator_decision_record_dry_run_markdown(packet)

    assert markdown[0] == "# Grok ABX-Runes Operator Decision Record Dry Run"
    assert any("grok_claim_disposition_not_attested" in line for line in markdown)
    assert any("MAINTAIN_GROK_ABX_RUNES_OPERATOR_REVIEW_HOLD" in line for line in markdown)
