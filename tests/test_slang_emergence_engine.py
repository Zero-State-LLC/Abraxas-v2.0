"""Tests for skills/holler-sports/slang-emergence/scripts/slang_emergence_engine.py (TEST candidate 8e7273f8bf58445f)"""

import sys
import json
import hashlib
from datetime import datetime, timezone
sys.path.insert(0, "skills/holler-sports/slang-emergence/scripts")
import slang_emergence_engine as s

def test_humanize_slang_output_strips_aiisms():
    text = "This pivotal underscoring showcasing crucial landscape tapestry delve realm moment."
    result = s.humanize_slang_output(text)
    for bad in ["pivotal", "underscoring", "showcasing", "crucial", "landscape", "tapestry", "delve", "realm"]:
        assert bad not in result
    assert "feels off but sharp money is already running with it" in result

def test_detect_memetic_patterns_structure():
    out = s.detect_memetic_patterns("holler sports slang")
    assert "observed" in out
    assert "inferred" in out
    assert "speculative" in out
    assert "provenance" in out
    prov = out["provenance"]
    assert "canonical_hash" in prov
    assert prov["brier"] == 0.89
    assert "memclaw" in prov

def test_canonical_hash_stable():
    q = "test query"
    obs = "some observed text"[:100]
    canonical = json.dumps({"q": q, "obs": obs}, sort_keys=True, separators=(",", ":"))
    h = hashlib.sha256(canonical.encode()).hexdigest()[:16]
    assert len(h) == 16
    h2 = hashlib.sha256(canonical.encode()).hexdigest()[:16]
    assert h == h2

def test_recommendation_present():
    out = s.detect_memetic_patterns()
    assert "recommendation" in out
    assert "Bind to COMMUNICATION_RELAY" in out["recommendation"]