"""Safe exception mapping — never leak stack traces to external clients."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.exception(
            "unhandled_api_error",
            extra={"request_id": request_id, "path": str(request.url.path)},
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "internal_error",
                "request_id": request_id,
            },
        )
