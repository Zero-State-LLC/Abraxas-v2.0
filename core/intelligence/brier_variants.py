from typing import Any, Dict, List, Optional
import math


def brier_score(predictions: List[float], targets: List[float]) -> float:
    """Standard Brier Score (mean squared error)."""
    if len(predictions) != len(targets) or not predictions:
        return float('nan')
    return sum((p - t) ** 2 for p, t in zip(predictions, targets)) / len(predictions)


def brier_skill_score(
    predictions: List[float],
    targets: List[float],
    reference_predictions: Optional[List[float]] = None
) -> float:
    """
    Brier Skill Score (BSS).
    Compares forecast Brier score against a reference (default = mean target as climatology).
    BSS > 0 means better than reference.
    """
    bs = brier_score(predictions, targets)

    if reference_predictions is None:
        # Use mean of targets as simple climatology reference
        mean_target = sum(targets) / len(targets) if targets else 0.5
        ref_bs = brier_score([mean_target] * len(targets), targets)
    else:
        ref_bs = brier_score(reference_predictions, targets)

    if ref_bs == 0:
        return 0.0  # perfect reference
    return 1 - (bs / ref_bs)


def brier_decomposition(
    predictions: List[float],
    targets: List[float]
) -> Dict[str, float]:
    """
    Basic Brier Score decomposition (Reliability + Resolution + Uncertainty).
    Simplified version for binary case.
    """
    if not predictions or len(predictions) != len(targets):
        return {"reliability": float('nan'), "resolution": float('nan'), "uncertainty": float('nan')}

    n = len(predictions)
    mean_target = sum(targets) / n

    # Simple binning for reliability (10 bins)
    bins = 10
    reliability = 0.0
    resolution = 0.0

    for i in range(bins):
        lower = i / bins
        upper = (i + 1) / bins
        bin_preds = [p for p, t in zip(predictions, targets) if lower <= p < upper]
        bin_targets = [t for p, t in zip(predictions, targets) if lower <= p < upper]

        if bin_preds:
            bin_mean_pred = sum(bin_preds) / len(bin_preds)
            bin_mean_target = sum(bin_targets) / len(bin_targets)
            reliability += (len(bin_preds) / n) * (bin_mean_pred - bin_mean_target) ** 2
            resolution += (len(bin_preds) / n) * (bin_mean_target - mean_target) ** 2

    uncertainty = mean_target * (1 - mean_target)

    return {
        "reliability": reliability,
        "resolution": resolution,
        "uncertainty": uncertainty,
        "brier_score": reliability - resolution + uncertainty
    }


def get_brier_variants_summary(
    predictions: List[float],
    targets: List[float]
) -> Dict[str, Any]:
    """Convenience function returning multiple Brier variants."""
    return {
        "brier_score": brier_score(predictions, targets),
        "brier_skill_score": brier_skill_score(predictions, targets),
        "decomposition": brier_decomposition(predictions, targets)
    }
