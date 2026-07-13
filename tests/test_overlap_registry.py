"""Tests for skills/abx-neon-genie/overlap_registry.py (TEST candidate c57618e856e347a4)"""

import sys
sys.path.insert(0, "skills/abx-neon-genie")
import overlap_registry as o

def test_classify_overlap_empty():
    res = o.classify_overlap([])
    assert res["classification"] == "NOT_COMPUTABLE"

def test_classify_overlap_forecast():
    res = o.classify_overlap([{"desc": "forecast predict model"}])
    assert res["classification"] == "DUPLICATE"
    assert "Abraxas" in res["recommended_route"]

def test_classify_overlap_dream():
    res = o.classify_overlap([{"desc": "dream symbolic motif"}])
    assert res["classification"] == "ADJACENT"

def test_classify_overlap_virality():
    res = o.classify_overlap([{"desc": "level 99 virality"}])
    assert res["classification"] == "WRAPPER_CANDIDATE"

def test_classify_overlap_novel():
    res = o.classify_overlap([{"desc": "completely new thing"}])
    assert res["classification"] == "NOVEL"
    assert "NeonGenie" in res["recommended_route"]