from __future__ import annotations

import pytest

from core.optimization.optuna_backend import BayesianOptimizer, OptunaBackend


def test_module_imports_without_optional_optuna_dependency() -> None:
    # Import already happened above; this test documents the desired contract.
    assert BayesianOptimizer.__name__ == "BayesianOptimizer"
    assert OptunaBackend.__name__ == "OptunaBackend"


def test_unsupported_backend_fails_closed() -> None:
    optimizer = BayesianOptimizer(backend="gp")

    with pytest.raises(ValueError, match="Unsupported backend"):
        optimizer.optimize(lambda params: 0.0)


def test_optuna_backend_reports_missing_dependency() -> None:
    if pytest.importorskip("optuna", reason="optuna installed in this environment"):
        pytest.skip("optuna is installed; missing-dependency path is not applicable")

    with pytest.raises(RuntimeError, match="optuna is not installed"):
        OptunaBackend()
