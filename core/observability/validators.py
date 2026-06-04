from __future__ import annotations

from typing import Any


def validate_lineage_replay(trace: dict[str, Any], replay_packet: dict[str, Any]) -> dict[str, Any]:
    nodes = trace.get("nodes", [])
    seen_hashes: set[str] = set()
    for n in nodes:
        ph = n.get("parent_hash")
        if ph is not None and ph not in seen_hashes:
            return {"status": "failed", "reason": "missing parent", "deterministic": False}
        sh = n.get("source_hash")
        if sh in seen_hashes:
            return {"status": "failed", "reason": "cyclic lineage", "deterministic": False}
        seen_hashes.add(sh)
    if replay_packet.get("status") != "passed":
        return {"status": "failed", "reason": "replay mismatch", "deterministic": False}
    return {"status": "passed", "reason": "lineage deterministic", "deterministic": True}
