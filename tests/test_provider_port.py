"""Provider adapter port — fail-closed default."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.ports.provider import DeniedProvider, ProviderDeniedError
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
