"""ASGI middleware for request IDs and baseline security headers."""

from __future__ import annotations

import re
import secrets
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Client-supplied request IDs are echoed back, so accept only short tokens.
_REQUEST_ID_PATTERN = re.compile(r"[A-Za-z0-9._:-]{1,128}")


def _request_id(request: Request) -> str:
    supplied = request.headers.get("x-request-id")
    if supplied and _REQUEST_ID_PATTERN.fullmatch(supplied):
        return supplied
    return secrets.token_hex(8)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = _request_id(request)
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response
