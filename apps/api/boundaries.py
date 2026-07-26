"""Service integration boundaries (authn / rate-limit) — hooks only.

These are not product auth implementations. They define fail-closed seams for
future adapters without granting EXTERNAL_PRODUCTION authority.
"""

from __future__ import annotations

from fastapi import HTTPException, Request

from apps.api.settings import get_settings


def check_authentication_boundary(request: Request) -> None:
    """Authn integration boundary.

    Default: allow anonymous for LOCAL_DEV/SANDBOX API use.
    When ``ABRAXAS_REQUIRE_AUTH=true`` (settings.require_auth), deny until a
    real authenticator is wired — fail closed.
    """
    settings = get_settings()
    require_auth = bool(getattr(settings, "require_auth", False))
    if not require_auth:
        return
    # Placeholder: no authenticator wired yet.
    authorization = request.headers.get("authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="authentication_required")
    raise HTTPException(status_code=501, detail="authenticator_not_configured")


def check_rate_limit_boundary(request: Request) -> None:
    """Rate-limit integration boundary.

    Default: allow. When ``require_rate_limit`` is enabled, deny until a limiter
    adapter is configured — fail closed rather than silent unlimited traffic.
    """
    settings = get_settings()
    require_rate_limit = bool(getattr(settings, "require_rate_limit", False))
    if not require_rate_limit:
        return
    raise HTTPException(status_code=501, detail="rate_limiter_not_configured")
