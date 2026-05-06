"""Validation router for ABRAXAS v2.0 API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter

router = APIRouter()

_VALIDATION_PATH = Path("out/validation/latest.json")
_PROJECTION_PATH = Path("out/projections/aal_viz.latest.json")


def _not_computable(kind: str, detail: str) -> dict[str, Any]:
    return {
        "schema_version": f"{kind}.NOT_COMPUTABLE.v1",
        "status": "not_computable",
        "reason": detail,
    }


@router.get("/validation")
async def get_validation() -> dict[str, Any]:
    if _VALIDATION_PATH.exists():
        return json.loads(_VALIDATION_PATH.read_text(encoding="utf-8"))
    return _not_computable("DoctrineValidationRun", "validation output missing")


@router.get("/projection")
async def get_projection() -> dict[str, Any]:
    if _PROJECTION_PATH.exists():
        return json.loads(_PROJECTION_PATH.read_text(encoding="utf-8"))
    return _not_computable("GlobalPipelineAALVizProjectionPacket", "projection output missing")
