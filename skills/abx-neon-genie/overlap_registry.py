"""Overlap / Duplicate Detector (critical high-risk gate)."""

from __future__ import annotations
from typing import Any, Dict, List

# Stub inventory — in real use would query repo-intel + ownership matrix + catalog
KNOWN_SUBSYSTEMS = {
    "forecasting": "Abraxas / PSE Forecast",
    "dream": "Noctis",
    "music": "BeatOven",
    "introspection": "PsyFi",
    "provenance": "Phonomicon",
    "visualization": "AAL-Viz",
    "virality": "Level 99",
    "execution": "ABX-Familiar",
    "competitive": "SignalOps / LeakForge",
    "construct": "Sigil-Forge",
    "tradition": "Athanor",
    "sign": "Semion",
    "brier": "Trutina",
    "slang": "Hyperlex",
}

def classify_overlap(concepts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Classify for overlap/duplicate risk. Stub logic."""
    if not concepts:
        return {"classification": "NOT_COMPUTABLE", "recommended_route": "none"}

    # Extremely simplified — real version queries full inventory
    description = str(concepts[0]).lower()
    if any(k in description for k in ["forecast", "predict"]):
        return {"classification": "DUPLICATE", "recommended_route": "Abraxas", "reason": "forecast overlap"}
    if any(k in description for k in ["dream", "symbolic", "motif"]):
        return {"classification": "ADJACENT", "recommended_route": "Noctis (seeds only)", "reason": "symbolic seed"}
    if "level 99" in description or "virality" in description:
        return {"classification": "WRAPPER_CANDIDATE", "recommended_route": "Level 99", "reason": "memetic overlap"}
    if "competitive" in description or "leakforge" in description:
        return {"classification": "DUPLICATE", "recommended_route": "SignalOps / LeakForge"}
    if any(k in description for k in ["sigil-forge", "kamea", "construct glyph"]):
        return {
            "classification": "ADJACENT",
            "recommended_route": "Sigil-Forge",
            "specialist_skills": ["sigil-forge"],
            "reason": "construct / geometry seed",
        }
    if "athanor" in description or "tradition retrieve" in description:
        return {
            "classification": "ADJACENT",
            "recommended_route": "Athanor",
            "specialist_skills": ["athanor"],
            "reason": "tradition retrieve seed",
        }
    if "semion" in description or "sign triad" in description:
        return {
            "classification": "ADJACENT",
            "recommended_route": "Semion",
            "specialist_skills": ["semion"],
            "reason": "sign-class seed",
        }
    if "trutina" in description or "brier" in description:
        return {
            "classification": "ADJACENT",
            "recommended_route": "Trutina",
            "specialist_skills": ["trutina"],
            "reason": "settled score ask — not a Neon rank",
        }
    if "hyperlex" in description or "slang" in description:
        return {
            "classification": "ADJACENT",
            "recommended_route": "Hyperlex",
            "specialist_skills": ["hyperlex"],
            "reason": "form / lexical seed",
        }

    # Default to novel for this thin stub
    return {
        "classification": "NOVEL",
        "recommended_route": "NeonGenie",
        "specialist_skills": [],
        "reason": "no strong overlap detected in stub inventory",
    }