"""Rune registry for ABRAXAS v2.0."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.runes.models import RuneContract


def load_rune_catalog(path: str | Path) -> dict[str, RuneContract]:
    """Load the rune catalog JSON and return a mapping of rune_id -> RuneContract."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    catalog: dict[str, RuneContract] = {}
    for entry in data.get("runes", []):
        rune = RuneContract.model_validate(entry)
        catalog[rune.rune_id] = rune
    return catalog


def lookup_rune(
    rune_id: str, catalog: dict[str, RuneContract]
) -> dict[str, Any]:
    """Return the rune entry or a NOT_COMPUTABLE result if unknown."""
    if rune_id in catalog:
        return {"status": "found", "rune": catalog[rune_id].model_dump()}
    return {
        "status": "not_computable",
        "reason": f"Unknown rune_id: {rune_id!r}",
        "rune_id": rune_id,
    }
