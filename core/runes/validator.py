"""Rune validator stub."""

from __future__ import annotations

from core.runes.models import RuneContract


def validate_rune(rune: RuneContract) -> dict[str, object]:
    """Validate a single rune contract; returns a result dict."""
    try:
        rune.authority.assert_locked()
        return {"rune_id": rune.rune_id, "status": "valid"}
    except ValueError as exc:
        return {"rune_id": rune.rune_id, "status": "invalid", "reason": str(exc)}
