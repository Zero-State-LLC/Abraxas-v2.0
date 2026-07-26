"""API settings — thin alias over core.RuntimeSettings."""

from __future__ import annotations

from core.settings import (
    RuntimeSettings,
    configure_runtime_settings,
    get_runtime_settings,
    load_runtime_settings,
)

# Backward-compatible names used by apps.api.main / routers.
AppSettings = RuntimeSettings
configure_settings = configure_runtime_settings
get_settings = get_runtime_settings
load_settings = load_runtime_settings

__all__ = [
    "AppSettings",
    "RuntimeSettings",
    "configure_settings",
    "get_settings",
    "load_settings",
]
