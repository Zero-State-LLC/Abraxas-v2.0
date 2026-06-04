from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CadenceBounds:
    base_seconds: int
    min_seconds: int
    max_seconds: int


def clamp_int(value: float, minimum: int, maximum: int) -> int:
    if minimum <= 0 or maximum <= 0:
        raise ValueError("cadence_bounds_must_be_positive")
    if minimum > maximum:
        raise ValueError("minimum_cannot_exceed_maximum")
    return int(max(minimum, min(maximum, round(value))))


def resolve_cadence_seconds(
    bounds: CadenceBounds,
    *,
    quiet_window_multiplier: float = 1.0,
    volatility_multiplier: float = 1.0,
) -> int:
    if bounds.base_seconds <= 0:
        raise ValueError("base_seconds_must_be_positive")
    if quiet_window_multiplier <= 0 or volatility_multiplier <= 0:
        raise ValueError("cadence_multipliers_must_be_positive")

    raw = bounds.base_seconds * quiet_window_multiplier * volatility_multiplier
    return clamp_int(raw, bounds.min_seconds, bounds.max_seconds)
