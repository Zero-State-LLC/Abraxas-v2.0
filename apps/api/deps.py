"""Shared FastAPI dependencies for ABRAXAS v2.0 API."""

from __future__ import annotations

from fastapi import HTTPException

from core.config import api_public_readonly_enabled


def require_public_readonly_api_enabled() -> None:
    """Raise 403 unless ABRAXAS_API_PUBLIC_READONLY is explicitly enabled."""
    try:
        enabled = api_public_readonly_enabled()
    except ValueError:
        raise HTTPException(status_code=403, detail="api_public_readonly_disabled") from None
    if not enabled:
        raise HTTPException(status_code=403, detail="api_public_readonly_disabled")
