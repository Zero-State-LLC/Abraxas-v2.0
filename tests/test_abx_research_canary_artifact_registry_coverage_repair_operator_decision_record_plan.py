from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan import (
    PLAN_ID,
    build_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan,
    write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan.py",
    "local_abx_research_canary_registry_repair_decision_record_plan_runner",
)
SCHEMA_PATH = (
    "contracts/operator_review/"
    "abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan.v1.schema.json"
)


def test_decision_record_plan_is_deterministic() -> None:
    first = build_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan(
        source_root=REPO_ROOT
    )
    second = build_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan(
        source_root=REPO_ROOT
    )
    assert first["decision_record_plan_hash"] == second["decision_record_plan_hash"]
    assert first["decision_record_plan_id"] == PLAN_ID


def test_decision_record_plan_ready() -> None:
    packet = build_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan(
        source_root=REPO_ROOT
    )
    assert packet["status"] == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_RECORD_PLAN_READY"
    assert "AUTHORIZE_REGISTRY_REPAIR_EXECUTION_SPEC" in packet["decision_options"]


def test_writer_and_schema(tmp_path: Path) -> None:
    packet = write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan(
        source_root=REPO_ROOT,
        out_root=tmp_path,
    )
    json_path = (
        tmp_path
        / "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan_001.latest.json"
    )
    assert json_path.exists()
    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_root=tmp_path)
    assert runner_packet["decision_record_plan_hash"] == packet["decision_record_plan_hash"]
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_registry_includes_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
