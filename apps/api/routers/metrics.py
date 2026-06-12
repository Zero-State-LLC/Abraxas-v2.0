"""Read-only ABX metric dashboard router."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from apps.api.deps import require_public_readonly_api_enabled
from core.abx_metric_dashboard import build_abx_metric_dashboard_frame

router = APIRouter()


@router.get("/api/abx/metrics/dashboard")
async def get_abx_metric_dashboard(
    _guard: None = Depends(require_public_readonly_api_enabled),
) -> dict[str, Any]:
    return build_abx_metric_dashboard_frame()
