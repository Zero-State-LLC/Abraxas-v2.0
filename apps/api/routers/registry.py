"""Registry router for ABRAXAS v2.0 API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter()

_REGISTRY_PATH = Path("out/registry/latest.json")
_CONTRACTS_DIR = Path("contracts/pipelines")


@router.get("/registry")
async def get_registry() -> dict[str, Any]:
    """Return the pipeline registry, loading from file if available."""
    if _REGISTRY_PATH.exists():
        return json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))

    # Generate on the fly if file doesn't exist
    try:
        from core.pipelines.registry import build_registry, load_contracts

        contracts = load_contracts(_CONTRACTS_DIR)
        return build_registry(contracts)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
