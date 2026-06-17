from __future__ import annotations

from core.canonical.json import canonical_hash
from core.scoring.mfdfa_hurst import (
    MFDFA_FIXTURE_SERIES,
    build_mfdfa_hurst_fixture_result,
    compute_detrended_fluctuation,
    compute_hurst_exponent,
    compute_mfdfa_profile,
)


def test_mfdfa_fixture_series_is_deterministic() -> None:
    first = build_mfdfa_hurst_fixture_result()
    second = build_mfdfa_hurst_fixture_result()
    assert first == second
    assert first["mfdfa_hurst_fixture_hash"] == second["mfdfa_hurst_fixture_hash"]


def test_mfdfa_profile_contains_hurst_exponent() -> None:
    profile = compute_mfdfa_profile(MFDFA_FIXTURE_SERIES)
    assert profile["series_length"] == len(MFDFA_FIXTURE_SERIES)
    assert len(profile["profile_rows"]) == 3
    assert profile["hurst_exponent"] > 0.0
    assert profile["hurst_exponent"] < 2.0


def test_detrended_fluctuation_increases_with_scale_on_fixture() -> None:
    f4 = compute_detrended_fluctuation(MFDFA_FIXTURE_SERIES, 4)
    f8 = compute_detrended_fluctuation(MFDFA_FIXTURE_SERIES, 8)
    f16 = compute_detrended_fluctuation(MFDFA_FIXTURE_SERIES, 16)
    assert f4 > 0.0
    assert f8 > f4
    assert f16 > f8


def test_hurst_exponent_linear_slope() -> None:
    hurst = compute_hurst_exponent([0.0, 1.0], [0.0, 0.5])
    assert hurst == 0.5


def test_fixture_result_sample_output_fields() -> None:
    fixture = build_mfdfa_hurst_fixture_result()
    assert fixture["telemetry_only"] is True
    assert fixture["decomposition_mode"] == "MFDFA_HURST"
    assert fixture["hurst_exponent"] == fixture["mfdfa_profile"]["hurst_exponent"]
    assert fixture["mfdfa_profile"]["profile_rows"][0]["scale"] == 4
    without_hash = dict(fixture)
    observed = without_hash.pop("mfdfa_hurst_fixture_hash")
    assert canonical_hash(without_hash) == observed
