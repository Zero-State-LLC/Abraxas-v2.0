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

    # Default to novel for this thin stub
    return {
        "classification": "NOVEL",
        "recommended_route": "NeonGenie",
        "specialist_skills": [],
        "reason": "no strong overlap detected in stub inventory",
    }