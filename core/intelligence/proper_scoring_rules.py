from typing import Any, Dict, List
import math


def log_score(
    predictions: List[float],
    targets: List[float],
    eps: float = 1e-15,
    multiclass: bool = False
) -> float:
    """
    Logarithmic Scoring Rule (also called Ignorance Score or Log Score).

    Properties:
    - Strictly proper scoring rule
    - Heavily penalizes confident but wrong predictions
    - Lower values are better
    - Related to cross-entropy / negative log-likelihood

    For binary case:
        score = - (t * log(p) + (1-t) * log(1-p))

    For multiclass:
        score = - sum(t_i * log(p_i))
    """
    if len(predictions) != len(targets) or not predictions:
        return float('nan')

    total = 0.0
    n = len(predictions)

    if multiclass:
        # Assume predictions and targets are lists of lists for multiclass
        for pred_row, target_row in zip(predictions, targets):
            for p, t in zip(pred_row, target_row):
                p_safe = max(min(p, 1 - eps), eps)
                total += t * math.log(p_safe)
        return -total / n
    else:
        for p, t in zip(predictions, targets):
            p_safe = max(min(p, 1 - eps), eps)
            total += t * math.log(p_safe) + (1 - t) * math.log(1 - p_safe)
        return -total / n


def spherical_score(predictions: List[float], targets: List[float]) -> float:
    if len(predictions) != len(targets) or not predictions:
        return float('nan')

    score = 0.0
    for p, t in zip(predictions, targets):
        norm = math.sqrt(p**2 + (1 - p)**2)
        score += t * (p / norm) if norm > 0 else 0
    return score / len(predictions)


def get_proper_scoring_summary(
    predictions: List[float],
    targets: List[float]
) -> Dict[str, Any]:
    return {
        "log_score": log_score(predictions, targets),
        "spherical_score": spherical_score(predictions, targets),
        "brier_score": sum((p - t)**2 for p, t in zip(predictions, targets)) / len(predictions)
    }
