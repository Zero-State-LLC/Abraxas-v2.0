from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_registry_direct_repair_implementation_plan import (
    build_abx_artifact_lineage_registry_direct_repair_implementation_plan,
    render_markdown,
    write_abx_artifact_lineage_registry_direct_repair_implementation_plan,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "scripts/run_abx_artifact_lineage_registry_direct_repair_implementation_plan.py",
    "local_abx_artifact_lineage_registry_direct_repair_implementation_plan_runner",
)


def test_plan_id_and_sources_are_exact() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_implementation_plan()
    assert packet["plan_id"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_IMPLEMENTATION_PLAN_001"
    assert packet["source_batch"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_BATCH_001"
    assert packet["source_execution_plan"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_REPAIR_EXECUTION_PLAN_001"
    assert packet["source_batch_observed"] is True
    assert packet["source_execution_plan_observed"] is True


def test_governance_locks_are_preserved() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_implementation_plan()
    locks = packet["governance_locks"]
    assert locks["governance_status"] == "FROZEN"
    assert locks["canon_status"] == "ADVISORY_ONLY"
    assert locks["execution_authority"] is False
    assert locks["canon_mutation_allowed"] is False
    assert locks["runtime_mutation_allowed"] is False
    assert locks["research_candidates_canonized"] is False
    assert packet["downstream"] == "NOT_COMPUTABLE"


def test_implementation_phases_cover_three_workstreams() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_implementation_plan()
    workstream_ids = {item["source_workstream_id"] for item in packet["implementation_phases"]}
    assert workstream_ids == {
        "DIRECT_REGISTRY_COVERAGE_CLASSIFICATION",
        "DIRECT_OUTPUT_PAIRING_CLASSIFICATION",
        "DIRECT_DOCS_REFERENCE_CLASSIFICATION",
    }
    assert packet["impacted_count_total"] == 0


def test_ready_and_blocked_phase_ids_are_stable() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_implementation_plan()
    assert packet["ready_phase_ids"] == ["DIRECT-IMPL-001", "DIRECT-IMPL-002", "DIRECT-IMPL-003"]
    assert packet["blocked_phase_ids"] == ["DIRECT-IMPL-CLOSURE"]


def test_unresolved_items_remain_not_computable() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_implementation_plan()
    assert {item["status"] for item in packet["unresolved_items"]} == {"NOT_COMPUTABLE"}


def test_schema_and_markdown_validation_pass() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_implementation_plan()
    schema = json.loads(
        Path(
            "contracts/canon/abx_artifact_lineage_registry_direct_repair_implementation_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_markdown(packet)
    assert "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_IMPLEMENTATION_PLAN_001" in markdown
    assert "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_IMPLEMENTATION_DRY_RUN_001" in markdown
    assert "NOT_COMPUTABLE" in markdown


def test_output_is_deterministic() -> None:
    first = build_abx_artifact_lineage_registry_direct_repair_implementation_plan()
    second = build_abx_artifact_lineage_registry_direct_repair_implementation_plan()
    assert first == second


def test_writer_and_runner_emit_outputs(tmp_path: Path) -> None:
    json_path = tmp_path / "out/sync/abx_artifact_lineage_registry_direct_repair_implementation_plan/latest.json"
    md_path = tmp_path / "out/sync/abx_artifact_lineage_registry_direct_repair_implementation_plan/latest.md"
    packet = write_abx_artifact_lineage_registry_direct_repair_implementation_plan(json_path, md_path)
    assert json_path.exists()
    assert md_path.exists()
    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_json=json_path, out_md=md_path)
    assert runner_packet["packet_hash"] == packet["packet_hash"]
