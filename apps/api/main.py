"""ABRAXAS v2.0 FastAPI application."""

from __future__ import annotations

from fastapi import FastAPI

from apps.api.routers import health, registry, validation

app = FastAPI(
    title="ABRAXAS v2.0",
    description="Recursively governed symbolic operating substrate – Kernel Zero",
    version="2.0.0",
)

app.include_router(health.router)
app.include_router(registry.router)
app.include_router(validation.router)
