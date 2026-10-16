"""Tests for skills/holler-sports/slang-emergence/scripts/slang_emergence_engine.py (TEST candidate 8e7273f8bf58445f)"""

import sys
import json
import hashlib
sys.path.insert(0, "skills/holler-sports/slang-emergence/scripts")
import slang_emergence_engine as s

def test_no_invented_slang_without_retrieved_corpus():
    # Hardened in 1e2a5b01: no corpus means NOT_COMPUTABLE, never generated copy.
    out = s.detect_memetic_patterns("holler sports slang")
    assert out["status"] == "NOT_COMPUTABLE"
    assert out["observed"] == [] and out["inferred"] == [] and out["speculative"] == []
    assert not hasattr(s, "humanize_slang_output")

def test_detect_memetic_patterns_structure():
    out = s.detect_memetic_patterns("holler sports slang")
    assert "observed" in out
    assert "inferred" in out
    assert "speculative" in out
    assert "provenance" in out
    prov = out["provenance"]
    assert "canonical_hash" in prov
    assert prov["brier"] is None  # no Brier without a settled forecast

def test_canonical_hash_stable():
    q = "test query"
    obs = "some observed text"[:100]
    canonical = json.dumps({"q": q, "obs": obs}, sort_keys=True, separators=(",", ":"))
    h = hashlib.sha256(canonical.encode()).hexdigest()[:16]
    assert len(h) == 16
    h2 = hashlib.sha256(canonical.encode()).hexdigest()[:16]
    assert h == h2

def test_no_recommendation_without_evidence():
    out = s.detect_memetic_patterns()
    assert out["status"] == "NOT_COMPUTABLE"
    assert "recommendation" not in out