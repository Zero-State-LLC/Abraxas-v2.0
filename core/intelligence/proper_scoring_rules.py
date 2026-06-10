from typing import Any, Dict, List
import math


def log_score(predictions: List[float], targets: List[float], eps: float = 1e-15) -> float:
    """
    Logarithmic scoring rule (also called Ignorance Score).
    Lower is better. Proper scoring rule.
    """
    if len(predictions) != len(targets) or not predictions:
        return float('nan')

    score = 0.0
    for p, t in zip(predictions, targets):
        p = max(min(p, 1 - eps), eps)  # avoid log(0)
        score += t * math.log(p) + (1 - t) * math.log(1 - p)
    return -score / len(predictions)  # negative log likelihood style


def spherical_score(predictions: List[float], targets: List[float]) -> float:
    """
    Spherical scoring rule.
    Higher is better. Proper scoring rule.
    """
    if len(predictions) != len(targets) or not predictions:
        return float('nan')

    score = 0.0
    for p, t in zip(predictions, targets):
        # Spherical score: t * p / ||p||
        norm = math.sqrt(p**2 + (1-p)**2)
        score += t * (p / norm) if norm > 0 else 0
    return score / len(predictions)


def get_proper_scoring_summary(
    predictions: List[float],
    targets: List[float]
) -> Dict[str, Any]:
    """Returns multiple proper scoring rules in one call."""
    return {
        "log_score": log_score(predictions, targets),
        "spherical_score": spherical_score(predictions, targets),
        "brier_score": sum((p - t)**2 for p, t in zip(predictions, targets)) / len(predictions)
    }
