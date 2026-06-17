from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_research_canary_artifact_registry_coverage_repair_execution_authorization_gate import (
    write_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_gate,
)
from core.abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record import (
    write_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record,
)
from core.abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt import (
    RECEIPT_ID,
    build_abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt,
    render_abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt_markdown,
    write_abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt,
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
    "Scripts/run_abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt.py",
    "local_abx_research_canary_registry_repair_scoped_execution_receipt_runner",
)
SCHEMA_PATH = (
    "contracts/operator_review/"
    "abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt.v1.schema.json"
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
    write_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record(
        source_root=tmp_path,
        out_root=tmp_path,
    )


def test_scoped_execution_receipt_is_deterministic_and_bounded() -> None:
    first = build_abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt(
        source_root=REPO_ROOT
    )
    second = build_abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt(
        source_root=REPO_ROOT
    )

    assert first["receipt_hash"] == second["receipt_hash"]
    assert first["status"] == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_SCOPED_EXECUTION_RECEIPT_EMITTED"
    assert first["repair_execution_performed"] is True
    assert first["registry_mutation_performed"] is True
    assert first["execution_authority"] is True
    assert first["execution_allowed"] is False
    assert first["valid_for_execution"] is False
    assert first["valid_for_repair"] is False
    assert first["derived_optional_registry_repair"]["repaired_count"] == 28
    assert first["lane_id_traceability_repair"]["repaired_count"] == 28
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert first["downstream_status"] == "COVERAGE_AUDIT_REGENERATION_OBSERVED"


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    _bootstrap(tmp_path)
    packet = write_abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt(
        REPO_ROOT,
        out_root=tmp_path,
    )

    json_path = (
        tmp_path
        / "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt_001.latest.json"
    )
    md_path = (
        tmp_path
        / "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt_001.latest.md"
    )
    assert json_path.exists()
    assert md_path.exists()

    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_root=tmp_path)
    assert runner_packet["receipt_hash"] == packet["receipt_hash"]

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)
    markdown = render_abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt_markdown(
        packet
    )
    assert markdown[0] == "# ABX Research Canary Artifact Registry Coverage Repair Scoped Execution Receipt 001"
    assert any("P130_ACTIVATION" in line for line in markdown)


def test_registry_includes_scoped_receipt_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )


def test_registry_includes_canonical_research_output_paths() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/research_shadow_replay_audit/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS
    assert (
        "out/research_canary_final_activation_authorization_review/latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )


def test_receipt_id_constant() -> None:
    packet = build_abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt(
        source_root=REPO_ROOT
    )
    assert packet["artifact_id"] == RECEIPT_ID
