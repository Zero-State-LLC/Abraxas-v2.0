"""Tests for scripts/run_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan.py (TEST candidate 182435d757e3c0f0)"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scripts.run_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan as p

def test_run_builds_packet(tmp_path, monkeypatch):
    fake_packet = {
        "plan_id": "test-plan",
        "recommended_patch_sequence_precondition_plan_status": "READY",
        "recommended_next_lane": "lane"
    }
    with patch("scripts.run_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan.build_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan") as mock_build:
        mock_build.return_value = fake_packet
        with patch("scripts.run_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan.write_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan"):
            with patch("scripts.run_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan.write_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan_markdown"):
                result = p.run(repo_root=tmp_path)
                assert result["plan_id"] == "test-plan"

def test_main_prints(monkeypatch, capsys):
    with patch("scripts.run_abx_codegen_intelligence_spine_recommended_patch_sequence_precondition_plan.run") as mock_run:
        mock_run.return_value = {
            "plan_id": "pid",
            "recommended_patch_sequence_precondition_plan_status": "READY",
            "recommended_next_lane": "lane"
        }
        monkeypatch.setattr(sys, "argv", ["script"])
        ret = p.main()
        captured = capsys.readouterr()
        assert "pid" in captured.out
        assert ret == 0
