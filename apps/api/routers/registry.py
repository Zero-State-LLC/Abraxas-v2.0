"""Registry router for ABRAXAS v2.0 API."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from apps.api.deps import require_public_readonly_api_enabled
from core.config import RuntimePaths
from core.diagnostics import log_event, stable_correlation_id

router = APIRouter()

logger = logging.getLogger(__name__)

_PATHS = RuntimePaths.from_env()
_REGISTRY_PATH = _PATHS.registry_latest
_CONTRACTS_DIR = _PATHS.pipelines_contracts_dir


@router.get("/registry")
async def get_registry(
    _guard: None = Depends(require_public_readonly_api_enabled),
) -> dict[str, Any]:
    """Return the pipeline registry, loading from file if available."""
    if _REGISTRY_PATH.exists():
        content = await asyncio.to_thread(_REGISTRY_PATH.read_text, encoding="utf-8")
        return json.loads(content)

    # Generate on the fly if file doesn't exist
    try:
        from core.pipelines.registry import build_registry, load_contracts

        contracts = await asyncio.to_thread(load_contracts, _CONTRACTS_DIR)
        return build_registry(contracts)
    except Exception:
        log_event(
            logger,
            "ERROR",
            "api_registry_unavailable",
            exc_info=True,
            route="/registry",
            reason="registry_unavailable",
            artifact_path=str(_REGISTRY_PATH),
            contracts_dir=str(_CONTRACTS_DIR),
            correlation_id=stable_correlation_id(
                "api_registry_failure",
                artifact_path=_REGISTRY_PATH,
                context={
                    "route": "/registry",
                    "contracts_dir": str(_CONTRACTS_DIR),
                    "reason": "registry_unavailable",
                },
            ),
        )
        raise HTTPException(status_code=500, detail="registry_unavailable") from None
