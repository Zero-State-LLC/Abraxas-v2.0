from __future__ import annotations

import math
from typing import Any

from core.canonical.json import canonical_hash

NOT_COMPUTABLE = "NOT_COMPUTABLE"
ROUNDING_POLICY = "ROUND_10_DP"

# Deterministic fixture series (cumulative profile of fixed increments).
MFDFA_FIXTURE_INCREMENTS = (
    0.12,
    -0.04,
    0.09,
    0.03,
    -0.07,
    0.11,
    -0.02,
    0.06,
    0.08,
    -0.05,
    0.1,
    0.04,
    -0.03,
    0.07,
    0.05,
    -0.06,
    0.09,
    0.02,
    -0.04,
    0.08,
    0.06,
    -0.01,
    0.05,
    0.03,
    -0.08,
    0.1,
    0.04,
    -0.02,
    0.07,
    0.06,
    -0.05,
    0.09,
)

MFDFA_DEFAULT_Q_VALUES = (2.0,)
MFDFA_DEFAULT_SCALES = (4, 8, 16)


def _round_value(value: float) -> float:
    return round(value, 10)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def build_mfdfa_fixture_series() -> tuple[float, ...]:
    profile: list[float] = []
    total = 0.0
    for increment in MFDFA_FIXTURE_INCREMENTS:
        total += increment
        profile.append(total)
    return tuple(profile)


MFDFA_FIXTURE_SERIES = build_mfdfa_fixture_series()


def _linear_trend_residuals(segment: list[float]) -> list[float]:
    n = len(segment)
    if n < 2:
        return [0.0 for _ in segment]
    x_mean = (n - 1) / 2.0
    y_mean = _mean(segment)
    numerator = sum((index - x_mean) * (value - y_mean) for index, value in enumerate(segment))
    denominator = sum((index - x_mean) ** 2 for index in range(n))
    slope = numerator / denominator if denominator else 0.0
    intercept = y_mean - slope * x_mean
    return [value - (intercept + slope * index) for index, value in enumerate(segment)]


def compute_detrended_fluctuation(series: tuple[float, ...] | list[float], scale: int) -> float:
    if scale < 2 or len(series) < scale:
        return 0.0
    mean_value = _mean(list(series))
    integrated = [value - mean_value for value in series]
    cumulative: list[float] = []
    running = 0.0
    for value in integrated:
        running += value
        cumulative.append(running)
    variances: list[float] = []
    segment_count = len(cumulative) // scale
    for segment_index in range(segment_count):
        start = segment_index * scale
        segment = cumulative[start : start + scale]
        residuals = _linear_trend_residuals(segment)
        variances.append(_mean([residual * residual for residual in residuals]))
    if not variances:
        return 0.0
    return _round_value(math.sqrt(_mean(variances)))


def compute_hurst_exponent(log_scales: list[float], log_fluctuations: list[float]) -> float:
    if len(log_scales) < 2 or len(log_scales) != len(log_fluctuations):
        return 0.0
    x_mean = _mean(log_scales)
    y_mean = _mean(log_fluctuations)
    numerator = sum(
        (x_value - x_mean) * (y_value - y_mean)
        for x_value, y_value in zip(log_scales, log_fluctuations)
    )
    denominator = sum((x_value - x_mean) ** 2 for x_value in log_scales)
    if denominator == 0.0:
        return 0.0
    return _round_value(numerator / denominator)


def compute_mfdfa_profile(
    series: tuple[float, ...] | list[float],
    *,
    q_values: tuple[float, ...] = MFDFA_DEFAULT_Q_VALUES,
    scales: tuple[int, ...] = MFDFA_DEFAULT_SCALES,
) -> dict[str, Any]:
    profile_rows: list[dict[str, Any]] = []
    log_scales: list[float] = []
    log_fluctuations: list[float] = []
    for scale in scales:
        fluctuation = compute_detrended_fluctuation(series, scale)
        row: dict[str, Any] = {
            "scale": scale,
            "fluctuation": fluctuation,
        }
        for q_value in q_values:
            if q_value == 2.0:
                row[f"fq_q{str(q_value).replace('.', '_')}"] = fluctuation
        profile_rows.append(row)
        if fluctuation > 0.0:
            log_scales.append(_round_value(math.log(float(scale))))
            log_fluctuations.append(_round_value(math.log(fluctuation)))
    hurst_exponent = compute_hurst_exponent(log_scales, log_fluctuations)
    return {
        "series_length": len(series),
        "q_values": list(q_values),
        "scales": list(scales),
        "profile_rows": profile_rows,
        "log_scales": log_scales,
        "log_fluctuations": log_fluctuations,
        "hurst_exponent": hurst_exponent,
        "rounding_policy": ROUNDING_POLICY,
    }


def build_mfdfa_hurst_fixture_result() -> dict[str, Any]:
    profile = compute_mfdfa_profile(MFDFA_FIXTURE_SERIES)
    packet: dict[str, Any] = {
        "contract_id": "v2_scoring_mfdfa_hurst_fixture_result_001",
        "telemetry_only": True,
        "fixture_series": list(MFDFA_FIXTURE_SERIES),
        "fixture_increments": list(MFDFA_FIXTURE_INCREMENTS),
        "mfdfa_profile": profile,
        "hurst_exponent": profile["hurst_exponent"],
        "decomposition_mode": "MFDFA_HURST",
        "resolution_allowed": False,
        "mfdfa_hurst_fixture_hash": "",
    }
    packet["mfdfa_hurst_fixture_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "mfdfa_hurst_fixture_hash"}
    )
    return packet
