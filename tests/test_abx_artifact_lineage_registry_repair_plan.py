from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_registry_repair_plan import (
    build_abx_artifact_lineage_registry_repair_plan,
    render_markdown,
    write_abx_artifact_lineage_registry_repair_plan,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_artifact_lineage_registry_repair_plan.py",
    "local_abx_artifact_lineage_registry_repair_plan_runner",
)


def test_plan_id_and_source_audit_are_exact() -> None:
    packet = build_abx_artifact_lineage_registry_repair_plan()
    assert packet["plan_id"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_REPAIR_PLAN_001"
    assert packet["source_traceability_audit"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_001"
    assert packet["source_traceability_audit_observed"] is True


def test_governance_locks_are_preserved() -> None:
    packet = build_abx_artifact_lineage_registry_repair_plan()
    locks = packet["governance_locks"]
    assert locks["governance_status"] == "FROZEN"
    assert locks["canon_status"] == "ADVISORY_ONLY"
    assert locks["execution_authority"] is False
    assert locks["canon_mutation_allowed"] is False
    assert locks["runtime_mutation_allowed"] is False
    assert locks["research_candidates_canonized"] is False
    assert packet["downstream"] == "NOT_COMPUTABLE"


def test_repair_batches_cover_direct_operator_and_external_modes() -> None:
    packet = build_abx_artifact_lineage_registry_repair_plan()
    modes = {batch["repair_mode"] for batch in packet["repair_batches"]}
    assert modes == {
        "REPO_LOCAL_DIRECT_REPAIR_CANDIDATE",
        "OPERATOR_REVIEW_REQUIRED",
        "EXTERNAL_EVIDENCE_REQUIRED",
    }


def test_required_batches_are_present() -> None:
    packet = build_abx_artifact_lineage_registry_repair_plan()
    batch_ids = {batch["batch_id"] for batch in packet["repair_batches"]}
    assert batch_ids == {
        "REGISTRY_COVERAGE_REPAIR_BATCH",
        "MARKDOWN_JSON_PAIRING_REPAIR_BATCH",
        "DOCS_ARTIFACT_REFERENCE_REPAIR_BATCH",
        "RUNNER_CASING_POLICY_REVIEW_BATCH",
        "NOTION_MAPPING_EVIDENCE_BATCH",
    }


def test_unresolved_items_remain_not_computable() -> None:
    packet = build_abx_artifact_lineage_registry_repair_plan()
    assert {item["status"] for item in packet["unresolved_items"]} == {"NOT_COMPUTABLE"}
    item_ids = {item["item_id"] for item in packet["unresolved_items"]}
    assert "RUNNER_CASING_POLICY_DECISION" not in item_ids
    assert "NOTION_SURFACE_COMPLETENESS_PROOF" not in item_ids
    assert packet["operator_review_batches"] == []
    assert packet["external_evidence_batches"] == []


def test_schema_and_markdown_validation_pass() -> None:
    packet = build_abx_artifact_lineage_registry_repair_plan()
    schema = json.loads(
        Path(
            "contracts/canon/abx_artifact_lineage_registry_repair_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_markdown(packet)
    assert "ABX_ARTIFACT_LINEAGE_REGISTRY_REPAIR_PLAN_001" in markdown
    assert "ABX_ARTIFACT_LINEAGE_REGISTRY_REPAIR_EXECUTION_PLAN_001" in markdown
    assert "NOT_COMPUTABLE" in markdown


def test_output_is_deterministic() -> None:
    first = build_abx_artifact_lineage_registry_repair_plan()
    second = build_abx_artifact_lineage_registry_repair_plan()
    assert first == second


def test_writer_and_runner_emit_outputs(tmp_path: Path) -> None:
    json_path = tmp_path / "out/sync/abx_artifact_lineage_registry_repair_plan/latest.json"
    md_path = tmp_path / "out/sync/abx_artifact_lineage_registry_repair_plan/latest.md"
    packet = write_abx_artifact_lineage_registry_repair_plan(json_path, md_path)
    assert json_path.exists()
    assert md_path.exists()
    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_json=json_path, out_md=md_path)
    assert runner_packet["packet_hash"] == packet["packet_hash"]
