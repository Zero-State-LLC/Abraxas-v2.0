"""Tests for out/audit/holler_sports_forecasting_model_sketch_v2.1.py (TEST candidate 1be5e523a6d17881)"""

import importlib.util
from pathlib import Path

# Dynamically load the sketch (not a package)
sketch_path = Path("out/audit/holler_sports_forecasting_model_sketch_v2.1.py")
spec = importlib.util.spec_from_file_location("holler_sketch", sketch_path)
sketch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sketch)

def test_canonical_hash_deterministic():
    data = {"events": [1, 2], "runes": ["A", "B"]}
    h1 = sketch.canonical_hash(data)
    h2 = sketch.canonical_hash(data)
    assert h1 == h2
    assert len(h1) == 16

def test_brier_weighted_forecast_basic():
    events = [{"game": "g1", "odds": 1.8}]
    runes = ["RUNE.TEST"]
    result = sketch.brier_weighted_forecast(events, runes)
    assert result["events_forecasted"] == 1
    assert result["rune_bindings"] == runes
    assert result["brier_score"] == 0.85
    assert "provenance" in result

def test_main_dry_run(capsys):
    sketch.main(dry_run=True)
    out = capsys.readouterr().out
    assert "ABX HollerSports Forecasting Model Sketch v2.1" in out
    assert "DRY-RUN ONLY" in out or "Brier 0.85" in out
