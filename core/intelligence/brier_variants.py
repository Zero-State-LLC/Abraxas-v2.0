from typing import Any, Dict, List, Optional


def brier_score(predictions: List[float], targets: List[float]) -> float:
    """Standard Brier Score (mean squared error between predicted probabilities and outcomes)."""
    if len(predictions) != len(targets) or not predictions:
        return float('nan')
    return sum((p - t) ** 2 for p, t in zip(predictions, targets)) / len(predictions)


def brier_skill_score(
    predictions: List[float],
    targets: List[float],
    reference_predictions: Optional[List[float]] = None,
    reference_type: str = "climatology"
) -> float:
    """
    Brier Skill Score (BSS).

    Measures the improvement of the forecast over a reference forecast.
    BSS = 1 - (BS_forecast / BS_reference)

    Interpretation:
        - BSS = 1     : Perfect forecast
        - BSS = 0     : Same as reference
        - BSS < 0     : Worse than reference

    Args:
        reference_type: 'climatology' (default) or 'persistence'
    """
    bs = brier_score(predictions, targets)

    if reference_predictions is not None:
        ref_bs = brier_score(reference_predictions, targets)
    else:
        if reference_type == "climatology":
            # Use mean of targets as climatological reference
            if not targets:
                return float('nan')
            mean_target = sum(targets) / len(targets)
            ref_bs = brier_score([mean_target] * len(targets), targets)
        elif reference_type == "persistence":
            # Simple persistence: use previous target as prediction
            if len(targets) < 2:
                return float('nan')
            ref_preds = targets[:-1] + [targets[-1]]  # last observation persists
            ref_bs = brier_score(ref_preds, targets)
        else:
            mean_target = sum(targets) / len(targets)
            ref_bs = brier_score([mean_target] * len(targets), targets)

    if ref_bs == 0:
        return 0.0
    return 1 - (bs / ref_bs)


def brier_decomposition(
    predictions: List[float],
    targets: List[float]
) -> Dict[str, float]:
    """
    Brier Score decomposition into Reliability, Resolution, and Uncertainty.
    """
    if not predictions or len(predictions) != len(targets):
        return {"reliability": float('nan'), "resolution": float('nan'), "uncertainty": float('nan')}

    n = len(predictions)
    mean_target = sum(targets) / n

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
    return {
        "brier_score": brier_score(predictions, targets),
        "brier_skill_score": brier_skill_score(predictions, targets),
        "decomposition": brier_decomposition(predictions, targets)
    }
