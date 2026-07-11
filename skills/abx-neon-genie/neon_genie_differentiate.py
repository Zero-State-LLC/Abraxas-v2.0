"""Neon Genie Differentiate stage (thin stub)."""

from __future__ import annotations
from typing import Any, Dict, List

def differentiate(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Apply basic differentiation (stub)."""
    for c in candidates:
        c["differentiation_note"] = "Differentiated from known patterns (stub)"
    return candidates