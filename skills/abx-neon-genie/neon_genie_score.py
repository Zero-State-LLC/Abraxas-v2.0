"""Neon Genie Score stage (deterministic stub)."""

from __future__ import annotations
from typing import Any, Dict, List


def score(candidates: List[Dict[str, Any]], evidence_pack: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Deterministic scoring stub. Uses EvidencePack density when present."""
    density = evidence_pack.get("evidence_density")
    if density is None:
        status = str(evidence_pack.get("status", "")).upper()
        if status == "PROMPT_ONLY":
            density = 0.35
        elif status == "NOT_COMPUTABLE":
            density = 0.1
        elif status == "EVIDENCE_PACK":
            density = 0.55
        else:
            density = 0.4
    density = float(density)

    commercial_blocked = bool(evidence_pack.get("commercial_claims_blocked", True))
    monetization = 0.2 if commercial_blocked else 0.55

    for c in candidates:
        c["score_vector"] = {
            "novelty": 0.6,
            "usefulness": 0.75,
            "buildability": 0.5,
            "monetization": monetization,
            "evidence_density": density,
            "overall": round((0.6 + 0.75 + 0.5 + monetization + density) / 5, 2),
        }
        c["commercial_claims_blocked"] = commercial_blocked
    return candidates
