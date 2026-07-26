"""ABRAXAS v2 API app — supported service factory."""

from __future__ import annotations

from fastapi import FastAPI

from apps.api.routers.analyze import router as analyze_router
from apps.api.routers.health import router as health_router
from apps.api.routers.metrics import router as metrics_router
from apps.api.routers.registry import router as registry_router
from apps.api.routers.validation import router as validation_router
from apps.api.settings import AppSettings, configure_settings, load_settings


def create_app(settings: AppSettings | None = None) -> FastAPI:
    """Application factory for the supported ASGI service."""
    resolved = configure_settings(settings if settings is not None else load_settings())
    application = FastAPI(title=resolved.app_title, version=resolved.app_version)
    application.include_router(health_router)
    application.include_router(analyze_router)
    application.include_router(registry_router)
    application.include_router(validation_router)
    application.include_router(metrics_router)
    return application


# Backward-compatible module-level app for existing tests and uvicorn targets.
app = create_app()
