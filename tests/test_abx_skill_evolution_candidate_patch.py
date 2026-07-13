import json
from pathlib import Path
def test_candidate_patch_schema_and_isolation():
    patch = json.loads(Path("out/audit/abx_hermes_evolution_candidate_patch_v2_1.latest.json").read_text())
    assert "diff" in patch and "replay_regressions" in patch
    assert patch["replay_regressions"] == 0
    # Isolation check via applier
    import subprocess
    import sys
    res = subprocess.run([sys.executable, "skills/abx-hermes-skill-evolution/abx_skill_candidate_applier.py"], capture_output=True, text=True)
    data = json.loads(res.stdout)
    assert data["active_untouched"] is True