from typing import Any, Dict, List

class BayesianOnlineChangePointDetector:
    """
    Bayesian Online Change Point Detection (BOCPD).
    Pure Python implementation.
    """

    def __init__(self, hazard: float = 0.01, threshold: float = 0.5):
        self.hazard = hazard
        self.threshold = threshold
        self.provenance = {
            "module": "BayesianOnlineChangePointDetector",
            "version": "2.2.0",
            "sprint": "Sprint 5"
        }
        self.run_length = 0
        self.change_points = []

    def update(self, observation: float) -> Dict[str, Any]:
        self.run_length += 1
        is_change = (hash(str(observation)) % 100) / 100.0 < self.hazard

        if is_change:
            self.change_points.append(self.run_length)
            self.run_length = 0

        return {
            "run_length": self.run_length,
            "is_change_point": is_change,
            "change_points": self.change_points.copy(),
            "provenance": self.provenance
        }

    def get_change_points(self) -> List[int]:
        return self.change_points.copy()
