"""Tests for core.settings.RuntimeSettings."""

from __future__ import annotations

from pathlib import Path

from apps.api.main import create_app
from apps.api.settings import AppSettings
from core.governance.activation_policy import ActivationLane
from core.settings import (
    configure_runtime_settings,
    get_runtime_settings,
    load_runtime_settings,
)


def test_load_runtime_settings_defaults(tmp_path: Path) -> None:
    settings = load_runtime_settings(repo_root=tmp_path)
    assert settings.default_activation_lane == ActivationLane.LOCAL_DEV
    assert settings.resolved_out_dir() == tmp_path / "out"
    assert settings.runtime_paths().out_dir == tmp_path / "out"
    diag = settings.redacted_diagnostics()
    assert "secret" not in str(diag).lower()
    assert diag["default_activation_lane"] == "LOCAL_DEV"


def test_configure_runtime_settings_roundtrip(tmp_path: Path) -> None:
    previous = get_runtime_settings()
    try:
        configured = configure_runtime_settings(
            repo_root=tmp_path,
            app_version="2.5.0-test",
            default_activation_lane="SANDBOX",
        )
        assert get_runtime_settings().app_version == "2.5.0-test"
        assert get_runtime_settings().default_activation_lane == ActivationLane.SANDBOX
        assert configured.repo_root == tmp_path
    finally:
        configure_runtime_settings(previous)


def test_app_settings_alias_create_app() -> None:
    app = create_app(AppSettings(app_version="9.9.9", enable_analyze_endpoint=True))
    assert app.version == "9.9.9"
