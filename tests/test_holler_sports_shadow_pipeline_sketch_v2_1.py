"""Tests for out/audit/holler_sports_shadow_pipeline_sketch_v2.1.py (TEST candidate 02d9200a70bb3f92)"""

import importlib.util
from pathlib import Path

sketch_path = Path("out/audit/holler_sports_shadow_pipeline_sketch_v2.1.py")
spec = importlib.util.spec_from_file_location("shadow_sketch", sketch_path)
sketch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sketch)

def test_canonical_hash_deterministic():
    data = {"events": ["g1"], "runes": ["R1"]}
    h1 = sketch.canonical_hash(data)
    h2 = sketch.canonical_hash(data)
    assert h1 == h2
    assert len(h1) == 16

def test_simulate_rune_bound_ingest():
    data = {"events": ["g1", "g2"]}
    res = sketch.simulate_rune_bound_ingest("RUNE.TEST", data)
    assert res["rune_id"] == "RUNE.TEST"
    assert res["ingest_status"] == "BOUND_SHADOW"
    assert res["data_points"] == 2
    assert res["brier_forecast"] == 0.85

def test_main_dry_run(capsys):
    sketch.main(dry_run=True)
    out = capsys.readouterr().out
    assert "ABX HollerSports Shadow Pipeline Sketch v2.1" in out
    assert "ADVISORY_ONLY" in out or "Brier 0.85" in out
