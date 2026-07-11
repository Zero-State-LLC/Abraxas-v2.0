"""Neon Genie Package stage (thin stub)."""

from __future__ import annotations
from typing import Any, Dict, List

def package(shaped: List[Dict[str, Any]], overlap: Dict[str, Any], evidence_pack: Dict[str, Any], mode: str) -> Dict[str, Any]:
    """Assemble venture packet (stub for v0.4)."""
    top = shaped[0] if shaped else {}
    return {
        "schema_version": "NeonGenieVenturePacket.v0.4",
        "input_mode": mode,
        "venture_name": top.get("shaped_name", "Unnamed Venture"),
        "output_class": top.get("venture_class", "HYBRID"),
        "overlap_classification": overlap.get("classification", "NOT_COMPUTABLE"),
        "score_vector": top.get("score_vector", {}),
        "evidence_basis": evidence_pack.get("status", "NOT_COMPUTABLE"),
        "route_binding": overlap.get("recommended_route", "internal"),
        "public_redacted": True,
    }