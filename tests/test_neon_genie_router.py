"""Tests for skills/abx-neon-genie/neon_genie_router.py (TEST candidate 2b3ec567a01a1362)"""

import sys
sys.path.insert(0, "skills/abx-neon-genie")
import neon_genie_router as r

def test_classify_mode():
    assert r.classify_mode({}) == "PROMPT_LED"
    assert r.classify_mode({"mode": "market_led"}) == "MARKET_LED"
    assert r.classify_mode({"mode": "trend_led"}) == "TREND_LED"

def test_require_evidence():
    assert r.require_evidence("MARKET_LED", {}) is True
    assert r.require_evidence("PROMPT_LED", {}) is False
    assert r.require_evidence("PROMPT_LED", {"require_evidence": True}) is True

def test_run_venture_cycle_basic():
    req = {"mode": "prompt_led"}
    result = r.run_venture_cycle(req)
    assert "schema_version" in result
    assert result["input_mode"] == "PROMPT_LED"
    assert "venture_packet" in result
    assert "route_decision" in result

def test_run_venture_cycle_with_evidence():
    req = {"mode": "market_led", "evidence_pack": {"status": "ACQUIRED"}}
    result = r.run_venture_cycle(req)
    assert result["evidence_status"] == "ACQUIRED"
    assert "overlap_classification" in result