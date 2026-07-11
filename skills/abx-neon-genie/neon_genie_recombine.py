"""Neon Genie Recombine stage (thin stub)."""

from __future__ import annotations
from typing import Any, Dict, List

def recombine(opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Recombine into candidate concepts (stub)."""
    candidates = []
    for opp in opportunities:
        candidates.append({
            "candidate_id": "cand_" + opp["opp_id"][-6:],
            "basis": opp,
            "recombined_description": f"Recombinant concept: {opp['description']}",
        })
    return candidates