"""Bounded advisory analysis endpoint (supported product spine)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from apps.api.boundaries import (
    check_authentication_boundary,
    check_rate_limit_boundary,
)
from apps.api.deps import require_public_readonly_api_enabled
from apps.api.settings import get_settings
from core.application.advisory_spine import run_advisory_spine
from core.governance.activation_policy import ActivationLane

router = APIRouter()


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(min_length=1, max_length=128)
    input_payload: dict[str, Any] = Field(default_factory=dict)
    schema_ref: str | None = None
    alembic_task: dict[str, Any] | None = None
    oracle_candidate: dict[str, Any] | None = None
    enable_alembic: bool = True
    alembic_mode: str = "advisory"
    activation_lane: str | None = None


@router.post(
    "/analyze",
    dependencies=[
        Depends(check_authentication_boundary),
        Depends(check_rate_limit_boundary),
    ],
)
async def analyze(body: AnalyzeRequest) -> dict[str, Any]:
    settings = get_settings()
    if not settings.enable_analyze_endpoint:
        raise HTTPException(status_code=404, detail="analyze_endpoint_disabled")
    if settings.require_public_readonly_for_analyze:
        require_public_readonly_api_enabled()

    lane = body.activation_lane or settings.default_activation_lane
    try:
        ActivationLane(lane)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid_activation_lane") from exc

    if len(str(body.input_payload)) > 200_000:
        raise HTTPException(status_code=413, detail="input_payload_too_large")

    return run_advisory_spine(
        {
            "run_id": body.run_id,
            "activation_lane": lane,
            "input_payload": body.input_payload,
            "schema_ref": body.schema_ref,
            "alembic_task": body.alembic_task,
            "oracle_candidate": body.oracle_candidate,
            "enable_alembic": body.enable_alembic,
            "alembic_mode": body.alembic_mode,
        }
    )


@router.get("/ready")
async def readiness() -> dict[str, Any]:
    settings = get_settings()
    return {
        "status": "ready",
        "system": "abraxas-v2",
        "analyze_enabled": settings.enable_analyze_endpoint,
        "candidate_status": "NOT_READY",
        "external_production_authorized": False,
    }


@router.get("/version")
async def version() -> dict[str, str]:
    settings = get_settings()
    return {
        "system": "abraxas-v2",
        "version": settings.app_version,
        "title": settings.app_title,
    }
