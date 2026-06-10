from typing import Any, Dict, List
import math

class PlattScalingCalibrator:
    """
    Platt Scaling for probability calibration.
    Fits a logistic regression on scores to map them to calibrated probabilities.
    Simple gradient descent implementation (no external libs).
    """

    def __init__(self, max_iter: int = 100, learning_rate: float = 0.1):
        self.max_iter = max_iter
        self.learning_rate = learning_rate
        self.provenance = {
            "module": "PlattScalingCalibrator",
            "version": "2.2.0",
            "sprint": "Sprint 5",
            "method": "platt_scaling"
        }
        self.A = 0.0  # weight
        self.B = 0.0  # bias
        self._fitted = False

    def _sigmoid(self, z: float) -> float:
        return 1.0 / (1.0 + math.exp(-max(min(z, 500), -500)))

    def fit(self, scores: List[float], targets: List[float]) -> Dict[str, Any]:
        if len(scores) != len(targets):
            raise ValueError("scores and targets must have same length")

        self.A = 0.0
        self.B = 0.0

        for _ in range(self.max_iter):
            grad_A = 0.0
            grad_B = 0.0

            for s, t in zip(scores, targets):
                z = self.A * s + self.B
                p = self._sigmoid(z)
                error = p - t
                grad_A += error * s
                grad_B += error

            self.A -= self.learning_rate * grad_A / len(scores)
            self.B -= self.learning_rate * grad_B / len(scores)

        self._fitted = True
        return {
            "status": "fitted",
            "n_samples": len(scores),
            "A": self.A,
            "B": self.B,
            "provenance": self.provenance
        }

    def predict(self, scores: List[float]) -> List[float]:
        if not self._fitted:
            return [self._sigmoid(s) for s in scores]

        return [self._sigmoid(self.A * s + self.B) for s in scores]

    def calibrate(self, scores: List[float]) -> Dict[str, Any]:
        calibrated = self.predict(scores)
        return {
            "calibrated_scores": calibrated,
            "provenance": self.provenance
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "fitted": self._fitted,
            "A": self.A,
            "B": self.B,
            "provenance": self.provenance
        }
