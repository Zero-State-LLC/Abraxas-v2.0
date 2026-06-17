from __future__ import annotations

from core.scoring.brier import (
    DECOMPOSITION_MODE,
    NOT_COMPUTABLE,
    compute_brier_score,
    compute_full_decomposition,
    compute_murphy_decomposition,
    compute_yates_decomposition,
)

FIXTURE_PREDICTIONS = [0.7, 0.8, 0.6]
FIXTURE_TARGETS = [1.0, 0.0, 1.0]


def test_murphy_identity_on_fixture() -> None:
    murphy = compute_murphy_decomposition(FIXTURE_PREDICTIONS, FIXTURE_TARGETS)
    mean_brier = sum(
        compute_brier_score(prediction, target)
        for prediction, target in zip(FIXTURE_PREDICTIONS, FIXTURE_TARGETS)
    ) / len(FIXTURE_PREDICTIONS)
    assert murphy["reliability"] != NOT_COMPUTABLE
    assert murphy["brier_score"] == round(
        float(murphy["reliability"]) - float(murphy["resolution"]) + float(murphy["uncertainty"]),
        10,
    )
    assert abs(float(murphy["brier_score"]) - mean_brier) < 1e-9


def test_yates_component_sum_identity() -> None:
    yates = compute_yates_decomposition(FIXTURE_PREDICTIONS, FIXTURE_TARGETS)
    mean_brier = sum(
        compute_brier_score(prediction, target)
        for prediction, target in zip(FIXTURE_PREDICTIONS, FIXTURE_TARGETS)
    ) / len(FIXTURE_PREDICTIONS)
    component_sum = (
        float(yates["bias_squared"])
        + float(yates["excess_variance"])
        + float(yates["covariance_deficit"])
    )
    assert abs(component_sum - float(yates["brier_score"])) < 1e-9
    assert abs(float(yates["brier_score"]) - mean_brier) < 1e-9


def test_compute_full_decomposition_returns_both_branches() -> None:
    full = compute_full_decomposition(FIXTURE_PREDICTIONS, FIXTURE_TARGETS)
    assert full["decomposition_mode"] == DECOMPOSITION_MODE
    assert set(full["murphy"]) == {"reliability", "resolution", "uncertainty", "brier_score"}
    assert set(full["yates"]) == {
        "bias_squared",
        "excess_variance",
        "covariance_deficit",
        "brier_score",
    }


def test_empty_input_fail_closed() -> None:
    murphy = compute_murphy_decomposition([], [])
    yates = compute_yates_decomposition([], [])
    full = compute_full_decomposition([], [])
    assert murphy["brier_score"] == NOT_COMPUTABLE
    assert yates["brier_score"] == NOT_COMPUTABLE
    assert full["murphy"]["brier_score"] == NOT_COMPUTABLE
    assert full["yates"]["brier_score"] == NOT_COMPUTABLE


def test_mismatched_lengths_fail_closed() -> None:
    murphy = compute_murphy_decomposition([0.5], [1.0, 0.0])
    assert murphy["brier_score"] == NOT_COMPUTABLE
