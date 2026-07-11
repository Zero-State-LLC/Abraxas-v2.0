"""Neon Genie Score stage (deterministic stub)."""

from __future__ import annotations
from typing import Any, Dict, List

def score(candidates: List[Dict[str, Any]], evidence_pack: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Deterministic scoring stub. Evidence-aware but simple."""
    for c in candidates:
        evidence_density = 0.7 if evidence_pack.get("status") == "PROMPT_ONLY" else 0.4
        c["score_vector"] = {
            "novelty": 0.6,
            "usefulness": 0.75,
            "buildability": 0.5,
            "monetization": 0.55,
            "evidence_density": evidence_density,
            "overall": round((0.6 + 0.75 + 0.5 + 0.55 + evidence_density) / 5, 2),
        }
    return candidates