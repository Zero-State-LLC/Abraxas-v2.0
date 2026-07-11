"""Neon Genie Shape stage (thin stub)."""

from __future__ import annotations
from typing import Any, Dict, List

def shape(scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Shape into venture-ready form (stub)."""
    for s in scored:
        s["shaped_name"] = f"Shaped: {s.get('basis', {}).get('description', 'Concept')[:40]}"
        s["venture_class"] = "HYBRID"  # default stub
    return scored