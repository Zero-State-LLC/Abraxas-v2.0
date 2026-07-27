"""Neon Genie Package stage (thin stub)."""

from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List

_THIS = Path(__file__).resolve()
_SKILL_DIR = _THIS.parent


def _load_evidence_mod():
    path = _SKILL_DIR / "evidence_pack.py"
    name = "neon_genie_evidence_pack_for_package"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load evidence_pack from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_evidence = _load_evidence_mod()


def package(shaped: List[Dict[str, Any]], overlap: Dict[str, Any], evidence_pack: Dict[str, Any], mode: str) -> Dict[str, Any]:
    """Assemble venture packet (stub for v0.4) with EvidencePack gates."""
    top = shaped[0] if shaped else {}
    packet: Dict[str, Any] = {
        "schema_version": "NeonGenieVenturePacket.v0.4",
        "input_mode": mode,
        "venture_name": top.get("shaped_name", "Unnamed Venture"),
        "output_class": top.get("venture_class", "HYBRID"),
        "overlap_classification": overlap.get("classification", "NOT_COMPUTABLE"),
        "score_vector": top.get("score_vector", {}),
        "evidence_basis": evidence_pack.get("status", "NOT_COMPUTABLE"),
        "evidence_pack_ref": evidence_pack.get("pack_ref"),
        "evidence_density": evidence_pack.get("evidence_density"),
        "seed_evidence": {
            "pack_id": evidence_pack.get("pack_id"),
            "pack_ref": evidence_pack.get("pack_ref"),
            "status": evidence_pack.get("status", "NOT_COMPUTABLE"),
            "register_counts": evidence_pack.get("register_counts"),
        },
        "route_binding": overlap.get("recommended_route", "internal"),
        "public_redacted": True,
        # Placeholder market_model — redacted when commercial gate fires
        "market_model": {
            "status": "PENDING_EVIDENCE",
            "buyer": None,
            "pricing": None,
            "competitors": None,
        },
    }
    _evidence.redact_commercial_fields(packet, evidence_pack)
    return packet
