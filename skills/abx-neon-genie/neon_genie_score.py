"""Neon Genie Score stage — honest features, no stub ranker.

novelty / usefulness / buildability / monetization / overall stay
NOT_COMPUTABLE until a gated neon.rank model exists. evidence_density
may be COMPUTED from an EvidencePack. This is not Trutina and not forecast.
"""

from __future__ import annotations

from typing import Any, Dict, List

SCHEMA_VERSION = "NeonGenieScoreVector.v1"
_AXES = ("novelty", "usefulness", "buildability", "monetization", "overall")
_NO_RANKER = "no neon.rank model"


def _axis(reason: str) -> Dict[str, Any]:
    return {"value": None, "register": "NOT_COMPUTABLE", "reason": reason}


def _density_cell(evidence_pack: Dict[str, Any]) -> Dict[str, Any]:
    density = evidence_pack.get("evidence_density")
    if isinstance(density, (int, float)):
        return {
            "value": float(density),
            "register": "COMPUTED",
            "source": "EvidencePack.v0",
        }
    return {
        "value": None,
        "register": "NOT_COMPUTABLE",
        "reason": "no evidence_density",
    }


def score(candidates: List[Dict[str, Any]], evidence_pack: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Attach an honest score_vector. Never invent 0.6/0.75-style ranks."""
    blocked = bool(evidence_pack.get("commercial_claims_blocked", True))
    density = _density_cell(evidence_pack)
    n = len(candidates)
    for index, candidate in enumerate(candidates):
        desc = str(
            candidate.get("recombined_description")
            or candidate.get("description")
            or candidate.get("shaped_name")
            or ""
        )
        monetization_reason = (
            "COMMERCIAL_EVIDENCE_REQUIRED" if blocked else _NO_RANKER
        )
        candidate["score_vector"] = {
            "schema_version": SCHEMA_VERSION,
            "lane": "SHADOW",
            "ranker": "none",
            "novelty": _axis(_NO_RANKER),
            "usefulness": _axis(_NO_RANKER),
            "buildability": _axis(_NO_RANKER),
            "monetization": _axis(monetization_reason),
            "overall": _axis(_NO_RANKER),
            "evidence_density": density,
            "features": {
                "candidate_index": index,
                "candidate_count": n,
                "seed_char_len": len(desc),
                "commercial_claims_blocked": blocked,
                "evidence_status": evidence_pack.get("status"),
            },
        }
        candidate["commercial_claims_blocked"] = blocked
    return candidates
