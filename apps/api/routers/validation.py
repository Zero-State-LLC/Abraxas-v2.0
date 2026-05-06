"""Validation router for ABRAXAS v2.0 API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter()

_VALIDATION_PATH = Path("out/validation/latest.json")
_PROJECTION_PATH = Path("out/projections/aal_viz.latest.json")


@router.get("/validation")
async def get_validation() -> dict[str, Any]:
    """Return the latest doctrine validation run."""
    if _VALIDATION_PATH.exists():
        return json.loads(_VALIDATION_PATH.read_text(encoding="utf-8"))
    raise HTTPException(
        status_code=404,
        detail="No validation output found. Run scripts/run_doctrine_validator.py first.",
    )


@router.get("/projection")
async def get_projection() -> dict[str, Any]:
    """Return the latest AAL-Viz projection packet."""
    if _PROJECTION_PATH.exists():
        return json.loads(_PROJECTION_PATH.read_text(encoding="utf-8"))
    raise HTTPException(
        status_code=404,
        detail="No projection output found. Run scripts/run_doctrine_validator.py first.",
    )
