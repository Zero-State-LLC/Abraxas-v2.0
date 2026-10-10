from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_research_canary_artifact_registry_coverage_repair_operator_decision_record import (
    AUTHORIZED_DECISION,
    EXECUTION_SPEC_PLAN_LANE,
    RECORD_ID,
    build_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record,
    write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record,
)
from core.abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan import (
    write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan,
)
from tests._repo_mirror import make_repo_mirror
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "scripts/run_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record.py",
    "local_abx_research_canary_registry_repair_decision_record_runner",
)
SCHEMA_PATH = (
    "contracts/operator_review/"
    "abx_research_canary_artifact_registry_coverage_repair_operator_decision_record.v1.schema.json"
)


def test_decision_record_authorizes_spec_authoring(tmp_path: Path) -> None:
    write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan(
        source_root=REPO_ROOT,
        out_root=tmp_path,
    )
    packet = build_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record(
        source_root=tmp_path
    )

    assert packet["selected_decision"] == AUTHORIZED_DECISION
    assert (
        packet["status"]
        == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_RECORD_APPROVED_FOR_EXECUTION_SPEC"
    )
    assert packet["registry_repair_execution_spec_authoring_approved"] is True
    assert packet["execution_authority"] is False
    assert packet["registry_mutation_performed"] is False
    assert packet["recommended_next_lane"] == EXECUTION_SPEC_PLAN_LANE
    assert packet["decision_record_id"] == RECORD_ID


def test_decision_record_is_deterministic(tmp_path: Path) -> None:
    # The plan is read back from the root it is written to: use a working-tree
    # mirror so the tracked out/ plan is not rewritten.
    mirror = make_repo_mirror(tmp_path)
    write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan(
        source_root=mirror
    )
    first = build_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record(
        source_root=mirror
    )
    second = build_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record(
        source_root=mirror
    )
    assert first["decision_record_hash"] == second["decision_record_hash"]


def test_writer_and_schema(tmp_path: Path) -> None:
    write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan(
        source_root=REPO_ROOT,
        out_root=tmp_path,
    )
    packet = write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record(
        source_root=REPO_ROOT,
        out_root=tmp_path,
    )
    json_path = (
        tmp_path
        / "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_001.latest.json"
    )
    assert json_path.exists()
    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_root=tmp_path)
    assert runner_packet["decision_record_hash"] == packet["decision_record_hash"]
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_registry_includes_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
