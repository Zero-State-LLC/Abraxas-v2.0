from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.oracle_signal_shadow_intake_operator_review_request import (
    build_oracle_signal_shadow_intake_operator_review_request,
    render_oracle_signal_shadow_intake_operator_review_request_markdown,
    write_oracle_signal_shadow_intake_operator_review_request,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "scripts/run_oracle_signal_shadow_intake_operator_review_request.py",
    "local_oracle_signal_shadow_intake_operator_review_request_runner",
)


def test_review_request_is_deterministic_and_held() -> None:
    first = build_oracle_signal_shadow_intake_operator_review_request()
    second = build_oracle_signal_shadow_intake_operator_review_request()

    assert first["request_hash"] == second["request_hash"]
    assert first["status"] == "ORACLE_SIGNAL_SHADOW_INTAKE_OPERATOR_REVIEW_REQUEST_HELD"
    assert first["decision_scope"] == "SHADOW_INTAKE_RECEIPT_REVIEW_REQUIRED"
    assert first["receipt_ready_for_review"] is True
    assert first["recommended_decision"] == "HOLD_SHADOW_RECEIPT"
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_review_request_denies_authority_and_auto_continuation() -> None:
    packet = build_oracle_signal_shadow_intake_operator_review_request()

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


def test_review_request_carries_required_review_items_and_blocks_implementation() -> None:
    packet = build_oracle_signal_shadow_intake_operator_review_request()

    assert "HOLD_SHADOW_RECEIPT" in packet["decision_options"]
    assert "APPROVE_REVIEW_ONLY_COMPLETION" in packet["decision_options"]
    assert "CORE_ORACLE_SIGNAL_IMPLEMENTATION" in packet["blocked_actions"]
    assert "INGEST_RUNNER_BEHAVIOR_MUTATION" in packet["blocked_actions"]
    assert any("SOURCE_URI_ONLY_NO_FETCH" in item for item in packet["required_operator_review_items"])
    assert any("REFERENCE_ONLY_NOT_BOUND" in item for item in packet["required_operator_review_items"])


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    packet = write_oracle_signal_shadow_intake_operator_review_request(".", out_root=tmp_path)
    json_path = tmp_path / "out/operator_review/oracle_signal_shadow_intake_operator_review_request_001.latest.json"
    md_path = tmp_path / "out/operator_review/oracle_signal_shadow_intake_operator_review_request_001.latest.md"

    assert json_path.exists()
    assert md_path.exists()
    runner_packet = RUNNER.run(repo_root=".", out_root=tmp_path)
    assert runner_packet["request_hash"] == packet["request_hash"]

    schema = json.loads(
        Path("contracts/operator_review/oracle_signal_shadow_intake_operator_review_request.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    validate(packet, schema)
    markdown = render_oracle_signal_shadow_intake_operator_review_request_markdown(packet)
    assert markdown[0] == "# Oracle Signal Shadow Intake Operator Review Request"
    assert any("HOLD_SHADOW_RECEIPT" in line for line in markdown)


def test_registry_includes_review_request_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/oracle_signal_shadow_intake_operator_review_request_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/operator_review/oracle_signal_shadow_intake_operator_review_request_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
