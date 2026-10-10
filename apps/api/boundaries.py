"""Reference access policy for the compute endpoint (POST /analyze).

This is doctrine reference code, not a supported deployment: the supported
runtime is Zero-State-LLC/Abraxas. The policy it expresses:

- Authenticated by default. Callers send ``X-ABX-Token`` (the header the
  canonical runtime uses), compared in constant time with the configured
  ``ABRAXAS_API_TOKEN``. With no token configured the endpoint fails closed.
- Anonymous access needs ``ABRAXAS_ALLOW_ANONYMOUS_LOCAL_DEV=true`` *and*
  ``ABRAXAS_DEPLOYMENT_PROFILE=local`` (settings refuse the flag under any other
  profile) *and* a loopback client, so the flag cannot open a deployed service.
- Rate limited per principal; request bodies and execution time are bounded.
- Credentials never appear in responses or logs: principals are identified by
  a short token fingerprint, and errors carry fixed detail strings.
"""

from __future__ import annotations

import hashlib
import ipaddress
import secrets
import threading
import time
from collections import deque
from collections.abc import Callable

from fastapi import HTTPException, Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from apps.api.settings import get_settings

TOKEN_HEADER = "x-abx-token"
LOCAL_PROFILE = "local"


def _is_loopback(host: str | None) -> bool:
    if not host:
        return False
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _fingerprint(token: str) -> str:
    return "token:" + hashlib.sha256(token.encode("utf-8")).hexdigest()[:16]


def check_authentication_boundary(request: Request) -> str:
    """Authenticate the caller and return its principal id (never the token)."""
    settings = get_settings()
    supplied = request.headers.get(TOKEN_HEADER)
    expected = settings.api_token.get_secret_value() if settings.api_token else None

    if supplied is not None:
        if expected is None:
            raise HTTPException(status_code=503, detail="api_auth_not_configured")
        if not secrets.compare_digest(supplied.encode("utf-8"), expected.encode("utf-8")):
            raise HTTPException(status_code=401, detail="invalid_credentials")
        principal = _fingerprint(supplied)
    else:
        client_host = request.client.host if request.client else None
        anonymous_ok = (
            settings.allow_anonymous_local_dev
            and settings.deployment_profile == LOCAL_PROFILE
            and _is_loopback(client_host)
        )
        if not anonymous_ok:
            if expected is None and not settings.allow_anonymous_local_dev:
                raise HTTPException(status_code=503, detail="api_auth_not_configured")
            raise HTTPException(status_code=401, detail="authentication_required")
        principal = f"anonymous-local:{client_host}"

    request.state.principal = principal
    return principal


class SlidingWindowRateLimiter:
    """In-process per-principal limiter (reference only: one process, no sharing)."""

    def __init__(
        self,
        limit: int,
        window_seconds: float = 60.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._clock = clock
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def acquire(self, principal: str) -> float | None:
        """Record a hit; return None if allowed, else seconds until a slot frees."""
        now = self._clock()
        with self._lock:
            hits = self._hits.setdefault(principal, deque())
            while hits and now - hits[0] >= self.window_seconds:
                hits.popleft()
            if len(hits) >= self.limit:
                return self.window_seconds - (now - hits[0])
            hits.append(now)
            return None


def check_rate_limit_boundary(request: Request) -> None:
    """Apply the per-principal rate limit (runs after authentication)."""
    limiter: SlidingWindowRateLimiter | None = getattr(
        request.app.state, "analyze_rate_limiter", None
    )
    if limiter is None:
        raise HTTPException(status_code=503, detail="rate_limiter_not_configured")
    principal = getattr(request.state, "principal", None) or "unknown"
    retry_after = limiter.acquire(principal)
    if retry_after is not None:
        raise HTTPException(
            status_code=429,
            detail="rate_limited",
            headers={"Retry-After": str(max(1, int(retry_after + 0.999)))},
        )


class BodySizeLimitMiddleware:
    """Reject request bodies larger than ``max_bytes`` before they are parsed."""

    def __init__(self, app: ASGIApp, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        for name, value in scope.get("headers", []):
            if name == b"content-length":
                try:
                    declared = int(value)
                except ValueError:
                    declared = self.max_bytes + 1
                if declared > self.max_bytes:
                    await _send_too_large(send)
                    return

        received = 0

        async def limited_receive() -> Message:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_bytes:
                    raise _BodyTooLarge
            return message

        try:
            await self.app(scope, limited_receive, send)
        except _BodyTooLarge:
            await _send_too_large(send)


class _BodyTooLarge(Exception):
    pass


async def _send_too_large(send: Send) -> None:
    body = b'{"detail":"request_body_too_large"}'
    await send(
        {
            "type": "http.response.start",
            "status": 413,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode()),
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})
