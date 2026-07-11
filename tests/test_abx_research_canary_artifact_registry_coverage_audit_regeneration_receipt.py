from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt import (
    RECEIPT_ID,
    build_abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt,
    render_abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt_markdown,
    write_abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "scripts/run_abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt.py",
    "local_abx_research_canary_registry_coverage_audit_regeneration_receipt_runner",
)
SCHEMA_PATH = (
    "contracts/operator_review/"
    "abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt.v1.schema.json"
)


def test_regeneration_receipt_is_deterministic_and_bounded() -> None:
    first = build_abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt(
        source_root=REPO_ROOT
    )
    second = build_abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt(
        source_root=REPO_ROOT
    )

    assert first["receipt_hash"] == second["receipt_hash"]
    assert first["status"] == "RESEARCH_CANARY_REGISTRY_COVERAGE_AUDIT_REGENERATION_RECEIPT_EMITTED"
    assert first["audit_regeneration_performed"] is True
    assert first["execution_allowed"] is False
    assert first["valid_for_execution"] is False
    assert first["valid_for_repair"] is False
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert first["downstream_status"] == "COVERAGE_REPAIR_CHAIN_COMPLETE"
    assert first["pre_regeneration_audit"]["audit_status"] == (
        "RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_GAP_CONFIRMED"
    )
    assert first["post_regeneration_audit"]["lane_id_gap_count"] == 0
    assert first["post_regeneration_audit"]["output_path_gap_count"] == 0


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    packet = write_abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt(
        REPO_ROOT,
        out_root=tmp_path,
    )

    json_path = (
        tmp_path
        / "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt_001.latest.json"
    )
    md_path = (
        tmp_path
        / "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt_001.latest.md"
    )
    audit_json_path = (
        tmp_path / "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_001.latest.json"
    )
    assert json_path.exists()
    assert md_path.exists()
    assert audit_json_path.exists()

    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_root=tmp_path)
    assert runner_packet["receipt_hash"] == packet["receipt_hash"]

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)
    markdown = render_abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt_markdown(
        packet
    )
    assert markdown[0] == "# ABX Research Canary Artifact Registry Coverage Audit Regeneration Receipt 001"
    assert any("P130_ACTIVATION" in line for line in markdown)


def test_regenerated_audit_is_post_repair(tmp_path: Path) -> None:
    write_abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt(
        REPO_ROOT,
        out_root=tmp_path,
    )
    audit = json.loads(
        (
            tmp_path / "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_001.latest.json"
        ).read_text(encoding="utf-8")
    )
    assert audit["audit_status"] == "NOT_COMPUTABLE"
    assert audit["coverage_summary"]["direct_registry_lane_id_coverage"] is True
    assert audit["coverage_summary"]["lane_id_gap_count"] == 0
    assert audit["governance_boundaries"]["registry_repair_performed"] is True


def test_registry_includes_regeneration_receipt_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )


def test_receipt_id_constant() -> None:
    packet = build_abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt(
        source_root=REPO_ROOT
    )
    assert packet["artifact_id"] == RECEIPT_ID
