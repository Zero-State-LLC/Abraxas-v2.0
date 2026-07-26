"""Provider adapter port — fail-closed by default; no network at import/construct."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from core.governance.activation_policy import ActivationLane
from core.settings import RuntimeSettings


class ProviderError(RuntimeError):
    """Base error for provider adapter failures."""


class ProviderDeniedError(ProviderError):
    """Raised when no provider adapter is configured or lane/settings deny invoke."""


class ProviderPort(Protocol):
    """Outbound model/tool provider seam.

    Implementations may perform network I/O only after explicit construction and
    lane-appropriate configuration. Importing this module never opens sockets.
    """

    @property
    def provider_id(self) -> str: ...

    def invoke(self, request: Mapping[str, Any]) -> dict[str, Any]:
        """Execute a provider request or raise ProviderError."""


class DeniedProvider:
    """Default adapter: deny all invokes; never contacts external services."""

    provider_id = "denied"

    def invoke(self, request: Mapping[str, Any]) -> dict[str, Any]:
        raise ProviderDeniedError(
            "provider_adapter_not_configured; no network calls permitted by default"
        )


class FixtureProvider:
    """Deterministic in-memory fixture adapter — never opens sockets."""

    provider_id = "fixture"

    def __init__(self, fixtures: Mapping[str, Mapping[str, Any]] | None = None) -> None:
        self._fixtures = {
            str(key): dict(value) for key, value in dict(fixtures or {}).items()
        }

    def invoke(self, request: Mapping[str, Any]) -> dict[str, Any]:
        fixture_id = str(request.get("fixture_id") or request.get("id") or "")
        if not fixture_id:
            raise ProviderError("fixture_id required")
        if fixture_id not in self._fixtures:
            raise ProviderError(f"unknown_fixture_id:{fixture_id}")
        payload = dict(self._fixtures[fixture_id])
        return {
            "provider_id": self.provider_id,
            "fixture_id": fixture_id,
            "status": "OK",
            "payload": payload,
        }


def gated_invoke(
    provider: ProviderPort,
    request: Mapping[str, Any],
    *,
    lane: ActivationLane | str,
    settings: RuntimeSettings,
) -> dict[str, Any]:
    """Invoke a provider only when lane/settings permit.

    - EXTERNAL_PRODUCTION is always denied.
    - Non-denied providers require ``settings.allow_provider_invoke``.
    - DeniedProvider remains fail-closed regardless of the flag.
    """
    resolved_lane = ActivationLane(lane)
    if resolved_lane == ActivationLane.EXTERNAL_PRODUCTION:
        raise ProviderDeniedError(
            "provider_invoke_denied; EXTERNAL_PRODUCTION is operator-gated"
        )
    if isinstance(provider, DeniedProvider):
        return provider.invoke(request)
    if not bool(getattr(settings, "allow_provider_invoke", False)):
        raise ProviderDeniedError(
            "provider_invoke_denied; ABRAXAS_ALLOW_PROVIDER_INVOKE is false"
        )
    return provider.invoke(request)
