"""Validation router for ABRAXAS v2.0 API."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from fastapi import APIRouter, Depends

from apps.api.deps import require_public_readonly_api_enabled
from core.config import RuntimePaths

router = APIRouter()

logger = logging.getLogger(__name__)

_PATHS = RuntimePaths.from_env()
_VALIDATION_PATH = _PATHS.validation_latest
_PROJECTION_PATH = _PATHS.projection_aal_viz_latest


def _not_computable(kind: str, detail: str) -> dict[str, Any]:
    return {
        "schema_version": f"{kind}.NOT_COMPUTABLE.v1",
        "status": "not_computable",
        "reason": detail,
    }


@router.get("/validation")
async def get_validation(
    _guard: None = Depends(require_public_readonly_api_enabled),
) -> dict[str, Any]:
    if _VALIDATION_PATH.exists():
        content = await asyncio.to_thread(_VALIDATION_PATH.read_text, encoding="utf-8")
        return json.loads(content)
    return _not_computable("DoctrineValidationRun", "validation output missing")


@router.get("/projection")
async def get_projection(
    _guard: None = Depends(require_public_readonly_api_enabled),
) -> dict[str, Any]:
    if _PROJECTION_PATH.exists():
        content = await asyncio.to_thread(_PROJECTION_PATH.read_text, encoding="utf-8")
        return json.loads(content)
    return _not_computable("GlobalPipelineAALVizProjectionPacket", "projection output missing")
