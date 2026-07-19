"""Canonical service layer (WS3) — versioned facades over kernel capabilities."""

from core.services.validation_service import (
    SERVICE_ID,
    SERVICE_VERSION,
    validate,
)

__all__ = ["SERVICE_ID", "SERVICE_VERSION", "validate"]
