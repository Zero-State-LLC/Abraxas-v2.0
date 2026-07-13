"""Tests for scripts/run_notion_writeback_dry_run_plan.py (TEST candidate 16a554669212f6c6)"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scripts.run_notion_writeback_dry_run_plan as p

def test_run_builds_packet(tmp_path, monkeypatch):
    # Minimal dry run with full expected packet shape
    fake_packet = {
        "plan_id": "test-plan",
        "plan_status": "READY",
        "target_state": {"foo": "bar"},
        "recommended_next_lane": "lane"
    }
    with patch("scripts.run_notion_writeback_dry_run_plan.build_notion_writeback_dry_run_plan") as mock_build:
        mock_build.return_value = fake_packet
        with patch("scripts.run_notion_writeback_dry_run_plan.write_notion_writeback_dry_run_plan"):
            with patch("scripts.run_notion_writeback_dry_run_plan.write_notion_writeback_dry_run_plan_markdown"):
                result = p.run(repo_root=tmp_path, target_page_id="page1", target_label="label1")
                assert result["plan_id"] == "test-plan"

def test_main_prints_and_exits(monkeypatch, capsys):
    with patch("scripts.run_notion_writeback_dry_run_plan.run") as mock_run:
        mock_run.return_value = {"plan_id": "pid", "plan_status": "READY", "recommended_next_lane": "lane"}
        monkeypatch.setattr(sys, "argv", ["script", "--target-page-id", "p1"])
        ret = p.main()
        captured = capsys.readouterr()
        assert "pid" in captured.out
        assert ret == 0
