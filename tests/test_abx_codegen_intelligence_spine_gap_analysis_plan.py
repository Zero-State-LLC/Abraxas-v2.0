from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_gap_analysis_plan import (
    build_abx_codegen_intelligence_spine_gap_analysis_plan,
)
from core.canonical.json import canonical_hash
from scripts.codegen import run_abx_codegen_intelligence_spine_gap_analysis_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/abx_codegen_intelligence_spine_gap_analysis_plan.v1.schema.json"


def test_abx_codegen_intelligence_spine_gap_analysis_plan_is_advisory_only() -> None:
    packet = build_abx_codegen_intelligence_spine_gap_analysis_plan(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "AbxCodegenIntelligenceSpineGapAnalysisPlan.v1"
    assert packet["plan_status"] == "ABX_CODEGEN_INTELLIGENCE_SPINE_GAP_ANALYSIS_PLAN_READY"
    assert packet["target_surface"] == "ABX_CODEGEN_INTELLIGENCE_SPINE_001"
    assert packet["codegen_spine_implementation_performed"] is False
    assert packet["code_generation_allowed"] is False
    assert packet["code_mutation_allowed"] is False
    assert packet["file_writeback_allowed"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_abx_codegen_intelligence_spine_gap_analysis_plan_maps_controls() -> None:
    packet = build_abx_codegen_intelligence_spine_gap_analysis_plan(repo_root=REPO_ROOT)

    assert packet["notion_gap_evidence"]["implementation_status"] == "MISSING"
    assert packet["gap_summary"]["spine_missing_paths"] == packet["gap_summary"][
        "spine_required_paths"
    ]
    assert packet["generated_artifact_control_evidence"]["control_paths_observed"] == packet[
        "generated_artifact_control_evidence"
    ]["control_paths_total"]
    assert "code_generation" in packet["blocked_actions"]
    assert "code_mutation" in packet["blocked_actions"]


def test_abx_codegen_intelligence_spine_gap_analysis_plan_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_gap_analysis_plan(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_abx_codegen_intelligence_spine_gap_analysis_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path / "out/audit/abx_codegen_intelligence_spine_gap_analysis_plan_001.latest.json"
    )
    out_md = tmp_path / "out/audit/abx_codegen_intelligence_spine_gap_analysis_plan_001.latest.md"

    first = run_abx_codegen_intelligence_spine_gap_analysis_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_gap_analysis_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
    assert first_md.startswith("# ABX Codegen Intelligence Spine Gap Analysis Plan\n")
