"""ABRAXAS v2 API app."""

from __future__ import annotations

from fastapi import FastAPI

from apps.api.routers.health import router as health_router
from apps.api.routers.registry import router as registry_router
from apps.api.routers.validation import router as validation_router

app = FastAPI(title="ABRAXAS v2")
app.include_router(health_router)
app.include_router(registry_router)
app.include_router(validation_router)
