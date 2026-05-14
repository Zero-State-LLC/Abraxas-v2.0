"""Deterministic diagnostics helpers for ABRAXAS v2.0."""

from __future__ import annotations

import hashlib
import logging
import sys
from pathlib import Path
from typing import Any, Literal, TextIO

from core.canonical.json import canonical_dumps

Severity = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

_LEVELS: dict[Severity, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def _normalize_path(value: str | Path) -> str:
    if isinstance(value, Path):
        return value.as_posix()
    return str(value)


def stable_correlation_id(
    namespace: str,
    *,
    artifact_path: str | Path | None = None,
    context: Any | None = None,
) -> str:
    basis: dict[str, Any] = {"namespace": namespace}
    if artifact_path is not None:
        basis["artifact_path"] = _normalize_path(artifact_path)
    if context is not None:
        basis["context"] = context
    digest = hashlib.sha256(canonical_dumps(basis).encode("utf-8")).hexdigest()[:16]
    return f"{namespace}:{digest}"


def build_event(event: str, severity: Severity, **fields: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"event": event, "severity": severity}
    for key, value in fields.items():
        if value is not None:
            payload[key] = value
    return payload


def format_event(event: str, severity: Severity, **fields: Any) -> str:
    return canonical_dumps(build_event(event, severity, **fields))


def log_event(
    logger: logging.Logger,
    severity: Severity,
    event: str,
    *,
    exc_info: bool = False,
    **fields: Any,
) -> str:
    message = format_event(event, severity, **fields)
    logger.log(_LEVELS[severity], message, exc_info=exc_info)
    return message


def get_structured_logger(
    name: str,
    *,
    stream: TextIO | None = None,
    level: int = logging.INFO,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    target_stream = stream if stream is not None else sys.stdout
    if logger.handlers:
        handler = logger.handlers[0]
        if isinstance(handler, logging.StreamHandler) and handler.stream is not target_stream:
            logger.removeHandler(handler)
            handler = logging.StreamHandler(target_stream)
            handler.setFormatter(logging.Formatter("%(message)s"))
            logger.addHandler(handler)
        else:
            handler.setFormatter(logging.Formatter("%(message)s"))
        return logger

    handler = logging.StreamHandler(target_stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

    return logger
