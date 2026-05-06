"""Tests for core/governance/authority.py"""

from __future__ import annotations

import pytest

from core.governance.authority import Authority, locked_authority


def test_all_false_passes():
    auth = Authority()
    auth.assert_locked()  # should not raise


def test_forbidden_true_flags_empty_when_all_false():
    auth = Authority()
    assert auth.forbidden_true_flags() == []


def test_any_true_flag_raises_on_construction():
    with pytest.raises(Exception):
        Authority(promotion_allowed=True)


def test_forecast_weight_allowed_true_raises():
    with pytest.raises(Exception):
        Authority(forecast_weight_allowed=True)


def test_runtime_mutation_allowed_true_raises():
    with pytest.raises(Exception):
        Authority(runtime_mutation_allowed=True)


def test_baseline_mutation_allowed_true_raises():
    with pytest.raises(Exception):
        Authority(baseline_mutation_allowed=True)


def test_canon_mutation_allowed_true_raises():
    with pytest.raises(Exception):
        Authority(canon_mutation_allowed=True)


def test_aal_viz_inference_authority_true_raises():
    with pytest.raises(Exception):
        Authority(aal_viz_inference_authority=True)


def test_locked_authority_returns_all_false():
    la = locked_authority()
    assert all(v is False for v in la.values())


def test_locked_authority_has_all_fields():
    la = locked_authority()
    expected_keys = {
        "promotion_allowed",
        "forecast_weight_allowed",
        "runtime_mutation_allowed",
        "baseline_mutation_allowed",
        "canon_mutation_allowed",
        "aal_viz_inference_authority",
    }
    assert set(la.keys()) == expected_keys
