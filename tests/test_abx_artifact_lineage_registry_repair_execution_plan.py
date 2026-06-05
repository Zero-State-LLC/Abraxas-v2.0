from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_registry_repair_execution_plan import (
    build_abx_artifact_lineage_registry_repair_execution_plan,
    render_markdown,
    write_abx_artifact_lineage_registry_repair_execution_plan,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_artifact_lineage_registry_repair_execution_plan.py",
    "local_abx_artifact_lineage_registry_repair_execution_plan_runner",
)


def test_plan_id_and_source_plan_are_exact() -> None:
    packet = build_abx_artifact_lineage_registry_repair_execution_plan()
    assert packet["plan_id"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_REPAIR_EXECUTION_PLAN_001"
    assert packet["source_repair_plan"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_REPAIR_PLAN_001"
    assert packet["source_repair_plan_observed"] is True


def test_governance_locks_are_preserved() -> None:
    packet = build_abx_artifact_lineage_registry_repair_execution_plan()
    locks = packet["governance_locks"]
    assert locks["governance_status"] == "FROZEN"
    assert locks["canon_status"] == "ADVISORY_ONLY"
    assert locks["execution_authority"] is False
    assert locks["canon_mutation_allowed"] is False
    assert locks["runtime_mutation_allowed"] is False
    assert locks["research_candidates_canonized"] is False
    assert packet["downstream"] == "NOT_COMPUTABLE"


def test_execution_batches_cover_ready_and_blocked_modes() -> None:
    packet = build_abx_artifact_lineage_registry_repair_execution_plan()
    statuses = {batch["batch_status"] for batch in packet["execution_batches"]}
    assert statuses == {"PLANNED", "NOT_COMPUTABLE"}
    assert packet["ready_batches"] == ["DIRECT_REPAIR_BATCH_001"]
    assert set(packet["blocked_batches"]) == {
        "RUNNER_POLICY_HOLD_BATCH_001",
        "NOTION_EVIDENCE_HOLD_BATCH_001",
    }


def test_execution_sequence_is_ordered_and_bounded() -> None:
    packet = build_abx_artifact_lineage_registry_repair_execution_plan()
    sequence = packet["execution_sequence"]
    assert [step["step_id"] for step in sequence] == [
        "SEQ_001_DIRECT_REPAIR_CLASSIFICATION",
        "SEQ_002_RUNNER_POLICY_REVIEW",
        "SEQ_003_NOTION_MAPPING_EVIDENCE",
    ]


def test_unresolved_items_remain_not_computable() -> None:
    packet = build_abx_artifact_lineage_registry_repair_execution_plan()
    assert {item["status"] for item in packet["unresolved_items"]} == {"NOT_COMPUTABLE"}


def test_schema_and_markdown_validation_pass() -> None:
    packet = build_abx_artifact_lineage_registry_repair_execution_plan()
    schema = json.loads(
        Path(
            "contracts/canon/abx_artifact_lineage_registry_repair_execution_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_markdown(packet)
    assert "ABX_ARTIFACT_LINEAGE_REGISTRY_REPAIR_EXECUTION_PLAN_001" in markdown
    assert "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_BATCH_001" in markdown
    assert "NOT_COMPUTABLE" in markdown


def test_output_is_deterministic() -> None:
    first = build_abx_artifact_lineage_registry_repair_execution_plan()
    second = build_abx_artifact_lineage_registry_repair_execution_plan()
    assert first == second


def test_writer_and_runner_emit_outputs(tmp_path: Path) -> None:
    json_path = tmp_path / "out/sync/abx_artifact_lineage_registry_repair_execution_plan/latest.json"
    md_path = tmp_path / "out/sync/abx_artifact_lineage_registry_repair_execution_plan/latest.md"
    packet = write_abx_artifact_lineage_registry_repair_execution_plan(json_path, md_path)
    assert json_path.exists()
    assert md_path.exists()
    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_json=json_path, out_md=md_path)
    assert runner_packet["packet_hash"] == packet["packet_hash"]
