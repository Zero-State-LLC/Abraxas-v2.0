"""Shared FastAPI dependencies for ABRAXAS v2.0 API."""

from __future__ import annotations

import os

from fastapi import HTTPException


def require_public_readonly() -> None:
    """Require ABRAXAS_API_PUBLIC_READONLY=true or return 403.

    Registry and validation endpoints are read-only public only when
    this flag is explicitly set.  Default is fail-closed.
    """
    if os.environ.get("ABRAXAS_API_PUBLIC_READONLY", "").lower() != "true":
        raise HTTPException(status_code=403, detail="api_public_readonly_disabled")
