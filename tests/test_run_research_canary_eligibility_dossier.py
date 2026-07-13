"""Tests for scripts/run_research_canary_eligibility_dossier.py (TEST candidate 180122a071a6805f)"""

import sys
import argparse
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scripts.run_research_canary_eligibility_dossier as s

def test_parse_args_defaults():
    args = s._parse_args([])
    assert args.p105_path == "out/research_promotion_blocker_ledger/latest.json"

def test_load_json_packet_missing(tmp_path):
    p = tmp_path / "missing.json"
    assert s._load_json_packet(p) is None

def test_load_json_packet_valid(tmp_path):
    p = tmp_path / "pkt.json"
    p.write_text('{"a": 1}')
    assert s._load_json_packet(p) == {"a": 1}

def test_main_runs(monkeypatch):
    full_packet = {
        "dossier_id": "d1",
        "status": "READY",
        "plan_status": "READY",
        "recommended_next_lane": "lane",
        "canary_eligibility_dossier_status": "READY"
    }
    with patch("scripts.run_research_canary_eligibility_dossier.build_research_canary_eligibility_dossier") as mock_build:
        mock_build.return_value = full_packet
        with patch("scripts.run_research_canary_eligibility_dossier.write_research_canary_eligibility_dossier"):
            with patch("scripts.common.runner.print_packet_fields"):
                with patch("scripts.common.runner.run_packet_and_write"):
                    monkeypatch.setattr(sys, "argv", ["script"])
                    ret = s.main()
                    assert ret == 0
