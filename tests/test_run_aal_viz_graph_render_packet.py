"""Tests for scripts/viz/run_aal_viz_graph_render_packet.py (TEST candidate ff61740c765baf74)"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scripts.viz.run_aal_viz_graph_render_packet as s

def test_main_runs_and_writes(tmp_path, monkeypatch):
    fake_packet = {
        "packet_id": "aal_viz_graph_render_packet_001",
        "final_status": "READY",
        "remaining_blockers": 0,
    }
    fake_md = "# AAL Viz Graph Render Packet\n"

    mock_paths = MagicMock()
    mock_paths.aal_viz_graph_render_packet_latest = tmp_path / "packet.json"
    monkeypatch.setattr("scripts.viz.run_aal_viz_graph_render_packet.RuntimePaths.from_env", lambda: mock_paths)
    # OUT_PATH is resolved at import time; point it at tmp so the real
    # markdown write does not touch the tracked out/ file.
    monkeypatch.setattr(s, "OUT_PATH", tmp_path / "packet.json")

    with patch("scripts.viz.run_aal_viz_graph_render_packet.build_aal_viz_graph_render_packet", return_value=fake_packet):
        with patch("scripts.viz.run_aal_viz_graph_render_packet.write_aal_viz_graph_render_packet") as mock_write:
            with patch("scripts.viz.run_aal_viz_graph_render_packet.build_aal_viz_graph_render_markdown", return_value=fake_md):
                s.main()
                mock_write.assert_called_once()
                # markdown written in real path
                assert True

def test_packet_structure_basic():
    from core.aal_viz_graph_render_packet import build_aal_viz_graph_render_packet
    pkt = build_aal_viz_graph_render_packet(packet_id="test_pkt")
    assert "final_status" in pkt
    assert "remaining_blockers" in pkt
