from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_research_canary_artifact_registry_coverage_repair_operator_decision_request import (
    write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_request,
)
from core.abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt import (
    OPERATOR_DECISION_RECORD_PLAN_LANE,
    RECEIPT_ID,
    build_abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt,
    render_abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt_markdown,
    write_abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt,
)
from tests.conftest import bootstrap_pre_repair_phase_receipt_chain
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt.py",
    "local_abx_research_canary_registry_repair_phase_execution_receipt_runner",
)
SCHEMA_PATH = (
    "contracts/operator_review/"
    "abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt.v1.schema.json"
)


def _phase(packet: dict, phase_id: str) -> dict:
    return next(phase for phase in packet["phase_results"] if phase["phase_id"] == phase_id)


def test_receipt_is_deterministic(tmp_path: Path) -> None:
    bootstrap_pre_repair_phase_receipt_chain(tmp_path)
    first = build_abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt(
        source_root=tmp_path
    )
    second = build_abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt(
        source_root=tmp_path
    )

    assert first["receipt_hash"] == second["receipt_hash"]
    assert first["receipt_id"] == RECEIPT_ID


def test_receipt_completes_all_five_phases(tmp_path: Path) -> None:
    bootstrap_pre_repair_phase_receipt_chain(tmp_path)
    packet = build_abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt(
        source_root=tmp_path
    )

    assert packet["receipt_status"] == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_PHASE_EXECUTION_RECEIPT_EMITTED"
    assert packet["phases_complete"] is True
    assert packet["phase_count"] == 5
    assert packet["expected_phase_count"] == 5
    assert packet["recommended_next_lane"] == OPERATOR_DECISION_RECORD_PLAN_LANE


def test_phase_results_include_expected_classifications(tmp_path: Path) -> None:
    bootstrap_pre_repair_phase_receipt_chain(tmp_path)
    packet = build_abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt(
        source_root=tmp_path
    )

    phase_001 = _phase(packet, "REPAIR_SPEC_PHASE_001")
    assert phase_001["phase_status"] == "CLASSIFICATION_COMPLETE"
    assert phase_001["gap_count"] >= 26

    phase_002 = _phase(packet, "REPAIR_SPEC_PHASE_002")
    assert phase_002["phase_status"] == "CLASSIFICATION_COMPLETE"
    assert phase_002["gap_count"] == 28

    phase_003 = _phase(packet, "REPAIR_SPEC_PHASE_003")
    assert phase_003["phase_status"] == "OPERATOR_REVIEW_REQUIRED"

    phase_004 = _phase(packet, "REPAIR_SPEC_PHASE_004")
    assert phase_004["phase_status"] == "EXCLUSION_POLICY_EMITTED"
    assert phase_004["gap_count"] == 10

    phase_005 = _phase(packet, "REPAIR_SPEC_PHASE_005")
    assert phase_005["phase_status"] == "GATE_EMITTED"
    assert phase_005["authorization_granted"] is False


def test_receipt_performs_no_registry_repair(tmp_path: Path) -> None:
    bootstrap_pre_repair_phase_receipt_chain(tmp_path)
    packet = build_abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt(
        source_root=tmp_path
    )

    assert packet["registry_mutation_performed"] is False
    assert packet["repair_execution_performed"] is False
    assert packet["governance_boundaries"]["registry_repair_performed"] is False
    assert packet["governance_boundaries"]["research_canary_spine_refresh_performed"] is False


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    bootstrap_pre_repair_phase_receipt_chain(tmp_path)
    packet = write_abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt(
        source_root=tmp_path,
        out_root=tmp_path,
    )

    json_path = (
        tmp_path
        / "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt_001.latest.json"
    )
    md_path = (
        tmp_path
        / "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt_001.latest.md"
    )
    assert json_path.exists()
    assert md_path.exists()

    runner_packet = RUNNER.run(repo_root=tmp_path, out_root=tmp_path)
    assert runner_packet["receipt_hash"] == packet["receipt_hash"]

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)
    markdown = render_abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt_markdown(
        packet
    )
    assert markdown[0].startswith("# ABX Research Canary")
    assert any("REPAIR_SPEC_PHASE_005" in line for line in markdown)


def test_registry_includes_phase_execution_receipt_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
