from typing import Any, Dict, List, Optional

try:
    from core.intelligence.brier_variants import (
        brier_score,
        brier_skill_score,
        brier_decomposition,
        get_brier_variants_summary,
    )
    from core.intelligence.proper_scoring_rules import (
        log_score,
        spherical_score,
    )
except ImportError:
    brier_score = None
    brier_skill_score = None
    brier_decomposition = None
    get_brier_variants_summary = None
    log_score = None
    spherical_score = None


class BrierScorer:
    """
    Comprehensive scorer supporting Brier variants + proper scoring rules (Log, Spherical).
    """

    def __init__(self):
        self.scores: List[float] = []
        self.targets: List[float] = []
        self.predictions: List[float] = []

    def update(self, prediction: float, target: float) -> float:
        brier = (prediction - target) ** 2
        self.scores.append(brier)
        self.targets.append(target)
        self.predictions.append(prediction)
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

    def get_skill_score(self, reference_predictions: Optional[List[float]] = None) -> float:
        if brier_skill_score is None or not self.predictions:
            return float('nan')
        return brier_skill_score(self.predictions, self.targets, reference_predictions)

    def get_decomposition(self) -> Dict[str, float]:
        if brier_decomposition is None or not self.predictions:
            return {}
        return brier_decomposition(self.predictions, self.targets)

    def get_log_score(self) -> float:
        if log_score is None or not self.predictions:
            return float('nan')
        return log_score(self.predictions, self.targets)

    def get_spherical_score(self) -> float:
        if spherical_score is None or not self.predictions:
            return float('nan')
        return spherical_score(self.predictions, self.targets)

    def get_full_variants(self) -> Dict[str, Any]:
        if get_brier_variants_summary is None or not self.predictions:
            return {}
        variants = get_brier_variants_summary(self.predictions, self.targets)
        # Add proper scoring rules
        variants["log_score"] = self.get_log_score()
        variants["spherical_score"] = self.get_spherical_score()
        return variants

    def reset(self):
        self.scores.clear()
        self.targets.clear()
        self.predictions.clear()
