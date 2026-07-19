"""Tests for scripts/temporal/run_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan.py (TEST candidate ff3d654f5a8aca6f)"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scripts.temporal.run_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan as s

def test_run_returns_packet(monkeypatch, tmp_path):
    fake_packet = {
        "p83_record_creation_record_plan_status": "COMPLETE",
        "p83_record_creation_record_required": False,
        "recommended_next_lane": "PROJECTION",
        "canonical_status": "VALID",
    }
    with patch("scripts.temporal.run_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan.build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan", return_value=fake_packet):
        with patch("scripts.temporal.run_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan.write_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan"):
            pkt = s.run(out_path=tmp_path / "out.json")
            assert pkt["p83_record_creation_record_plan_status"] == "COMPLETE"

def test_main_runs(monkeypatch, tmp_path):
    fake_packet = {
        "p83_record_creation_record_plan_status": "COMPLETE",
        "p83_record_creation_record_required": False,
        "recommended_next_lane": "PROJECTION",
        "canonical_status": "VALID",
    }
    with patch("scripts.temporal.run_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan.build_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan", return_value=fake_packet):
        with patch("scripts.temporal.run_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan.write_temporal_continuity_p83_regeneration_authorization_record_creation_record_plan"):
            ret = s.main()
            assert ret == 0
