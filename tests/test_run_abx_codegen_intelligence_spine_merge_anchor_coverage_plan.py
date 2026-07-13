"""Tests for scripts/run_abx_codegen_intelligence_spine_merge_anchor_coverage_plan.py (candidate fd3c3a8ef35fc91a)"""

from unittest.mock import patch
from pathlib import Path
from scripts.run_abx_codegen_intelligence_spine_merge_anchor_coverage_plan import run

def test_run_returns_dict():
    mock_packet = {
        "plan_id": "ABX_CODEGEN_INTELLIGENCE_SPINE_MERGE_ANCHOR_COVERAGE_PLAN_001",
        "schema_version": "AbxCodegenIntelligenceSpineMergeAnchorCoveragePlan.v1",
        "anchors": []
    }
    with patch("scripts.run_abx_codegen_intelligence_spine_merge_anchor_coverage_plan.build_abx_codegen_intelligence_spine_merge_anchor_coverage_plan", return_value=mock_packet):
        with patch("scripts.run_abx_codegen_intelligence_spine_merge_anchor_coverage_plan.write_abx_codegen_intelligence_spine_merge_anchor_coverage_plan"):
            with patch("scripts.run_abx_codegen_intelligence_spine_merge_anchor_coverage_plan.write_abx_codegen_intelligence_spine_merge_anchor_coverage_plan_markdown"):
                result = run(repo_root=Path("/tmp"))
                assert isinstance(result, dict)

def test_run_calls_build():
    mock_packet = {
        "plan_id": "ABX_CODEGEN_INTELLIGENCE_SPINE_MERGE_ANCHOR_COVERAGE_PLAN_001",
        "schema_version": "AbxCodegenIntelligenceSpineMergeAnchorCoveragePlan.v1",
        "anchors": []
    }
    with patch("scripts.run_abx_codegen_intelligence_spine_merge_anchor_coverage_plan.build_abx_codegen_intelligence_spine_merge_anchor_coverage_plan", return_value=mock_packet) as mock_build:
        with patch("scripts.run_abx_codegen_intelligence_spine_merge_anchor_coverage_plan.write_abx_codegen_intelligence_spine_merge_anchor_coverage_plan"):
            with patch("scripts.run_abx_codegen_intelligence_spine_merge_anchor_coverage_plan.write_abx_codegen_intelligence_spine_merge_anchor_coverage_plan_markdown"):
                result = run(repo_root=Path("/tmp"))
                mock_build.assert_called_once()
                assert isinstance(result, dict)
