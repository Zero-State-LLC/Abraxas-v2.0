from typing import Any, Dict, List

class IsotonicRegressionCalibrator:
    """
    Isotonic Regression for probability / score calibration.
    Monotonic, non-parametric calibration method.
    """

    def __init__(self):
        self.provenance = {
            "module": "IsotonicRegressionCalibrator",
            "version": "2.2.0",
            "sprint": "Sprint 5",
            "method": "isotonic_regression"
        }
        self._x: List[float] = []
        self._y: List[float] = []
        self._fitted = False

    def fit(self, scores: List[float], targets: List[float]) -> Dict[str, Any]:
        """
        Fit isotonic regression on (scores, targets).
        Simple implementation using pool-adjacent-violators style logic.
        """
        if len(scores) != len(targets):
            raise ValueError("scores and targets must have same length")

        # Sort by scores
        paired = sorted(zip(scores, targets))
        self._x = [p[0] for p in paired]
        self._y = [p[1] for p in paired]

        # Basic isotonic adjustment (pool adjacent violators)
        for i in range(1, len(self._y)):
            if self._y[i] < self._y[i-1]:
                self._y[i] = self._y[i-1]

        self._fitted = True
        return {
            "status": "fitted",
            "n_samples": len(scores),
            "provenance": self.provenance
        }

    def predict(self, scores: List[float]) -> List[float]:
        if not self._fitted:
            return scores  # return raw if not fitted

        calibrated = []
        for s in scores:
            # Simple linear interpolation between nearest points
            if s <= self._x[0]:
                calibrated.append(self._y[0])
            elif s >= self._x[-1]:
                calibrated.append(self._y[-1])
            else:
                for j in range(len(self._x)-1):
                    if self._x[j] <= s <= self._x[j+1]:
                        # linear interpolation
                        weight = (s - self._x[j]) / (self._x[j+1] - self._x[j]) if self._x[j+1] != self._x[j] else 0
                        val = self._y[j] + weight * (self._y[j+1] - self._y[j])
                        calibrated.append(val)
                        break
        return calibrated

    def calibrate(self, scores: List[float]) -> Dict[str, Any]:
        calibrated_scores = self.predict(scores)
        return {
            "calibrated_scores": calibrated_scores,
            "provenance": self.provenance
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "fitted": self._fitted,
            "n_points": len(self._x),
            "provenance": self.provenance
        }
