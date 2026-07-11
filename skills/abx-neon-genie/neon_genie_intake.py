"""Neon Genie Intake stage (thin stub)."""

from __future__ import annotations
from typing import Any, Dict, List

def intake(request: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Capture raw request as seed(s)."""
    seed = {
        "seed_id": "seed_" + str(hash(str(request)))[:8],
        "raw": request.get("seed") or request.get("prompt") or str(request),
        "mode": request.get("mode", "PROMPT_LED"),
        "tags": request.get("tags", []),
    }
    return [seed]