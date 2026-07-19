#!/usr/bin/env python3
"""
Pre-Execution Snapshot for Oracle Guided Execution v1
Candidate 00d0fb441ea388c2
"""

import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as e:
        return f"ERROR: {e.output.strip()}"

def snapshot():
    snap = {
        "candidate_id": "00d0fb441ea388c2",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "git_status": run_cmd("git status --porcelain"),
        "git_head": run_cmd("git rev-parse HEAD"),
        "relevant_file_hashes": {},
        "oracle_artifact_hashes": {},
        "work_packet_hash": None,
        "boundary_hash": None,
        "test_baseline": run_cmd("env -i PATH=\"$PATH\" HOME=\"$HOME\" USER=\"$USER\" UV_CACHE_DIR=\"$HOME/.cache/uv\" uv run python -m pytest tests/test_abraxas_engineering_oracle_v1.py tests/test_abx_skill_evolution*.py -q --tb=no"),
        "policy_refs": 3,
        "affected_path_state": {},
        "unrelated_dirty": [],
    }

    # File hashes
    for p in ["core/scoring/models.py"]:
        if Path(p).exists():
            snap["relevant_file_hashes"][p] = hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]

    oracle_dir = Path("out/repo_intelligence/engineering_oracle")
    for f in ["engineering_candidates.v1.json", "engineering_oracle_decision.v1.json", "primary_work_packet.v1.json"]:
        fp = oracle_dir / f
        if fp.exists():
            snap["oracle_artifact_hashes"][f] = hashlib.sha256(fp.read_bytes()).hexdigest()[:16]

    # Packet and boundary
    pkt = json.loads((oracle_dir / "primary_work_packet.v1.json").read_text())
    snap["work_packet_hash"] = hashlib.sha256(json.dumps(pkt, sort_keys=True).encode()).hexdigest()[:16]

    boundary_path = Path("out/oracle_execution/execution_boundary.v1.json")
    if boundary_path.exists():
        b = json.loads(boundary_path.read_text())
        snap["boundary_hash"] = b.get("boundary_hash")

    # Affected path
    snap["affected_path_state"]["core/scoring/models.py"] = {
        "exists": Path("core/scoring/models.py").exists(),
        "size": Path("core/scoring/models.py").stat().st_size if Path("core/scoring/models.py").exists() else 0
    }

    # TD Wave 1: pure builder — scripts/run_oracle_pre_execution_snapshot.py publishes.
    return snap

if __name__ == "__main__":
    snap = snapshot()
    print(json.dumps(snap, indent=2, sort_keys=True))
    print("Note: not writing out/; use scripts/run_oracle_pre_execution_snapshot.py to publish.")
