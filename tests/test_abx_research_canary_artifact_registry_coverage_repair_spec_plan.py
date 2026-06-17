from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_research_canary_artifact_registry_coverage_audit import (
    write_abx_research_canary_artifact_registry_coverage_audit,
)
from core.abx_research_canary_artifact_registry_coverage_repair_spec_plan import (
    BLOCKED_ACTIONS,
    OPERATOR_DECISION_REQUEST_LANE,
    SPEC_PLAN_ID,
    build_abx_research_canary_artifact_registry_coverage_repair_spec_plan,
    render_abx_research_canary_artifact_registry_coverage_repair_spec_plan_markdown,
    write_abx_research_canary_artifact_registry_coverage_repair_spec_plan,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_research_canary_artifact_registry_coverage_repair_spec_plan.py",
    "local_abx_research_canary_artifact_registry_coverage_repair_spec_plan_runner",
)
SCHEMA_PATH = (
    "contracts/operator_review/"
    "abx_research_canary_artifact_registry_coverage_repair_spec_plan.v1.schema.json"
)


def _batch(packet: dict, batch_id: str) -> dict:
    return next(batch for batch in packet["repair_batches"] if batch["batch_id"] == batch_id)


def test_spec_plan_is_deterministic() -> None:
    first = build_abx_research_canary_artifact_registry_coverage_repair_spec_plan(repo_root=REPO_ROOT)
    second = build_abx_research_canary_artifact_registry_coverage_repair_spec_plan(repo_root=REPO_ROOT)

    assert first["spec_plan_hash"] == second["spec_plan_hash"]
    assert first["spec_plan_id"] == SPEC_PLAN_ID


def test_spec_plan_is_advisory_and_performs_no_repairs() -> None:
    packet = build_abx_research_canary_artifact_registry_coverage_repair_spec_plan(repo_root=REPO_ROOT)

    assert packet["advisory_only"] is True
    assert packet["execution_allowed"] is False
    assert packet["repair_execution_performed"] is False
    assert packet["registry_mutation_performed"] is False
    assert packet["authority_granted"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["runtime_mutation_allowed"] is False
    assert packet["canon_mutation_allowed"] is False
    assert packet["scheduler_mutation_allowed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["governance_boundaries"]["registry_repair_performed"] is False
    assert packet["governance_boundaries"]["research_canary_spine_refresh_performed"] is False


def test_spec_plan_ready_on_real_repo() -> None:
    packet = build_abx_research_canary_artifact_registry_coverage_repair_spec_plan(repo_root=REPO_ROOT)

    assert packet["spec_plan_status"] == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_SPEC_PLAN_READY"
    assert packet["source_audit"]["source_audit_observed"] is True
    assert packet["recommended_next_lane"] == OPERATOR_DECISION_REQUEST_LANE
    assert packet["downstream_status"] == "READY_FOR_OPERATOR_DECISION_REQUEST"


def test_repair_batches_include_expected_gaps() -> None:
    packet = build_abx_research_canary_artifact_registry_coverage_repair_spec_plan(repo_root=REPO_ROOT)

    output_batch = _batch(packet, "CANONICAL_LANE_OUTPUT_PATH_REGISTRY_BATCH")
    assert output_batch["batch_status"] == "ACTIVE"
    assert output_batch["impacted_count"] >= 26

    lane_id_batch = _batch(packet, "LANE_ID_TRACEABILITY_METADATA_BATCH")
    assert lane_id_batch["batch_status"] == "ACTIVE"
    assert lane_id_batch["impacted_count"] == 28

    orphan_batch = _batch(packet, "ORPHAN_RESEARCH_OUTPUT_POLICY_BATCH")
    assert orphan_batch["batch_status"] == "ACTIVE"
    assert orphan_batch["impacted_count"] == 10


def test_blocked_actions_preserved() -> None:
    packet = build_abx_research_canary_artifact_registry_coverage_repair_spec_plan(repo_root=REPO_ROOT)

    for blocked_action in BLOCKED_ACTIONS:
        assert blocked_action in packet["blocked_actions"]


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    write_abx_research_canary_artifact_registry_coverage_audit(
        REPO_ROOT,
        out_root=tmp_path,
    )
    packet = write_abx_research_canary_artifact_registry_coverage_repair_spec_plan(
        source_root=REPO_ROOT,
        out_root=tmp_path,
    )

    json_path = (
        tmp_path
        / "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_spec_plan_001.latest.json"
    )
    md_path = (
        tmp_path
        / "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_spec_plan_001.latest.md"
    )
    assert json_path.exists()
    assert md_path.exists()

    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_root=tmp_path)
    assert runner_packet["spec_plan_hash"] == packet["spec_plan_hash"]

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)
    markdown = render_abx_research_canary_artifact_registry_coverage_repair_spec_plan_markdown(packet)
    assert markdown[0] == "# ABX Research Canary Artifact Registry Coverage Repair Spec Plan 001"
    assert any("DIRECT_REGISTRY_REPAIR" in line for line in markdown)


def test_registry_includes_spec_plan_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_spec_plan_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_spec_plan_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
