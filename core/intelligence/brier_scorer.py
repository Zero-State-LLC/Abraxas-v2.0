from typing import Any, Dict, List


class BrierScorer:
    """
    Dedicated component for Brier score tracking and summary.
    """

    def __init__(self):
        self.scores: List[float] = []
        self.targets: List[float] = []

    def update(self, prediction: float, target: float) -> float:
        brier = (prediction - target) ** 2
        self.scores.append(brier)
        self.targets.append(target)
        return brier

    def get_summary(self) -> Dict[str, Any]:
        if not self.scores:
            return {"status": "no_scores_yet"}
        return {
            "n_scores": len(self.scores),
            "mean_brier": sum(self.scores) / len(self.scores),
            "latest_brier": self.scores[-1],
            "min_brier": min(self.scores),
            "max_brier": max(self.scores),
        }

    def reset(self):
        self.scores.clear()
        self.targets.clear()
