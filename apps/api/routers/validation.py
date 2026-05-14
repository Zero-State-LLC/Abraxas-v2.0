"""Validation router for ABRAXAS v2.0 API."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends

from apps.api.dependencies import require_public_readonly

logger = logging.getLogger(__name__)

router = APIRouter()

_VALIDATION_PATH = Path("out/validation/latest.json")
_PROJECTION_PATH = Path("out/projections/aal_viz.latest.json")


def _not_computable(kind: str, detail: str) -> dict[str, Any]:
    return {
        "schema_version": f"{kind}.NOT_COMPUTABLE.v1",
        "status": "not_computable",
        "reason": detail,
    }


@router.get("/validation", dependencies=[Depends(require_public_readonly)])
async def get_validation() -> dict[str, Any]:
    if _VALIDATION_PATH.exists():
        content = await asyncio.to_thread(_VALIDATION_PATH.read_text, encoding="utf-8")
        return json.loads(content)  # type: ignore[no-any-return]
    return _not_computable("DoctrineValidationRun", "validation output missing")


@router.get("/projection", dependencies=[Depends(require_public_readonly)])
async def get_projection() -> dict[str, Any]:
    if _PROJECTION_PATH.exists():
        content = await asyncio.to_thread(_PROJECTION_PATH.read_text, encoding="utf-8")
        return json.loads(content)  # type: ignore[no-any-return]
    return _not_computable("GlobalPipelineAALVizProjectionPacket", "projection output missing")
