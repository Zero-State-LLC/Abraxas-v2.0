from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_research_canary_artifact_registry_coverage_audit import (
    AUDIT_ID,
    BLOCKED_ACTIONS,
    REPAIR_SPEC_PLAN_LANE,
    build_abx_research_canary_artifact_registry_coverage_audit,
    render_abx_research_canary_artifact_registry_coverage_audit_markdown,
    write_abx_research_canary_artifact_registry_coverage_audit,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_research_canary_artifact_registry_coverage_audit.py",
    "local_abx_research_canary_artifact_registry_coverage_audit_runner",
)
SCHEMA_PATH = (
    "contracts/operator_review/abx_research_canary_artifact_registry_coverage_audit.v1.schema.json"
)


def _lane(packet: dict, lane_id: str) -> dict:
    return next(record for record in packet["lane_records"] if record["lane_id"] == lane_id)


def test_audit_is_deterministic() -> None:
    first = build_abx_research_canary_artifact_registry_coverage_audit(repo_root=REPO_ROOT)
    second = build_abx_research_canary_artifact_registry_coverage_audit(repo_root=REPO_ROOT)

    assert first["audit_hash"] == second["audit_hash"]
    assert first["audit_id"] == AUDIT_ID


def test_audit_is_advisory_and_performs_no_repairs() -> None:
    packet = build_abx_research_canary_artifact_registry_coverage_audit(repo_root=REPO_ROOT)

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


def test_audit_confirms_registry_coverage_gap() -> None:
    packet = build_abx_research_canary_artifact_registry_coverage_audit(repo_root=REPO_ROOT)

    assert packet["audit_status"] == "RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_GAP_CONFIRMED"
    assert packet["coverage_summary"]["canonical_lane_count"] == 28
    assert packet["coverage_summary"]["direct_registry_lane_id_coverage"] is False
    assert packet["coverage_summary"]["lane_id_gap_count"] == 28
    assert packet["coverage_summary"]["implemented_artifacts_present"] is True
    assert packet["coverage_summary"]["output_artifacts_present"] is True
    assert packet["coverage_summary"]["tests_present"] is True
    assert packet["coverage_summary"]["schemas_present"] is True
    assert packet["recommended_next_lane"] == REPAIR_SPEC_PLAN_LANE
    assert packet["downstream_status"] == "READY_FOR_REGISTRY_COVERAGE_REPAIR_SPEC_PLAN"


def test_lane_records_include_key_surfaces() -> None:
    packet = build_abx_research_canary_artifact_registry_coverage_audit(repo_root=REPO_ROOT)

    for lane_id in (
        "P103_RESEARCH_SHADOW_REPLAY_AUDIT",
        "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS",
        "P105_RESEARCH_PROMOTION_BLOCKER_LEDGER",
        "P130_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_REVIEW",
    ):
        record = _lane(packet, lane_id)
        assert record["core_module_observed"] is True
        assert record["runner_observed"] is True
        assert record["schema_observed"] is True
        assert record["test_observed"] is True
        assert record["output_json_observed"] is True
        assert record["registry_coverage_status"] == "GAP_CONFIRMED"
        assert record["lane_id_in_registry_source"] is False


def test_blocked_actions_preserved() -> None:
    packet = build_abx_research_canary_artifact_registry_coverage_audit(repo_root=REPO_ROOT)

    for blocked_action in BLOCKED_ACTIONS:
        assert blocked_action in packet["blocked_actions"]


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    packet = write_abx_research_canary_artifact_registry_coverage_audit(
        REPO_ROOT,
        out_root=tmp_path,
    )

    json_path = (
        tmp_path
        / "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_001.latest.json"
    )
    md_path = (
        tmp_path
        / "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_001.latest.md"
    )
    assert json_path.exists()
    assert md_path.exists()

    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_root=tmp_path)
    assert runner_packet["audit_hash"] == packet["audit_hash"]

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)
    markdown = render_abx_research_canary_artifact_registry_coverage_audit_markdown(packet)
    assert markdown[0] == "# ABX Research Canary Artifact Registry Coverage Audit 001"
    assert any("DIRECT_REGISTRY_REPAIR" in line for line in markdown)


def test_registry_includes_audit_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
