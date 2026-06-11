from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.oracle_signal_shadow_intake_operator_review_decision_record import (
    build_oracle_signal_shadow_intake_operator_review_decision_record,
    render_oracle_signal_shadow_intake_operator_review_decision_record_markdown,
    write_oracle_signal_shadow_intake_operator_review_decision_record,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_oracle_signal_shadow_intake_operator_review_decision_record.py",
    "local_oracle_signal_shadow_intake_operator_review_decision_record_runner",
)


def test_decision_record_is_deterministic_and_review_only_approved() -> None:
    first = build_oracle_signal_shadow_intake_operator_review_decision_record()
    second = build_oracle_signal_shadow_intake_operator_review_decision_record()

    assert first["decision_record_hash"] == second["decision_record_hash"]
    assert first["status"] == "ORACLE_SIGNAL_SHADOW_INTAKE_OPERATOR_REVIEW_COMPLETION_APPROVED"
    assert first["selected_decision"] == "APPROVE_REVIEW_ONLY_COMPLETION"
    assert first["review_only_completion_approved"] is True
    assert first["receipt_accepted_as_review_only_evidence"] is True
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_decision_record_keeps_all_authority_denied() -> None:
    packet = build_oracle_signal_shadow_intake_operator_review_decision_record()

    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["runtime_mutation_allowed"] is False
    assert packet["scheduler_mutation_allowed"] is False
    assert packet["pipeline_or_route_mutation_allowed"] is False
    assert packet["queue_mutation_allowed"] is False
    assert packet["canon_mutation_allowed"] is False
    assert packet["forecast_weight_allowed"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["token_minting_allowed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["safe_to_prepare_planning_pr"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert "CORE_ORACLE_SIGNAL_IMPLEMENTATION" in packet["blocked_actions"]


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    packet = write_oracle_signal_shadow_intake_operator_review_decision_record(".", out_root=tmp_path)
    json_path = tmp_path / "out/operator_review/oracle_signal_shadow_intake_operator_review_decision_record_001.latest.json"
    md_path = tmp_path / "out/operator_review/oracle_signal_shadow_intake_operator_review_decision_record_001.latest.md"

    assert json_path.exists()
    assert md_path.exists()
    runner_packet = RUNNER.run(repo_root=".", out_root=tmp_path)
    assert runner_packet["decision_record_hash"] == packet["decision_record_hash"]

    schema = json.loads(
        Path("contracts/operator_review/oracle_signal_shadow_intake_operator_review_decision_record.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    validate(packet, schema)
    markdown = render_oracle_signal_shadow_intake_operator_review_decision_record_markdown(packet)
    assert markdown[0] == "# Oracle Signal Shadow Intake Operator Review Decision Record"
    assert any("APPROVE_REVIEW_ONLY_COMPLETION" in line for line in markdown)


def test_registry_includes_decision_record_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/oracle_signal_shadow_intake_operator_review_decision_record_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/operator_review/oracle_signal_shadow_intake_operator_review_decision_record_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
