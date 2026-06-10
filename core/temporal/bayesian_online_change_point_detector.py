from typing import Any, Dict, List
import numpy as np

class BayesianOnlineChangePointDetector:
    """
    Bayesian Online Change Point Detection (BOCPD) for regime/shift detection.
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
        # Simplified BOCPD logic
        self.run_length += 1
        is_change = np.random.rand() < self.hazard  # placeholder probability

        if is_change:
            self.change_points.append(self.run_length)
            self.run_length = 0

        return {
            "run_length": self.run_length,
            "is_change_point": is_change,
            "change_points": self.change_points,
            "provenance": self.provenance
        }

    def get_change_points(self) -> List[int]:
        return self.change_points
