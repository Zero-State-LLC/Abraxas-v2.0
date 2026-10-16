"""Bounded advisory analysis endpoint (supported product spine)."""

from __future__ import annotations

import asyncio
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from starlette.concurrency import run_in_threadpool

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
    alembic_mode: Literal["advisory", "shadow"] = "advisory"
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

    request = {
        "run_id": body.run_id,
        "activation_lane": lane,
        "input_payload": body.input_payload,
        "schema_ref": body.schema_ref,
        "alembic_task": body.alembic_task,
        "oracle_candidate": body.oracle_candidate,
        "enable_alembic": body.enable_alembic,
        "alembic_mode": body.alembic_mode,
    }
    # Bounded execution: the spine runs off the event loop under a deadline.
    # A timed-out worker thread is not killed (reference limitation).
    try:
        return await asyncio.wait_for(
            run_in_threadpool(
                run_advisory_spine,
                request,
                repo_root=settings.repo_root,
                canary_evidence=(
                    settings.canary_evidence_verification()
                    if lane == ActivationLane.INTERNAL_CANARY
                    else None
                ),
            ),
            timeout=settings.analyze_timeout_seconds,
        )
    except TimeoutError:
        raise HTTPException(status_code=503, detail="analysis_timeout") from None
    except ValidationError:
        # Malformed nested task/candidate: client error, not an internal one.
        raise HTTPException(status_code=422, detail="invalid_analysis_request") from None


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
async def version() -> dict[str, str | None]:
    """Identify this build as doctrine reference code, never as a product release.

    v2.0 publishes doctrine revisions (the ``v1.N`` tags, mirrored in VERSION);
    the supported Abraxas product and its versions live in Zero-State-LLC/Abraxas.
    """
    settings = get_settings()
    version_file = settings.repo_root / "VERSION"
    doctrine_revision = (
        version_file.read_text(encoding="utf-8").strip() if version_file.is_file() else None
    )
    return {
        "system": "abraxas-v2",
        "title": settings.app_title,
        "role": "doctrine-reference",
        "doctrine_revision": doctrine_revision,
        "reference_build": settings.app_version,
        "product_version": None,
        "canonical_product_repository": "Zero-State-LLC/Abraxas",
    }
