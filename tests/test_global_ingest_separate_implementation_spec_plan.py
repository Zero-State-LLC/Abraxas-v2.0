from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.global_ingest_operator_decision_record import write_global_ingest_operator_decision_record
from core.global_ingest_separate_implementation_spec_plan import (
    build_global_ingest_separate_implementation_spec_plan,
    render_global_ingest_separate_implementation_spec_plan_markdown,
    write_global_ingest_separate_implementation_spec_plan,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_global_ingest_separate_implementation_spec_plan.py",
    "local_global_ingest_separate_implementation_spec_plan_runner",
)


def test_spec_plan_is_deterministic_and_enabled_by_decision_record() -> None:
    first = build_global_ingest_separate_implementation_spec_plan()
    second = build_global_ingest_separate_implementation_spec_plan()

    assert first["spec_plan_hash"] == second["spec_plan_hash"]
    assert first["status"] == "GLOBAL_INGEST_SEPARATE_IMPLEMENTATION_SPEC_PLAN_CONSUMED_BY_IMPLEMENTATION_SPEC"
    assert first["decision_record_approved_spec_authoring"] is True
    assert first["spec_authoring_allowed"] is True
    assert first["safe_to_prepare_planning_pr"] is False
    assert first["implementation_spec_observed"] is True
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_spec_plan_blocks_direct_implementation_and_runtime_mutation() -> None:
    packet = build_global_ingest_separate_implementation_spec_plan()

    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["runtime_mutation_allowed"] is False
    assert packet["scheduler_mutation_allowed"] is False
    assert packet["pipeline_or_route_mutation_allowed"] is False
    assert packet["canon_mutation_allowed"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert "core/oracle_signal.py" in packet["blocked_delivery_surfaces"]


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    write_global_ingest_operator_decision_record(".", out_root=tmp_path)
    packet = write_global_ingest_separate_implementation_spec_plan(tmp_path, out_root=tmp_path)

    json_path = tmp_path / "out/operator_review/global_ingest_separate_implementation_spec_plan_001.latest.json"
    md_path = tmp_path / "out/operator_review/global_ingest_separate_implementation_spec_plan_001.latest.md"
    assert json_path.exists()
    assert md_path.exists()

    runner_packet = RUNNER.run(repo_root=tmp_path, out_root=tmp_path)
    assert runner_packet["spec_plan_hash"] == packet["spec_plan_hash"]

    schema = json.loads(
        Path("contracts/operator_review/global_ingest_separate_implementation_spec_plan.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    validate(packet, schema)
    markdown = render_global_ingest_separate_implementation_spec_plan_markdown(packet)
    assert markdown[0] == "# Global Ingest Separate Implementation Spec Plan"
    assert any("core/oracle_signal.py" in line for line in markdown)


def test_registry_includes_spec_plan_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/global_ingest_separate_implementation_spec_plan_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/operator_review/global_ingest_separate_implementation_spec_plan_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
