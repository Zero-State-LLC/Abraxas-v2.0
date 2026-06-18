from __future__ import annotations

import os
from enum import Enum


class HygieneMode(str, Enum):
    OFF = "OFF"
    ADVISORY = "ADVISORY"
    STRICT = "STRICT"

    @classmethod
    def from_string(cls, value: str | None) -> "HygieneMode":
        if value is None or not value.strip():
            return cls.ADVISORY
        normalized = value.strip().upper()
        try:
            return cls(normalized)
        except ValueError as exc:
            raise ValueError(f"invalid hygiene mode: {value}") from exc


def resolve_hygiene_mode(env: os._Environ[str] | None = None) -> HygieneMode:
    source = os.environ if env is None else env
    return HygieneMode.from_string(source.get("ABX_V2_HYGIENE_MODE"))
