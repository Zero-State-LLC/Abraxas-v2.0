from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan import (
    AUTHORIZATION_GATE_LANE,
    SPEC_PLAN_ID,
    build_abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan,
    write_abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan,
)
from core.abx_research_canary_artifact_registry_coverage_repair_operator_decision_record import (
    write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record,
)
from core.abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan import (
    write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan.py",
    "local_abx_research_canary_registry_repair_execution_spec_plan_runner",
)
SCHEMA_PATH = (
    "contracts/operator_review/"
    "abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan.v1.schema.json"
)


def _bootstrap(repo_root: Path, out_root: Path | None = None) -> None:
    write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan(
        source_root=repo_root,
        out_root=out_root,
    )
    write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record(
        source_root=repo_root,
        out_root=out_root,
    )


def test_execution_spec_plan_ready() -> None:
    _bootstrap(REPO_ROOT)
    packet = build_abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan(
        source_root=REPO_ROOT
    )

    assert packet["status"] == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_EXECUTION_SPEC_PLAN_READY"
    assert packet["spec_plan_id"] == SPEC_PLAN_ID
    assert packet["registry_mutation_performed"] is False
    assert packet["execution_allowed"] is False
    assert len(packet["proposed_repair_steps"]) == 4
    assert packet["recommended_next_lane"] == AUTHORIZATION_GATE_LANE


def test_execution_spec_plan_is_deterministic() -> None:
    _bootstrap(REPO_ROOT)
    first = build_abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan(
        source_root=REPO_ROOT
    )
    second = build_abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan(
        source_root=REPO_ROOT
    )
    assert first["spec_plan_hash"] == second["spec_plan_hash"]


def test_writer_and_schema(tmp_path: Path) -> None:
    _bootstrap(REPO_ROOT, out_root=tmp_path)
    packet = write_abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan(
        source_root=REPO_ROOT,
        out_root=tmp_path,
    )
    json_path = (
        tmp_path
        / "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan_001.latest.json"
    )
    assert json_path.exists()
    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_root=tmp_path)
    assert runner_packet["spec_plan_hash"] == packet["spec_plan_hash"]
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_registry_includes_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
