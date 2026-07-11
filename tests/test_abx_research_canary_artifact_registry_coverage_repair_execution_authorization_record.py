from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_research_canary_artifact_registry_coverage_repair_execution_authorization_gate import (
    write_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_gate,
)
from core.abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record import (
    BLOCKED_ACTIONS,
    RECORD_ID,
    SCOPED_EXECUTION_RECEIPT_LANE,
    SCOPED_REPAIR_ACTIONS,
    build_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record,
    write_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record,
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
    "scripts/run_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record.py",
    "local_abx_research_canary_registry_repair_exec_auth_record_runner",
)
SCHEMA_PATH = (
    "contracts/operator_review/"
    "abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record.v1.schema.json"
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
    write_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_gate(
        source_root=tmp_path,
        out_root=tmp_path,
    )


def test_authorization_record_granted_for_scoped_pr(tmp_path: Path) -> None:
    _bootstrap(tmp_path)
    packet = build_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record(
        source_root=tmp_path
    )

    assert packet["authorization_record_id"] == RECORD_ID
    assert (
        packet["status"]
        == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_EXECUTION_AUTHORIZATION_RECORD_GRANTED_FOR_SCOPED_EXECUTION_PR"
    )
    assert packet["authorization_granted"] is True
    assert packet["execution_authority"] is True
    assert packet["execution_allowed"] is False
    assert packet["registry_mutation_performed"] is False
    assert packet["safe_to_prepare_execution_pr"] is True
    assert packet["recommended_next_lane"] == SCOPED_EXECUTION_RECEIPT_LANE


def test_authorization_record_is_deterministic(tmp_path: Path) -> None:
    _bootstrap(tmp_path)
    first = build_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record(
        source_root=tmp_path
    )
    second = build_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record(
        source_root=tmp_path
    )
    assert first["authorization_record_hash"] == second["authorization_record_hash"]


def test_authorization_record_preserves_scope_boundaries(tmp_path: Path) -> None:
    _bootstrap(tmp_path)
    packet = build_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record(
        source_root=tmp_path
    )

    for action in SCOPED_REPAIR_ACTIONS:
        assert action in packet["scoped_repair_actions"]
    for blocked_action in BLOCKED_ACTIONS:
        assert blocked_action in packet["blocked_actions"]
    assert packet["operator_authorization"]["p130_hold_preservation_acknowledged"] is True
    assert packet["operator_authorization"]["orphan_exclusion_policy_acknowledged"] is True


def test_writer_and_schema(tmp_path: Path) -> None:
    _bootstrap(tmp_path)
    packet = write_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record(
        source_root=tmp_path,
        out_root=tmp_path,
    )
    json_path = (
        tmp_path
        / "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record_001.latest.json"
    )
    assert json_path.exists()
    runner_packet = RUNNER.run(repo_root=tmp_path, out_root=tmp_path)
    assert runner_packet["authorization_record_hash"] == packet["authorization_record_hash"]
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_registry_includes_record_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
