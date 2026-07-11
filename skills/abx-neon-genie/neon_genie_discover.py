"""Neon Genie Discover stage (thin stub)."""

from __future__ import annotations
from typing import Any, Dict, List

def discover(seeds: List[Dict[str, Any]], evidence_pack: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Map seeds to opportunities (stub)."""
    opps = []
    for seed in seeds:
        opps.append({
            "opp_id": "opp_" + seed["seed_id"][-6:],
            "from_seed": seed["seed_id"],
            "description": f"Opportunity derived from: {seed['raw'][:80]}",
            "evidence_status": evidence_pack.get("status", "UNKNOWN"),
        })
    return opps