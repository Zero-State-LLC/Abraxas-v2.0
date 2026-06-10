from typing import Any, Dict, List


def format_brier_summary(summary: Dict[str, Any]) -> str:
    if summary.get("status") == "no_scores_yet":
        return "No Brier scores recorded yet."

    lines = [
        "Brier Score Summary:",
        f"  Samples     : {summary.get('n_scores', 0)}",
        f"  Mean Brier  : {summary.get('mean_brier', 0):.4f}",
        f"  Latest      : {summary.get('latest_brier', 0):.4f}",
        f"  Min         : {summary.get('min_brier', 0):.4f}",
        f"  Max         : {summary.get('max_brier', 0):.4f}",
    ]
    return "\n".join(lines)


def print_brier_trend(brier_scores: List[float], max_lines: int = 5):
    if not brier_scores:
        print("No scores to visualize.")
        return
    recent = brier_scores[-max_lines:]
    max_val = max(recent) or 1
    for score in recent:
        bar = "#" * int((score / max_val) * 20)
        print(f"{score:.3f} | {bar}")


def format_decomposition(decomp: Dict[str, float]) -> str:
    if not decomp or "reliability" not in decomp:
        return "No decomposition available."

    lines = [
        "Brier Score Decomposition:",
        f"  Reliability : {decomp.get('reliability', 0):.4f}",
        f"  Resolution  : {decomp.get('resolution', 0):.4f}",
        f"  Uncertainty : {decomp.get('uncertainty', 0):.4f}",
        f"  Total Brier : {decomp.get('brier_score', 0):.4f}",
    ]
    lines.append("")
    lines.append("Components (higher Resolution = better discrimination; lower Reliability = better calibration):")
    for key in ["reliability", "resolution", "uncertainty"]:
        val = decomp.get(key, 0)
        bar = "#" * int(val * 25)
        lines.append(f"  {key.capitalize():12} : {val:.4f} | {bar}")
    return "\n".join(lines)


def format_reliability_diagram(
    predictions: List[float],
    targets: List[float],
    n_bins: int = 10
) -> str:
    """
    Simple text-based Reliability Diagram.
    Shows predicted probability vs observed frequency per bin.
    """
    if not predictions or len(predictions) != len(targets):
        return "Insufficient data for reliability diagram."

    bins = [[] for _ in range(n_bins)]
    bin_targets = [[] for _ in range(n_bins)]

    for p, t in zip(predictions, targets):
        bin_idx = min(int(p * n_bins), n_bins - 1)
        bins[bin_idx].append(p)
        bin_targets[bin_idx].append(t)

    lines = ["Reliability Diagram (Predicted vs Observed Frequency):"]
    lines.append("Bin | Predicted | Observed | Reliability |")
    lines.append("-" * 55)

    for i in range(n_bins):
        if bins[i]:
            mean_pred = sum(bins[i]) / len(bins[i])
            mean_obs = sum(bin_targets[i]) / len(bin_targets[i])
            reliability = abs(mean_pred - mean_obs)
            bar = "#" * int(mean_obs * 20)
            lines.append(
                f"{i:3d} | {mean_pred:.3f}   | {mean_obs:.3f}   | {reliability:.3f}      | {bar}"
            )
    return "\n".join(lines)
