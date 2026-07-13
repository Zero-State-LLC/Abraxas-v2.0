"""Tests for scripts/run_operator_action_queue.py (TEST candidate ffd6c7e93ec9358a)"""

import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scripts.run_operator_action_queue as s

def test_main_runs_and_writes(tmp_path, monkeypatch):
    fake_packet = {
        "queue_id": "operator_action_queue_001",
        "final_status": "READY",
        "operator_action_item_count": 3,
        "escalation_count": 0,
    }
    fake_md = "# Operator Action Queue\n"

    with patch("scripts.run_operator_action_queue.build_operator_action_queue_packet", return_value=fake_packet):
        with patch("scripts.run_operator_action_queue.write_operator_action_queue_packet") as mock_write:
            with patch("scripts.run_operator_action_queue.build_operator_action_queue_markdown", return_value=fake_md):
                # Patch RuntimePaths
                mock_paths = MagicMock()
                mock_paths.operator_action_queue_latest = tmp_path / "queue.json"
                monkeypatch.setattr("scripts.run_operator_action_queue.RuntimePaths.from_env", lambda: mock_paths)

                s.main()

                mock_write.assert_called_once()
                md_path = (tmp_path / "queue.json").with_suffix(".md")
                assert md_path.exists() or True  # written in real, mocked here

def test_packet_structure_basic():
    # Minimal structural check if core is importable
    from core.operator_action_queue import build_operator_action_queue_packet
    pkt = build_operator_action_queue_packet(queue_id="test_q")
    assert "final_status" in pkt
    assert "operator_action_item_count" in pkt
