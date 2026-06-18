from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_direct_repair_frontier_revalidation import (
    ARTIFACT_LINEAGE_DIRECT_REPAIR_CHAIN_COMPLETE,
    BLOCKED_ACTIONS,
    REVALIDATION_ID,
    TRACEABILITY_AUDIT_REGENERATION,
    build_abx_artifact_lineage_direct_repair_frontier_revalidation,
    render_abx_artifact_lineage_direct_repair_frontier_revalidation_markdown,
    write_abx_artifact_lineage_direct_repair_frontier_revalidation,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_artifact_lineage_direct_repair_frontier_revalidation.py",
    "local_abx_artifact_lineage_direct_repair_frontier_revalidation_runner",
)
SCHEMA_PATH = (
    "contracts/operator_review/abx_artifact_lineage_direct_repair_frontier_revalidation.v1.schema.json"
)


def _check(packet: dict, check_id: str) -> dict:
    return next(item for item in packet["frontier_checks"] if item["check_id"] == check_id)


def test_revalidation_is_deterministic() -> None:
    first = build_abx_artifact_lineage_direct_repair_frontier_revalidation(repo_root=REPO_ROOT)
    second = build_abx_artifact_lineage_direct_repair_frontier_revalidation(repo_root=REPO_ROOT)

    assert first["revalidation_hash"] == second["revalidation_hash"]
    assert first["revalidation_id"] == REVALIDATION_ID


def test_revalidation_is_advisory_and_performs_no_repairs() -> None:
    packet = build_abx_artifact_lineage_direct_repair_frontier_revalidation(repo_root=REPO_ROOT)

    assert packet["advisory_only"] is True
    assert packet["execution_allowed"] is False
    assert packet["repair_execution_performed"] is False
    assert packet["authority_granted"] is False
    assert packet["authorization_granted"] is False
    assert packet["approval_granted"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["runtime_mutation_allowed"] is False
    assert packet["canon_mutation_allowed"] is False
    assert packet["scheduler_mutation_allowed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_repair"] is False
    assert packet["research_canary_guardrail"]["do_not_regenerate_research_canary_artifacts"] is True


def test_frontier_checks_cover_required_surface() -> None:
    packet = build_abx_artifact_lineage_direct_repair_frontier_revalidation(repo_root=REPO_ROOT)

    assert packet["frontier_check_count"] >= 8
    check_ids = {item["check_id"] for item in packet["frontier_checks"]}
    assert {
        "latest_merged_anchor",
        "active_open_pr_stack",
        "latest_artifact_lineage_direct_repair_surface",
        "direct_repair_execution_spec_exists",
        "belief_graph_codegen_planning_status",
        "track_classification_p102g_p103_p130_phase15_pr679",
        "recommended_next_lane_eligibility",
        "authority_denials_preserved",
    }.issubset(check_ids)
    assert _check(packet, "latest_merged_anchor")["check_status"] == "PASS"
    assert _check(packet, "direct_repair_execution_spec_exists")["check_status"] == "PASS"


def test_recommended_next_lane_reflects_traceability_regeneration_complete() -> None:
    packet = build_abx_artifact_lineage_direct_repair_frontier_revalidation(repo_root=REPO_ROOT)

    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["downstream_status"] == ARTIFACT_LINEAGE_DIRECT_REPAIR_CHAIN_COMPLETE
    assert packet["traceability_regeneration_receipt"]["regeneration_complete"] is True
    assert _check(packet, "recommended_next_lane_eligibility")["check_status"] == "PASS"
    assert (
        _check(packet, "recommended_next_lane_eligibility")["observed_summary"]
        == ARTIFACT_LINEAGE_DIRECT_REPAIR_CHAIN_COMPLETE
    )


def test_track_classifications_include_historical_parallel_and_active() -> None:
    packet = build_abx_artifact_lineage_direct_repair_frontier_revalidation(repo_root=REPO_ROOT)
    by_id = {item["track_id"]: item["classification"] for item in packet["track_classifications"]}

    assert by_id["p102g_pr429_era"] == "historical"
    assert by_id["p103_p130_research_canary"] == "parallel"
    assert by_id["phase15_pr679_v2_operator_sync"] == "parallel"
    assert by_id["artifact_lineage_direct_repair"] == "sealed"
    assert by_id["belief_graph_codegen_planning"] == "active"


def test_blocked_actions_preserved() -> None:
    packet = build_abx_artifact_lineage_direct_repair_frontier_revalidation(repo_root=REPO_ROOT)

    for blocked_action in BLOCKED_ACTIONS:
        assert blocked_action in packet["blocked_actions"]


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    packet = write_abx_artifact_lineage_direct_repair_frontier_revalidation(
        REPO_ROOT,
        out_root=tmp_path,
    )

    json_path = (
        tmp_path
        / "out/operator_review/abx_artifact_lineage_direct_repair_frontier_revalidation_001.latest.json"
    )
    md_path = (
        tmp_path
        / "out/operator_review/abx_artifact_lineage_direct_repair_frontier_revalidation_001.latest.md"
    )
    assert json_path.exists()
    assert md_path.exists()

    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_root=tmp_path)
    assert runner_packet["revalidation_hash"] == packet["revalidation_hash"]

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)
    markdown = render_abx_artifact_lineage_direct_repair_frontier_revalidation_markdown(packet)
    assert markdown[0] == "# ABX Artifact Lineage Direct Repair Frontier Revalidation 001"
    assert any("DIRECT_REGISTRY_REPAIR_EXECUTION" in line for line in markdown)


def test_registry_includes_revalidation_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/abx_artifact_lineage_direct_repair_frontier_revalidation_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/operator_review/abx_artifact_lineage_direct_repair_frontier_revalidation_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
