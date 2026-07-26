"""Clock port — inject FixedClock in tests; never rely on wall-clock in domain pure paths."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol


class Clock(Protocol):
    def now_utc_iso(self) -> str:
        """Return UTC timestamp as YYYY-MM-DDTHH:MM:SSZ."""


class SystemClock:
    def now_utc_iso(self) -> str:
        return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class FixedClock:
    """Deterministic clock for tests and replay."""

    def __init__(self, instant: str = "1970-01-01T00:00:00Z") -> None:
        self._instant = instant

    def now_utc_iso(self) -> str:
        return self._instant
