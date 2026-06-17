from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt import (
    CHAIN_STEPS,
    RECEIPT_ID,
    build_abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt,
    render_abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt_markdown,
    write_abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt,
)
from core.generated_artifact_registry import build_generated_artifact_registry
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt.py",
    "local_abx_research_canary_registry_coverage_repair_chain_closure_receipt_runner",
)
SCHEMA_PATH = (
    "contracts/operator_review/"
    "abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt.v1.schema.json"
)


def test_chain_closure_receipt_is_deterministic_and_sealed() -> None:
    first = build_abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt(
        source_root=REPO_ROOT
    )
    second = build_abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt(
        source_root=REPO_ROOT
    )

    assert first["receipt_hash"] == second["receipt_hash"]
    assert first["artifact_id"] == RECEIPT_ID
    assert first["status"] == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_CHAIN_CLOSURE_RECEIPT_EMITTED"
    assert first["chain_closure_status"] == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_CHAIN_SEALED"
    assert first["closure_posture"] in {"SEALED", "SEALED_WITH_OBSERVED_BLOCKERS"}
    assert first["execution_allowed"] is False
    assert first["valid_for_execution"] is False
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert first["downstream_status"] == "NOT_COMPUTABLE"
    assert len(first["chain_step_records"]) == len(CHAIN_STEPS)
    assert all(record["step_ready"] for record in first["chain_step_records"])
    assert first["terminal_validation_summary"]["regeneration_receipt_ready"] is True
    assert first["terminal_validation_summary"]["scoped_execution_receipt_ready"] is True
    assert first["terminal_validation_summary"]["post_repair_audit_ready"] is True


def test_chain_closure_receipt_not_computable_when_terminal_missing(tmp_path: Path) -> None:
    packet = build_abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt(
        source_root=tmp_path
    )
    assert packet["chain_closure_status"] == "NOT_COMPUTABLE"
    assert packet["closure_posture"] == "NOT_COMPUTABLE"
    assert packet["status"] == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_CHAIN_CLOSURE_RECEIPT_BLOCKED"
    assert packet["blockers"]


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    packet = write_abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt(
        REPO_ROOT,
        out_root=tmp_path,
    )

    json_path = (
        tmp_path
        / "out/operator_review/"
        "abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt_001.latest.json"
    )
    md_path = (
        tmp_path
        / "out/operator_review/"
        "abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt_001.latest.md"
    )
    assert json_path.exists()
    assert md_path.exists()

    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_root=tmp_path)
    assert runner_packet["receipt_hash"] == packet["receipt_hash"]

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)
    markdown = render_abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt_markdown(
        packet
    )
    assert markdown[0] == (
        "# ABX Research Canary Artifact Registry Coverage Repair Chain Closure Receipt 001"
    )


def test_chain_closure_receipt_in_derived_optional_registry() -> None:
    registry = build_generated_artifact_registry(REPO_ROOT)
    emap = {entry.artifact_path: entry for entry in registry.entries}
    json_path = (
        "out/operator_review/"
        "abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt_001.latest.json"
    )
    md_path = (
        "out/operator_review/"
        "abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt_001.latest.md"
    )
    assert emap[json_path].determinism_class == "DERIVED_OPTIONAL"
    assert emap[md_path].determinism_class == "DERIVED_OPTIONAL"
