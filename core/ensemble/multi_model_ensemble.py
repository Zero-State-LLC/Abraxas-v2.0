from typing import Any, Dict, List, Optional

class MultiModelEnsemble:
    """
    Basic multi-model ensemble for combining detector outputs.
    Supports simple voting and performance-weighted strategies.
    """

    def __init__(self, strategy: str = "weighted"):
        self.strategy = strategy  # 'voting' or 'weighted'
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
        """Update performance history (lower Brier = better)."""
        if name in self.performance_history:
            self.performance_history[name].append(score)
            if len(self.performance_history[name]) > 20:
                self.performance_history[name].pop(0)

            # Update weight based on recent performance (inverse of mean Brier)
            recent = self.performance_history[name][-5:]
            if recent:
                avg_score = sum(recent) / len(recent)
                self.model_weights[name] = max(0.1, 1.0 / (avg_score + 0.01))

    def combine_anomaly_scores(self, model_outputs: Dict[str, List[int]]) -> List[int]:
        """
        Combine anomaly decisions from multiple models.
        model_outputs = {'hdbscan': [0,1,0,...], 'bocpd': [...], ...}
        """
        if not model_outputs:
            return []

        # Get all indices
        all_indices = set()
        for scores in model_outputs.values():
            all_indices.update(range(len(scores)))

        final_scores = []
        for i in all_indices:
            votes = []
            for model_name, scores in model_outputs.items():
                if i < len(scores):
                    weight = self.model_weights.get(model_name, 1.0)
                    votes.append(scores[i] * weight)

            if self.strategy == "voting":
                avg = sum(votes) / len(votes) if votes else 0
                final_scores.append(1 if avg > 0.5 else 0)
            else:  # weighted
                total_weight = sum(self.model_weights.get(m, 1.0) for m in model_outputs.keys())
                if total_weight > 0:
                    weighted_avg = sum(votes) / total_weight
                    final_scores.append(1 if weighted_avg > 0.5 else 0)
                else:
                    final_scores.append(0)

        return final_scores

    def get_status(self) -> Dict[str, Any]:
        return {
            "strategy": self.strategy,
            "model_weights": self.model_weights.copy(),
            "provenance": self.provenance
        }
