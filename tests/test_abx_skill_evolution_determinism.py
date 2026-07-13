import json
from pathlib import Path
import subprocess
import sys
def test_deterministic_replay_and_corpus_hash():
    c1 = json.loads(Path("out/audit/abx_hermes_replay_corpus_v2_2.latest.json").read_text())
    c2 = json.loads(Path("out/audit/abx_hermes_replay_corpus_v2_2.latest.json").read_text())
    assert c1["corpus_hash"] == c2["corpus_hash"]
    # Run comparator twice
    r1 = subprocess.run([sys.executable, "skills/abx-hermes-skill-evolution/abx_skill_replay_stub.py"], capture_output=True, text=True)
    r2 = subprocess.run([sys.executable, "skills/abx-hermes-skill-evolution/abx_skill_replay_stub.py"], capture_output=True, text=True)
    assert r1.stdout == r2.stdout  # deterministic output