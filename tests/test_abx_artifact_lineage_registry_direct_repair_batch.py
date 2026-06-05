from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_registry_direct_repair_batch import (
    build_abx_artifact_lineage_registry_direct_repair_batch,
    render_markdown,
    write_abx_artifact_lineage_registry_direct_repair_batch,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_artifact_lineage_registry_direct_repair_batch.py",
    "local_abx_artifact_lineage_registry_direct_repair_batch_runner",
)


def test_batch_id_and_sources_are_exact() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_batch()
    assert packet["batch_id"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_BATCH_001"
    assert packet["source_execution_plan"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_REPAIR_EXECUTION_PLAN_001"
    assert packet["source_traceability_audit"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_001"
    assert packet["source_execution_plan_observed"] is True
    assert packet["direct_batch_ready"] is True


def test_governance_locks_are_preserved() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_batch()
    locks = packet["governance_locks"]
    assert locks["governance_status"] == "FROZEN"
    assert locks["canon_status"] == "ADVISORY_ONLY"
    assert locks["execution_authority"] is False
    assert locks["canon_mutation_allowed"] is False
    assert locks["runtime_mutation_allowed"] is False
    assert locks["research_candidates_canonized"] is False
    assert packet["downstream"] == "NOT_COMPUTABLE"


def test_workstreams_cover_three_direct_repair_scopes() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_batch()
    workstream_ids = {item["workstream_id"] for item in packet["workstreams"]}
    assert workstream_ids == {
        "DIRECT_REGISTRY_COVERAGE_CLASSIFICATION",
        "DIRECT_OUTPUT_PAIRING_CLASSIFICATION",
        "DIRECT_DOCS_REFERENCE_CLASSIFICATION",
    }


def test_classification_ledger_entries_are_present() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_batch()
    ledger_ids = {item["ledger_entry_id"] for item in packet["classification_ledger"]}
    assert ledger_ids == {
        "REGISTRY_DRIFT_LEDGER",
        "PAIRING_DRIFT_LEDGER",
        "DOCS_DRIFT_LEDGER",
    }


def test_unresolved_items_remain_not_computable() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_batch()
    assert {item["status"] for item in packet["unresolved_items"]} == {"NOT_COMPUTABLE"}


def test_schema_and_markdown_validation_pass() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_batch()
    schema = json.loads(
        Path(
            "contracts/canon/abx_artifact_lineage_registry_direct_repair_batch.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_markdown(packet)
    assert "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_BATCH_001" in markdown
    assert "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_IMPLEMENTATION_PLAN_001" in markdown
    assert "NOT_COMPUTABLE" in markdown


def test_output_is_deterministic() -> None:
    first = build_abx_artifact_lineage_registry_direct_repair_batch()
    second = build_abx_artifact_lineage_registry_direct_repair_batch()
    assert first == second


def test_writer_and_runner_emit_outputs(tmp_path: Path) -> None:
    json_path = tmp_path / "out/sync/abx_artifact_lineage_registry_direct_repair_batch/latest.json"
    md_path = tmp_path / "out/sync/abx_artifact_lineage_registry_direct_repair_batch/latest.md"
    packet = write_abx_artifact_lineage_registry_direct_repair_batch(json_path, md_path)
    assert json_path.exists()
    assert md_path.exists()
    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_json=json_path, out_md=md_path)
    assert runner_packet["packet_hash"] == packet["packet_hash"]
