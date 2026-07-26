"""Provider adapter port — fail-closed default + fixture/lane gate."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.governance.activation_policy import ActivationLane
from core.ports.provider import (
    DeniedProvider,
    FixtureProvider,
    ProviderDeniedError,
    ProviderError,
    gated_invoke,
)
from core.runtime_context import RuntimeContext
from core.settings import load_runtime_settings


def test_denied_provider_fail_closed() -> None:
    provider = DeniedProvider()
    assert provider.provider_id == "denied"
    with pytest.raises(ProviderDeniedError, match="provider_adapter_not_configured"):
        provider.invoke({"prompt": "nope"})


def test_runtime_context_defaults_to_denied_provider(tmp_path: Path) -> None:
    ctx = RuntimeContext.build(load_runtime_settings(repo_root=tmp_path))
    assert ctx.provider.provider_id == "denied"
    with pytest.raises(ProviderDeniedError):
        ctx.provider.invoke({})


def test_fixture_provider_deterministic() -> None:
    provider = FixtureProvider({"echo": {"text": "hello", "n": 1}})
    first = provider.invoke({"fixture_id": "echo"})
    second = provider.invoke({"fixture_id": "echo"})
    assert first == second
    assert first["status"] == "OK"
    assert first["payload"]["text"] == "hello"
    with pytest.raises(ProviderError, match="unknown_fixture_id"):
        provider.invoke({"fixture_id": "missing"})


def test_gated_invoke_denies_external_production(tmp_path: Path) -> None:
    settings = load_runtime_settings(
        repo_root=tmp_path,
        allow_provider_invoke=True,
    )
    provider = FixtureProvider({"x": {"ok": True}})
    with pytest.raises(ProviderDeniedError, match="EXTERNAL_PRODUCTION"):
        gated_invoke(
            provider,
            {"fixture_id": "x"},
            lane=ActivationLane.EXTERNAL_PRODUCTION,
            settings=settings,
        )


def test_gated_invoke_requires_allow_flag(tmp_path: Path) -> None:
    settings = load_runtime_settings(
        repo_root=tmp_path,
        allow_provider_invoke=False,
    )
    provider = FixtureProvider({"x": {"ok": True}})
    with pytest.raises(ProviderDeniedError, match="ALLOW_PROVIDER_INVOKE"):
        gated_invoke(
            provider,
            {"fixture_id": "x"},
            lane=ActivationLane.LOCAL_DEV,
            settings=settings,
        )


def test_gated_invoke_fixture_when_allowed(tmp_path: Path) -> None:
    settings = load_runtime_settings(
        repo_root=tmp_path,
        allow_provider_invoke=True,
    )
    provider = FixtureProvider({"x": {"ok": True}})
    result = gated_invoke(
        provider,
        {"fixture_id": "x"},
        lane="LOCAL_DEV",
        settings=settings,
    )
    assert result["payload"]["ok"] is True


def test_runtime_context_accepts_fixture_provider(tmp_path: Path) -> None:
    settings = load_runtime_settings(repo_root=tmp_path)
    ctx = RuntimeContext.build(
        settings,
        provider=FixtureProvider({"probe": {"v": 2}}),
    )
    assert ctx.provider.provider_id == "fixture"
    assert ctx.provider.invoke({"fixture_id": "probe"})["payload"]["v"] == 2
