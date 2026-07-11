"""Abraxas v2.0 Bayesian optimization backend wrapper.

Optuna integration is optional. The module stays importable even when optuna is
not installed so callers can fail closed with a clear backend error instead of a
hard import failure.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

try:
    import optuna
except ImportError:  # pragma: no cover - exercised by environments without optuna
    optuna = None


class OptunaBackend:
    """Optuna wrapper with Abraxas provenance and governance."""

    def __init__(
        self,
        study_name: str = "abraxas_optimization",
        storage: str = "sqlite:///out/optimization/abraxas_optuna.db",
    ) -> None:
        if optuna is None:
            raise RuntimeError(
                "Optuna backend requested but optuna is not installed. "
                "Install the optional dependency or choose a supported backend."
            )

        self.study = optuna.create_study(
            study_name=study_name,
            storage=storage,
            direction="minimize",  # or maximize depending on objective
            sampler=optuna.samplers.TPESampler(),
            pruner=optuna.pruners.MedianPruner(),
        )
        self.trials_history: list[dict[str, Any]] = []

    def optimize(self, objective_fn: Callable[[dict[str, Any]], float], n_trials: int = 20, **kwargs: Any) -> dict[str, Any]:
        """Run Optuna optimization with provenance."""

        def wrapped_objective(trial: Any) -> float:
            params: dict[str, Any] = {}
            # Example dynamic param suggestion - extend as needed
            if "sharpness" in kwargs.get("param_space", {}):
                params["sharpness"] = trial.suggest_float("sharpness", 0.5, 5.0)
            # Add more param spaces as needed
            score = objective_fn(params)
            self.trials_history.append(
                {
                    "trial_number": trial.number,
                    "params": params,
                    "value": score,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            return score

        self.study.optimize(wrapped_objective, n_trials=n_trials)

        best = {
            "best_params": self.study.best_params,
            "best_value": self.study.best_value,
            "n_trials": n_trials,
            "provenance": {
                "timestamp": datetime.now().isoformat(),
                "study_name": self.study.study_name,
                "backend": "optuna_tpe",
            },
        }
        return best


class BayesianOptimizer:
    def __init__(self, backend: str = "optuna") -> None:
        self.backend = backend

    def optimize(self, objective_fn: Callable[[dict[str, Any]], float], **kwargs: Any) -> dict[str, Any]:
        if self.backend == "optuna":
            optuna_backend = OptunaBackend()
            return optuna_backend.optimize(objective_fn, **kwargs)

        raise ValueError(
            f"Unsupported backend '{self.backend}'. Supported backends: ['optuna']"
        )
