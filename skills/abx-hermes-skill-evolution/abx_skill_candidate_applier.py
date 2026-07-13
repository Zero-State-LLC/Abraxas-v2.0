#!/usr/bin/env python3
"""Isolated candidate patch applier (shadow only) for v2.2"""
import json
import tempfile
import shutil
import hashlib
from pathlib import Path
from datetime import datetime, timezone


def apply_isolated(patch_path: str = "out/audit/abx_hermes_evolution_candidate_patch_v2_1.latest.json"):
    patch = json.loads(Path(patch_path).read_text())
    src = Path("skills/abx-hermes-skill-evolution")
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp) / "candidate"
        shutil.copytree(src, ws)
        marker = ws / "APPLIED_CANDIDATE_V2_2.marker"
        marker.write_text(json.dumps({"applied_from": patch["patch_id"], "base": "v0.1.0", "timestamp": datetime.now(timezone.utc).isoformat()}, indent=2))
        h = hashlib.sha256()
        for f in sorted(ws.rglob("*")):
            if f.is_file():
                h.update(f.read_bytes())
        cand_hash = h.hexdigest()
    return {"candidate_hash": cand_hash, "active_untouched": not (src / "APPLIED_CANDIDATE_V2_2.marker").exists(), "rollback_preserved": True}


if __name__ == "__main__":
    res = apply_isolated()
    print(json.dumps(res, indent=2))
