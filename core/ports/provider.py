"""Provider adapter port — fail-closed by default; no network at import/construct."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol


class ProviderError(RuntimeError):
    """Base error for provider adapter failures."""


class ProviderDeniedError(ProviderError):
    """Raised when no provider adapter is configured (fail-closed)."""


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
