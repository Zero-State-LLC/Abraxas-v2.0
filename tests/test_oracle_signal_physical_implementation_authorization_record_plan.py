from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.oracle_signal_physical_implementation_authorization_record_plan import (
    build_oracle_signal_physical_implementation_authorization_record_plan,
    render_oracle_signal_physical_implementation_authorization_record_plan_markdown,
    write_oracle_signal_physical_implementation_authorization_record_plan,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_oracle_signal_physical_implementation_authorization_record_plan.py",
    "local_oracle_signal_physical_implementation_authorization_record_plan_runner",
)


def test_record_plan_is_deterministic_and_ready() -> None:
    first = build_oracle_signal_physical_implementation_authorization_record_plan()
    second = build_oracle_signal_physical_implementation_authorization_record_plan()

    assert first["plan_hash"] == second["plan_hash"]
    assert first["status"] == "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_RECORD_PLAN_READY"
    assert first["record_plan_ready"] is True
    assert first["record_creation_authorized"] is False
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_record_plan_preserves_authority_locks() -> None:
    packet = build_oracle_signal_physical_implementation_authorization_record_plan()

    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["runtime_mutation_allowed"] is False
    assert packet["scheduler_mutation_allowed"] is False
    assert packet["ingest_runner_mutation_allowed"] is False
    assert packet["pipeline_or_route_mutation_allowed"] is False
    assert packet["queue_mutation_allowed"] is False
    assert packet["canon_mutation_allowed"] is False
    assert packet["forecast_weight_allowed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["safe_to_create_authorization_record"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    packet = write_oracle_signal_physical_implementation_authorization_record_plan(out_root=tmp_path)
    json_path = tmp_path / "out/operator_review/oracle_signal_physical_implementation_authorization_record_plan_001.latest.json"
    md_path = tmp_path / "out/operator_review/oracle_signal_physical_implementation_authorization_record_plan_001.latest.md"

    assert json_path.exists()
    assert md_path.exists()
    runner_packet = RUNNER.run(repo_root=".", out_root=tmp_path)
    assert runner_packet["plan_hash"] == packet["plan_hash"]

    schema = json.loads(
        Path(
            "contracts/operator_review/oracle_signal_physical_implementation_authorization_record_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_oracle_signal_physical_implementation_authorization_record_plan_markdown(packet)
    assert markdown[0] == "# Oracle Signal Physical Implementation Authorization Record Plan"
    assert any("authority_boundaries_acknowledged" in line for line in markdown)


def test_registry_includes_record_plan_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/operator_review/oracle_signal_physical_implementation_authorization_record_plan_001.latest.json" in (
        _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert "out/operator_review/oracle_signal_physical_implementation_authorization_record_plan_001.latest.md" in (
        _DERIVED_OPTIONAL_ARTIFACTS
    )
