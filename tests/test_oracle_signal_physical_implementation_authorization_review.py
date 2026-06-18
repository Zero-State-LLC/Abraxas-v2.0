from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.oracle_signal_physical_implementation_authorization_review import (
    build_oracle_signal_physical_implementation_authorization_review,
    render_oracle_signal_physical_implementation_authorization_review_markdown,
    write_oracle_signal_physical_implementation_authorization_review,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_oracle_signal_physical_implementation_authorization_review.py",
    "local_oracle_signal_physical_implementation_authorization_review_runner",
)


def test_review_is_deterministic_and_reflects_operator_authorization_state() -> None:
    first = build_oracle_signal_physical_implementation_authorization_review()
    second = build_oracle_signal_physical_implementation_authorization_review()

    assert first["review_hash"] == second["review_hash"]
    assert first["status"] in {
        "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_REVIEW_HELD_FOR_OPERATOR",
        "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_REVIEW_AUTHORIZATION_CONSUMED",
    }
    assert first["review_requested"] is True
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_review_preserves_authority_locks() -> None:
    packet = build_oracle_signal_physical_implementation_authorization_review()

    assert packet["execution_authority"] is False
    assert packet["runtime_mutation_allowed"] is False
    assert packet["scheduler_mutation_allowed"] is False
    assert packet["ingest_runner_mutation_allowed"] is False
    assert packet["pipeline_or_route_mutation_allowed"] is False
    assert packet["queue_mutation_allowed"] is False
    assert packet["canon_mutation_allowed"] is False
    assert packet["forecast_weight_allowed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["safe_to_prepare_implementation_pr"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_review_binds_current_planning_sources() -> None:
    packet = build_oracle_signal_physical_implementation_authorization_review()

    assert packet["source_paths"]["repo_execution_prep"] == (
        "out/operator_review/global_pipeline_repo_execution_prep_001.latest.json"
    )
    assert packet["source_paths"]["global_ingest_operator_decision_record"] == (
        "out/operator_review/global_ingest_operator_decision_record_001.latest.json"
    )
    assert packet["source_paths"]["global_ingest_adapter_spine_implementation_spec"] == (
        "out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.json"
    )
    assert "CORE_ORACLE_SIGNAL_IMPLEMENTATION" in packet["blocked_actions"]


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    packet = write_oracle_signal_physical_implementation_authorization_review(out_root=tmp_path)
    json_path = tmp_path / "out/operator_review/oracle_signal_physical_implementation_authorization_review_001.latest.json"
    md_path = tmp_path / "out/operator_review/oracle_signal_physical_implementation_authorization_review_001.latest.md"

    assert json_path.exists()
    assert md_path.exists()
    runner_packet = RUNNER.run(repo_root=".", out_root=tmp_path)
    assert runner_packet["review_hash"] == packet["review_hash"]

    schema = json.loads(
        Path(
            "contracts/operator_review/oracle_signal_physical_implementation_authorization_review.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_oracle_signal_physical_implementation_authorization_review_markdown(packet)
    assert markdown[0] == "# Oracle Signal Physical Implementation Authorization Review"
    assert any("COLLECT_EXPLICIT_PHYSICAL_IMPLEMENTATION_OPERATOR_AUTHORIZATION" in line for line in markdown)


def test_registry_includes_review_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/operator_review/oracle_signal_physical_implementation_authorization_review_001.latest.json" in (
        _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert "out/operator_review/oracle_signal_physical_implementation_authorization_review_001.latest.md" in (
        _DERIVED_OPTIONAL_ARTIFACTS
    )
