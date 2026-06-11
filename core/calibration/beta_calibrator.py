from typing import Any, Dict, List

class BetaCalibrator:
    """
    Beta Calibration for probability scores.
    Maps scores using a Beta distribution (more flexible than Platt).
    Simple moment-matching implementation.
    """

    def __init__(self):
        self.provenance = {
            "module": "BetaCalibrator",
            "version": "2.2.0",
            "sprint": "Sprint 5",
            "method": "beta_calibration"
        }
        self.alpha = 1.0
        self.beta = 1.0
        self._fitted = False

    def fit(self, scores: List[float], targets: List[float]) -> Dict[str, Any]:
        if len(scores) != len(targets):
            raise ValueError("scores and targets must have same length")

        # Simple moment matching for Beta parameters
        mean_score = sum(scores) / len(scores)
        var_score = sum((s - mean_score)**2 for s in scores) / len(scores)

        if var_score > 0:
            self.alpha = mean_score * ((mean_score * (1 - mean_score) / var_score) - 1)
            self.beta = (1 - mean_score) * ((mean_score * (1 - mean_score) / var_score) - 1)
        else:
            self.alpha = 2.0
            self.beta = 2.0

        self.alpha = max(self.alpha, 0.1)
        self.beta = max(self.beta, 0.1)

        self._fitted = True
        return {
            "status": "fitted",
            "alpha": self.alpha,
            "beta": self.beta,
            "provenance": self.provenance
        }

    def predict(self, scores: List[float]) -> List[float]:
        if not self._fitted:
            return scores

        calibrated = []
        for s in scores:
            # Beta CDF approximation (simple)
            x = max(min(s, 0.999), 0.001)
            # Rough Beta CDF using incomplete beta approximation
            val = (x ** self.alpha) / (x ** self.alpha + (1 - x) ** self.beta)
            calibrated.append(val)
        return calibrated

    def calibrate(self, scores: List[float]) -> Dict[str, Any]:
        calibrated = self.predict(scores)
        return {
            "calibrated_scores": calibrated,
            "provenance": self.provenance
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "fitted": self._fitted,
            "alpha": self.alpha,
            "beta": self.beta,
            "provenance": self.provenance
        }
