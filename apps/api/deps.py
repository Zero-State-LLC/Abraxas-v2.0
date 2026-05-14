"""Shared FastAPI dependencies for ABRAXAS v2.0 API."""

from __future__ import annotations

import os

from fastapi import HTTPException


def require_public_readonly_api_enabled() -> None:
    """Raise 403 unless ABRAXAS_API_PUBLIC_READONLY is explicitly enabled."""
    flag = os.getenv("ABRAXAS_API_PUBLIC_READONLY", "").lower()
    if flag not in ("1", "true", "yes"):
        raise HTTPException(status_code=403, detail="api_public_readonly_disabled")
