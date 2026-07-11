import json
from pathlib import Path
def test_canary_authority_isolation():
    canary = json.loads(Path("out/audit/abx_hermes_canary_observation_v2_2.latest.json").read_text())
    assert "SHADOW" in canary["boundary"]
    assert canary["authority_violations"] == 0
def test_no_active_mutation_in_cycle():
    cycle = json.loads(Path("out/audit/abx_hermes_evolution_cycle_001.latest.json").read_text())
    assert cycle["active_skill_modified"] is False
    assert cycle["candidate_promoted"] is False