from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_research_canary_artifact_registry_coverage_repair_execution_authorization_gate import (
    AUTHORIZATION_RECORD_LANE,
    BLOCKED_ACTIONS,
    GATE_ID,
    build_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_gate,
    write_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_gate,
)
from core.abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan import (
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
    "Scripts/run_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_gate.py",
    "local_abx_research_canary_registry_repair_exec_auth_gate_runner",
)
SCHEMA_PATH = (
    "contracts/operator_review/"
    "abx_research_canary_artifact_registry_coverage_repair_execution_authorization_gate.v1.schema.json"
)


def _bootstrap(tmp_path: Path) -> None:
    write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan(
        source_root=REPO_ROOT,
        out_root=tmp_path,
    )
    write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_record(
        source_root=REPO_ROOT,
        out_root=tmp_path,
    )
    write_abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan(
        source_root=REPO_ROOT,
        out_root=tmp_path,
    )


def test_authorization_gate_is_deterministic_and_held(tmp_path: Path) -> None:
    _bootstrap(tmp_path)
    first = build_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_gate(
        source_root=tmp_path
    )
    second = build_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_gate(
        source_root=tmp_path
    )

    assert first["authorization_gate_hash"] == second["authorization_gate_hash"]
    assert first["authorization_gate_id"] == GATE_ID
    assert (
        first["status"]
        == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_EXECUTION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
    )
    assert first["operator_authorization_required"] is True
    assert first["authorization_granted"] is False
    assert first["recommended_next_lane"] == AUTHORIZATION_RECORD_LANE


def test_authorization_gate_denies_execution_authority(tmp_path: Path) -> None:
    _bootstrap(tmp_path)
    packet = build_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_gate(
        source_root=tmp_path
    )

    assert packet["execution_authority"] is False
    assert packet["registry_mutation_performed"] is False
    assert packet["safe_to_prepare_execution_pr"] is False
    for blocked_action in BLOCKED_ACTIONS:
        assert blocked_action in packet["blocked_actions"]


def test_writer_and_schema(tmp_path: Path) -> None:
    _bootstrap(tmp_path)
    packet = write_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_gate(
        source_root=tmp_path,
        out_root=tmp_path,
    )
    json_path = (
        tmp_path
        / "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_execution_authorization_gate_001.latest.json"
    )
    assert json_path.exists()
    runner_packet = RUNNER.run(repo_root=tmp_path, out_root=tmp_path)
    assert runner_packet["authorization_gate_hash"] == packet["authorization_gate_hash"]
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_registry_includes_gate_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_execution_authorization_gate_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
