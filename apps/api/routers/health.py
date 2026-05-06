"""Health router for ABRAXAS v2.0 API."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    """Return system health status."""
    return {"status": "ok", "system": "abraxas-v2"}
