"""Registry router for ABRAXAS v2.0 API."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from apps.api.dependencies import require_public_readonly

logger = logging.getLogger(__name__)

router = APIRouter()

_REGISTRY_PATH = Path("out/registry/latest.json")
_CONTRACTS_DIR = Path("contracts/pipelines")


@router.get("/registry", dependencies=[Depends(require_public_readonly)])
async def get_registry() -> dict[str, Any]:
    """Return the pipeline registry, loading from file if available."""
    if _REGISTRY_PATH.exists():
        content = await asyncio.to_thread(_REGISTRY_PATH.read_text, encoding="utf-8")
        return json.loads(content)  # type: ignore[no-any-return]

    # Generate on the fly if file doesn't exist
    try:
        from core.pipelines.registry import build_registry, load_contracts

        contracts = load_contracts(_CONTRACTS_DIR)
        return build_registry(contracts)  # type: ignore[no-any-return]
    except Exception as exc:
        logger.exception("registry build failed: %s", exc)
        raise HTTPException(status_code=500, detail="registry_unavailable") from exc
