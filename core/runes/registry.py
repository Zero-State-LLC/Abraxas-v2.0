"""Rune registry for ABRAXAS v2.0."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.file_cache import read_text_cached
from core.runes.models import RuneContract

_RUNE_CATALOG_CACHE: dict[str, tuple[str, dict[str, RuneContract]]] = {}


def load_rune_catalog(path: str | Path) -> dict[str, RuneContract]:
    """Load the rune catalog JSON and return a mapping of rune_id -> RuneContract."""
    target = Path(path)
    cache_key = target.resolve().as_posix()
    text = read_text_cached(target)
    cached = _RUNE_CATALOG_CACHE.get(cache_key)
    if cached is not None and cached[0] == text:
        return {rune_id: rune.model_copy(deep=True) for rune_id, rune in cached[1].items()}
    data = json.loads(text)
    catalog: dict[str, RuneContract] = {}
    for entry in data.get("runes", []):
        rune = RuneContract.model_validate(entry)
        catalog[rune.rune_id] = rune
    _RUNE_CATALOG_CACHE[cache_key] = (text, catalog)
    return {rune_id: rune.model_copy(deep=True) for rune_id, rune in catalog.items()}


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
