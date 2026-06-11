from typing import Any, Dict, List
import math

class MultiModelEnsemble:
    """
    Multi-model ensemble supporting multiple strategies including Bayesian Model Averaging.
    """

    def __init__(self, strategy: str = "weighted"):
        self.strategy = strategy  # 'voting', 'weighted', or 'bma'
        self.model_weights: Dict[str, float] = {}
        self.performance_history: Dict[str, List[float]] = {}
        self.provenance = {
            "module": "MultiModelEnsemble",
            "version": "2.2.0",
            "sprint": "Sprint 5"
        }

    def register_model(self, name: str, initial_weight: float = 1.0):
        self.model_weights[name] = initial_weight
        self.performance_history[name] = []

    def update_model_performance(self, name: str, score: float):
        """Update performance (lower is better, e.g. Brier score)."""
        if name in self.performance_history:
            self.performance_history[name].append(score)
            if len(self.performance_history[name]) > 30:
                self.performance_history[name].pop(0)

            # Update weights based on strategy
            if self.strategy == "bma":
                self._update_bma_weights()
            elif self.strategy == "weighted":
                recent = self.performance_history[name][-5:]
                if recent:
                    avg_score = sum(recent) / len(recent)
                    self.model_weights[name] = max(0.05, 1.0 / (avg_score + 0.01))

    def _update_bma_weights(self):
        """Bayesian Model Averaging style weight update."""
        if not self.performance_history:
            return

        # Approximate posterior model probability using exponential of negative Brier
        # (lower Brier = higher posterior probability)
        log_posteriors = {}
        for name, scores in self.performance_history.items():
            if scores:
                recent_avg = sum(scores[-10:]) / min(len(scores), 10)
                # Negative Brier as log-likelihood proxy
                log_posteriors[name] = -recent_avg
            else:
                log_posteriors[name] = 0.0

        # Normalize to get posterior probabilities (softmax)
        max_log = max(log_posteriors.values()) if log_posteriors else 0
        exp_values = {name: math.exp(lp - max_log) for name, lp in log_posteriors.items()}
        total = sum(exp_values.values())

        if total > 0:
            for name in self.model_weights:
                self.model_weights[name] = exp_values.get(name, 0.0) / total

    def combine_anomaly_scores(self, model_outputs: Dict[str, List[int]]) -> List[int]:
        if not model_outputs:
            return []

        all_indices = set()
        for scores in model_outputs.values():
            all_indices.update(range(len(scores)))

        final_scores = []
        for i in all_indices:
            votes = []
            weights = []
            for model_name, scores in model_outputs.items():
                if i < len(scores):
                    weight = self.model_weights.get(model_name, 1.0)
                    votes.append(scores[i] * weight)
                    weights.append(weight)

            if self.strategy in ["weighted", "bma"]:
                total_weight = sum(weights) if weights else 1
                if total_weight > 0:
                    weighted_avg = sum(votes) / total_weight
                    final_scores.append(1 if weighted_avg > 0.5 else 0)
                else:
                    final_scores.append(0)
            else:  # voting
                avg = sum(votes) / len(votes) if votes else 0
                final_scores.append(1 if avg > 0.5 else 0)

        return final_scores

    def get_status(self) -> Dict[str, Any]:
        return {
            "strategy": self.strategy,
            "model_weights": self.model_weights.copy(),
            "provenance": self.provenance
        }
