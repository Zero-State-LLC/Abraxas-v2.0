"""Typed API settings (filesystem paths stay in RuntimePaths)."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ABRAXAS_",
        extra="ignore",
        frozen=True,
    )

    app_title: str = "ABRAXAS v2"
    app_version: str = "2.5.0"
    enable_analyze_endpoint: bool = True
    default_activation_lane: str = "LOCAL_DEV"
    # When true, gated read endpoints require ABRAXAS_API_PUBLIC_READONLY=true.
    require_public_readonly_for_analyze: bool = False


_SETTINGS: AppSettings | None = None


def load_settings(**overrides: object) -> AppSettings:
    if overrides:
        return AppSettings(**overrides)  # type: ignore[arg-type]
    return AppSettings()


def configure_settings(settings: AppSettings | None = None, **overrides: object) -> AppSettings:
    """Set process-wide settings used by the app factory and dependencies."""
    global _SETTINGS
    if settings is not None and overrides:
        raise ValueError("pass settings or overrides, not both")
    _SETTINGS = settings if settings is not None else load_settings(**overrides)
    return _SETTINGS


def get_settings() -> AppSettings:
    global _SETTINGS
    if _SETTINGS is None:
        _SETTINGS = load_settings()
    return _SETTINGS
