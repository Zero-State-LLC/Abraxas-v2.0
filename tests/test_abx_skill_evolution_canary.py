import json
from pathlib import Path

def test_canary_is_shadow_only():
    canary = json.loads(Path("out/audit/abx_hermes_canary_observation_v2_2.latest.json").read_text())
    assert "SHADOW" in canary["boundary"]
    assert canary.get("authority_violations", 0) == 0
    assert canary["actual_runs"] >= 5

def test_canary_agreement_rate_reasonable():
    canary = json.loads(Path("out/audit/abx_hermes_canary_observation_v2_2.latest.json").read_text())
    assert 0.5 <= canary["agreement_rate"] <= 1.0